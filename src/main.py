# main.py
try:
    from .Friday import Friday
    from . import settings
except SystemError:
    from Friday import Friday
    import settings


def main():
    assistant = Friday(debugging=settings.debugging, speech_file_location=settings.home,
                       speech_system=settings.speech_system)
    while assistant.is_active:
        assistant.input(settings.input_type, settings.debugging)
        assistant.execute()
        if assistant.received_kill_signal():
            break
        assistant.choose_response()
        assistant.print_response()
        assistant.speak_response()

if __name__ == '__main__':
    main()
