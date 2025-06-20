import time

from tool.entity.rule import Rule
from tool.generator import CheckerGenerator

def main():

    rule_name = ""
    rule_description = ""
    rule_checker_path_in_pmd = ""
    rule_cases_xml_path = ""
    rule_cases_path_in_pmd = ""

    rule = Rule(rule_name, rule_description, rule_checker_path_in_pmd, rule_cases_xml_path, rule_cases_path_in_pmd)

    # pmd-project-url: https://github.com/pmd/pmd/tree/pmd_releases/7.0.0-rc4
    pmd_project = "../pmd/pmd_project/"

    checker_generator = CheckerGenerator(
        "https://api.deepseek.com/v1",
        "your openai_key",
        "deepseek-v3",
        rule,
        pmd_project
    )

    # !!!!!!!!!!!!!!
    # you must ensure the pmd project successfully compile before following checker generation

    print("begin")
    print()
    time1 = time.time()

    rule_with_checker = checker_generator.checker_generate()

    print("this cases fail to generate checker within five rounds, so they are skipped.")
    print(rule_with_checker.SKIPPED_TEST_CASES)
    # the last element in outputted list is the final checker which we want
    print("each generated checker and its passed cases are here:")
    print(rule_with_checker.RULE.get_checker())

    time2 = time.time()
    print("end")
    print()
    execution_time = time2 - time1
    print("time cost: " + str(execution_time) + " seconds")


if __name__ == "__main__":
    main()
