class Case:
    def __init__(self, code: str, text_description: str, flag: bool):
        """
        init a test case
        :param code:
        :param text_description:
        """
        self.code = code
        self.text_description = text_description
        self.flag = flag

    def get_description(self):
        return self.text_description

    def get_code(self):
        return self.code

    def get_flag(self):
        return self.flag
