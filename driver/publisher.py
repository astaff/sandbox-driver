#!/usr/bin/env python3


import json, collections


class Publisher:
    def __init__(self, session=None):
        """
        """
        print('publisher.__init__ called')
        self.caller = None
        if session is not None:
            self.caller = session

        self.topics = {
            'frontend':'com.opentrons.frontend',
            'bootloader':'com.opentrons.bootloader',
            'labware':'com.opentrons.labware',
            'driver':'com.opentrons.driver'
        }


    def set_caller(self, session):
        """
        """
        print('publisher.set_caler called')
        self.caller = session


    def publish(self,topic,name,message,param):
        """
        """
        print('publisher.publish called')
        if self.caller is not None and topic is not None and name is not None and message is not None and param is not None:
            msg = {name:{message:param}}
            try:
                self.caller._myAppSession.publish(self.topic.get(topic),json.dumps(msg))
            except:
                print("error trying to send_message")
                raise

