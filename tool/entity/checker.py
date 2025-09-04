# from tool.entity.case import Case
from typing import List, Optional
from entity.case import Case
class Checker:
    def __init__(self, code: str, passed_cases: List[Case] = None):
        """
        init a checker
        :param code:
        :param passed_cases:
        """
        self.code = code
        self.passed_cases = passed_cases if passed_cases is not None else []  # 避免可变默认参数问题

    def get_passed_cases(self):
        return self.passed_cases

    def get_code(self):
        return self.code
