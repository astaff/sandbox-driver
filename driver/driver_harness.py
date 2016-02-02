#!/usr/bin/env python3

"""
TODO:
- nose testing someday
"""

import driver
import sys
import datetime

class Harness(object):

	def __init__(self, publisher=None):
		"""
		"""
		print(datetime.datetime.now(),' - driver_harness.__init__:')
		print('\tpublisher: '+str(publisher))
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
			'commands' : lambda name,param: self.commands(name,param),
			'configs' : lambda name,param: self.configs(name,param),
			'set_config' : lambda name,param: self.set_config(name,param)
		}


	def set_publisher(self, publisher):
		"""
		"""
		print(datetime.datetime.now(),' - driver_harness.set_publisher:')
		print('\tpublisher: ',publisher)
		self._publisher = publisher


	def drivers(self, name, param):
		"""
		name: n/a
		param: n/a
		"""
		print(datetime.datetime.now(),'- driver_harness.drivers:')
		print('\tname: ',name)
		print('\tparam: ',param)
		if name is None:
			name = 'None'
		self._publisher.publish('frontend','driver',name,'drivers',list(self.driver_dict))


	def add_driver(self, name, param):
		"""
		name: name of driver to add_driver
		param: driver object
		"""
		print(datetime.datetime.now(),' - driver_harness.add_driver:')
		print('\tname: ',name)
		print('\tparam: ',param)
		self.driver_dict[name] = param


	def remove_driver(self, name, param):
		"""
		name: name of driver to be driver
		param: n/a
		"""
		print(datetime.datetime.now(),' - driver_harness.remove_driver:')
		print('\tname: ',name)
		print('\tparam: ',param)
		del self.driver_dict[name]


	def callbacks(self, name, param):
		"""
		name: name of driver
		param: n/a
		"""
		print(datetime.datetime.now(),' - driver_harness.callbacks:')
		print('\tname: ',name)
		print('\tparam: ',param)
		self._publisher.publish('frontend','driver',name,'callbacks',self.driver_dict[name].callbacks())


	def meta_callbacks(self, name, param):
		"""
		name: name of driver
		param: n/a
		"""
		print(datetime.datetime.now(),' - driver_harness.meta_callbacks:')
		print('\tname: ',name)
		print('\tparam: ',param)
		self._publisher.publish('frontend','driver',name,'meta_callbacks',self.driver_dict[name].meta_callbacks())


	def set_meta_callback(self, name, param):
		"""
		name: name of driver
		param: { meta-callback-name : meta-callback-object }
		"""
		print(datetime.datetime.now(),' - driver_harness.set_meta_callback:')
		print('\tname: ',name)
		print('\tparam: ',param)
		if isinstance(param,dict):
			self.driver_dict.get(name).set_meta_callback(list(param)[0],list(param.values)[0])
		self._publisher.publish('frontend','driver',name,'meta_callback',self.driver_dict.get(name).meta_callbacks())


	def add_callback(self, name, param):
		"""
		name: name of driver
		param: { callback obj: [messages list] }
		"""
		print(datetime.datetime.now(),' - driver_harness.add_callback:')
		print('\tname: ',name)
		print('\tparam: ',param)
		self.driver_dict[name].add_callback(list(param)[0],list(param.values())[0])
		self._publisher.publish('frontend','driver',name,'callbacks',self.driver_dict.get(name).callbacks())


	def remove_callback(self, name, param):
		"""
		name: name of driver
		param: name of callback to remove
		"""
		print(datetime.datetime.now(),' - driver_harness.remove_callback:')
		print('\tname: ',name)
		print('\tparam: ',param)
		self.driver_dict[name].remove_callback(param)
		self._publisher.publish('frontend','driver',name,'callbacks',self.driver_dict.get(name).callbacks())


	def flow(self, name, param):
		"""
		name: name of driver
		param: n/a
		"""
		print(datetime.datetime.now(),' - driver_harness.flow:')
		print('\tname: ',name)
		print('\tparam: ',param)
		self._publisher.publish('frontend','driver',name,'flow',self.driver_dict.get(name).flow())


	def clear_queue(self, name, param):
		"""
		name: name of driver
		param: n/a
		"""
		print(datetime.datetime.now(),' - driver_harness.clear_queue:')
		print('\tname: ',name)
		print('\tparam: ',param)
		self.driver_dict.get(name).clear_queue()
		self.flow(name, None)


	def connect(self, name, param):
		"""
		name: name of driver
		param: n/a
		"""
		print(datetime.datetime.now(),' - driver_harness.connect:')
		print('\tname: ',name)
		print('\tparam: ',param)
		self.driver_dict[name].connect()


	def disconnect(self, name, param):
		"""
		name: name of driver
		param: n/a
		"""
		print(datetime.datetime.now(),' - driver_harness.disconnect:')
		print('\tname: ',name)
		print('\tparam: ',param)
		self.driver_dict.get(name).disconnect()


	def commands(self, name, param):
		"""
		name: name of driver
		param: n/a
		"""
		print(datetime.datetime.now(),' - driver_harness.commands:')
		print('\tname: ',name)
		print('\tparam: ',param)
		self._publisher.publish('frontend','driver',name,'commands',self.driver_dict.get(name).commands())


	def meta_commands(self, name, param):
		"""
		name: name of driver
		param: n/a
		"""
		print(datetime.datetime.now(),' - driver_harness.meta_commands:')
		print('\tname: ',name)
		print('\tparam: ',param)
		self._publisher.publish('frontend','driver',name,'meta_commands',copy.deepcopy(self.meta_dict))

	def configs(self, name, param):
		"""
		name: name of driver
		param: n/a
		"""
		print(datetime.datetime.now(),' - driver_harness.meta_commands:')
		print('\tname: ',name)
		print('\tparam: ',param)
		self._publisher.publish('frontend','driver',name,'configs',self.driver_dict.get(name).configs())


	def set_config(self, name, param):
		"""
		name: name
		param: { config name : config value }
		"""
		print(datetime.datetime.now(),' - driver_harness.meta_commands:')
		print('\tname: ',str(name))
		print('\tparam: ',str(param))
		if isinstance(param,dict):
			self.driver_dict.get(name).set_config(list(param)[0],list(param.values)[0])
		self._publisher.publish('frontend','driver',name,'configs',self.driver_dict.get(name).configs())


	def meta_command(self, data):
		"""

		data should be in the form:

		{
			'name': name,

			'message': value

		}

		where name the name of the driver or None if n/a,

		and value is one of two forms:

		1. string

		2. {command:params}
			params --> {param1:value, ... , paramN:value}


		"""
		print(datetime.datetime.now(),' - driver_harness.meta_command:')
		print('\tdata: ',data)
		if isinstance(data, dict):
			name = data['name']
			value = data['message']
			if name in self.driver_dict:
				if isinstance(value, dict):
					command = list(value)[0]
					params = value[command]
					try:
						self.meta_dict[command](name,params)
					except:
						self._publisher.publish('frontend','driver',name,'error',sys.exc_info())
						print(datetime.datetime.now(),' - meta_command error: ',sys.exc_info())
				elif isinstance(value, str):
					command = value
					try:
						self.meta_dict[command](name,None)
					except:
						self._publisher.publish('frontend','driver',name,'error',sys.exc_info())
						print(datetime.datetime.now(),' - meta_command error: ',sys.exc_info())
			else:
				if isinstance(value, dict):
					command = list(value)[0]
					params = value[command]
					try:
						self.meta_dict[command](None, params)
					except:
						self._publisher.publish('frontend','driver',name,'error',sys.exc_info())
						print(datetime.datetime.now(),' - meta_command error, name not in drivers: ',sys.exc_info())
				elif isinstance(value, str):
					command = value
					try:
						self.meta_dict[command](None,None)
					except:
						self._publisher.publish('frontend','driver','None','error',sys.exc_info())
						print(datetime.datetime.now(),' - meta_command error, name not in drivers: ',sys.exc_info())


	def send_command(self, data):
		"""
		data:
		{
			'name': <name-of-driver>
			'message': <string> or { message : {param:values} } <--- the part the driver cares about
		}
		"""
		print('driver_harness.send_command:')
		print('\tdata: '+str(data))
		if isinstance(data, dict):
			name = data['name']
			value = data['message']
			if name in self.driver_dict:
				try:
					self.driver_dict[name].send_command(value)
				except:
					self._publisher.publish('frontend','driver',name,'error',sys.exc_info()[0])
					print(datetime.datetime.now(),' - send_command error: '+sys.exc_info()[0])
			else:
				self._publisher.publish('frontend','driver','None','error',sys.exc_info()[0])
				print(datetime.datetime.now(),' - send_command_error, name not in drivers: '+sys.exc_info()[0])















