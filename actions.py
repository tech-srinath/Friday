from __init__ import *


def wolfquery(question):
    if question.lower().startswith('wolfram'):
        question = question[8:]
    client = wolframalpha.Client('R33RAT-7QTK4AL8LL')
    res = client.query(question)
    try:
        return next(res.results).text
    except StopIteration:
        try:
            answers = '   '.join([each_answer.text for each_answer in res.pods if each_answer])
        except TypeError:
            answers = None
        if answers:
            return answers
        return "Sorry, Wolfram doesn't know the answer."


def say(message, title='Speak', speech_system='google', say=True, lang='en'):
    if speech_system == 'google':
        # Create the MP3 file which will speak the text
        folder = ''
        if '\\' in title:
            folder = '\\'.join(title.split('\\')[:-1])
        title += '.mp3'
        tts = gTTS(message, lang=lang)
        path = home+'\\'+title
        folder_path = home + "\\" + folder
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        tts.save(path)
        if say:
            call("start /MIN {}".format(home+'\\'+title), shell=True)
    else:
        # Create the Visual Basic code which will speak the text
        with open(title + '.vbs', 'w') as file:
            file.write(
                    """
                    speaks="{}"
                    Dim speaks, speech
                    Set speech=CreateObject("sapi.spvoice")
                    speech.Speak speaks
                    """
                    .format(
                        str(message).replace('"', '').replace('\n', '')))
        # Execute the file
        call(['cscript.exe', title + '.vbs'])


def ask_google():
        print("Please speak now")
        with m as source:
                audio = r.listen(source)
        print("Processing audio")
        try:
            return r.recognize_google(audio)
        except sr.UnknownValueError: # speech is unintelligible
            return "GSR Could not understand audio"
        except sr.RequestError:
            return "Could not request results from Google Speech Recognition service"


def query(input_type):
    resampler = apiai.Resampler(source_samplerate=RATE)
    request = None
    
    vad = apiai.VAD()

    if input_type == 'local':
        print("Local Speech Recognition")
        request = ai.voice_request()
        
        def callback(in_data, frame_count, time_info, status):
            frames, data = resampler.resample(in_data, frame_count)
            if show_decibels:
                decibel = 20 * log(audioop.rms(data, 2)+1, 10)
                print(decibel)
            state = vad.processFrame(frames)
            request.send(data)

            if state == 1:
                return in_data, pyaudio.paContinue
            else:
                return in_data, pyaudio.paComplete

        p = pyaudio.PyAudio()
        
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        output=False,
                        frames_per_buffer=CHUNK,
                        stream_callback=callback)

        stream.start_stream()
        
        print ("Speak!")
        
        try:
            while stream.is_active():
                time.sleep(0.1)
        except Exception as e:
            raise e
        except KeyboardInterrupt:
            pass
        
        stream.stop_stream()
        stream.close()
        p.terminate()
    elif input_type == 'google':
        print("Google's speech recognition")
        request = ai.text_request()
        request.query = ask_google()
    else:
        request = ai.text_request()
        try:
            request.query = input("Input your query: ")
        except KeyboardInterrupt:
            raise SystemExit
    print ("Wait for response...")
    response = request.getresponse()
    response = response.read()

    try:
        response = eval(response.decode('UTF-8'))
    except NameError:
        response = {'result':{'fulfillment':{'speech':" "}, 'action': "None", 'resolvedQuery': "UNKNOWN"}}
    return response


def listen(input_type = 'google'):
    action = "None"
    response = query(input_type)['result']
    reply = response['fulfillment']['speech']
    question = response['resolvedQuery']
    print("You said: " + question)
    action = response['action']
    
    return action, question, reply


def wolf(question):
    answer = wolfquery(question)
    answer = answer.replace('\n', '; ').replace('~~', ' or about ')
    try:
        answer = answer[answer.index('=')+1:]
    except ValueError:
        pass
    return answer


def causality(action):
    return {
        "manage.app_close": manage.app_close,
        "input.unknown": wolf,
        "wisdom.unknown": wolf,
    }.get(action, wolf)
