"""
Author Nate,
License: Meh.. just remember me when you make your millions off this ;-)

Description:
    WebSocket Client
    Pi Calculator using the gosper unbounded streaming algorithm. Streams to an Echo Server to seprate web and websocket
    client processing load for optimized calculation.
    connects to echo websocket server
"""

import time
from gmpy2 import mpz, add, div, sub, mul

from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory, connectWS
from twisted.internet import reactor
from twisted.internet import threads
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.python import log

# ujson is significantly faster at converting objects into json strings
try:
    import ujson as json
except ImportError:
    import json

calc_uy = 1
u, y = -1, -1
q, r, t, j = mpz(1), mpz(180), mpz(60), 2
startTime = -1
"""
Enhanced equation from https://github.com/DaveMDS/pigreco/blob/master/generator_spigot.py
modified by adding mpz the python-gpmy library
added global variables to allow for variables to be saved globally for the next calculations
"""


def pi_calc():
    global calcs, y, u, q, r, t, j, calc_uy, startTime
    digitstring = ''
    dpm = 0
    strPi = ''
    loop = 1
    elapsed = 0
    elapsedStart = time.time()
    while loop:
        digitCalcTime = time.time()
        j3 = mul(3, j)
        u, y = mpz(3 * (j3 + 1) * (j3 + 2)), mpz(div((add(mul(q, (mul(27, j)) - 12), mul(5, r))), mul(5, t)))
        strPi = str(y)
        digitstring += strPi
        q, r, t, j = mpz(mul((20 * j ** 2 - mul(10, j)), q)), \
                     mpz(mul(mul(10, u), (q * (mul(5, j) - 2) + r - mul(y, t)))), \
                     mpz(mul(t, u)), add(j, 1)
        # dpm = digits per minute
        now = time.time()
        elapsed = now - elapsedStart
        # if the elapsed calculation time exceeds .5 seconds break the loop and return the digits calculated
        if elapsed >= .5:
            break
        elif (j - 2) % 1000 == 0:  # break also every 1000nth digit to report stats
            break
    dps = (1.0 / elapsed) * len(digitstring)
    info = {
        "digits": digitstring,
        "digitcount": int(j) - 2,
        "dpm": round(dps * 60),
        "dps": round(dps, 2)
    }
    if (j - 2) % 1000 == 0:
        info['mark'] = {"digitmark": (int(str(j)) - 2),
                        "runtime": time.time() - startTime}
    return info


class PiWebSocketProtocol(WebSocketClientProtocol):
    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))
        self.factory.resetDelay()
        self.factory.sendMessage = self.sendMessage

    def onOpen(self):
        if not self.factory.running_calc:
            mar14_2017 = 1489449600
            self.testTime = 1489278638.22434
            t = self.testTime - time.time()
            self.t = t
            if t >= 6000:
                t = 30
            if t < 0:
                t = (time.time() + 30) - time.time()

            print t, 'remain'
            reactor.callLater(t, self.factory.start_calculating)
            reactor.callLater(1, self.update)
            # self.factory.start_calculating()
        else:
            self.sendMessage(json.dumps({"startTime": time.time()}))

        pass

    def update(self):
        t = self.testTime - time.time()
        print t,'remain'
        self.sendMessage(json.dumps({"countdown": t}))
        if (t > 0):
            reactor.callLater(1, self.update)

    def onMessage(self, payload, isBinary):
        pass

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


class PiWebSocketFactory(WebSocketClientFactory, ReconnectingClientFactory):
    protocol = PiWebSocketProtocol
    running_calc = 0
    mar14 = 1489449600  # March 14 12:00 AM GMT
    testMark = mar14

    def clientConnectionFailed(self, connector, reason):
        print("Client connection failed .. retrying ..")
        self.retry(connector)

    def clientConnectionLost(self, connector, reason):
        print("Client connection lost .. retrying ..")
        self.retry(connector)

    def start_calculating(self):
        global startTime
        print 'starting calcs in:', self.testMark - time.time()
        self.startTime = time.time()
        self.getDigit()
        self.running_calc = 1
        self.sendMessage(json.dumps({"startTime": time.time()}))
        # if not self.running_calc and self.testMark - time.time() <= 0:
        #     self.sendMessage(json.dumps({"startTime": time.time()}))
        #     startTime = time.time()
        #     print 'start time', startTime
        #     # using Twisted Aync calls to prevent blocking the thread during long calculations
        #     d = threads.deferToThread(pi_calc)
        #     d.addCallback(self.getDigit)
        #     self.running_calc = 1
        # if not (self.testMark - time.time() <= 0):
        #     reactor.callLater(.5, self.start_calculating)
        #     self.sendMessage(json.dumps({"countdown": self.testMark - time.time()}))

    def getDigit(self):
        threads.deferToThread(pi_calc).addCallback(self.sendDigits)

    def sendDigits(self, digits):
        print digits
        elapsed = time.time() - self.startTime
        digits['elapsed'] = elapsed
        self.sendMessage(json.dumps(digits))
        self.getDigit()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('address', help="address", default="localhost", nargs="?")
    parser.add_argument('port', help="port", default=8888, nargs="?")
    parser.add_argument('client_name', help="pi client name", default="Rpi", nargs="?")
    parser.add_argument('debug', help="debug", default=False, nargs="?")

    args = parser.parse_args()
    # url to echo server
    url = "ws://{}:{}/ws_pi?pi".format(args.address, args.port)
    import sys

    debug = True
    if args.debug or debug:
        log.startLogging(sys.stdout)
    log.startLogging(sys.stdout)
    headers = {"PiClient": args.client_name}
    factory = PiWebSocketFactory(u"{}".format(url), headers=headers)

    connectWS(factory)
    reactor.run()
