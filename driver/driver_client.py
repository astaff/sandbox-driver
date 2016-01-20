#!/usr/bin/env python3


import driver
import driver_harness
import asyncio
import time
import json
from subscriber import Subscriber
from publisher import Publisher

from autobahn.asyncio import wamp, websocket

subscriber = None
publisher = None
crossbar_status = False
#driver_harness = None



class WampComponent(wamp.ApplicationSession):
    """WAMP application session for OTOne (Overrides protocol.ApplicationSession - WAMP endpoint session)
    """

    def onConnect(self):
        """Callback fired when the transport this session will run over has been established.
        """
        self.join(u"ot_realm")

    @asyncio.coroutine
    def onJoin(self, details):
        """Callback fired when WAMP session has been established.

        May return a Deferred/Future.

        Starts instatiation of robot objects by calling :meth:`otone_client.instantiate_objects`.
        """
        print('otone_client : WampComponent.onJoin called')
        if not self.factory._myAppSession:
            self.factory._myAppSession = self
        
        crossbar_status = True
        instantiate_objects()
        
        
        def set_client_status(status):
            #if debug == True: 
            print('otone_client : WampComponent.set_client_status called')
            global client_status
            client_status = status
            self.publish('com.opentrons.driver_client_ready',True)
            msg = {
                'type':'dummy data',
                'data':"dummy"
            }
            self.publish('com.opentrons.driver_to_frontend',json.dumps(msg))
        
        print('about to publish com.opentrons.driver_client_ready TRUE')
        self.publish('com.opentrons.driver_client_ready',True)
        msg = {
            'type':'dummy data',
            'data':"dummy"
        }
        self.publish('com.opentrons.driver_to_frontend',json.dumps(msg))
        yield from self.subscribe(set_client_status, 'com.opentrons.frontend_client_ready')
        yield from self.subscribe(subscriber.dispatch_message, 'com.opentrons.frontend_to_driver')


    def onLeave(self, details):
        """Callback fired when WAMP session has been closed.
        :param details: Close information.
        """
        if self.factory._myAppSession == self:
            self.factory._myAppSession = None
        try:
            self.disconnect()
        except:
            pass
	        
    def onDisconnect(self):
        """Callback fired when underlying transport has been closed.
        """
        asyncio.get_event_loop().stop()


def make_a_connection():
    """Attempt to create streaming transport connection and run event loop
    """
    coro = loop.create_connection(transport_factory, '127.0.0.1', 8080)

    transporter, protocoler = loop.run_until_complete(coro)
    #instantiate the subscriber and publisher for communication
    
    loop.run_forever()


def instantiate_objects():
    """After connection has been made, instatiate the various robot objects
    """
    #publisher = Publisher(session_factory)
    #otdriver_harness = driver_harness.Harness(publisher)
    #subscriber = Subscriber(otdriver_harness)
    #otdriver_harness.set_publisher(publisher)
    #otdriver_harness.connect()


try:
    session_factory = wamp.ApplicationSessionFactory()
    session_factory.session = WampComponent

    session_factory._myAppSession = None

    url = "ws://127.0.0.1:8080/ws"
    transport_factory = websocket \
            .WampWebSocketClientFactory(session_factory,
                                        url=url,
                                        debug=False,
                                        debug_wamp=False)
    loop = asyncio.get_event_loop()

    publisher = Publisher(session_factory)
    otdriver_harness = driver_harness.Harness(publisher)
    subscriber = Subscriber(otdriver_harness)
    otdriver_harness.set_publisher(publisher)
    otdriver_harness.connect()

    while (crossbar_status == False):
        try:
            print('trying to CROSSBAR make a connection...')
            make_a_connection()
        except KeyboardInterrupt:
            crossbar_status = True
        except:
            #raise
            pass
        finally:
            print('error while trying to make a CROSSBAR connection, sleeping for 5 seconds')
            time.sleep(5)
except KeyboardInterrupt:
    pass
finally:
    loop.close()














