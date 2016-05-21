import os
import pyaudio
# Program settings
# Input_type can be 'google', or 'text'
input_type = 'text'
# Only works with local text to speech
show_decibels = False
# Not implemented
show_confidence = False
# Enable verbose debugging messages
debugging = True
# Show complete response from google tts
verbose_tts_response = False
# Determine what service is used to convert text to speech, can be 'google' or 'local'
speech_system = 'local'
# Determines where the program should store files.
home = os.path.expanduser("~")

# Assume services aren't installed until proven otherwise
installed = {
    "apiai": False,
    "gtts":  False,
}

# Microphone settings
DEVICE = 2
CHUNK = 2048
FORMAT = pyaudio.paInt32
CHANNELS = 1
RATE = 48000
RECORD_SECONDS = 5
