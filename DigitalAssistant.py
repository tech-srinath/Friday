from __init__ import *
from actions import *

class Assistant:
    def __init__(self):
        self.action = None
        self.answer = None
        self.api_reply = None
        self.debugging = False
        self.error = None
        self.perception = None
        self.question = None
        self.talking = True
        self._debug = {
            "Reply": self.api_reply,
            "Question": self.question,
            "Error": self.error,
            "Intent": self.action
        }
    
    def listen(self, input_type='google'):
        try:
            self.perception = listen(input_type)
        except KeyboardInterrupt:
            self.action = "Shut down"
            self.talking = False
        else:
            self.action, self.question, self.api_reply = self.perception
    
    def debug(self):
        return self._debug
    
    def execute(self):
        execute = causality(self.action)
        self.answer = execute(self.question) if callable(execute) else execute




def main():
    assistant = Assistant()
    
    while assistant.talking:
        assistant.listen('google')
        assistant.execute()
        
        if type(assistant.answer) == tuple: # Shut down
            say(assistant.answer[0])
            break
        
        choices = [assistant.api_reply, assistant.answer] # Determines order of importance
        for response in choices:
            if response:
                output = response
                break
        
        try:
            pprint.pprint(output)
        except UnicodeEncodeError:
            print("Unicode is lovely.")
        say(output)
        
if __name__ == '__main__':
    main()
