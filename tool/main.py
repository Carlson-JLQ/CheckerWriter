import json
import time
import sys
from entity.case import Case
from entity.checker import Checker
from entity.rule import Rule
from generator import CheckerGenerator

def main():

    # you need to fill in the address of 'base_dir' in the config file, which is the root directory of the current project
    #base地址是项目根目录 /home/jiliqiang/Research/CheckerWriter
    # read config file
    with open('config.json') as f:
        config = json.load(f)

    rule_name = "AvoidUsingOctalValuesRule"
    #这个规则是说整数字面量不应以零开头，因为这表示后续的数字将被解释为八进制值。
    rule_description = "Integer literals should not start with zero since this denotes that the rest of literal will be interpreted as an octal value."
    #规则AvoidUsingOctalValuesRule的检查器的路径，是PMD项目中的Java规则文件，可以检查这个规则有没有违反
    #相对路径：framework/pmd_project/pmd-java/src/main/java/net/sourceforge/pmd/lang/java/rule/errorprone/AvoidUsingOctalValuesRule.java
    #绝对路径：/home/jiliqiang/Research/CheckerWriter/framework/pmd_project/pmd-java/src/main/java/net/sourceforge/pmd/lang/java/rule/errorprone/AvoidUsingOctalValuesRule.java
    rule_checker_path_in_pmd = config['file_paths']['base_dir'] + config['file_paths']['pmd_project'] + "/src/main/java/net/sourceforge/pmd/lang/java/rule/errorprone/AvoidUsingOctalValuesRule.java"


    #规则的测试用例XML文件路径：experiment/experimental-20rules-test-suite/easy/AvoidUsingOctalValues.xml
    rule_cases_xml_path = config['file_paths']['base_dir'] + "/experiment/experimental-20rules-test-suite/easy/AvoidUsingOctalValues.xml"
    #PMD项目中测试用例的路径：framework/pmd_project/pmd-java/src/test/resources/net/sourceforge/pmd/lang/java/rule/errorprone/AvoidUsingOctalValuesTest.java
    rule_cases_path_in_pmd = config['file_paths']['base_dir'] + config['file_paths']['pmd_project'] + "/src/test/java/net/sourceforge/pmd/lang/java/rule/errorprone/AvoidUsingOctalValuesTest.java"
    # print("rule_cases_path_in_pmd: " + rule_cases_path_in_pmd)
    # print("rule_cases_xml_path: " + rule_cases_xml_path)
    rule = Rule(rule_name, rule_description, rule_checker_path_in_pmd, rule_cases_xml_path, rule_cases_path_in_pmd)

    pmd_project_path = config['file_paths']['base_dir'] + config['file_paths']['pmd_project']

    checker_generator = CheckerGenerator(
        "https://api.deepseek.com",
        "sk-e9e9fd48067b4737bb2b672ac745d1a9",
        "deepseek-reasoner",
        rule,
        pmd_project_path
    )

    # !!!!!!!!!!!!!!
    # you must ensure the framework project successfully compile before following checker generation

    print("begin")
    print()
    time1 = time.time()

    output = checker_generator.checker_generate()

    print("this cases fail to generate checker within five rounds, so they are skipped.")
   
    # print(output.SKIPPED_TEST_CASES)
    # the last element in outputted list is the final checker which we want
    print("each generated checker and its passed cases are here:")
    # print(output.RULE.get_checker())

    time2 = time.time()
    print("end")
    print()
    execution_time = time2 - time1
    print("time cost: " + str(execution_time) + " seconds")


if __name__ == "__main__":
    main()
