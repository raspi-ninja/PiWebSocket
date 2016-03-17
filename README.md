# PiWebSocket
A WebSocket Client & Echo Server to stream pi as it is calculated to the internets

- Requires
    - AutobahnPython
    - python-gmpy
    - python-ujson
    - python-twisted

- Web clients connect to ws://url:8081/ws_pi or other client waiting to recieve digits
- PIClientWS.py - Client that calculates pi and connects to the echo server ws://url:8081/ws_pi?pi,  uses a modified header     containing the Raspberry PI's name
- EchoWS.py - Echo WebSocket Server that modifies the pi message to better suite web clients.  Hosts server at
   ws://localhost:8081/ws_pi

#Setup
    $ git clone https://github.com/raspi-ninja/PiWebSocket.git
    $ cd PiWebSocket
    $ python setup.py install
    #if setup.py fails on gmp.h install: apt-get install python-gmpy

#Commandline Usage

        python -m PiWebSocket [-h] [--debug] {echo,calc,stream} ...

        positional arguments:
    
                {echo,calc,stream}  service type
              
                    echo    start echo websocket service
                    calc    start calc websocket service
                    stream  connect to echo websocket and stream restults
                
                optional arguments:
                    -h, --help          show this help message and exit
                    --debug, -d         debug


- Stream Digits from Echo Server:
    
        python PiWebSocket stream [-h] [--address ADDRESS] [--port PORT] [--statsonly]

        optional arguments:
            -h, --help            show this help message and exit
            --address ADDRESS, -a ADDRESS
            --port PORT, -p PORT  port number to host echo service on
            --statsonly, -s       show only 1000th digit stats


- Start WebSocket Echo Server
    
        python PiWebSocket echo [-h] [--port [PORT]]

        optional arguments:
            -h, --help            show this help message and exit
            --port [PORT], -p [PORT]

- Start Pi Calculation Client

        python PiWebSocket calc [-h] [--address ADDRESS] [--name NAME] [--port [PORT]]

        optional arguments:
          -h, --help            show this help message and exit
          --address ADDRESS, -a ADDRESS
          --name NAME, -n NAME  your pi's name
          --port [PORT], -p [PORT]

