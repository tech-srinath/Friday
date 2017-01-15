from yapsy.IPlugin import IPlugin


class APIAI(IPlugin):
    def can_perform(self, friday, request):
        return 'fulfillment' in request['result'] \
               and 'speech' in request['result']['fulfillment']

    def perform(self, friday, request):
        friday.response = request['result']['fulfillment']['speech']
        return True

    def activate(self):
        print("Calendar activated")

    def deactivate(self):
        print("Calendar activated")
