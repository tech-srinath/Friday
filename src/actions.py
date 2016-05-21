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
            audio = __init__.r.input(source)
    print("Processing audio")
    try:
        # Try to recognize the text
        return __init__.r.recognize_google(audio, show_all=debugging)
    except __init__.sr.UnknownValueError:  # speech is unintelligible
        return "Google could not understand the audio."
    except __init__.sr.RequestError:
        return "Could not request results from Google's speech recognition service."


# No longer being used. Too dependent on one platform. Too many dependencies
# Could possibly be rewritten, so it isn't being thrown out yet.
# Also a misnomer since it uses the API.AI speech recognition service.
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
    # This heavily assumes the response formats, make our own
    # which every service converts their response into?
    if debugging:
        print(input_type)
    if input_type == 'google':
        question = google_tts(debugging)
    else:
        question = input("Input your query: ")
    print("Wait for response...")
    # Get a response from the AI using the api interface.
    __init__.ai.get_response(question)
    # Clean up the response and turn it into a Python object that can be read
    response = __init__.ai.parse(debugging)  # Need to work on the interface
    result = response['result']  # Assumes we're using gTTS
    # Get the text that is supposed to be spoken aloud
    reply = result['fulfillment']['speech']
    # Get what the service thought you said
    question = result['resolvedQuery']
    if input_type == 'google':
        print("You said: " + question)
    # Get the classification for the input, this includes
    # whether it is a request about some information or
    # a specific action that the user wants the bot to
    # perform, etc.
    action = result['action']
    return action, question, reply


def wolfram_query(question):
    import wolframalpha
    # Every service should have a general set of requirements under which
    # it is activated, this would be one of the ones that Wolfram Alpha
    # uses, it does have others as well. Consider having a single method
    # in the plugin system that returns a boolean determining whether
    # a plugin should be activated.
    if question.lower().startswith('wolfram'):
        question = question[8:]
    client = wolframalpha.Client(user_info.WOLFRAM_KEY)
    res = client.query(question)
    try:
        return next(res.results).text  # This really needs to be changed.
        # I shouldn't have to rely upon error catching for my flow control.
    except StopIteration:
        pass
    try:
        answer = '   '.join([each_answer.text for each_answer in res.pods if each_answer])
    except TypeError:
        answer = None
    if not answer:
        answer = "Sorry, Wolfram doesn't know the answer."

    # Replace some of its notation so it's more easily read.
    answer = answer.replace('\n', '; ').replace('~~', ' or about ')
    # Get the result to a computation and don't bother reading the original question.
    if '=' in answer:
        answer = answer[answer.index('=')+1:]
    return [answer, None]  # Follows answer format of [text, action]


reactions = {
    "manage.app_close": manage.app_close,  # General command for closing the app was given.
    "input.unknown": wolfram_query,  # If the AI system doesn't know what's being asked
    "wisdom.unknown": wolfram_query,  # If the AI system doesn't know the answer to what's being asked
    "calculator.math": wolfram_query,  # Use Wolfram for math
}


def get_reaction(action):
    """
    Handles getting an action to be executed
    depending on the input.
    :param action: A general classification for a query
    :return: A function to be executed as a result of
    the query or None if a reaction does not exist.
    """
    return reactions.get(action, None)

