from yapsy.IPlugin import IPlugin

import sys

class Exit(IPlugin):
    def can_perform(self, request):
        return 'action' in request['result'] and 'app_close' in request['result']['action']

    def perform(self, request):
        return sys.exit(0)

    def activate(self):
        print("Exiting program")

    def deactivate(self):
        print("Program exited")
