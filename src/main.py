# main.py
try:
    from .Friday import Friday
    from . import settings
except SystemError:
    from Friday import Friday
    import settings

debug = settings.debugging
speech_home = settings.home
tts_sys = settings.speech_system
response_type = settings.output_type


def main():
    assistant = Friday(debugging=debug, speech_file_location=speech_home,
                       input_system=tts_sys, output_system=response_type)
    while assistant.is_active:
        assistant.input(settings.input_type, settings.debugging)
        assistant.execute()
        if assistant.received_kill_signal():
            break
        assistant.choose_response()
        assistant.respond()

if __name__ == '__main__':
    main()
