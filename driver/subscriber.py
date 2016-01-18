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

def set_driver(driver):
    print("set_driver called")
    driver = driver


def dispatch_message(message):
    print("dispatch_message called")
	try:
        dictum = collections.OrderedDict(json.loads(message.strip(), object_pairs_hook=collections.OrderedDict))
        if 'data' in dictum:
            in_dispatch(dictum['type'],dictum['data'])
        else:
            in_dispatch(dictum['type'],None)
    except:
        print('*** error in subscriber.dispatch_message ***')
        raise


def dispatch(data):
    print("dispatch called")
	if data is not None:
        in_dispatcher[type_](self,data)
    else:
        in_dispatcher[type_](self)


class Subscriber():
	def __init__(self, driver=None):
		driver = driver


