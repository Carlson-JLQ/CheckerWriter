from entity.checker import Checker

# from tool.entity.checker import Checker
class Rule:
    def __init__(self, name: str, text_description: str, checker_test_path: str, cases_set_xml_path: str, cases_test_xml_path: str):
        self.name = name
        self.text_description = text_description
        self.cases_set_xml_path = cases_set_xml_path
        self.checker_test_path = checker_test_path
        self.cases_test_xml_path = cases_test_xml_path
        self.checker = []


    def add_checker(self, checker: Checker):
        self.checker.append(checker)
    
