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
		if session is not None:
			caller = session


	def set_caller(self, session):
		caller = session


	def dispatch_message(self, message):
		try:
			dictum = collections.OrderedDict(json.loads(message.strip(), object_pairs_hook=collections.OrderedDict))
			if 'data' in dictum:
    			dispatch(dictum['type'],dictum['data'])
    		else:
    			dispatch(dictum['type'],None)
    	except:
    		print('*** error in publisher.dispatch_message ***')
    		raise


	def dispatch(self, data):
		if data is not None:
			out_dispatcher[type_](self,data)
		else:
			out_dispatcher[type_](self)


	def send_message(self,type_,data_):
		if caller is not None and type_ is not None:
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


