# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from friday import ai_interface
from gtts import gTTS
from platform import system
from subprocess import call
from yapsy.PluginManager import PluginManager

import apiai
import click
import os
import re
import speech_recognition as sr
import yaml

click.disable_unicode_literals_warning = True

directory_path = os.path.dirname(__file__)
file_path = os.path.join(directory_path, "SETTINGS")
settings_file = open(file_path)
settings = yaml.load(settings_file)
settings_file.close()


class Friday:
    def __init__(self):
        self.ai = ai_interface.API(apiai.ApiAI(settings['CLIENT_ACCESS_TOKEN'],
                                               settings['SUBSCRIPTION_KEY']))
        self.debugging = settings['debugging']
        self.spoken_language = settings['spoken language']
        self.input_system = settings['input system']  # google, local, text
        self.output_system = settings['output system']  # both, audio, text
        self.speech_file_location = settings['speech file location']  # .
        self.speech_file_name = settings['speech file name']  # audio response
        self.speak = settings['speak']  # True
        # The question that the assistant hears
        self.question = None
        # The chosen, spoken response given to the user.
        self.response = None
        # Whether Friday is active
        self.is_active = True
        # What type of question is being asked.
        self.request_type = None
        if settings['input system'] != 'text':
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone(device_index=settings['DEVICE'],
                                            sample_rate=settings['RATE'],
                                            chunk_size=settings['CHUNK'])

            if settings['input_system'] == 'google':
                with self.microphone as source:
                    if settings['debugging']:
                        click.echo("Adjusting to ambient noise.")
                        # we only need to calibrate once, before we start listening
                    self.recognizer.adjust_for_ambient_noise(source)

        # Build the manager
        self.manager = PluginManager()
        # Tell it the default place(s) where to find plugins
        self.manager.setPluginPlaces(settings["plugin folder"])
        # Load all plugins
        self.manager.locatePlugins()
        self.manager.loadPlugins()

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
                click.echo(decibel)
            state = vad.processFrame(frames)
            request.send(data)
            state_signal = pyaudio.paContinue if state == 1 else pyaudio.paComplete
            return in_data, state_signal

        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt32, input=True, output=False, stream_callback=callback,
                        channels=settings['CHANNELS'], rate=settings['RATE'], frames_per_buffer=settings['CHUNK'])
        stream.start_stream()
        click.echo("Speak!")
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
        click.echo("Please speak now")
        # Listen to the microphone set up in the __init__ file.
        with self.microphone as mic_source:
            audio = self.recognizer.listen(mic_source)
        click.echo("Processing audio")
        try:
            # Try to recognize the text
            return self.recognizer.recognize_google(audio, show_all=self.debugging)
        except sr.UnknownValueError:  # speech is unintelligible
            return "Google could not understand the audio."
        except sr.RequestError:
            return "Could not request results from Google's speech recognition service."

    def listen(self):
        # Default value.
        # TODO: Input plugin system goes here
        # Plugins should be used for getting input so users can build their
        # own custom front-end to the application.
        # This will allow the speech to text functions to be moved out of the
        # main class and into their own plugins.
        if self.input_system == 'google':
            self.question = self._google_stt()
        else:
            self.question = click.prompt("Input your query")

        # TODO: Loading plugin system goes here
        # Eventually I want people to be able to build custom behavior
        # that executes when the response is being fetched. So there could
        # be a loading screen that plays music or something for example.
        click.echo("Wait for response...")
        # Get a response from the AI using the api interface.
        self.ai.get_response(self.question)
        # Clean up the response and turn it into a Python object that can be read
        self.response = self.ai.parse()
        return self.response

    def think(self, request):
        # TODO: Move plugins to a priority system
        # Eventually plugins should return an integer value which determines
        # their ordering when responding to a request, in the event multiple
        # plugins are able to respond to the same request.
        # This may eventually allow for watchdog plugins which check for
        # erroneous requests and alert the system by returning negative (Maybe)
        # priorities, which can then be used to safeguard a user's system or
        # settings.
        return any(plugin.can_perform(self, request)
                   for name, plugin in self.plugins.items())

    def perform(self, request):
        # Trigger 'some request' from the loaded plugins
        for name, plugin in self.plugins.items():
            if plugin.can_perform(self, request):
                # TODO: Allow plugins to fail
                # Plugins will be able to return False in the event they fail,
                # allowing the system to then apologize to the user.
                plugin.perform(self, request)
        return True

    def refuse(self):
        # May become unnecessary as the plugins could be built to refuse
        # requests directly.
        click.echo("Can't do that")

    def apologize(self):
        # May eventually become unnecessary as plugins could be built to
        # return apologies directly.
        click.echo("I failed to do that, sorry.")

    def _print_response(self):
        click.echo(self.response)

    def _speak_response(self):
        self.say(self.response, title=self.speech_file_name, speak_aloud=self.speak)

    def respond(self):
        # TODO: Output plugin system goes here
        # Plugins should be used for providing output for the same reasons
        # that plugins should be used for providing input.
        if self.output_system == "audio":
            self._speak_response()
        elif self.output_system == "text":
            self._print_response()
        else:
            self._print_response()
            self._speak_response()

    def say(self, message, speak_aloud=True, title='Speak'):
        # May eventually be moved into its own plugin
        message = str(message)
        if not message.strip():
            click.echo("No text to speak.")
            return
        computer_os = system()
        folder = os.path.split(title)[0]
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
                    click.echo("File not accessible:", speech_file)

