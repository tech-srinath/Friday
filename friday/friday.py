# -*- coding: utf-8 -*-

import ai_interface
import apiai
import os
import random
import re
import speech_recognition as sr
import yaml
from gtts import gTTS
from platform import system
from pprint import pprint
from subprocess import call
from yapsy.PluginManager import PluginManager

file_path = os.path.relpath("SETTINGS")
settings_file = open(file_path)
settings = yaml.load(settings_file)
settings_file.close()

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
    def __init__(self):
        """
        Some of the variables used are redundant or should be renamed to better reflect their purpose.
        :param input_system: How the system should request input: google, local, text
        :param output_system: How should answers be returned to the user: audio, text, both
        :param spoken_language: The language of the voice that the assistant uses
        :param speech_file_location: Where generated speech files should be saved
        :param speech_file_name: What generated speech files should be called
        :param speak: Determines if the system plays sound files that are generated
        :param debugging: Whether a verbose debug log should be printed to the console.
        """
        self.ai = ai_interface.API(apiai.ApiAI(settings['CLIENT_ACCESS_TOKEN'],
                                               settings['SUBSCRIPTION_KEY']))
        self.debugging = settings['debugging']
        self.spoken_language = settings['spoken language']
        self.input_system = settings['input system']  # google, local, text
        self.output_system = settings['output system']  # both, audio, text
        self.speech_file_location = settings['speech file location']  # .
        self.speech_file_name = settings['speech file name']  # audio response
        self.speak = settings['speak']  # True
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
        # self.reactions = {
        #     "manage.app_close": manage.app_close,  # General command for closing the app was given.
        #     "input.unknown": wolfram_query,  # If the AI system doesn't know what's being asked
        #     "wisdom.unknown": wolfram_query,  # If the AI system doesn't know the answer to what's being asked
        #     "wisdom.physics": wolfram_query,  # Wolfram for physics, yay
        #     "wisdom.languages": wolfram_query,
        #     "wisdom.institutions": wolfram_query,
        #     "wisdom.words": wolfram_query,
        #     "calculator.math": wolfram_query,  # Use Wolfram for math
        # }

        if settings['input system'] != 'text':
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone(device_index=settings['DEVICE'],
                                            sample_rate=settings['RATE'],
                                            chunk_size=settings['CHUNK'])

            if settings['input_system'] == 'google':
                with self.microphone as source:
                    if settings['debugging']:
                        print("Adjusting to ambient noise.")
                        # we only need to calibrate once, before we start listening
                    self.recognizer.adjust_for_ambient_noise(source)
                    # recognizer.energy_threshold = 200

        # Build the manager
        self.manager = PluginManager()
        # Tell it the default place(s) where to find plugins
        self.manager.setPluginPlaces(settings["plugin folder"])
        # Load all plugins
        self.manager.locatePlugins()
        self.manager.loadPlugins()
        #self.manager.collectPlugins()

        self.plugins = {}
        # Activate all loaded plugins
        for plugin in self.manager.getAllPlugins():
            self.plugins[plugin.name] = plugin.plugin_object

    def _local_stt(self):
        pass

    def _apiai_stt(self):
        from math import log
        import audioop
        import pyaudio
        import time
        resampler = apiai.Resampler(source_samplerate=settings['RATE'])
        request = self.ai.voice_request()
        vad = apiai.VAD()

        def callback(in_data, frame_count):
            frames, data = resampler.resample(in_data, frame_count)
            if settings.show_decibels:
                decibel = 20 * log(audioop.rms(data, 2) + 1, 10)
                print(decibel)
            state = vad.processFrame(frames)
            request.send(data)
            state_signal = pyaudio.paContinue if state == 1 else pyaudio.paComplete
            return in_data, state_signal

        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt32, input=True, output=False, stream_callback=callback,
                        channels=settings['CHANNELS'], rate=settings['RATE'], frames_per_buffer=settings['CHUNK'])
        stream.start_stream()
        print("Speak!")
        while stream.is_active():
            time.sleep(0.1)
        stream.stop_stream()
        stream.close()
        p.terminate()

    def _google_stt(self):
        """
        Uses Google's Speech to Text engine to
        understand speech and convert it into
        text.
        :return: String, either the spoken text or error text.
        """
        print("Please speak now")
        # Listen to the microphone set up in the __init__ file.
        with self.microphone as mic_source:
            audio = self.recognizer.listen(mic_source)
        print("Processing audio")
        try:
            # Try to recognize the text
            return self.recognizer.recognize_google(audio, show_all=self.debugging)
        except sr.UnknownValueError:  # speech is unintelligible
            return "Google could not understand the audio."
        except sr.RequestError:
            return "Could not request results from Google's speech recognition service."

    def listen(self):
        # Default value.
        # request_type = None
        if self.input_system == 'google':
            question = self._google_stt()
        else:
            question = input("Input your query: ")
        print("Wait for response...")
        # Get a response from the AI using the api interface.
        self.ai.get_response(question)
        # Clean up the response and turn it into a Python object that can be read
        response = self.ai.parse(self.debugging)
        return response
        # This heavily assumes the response formats, make our own
        # which every service converts their response into?
        # Should I just read the JSON directly and pass around
        # the response object? It'd require me to standardize
        # things a bit, but it would work and that'd probably
        # be better for the long term.
        # if 'result' in response:
        #     result = response['result']  # Assumes we're using gTTS
        #     # Get the text that is supposed to be spoken aloud
        #     reply = result['fulfillment']['speech']
        #     # Get what the service thought you said
        #     question = result['resolvedQuery']
        #     if self.input_system == 'google':
        #         print("You said: " + question)
        #     if 'parameters' in response['result']:
        #         if 'request_type' in response['result']['parameters']:
        #             request_type = response['result']['parameters']['request_type']
        #         else:
        #             request_type = None
        # else:
        #     result = {}
        #     reply = None
        #     question = None
        #
        # # Get the classification for the input, this includes
        # # whether it is a request about some information or
        # # a specific action that the user wants the bot to
        # # perform, etc.
        # if 'action' in result:
        #     action = result['action']
        # else:
        #     action = 'wisdom.unknown'
        # return action, question, reply, request_type

    def think(self, request):
        return any(plugin.can_perform(request)
                   for name, plugin in self.plugins.items())

    def perform(self, request):
        # Trigger 'some request' from the loaded plugins
        for name, plugin in self.plugins.items():
            if plugin.can_perform(request):
                pprint(plugin.perform(request))

    def refuse(self):
        print("Can't do that")
        pass

    def apologize(self):
        print("I failed to do that, sorry.")
        pass

    def get_input_from_user(self):
        try:
            self.perception = self.listen()
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
        else:  # Otherwise use a boxed response.
            self.response = random.choice(self.confused_responses)

    def _print_response(self, pretty_print=True):
        try:
            if pretty_print:
                pprint(self.response)
            else:
                print(self.response)
            if self.debugging:
                print("main function output:", self.response)
        except UnicodeEncodeError:
            print("Unicode is lovely.")

    def _speak_response(self):
        self.say(self.response, home=self.speech_file_location,
                 title=self.speech_file_name, speak_aloud=self.speak)

    def respond(self):
        if self.output_system == "audio":
            self._speak_response(self)
        elif self.output_system == "text":
            self._print_response(self, self.pretty_print)
        else:
            self._print_response(self, self.pretty_print)
            self._speak_response(self)

    def say(self, message, speak_aloud=True,
            title='Speak'):
        message = str(message)
        if not message.strip():
            print("No text to speak.")
            return
        computer_os = system()
        folder, file_name = os.path.split(title)
        folder_path = os.path.join(self.speech_file_location,
                                   folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        home = settings['home']
        if self.input_system == 'google':
            # Create the MP3 file which will speak the text
            title += '.wav'
            path = os.path.join(home, title)
            tts = gTTS(message, lang=self.spoken_language)
            tts.save(path)

            speech_file = "start /MIN {}"
            if computer_os != 'Windows':
                speech_file = "mpg123 {}"

            speech_file = speech_file.format(os.path.join(home, title))
        else:
            # Create the Visual Basic code which will speak the text
            title += '.vbs'
            path = os.path.join(home, title)
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
