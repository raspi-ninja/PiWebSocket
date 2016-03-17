import argparse
from PiWebSocket import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--debug', '-d', help="debug", default=False, action='store_true', dest='debug')
    subparser = parser.add_subparsers(help='service type', dest='command')

    echoparser = subparser.add_parser('echo', help='start echo websocket service')
    echoparser.add_argument('--port', '-p', help="port", default=8081, nargs="?", dest='port')

    calcparser = subparser.add_parser('calc', help='start calc websocket service')
    calcparser.add_argument('--address', '-a', help="address", default="localhost", dest='address')
    calcparser.add_argument('--name', '-n', help="your pi's name",default="pi", dest='name')
    calcparser.add_argument('--port', '-p', help="port", default=8081, nargs="?", dest='port')

    streamparser = subparser.add_parser('stream', help='connect to echo websocket and stream restults')
    streamparser.add_argument('--address', '-a', help="address", default="localhost", dest='address')
    streamparser.add_argument('--port', '-p', help="port number to host echo service on", default=8081, dest='port')
    streamparser.add_argument('--statsonly', '-s', help="show only 1000th digit stats", action='store_true',
                              default=False, dest='statsonly')
    args = parser.parse_args()
    print args
    if args.debug:
        log.startLogging(sys.stdout)
    log.startLogging(sys.stdout)

    if args.command == "stream":
        StreamPiData(args.address, args.port, statsonly=args.statsonly)
    if args.command == "calc":
        if args.name =="pi":
            args.name="pi_"+str(int(time.time()))
        StartPiCalcClient(args.address, args.port, args.name)
    if args.command == "echo":
        StartEchoServer(args.port)
