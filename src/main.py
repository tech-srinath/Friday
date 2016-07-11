# main.py
try:
    from .Friday import Friday
    from . import settings
except SystemError:
    from Friday import Friday
    import settings

# Load in settings
debug = settings.debugging
speech_home = settings.home
tts_sys = settings.speech_system
response_type = settings.output_type


def main():
    assistant = Friday(None, debugging=debug, speech_file_location=speech_home,
                       input_system=tts_sys, output_system=response_type)
    while assistant.is_active:
        assistant.get_input_from_user(settings.input_type, settings.debugging)
        # Execute functions associated with the user's input.
        assistant.perform_action()
        # If the resulting function sent back the kill signal then quit.
        if assistant.received_kill_signal():
            break
        # Decide which response the assistant should return to the user.
        assistant.choose_response()
        # Display a response to the user.
        assistant.respond()

if __name__ == '__main__':
    main()
