#!/usr/bin/env python3


import json, collections
import sys
import datetime


class Publisher:

    topic = {
        'frontend' : 'com.opentrons.frontend',
        'driver' : 'com.opentrons.driver',
        'labware' : 'com.opentrons.labware',
        'bootloader' : 'com.opentrons.bootloader'
    }

    def __init__(self, session=None):
        """
        """
        print(datetime.datetime.now(),' - publisher.__init__:')
        print('\tsession: ',session)
        self.caller = None
        if session is not None:
            self.caller = session


    def set_caller(self, session):
        """
        """
        print(datetime.datetime.now(),' - publisher.set_caller:')
        print('\tsession: ',session)
        self.caller = session


    def publish(self,topic,type_,name,message,param):
        """
        """
        print(datetime.datetime.now(),' - publisher.publish:')
        print('\ttopic: ',topic)
        print('\ttype_: ',type_)
        print('\tname: ',name)
        print('\tmessage: ',message)
        print('\tparam: ',param)
        if self.caller is not None and topic is not None and type_ is not None:
            if name is None:
                name = 'None'
            if message is None:
                message = ''
            if param is None:
                param = ''
            if self.caller._myAppSession is not None:
                msg = {'type':type_,'data':{'name':name,'message':{message:param}}}
                try:
                    self.caller._myAppSession.publish(self.topic.get(topic),json.dumps(msg))
                except:
                    print(datetime.datetime.now(),' - publisher.py - publish - error:\n\r',sys.exc_info()[0])
                    raise
            else:
                print(datetime.datetime.now(),' - publisher.py - publish - error: caller._myAppSession is None')
        else:
            print(datetime.datetime.now(),' - publisher.py - publish - error: calller, topic, or type_ is None')

