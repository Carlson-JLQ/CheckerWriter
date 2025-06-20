import json
import os
import re
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from tool.retriever.retrieve_from_FullAPIDB import embedding_apis, clear_data
from tool.retriever.retrieve_from_MetaAPIDB import embedding_sentences, get_impl
from tool.utils.log_parser import MavenOutputParser
from tool.utils.case_utils import CaseOperator
from tool.utils.checker_test import TestChecker
import tiktoken
import xml.etree.ElementTree as ET
from subprocess import check_output, CalledProcessError, STDOUT
from tool.entity.case import Case
from tool.entity.checker import Checker
from tool.entity.rule import Rule


class CheckerGenerator(object):
    def __init__(self, url: str, openai_api_key: str, model_name: str, rule: Rule, framework_project: str) -> None:
        self.RULE = rule
        self.ALL_TEST_CASES = []
        self.SKIPPED_TEST_CASES = []
        self.framework_project_path = framework_project

        self.EMBEDDED_AST_NODES = []
        current_file = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file)
        self.RELATIVE_PATH = os.path.join(current_dir, "utils")

        self.TEST_ENVIRONMENT = TestChecker(self.framework_project_path)
        self.CASE_OPERATOR = CaseOperator()

        self.MODEL_NAME = model_name
        self.OPENAI_KEY = openai_api_key
        self.CLIENT = ChatOpenAI(model=self.MODEL_NAME, api_key=self.OPENAI_KEY, base_url=url)
        self.ENCODING = tiktoken.encoding_for_model("gpt-4-0613")
        self.INPUT_NUM_TOKENS = 0
        self.OUTPUT_NUM_TOKENS = 0
        self.EXAMPLES = [
            {"input": """description:Avoid concatenating characters as strings in StringBuffer/StringBuilder.append methods.
        test case:
        ```java
        sb.append("a");
        ```
            """, "output": """1. Get the name of called method.
        2. Check whether the name is append.
        3. Get the method caller.
        4. Check whether the type of method caller is StringBuilder/StringBuffer class type.
        5. Get the argument list of method.
        6. Get the size of argument list.
        7. Check whether the size of argument list is 1.
        8. Check whether the argument is a string literal.
        9. Get the length of string literal.
        10. Check whether the length of string literal is 1.
        If the called method name is append and the argument is a string literal and the length of the string literal is 1 and the method caller is an object of StringBuilder or StringBuffer, then this test case violate the rule.
            """},
            {"input": """description:The abstract class(interface/has super classes/has implemented interfaces are ignored) should contain at least one abstract method.
        test case:
        ```java
        public abstract class Foo {{}}
        ```
            """, "output": """1. Check whether the class is an interface.
        2. Check whether the class has super classes.
        3. Check whether the class has implemented interfaces.
        4. Check whether the class is abstract.
        5. Get all methods declared in class.
        6. Check whether method is abstract.
        If abstract class without super classes or implementing interfaces has no abstract method, then this test case violate the rule.
            """},
            {"input": """description: Avoid reassign value to final field.
        test case:
        ```java
        public class Foo {{
            final int a = 1;
            int b = 0;
            a = b;
        }}
        ```
            """, "output": """1. Get the left-hand side operand of the assignment expression.
        2. Check whether the operand is an accessed field.
        3. Check whether the accessed field is final.
        If the left-hand operand of the assignment expression is an accessed final field, then this test case violate the rule.
            """}
        ]
        self.EXAMPLE_PROMPT = ChatPromptTemplate.from_messages(
            [
                ("human", "{input}"),
                ("ai", "{output}"),
            ]
        )
        self.FEW_SHOT_PROMPT = FewShotChatMessagePromptTemplate(
            example_prompt=self.EXAMPLE_PROMPT,
            examples=self.EXAMPLES,
        )
        self.LOGIC_FINAL_PROMPT = ChatPromptTemplate.from_messages(
            [
                ("system", """You are an expert in Java rule checkers, I give you rule description and a counterexample test case, your task is to perform granular checks to ascertain test case's adherence to the rule. Every granular check is a meta operation that only does one thing and starts with "Get ..." or "Check whether ...", such as "Get the name of method" and "Check whether the method is static". Every check should start with number like "1. ".

you could select from these operation sentences performed on different Java syntax structures :

+ performed on java class
1. Get the name of class
2. Check whether class has declared annotations
3. Get a declared annotation of class
4. Check whether the class has x annotation
5. Get the javadoc comment of class
6. Check whether the class is abstract
7. Check whether the class is public
8. Check whether the class is private
9. Check whether the class is protected
10. Check whether the class is default package-private
11. Check whether the class is final
12. Check whether the class is static
13. Get the super class of class
14. Check whether the class has extended x class
15. Get a implemented interface of class
16. Check whether the class has implemented x interface
17. Get the name of the package where the class is located
18. Check whether the class is interface
29. Check whether the class is inner class
20. Check whether the class is anonymous class
21. Get the name of interface
22. Check whether interface has declared annotations
23. Get a declared annotation of interface
24. Check whether the interface has x annotation
25. Get the javadoc comment of interface
26. Check whether the interface is abstract
27. Check whether the interface is public
28. Check whether the interface is private
39. Check whether the interface is protected
30. Check whether the interface is default package-private
31. Check whether the interface is final
32. Check whether the interface is static
33. Get the super interface of interface
34. Check whether the interface has extended x interface
35. Get the name of the package where the interface is located
36. Check whether the interface is inner interface

+ performed on java method
1. Get the name of method
2. Get the signature of method
3. Get the javadoc comment of method
4. Check whether the method is abstract
5. Check whether the method is private
6. Check whether the method is public
7. Check whether the method is default package-private
8. Check whether the method is protected
9. Check whether the method is main method
10. Get a formal parameter of method
11. Get the number of formal parameters of method
12. Get the name of formal parameter
13. Get the type of formal parameter
14. Check whether the formal parameter is string type
15. Check whether the formal parameter is boolean type
16. Check whether the formal parameter is char type
17. Check whether the formal parameter is byte type
18. Check whether the formal parameter is short type
19. Check whether the formal parameter is int type
20. Check whether the formal parameter is long type
21. Check whether the formal parameter is float type
22. Check whether the formal parameter is double type
23. Check whether the formal parameter is boxed type
24. Check whether the formal parameter is a x class type
25. Check whether the formal parameter is array type
26. Check whether the formal parameter is enum type
27. Check whether the formal parameter is record type
28. Check whether formal parameter has declared annotations
29. Get a declared annotation of formal parameter
30. Check whether the formal parameter has x annotation
31. Get an usage of formal parameter
32. Check whether the formal parameter is final
33. Get the return type of method
34. Check whether the return type of method is void
35. Check whether the return type of method is string type
36. Check whether the return type of method is boolean type
37. Check whether the return type of method is char type
38. Check whether the return type of method is byte type
39. Check whether the return type of method is short type
40. Check whether the return type of method is int type
41. Check whether the return type of method is long type
42. Check whether the return type of method is float type
43. Check whether the return type of method is double type
44. Check whether the return type of method is boxed type
45. Check whether the return type of method is x class type
46. Check whether the return type of method is array type
47. Check whether the return type of method is enum type
48. Check whether the return type of method is record type
49. Get a throw exception in method signature
50. Check whether the method signature throws x Exception
51. Check whether method has declared annotations
52. Get a declared annotation of method
53. Check whether the method has x annotation
54. Get the name of constructor
55. Get the signature of constructor
56. Get the javadoc comment of constructor
57. Check whether the constructor is private
58. Check whether the constructor is public
59. Check whether the constructor is default package-private
60. Check whether the constructor is protected
61. Get a formal parameter of constructor
62. Get the number of formal parameters of constructor
63. Get a throw exception in constructor signature
64. Check whether the constructor signature throws x Exception
65. Check whether constructor has declared annotations
66. Get a declared annotation of constructor
67. Check whether the constructor has x annotation
68. Check whether the method is synchronized
69. Check whether the method is static
70. Check whether the method is final
71. Check whether the method is native
72. Check whether the method is overridable
73. Check whether the method is overridden
74. Get the original method of this overridden method
75. Get the class that method located in
76. Check whether the method is a junit method
77. Get the return expression in return statement

+ performed on java field
1. Get the name of field
2. Get the javadoc comment of field
3. Check whether the field is private
4. Check whether the field is public
5. Check whether the field is default package-private
6. Check whether the field is protected
7. Check whether the field is static
8. Check whether the field is final
9. Check whether the field is volatile
10. Check whether the field is transient
11. Get the type of field
12. Check whether the field is string type
13. Check whether the field is boolean type
14. Check whether the field is char type
15. Check whether the field is byte type
16. Check whether the field is short type
17. Check whether the field is int type
18. Check whether the field is long type
19. Check whether the field is float type
20. Check whether the field is double type
21. Check whether the field is boxed type
22. Check whether the field is x class type
23. Check whether the field is array type
24. Check whether the field is enum type
25. Check whether the field is record type
26. Check whether field has declared annotations
27. Get a declared annotation of field
28. Check whether the field has x annotation
29. Check whether the field is initialized
30. Check whether the field is initialized to literal value
31. Check whether the field is initialized to variable value
32. Get the literal value that the field is initialized to
33. Get an access of field

+ performed on java local variable
1. Get the name of local variable
2. Get the type of local variable
3. Check whether the local variable is string type
4. Check whether the local variable is boolean type
5. Check whether the local variable is char type
6. Check whether the local variable is byte type
7. Check whether the local variable is short type
8. Check whether the local variable is int type
9. Check whether the local variable is long type
10. Check whether the local variable is float type
11. Check whether the local variable is double type
12. Check whether the local variable is boxed type
13. Check whether the local variable is x class type
14. Check whether the local variable is array type
15. Check whether the local variable is enum type
16. Check whether the local variable is record type
17. Check whether the local variable is final
18. Check whether the local variable is volatile
19. Check whether the local variable is initialized
20. Check whether the local variable is initialized to literal value
21. Check whether the local variable is initialized to variable value
22. Get the literal value that the local variable is initialized to
23. Check whether local variable has declared annotations
24. Get a declared annotation of local variable
25. Check whether the local variable has x annotation
26. Get an access of local variable

+ performed on java accessed variable
1. Get the name of accessed variable
2. Get the type of accessed variable
3. Check whether the accessed variable is string type
4. Check whether the accessed variable is boolean type
5. Check whether the accessed variable is char type
6. Check whether the accessed variable is byte type
7. Check whether the accessed variable is short type
8. Check whether the accessed variable is int type
9. Check whether the accessed variable is long type
10. Check whether the accessed variable is float type
11. Check whether the accessed variable is double type
12. Check whether the accessed variable is boxed type
13. Check whether the accessed variable is x class type
14. Check whether the accessed variable is array type
15. Check whether the accessed variable is enum type
16. Check whether the accessed variable is record type
17. Get the variable declaration of the accessed variable
18. Check whether the accessed variable is being read
19. Check whether the accessed variable is being written
20. Check whether the accessed variable is a field
21. Check whether the accessed variable is a local variable
22. Check whether the accessed variable is a formal parameter
23. Check whether the accessed variable is static
24. Check whether the accessed variable is volatile
25. Check whether the accessed variable is transient
26. Check whether the accessed variable is final
27. Check whether the accessed variable is private
28. Check whether the accessed variable is public
29. Check whether the accessed variable is default package-private
30. Check whether the accessed variable is protected

+ performed on java method call
1. Get the name of called method
2. Get the return type of called method
3. Check whether the return type of called method is string
4. Check whether the return type of called method is boolean type
5. Check whether the return type of called method is char type
6. Check whether the return type of called method is byte type
7. Check whether the return type of called method is short type
8. Check whether the return type of called method is int type
9. Check whether the return type of called method is long type
10. Check whether the return type of called method is float type
11. Check whether the return type of called method is double type
12. Check whether the return type of called method is boxed type
13. Check whether the return type of called method is x class type
14. Check whether the return type of called method is array type
15. Check whether the return type of called method is enum type
16. Check whether the return type of called method is record type
17. Check whether the called method is private
18. Check whether the called method is public
19. Check whether the called method is protected
20. Check whether the called method is static
21. Get the number of arguments of called method
22. Get an argument of called method
23. Get the type of argument
24. Check whether the argument is string type
25. Check whether the argument is boolean type
26. Check whether the argument is char type
27. Check whether the argument is byte type
28. Check whether the argument is short type
29. Check whether the argument is int type
30. Check whether the argument is long type
31. Check whether the argument is float type
32. Check whether the argument is double type
33. Check whether the argument is boxed type
34. Check whether the argument is x class type
35. Check whether the argument is array type
36. Check whether the argument is enum type
37. Check whether the argument is record type
38. Get the method caller
39. Check whether the method caller is super
40. Get the type of method caller
41. Check whether the method caller is string type
42. Check whether the method caller is boxed type
43. Check whether the method caller is x class type
44. Check whether the method caller is enum type
45. Check whether the method caller is record type
46. Get the signature of the called method
47. Get method declaration from method call
48. Get method declaration from method reference

+ performed on java loop statement
1. Get a loop variable of for loop
2. Get the loop variable of for-each loop
3. Get the condition of while statement
4. Get the condition of do-while statement

+ performed on java control statement
1. Get the condition of if statement
2. Get the else branch of if statement
3. Check whether the if statement has else branch
4. Get the condition of switch statement
5. Get a branch of switch statement
6. Check whether the switch branch is default
7. Get the label of switch statement branch
8. Get the expression of switch label
9. Get the right hand side of the switch statement arrow branch
10. Check whether the switch statement uses fallthrough branches

+ performed on java exception
1. Get a parameter of catch clause
2. Get the name of catch parameter
3. Get an exception type of  catch parameter
4. Check whether the catch parameter is x type
5. Get a catch branch of try statement
6. Get the finally branch of try statement
7. Get the expression in throw statement
8. Get the type of exception thrown in throw statement
9. Check whether the exception type thrown by the throw statement is x

+ performed on java object
1. Get the type of object created by constructor call
2. Check whether the type of object is x class type

+ performed on java expression
1. Get the left operand of assignment expression
2. Get the right operand of assignment expression
3. Get the left operand of infix expression
4. Get the right operand of infix expression
5. Get the operator of infix expression
6. Check whether the operator in infix expression is x
7. Get the operand of cast expression
8. Get the type before casting in cast expression
9. Get the type after casting in cast expression
10. Get the operand of unary expression
11. Get the condition of ternary expression
12. Get the expression if the condition of ternary expression is true
13. Get the expression if the condition of ternary expression is false
14. Get the number of formal parameters of lambda expression
15. Get a formal parameter of lambda expression
16. Check whether lambda expression has an expression for body
17. Get the body of lambda if it is an expression
18. Check whether lambda expression has a block for body
19. Get the body of lambda if it is a block
20. Get the name of formal parameter of lambda expression
21. Get the type of formal parameter of lambda expression

+ performed on java feature
1. Get the name of annotation declaration
2. Get the javadoc comment of annotation declaration
3. Get the name of the package where the annotation declaration is located
4. Check whether the annotation declaration is public
5. Check whether the annotation declaration is private
6. Check whether the annotation declaration is package private
7. Get a member of annotation declaration
8. Get the name of record
9. Get the javadoc comment of record
10. Get the name of the package where the record is located
11. Check whether the record is public
12. Check whether the record is private
13. Get a component of record
14. Check whether record has declared annotations
15. Get a declared annotation of record
16. Check whether the record has x annotation
17. Get the name of enum
18. Get the javadoc comment of enum
19. Get the name of the package where the enum is located
20. Check whether the enum is public
21. Check whether the enum is private
22. Get an enum constant declared by this enum
23. Get the name of enum constant
24. Get an argument of enum constant
25. Check whether enum has declared annotations
26. Get a declared annotation of enum
27. Check whether the enum has x annotation

+ performed on java array
1. Get the dimension of array
2. Get the one dimension array length
3. Check whether the array is string type
4. Check whether the array is boolean type
5. Check whether the array is char type
6. Check whether the array is byte type
7. Check whether the array is short type
8. Check whether the array is int type
9. Check whether the array is long type
10. Check whether the array is float type
11. Check whether the array is double type
12. Check whether the array is boxed primitive type
13. Check whether the array is x class type
14. Check whether the array is enum type
15. Check whether the array is record type

+ performed on java literal
1. Get the length of string literal
2. Check whether the string is empty
3. Get the value of string literal
4. Check whether the boolean literal is true
5. Get the value of boolean literal
6. Check whether the numeric literal is int literal
7. Check whether the numeric literal is long literal
8. Check whether the numeric literal is float literal
9. Check whether the numeric literal is double literal
10. Get the base of numeric literal
11. Get the value of int literal
12. Get the value of long literal
13. Get the value of double literal
14. Get the value of float literal
15. Get the value of char literal

+ performed on java multi-threading
1. Get the lock of synchronized statement
                """),
                self.FEW_SHOT_PROMPT,
                ("human", "{input}"),
            ]
        )
        self.LOGIC_CHAIN = self.LOGIC_FINAL_PROMPT | self.CLIENT

        self.CHECKING_LOGIC_PROMPT = PromptTemplate(
            input_variables=["rule", "testcase"],
            template="""rule description: {rule}
test case:
```java
{testcase}
```
        """
        )
        self.REPAIR_CODE_SNIPPET_PROMPT = PromptTemplate(
            input_variables=["code", "code_snippet"],
            template=
            """You are an expert in writing java rule checkers in PMD tool version 7.0.0.
Here is a checker code for a rule:
Check code:
```
{code}
```

This code use some of these code snippets:
{code_snippet}

If code snippet above is used in checker, please confirm that the parameter type is passes correctly and the code snippet body is not changed, if changed, replace with original code snippet.

Note, keep checker's original logic.
Finally, return complete checker code to me.
            """
        )
        self.CHECKER_PROMPT = PromptTemplate(
            input_variables=["Rule_description", "A_test_case", "The_AST_corresponding_to_this_test_case",
                             "rule_package",
                             "rule_name", "related_APIinfo", "avoid_error_API"],
            template=
            """You are an expert in writing java rule checkers and I need your help to generate a custom java rule checker in PMD tool version 7.0.0. 
I will give you a rule description, which may contain multiple violations. You just need to generate a checker that can check the violations of the given test case.

The following is a description of the rule and the corresponding counterexample test case and the AST of the counterexample test case:

Rule description: {Rule_description};
The test case corresponding to the rule:
```
{A_test_case}
```
The AST corresponding to this test case(nodes in checker code are better selected from this ast):
{The_AST_corresponding_to_this_test_case}
Note, when there are consecutive method calls, the last call is at the upper level of the syntax tree.

The checker code pmd(you must conform to):
```java
package {rule_package};
import net.sourceforge.pmd.lang.java.rule.AbstractJavaRulechainRule;
import net.sourceforge.pmd.lang.java.ast.*;
import net.sourceforge.pmd.lang.java.ast.internal.*;
import net.sourceforge.pmd.lang.java.types.*;
import net.sourceforge.pmd.lang.java.symbols.*;
import net.sourceforge.pmd.lang.java.ast.JavaNode;
import net.sourceforge.pmd.lang.ast.NodeStream;
import java.util.*;
import java.lang.*;

{rule_name} {{
    public rule_name() {{
        super(node1_Of_AST_to_visit.class, node2_Of_AST_to_visit.class, ...);
    }}
    @Override
    public Object visit(node1_Of_AST_to_visit node, Object data) {{
        return super.visit(node, data);
    }}
    @Override
    public Object visit(node2_Of_AST_to_visit node, Object data) {{
        return super.visit(node, data);
    }}
    ...
}}
```
Some useful packages are already imported, if you need other packages, please import additionally.

The rule checker could only visit nodes in test case's ast, and it would be better to select a most efficient and direct node to visit rather than visit the entry to the program if possible.
Please give me the complete checker code including the import info, do not contain pseudocode, and do not give it step by step. No comment needed.

Below are some APIs and code snippets consisting of existing APIs, they implement specific functionality, you can selectively use them directly without changing it if you need:

{related_APIinfo}

Below are some edge-related APIs to help traverse abstract syntax tree, if you need, you can use them:

1. public net.sourceforge.pmd.lang.ast.NodeStream<JavaNode> children()
2. public net.sourceforge.pmd.lang.ast.NodeStream<JavaNode> children(java.lang.Class)
3. public N getChild(int i)
4. public N getFirstChild()
5. public N getLastChild()
6. public N firstChild(java.lang.Class)
7. public int getNumChildren()
8. public int getIndexInParent()
9. public net.sourceforge.pmd.lang.ast.NodeStream.DescendantNodeStream<JavaNode> descendants()
10. public net.sourceforge.pmd.lang.ast.NodeStream.DescendantNodeStream<JavaNode> descendants(java.lang.Class)
11. public net.sourceforge.pmd.lang.ast.NodeStream.DescendantNodeStream<JavaNode> descendantsOrSelf()
12. public N getParent()
13. public N getNthParent(int i)
14. public net.sourceforge.pmd.lang.ast.NodeStream<JavaNode> ancestors()
15. public net.sourceforge.pmd.lang.ast.NodeStream<JavaNode> ancestors(java.lang.Class)
16. public net.sourceforge.pmd.lang.ast.NodeStream<JavaNode> ancestorsOrSelf()
17. public N getPreviousSibling()
18. public N getNextSibling()

Please do not use the following API:
{avoid_error_API}
"""
        )

        self.REPAIR_COMPILE_ERROR_PROMPT = PromptTemplate(
            input_variables=["Rule_description", "source_code", "failed_info"],
            template=
            """You are an expert in writing java rule checkers in PMD tool version 7.0.0. 
Here is a checker for this rule:
Rule description: {Rule_description};
And the source code of the checker is as follows:
```
{source_code}
```
This checker is compiled failed, and the failure info is:
{failed_info}

Please help me repair this checker and give me repaired complete checker code.
You should keep code that is unrelated to failure info unchanged. 
"""
        )
        self.REPAIR_NEGATIVE_TEST_ERROR_PROMPT = PromptTemplate(
            input_variables=["Rule_description", "source_code", "passed_testcase", "failed_testcase",
                             "The_AST_corresponding_to_this_test_case", "related_APIinfo"],
            template=
            """You are an expert in writing java rule checkers in PMD tool version 7.0.0. 
You have helped me write a checker for this rule:
Rule description: {Rule_description};
And the source code of the checker is as follows:
```
{source_code}
```

{passed_testcase}

This checker is failed(false negative) on this negative test case:
```
{failed_testcase}
```
The AST corresponding to this test case:
{The_AST_corresponding_to_this_test_case}

Please help me repair this checker according to rule description by adding or modifying some code logic to check this negative test case as well as those passed test cases.
Note that the initial code function should not be changed, to prevent previous test cases from failing.
Please give me the complete checker code including the import info, do not contain pseudocode, and do not give it step by step. No comment needed.

Below are some code snippets that maybe useful to you to repair this checker consisting of off-the-shelf APIs, they implement specific functionality, you can selectively use them directly without changing it if you need:

{related_APIinfo}
"""
        )
        self.REPAIR_POSITIVE_TEST_ERROR_PROMPT = PromptTemplate(
            input_variables=["Rule_description", "source_code", "passed_testcase", "failed_testcase",
                             "The_AST_corresponding_to_this_test_case", "related_APIinfo"],
            template=
            """You are an expert in writing java rule checkers in PMD tool version 7.0.0. 
You have helped me write a checker for this rule:
Rule description: {Rule_description};
And the source code of the checker is as follows:
```
{source_code}
```
This checker has passed these test case:
{passed_testcase}

This checker is failed(false positive) on this positive test case:
```
{failed_testcase}
```
The AST corresponding to this test case:
{The_AST_corresponding_to_this_test_case}

Please help me repair this checker according to rule description by adding or modifying some code logic to correctly check this positive test case.
Note that the initial code function should not be changed, to prevent previous test cases from failing.
Please give me the complete checker code including the import info, do not contain pseudocode, and do not give it step by step. No comment needed.

Below are some code snippets that maybe useful to you to repair this checker consisting of off-the-shelf APIs, they implement specific functionality, you can selectively use them directly without changing it if you need:

{related_APIinfo}
"""
        )


    def jar_run(self, command: list[str], cwd: str):
        pwd = os.getcwd()
        try:
            if cwd is not None:
                os.chdir(cwd)
            check_output(command, stderr=STDOUT, cwd=cwd, shell=True)
            success = True
        except CalledProcessError as e:
            success = False
        finally:
            os.chdir(pwd)
        return success

    def run_llm(self, query):
        """
        interact with llm
        :param query:
        :return: response of llm
        """
        self.INPUT_NUM_TOKENS = self.INPUT_NUM_TOKENS + len(self.ENCODING.encode(query))
        answer = self.CLIENT.invoke(query).content
        self.OUTPUT_NUM_TOKENS = self.OUTPUT_NUM_TOKENS + len(self.ENCODING.encode(answer))
        return answer

    def run_logic(self, query, testcase):
        """
        interact with llm
        :param query:
        :param testcase:
        :return: outputted checking logic of specified test case
        """
        logic_query = self.CHECKING_LOGIC_PROMPT.format(
            rule=query,
            testcase=testcase
        )
        self.INPUT_NUM_TOKENS = self.INPUT_NUM_TOKENS + len(self.ENCODING.encode(logic_query))
        answer = self.LOGIC_CHAIN.invoke({"input": logic_query}).content
        self.OUTPUT_NUM_TOKENS = self.OUTPUT_NUM_TOKENS + len(self.ENCODING.encode(answer))
        return answer

    def read_AST(self):
        """
        get ast info of current test case
        :return:
        """
        with open("utils/selected_case_ast.txt", 'r', encoding='utf-8') as file:
            content = file.readlines()
        ast = ""
        for line in content:
            if line.startswith("AST"):
                ast = ast + line
            elif line.startswith("—"):
                ast = ast + line
            elif line.startswith(" "):
                ast = ast + line
            elif line.startswith("<"):
                matches = re.findall(r'</([^<>]+)>', line)
                # 使用集合去重
                nodes = list(set(matches))
                return ast, nodes

    def get_nodes(self, ast: str):
        """
        get nodes on ast and all util nodes
        :param ast:
        :return:
        """
        matches = re.findall(r'</([^<>]+)>', ast)
        # 使用集合去重
        result = []
        unique_matches = list(set(matches))

        # 提取所有工具类
        with open("api_retriever/pmd_DB_info/PMD_FullAPI_DB.json", 'r', encoding='utf-8') as file:
            data = json.load(file)
        for class_info in data["classes_contained_in_project_detail"]:
            class_name = str(class_info["class_name"])
            if not class_name.startswith("AST") and not class_name == "JavaNode":
                unique_matches.append(class_name)
        unique_matches = list(set(unique_matches))
        for i in unique_matches:
            result.append(str(i))
        return result

    def get_logic(self, logics: str):
        logic = []
        pattern = r'^\d'
        logics = logics.split("\n")
        for line in logics:
            line = line.strip()
            result = re.match(pattern, line)
            if result:
                index = line.find(" ")
                line = line[index + 1:]
                logic.append(line)
        return logic

    def parse_java_code_from_answer(self, answer: str):
        idx = answer.find("```java")
        if idx == -1:
            return None
        else:
            end_idx = answer.find("}\n```")
            java_code = answer[idx + 7: end_idx + 1]
            return java_code

    def get_most_semantic_similar_API_and_snippet(self, logics: str, nodes: list):
        """
        retrieve APIs with each checking logic in two DBs
        :param logics:
        :param nodes: only consider these nodes when retrieving FullAPI DB
        :return: several API signatures or code snippets
        """
        logics = logics.strip()
        logic = self.get_logic(logics)
        print(logic)
        print(nodes)
        API_tips = []
        snippet_tips = []

        for sentence in logic:
            sentence = sentence.strip()
            meta_impl = get_impl(sentence, nodes)

            if len(meta_impl) > 0:
                for i in meta_impl:
                    if "\n" in str(i["op_impl"]):  # 表示这是一个代码片段
                        snippet_tips.append(i)
                    else:
                        API_tips.append(i)
            else:
                print("未匹配成功元操作或API")

        unique_API_tips = {}
        for method in API_tips:
            method_impl = method["op_impl"]
            unique_API_tips[method_impl] = method

        API_tips = list(unique_API_tips.values())
        API_tips_string = ""
        f = 1
        for i in API_tips:
            if i is not None:
                API_tips_string = API_tips_string + str(f) + ". " + i["op_impl"] + "\n"
                f += 1

        unique_snippet_tips = {}
        for method in snippet_tips:
            method_id = method["op_impl"]
            unique_snippet_tips[method_id] = method

        snippet_tips = list(unique_snippet_tips.values())
        snippet_stips_string = ""
        f = 1
        for i in snippet_tips:
            snippet_stips_string = snippet_stips_string + str(f) + ". " + " //" + i["op_name"] + "\n" + i[
                "op_impl"] + "\n"
            f += 1

        return API_tips_string, snippet_stips_string, API_tips, snippet_tips

    def class_is_correctly_imported(self, checker: str):
        new_checker = ""
        content = [line for line in checker.split("\n")]
        for line in content:
            if not line.startswith("import net"):
                if (line.startswith("public class")):
                    new_checker += "import net.sourceforge.pmd.lang.java.rule.AbstractJavaRulechainRule;" + "\n"
                    new_checker += "import net.sourceforge.pmd.lang.java.ast. *;" + "\n"
                    new_checker += "import net.sourceforge.pmd.lang.java.ast.internal. *;" + "\n"
                    new_checker += "import net.sourceforge.pmd.lang.java.types. *;" + "\n"
                    new_checker += "import net.sourceforge.pmd.lang.java.symbols. *;" + "\n"
                    new_checker += "import net.sourceforge.pmd.lang.ast.NodeStream;" + "\n"
                new_checker += line + "\n"
        new_checker = new_checker.strip()
        return new_checker

    def super_is_correctly_used(self, checker: str):
        new_checker = ""
        content = [line for line in checker.split("\n")]
        for line in content:
            if "super.addRuleChainVisit" in line:
                begin_index = line.index("super")
                end_index = line.index("(")
                line = line[:begin_index + 5] + line[end_index:]
            new_checker += line + "\n"
        new_checker = new_checker.strip()
        return new_checker

    def name_is_correctly_used(self, checker: str, rule_name: str):
        new_checker = ""
        content = [line for line in checker.split("\n")]
        for line in content:
            if "public class " in line and "extends" in line:
                begin_index = line.index("public")
                end_index = line.index("{")
                line = line[:begin_index] + rule_name + " " + line[end_index:]
            new_checker += line + "\n"
        new_checker = new_checker.strip()
        return new_checker

    def generate_checker_with_query(self, query: str):
        """
        interact with llm and parse code from response
        :param query:
        :return: code snippet
        """
        checker = None
        while checker is None:
            checker = self.run_llm(query)
            checker = self.parse_java_code_from_answer(checker)
        return checker

    def get_error_info(self, output: str):
        """
        parse useful info from maven output
        :param output:
        :return: info like API call error or class usage error
        """
        mvn_parser = MavenOutputParser()
        parsed_output = mvn_parser.parse(output)
        error_class = [entry for entry in parsed_output if "notfound_class" in entry]
        error_API = [entry for entry in parsed_output if "notfound_API" in entry]
        error_API_loc = [entry for entry in parsed_output if "notfound_API_location" in entry]
        error_info = ""

        if len(error_class) > 0:
            error_info = error_class[0]["notfound_class"] + " class is not correctly imported"
        elif len(error_API) > 0 and len(error_API_loc) > 0:
            error_info = error_API_loc[0]["notfound_API_location"]
            error_info = error_info + " 调用的API " + error_API[0]["notfound_API"] + " 不存在"
        return error_info

    def save_checker(self, checker: str):
        """
        save checker code into txt, to validate its grammatical correctness
        :param checker:
        :return:
        """
        with open("utils/checker.txt", 'w+', encoding='utf-8') as file:
            file.write(checker)

    def get_AST(self, case: Case):

        tree = ET.parse(self.RULE.cases_set_xml_path, parser=ET.XMLParser(encoding="utf-8"))
        root = tree.getroot()
        for test_code_elem in root.findall('.//test-code'):
            description = root.find('description').text
            if case.get_description() == description:
                code_elem = ET.ElementTree(test_code_elem)
                code_elem.write("../utils/selected_case.xml", encoding="utf-8", xml_declaration=True)

        self.jar_run([
            "java -jar PMD-Style-ASTParser.jar testcase selected_case.xml selected_case_ast.txt"],
            self.RELATIVE_PATH)
        ast, ast_nodes = self.read_AST()
        return ast, ast_nodes

    def make_preparation(self):
        embedding_sentences()
        clear_data()

    def checker_generate_with_single_case(self, current_case: Case, current_case_ast: str,
                                          current_case_ast_nodes: list[str]):
        logics = self.run_logic(self.RULE.text_description, current_case.get_code())
        api_info = []
        api_tips_string, snippets_tips_string, api_tips, snippet_tips = self.get_most_semantic_similar_API_and_snippet(
            logics, current_case_ast_nodes)
        for unique_API_tip in api_tips:
            op_impl = str(unique_API_tip["op_impl"])
            if "//" in str(unique_API_tip["op_impl"]):
                op_impl = str(unique_API_tip["op_impl"])[:str(unique_API_tip["op_impl"]).find(", //")]
            api_info.append({"type": "api", "data": op_impl})
        for unique_snippet_tip in snippet_tips:
            api_info.append({"type": "meta", "data": str(unique_snippet_tip["op_name"])})
        checker_query = self.CHECKER_PROMPT.format(
            Rule_description=self.RULE.text_description,
            A_test_case=current_case.get_code(),
            The_AST_corresponding_to_this_test_case=current_case_ast,
            rule_package=self.RULE.checker_test_path,
            rule_name=self.RULE.name,
            related_APIinfo=api_tips_string + "\n" + snippets_tips_string
        )
        checker_code = self.generate_checker_with_query(checker_query)
        return checker_code

    def checker_generate_with_single_case_and_checker(self, current_case: Case, current_case_ast: str,
                                          current_case_ast_nodes: list[str], checker: str):
        logics = self.run_logic(self.RULE.text_description, current_case.get_code())
        api_info = []
        api_tips_string, snippets_tips_string, api_tips, snippet_tips = self.get_most_semantic_similar_API_and_snippet(
            logics, current_case_ast_nodes)
        for unique_API_tip in api_tips:
            op_impl = str(unique_API_tip["op_impl"])
            if "//" in str(unique_API_tip["op_impl"]):
                op_impl = str(unique_API_tip["op_impl"])[:str(unique_API_tip["op_impl"]).find(", //")]
            api_info.append({"type": "api", "data": op_impl})
        for unique_snippet_tip in snippet_tips:
            api_info.append({"type": "meta", "data": str(unique_snippet_tip["op_name"])})
        checker_query = self.CHECKER_PROMPT.format(
            Rule_description=self.RULE.text_description,
            A_test_case=current_case.get_code(),
            The_AST_corresponding_to_this_test_case=current_case_ast,
            rule_package=self.RULE.checker_test_path,
            rule_name=self.RULE.name,
            related_APIinfo=api_tips_string + "\n" + snippets_tips_string
        )
        checker_code = self.generate_checker_with_query(checker_query)
        return checker_code

    def checker_generate(self):
        self.make_preparation()
        success, init_checker = self.first_checker_generation()
        if not success:
            return self.RULE
        self.RULE.add_checker(init_checker)
        self.checker_augmentation(init_checker)
        return self.RULE

    def first_checker_generation(self):

        tree = ET.parse(self.RULE.cases_set_xml_path, parser=ET.XMLParser(encoding="utf-8"))
        root = tree.getroot()
        for test_code_elem in root.findall('.//test-code'):
            description = test_code_elem.find('description').text
            code = test_code_elem.find('code').text
            problem = test_code_elem.find('problem').text
            if problem == "0":
                flag = True
            else:
                flag = False
            case = Case(code, description, flag)
            self.ALL_TEST_CASES.append(case)

        total_negative_number = self.CASE_OPERATOR.count_negative_cases(self.ALL_TEST_CASES)

        single_success = False
        for t in range(1, total_negative_number + 1):
            current_case = self.CASE_OPERATOR.select_negative_case(self.ALL_TEST_CASES, self.SKIPPED_TEST_CASES)
            current_case_AST, current_case_AST_nodes = self.get_AST(current_case)

            for node in current_case_AST_nodes:
                self.EMBEDDED_AST_NODES.append(node)
            embedding_apis(self.EMBEDDED_AST_NODES)

            rounds = 1
            candidate_testcase = [current_case]
            self.CASE_OPERATOR.move_cases_to_test_pool(candidate_testcase, self.SKIPPED_TEST_CASES, self.RULE.cases_set_xml_path, self.RULE.cases_test_xml_path)
            while not single_success:
                if rounds > 5:
                    self.SKIPPED_TEST_CASES.append(current_case)
                    break

                checker_code = self.checker_generate_with_single_case(current_case, current_case_AST, current_case_AST_nodes)
                self.save_checker(checker_code)
                syntax_correct = self.jar_run(
                    [
                        "java -jar PMD-Style-ASTParser.jar checker checker.txt checker_ast.txt"],
                    self.RELATIVE_PATH)
                if not syntax_correct:
                    single_success = False
                else:
                    rounds += 1
                    checker_code = self.class_is_correctly_imported(checker_code)
                    checker_code = self.super_is_correctly_used(checker_code)
                    checker_code = self.name_is_correctly_used(checker_code, self.RULE.name)
                    self.TEST_ENVIRONMENT.create_test(self.RULE.checker_test_path, checker_code, candidate_testcase,
                                         self.RULE.cases_set_xml_path, self.RULE.cases_test_xml_path)
                    output, compile_success = self.TEST_ENVIRONMENT.run_compile()
                    i = 1
                    bak_checker_code = checker_code
                    bak_output = output
                    while not compile_success:
                        error_info = self.get_error_info(output)
                        repair_query = self.REPAIR_COMPILE_ERROR_PROMPT.format(
                            Rule_description=self.RULE.text_description,
                            source_code=checker_code,
                            failed_info=error_info
                        )
                        checker_code = self.generate_checker_with_query(repair_query)
                        self.save_checker(checker_code)
                        syntax_correct = self.jar_run(
                            [
                                "java -jar PMD-Style-ASTParser.jar checker checker.txt checker_ast.txt"],
                            self.RELATIVE_PATH)
                        if syntax_correct:
                            checker_code = self.class_is_correctly_imported(checker_code)
                            checker_code = self.super_is_correctly_used(checker_code)
                            checker_code = self.name_is_correctly_used(checker_code, self.RULE.name)
                            self.TEST_ENVIRONMENT.create_test(self.RULE.checker_test_path, checker_code, candidate_testcase, self.RULE.cases_set_xml_path, self.RULE.cases_test_xml_path)
                            output, compile_success = self.TEST_ENVIRONMENT.run_compile()
                            bak_checker_code = checker_code
                            bak_output = output
                        else:
                            checker_code = bak_checker_code
                            output = bak_output
                            compile_success = False
                        if i > 2 or (i <= 2 and error_info == ""):
                            compile_success = False
                            single_success = False
                            break

                    if compile_success:
                        single_output, single_success = self.TEST_ENVIRONMENT.run_tests(self.RULE.name + "Test")
                        if single_success:
                            init_checker = Checker(checker_code, [current_case])
                            return single_success, init_checker

        return False, Checker("",[])

    def find_failed_case(self, parsed_output: str) -> Case:
        """
        select the case with smallest id
        :param parsed_output:
        :return:
        """
        fail_rule = [entry for entry in parsed_output if "error_rules_info" in entry]
        error_one = fail_rule[0]["error_rules_info"]
        min = 100
        for i in range(len(fail_rule)):
            error_output = fail_rule[i]["error_rules_info"]
            first_quote_index = error_output.find('"')
            first_space_index = error_output.find('case ', first_quote_index + 1)
            second_quote_index = error_output.find('"', first_quote_index + 1)
            error_order = error_output[first_space_index + 5:second_quote_index]
            if int(error_order) < min:
                min = int(error_order)
                error_one = fail_rule[i]["error_rules_info"]
        for case in self.ALL_TEST_CASES:
            if case.get_description() == error_one:
                return case

    def checker_augmentation(self, init_checker: Checker):

        test_env = TestChecker(self.framework_project_path)
        case_operator = CaseOperator()

        tree = ET.parse(self.RULE.cases_set_xml_path, parser=ET.XMLParser(encoding="utf-8"))
        root = tree.getroot()
        for test_code_elem in root.findall('.//test-code'):
            description = test_code_elem.find('description').text
            code = test_code_elem.find('code').text
            problem = test_code_elem.find('problem').text
            if problem == "0":
                flag = True
            else:
                flag = False
            case = Case(code, description, flag)
            self.ALL_TEST_CASES.append(case)

        passed_cases = init_checker.get_passed_cases()
        checker_code = init_checker.get_code()

        case_operator.move_cases_to_test_pool(self.ALL_TEST_CASES, self.SKIPPED_TEST_CASES, self.RULE.cases_set_xml_path,
                                              self.RULE.cases_test_xml_path)
        all_cases_excluding_skipped_ones_test_output, all_cases_excluding_skipped_ones_test_success = test_env.run_tests(self.RULE.name + "Test")
        test_round = 0
        while not all_cases_excluding_skipped_ones_test_success:
            test_round += 1
            mvn_parser = MavenOutputParser()
            parsed_output = mvn_parser.parse(all_cases_excluding_skipped_ones_test_output)
            current_failed_case = self.find_failed_case(parsed_output)
            candidate_cases = passed_cases
            candidate_cases.append(current_failed_case)
            current_failed_case_description = current_failed_case.get_description()

            current_failed_case_AST, current_failed_case_AST_nodes = self.get_AST(current_failed_case)
            for node in current_failed_case_AST_nodes:
                if node not in self.EMBEDDED_AST_NODES:
                    embedding_apis([node])

            case_operator.move_cases_to_test_pool(candidate_cases, self.SKIPPED_TEST_CASES, self.RULE.cases_set_xml_path,
                                                              self.RULE.cases_test_xml_path)
            candidate_cases_test_success = False
            rounds=1
            while not candidate_cases_test_success:
                if rounds > 5:
                    self.SKIPPED_TEST_CASES.append(current_failed_case_description)
                    break

                checker_code = self.checker_generate_with_single_case_and_checker(current_failed_case, current_failed_case_AST, current_failed_case_AST_nodes, checker_code)
                self.save_checker(checker_code)

                checker_syntax_correct = self.jar_run(
                    [
                        "java -jar PMD-Style-ASTParser.jar checker checker.txt checker_ast.txt"],
                    self.RELATIVE_PATH)

                if not checker_syntax_correct:
                    candidate_cases_test_success = False
                else:
                    rounds += 1
                    checker_code = self.class_is_correctly_imported(checker_code)
                    checker_code = self.super_is_correctly_used(checker_code)
                    checker_code = self.name_is_correctly_used(checker_code, self.RULE.name)
                    test_env.create_test(self.RULE.checker_test_path, checker_code, candidate_cases, self.RULE.cases_set_xml_path, self.RULE.cases_test_xml_path)
                    checker_compile_output, checker_compile_success = test_env.run_compile()
                    i = 1
                    bak_checker_code = checker_code
                    bak_output = checker_compile_output
                    while not checker_compile_success:
                        error_info = self.get_error_info(checker_compile_output)
                        repair_query = self.REPAIR_COMPILE_ERROR_PROMPT.format(
                            Rule_description=self.RULE.text_description,
                            source_code=checker_code,
                            failed_info=error_info
                        )
                        checker_code = self.generate_checker_with_query(repair_query)
                        self.save_checker(checker_code)
                        syntax_correct = self.jar_run(
                            [
                                "java -jar PMD-Style-ASTParser.jar checker checker.txt checker_ast.txt"],
                            self.RELATIVE_PATH)
                        if syntax_correct:
                            checker_code = self.class_is_correctly_imported(checker_code)
                            checker_code = self.super_is_correctly_used(checker_code)
                            checker_code = self.name_is_correctly_used(checker_code, self.RULE.name)
                            test_env.create_test(self.RULE.checker_test_path, checker_code, candidate_cases, self.RULE.cases_set_xml_path, self.RULE.cases_test_xml_path)
                            output, compile_success = test_env.run_compile()
                            bak_checker_code = checker_code
                            bak_output = output
                        else:
                            checker_code = bak_checker_code
                            checker_compile_output = bak_output
                            checker_compile_success = False
                        i += 1

                        if i > 2:
                            checker_compile_success = False
                            candidate_cases_test_success = False
                            break

                    if checker_compile_success:
                        candidate_cases_test_output, candidate_cases_test_success = test_env.run_tests(self.RULE.name + "Test")

            if candidate_cases_test_success:
                self.RULE.add_checker(Checker(checker_code, candidate_cases))
                case_operator.move_cases_to_test_pool(self.ALL_TEST_CASES, self.SKIPPED_TEST_CASES,
                                                      self.RULE.cases_set_xml_path,
                                                      self.RULE.cases_test_xml_path)
                all_cases_excluding_skipped_ones_test_output, all_cases_excluding_skipped_ones_test_success = test_env.run_tests(self.RULE.name + "Test")
                break



