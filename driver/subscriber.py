#!/usr/bin/env python3

import json, collections


driver = None

class Subscriber():
    def __init__(self, driver_harness=None):
        self._driver_harness = driver_harness

        self.in_dispatcher = {
            'command': lambda data: self._driver_harness.send_command(data),
            'meta': lambda data: self._driver_harness.meta_command(data)
            #'move': lambda data: self._driver_harness.send_command(data),
            #'move_to': lambda data: self._driver_harness.send_command(data),
            #'home': lambda data: self._driver_harness.send_command(data),
            #'get_state': lambda data: self._driver_harness.get_state(data),
            #'clear_queue': lambda data: self._driver_harness.clear_queue(data),
            #'connect': lambda data: self._driver_harness.connect(data),
            #'disconnect': lambda data: self._driver_harness.disconnect(data),
            #'get_commands': lambda data: self._driver_harness.get_commands(data),
            #'get_drivers': lambda data: self._driver_harness.get_drivers(data)
        }

    def set_driver(self, driver_harness):
        print("set_driver_harness called")
        self._driver_harness = driver_harness


    def dispatch_message(self, message):
        print("dispatch_message called")
        try:
            dictum = collections.OrderedDict(json.loads(message.strip(), object_pairs_hook=collections.OrderedDict))
            if 'type' in dictum and 'data' in dictum:
                if dictum['type'] in self.in_dispatcher:
                    self.in_dispatcher[dictum['type']](dictum['data'])
                else:
                    print('report error here, malformed message, type not in in_dispatcher')
            else:
                print('report error here, malformed message, type or data not in message')
        except:
            print('*** error in subscriber.dispatch_message ***')
            raise





