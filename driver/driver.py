#!/usr/bin/env python3

#import serial
import asyncio, json, copy
from collections import Callable


class Output(asyncio.Protocol):


	def __init__(self, outer):
		self.outer = outer
		self._delimiter = "\n"
		self.data_buffer = ""
		self.transport = None


	def connection_made(self, transport):
		print("Output.connection_made called")
		self.transport = transport
		self.outer.smoothie_transport = transport
		transport.write("M114\r\n".encode())
		loop = asyncio.get_event_loop()
		self.outer._on_connection_made()


	def data_received(self, data):
		#print("Output.data_received called")
		self.data_buffer = self.data_buffer + data.decode()
		delimiter_index = self.data_buffer.rfind("\n")
		if delimiter_index >= 0:
			current_data = self.data_buffer[:delimiter_index]
			self.data_buffer = self.data_buffer[delimiter_index+1:]
			data_list = [e+self._delimiter for e in current_data.split(self._delimiter)]
			for datum in data_list:
				self.outer._smoothie_data_handler(datum)
		self.outer._on_raw_data(data)


	def connection_lost(self, exc):
		print("Output.connection_lost called")
		self.transport = None
		self.outer.smoothie_transport = None
		self.data_buffer = ""
		loop = asyncio.get_event_loop()
		self.outer._on_connection_lost()


