from yapsy.IPlugin import IPlugin


class Weather(IPlugin):
    def can_perform(self, request):
        return True

    def perform(self, request):
        return "Dingus"
