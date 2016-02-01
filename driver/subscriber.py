#!/usr/bin/env python3

import json, collections
import sys
import datetime

driver = None

class Subscriber():
    def __init__(self, harness=None):
        print(datetime.datetime.now(),' - subscriber.__init__:')
        print('\tharness: ',str(harness))
        self.harness = harness

        self.in_dispatcher = {
            'command': lambda data: self._driver_harness.send_command(data),
            'meta': lambda data: self._driver_harness.meta_command(data)
        }

    def set_harness(self, harness):
        print(datetime.datetime.now(),' - set_harness:')
        print('\tharness: ',str(harness))
        self.harness = harness


    def dispatch_message(self, message):
        print(datetime.datetime.now(),' - dispatch_message:')
        print('\tmessage: ',str(message))
        try:
            dictum = collections.OrderedDict(json.loads(message.strip(), object_pairs_hook=collections.OrderedDict))
            if 'type' in dictum and 'data' in dictum:
                if dictum['type'] in self.in_dispatcher:
                    self.in_dispatcher[dictum['type']](dictum['data'])
                else:
                    print(datetime.datetime.now(),' - {error,malformed message, type not in in_dispatcher}\n\r',sys.exc_info()[0])
                    return '{error,malformed message, type not in in_dispatcher}'
            else:
                print(datetime.datetime.now(),' - {error:subscriber.dispatch_message type or data error}\n\r',sys.exc_info()[0])
                return '{error:subscriber.dispatch_message type or data error}'
        except:
            print(datetime.datetime.now(),' - {error:general subscriber.dispatch_message error}\n\r',sys.exc_info()[0])
            return '{error:general subscriber.dispatch_message error}'





