import json


class API:
    # This may eventually be removed
    def __init__(self, system):
        self.system = system
        self.query = None
        self.response = None
        self.parsed_response = None

    def get_response(self, text):
        request = self.system.text_request()
        request.query = text
        response = request.getresponse()
        self.response = response.read()
        return self.response

    def parse(self):
        self.parsed_response = json.loads(self.response.decode('UTF-8'))
        return self.parsed_response
