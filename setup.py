from distutils.core import setup

setup(
        name='Pi Calc Stream',
        version='0.1.1',
        packages=[''],
        url='http://www.raspi-ninja.com',
        license='meh',
        author='Nate',
        author_email='masterninja@raspi-ninja.com',
        description="Stream pi realtime as it's calculated through the Websocket Echo Server to Other Clients'",
        requires=["autobahn","gmpy","twisted","ujson"]
    )

