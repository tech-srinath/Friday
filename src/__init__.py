__author__ = "Isaac Smith (Zenohm)"

# input_type can be 'local', 'google', or 'text'
input_type = 'text'
show_decibels = False
debugging = False


import audioop
import os
import pprint
import pyaudio
import speech_recognition as sr
import sys
import time
import wolframalpha
from gtts import gTTS
from math import log
from subprocess import call

import manage


home = os.path.expanduser("~")

try:
    import apiai
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
    import apiai


CHUNK = 2048
FORMAT = pyaudio.paInt32
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5


r = sr.Recognizer()
m = sr.Microphone()


CLIENT_ACCESS_TOKEN = '8386a96431bb49ef9d480732fb6a0e21'
SUBSCRIPTION_KEY = '3c972944-87a5-476e-8307-3349f34842e0' 

ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN, SUBSCRIPTION_KEY)

with m as source:
    r.adjust_for_ambient_noise(source) # we only need to calibrate once, before we start listening
#r.energy_threshold = 200
