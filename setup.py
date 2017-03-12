try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(
        name='Pi Calc Stream',
        version='0.1.5.3',
        url='https://github.com/raspi-ninja/PiWebSocket',
        license='meh',
        author='Nate',
        author_email='masterninja@raspi-ninja.com',
        description="Stream pi realtime as it's calculated through the Websocket Echo Server to Other Clients'",
        packages=["PiWebSocket"],
        install_requires=["gmpy2", "ujson", "autobahn[twisted]>=0.11.0", "twisted", "txaio"]
)
