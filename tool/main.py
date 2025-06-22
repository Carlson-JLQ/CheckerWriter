import json
import time

from tool.entity.rule import Rule
from tool.generator import CheckerGenerator

def main():

    # you need to fill in the address of 'base_dir' in the config file, which is the root directory of the current project

    # read config file
    with open('../../config.json') as f:
        config = json.load(f)

    rule_name = "AvoidUsingOctalValuesRule"
    rule_description = "Integer literals should not start with zero since this denotes that the rest of literal will be interpreted as an octal value."
    rule_checker_path_in_pmd = config['file_paths']['base_dir'] + config['file_paths']['pmd_project'] + "/src/main/java/net/sourceforge/framework/lang/java/rule/errorprone/AvoidUsingOctalValuesRule.java"

    rule_cases_xml_path = config['file_paths']['base_dir'] + "experiment/experimental-20rules-test-suite/easy/AvoidUsingOctalValues.xml"
    rule_cases_path_in_pmd = config['file_paths']['base_dir'] + config['file_paths']['pmd_project'] + "/src/test/java/net/sourceforge/framework/lang/java/rule/errorprone/AvoidUsingOctalValuesTest.java"

    rule = Rule(rule_name, rule_description, rule_checker_path_in_pmd, rule_cases_xml_path, rule_cases_path_in_pmd)

    pmd_project_path = config['file_paths']['base_dir'] + config['file_paths']['pmd_project']

    checker_generator = CheckerGenerator(
        "https://api.deepseek.com/v1",
        "your openai_key",
        "deepseek-v3",
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
    print(output.SKIPPED_TEST_CASES)
    # the last element in outputted list is the final checker which we want
    print("each generated checker and its passed cases are here:")
    print(output.RULE.get_checker())

    time2 = time.time()
    print("end")
    print()
    execution_time = time2 - time1
    print("time cost: " + str(execution_time) + " seconds")


if __name__ == "__main__":
    main()
