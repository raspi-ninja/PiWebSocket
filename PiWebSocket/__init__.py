"""

"""
import txaio, ujson as json, time
from twisted.internet.protocol import ReconnectingClientFactory

txaio.use_twisted()
from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory, connectWS
from autobahn.twisted.resource import WebSocketResource
from autobahn.twisted.websocket import listenWS, connectWS, WebSocketClientFactory
import sys, ujson
from twisted.python import log
from twisted.internet import reactor

from PiEchoServerWS import PiServerProtocol
from PiEchoServerWS import BroadcastServerFactory
from PiCalcClientWS import PiWebSocketFactory
from PiCalcClientWS import PiWebSocketProtocol

def showdebug(msg):
    print msg


def StartEchoServer(port):
    factory80 = BroadcastServerFactory(u"ws://localhost:{}/ws_pi".format(port))
    factory80.protocol = PiServerProtocol
    listenWS(factory80)
    print 'starting websocket echo server'
    reactor.run()


def StartPiCalcClient(echo_server_url, echo_server_port, picalcname="Raspi", debug=False):
    if debug:
        log.startLogging(sys.stdout)
    headers = {"PiClient": picalcname}
    factory = PiWebSocketFactory(u"ws://{}:{}/ws_pi?pi".format(echo_server_url, echo_server_port),
                                 headers=headers)
    connectWS(factory)
    reactor.run()


class ShowPiStreamProtocol(WebSocketClientProtocol):
    customCalback = None
    showpi = True

    def onConnect(self, response):
        print("connected to : {0}".format(response.peer))

        self.sendMessage(ujson.dumps({"showpi": self.showpi}))
        self.factory.resetDelay()

    def onMessage(self, payload, isBinary):
        if not self.customCalback:
            print payload
        else:
            self.customCalback(payload)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


class ShowPiStreamFactory(WebSocketClientFactory, ReconnectingClientFactory):
    protocol = ShowPiStreamProtocol

    def clientConnectionFailed(self, connector, reason):
        print("Client connection failed .. retrying ..")
        self.retry(connector)

    def clientConnectionLost(self, connector, reason):
        print("Client connection lost .. retrying ..")
        self.retry(connector)


def StreamPiData(echo_server_url='localhost', echo_server_port=8081, customcallback=None, statsonly=False):
    """
    Connect to the Echo server to stream the digits of pi
    :param echo_server_url: 127.0.0.1
    :param echo_server_port: 9000
    :return:none
    """
    url = "ws://{}:{}/ws_pi?pi".format(echo_server_url, echo_server_port)
    print "connecting to {}".format(url)
    client = ShowPiStreamFactory(url)
    client.protocol.showpi = not statsonly
    connectWS(client)
    client.protocol.customCalback = customcallback

    reactor.run()
