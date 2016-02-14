#!/usr/bin/env python3


import asyncio
import time
import json
import uuid
import datetime
import sys

from subscriber import Subscriber
from publisher import Publisher
from driver_harness import Harness
from driver import SmoothieDriver

from autobahn.asyncio import wamp, websocket
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner 



class WampComponent(wamp.ApplicationSession):
    """WAMP application session for OTOne (Overrides protocol.ApplicationSession - WAMP endpoint session)
    """

    def __init__(self,config=None): # <--- even necessary???
        wamp.ApplicationSession.__init__(self,config)
        print('START INIT')
        self.subscriber = None
        self.publisher = None
        self.driver_harness = None
        print('END INIT')


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

        self.driver_uuid = str(uuid.uuid4())

        self.loop = asyncio.get_event_loop()

        try:
            # TRYING THE FOLLOWING IN INSTANTIATE OBJECTS vs here
            # INITIAL SETUP PUBLISHER, HARNESS, SUBSCRIBER
            print('*\t*\t* initial setup - publisher, harness, subscriber\t*\t*\t*')
            self.publisher = Publisher(self)
            self.driver_harness = Harness(self.publisher)
            self.subscriber = Subscriber(self.driver_harness,self.publisher)
            self.driver_harness.set_publisher(self.publisher)


            # INSTANTIATE DRIVERS:
            print('*\t*\t* instantiate drivers\t*\t*\t*')
            self.smoothie_driver = SmoothieDriver()


            # ADD DRIVERS TO HARNESS 
            print('*\t*\t* add drivers to harness\t*\t*\t*')   
            self.driver_harness.add_driver(self.publisher.id,'smoothie',self.smoothie_driver)
            print(self.driver_harness.drivers(self.publisher.id,None,None))

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
                self.publisher.publish('frontend','','driver',name,list(data_dict)[0],dd_value)

            def positions(name, data_dict):
                """
                """
                print(datetime.datetime.now(),' - driver_client.positions:')
                print('\tdata_dict: ',data_dict)
                dd_name = list(data_dict)[0]
                dd_value = data_dict[dd_name]
                self.publisher.publish('frontend','','driver',name,list(data_dict)[0],dd_value)


            # ADD CALLBACKS VIA HARNESS:
            print('*\t*\t* add callbacks via harness\t*\t*\t*')
            self.driver_harness.add_callback(self.publisher.id,'smoothie', {none:['None']})
            self.driver_harness.add_callback(self.publisher.id,'smoothie', {positions:['M114']})

            for d in self.driver_harness.drivers(self.publisher.id,None,None):
                print(self.driver_harness.callbacks(self.publisher.id,d, None))

            # CONNECT TO DRIVERS:
            print('*\t*\t* connect to drivers\t*\t*\t*')
            self.driver_harness.connect(self.publisher.id,'smoothie',None)

        
            def handshake(client_data):
                """
                """
                #if debug == True:
                print(datetime.datetime.now(),' - driver_client : WampComponent.handshake:')
                self.publisher.handshake(client_data)


            yield from self.subscribe(handshake, 'com.opentrons.driver_handshake')
            yield from self.subscribe(subscriber.dispatch_message, 'com.opentrons.driver')

        except KeyboardInterrupt:
            pass


    def onLeave(self, details):
        """Callback fired when WAMP session has been closed.
        :param details: Close information.
        """
        print('driver_client : WampComponent.onLeave:')
        print('\tdetails: ',details)
        

    def onDisconnect(self):
        """Callback fired when underlying transport has been closed.
        """
        print(datetime.datetime.now(),' - driver_client : WampComponent.onDisconnect:')
        asyncio.get_event_loop().stop()
    


if __name__ == '__main__':
    runner = ApplicationRunner(
                u"ws://0.0.0.0:8080/ws",
                u"ot_realm",
                debug=False
            )

    def run():
        print(datetime.datetime.now(),' run()')
        try:
            runner.run(WampComponent)
        except:
            time.sleep(7)
            run()

    run()











