"""
Author Nate,
License: Meh.. just remember me when you make your millions off this ;-)

Description:
    WebSocket Echo Server for raspberry pi clients sending their pi calcs.  Handles the connection load of clients
    looking at the stream.
    - Client Connects to ws://url:8081/ws_pi
    - Pi Calculating Client connects to ws://url:9000/ws_pi?pi
    V0.1.3
"""

import ujson as json
from autobahn.twisted.resource import WebSocketResource
from autobahn.twisted.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory, listenWS
from twisted.internet import reactor


class DataObj(object):
    def __init__(self, d={}):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
                setattr(self, a, [DataObj(x) if isinstance(x, dict) else x for x in b])
            else:
                setattr(self, a, DataObj(b) if isinstance(b, dict) else b)
        pass

    def __getattr__(self, item):
        try:
            return super(DataObj, self).__getattribute__(item)
        except AttributeError:
            setattr(self, item, None)
            return super(DataObj, self).__getattribute__(item)


class Stats(object):
    pass


class PiServerProtocol(WebSocketServerProtocol):
    def onOpen(self):
        header = self.http_headers
        if header.has_key('piclient'):
            self.factory.registerPiServer(self)
        else:
            print 'non pi client', self.peer
            self.factory.register(self)

    def onConnect(self, request):
        # print request
        pass

    def onMessage(self, payload, isBinary):
        if self in self.factory.piClients:
            data = DataObj(json.loads(payload))
            ws_url = self.http_request_uri
            if data.startTime:
                self.stats.startTime = data.startTime
                self.factory.broadcast({
                    "piclient": self.device,
                    "stats": {
                        "startTime": self.stats.startTime
                    }
                })
            if data.countdown:
                self.factory.broadcast(data.__dict__)
            if data.digits:
                for num in data.digits:
                    if self.stats.digitcounts.has_key(num):
                        self.stats.digitcounts[num] += 1
                    else:
                        self.stats.digitcounts[num] = 1

            newpayload = {
                "device": self.device,
                # "digits": data.digits,
                "dpm": data.dpm,
                "digitcount": data.digitcount,
                # "digitcounts": self.stats.digitcounts
            }
            if data.mark:
                self.stats.digits_history.append(data.mark.__dict__)
                if data.dpm:
                    self.stats.dpm_history.append({data.mark.runtime: data.dps})
                newpayload['mark'] = {
                    "dps": data.dps,
                    "digitmark": data.mark.digitmark,
                    "time": data.mark.runtime
                }
            if data.dpm:
                self.factory.broadcast(newpayload, data.digits, self.stats.digitcounts)
        else:
            try:
                data = DataObj(json.loads(payload))
                # print data.__dict__
                if json.loads(payload).has_key("showpi"):
                    self.showpi = data.showpi

            except Exception as e:
                print e
                pass

    def onClose(self, wasClean, code, reason):
        self.factory.unregister(self)


class BroadcastServerFactory(WebSocketServerFactory):
    def __init__(self, url, debug=True):
        WebSocketServerFactory.__init__(self, url)
        self.clients = []
        self.piClients = []

    def registerPiServer(self, PiClient):
        PiClient.stats = Stats()
        PiClient.stats.startTime = 0
        PiClient.stats.digits_history = []
        PiClient.stats.digitcounts = {}
        PiClient.stats.digit_count = 0
        PiClient.stats.dpm_history = []
        PiClient.device = PiClient.http_headers['piclient']
        self.piClients.append(PiClient)
        print 'welcome :', PiClient.http_headers['piclient']

    def register(self, client):
        if client not in self.clients:
            client.showpi = False
            self.clients.append(client)
            for piclient in self.piClients:
                newclientdata = {
                    "piclient": piclient.device,
                    "stats": {
                        "startTime": piclient.stats.startTime
                    }
                }
                print newclientdata
                client.sendMessage(json.dumps(newclientdata))
            self.clientChange()

    def unregister(self, client):
        if client in self.clients:
            self.clients.remove(client)
            self.clientChange()
        if (client in self.piClients):
            self.piClients.remove(client)

    def clientChange(self):
        self.broadcast({"connectedClients": len(self.clients)})

    def broadcast(self, msg, digits="", digitcounts={}):
        # prepared_msg = self.prepareMessage((msg),isBinary=False)
        # print msg
        for c in self.clients:
            data = msg
            if c.showpi:
                data["digits"] = digits
            else:
                # print data['digits']
                data["digitcounts"] = digitcounts
            c.sendMessage(json.dumps(data))


if __name__ == '__main__':
    factory80 = BroadcastServerFactory(u"ws://localhost:8081/ws_pi")
    factory80.protocol = PiServerProtocol
    resource80 = WebSocketResource(factory80)
    listenWS(factory80)
    print 'starting...'
    reactor.run()
