#!/usr/bin/env python3


import asyncio
import time
import json
import uuid
import datetime
import sys

from driver_subscriber import Subscriber
from driver_publisher import Publisher
from driver_harness import Harness
from driver import SmoothieDriver

from autobahn.asyncio import wamp, websocket
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner 

loop = asyncio.get_event_loop()




def make_connection():
    if loop.is_running():
        loop.stop()
    coro = loop.create_connection(transport_factory, '0.0.0.0', 8080)
    transport, protocoler = loop.run_until_complete(coro)
    #protocoler.set_outer(self)
    if not loop.is_running():
        loop.run_forever()


class WampComponent(wamp.ApplicationSession):
    """WAMP application session for OTOne (Overrides protocol.ApplicationSession - WAMP endpoint session)
    """
    outer = None

    def set_outer(self, outer_):
        outer = outer_

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
        print(datetime.datetime.now(),' - driver_client : WampComponent.onJoin:')
        print('\tdetails: ',str(details))
        if not self.factory._myAppSession:
            self.factory._myAppSession = self
    
        def handshake(client_data):
            """
            """
            #if debug == True:
            print(datetime.datetime.now(),' - driver_client : WampComponent.handshake:')
            #if outer is not None:
            #outer.
            publisher.handshake(client_data)

        yield from self.subscribe(handshake, 'com.opentrons.driver_handshake')
        yield from self.subscribe(subscriber.dispatch_message, 'com.opentrons.driver')



    def onLeave(self, details):
        """Callback fired when WAMP session has been closed.
        :param details: Close information.
        """
        print('driver_client : WampComponent.onLeave:')
        print('\tdetails: ',details)
        if self.factory._myAppSession == self:
            self.factory._myAppSession = None
        try:
            self.disconnect()
        except:
            raise
        

    def onDisconnect(self):
        """Callback fired when underlying transport has been closed.
        """
        print(datetime.datetime.now(),' - driver_client : WampComponent.onDisconnect:')
        asyncio.get_event_loop().stop()

    
    


if __name__ == '__main__':

    try:
        session_factory = wamp.ApplicationSessionFactory()
        session_factory.session = WampComponent
        session_factory._myAppSession = None

        url = "ws://0.0.0.0:8080/ws"
        transport_factory = websocket.WampWebSocketClientFactory(session_factory,
                                                                url=url,
                                                                debug=False,
                                                                debug_wamp=False)
        loop = asyncio.get_event_loop()

        # TRYING THE FOLLOWING IN INSTANTIATE OBJECTS vs here
        # INITIAL SETUP PUBLISHER, HARNESS, SUBSCRIBER
        print('*\t*\t* initial setup - publisher, harness, subscriber\t*\t*\t*')
        publisher = Publisher(session_factory)
        driver_harness = Harness(publisher)
        subscriber = Subscriber(driver_harness,publisher)
        driver_harness.set_publisher(publisher)


        # INSTANTIATE DRIVERS:
        print('*\t*\t* instantiate drivers\t*\t*\t*')
        smoothie_driver = SmoothieDriver()


        # ADD DRIVERS TO HARNESS 
        print('*\t*\t* add drivers to harness\t*\t*\t*')   
        driver_harness.add_driver(publisher.id,'smoothie',smoothie_driver)
        print(driver_harness.drivers(publisher.id,None,None))

        # DEFINE CALLBACKS:
        #
        #   data_dict format:
        #
        #
        #
        #
        #
        print('*\t*\t* define callbacks\t*\t*\t*')
        def none(name, data_dict):
            """
            """
            print(datetime.datetime.now(),' - driver_client.none:')
            print('\tdata_dict: ',data_dict)
            dd_name = list(data_dict)[0]
            dd_value = data_dict[dd_name]
            publisher.publish('frontend','','driver',name,list(data_dict)[0],dd_value)

        def positions(name, data_dict):
            """
            """
            print(datetime.datetime.now(),' - driver_client.positions:')
            print('\tdata_dict: ',data_dict)
            dd_name = list(data_dict)[0]
            dd_value = data_dict[dd_name]
            publisher.publish('frontend','','driver',name,list(data_dict)[0],dd_value)


        # ADD CALLBACKS VIA HARNESS:
        print('*\t*\t* add callbacks via harness\t*\t*\t*')
        driver_harness.add_callback(publisher.id,'smoothie', {none:['None']})
        driver_harness.add_callback(publisher.id,'smoothie', {positions:['M114']})

        for d in driver_harness.drivers(publisher.id,None,None):
            print(driver_harness.callbacks(publisher.id,d, None))

        # CONNECT TO DRIVERS:
        print('*\t*\t* connect to drivers\t*\t*\t*')
        driver_harness.connect(publisher.id,'smoothie',None)

        print('END INIT')

        make_connection()

    except KeyboardInterrupt:
        pass
    finally:
        loop.close()














