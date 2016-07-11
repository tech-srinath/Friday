# Friday.py
try:
    from .__init__ import *
    from . import actions
except SystemError:
    from __init__ import *
    import actions
from gtts import gTTS
import os
import re
from platform import system
import random
from subprocess import call
from pprint import pprint


# """Example of Python client calling Knowledge Graph Search API."""
# import requests
#
# api_key = open('/home/zen/.api_key').read()
# query = 'Taylor Swift'
# service_url = 'https://kgsearch.googleapis.com/v1/entities:search'
# params = {
#     'query': query,
#     'limit': 10,
#     'indent': True,
#     'key': api_key,
# }
# response = requests.get(service_url, params=params).json()


class Friday:
    def __init__(self, ai_system, input_system='google', output_system='both', lang='en-au',
                 speech_file_location='.', speech_file_name='audio_response',
                 speak: boolean=True, debugging: boolean=False):
        '''
        Some of the variables used are redundant or should be renamed to better reflect their purpose.
        :param ai_system: The AI system that is to be referenced.
        :param input_system: How the system should request input: google, local, text
        :param output_system: How should answers be returned to the user: audio, text, both
        :param lang: The language of the voice that the assistant uses
        :param speech_file_location: Where generated speech files should be saved
        :param speech_file_name: What generated speech files should be called
        :param speak: Determines if the system plays sound files that are generated
        :param debugging: Whether a verbose debug log should be printed to the console.
        '''
        self.ai = ai_system
        self.debugging = debugging
        self.lang = lang
        self.input_system = input_system
        self.output_system = output_system
        self.speak = speak
        self.speech_file_location = speech_file_location
        self.speech_file_name = speech_file_name
        # The specific function that should be executed.
        self.action_category = None
        # What the assistant hears and what it decides to say back/do
        self.perception = None
        # The question that the assistant hears
        self.question = None
        # The chosen, spoken response given to the user.
        self.response = None
        # Whether Friday is active
        self.is_active = True
        # What type of question is being asked.
        self.request_type = None
        # Whether to pretty-print the text output
        self.pretty_print = True
        # The response to a query and an action that could be applied to it.
        self.answer = [None, None]
        # The response to a query given by an API
        self.api_reply = [None, None]
        # If a service raises an error, it'll be stored here
        self.error = None
        # Returned by a service when it does not understand an input. Ensures quality answers.
        # There has to be an easier way than this.
        self.confused_responses = [
            "Could you reword that last statement?",
            "I beg your pardon, I don't understand.",
            "I'm not sure I follow.",
            "I'm a bit confused.",
            "Sorry, that didn't make sense to me.",
            "I'm not quite sure I understand.",
            "Can you rephrase that, please?",
            "I\x92'm afraid I don't know much about that yet.",
            "I'm afraid I don't know much about that yet.",
            "Sorry, come again?",
            "Hold on, what was that?",
            "Can you try repeating that, please?",
            "My apologies, I didn't grasp that last part.",
            "Sorry, can you please start over?",
            "I don't quite get what you're asking.",
            "I'd love to help, but I don't understand.",
            "You haven't taught me about that yet.",
            "I'm afraid that's not in my skill set just yet.",
            "I'm sorry, I'm not too familiar with that yet.",
        ]
        self.reactions = {
            "manage.app_close": manage.app_close,  # General command for closing the app was given.
            "input.unknown": wolfram_query,  # If the AI system doesn't know what's being asked
            "wisdom.unknown": wolfram_query,  # If the AI system doesn't know the answer to what's being asked
            "wisdom.physics": wolfram_query,  # Wolfram for physics, yay
            "wisdom.languages": wolfram_query,
            "wisdom.institutions": wolfram_query,
            "wisdom.words": wolfram_query,
            "calculator.math": wolfram_query,  # Use Wolfram for math
        }

    def get_input_from_user(self, input_type='google', debugging=False):
        try:
            self.perception = actions.listen(input_type, debugging)
        except KeyboardInterrupt:
            if settings.debugging:
                print("Received keyboard interrupt signal. Shutting down.")
            self.action_category = ["Shut down", manage.app_close]
            self.is_active = False
        else:
            self.action_category, self.question, self.api_reply[0], self.request_type = self.perception

    def get_reaction(self, intent_classification):
        """
        Handles getting an action to be executed
        depending on the input.
        :param intent_classification: A general classification for a query
        :return: A function to be executed as a result of
        the query or None if a reaction does not exist.
        """
        return self.reactions.get(intent_classification, None)

    def perform_action(self):
        """
        Tries to execute the function associated
        with an input classification.
        If the action exists it will be executed
        with the question passed to it as an
        argument.
        The answer will be stored in the
        self.answer variable as a list with the
        second item being the action that was
        executed. If no action was found, the
        second item will be None.

        :return: No return value.
        """
        action = actions.get_reaction(self.action_category)
        if self.debugging:
            print("API Action Category:", self.action_category)
            print("Function corresponding to category:", action)
            print("API Reply:", self.api_reply)
            print("Response Type:", self.request_type)

        # Send all wisdom or general-knowledge based question to Wolfram Alpha.
        if "wisdom" in self.action_category:
            action = actions.wolfram_query

        # Follows answer format of [text, action]
        if action is not None:
            self.answer = [action(self.question), action]
        else:
            self.answer = ["", None]

    def choose_response(self):
        """
        Loop through all the available responses
        from all installed services and pick
        one based on some conditions.
        Store the chosen response in the
        self.response variable.
        :return: No return value.
        """
        choices = [self.api_reply, self.answer]  # Determines order of importance
        if self.debugging:
            print(choices)
        # index = 0
        for response in choices:
            # if index == 0 and (self.request_type != 'whois' or self.request_type != 'whatis'):
            #     index += 1
            #     continue

            if response[0] and response[0] not in self.confused_responses:
                if self.debugging:
                    print(response)
                self.response = response[0]
                return
            # index += 1
        # If the intel service returned an intelligent, confused response. Use that; it's more dynamic.
        if self.debugging:
            print("No intelligent reply found, resorting to confusion.")
        if choices[0][0]:
            self.response = choices[0][0]
        else: # Otherwise use a boxed response.
            self.response = random.choice([
                "I don't understand.",
                "That went right over my head, could you rephrase?",
                "Hold on, what was that?"
            ])

    def respond(self):
        def print_response(self, pretty_print=True):
            try:
                if pretty_print:
                    pprint(self.response)
                else:
                    print(self.response)
                if self.debugging:
                    print("main function output:", self.response)
            except UnicodeEncodeError:
                print("Unicode is lovely.")

        def speak_response(self):
            self.say(self.response, home=self.speech_file_location,
                     title=self.speech_file_name, speak_aloud=self.speak)

        if self.output_system == "audio":
            speak_response(self)
        elif self.output_system == "text":
            print_response(self, self.pretty_print)
        else:
            print_response(self, self.pretty_print)
            speak_response(self)

    def say(self, message, speak_aloud=True,
            title='Speak', home='~'):
        message = str(message)
        if not message.strip():
            print("No text to speak.")
            return
        computer_os = system()
        folder = ''
        if '\\' in title:  # Wtf does this do outside Windows?
            folder = '/'.join(title.split('\\')[:-1])
        home += '/'
        folder_path = home + folder
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        path = home
        if self.input_system == 'google':
            # Create the MP3 file which will speak the text
            title += '.wav'
            path += title
            tts = gTTS(message, lang=self.lang)
            tts.save(path)
            speech_file = "start /MIN {}"
            if computer_os != 'Windows':
                speech_file = "mpg123 {}"
            speech_file = speech_file.format(home + title)
        else:
            # Create the Visual Basic code which will speak the text
            title += '.vbs'
            path += title
            message = re.sub('["\n\t]', '', message)  # Strip out characters that would be spoken by the system.
            if computer_os == "Windows":
                with open(path, 'w') as file:
                    file.write(
                        """
                        speaks="{}"
                        Dim speaks, speech
                        Set speech=CreateObject("sapi.spvoice")
                        speech.Speak speaks
                        """.format(message))
            # Set up the file to be executed
            speech_file = ["cscript.exe", title]
            if computer_os != "Windows":
                speech_file = ["espeak", message]
        if speak_aloud:
            try:
                call(speech_file)
            except FileNotFoundError:
                if self.debugging:
                    print("File not accessible:", speech_file)

    def received_kill_signal(self):
        if self.answer[1] == manage.app_close:  # Shut down
            self.response = self.answer[0]
            self.respond()
            self.is_active = False
            return True
        return False


