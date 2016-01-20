#!/usr/bin/env python3

import driver

class Harness(object):

	def __init__(self, publisher=None):
		self._publisher = publisher
		self.driver_dict = {}

		self.driver_dict['otone'] = driver.OTOneDriver()
		def none_callback(message_value):
			self._publisher.publish('None',message_value)

		self.driver_dict['otone'].register_callback(none_callback, 'None')


	def set_publisher(self,publisher):
		self._publisher = publisher


	def register_callback_with_driver(self, driver_name, callback, messages):
		pass


	def add_driver(self, driver_name, driver):
		if driver_name not in list(self.driver_dict):
			self.driver_dict[driver_name] = driver
			print(driver_name + " added to drivers")
			self.publish_state(None)
		else:
			print(driver_name + " already in drivers")
			self.publish_state(None)	


	def remove_driver(self, driver_name):
		if driver_name in list(self.driver_dict):
			del self.driver_dict[driver_name]
			print(driver_name + " removed")
		else:
			print(driver_name + " not in drivers")


	def get_drivers_info(self, data):		
		#	eg:
		#	{
		#		'otone':
		#		{
		#			'state' : { ... },
		#			'callbacks' : {
		#				<callback_name> : [ <messages>... ],
		#				...
		#			}
		#		},
		#		...
		#	}
		#
		#
		return_dict = {}
		for driver in list(self.driver_dict):
			return_dict.update(self.driver_dict[driver].get_info())
		return return_dict


	def publish_drives_info(self, data):
		return_dict = self.get_drivers_info(None)
		self._publisher.publish('drivers_info',return_dict)
		return return_dict


	def publish_drivers(self, data):
		return_list = self.get_drivers(None)
		self.publisher.publish('drivers',return_list)
		return return_list


	def connect(self, data):
		self.driver_dict.get('otone').connect()
		return self.publish_state(None)


	def disconnect(self, data):
		self.driver_dict.get('otone').disconnect()
		return self.publish_state(None)


	def clear_queue(self, data):
		self.driver_dict.get('otone').clear_queue()
		return self.publish_state(None)


	def send_command(self, data):
		#TODO publish driver_state, dict
		if isinstance(data, dict):
			if 'command' in list(data):
				if 'params' in list(data):
					self.driver_dict.get('otone').send_command(data.get('command'),data.get('params'))
				else:
					self.driver_dict.get('otone').send_command(data.get('command'),None)
		return self.publish_state(None)


	def get_commands(self, data):
		return_dict = {}
		return_dict.update(self.driver_dict.get('otone').get_commands())
		return return_dict


	def publish_commands(self, data):
		return_dict = self.get_commands(None)
		self.publisher.publish('commands', return_dict)
		return return_dict


	def get_state(self, data):
		return_dict = {}
		return_dict.update(self.driver_dict.get('otone').get_state())
		return_date['drivers'] = self.get_drivers(None)
		return return_dict


	def publish_state(self, data):
		return_dict = self.get_state(None)
		self.publisher.publish('state', return_dict)
		return return_dict








