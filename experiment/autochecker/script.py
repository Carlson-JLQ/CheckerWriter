easy_rules = ["AvoidUsingOctalValuesRule","ExcessiveImportsRule","NullAssignmentRule","IdenticalCatchBranchesRule",
          "InefficientEmptyStringCheckRule","SignatureDeclareThrowsExceptionRule","StringInstantiationRule","UseStringBufferForStringAppendsRule",
               "ExceptionAsFlowControlRule","ExcessivePublicCountRule"]
not_easy_rules = ["LiteralsFirstInComparisonsRule","MethodNamingConventionsRule","UnnecessaryImportRule","AssignmentToNonFinalStaticRule","AvoidDuplicateLiteralsRule",
    "AvoidThrowingNullPointerExceptionRule","EmptyControlStatementRule","BrokenNullCheckRule","AvoidInstantiatingObjectsInLoopsRule",
                  "ClassWithOnlyPrivateConstructorsShouldBeFinalRule"]

easy1 = []
hard1=[]
easy2=[]
hard2=[]
easy3=[]
hard3=[]
easy4=[]
hard4=[]
for rule in easy_rules:
    path = "codellama-results/1st/easy/"+rule+".txt"
    with open(path, 'r', encoding='utf-8') as file:
        content = file.readlines()
    count=0
    time=0
    success=0
    for line in content:
        if "修复新加测试用例后生成的checker" in line or "5轮中每一轮为第一个测试用例生成的checker" in line:
            count=count+1
        if "规则执行完毕，时间总花" in line:
            time=line
        if "最终通过" in line:
            id1=line.find(" ")
            id2=line.find(" ",id1+1)
            success=line[id1+1:id2]

    id1 = time.find(" ")
    easy1.append(count)
    easy1.append(time[id1+1:])
    easy1.append(success)

for rule in easy_rules:
    path = "deepseek-results/1st/easy/"+rule+".txt"
    with open(path, 'r', encoding='utf-8') as file:
        content = file.readlines()
    count = 0
    time = 0
    success = 0
    for line in content:
        if "修复新加测试用例后生成的checker" in line or "5轮中每一轮为第一个测试用例生成的checker" in line:
            count = count + 1
        if "规则执行完毕，时间总花" in line:
            time = line
        if "最终通过" in line:
            id1 = line.find(" ")
            id2 = line.find(" ", id1 + 1)
            success = line[id1 + 1:id2]

    id1 = time.find(" ")
    easy2.append(count)
    easy2.append(time[id1 + 1:])
    easy2.append(success)

for rule in easy_rules:
    path = "GPT-4-results/2nd/easy/"+rule+".txt"
    with open(path, 'r', encoding='utf-8') as file:
        content = file.readlines()
    count = 0
    time = 0
    success = 0
    for line in content:
        if "修复新加测试用例后生成的checker" in line or "5轮中每一轮为第一个测试用例生成的checker" in line:
            count = count + 1
        if "规则执行完毕，时间总花" in line:
            time = line
        if "最终通过" in line:
            id1 = line.find(" ")
            id2 = line.find(" ", id1 + 1)
            success = line[id1 + 1:id2]

    id1 = time.find(" ")
    easy3.append(count)
    easy3.append(time[id1 + 1:])
    easy3.append(success)

for rule in easy_rules:
    path = "qwen-results/1st/easy/"+rule+".txt"
    with open(path, 'r', encoding='utf-8') as file:
        content = file.readlines()
    count = 0
    time = 0
    success = 0
    for line in content:
        if "修复新加测试用例后生成的checker" in line or "5轮中每一轮为第一个测试用例生成的checker" in line:
            count = count + 1
        if "规则执行完毕，时间总花" in line:
            time = line
        if "最终通过" in line:
            id1 = line.find(" ")
            id2 = line.find(" ", id1 + 1)
            success = line[id1 + 1:id2]

    id1 = time.find(" ")
    easy4.append(count)
    easy4.append(time[id1 + 1:])
    easy4.append(success)

