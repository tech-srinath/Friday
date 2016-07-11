try:
    from . import manage
    from . import user_info
    from . import settings
    from . import __init__
except SystemError:
    import manage
    import user_info
    import settings
    import __init__


# Move all these out into plugins

def google_tts(debugging=False):
    """
    Uses Google's Text to Speech engine to
    understand speech and convert it into
    text.
    :param debugging: Verbose debug output
    :return: String, either the spoken text or error text.
    """
    print("Please speak now")
    # Listen to the microphone set up in the __init__ file.
    with __init__.m as source:
            audio = __init__.r.listen(source)
    print("Processing audio")
    try:
        # Try to recognize the text
        return __init__.r.recognize_google(audio, show_all=debugging)
    except __init__.sr.UnknownValueError:  # speech is unintelligible
        return "Google could not understand the audio."
    except __init__.sr.RequestError:
        return "Could not request results from Google's speech recognition service."


# No longer being used. Too many dependencies
# Could possibly be rewritten, so it isn't being thrown out yet.
# Also a misnomer since it uses the API.AI speech recognition service.
# Could be written to use Sphinx. That might be best since that's fast.
def local_speech_recognition():
    import apiai
    from .__init__ import ai
    from math import log
    import audioop
    import pyaudio
    import time
    resampler = apiai.Resampler(source_samplerate=settings.RATE)
    request = ai.voice_request()
    vad = apiai.VAD()
    
    def callback(in_data, frame_count):
        frames, data = resampler.resample(in_data, frame_count)
        if settings.show_decibels:
            decibel = 20 * log(audioop.rms(data, 2)+1, 10)
            print(decibel)
        state = vad.processFrame(frames)
        request.send(data)
        state_signal = pyaudio.paContinue if state == 1 else pyaudio.paComplete
        return in_data, state_signal

    p = pyaudio.PyAudio()
    stream = p.open(format=settings.FORMAT, channels=settings.CHANNELS,
                    rate=settings.RATE, input=True,
                    output=False, frames_per_buffer=settings.CHUNK,
                    stream_callback=callback)
    stream.start_stream()
    print("Speak!")
    while stream.is_active():
        time.sleep(0.1)
    stream.stop_stream()
    stream.close()
    p.terminate()


def listen(input_type='google', debugging=False):
    # Default value.
    request_type = None
    if input_type == 'google':
        question = google_tts(debugging)
    else:
        question = input("Input your query: ")
    print("Wait for response...")
    # Get a response from the AI using the api interface.
    # This should NOT be in __init__
    __init__.ai.get_response(question)
    # Clean up the response and turn it into a Python object that can be read
    response = __init__.ai.parse(debugging)  # Need to work on the interface

    # This heavily assumes the response formats, make our own
    # which every service converts their response into?
    # Should I just read the JSON directly and pass around
    # the response object? It'd require me to standardize
    # things a bit, but it would work and that'd probably
    # be better for the long term.
    if 'result' in response:
        result = response['result']  # Assumes we're using gTTS
        # Get the text that is supposed to be spoken aloud
        reply = result['fulfillment']['speech']
        # Get what the service thought you said
        question = result['resolvedQuery']
        if input_type == 'google':
            print("You said: " + question)
        if 'parameters' in response['result']:
            if 'request_type' in response['result']['parameters']:
                request_type = response['result']['parameters']['request_type']
            else:
                request_type = None
    else:
        result = {}
        reply = None
        question = None

    # Get the classification for the input, this includes
    # whether it is a request about some information or
    # a specific action that the user wants the bot to
    # perform, etc.
    if 'action' in result:
        action = result['action']
    else:
        action = 'wisdom.unknown'
    return action, question, reply, request_type


# Rework this so it isn't returning function calls.



