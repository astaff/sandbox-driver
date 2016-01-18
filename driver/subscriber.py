#!/usr/bin/env python3

import json, collections


in_dispatcher = {
	'': lambda data: a(),
	'': lambda data: b(),
	'': lambda data: c(),
	'': lambda data: d(),
	'': lambda data: e()
}

driver = None

class Subscriber():
    def __init__(self, driver_=None):
        driver = driver_

    def set_driver(self, driver):
        print("set_driver called")
        driver = driver


    def dispatch_message(self, message):
        print("dispatch_message called")
        try:
            dictum = collections.OrderedDict(json.loads(message.strip(), object_pairs_hook=collections.OrderedDict))
            if 'data' in dictum:
                self.dispatch(dictum['type'],dictum['data'])
            else:
                self.dispatch(dictum['type'],None)
        except:
            print('*** error in subscriber.dispatch_message ***')
            raise


    def dispatch(self, type_, data):
        print("dispatch called")
        if data is not None:
            global in_dispatcher.get(type_)(self,data)
        else:
            global in_dispatcher.get(type_)(self)





