#!/usr/bin/env python3


import json, collections

out_dispatcher = {
    '': lambda data: a(),
    '': lambda data: b(),
    '': lambda data: c(),
    '': lambda data: d(),
    '': lambda data: e()
}


class Publisher:
    def __init__(self, session=None):
        self.caller = None
        if session is not None:
            self.caller = session


    def set_caller(self, session):
        self.caller = session


    def dispatch_message(self, message):
        try:
            dictum = collections.OrderedDict(json.loads(message.strip(), object_pairs_hook=collections.OrderedDict))
            if 'data' in dictum:
                self.out_dispatch[dictum['type']](self,dictum['data'])
            else:
                self.out_dispatch[dictum['type']](self,None)
        except:
            print('*** error in publisher.dispatch_message ***')
            raise


    def publish(self,type_,data_):
        if self.caller is not None and type_ is not None:
            if data_ is not None:
                msg = {
                    'type':type_,
                    'data':damsg
                }
            else:
                msg = {
                    'type':type_
                }
            try:
                self.caller._myAppSession.publish('com.opentrons.driver_to_frontend',json.dumps(msg))
            except:
                print("error trying to send_message")


