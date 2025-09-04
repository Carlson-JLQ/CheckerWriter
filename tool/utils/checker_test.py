import os
from subprocess import check_output, CalledProcessError, STDOUT
import xml.etree.ElementTree as ET
from entity.case import Case

class TestChecker(object):
    def __init__(self, framework_project_path: str) -> None:
        self.framework_project_path = framework_project_path

    def create_test(self, checker_path: str, checker_code: str, candidate_cases: list[Case], cases_set_xml_path: str, store_candidate_cases_to_test_xml_path: str):

        # prepare checker to test
        with open(checker_path, "w", encoding="utf-8") as f:
            f.write(checker_code)

        # prepare test cases to test
        tree = ET.parse(cases_set_xml_path, parser=ET.XMLParser(encoding="utf-8"))
        root = tree.getroot()
        candidate_cases_name = []
        for case in candidate_cases:
            candidate_cases_name.append(case.get_description())
        for test_code_elem in root.findall('.//test-code'):
            problem = test_code_elem.find('description').text
            if problem not in candidate_cases_name:
                root.remove(test_code_elem)
        tree.write(store_candidate_cases_to_test_xml_path)

    def maven_run(self, command: list, cwd: str):
        pwd = os.getcwd()
        try:
            if cwd is not None:
                os.chdir(cwd)
            output_bytes = check_output(command, stderr=STDOUT, cwd=cwd, shell=True)
            output = output_bytes.decode('utf-8', errors='replace')
            success = True
        except CalledProcessError as e:
            output = e.output.decode('utf-8', errors='replace')
            success = False
        finally:
            os.chdir(pwd)
        return output, success

    def run_tests(self, rule: str):
        output, success = self.maven_run(["mvn", "test", "-Dtest="+rule], self.framework_project_path)
        return output, success

    def run_compile(self):
        self.maven_run(["mvn", "clean"], self.framework_project_path)
        output, success = self.maven_run(["mvn", "compile"], self.framework_project_path)
        return output, success