for rule in not_easy_rules:
    path = "codellama-results/1st/not easy/"+rule+".txt"
    with open(path, 'r', encoding='utf-8') as file:
        content = file.readlines()
    count = 0
    time = 0
    success = 0
    for line in content:
        if "修复新加测试用例后生成的checker" in line or "5轮中每一轮为第一个测试用例生成的checker" in line:
            count = count + 1
        if "规则执行完毕，时间总花" in line:
            time = line
        if "最终通过" in line:
            id1 = line.find(" ")
            id2 = line.find(" ", id1 + 1)
            success = line[id1 + 1:id2]

    id1 = time.find(" ")
    hard1.append(count)
    hard1.append(time[id1 + 1:])
    hard1.append(success)

for rule in not_easy_rules:
    path = "deepseek-results/1st/not easy/"+rule+".txt"
    with open(path, 'r', encoding='utf-8') as file:
        content = file.readlines()
    count = 0
    time = 0
    success = 0
    for line in content:
        if "修复新加测试用例后生成的checker" in line or "5轮中每一轮为第一个测试用例生成的checker" in line:
            count = count + 1
        if "规则执行完毕，时间总花" in line:
            time = line
        if "最终通过" in line:
            id1 = line.find(" ")
            id2 = line.find(" ", id1 + 1)
            success = line[id1 + 1:id2]

    id1 = time.find(" ")
    hard2.append(count)
    hard2.append(time[id1 + 1:])
    hard2.append(success)

for rule in not_easy_rules:
    path = "GPT-4-results/2nd/not easy/"+rule+".txt"
    with open(path, 'r', encoding='utf-8') as file:
        content = file.readlines()
    count = 0
    time = 0
    success = 0
    for line in content:
        if "修复新加测试用例后生成的checker" in line or "5轮中每一轮为第一个测试用例生成的checker" in line:
            count = count + 1
        if "规则执行完毕，时间总花" in line:
            time = line
        if "最终通过" in line:
            id1 = line.find(" ")
            id2 = line.find(" ", id1 + 1)
            success = line[id1 + 1:id2]

    id1 = time.find(" ")
    hard3.append(count)
    hard3.append(time[id1 + 1:])
    hard3.append(success)

for rule in not_easy_rules:
    path = "qwen-results/1st/not easy/"+rule+".txt"
    with open(path, 'r', encoding='utf-8') as file:
        content = file.readlines()
    count = 0
    time = 0
    success = 0
    for line in content:
        if "修复新加测试用例后生成的checker" in line or "5轮中每一轮为第一个测试用例生成的checker" in line:
            count = count + 1
        if "规则执行完毕，时间总花" in line:
            time = line
        if "最终通过" in line:
            id1 = line.find(" ")
            id2 = line.find(" ", id1 + 1)
            success = line[id1 + 1:id2]

    id1 = time.find(" ")
    hard4.append(count)
    hard4.append(time[id1 + 1:])
    hard4.append(success)

for i in range(0,10):
    print("-----")
    print(easy_rules[i])
    a=i*3
    b=a+1
    c=b+1

    print("codellama "+str(easy1[a]) + " " + easy1[b] + " " + str(easy1[c]))
    print("deepseek "+str(easy2[a]) + " " + easy2[b] + " " + str(easy2[c]))
    print("gpt "+str(easy3[a]) + " " + easy3[b] + " " + str(easy3[c]))
    print("qwen "+str(easy4[a]) + " " + easy4[b] + " " + str(easy4[c]))

for i in range(0,10):
    print("-----")
    print(not_easy_rules[i])
    a=i*3
    b=a+1
    c=b+1

    print("codellama "+str(hard1[a]) + " " + hard1[b] + " " + str(hard1[c]))
    print("deepseek "+str(hard2[a]) + " " + hard2[b] + " " + str(hard2[c]))
    print("gpt "+str(hard3[a]) + " " + hard3[b] + " " + str(hard3[c]))
    print("qwen "+str(hard4[a]) + " " + hard4[b] + " " + str(hard4[c]))