class SmoothieDriver(object):
	"""




	How data flows to and from Smoothieboard:

	To:




	From:

	1. Data coming in is split up by delimiter ('\n') and then
	each section is sent to a callback (SmoothieDriver._smoothie_data_handler)
	The raw data is then sent to another callback (SmoothieDriver._raw_data_handler)

	Function: Output.data_received()
	-> _smoothie_data_handler - callback for raw data
	-> _raw_data_handler - callback for chunks of data separated by delimiter

	2. In SmoothieDriver._smoothie_data_handler data is divided between text data and
	JSON data, serial text data formatted for JSON. Either way, the data is then 
	reformatted into a list of standardized dictionary objects with the following format:

	[
		{
		  [MESSAGE]:
			{ 
			  [PARAMETER]:[VALUE],
			  ...
			}
		},
		...
	]

	3. The standard dictionary object is checked for specific flow control data and 
	flow control logic is updated accordingly.

	4. The standard dictionary object is then routed to the appropriate callback based
	on the message.




	"""

	command_queue = []
	simulation_queue = []
	
	smoothie_transport = None
	the_loop = None

	state_dict = {
		'simulation':False,
		'connected':False,
		'transport':False,
		'locked':False,
		'ack_received':True,
		'ack_ready':True,
		'queue_size':0
	}

	config_dict = {
		'delimiter':"\n",
		'message_ender':"\r\n",
		'ack_received_message':"ok",
		'ack_received_parameter':None,
		'ack_received_value':None,
		'ack_ready_message':"stat",
		'ack_ready_parameter':None,
		'ack_ready_value':"0",
	}

	callbacks_dict = {}
	# dict:
	#
	#  {
	#    <callback_name>:
	#    {
	#      callback: <CALLBACK OBJECT>,
	#      messages: [ <messages>... ]
	#    },
	#    ...
	#  }
	meta_callbacks_dict = {
		'on_connect' : None,
		'on_disconnect' : None,
		'on_empty_queue' : None,
		'on_raw_data' : None
	}

	commands_dict = {
		"rapid_move":{
			"code":"G0",
			"parameters":["","X","Y","Z","A","B"]
		},
		"linear_move":{
			"code":"G1",
			"parameters":["","X","Y","Z","A","B"]
		},
		"home":{
			"code":"G28",
			"parameters":["","X","Y","Z","A","B"]
		},
		"absolute":{
			"code":"G90",
			"parameters":[]
		},
		"relative":{
			"code":"G91",
			"parameters":[]
		},
		"feedrate":{
			"code":"F",
			"parameters":[]
		},
		"feedrate_a":{
			"code":"a",
			"parameters":[]
		},
		"feedrate_b":{
			"code":"b",
			"parameters":[]
		},
		"feedrate_c":{
			"code":"c",
			"parameters":[]
		},
		"reset":{
			"code":"ls sd",
			"parameters":[]
		},
		"enable_motors":{
			"code":"M17",
			"parameters":[]
		},
		"disable_motors":{
			"code":"M18",
			"parameters":[]
		},
		"start_feedback":{
			"code":"M62",
			"parameters":[]
		},
		"stop_feedback":{
			"code":"M63",
			"parameters":[]
		},
		"limit_switches":{
			"code":"M119",
			"parameters":[]
		},
		"halt":{
			"code":"M112",
			"parameters":[]
		},
		"reset_from_halt":{
			"code":"M999",
			"parameters":[]
		}
	}



	def __init__(self, simulate=False):
		print('driver.__init__ called')
		self.simulation = simulate
		self.the_loop = asyncio.get_event_loop()


	def callbacks(self):
		print('driver.callbakcs called')
		return copy.deepcopy(self.callbacks_dict)


	def meta_callbacks(self):
		print('driver.meta_callbacks called')
		return_dict = dict()
		for name, value in self.meta_callbacks_dict.items():
			if value is not None and isinstance(value, Callable):
				return_dict[name] = value.__name__
			else:
				return_dict[name] = 'None'
		#return copy.deepcopy(self.meta_callbacks_dict)
		return return_dict


	def set_meta_callback(self, name, callback):
		print('driver.set_meta_callback called')
		if name in self.meta_callbacks_dict and isinstance(callback, Callable):
			self.meta_callbacks_dict[name] = callback
		return self.meta_callbacks()


	def add_callback(self, callback, messages):
		print('driver.add_callback called')
		if callback.__name__ not in list(self.callbacks_dict):
			if isinstance(messages, list):
				self.callbacks_dict[callback.__name__] = {'callback':callback, 'messages':messages}
			else:
				self.callbacks_dict[callback.__name__] = {'callback':callback, 'messages':[messages]}
		elif message not in self.callbacks_dict[callback.__name__]['messages']:
			if isinstance(messages, list):
				self.callbacks_dict[callback.__name__]['messages'].extend(messages)
			else:
				self.callbacks_dict[callback.__name__]['messages'].append(messages)


	def remove_callback(self, callback_name):
		print('driver.remove_callback called')
		del self.callbacks_dict[callback_name]


	def flow(self):
		print('driver.flow called')
		return copy.deepcopy(self.state_dict)


	def clear_queue(self):
		print('driver.clear_queue called')
		self.command_queue = []
		self.state_dict['queue_size'] = len(self.command_queue)
		self.state_dict['ack_received'] = True
		self.state_dict['ack_ready'] = True


	def connect(self, device=None, port=None):
		"""
		"""
		print('driver.connect called')
		self.the_loop = asyncio.get_event_loop()
		#asyncio.async(serial.aio.create_serial_connection(self.the_loop, Output, '/dev/ttyUSB0', baudrate=115200))
		callbacker = Output(self)
		asyncio.async(self.the_loop.create_connection(lambda: callbacker, host='0.0.0.0', port=3333))


	def disconnect(self):
		"""
		"""
		print('driver.disconnect called')
		pass


	def commands(self):
		"""
		"""
		print('driver.commands called')
		return copy.deepcopy(self.commands_dict)


	def unlock(self):
		"""
		"""
		print('driver.unlock called')
		self.state_dict['ack_received'] = True
		self.state_dict['ack_ready'] = True
		self.lock_check()


	def send(self, message):
		print('driver.send called')
		message = message + self.config_dict['message_ender']
		if self.simulation:
			self.simulation_queue.append(message)
		else:
			if self.smoothie_transport is not None:
				if self.lock_check() == False:
					self.state_dict['ack_received'] = False
					self.smoothie_transport.write(message.encode())
			else:
				print("smoothie_transport is None????")



