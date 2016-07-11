try:
    from . import manage
    from . import settings
    from . import api_interface
    from . import user_info
except SystemError:
    import manage
    import settings
    import api_interface
    import user_info
import speech_recognition as sr

__author__ = "Isaac Smith (Zenohm)"

# This is disorganized, see about cleaning it up.

settings.installed['apiai'] = manage.import_or_install('apiai', 'apiai',
                                                       'the api.ai intelligent unit',
                                                       'have advanced conversation capabilities')
if settings.installed['apiai']:
    import apiai

settings.installed['gtts'] = manage.import_or_install('gtts', 'gTTS',
                                                      'Google Text to Speech API',
                                                      'sound natural')

r = sr.Recognizer()
m = sr.Microphone(device_index=settings.DEVICE, sample_rate=settings.RATE, chunk_size=settings.CHUNK)

ai = api_interface.API(apiai.ApiAI(user_info.CLIENT_ACCESS_TOKEN, user_info.SUBSCRIPTION_KEY))

if settings.input_type == 'google':
    with m as source:
        if settings.debugging:
            print("Adjusting to ambient noise.")
        r.adjust_for_ambient_noise(source)  # we only need to calibrate once, before we start listening
    # r.energy_threshold = 200
