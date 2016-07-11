import abc
import json
from pprint import pprint


class API:
    __metaclass__ = abc.ABCMeta

    def __init__(self, system):
        self.system = system
        self.query = None
        self.response = None
        self.parsed_response = None
    
    @abc.abstractmethod
    def get_response(self, text):
        request = self.system.text_request()
        request.query = text
        response = request.getresponse()
        self.response = response.read()
        return self.response

    @abc.abstractmethod
    def parse(self, debugging=False):
        # if debugging:
        #     print("Response before loading:", self.response)
        self.parsed_response = json.loads(self.response.decode('UTF-8'))
        if debugging:
            print("Response after loading:")
            print(json.dumps(self.parsed_response, indent=2, sort_keys=True))
        return self.parsed_response
