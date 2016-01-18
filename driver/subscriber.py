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
                subscriber.in_dispatch(dictum['type'],dictum['data'])
            else:
                subscriber.in_dispatch(dictum['type'],None)
        except:
            print('*** error in subscriber.dispatch_message ***')
            raise


    def dispatch(self, data):
        print("dispatch called")
        if data is not None:
            subscriber.in_dispatcher[type_](self,data)
        else:
            subscriber.in_dispatcher[type_](self)





