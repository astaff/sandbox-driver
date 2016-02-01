#!/usr/bin/env python3

import json, collections


driver = None

class Subscriber():
    def __init__(self, harness=None):
        print('subscriber.__init__ called:')
        print('\tharness: '+str(harness))
        self.harness = harness

        self.in_dispatcher = {
            'command': lambda data: self._driver_harness.send_command(data),
            'meta': lambda data: self._driver_harness.meta_command(data)
        }

    def set_harness(self, harness):
        print('set_harness called')
        print('\tharness: '+str(harness))
        self.harness = harness


    def dispatch_message(self, message):
        print('dispatch_message called:')
        print('\tmessage: '+message)
        try:
            dictum = collections.OrderedDict(json.loads(message.strip(), object_pairs_hook=collections.OrderedDict))
            if 'type' in dictum and 'data' in dictum:
                if dictum['type'] in self.in_dispatcher:
                    self.in_dispatcher[dictum['type']](dictum['data'])
                else:
                    print('{error,malformed message, type not in in_dispatcher}')
                    return '{error,malformed message, type not in in_dispatcher}'
            else:
                print('{error:subscriber.dispatch_message type or data error}')
                return '{error:subscriber.dispatch_message type or data error}'
        except:
            print('{error:general subscriber.dispatch_message error}')
            return '{error:general subscriber.dispatch_message error}'





