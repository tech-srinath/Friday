from yapsy.IPlugin import IPlugin


class Calendar(IPlugin):
    def can_perform(self, request):
        return True

    def perform(self, request):
        return "Thingy"

    def activate():
        print("Calendar activated")

    def deactivate():
        print("Calendar activated")
