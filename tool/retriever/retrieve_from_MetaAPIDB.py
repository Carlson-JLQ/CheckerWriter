
import json
from transformers import AutoTokenizer, AutoModel
import torch
from retriever.retrieve_from_FullAPIDB import get_most_similar_api

with open('config.json') as f:
    config = json.load(f)

def get_data(file_path: str):
    sentences = []
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for op_info in data:
        op_name = str(op_info["meta_op"])
        sentences.append(op_name)
    return sentences

# Database to store embeddings and corresponding sentences
database = []
# Load model from HuggingFace Hub
tokenizer = AutoTokenizer.from_pretrained(config['file_paths']['base_dir'] + config['file_paths']['retriever'])
model = AutoModel.from_pretrained(config['file_paths']['base_dir'] + config['file_paths']['retriever'])
model.eval()

# Function to embed sentences and store in the database
def embedding_sentences():
    database.clear()
    sentences = get_data(config['file_paths']['base_dir'] + config['file_paths']['PMD_MetaAPI_DB'])
    encoded_input = tokenizer(sentences, padding=True, truncation=True, return_tensors='pt')
    with torch.no_grad():
        model_output = model(**encoded_input)
    # Use the first token's output as the sentence embedding
    # This is a common practice for models like BERT, where the first token (CLS token) is used for classification tasks
    # and can be interpreted as a sentence-level embedding.
    #提取第一个维度的第一个元素的所有行的第 0 列
        sentence_embeddings = model_output[0][:, 0]
    # Normalize the embeddings to unit length
    # Normalization is often done to ensure that the cosine similarity can be computed effectively.
    # It scales the embeddings to have a unit norm, which is useful for comparing similarity.
    sentence_embeddings = torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)
    for sent, emb in zip(sentences, sentence_embeddings):
        database.append({'sentence': sent, 'embedding': emb})

def find_op_impl(op_name: str):
    with open(config['file_paths']['base_dir'] + config['file_paths']['PMD_MetaAPI_DB'], 'r', encoding='utf-8') as file:
        data = json.load(file)
    for op_info in data:
        if str(op_info["meta_op"]) == op_name:
            return str(op_info["meta_impl"])

def get_most_similar_meta_operation(query: str):
    query_sentence = query
    encoded_query = tokenizer(query_sentence, padding=True, truncation=True, return_tensors='pt')
    with torch.no_grad():
        query_model_output = model(**encoded_query)
        query_embedding = query_model_output[0][:, 0]
    query_embedding = torch.nn.functional.normalize(query_embedding, p=2, dim=1)
    cosine_similarities = torch.nn.functional.cosine_similarity(query_embedding, torch.stack([entry['embedding'] for entry in database]), dim=1)
    most_similar_index = torch.argmax(cosine_similarities).item()
    most_similar_sentence = database[most_similar_index]['sentence']
    impl = []
    code = find_op_impl(most_similar_sentence)
    meta_data = {"op_name": most_similar_sentence, "op_impl": code}
    if float(cosine_similarities[most_similar_index].item()) > 0.85:
        impl.append(meta_data)
    return impl

def get_impl(query: str, nodes: list):
    # first compare with MetaAPI_DB
    impl = get_most_similar_meta_operation(query)
    if len(impl) >= 1:
        return impl
    else:
        # if pass in MetaAPI_DB, then retrieve in FullAPI_DB
        impl = get_most_similar_api(query, nodes)
        if len(impl) >= 1:
            return impl
    return []