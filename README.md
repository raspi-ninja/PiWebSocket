# PiWebSocket
A Websocket Client & Echo Server to stream pi as it is calculated to the internets
-Requires
    - AutobahnPython
    - python-gmpy
    - python-ujson
    - python-twisted

- Web clients connect to ws://url:9000/ws_pi or other client waiting to recieve digits
- PIClientWS.py - Client that calculates pi and connects to the echo server ws://url:9000/ws_pi?pi,  uses a modified header     containing the Raspberry PI's name 
- EchoWS.py - Echo WebSocket Server that modifies the pi message to better suite web clients.  Hosts server at
   ws://localhost:9000/ws_pi
