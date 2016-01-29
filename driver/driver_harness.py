#!/usr/bin/env python3

"""
TODO: 
1. publish error reports to Bootloader
"""


import driver

class Harness(object):

	def __init__(self, publisher=None):
		"""
		"""
		print('driver_harness.__init__ called')
		self._publisher = publisher
		self.driver_dict = {}
		self.meta_dict = {
			'drivers' : lambda name,param: self.drivers(name,param),
			'add_driver' : lambda name,param: self.add_driver(name,param),
			'remove_driver' : lambda name,param: self.remove_driver(name,param),
			'callbacks' : lambda name,param: self.callbacks(name,param),
			'meta_callbacks' : lambda name, param: self.meta_callbacks(name,param),
			'set_meta_callback' : lambda name,param: self.set_meta_callback(name,param),
			'add_callback' : lambda name,param: self.add_callback(name,param),
			'remove_callback' : lambda name,param: self.remove_callback(name,param),
			'flow' : lambda name,param: self.flow(name,param),
			'clear_queue' : lambda name,param: self.clear_queue(name,param),
			'connect' : lambda name,param: self.connect(name,param),
			'disconnect' : lambda name,param: self.disconnect(name,param),
			'commands' : lambda name,param: self.commands(name,param)
		}


	def set_publisher(self, publisher):
		"""

		"""
		print('driver_harness.set_publisher called')
		self._publisher = publisher


	def drivers(self, name, param):
		"""

		"""
		print('driver_harness.drivers called')
		if name is None:
			name = "None"
		self._publisher.publish('frontend','driver',name,'drivers',list(self.driver_dict))


	def add_driver(self, name, param):
		"""

		"""
		print('driver_harness.add_driver called')
		self.driver_dict[name] = param


	def remove_driver(self, name, param):
		"""
		
		"""
		print('driver_harness.remove_driver called')
		del self.driver_dict[name]


	def callbacks(self, name, param):
		"""
		
		"""
		print('driver_harness.callbacks called')
		self._publisher.publish('frontend','driver',name,'callbacks',driver_dict[name].callbacks())


	def meta_callbacks(self, name, param):
		"""

		"""
		print('driver_harness.meta_callbacks called')
		self._publisher.publish('frontend','driver',name,'meta_callbacks',driver_dict[name].meta_callbacks())


	def set_meta_callback(self, name, param):
		"""

		"""
		print('driver_harness.set_meta_callback called')
		if isinstance(param,dict):
			self.driver_dict.get(name).set_meta_callback(list(param)[0],list(param.values)[0])
		self._publisher.publish('frontend','driver',name,'meta_callback',driver_dict.get(name).meta_callbacks())


	def add_callback(self, name, param):
		"""

		"""
		print('driver_harness.add_callback called')
		self.driver_dict[name].add_callback(list(param)[0],list(param.values())[0])
		self._publisher.publish('frontend','driver',name,'callbacks',self.driver_dict.get(name).callbacks())


	def remove_callback(self, name, param):
		"""

		"""
		print('driver_harness.remove_callback called')
		self.driver_dict[name].remove_callback(param)
		self._publisher.publish('frontend','driver',name,'callbacks',self.driver_dict.get(name).callbacks())


	def flow(self, name, param):
		"""
		
		"""
		print('driver_harness.flow called')
		self._publisher.publish('frontend','driver',name,'flow',self.driver_dict.get(name).flow())


	def clear_queue(self, name, param):
		"""

		"""
		print('driver_harness.clear_queue called')
		self.driver_dict.get(name).clear_queue()
		self.flow(name, None)


	def connect(self, name, param):
		"""
		
		"""
		print('driver_harness.connect called')
		self.driver_dict[name].connect()


	def disconnect(self, name, param):
		"""
		
		"""
		print('driver_harness.disconnect called')
		self.driver_dict.get(name).disconnect()


	def commands(self, name, param):
		"""

		"""
		print('driver_harness.commands called')
		self._publisher.publish('frontend','driver',name,'commands',self.driver_dict.get(name).commands())


	def meta_command(self, data):
		"""

		"""
		print('driver_harness.meta_command called')
		print('data: ')
		print(data)
		print()
		if isinstance(data, dict):
			name = data['name']
			value = data['message']
			if name in self.driver_dict:
				if isinstance(value, dict):
					message = list(value)[0]
					params = value[message]
					try:
						self.meta_dict[message](name,params)
					except:
						print('meta command for '+message+' failed')
						print('name: '+str(name))
						print('value: '+str(value))
						print('message: '+str(message))
						print('params: '+str(params))
						print(sys.exc_info()[0])
				elif isinstance(value, str):
					message = value
					try:
						self.meta_dict[message](name,None)
					except:
						print('meta command for '+message+' failed')
						print('name: '+str(name))
						print('value: '+str(value))
						print(sys.exc_info()[0])
			else:
				if isinstance(value, dict):
					message = list(value)[0]
					params = value[message]
					try:
						self.meta_dict[message](None, params)
					except:
						print('name not in drivers, meta command for '+message+' failed')
						print('name: '+str(name))
						print('value: '+str(value))
						print('message: '+str(message))
						print('params: '+str(params))
						print(sys.exc_info()[0])
				elif isinstance(value, str):
					message = value
					try:
						self.meta_dict[message](None,None)
					except:
						print('meta command for '+message+' failed')
						print('message: '+str(message)
						print(sys.exc_info()[0])


	def send_command(self, data):
		"""

		"""
		print('driver_harness.send_command called')
		print('data: ')
		print(data)
		print()
		if isinstance(data, dict):
			name = data['name']
			value = data['message']
			print('name: ')
			print(name)
			print('value: ')
			print(value)
			if name in self.driver_dict:
				try:
					self.driver_dict[name].send_command(value)
				except:
					print('driver command failed: '+sys.exc_info()[0])
			else:
				print('name not in drivers: '+sys.exc_info()[0])















