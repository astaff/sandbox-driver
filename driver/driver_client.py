#!/usr/bin/env python3


import driver
import driver_harness
import asyncio
import time
import json
import uuid
import datetime
import sys

from subscriber import Subscriber
from publisher import Publisher

from autobahn.asyncio import wamp, websocket

subscriber = None
publisher = None
crossbar_status = False
uid = ''

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
        print(datetime.datetime.now(),' - driver_client : WampComponent.onJoin:')
        print('\tdetails: ',str(details))
        uid = str(uuid.uuid4())
        if not self.factory._myAppSession:
            self.factory._myAppSession = self
        
        crossbar_status = True
        instantiate_objects()
        
        
        def set_client_status(status):
            """
            """
            #if debug == True: 
            print(datetime.datetime.now(),' - driver_client : WampComponent.set_client_status:')
            print('\tstatus: ',str(status))
            global client_status
            client_status = status
            self.publish('com.opentrons.driver_client_ready',True)
            msg = {
                'type':'handshake',
                'data':{'driver':uid}
            }
            self.publish('com.opentrons.frontend',json.dumps(msg))
        
        print(datetime.datetime.now(),' - about to publish com.opentrons.driver_client_ready')
        self.publish('com.opentrons.driver_client_ready',True)
        msg = {
            'type':'handshake',
            'data':{'driver':uid}
        }
        self.publish('com.opentrons.frontend',json.dumps(msg))
        yield from self.subscribe(set_client_status, 'com.opentrons.frontend_client_ready')
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
            pass
	        
    def onDisconnect(self):
        """Callback fired when underlying transport has been closed.
        """
        print(datetime.datetime.now(),' - driver_client : WampComponent.onDisconnect:')
        asyncio.get_event_loop().stop()


def make_a_connection():
    """Attempt to create streaming transport connection and run event loop
    """
    print(datetime.datetime.now(),' - driver_client.make_a_connection')
    coro = loop.create_connection(transport_factory, '0.0.0.0', 8080)

    transporter, protocoler = loop.run_until_complete(coro)
    
    loop.run_forever()


def instantiate_objects():
    """After connection has been made, instatiate the various robot objects
    """
    print(datetime.datetime.now(),' - driver_client.instantiate_objects')
    
    


try:
    session_factory = wamp.ApplicationSessionFactory()
    session_factory.session = WampComponent

    session_factory._myAppSession = None

    url = "ws://0.0.0.0:8080/ws"
    transport_factory = websocket \
            .WampWebSocketClientFactory(session_factory,
                                        url=url,
                                        debug=False,
                                        debug_wamp=False)
    loop = asyncio.get_event_loop()

    # TRYING THE FOLLOWING IN INSTANTIATE OBJECTS vs here
    # INITIAL SETUP PUBLISHER, HARNESS, SUBSCRIBER
    print('*\t*\t* initial setup - publisher, harness, subscriber\t*\t*\t*')
    publisher = Publisher(session_factory)
    otdriver_harness = driver_harness.Harness(publisher)
    subscriber = Subscriber(otdriver_harness)
    otdriver_harness.set_publisher(publisher)


    # INSTANTIATE DRIVERS:
    print('*\t*\t* instantiate drivers\t*\t*\t*')
    otdriver = driver.SmoothieDriver()


    # ADD DRIVERS TO HARNESS 
    print('*\t*\t* add drivers to harness\t*\t*\t*')   
    otdriver_harness.add_driver('smoothie',otdriver)
    print(otdriver_harness.drivers(None,None))

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
        publisher.publish('frontend','driver',name,list(data_dict)[0],dd_value)

    def positions(name, data_dict):
        """
        """
        print(datetime.datetime.now(),' - driver_client.positions:')
        print('\tdata_dict: ',data_dict)
        dd_name = list(data_dict)[0]
        dd_value = data_dict[dd_name]
        publisher.publish('frontend','driver',name,list(data_dict)[0],dd_value)


    # ADD CALLBACKS VIA HARNESS:
    print('*\t*\t* add callbacks via harness\t*\t*\t*')
    otdriver_harness.add_callback('smoothie', {none:['None']})
    otdriver_harness.add_callback('smoothie', {positions:['M114']})

    for d in otdriver_harness.drivers(None,None):
        print(otdriver_harness.callbacks(d, None))

    # CONNECT TO DRIVERS:
    print('*\t*\t* connect to drivers\t*\t*\t*')
    otdriver_harness.connect('smoothie',None)




    #publisher = Publisher(session_factory)
    #otdriver_harness = driver_harness.Harness(publisher)
    #subscriber = Subscriber(otdriver_harness)
    #otdriver_harness.set_publisher(publisher)


    # INSTANTIATE DRIVERS:
    #otdriver = driver.SmoothieDriver()


    # ADD DRIVERS TO HARNESS    
    #otdriver_harness.add_driver('smoothie',otdriver)
    

    # DEFINE CALLBACKS:
    #
    #   data_dict format:
    #
    #
    #
    #
    #
    #def positions(name, data_dict):
        #print(datetime.datetime.now(),' - driver_client.positions:')
        #print('\tdata_dict: ',str(data_dict))
        #dd_name = list(data_dict)[0]
        #dd_value = data_dict[dd_name]
        #publisher.publish('frontend','driver',name,list(data_dict)[0],dd_value)



    # ADD CALLBACKS TO HARNESS:
    #otdriver_harness.add_callback('smoothie', {positions:['None']})


    # CONNECT TO DRIVERS:
    #otdriver_harness.connect('smoothie',None)


    while (crossbar_status == False):
        try:
            print('*\t*\t* trying to make a CROSSBAR connection...\t*\t*\t*')
            #make_a_connection()
        except KeyboardInterrupt:
            crossbar_status = True
        except:
            #raise
            pass
        finally:
            print('run forever time')
            loop.run_forever()
            #print('*\t*\t* error while trying to make a CROSSBAR connection, sleeping for 5 seconds\t*\t*\t*')
            time.sleep(20)
except KeyboardInterrupt:
    pass
finally:
    loop.close()














