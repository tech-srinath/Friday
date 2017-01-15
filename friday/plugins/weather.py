from yapsy.IPlugin import IPlugin


class Weather(IPlugin):
    def can_perform(self, friday, request):
        return 'action' in request['result'] and 'weather' in request['result']['action']

    def perform(self, friday, request):
        return "Dingus"