# flow control 

	def lock_check(self):
		print('driver.lock_check called')
		#print("SmoothieDriver.lock check called")
		if self.state_dict['ack_received'] and self.state_dict['ack_ready']:
			self.state_dict['locked'] = False
			#print("unlocked")
			return False
		else:
			self.state_dict['locked'] = True
			#print("locked")
			return True


	def _add_to_command_queue(self, command):
		print('driver._add_to_command_queue called')
		self.command_queue.append(command)
		self.state_dict['queue_size'] = len(self.command_queue)
		self._step_command_queue()


	def _step_command_queue(self):
		print('driver._step_command_queue called')
		self.lock_check()
		if self.state_dict['locked'] == False:
			if len(self.command_queue) == 0:
				if isinstance(self.meta_callbacks_dict['on_empty_queue'],Callable):
					self.meta_callbacks_dict['on_empty_queue']()
			else:
				self._send(self.command_queue.pop(0))
				self.state_dict['queue_size'] = len(self.command_queue)





	def _format_text_data(self, text_data):
		print('driver._format_text_data called')
		return_list = []
		remainder_data = text_data
		while remainder_data.find(',')>=0:
			stupid_dict = self._format_group( remainder_data[:remainder_data.find(',')] ) 
			return_list.append(stupid_dict)
			remainder_data = remainder_data[remainder_data.find(',')+1:]
		stupid_dict = self._format_group( remainder_data )
		return_list.append(stupid_dict)
		return return_list


	def _format_group(self, group_data):
		print('driver._format_group called')
		return_dict = dict()
		remainder_data = group_data
		if remainder_data.find(':')>=0:
			while remainder_data.find(':')>=0:
				message = remainder_data[:remainder_data.find(':')].replace('\n','').replace('\r','')
				remainder_data = remainder_data[remainder_data.find(':')+1:]
				if remainder_data.find(' ')>=0:
					parameter = remainder_data[:remainder_data.find(' ')].replace('\n','').replace('\r','')
					remainder_data = remainder_data[remainder_data.find(' ')+1:]
				else:
					parameter = remainder_data.replace('\r','').replace('\n','')
					return_dict[message] = parameter
		else:
			return_dict[group_data.strip()] = ''
		return return_dict


	def _format_json_data(self, json_data):

		#
		#	{ 
		#		name : value,
		#		... ,
		#		name : { ... }???
		#	}
		#
		#
		print('driver._format_json_data called')
		return_list = []
		for name, value in json_data.items():
			if isinstance(value, dict):
				message = name
				for value_name, value_value in value.items():
					parameter = value_name
					this_dict = {}
					this_dict[message] = {}
					this_dict[message][parameter] = value_value
					return_list.append(this_dict)
			else:
				message = 'None'
				parameter = name
				this_dict = {}
				this_dict[message] = {}
				this_dict[message][parameter] = value
				return_list.append(this_dict)


		#
		#	so, if json_data looks like:
		#	{ X:<f>, Y:<f>, Z:<f>, A:<f>, B:<f> }
		#
		#	it gets turned into:
		#	[ 
		#	  {  'None':
		#			{ X:<f>, Y:<f>, Z:<f>, A:<f>, B:<f> } 
		#	  } 
		#	]
		#


		return return_list


	def _process_message_dict(self, message_dict):
		print('driver._process_message_dict called')

		# first, check if ack_recieved confirmation
		if self.config_dict['ack_received_message'] in list(message_dict):
			value = message_dict.get(self.config_dict['ack_received_message'])
			if isinstance(value, dict):
				if self.config_dict['ack_receieved_parameter'] is None:
					self.state_dict['ack_received'] = True
				else:
					for value_name, value_value in value.items():
						if value_name == self.config_dict['ack_received_parameter']:
							if self.config_dict['ack_received_value'] is None or value_value == self.config_dict['ack_receieved_value']:
								self.state_dict['ack_received'] = True
			else:
				if self.config_dict['ack_received_parameter'] is None:
					if self.config_dict['ack_received_value'] is None or value == self.config_dict['ack_received_value']:
						self.state_dict['ack_received'] = True


		# second, check if ack_recieved confirmation
		if self.config_dict['ack_ready_message'] in list(self.config_dict['ack_ready_message']):
			value = message_dict.get(self.config_dict['ack_ready_message'])
			if isinstance(value, dict):
				if self.config_dict['ack_ready_parameter'] is None:
					self.state_dict['ack_ready'] = True
				else:
					for value_name, value_value in value.items():
						if value_name == self.config_dict['ack_ready_parameter']:
							if self.config_dict['ack_ready_value'] is None or value_value == self.config_dict['ack_ready_value']:
								self.state_dict['ack_ready'] = True
							else:
								self.state_dict['ack_ready'] = False
			else:
				if self.config_dict['ack_ready_parameter'] is None:
					if self.config_dict['ack_ready_value'] is None or value == self.config_dict['ack_ready_value']:
						self.state_dict['ack_ready'] = True
					else:
						self.state_dict['ack_ready'] = False


		# finally, pass messages to their respective callbacks based on callbacks and messages they're registered to receive

		# eg:
		#
		#	message dict:
		#	{ 'None':
		#		{ X:<f>, Y:<f>, Z:<f>, A:<f>, B:<f> } 
		#	}
		#
		#	---->  name_message = 'None'
		#	---->  value = { X:<f>, Y:<f>, Z:<f>, A:<f>, B:<f> } 
		#
		#

		for name_message, value in message_dict.items():

			for callback_name, callback in self.callbacks_dict.items():
				if name_message in callback['messages']:
					callback['callback'](value)

		self._step_command_queue()


