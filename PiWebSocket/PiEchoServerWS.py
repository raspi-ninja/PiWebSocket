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
            data = json.loads(payload)
            newpayload = {
                "device": self.device
            }
            ws_url = self.http_request_uri
            if data.has_key('startTime'):
                self.stats.startTime = data['startTime']
            # self.stats.startTime = data['startTime']
            #     self.factory.broadcast({
            #         "device": self.device,
            #         "stats": {
            #             "startTime": self.stats.startTime
            #         }
            #     })
            if data.has_key('countdown'):
                newpayload['countdown'] = data['countdown']
                self.factory.broadcast(newpayload)
            if data.has_key('dpm'):
                newpayload['dpm'] = data['dpm']
            if data.has_key('digits'):
                newpayload['digits'] = data['digits']
                for num in data['digits']:
                    if self.stats.digitcounts.has_key(num):
                        self.stats.digitcounts[num] += 1
                    else:
                        self.stats.digitcounts[num] = 1

            if data.has_key('digitcount'):
                newpayload['digitcount'] = data['digitcount']
            if data.has_key('elapsed'):
                newpayload['elapsed'] = data['elapsed']
            if data.has_key('mark'):
                self.stats.digits_history.append(data['mark'])
                if data.has_key('dpm'):
                    mark = data['mark']
                    self.stats.dpm_history.append(mark)
                newpayload['mark'] = {
                    "device": self.device,
                    "dps": data['dps'],
                    "digitmark": data['mark']['digitmark'],
                    "time": data['mark']['runtime']
                }
            if data.has_key('dpm'):
                self.stats.dpm_history.append(data['dpm'])
            if data.has_key('digits'):
                self.factory.broadcast(newpayload, data['digits'], self.stats.digitcounts)
        else:
            try:
                data = json.loads(payload)
                # print data.__dict__
                if json.loads(payload).has_key("showpi"):
                    self.showpi = data['showpi']

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
        reactor.callLater(1, self.sendStats)

    def sendStats(self):
        if len(self.piClients) > 0:
            stats = []
            for client in self.piClients:
                name = client.device
                stats.append({'device': name,
                              'digits_history': client.stats.digits_history})
            for c in self.clients:
                c.sendMessage(json.dumps({'pistats': stats}))
        reactor.callLater(1, self.sendStats)

    def registerPiServer(self, PiClient):
        PiClient.stats = Stats()
        PiClient.stats.startTime = 0
        PiClient.stats.digits_history = []
        PiClient.stats.digitcounts = {}
        PiClient.stats.digit_count = 0
        PiClient.stats.dpm_history = []
        PiClient.device = PiClient.http_headers['piclient']
        if (PiClient not in self.piClients):
            self.piClients.append(PiClient)
            print 'welcome :', PiClient.http_headers['piclient']

    def register(self, client):
        if client not in self.clients:
            client.showpi = False
            self.clients.append(client)
            for piclient in self.piClients:
                newclientdata = {
                    "device": piclient.device,
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
            # else:
            #     # print digitcounts
            #     data["digitcounts"] = digitcounts
            c.sendMessage(json.dumps(data))


if __name__ == '__main__':
    factory80 = BroadcastServerFactory(u"ws://localhost:8888/ws_pi")
    factory80.protocol = PiServerProtocol
    resource80 = WebSocketResource(factory80)
    listenWS(factory80)
    print 'starting...'
    reactor.run()
