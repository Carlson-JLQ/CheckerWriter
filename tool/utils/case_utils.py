
import xml.etree.ElementTree as ET

from entity.case import Case

#对测试用例进行增删改查等操作
class CaseOperator(object):

    def delete_failed_testcases_from_cases_set(self, test_case: str, testcase_set_xml_path: str):
        """
        delete specified test case from case set
        :param test_case: case to delete
        :param testcase_set_xml_path: test case set path
        :return: None
        """
        tree = ET.parse(testcase_set_xml_path, parser=ET.XMLParser(encoding="utf-8"))
        root = tree.getroot()
        for test_code_elem in root.findall('.//test-code'):
            problem = test_code_elem.find('description').text
            if problem == test_case:
                root.remove(test_code_elem)
        tree.write(testcase_set_xml_path)

    def move_cases_to_test_pool(self, candidate_cases: list[Case], skipped_cases: list[Case], cases_set_xml_path: str, cases_test_xml_path: str):
        """
        reset framework project with test case set to select failed test case
        :param testcase_set_xml_path: test case set
        :param rule_testcase_xml_filepath_in_pmd_project: test case path in framework project
        :return:
        """
        candidate_cases_names = []
        for case in candidate_cases:
            candidate_cases_names.append(case.get_description())

        skipped_cases_names = []
        for case in skipped_cases:
            skipped_cases_names.append(case.get_description())

        tree = ET.parse(cases_set_xml_path, parser=ET.XMLParser(encoding="utf-8"))
        root = tree.getroot()
        for test_code_elem in root.findall('.//test-code'):
            des = test_code_elem.find('description').text
            if des not in candidate_cases_names or des in skipped_cases_names:
                root.remove(test_code_elem)
        tree.write(cases_test_xml_path)

    def get_cases_that_are_already_passed_in_previewer_process(self, passed_testcase: list, testcase_set_xml_path: str):
        """

        get test cases that are already passed
        :param passed_testcase: test cases that are already passed in previewer rounds
        :param testcase_set_xml_path: test case set path
        :return: code of test cases
        """
        xml_file_path = testcase_set_xml_path
        tree = ET.parse(xml_file_path, parser=ET.XMLParser(encoding="utf-8"))
        root = tree.getroot()
        passed_testcase_code = ""
        for test_code_elem in root.findall('.//test-code'):
            problem = test_code_elem.find('description').text
            problem_num = int(test_code_elem.find('expected-problems').text)
            if problem in passed_testcase:
                code = test_code_elem.find('code').text.strip()
                if code.startswith("//"):
                    index = code.find("\n")
                    code = code[index + 1:]
                if problem_num > 0:
                    passed_testcase_code = passed_testcase_code + "This checker has passed this negative testcase:\n" + code + "\n"
                else:
                    passed_testcase_code = passed_testcase_code + "This checker has passed this positive testcase:\n" + code + "\n"
        return passed_testcase_code

    def select_negative_case(self, cases: list[Case], skipped_cases: list[Case]) -> Case:
        """
        select first negative case
        :param xml_path: test case path in framework project
        :return: None
        """
        for case in cases:
            flag = case.get_flag()
            if not flag and case not in skipped_cases:
                return case

    def select_name_specified_case(self, des: str, xml_path: str):
        """
        select test case with specified name
        :param des: description of test case
        :param xml_path: test case path in framework project
        :return: None
        """
        xml_file_path = xml_path
        tree = ET.parse(xml_file_path, parser=ET.XMLParser(encoding="utf-8"))
        root = tree.getroot()
        for test_code_elem in root.findall('.//test-code'):
            description = root.find('description').text
            if des == description:
                code_elem = ET.ElementTree(test_code_elem)
                code_elem.write("selected_case.xml", encoding="utf-8", xml_declaration=True)


    def count_negative_cases(self, cases: list[Case]):
        """
        count the number of negative cases(except for deleted ones)
        :param xml_path: test case path in original project
        :return: number of negative cases
        """
        count = 0
        for case in cases:
            flag = case.get_flag()
            if not flag:
                count = count + 1
        return count

    def count_all_cases(self, cases: list[Case]):
        """
        count the number of cases(except for deleted ones)
        :param xml_path: test case path in original project
        :return: number of test cases
        """
        count = len(cases)
        return count

    def get_code_of_current_case(self):
        """
        get source code of selected case in 'selected_case.xml'
        :return: code of selected case
        """
        xml_file_path = "selected_case.xml"
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        code_elem = root.find('code')
        testcase = code_elem.text.strip() if code_elem is not None and code_elem.text is not None else ""
        description = root.find('description').text
        expected_problems = root.find('expected-problems').text
        testcase = testcase + "\n" + "The description of this test case is: " + description + "\n" + "The number of violating the rule in this test case is: " + expected_problems + "\n"

        return testcase

    def get_description_of_current_case(self):
        """
        get textual description of selected case in 'selected_case.xml'
        :return: description of selected case
        """
        xml_file_path = "selected_case.xml"
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        description = root.find('description').text
        return description

    def get_error_num_of_current_case(self):
        """
        get the number of violations in selected case in 'selected_case.xml'
        :return: number of violating the rule in selected case
        """
        xml_file_path = "selected_case.xml"
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        num = root.find('expected-problems').text
        return num