# Device callbacks
	def _on_connection_made(self):
		print('driver._on_connection_made called')
		self.connected = True
		self.state_dict['transport'] = True if self.smoothie_transport else False
		print('connected!')
		if isinstance(self.meta_callbacks_dict['on_connect'],Callable):
			self.meta_callbacks_dict['on_connect']()


	def _on_raw_data(self, data):
		print('driver._on_raw_data called')
		if isinstance(self.meta_callbacks_dict['on_raw_data'],Callable):
			self.meta_callbacks_dict['on_raw_data']()


	def _smoothie_data_handler(self, datum):
		"""Handles incoming data from Smoothieboard that has already been split by delimiter

		"""
		print('driver._smoothie_data_handler called')
		json_data = ""
		text_data = datum

		if self.config_dict['ack_received_message'] in datum:
			self.ack_received = True

		if datum.find('{')>=0:
			json_data = datum[datum.find('{'):].replace('\n','').replace('\r','')
			text_data = datum[:datum.index('{')]
		
		#print("*"*15)
		#print("json_data:")
		#print(json_data)
		#print()
		#print("text_data:")
		#print(text_data)
		#print("*"*15)

		if text_data != "":
			text_message_list = self._format_text_data(text_data)
			#print()
			#print("_smoothie_data_handler --> text_message_list")
			#print(text_message_list)
			#print()
			for message in text_message_list:
				#print("_smoothie_data_handler --> message")
				#print(message)
				#print()
				self._process_message_dict(message)

		if json_data != "":
			try:
				json_data_dict = json.loads(json_data)
				json_message_list = self._format_json_data(json_data_dict)
				for message in json_message_list:
					self._process_message_dict(message)
			except:
				print('json.loads(json_data) error')
				raise

	def _on_connection_lost(self):
		print('driver._on_connection_lost called')
		self.connected = False
		self.state_dict['transport'] = True if self.smoothie_transport else False
		print('not connected!')
		if isinstance(self.meta_callbacks_dict['on_disconnect'],Callable):
			self.meta_callbacks_dict['on_disconnect']()


	def send_command(self, data):
		#	all entries should be of the form:
		#	1. command
		#
		#	2. data
		#	
		#	value 	
		#
		#	- or -
		#
		#	{
		#		'parameter':value,
		#		...
		#	}
		#

		#, arg=None,**kwargs):
		print('driver.send_command called!')
		command_text = ""
		# check if command is in commands dictionary
		if command in list(self.commands_dict):
			print("command is in list!")
			command_text = self.commands_dict[command]["code"]

			if isinstance(data, dict):
				for param, val in data.items():
					if param in commands_dict.get(command).parameters:
						command_text.append(" ")
						command_text.append("%s%s" % (param,val))
			else:
				command_text.append(data)

			print("command_text:")
			print(command_text)
			print()
			self.send(command_text)

		else:	#check whether command is actually a code in commands dictionary
			for cmd, dat in self.commands_dict.items():
				if command == dat.get("code"):
					print("command is a code in command list!")
					command_text = command

					if isinstance(data, dict):			
						for param, val in data.items():
							if param in val.parameters:
								command_text.append(" ")
								command_text.append("%s%s" % (param,val))
					else:
						command_text.append(data)

					print("command_text:")
					print(command_text)
					print()
					self.send(command_text)
					break

		#else:
		#	print("command is NOT in list!")




if __name__ == '__main__':
	smooth = OTOneDriver()
	run_called = False


	def runner():
		smooth.connect()
		print()
		print("smooth.get_just_commands:")
		print(smooth.get_just_commands())
		print()
		print("-"*10)
		print()

		loop = asyncio.get_event_loop()
		loop.call_later(4, run_commands)
		loop.run_forever()


	def run_commands():
		#i = 0
		#for command in smooth.get_just_commands():
		#	i = i+1
		#	if i < 2:
		#		print()
		#		print("command to send:")
		#		print(command)
		#		print()
		print()
		cmd = input("enter a command:\n")
		if cmd == "clear":
			smooth.clear_queue()
		if cmd == "unlock":
			smooth.unlock()
		if cmd == "help" or cmd == "h":
			print()
			print("possible commands:")
			print("-"*10)
			print("clear")
			print("help")
			print("-"*10)
			print(smooth.get_just_commands())
		else:
			smooth.send_command(cmd)
		#command
		loop = asyncio.get_event_loop()
		loop.call_later(2, run_commands)


	def check_run_called():
		if run_called == False:
			run_commands()


	try:
		loop = asyncio.get_event_loop()
		loop.run_until_complete(runner())

		#loop.run_forever()
	finally:
		pass
		#loop.close()












