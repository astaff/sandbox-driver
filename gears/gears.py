#!/usr/bin/env python3

#import serial
import asyncio, json


class Output(asyncio.Protocol):


	def __init__(self, outer):
		self.outer = outer
		self._delimiter = "\n"
		self.data_buffer = ""
		self.transport = None


	def connection_made(self, transport):
		self.transport = transport
		self.outer.smoothie_transport = transport
		transport.write("M114\r\n".encode())
		loop = asyncio.get_event_loop()
		self.outer._on_connection_made()


	def data_received(self, data):
		self.data_buffer = self.data_buffer + data.decode()
		delimiter_index = self.data_buffer.rfind("\n")
		if delimiter_index >= 0:
			current_data = self.data_buffer[:delimiter_index]
			self.data_buffer = self.data_buffer[delimiter_index+1:]
			data_list = [e+self._delimiter for e in current_data.split(self._delimiter)]
			for datum in data_list:
				self.outer._smoothie_data_handler(datum)
		self.outer._raw_data_handler(data)


	def connection_lost(self, exc):
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

	simulation = False
	command_queue = []
	simulation_queue = []

	connected = False
	
	smoothie_transport = None


	delimeter = "\n"
	message_ender = "\r\n"


	# flow control variables
	awaiting_ack = False
	lock = False
	ack_received = False
	ack_ready = True

	ack_received_message = "ok"
	ack_received_parameter = None # not used in this case
	ack_received_value = None # not used in this case

	ack_ready_message = "stat"
	ack_received_parameter = None # not used in this case
	ack_ready_value = "0"

	on_empty_queue_callback = None


	callbacks_name_callback_messages = []
	# dict:
	#
	#  {
	#    <CALLBACK_NAME>:
	#    {
	#      callback: <CALLBACK OBJECT>,
	#      messages: [ LIST OF MESSAGES... ]
	#    }
	#  }


	the_loop = None




	def __init__(self, simulate=False, on_empty_queue=None):
		self.simulation = simulate
		self.the_loop = asyncio.get_event_loop()
		self.on_empty_queue_callback = on_empty_queue


	def connect(self, device=None, port=None):
		self.the_loop = asyncio.get_event_loop()
		#asyncio.async(serial.aio.create_serial_connection(self.the_loop, Output, '/dev/ttyUSB0', baudrate=115200))
		callbacker = Output(self)
		asyncio.async(self.the_loop.create_connection(lambda: callbacker, host='0.0.0.0', port=3333))


	def disconnect(self):
		pass


	def set_on_empty_queue_callback(self, on_empty_queue):
		self.on_empty_queue_callback = on_empty_queue


	def on_empty_queue(self):
		if hasattr(self.on_empty_queue_callback, '__call__'):
			self.on_empty_queue_callback()


	def register_callback(self, callback, message):
		if callback.__name__ not in list(self.callbacks):
			new_dict = {'callback':callback, 'messages':[message]}
			self.callbacks_name_callback_messages[callback.__name__] = new_dict
		elif message not in self.callbacks_name_callback_messages[callback.__name__]['messages']:
			self.callbacks_name_callback_messages[callback.__name__]['messages'].append(message)


	def remove_callback(self, callback_name):
		del self.callbacks_name_callback_messages[callback_name]


	def remove_callback_message(self, callback_name, message):
		self.callbacks_name_callback_messages[callback_name]['messages'].remove(message)


	def unlock(self):
		self.ack_received = True
		self.ack_ready = True
		self.lock_check()


	def clear_queue(self):
		self.command_queue = []


	def send(self, message):
		print()
		print("send called!")
		print()
		message = message + self.message_ender
		print(message)
		print("...........")
		if self.simulation:
			self.simulation_queue.append(message)
			print("simulation queue")
			print(self.simulation_queue)
			#self.simulate_response(message)
		else:
			if self.smoothie_transport is not None:
				if self.lock_check() == False:
					self.ack_received = False
					print("smoothie_transport BOOM!!!!")
					print('encoded message:')
					print(message.encode())
					self.smoothie_transport.write(message.encode())
			else:
				print("smoothie_transport is None????")


# flow control 

	def lock_check(self):
		print("lock check called")
		if self.ack_received and self.ack_ready:
			self.locked = False
			print("unlocked")
			return False
		else:
			self.locked = True
			print("locked")
			return True

	def _add_to_command_queue(self, command):
		self.command_queue.append(command)
		self._step_command_queue()


	def _step_command_queue(self):
		self.lock_check()
		if self.locked == False:
			if len(self.command_queue) == 0:
				self.on_empty_queue()
			else:
				self._send(self.command_queue.pop(0))





	def _format_text_data(self, text_data):
		return_list = []
		remainder_data = text_data
		while remainder_data.find(',')>=0:
			stupid_dict = self._format_group( remainder_data[:remainder_data.find(',')] ) 
			print(1)
			print("_format_text_data --> stupid_dict1")
			print(stupid_dict)
			print(2)
			return_list.append(stupid_dict)
			remainder_data = remainder_data[remainder_data.find(',')+1:]
		stupid_dict = self._format_group( remainder_data )
		return_list.append(stupid_dict)
		print(3)
		print("_format_text_data --> stupid_dict2")
		print(stupid_dict)
		print(4)
		print("_format_text_data --> return_list")
		print(return_list)
		return return_list


	def _format_group(self, group_data):
		return_dict = dict()
		remainder_data = group_data
		if remainder_data.find(':')>=0:
			print(5)
			print("_format_group --> 1")
			print(6)
			while remainder_data.find(':')>=0:
				message = remainder_data[:remainder_data.find(':')].replace('\n','').replace('\r','')
				print(7)
				print("message before:")
				print(message)
				print(8)
				print("message after:")
				print(message.replace(" ",""))
				print(9)
				remainder_data = remainder_data[remainder_data.find(':')+1:]
				if remainder_data.find(' ')>=0:
					parameter = remainder_data[:remainder_data.find(' ')].replace('\n','').replace('\r','')
					remainder_data = remainder_data[remainder_data.find(' ')+1:]
				else:
					parameter = remainder_data.replace('\r','').replace('\n','')
					return_dict[message] = parameter
		else:
			print(10)
			print("_format_group --> 2")
			print(group_data)
			print(11)
			print(12)
			return_dict[group_data.strip()] = ''
			#("\n", "")] = ''
		return return_dict


	def _format_json_data(self, json_data):
		return_list = []
		for name, value in json_data.items():
			message = name
			if isinstance(value, dict):
				for value_name, value_value in value.items():
					parameter = value_name
					this_dict = {}
					this_dict[message] = {}
					this_dict[message][parameter] = value_value
					return_list.append(this_dict)
			else:
				this_dict = {}
				this_dict[message] = value
				return_list.append(this_dict)

		return return_list


	def _process_message_dict(self, message_dict):

		# first, check if ack_recieved confirmation
		if self.ack_received_message in list(message_dict):
			print("ack_received checking...")
			print(list(message_dict))
			value = message_dict.get(self.ack_received_message)
			if isinstance(value, dict):
				if self.ack_receieved_parameter is None:
					self.ack_received = True
				else:
					for value_name, value_value in value.items():
						if value_name == self.ack_received_parameter:
							if self.ack_received_value is None or value_value == self.ack_receieved_value:
								self.ack_received = True
			else:
				if self.ack_received_parameter is None:
					if self.ack_received_value is None or value == self.ack_received_value:
						self.ack_received = True


		# second, check if ack_recieved confirmation
		if self.ack_ready_message in list(self.ack_ready_message):
			print("ack_ready checking...")
			print(list(message_dict))
			value = message_dict.get(self.ack_ready_message)
			if isinstance(value, dict):
				if self.ack_ready_parameter is None:
					self.ack_ready = True
				else:
					for value_name, value_value in value.items():
						if value_name == self.ack_ready_parameter:
							if self.ack_ready_value is None or value_value == self.ack_ready_value:
								self.ack_ready = True
							else:
								self.ack_ready = False
			else:
				if self.ack_ready_parameter is None:
					if self.ack_ready_value is None or value == self.ack_ready_value:
						print("111111")
						self.ack_ready = True
					else:
						print("222222")
						self.ack_ready = False


		# finally, pass messages to their respective callbacks based on callbacks and messages they're registered to receive
		print("message_dict:")
		print(message_dict)
		print(13)

		for name_message, value in message_dict.items():

			for callback in self.callbacks_name_callback_messages:
				if name_message in callback['messages']:
					callback['callback'](message_dict)

		self._step_command_queue()








# Device callbacks
	def _on_connection_made(self):
		self.connected = True
		print('connected!')


	def _raw_data_handler(self, data):
		print()
		print('raw data:')
		print(data)
		print()



	def _smoothie_data_handler(self, datum):
		"""Handles incoming data from Smoothieboard that has already been split by delimiter

		"""
		json_data = ""
		text_data = datum

		if self.ack_received_message in datum:
			self.ack_received = True

		if datum.find('{')>=0:
			json_data = datum[datum.find('{'):].replace('\n','').replace('\r','')
			text_data = datum[:datum.index('{')]
		
		print()
		print("json_data:")
		print(json_data)
		print()
		print("text_data:")
		print(text_data)
		print()

		if text_data != "":
			text_message_list = self._format_text_data(text_data)
			print()
			print("_smoothie_data_handler --> text_message_list")
			print(text_message_list)
			print()
			for message in text_message_list:
				print("_smoothie_data_handler --> message")
				print(message)
				print()
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
		self.connected = False
		print('not connected!')



class OpenTronsGears(SmoothieDriver):


	commands_dictionary = {
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

	def __init__(self, *args, **kwargs):
		super(self.__class__, self).__init__(*args, **kwargs)


	def get_commands(self):
		return_dict = {}
		return_dict.update(self.commands_dictionary)
		return return_dict


	def get_just_commands(self):
		return_list = []
		return_list.extend(list(self.commands_dictionary))
		return list(return_list)


	def get_command_parameters(self, command):
		parameters = []
		if command in list(self.commands_dictionary):
			parameters = self.commands_dictionary.get(command).parameters
		return paramters
	

	def send_command(self, command, arg=None,**kwargs):
		print('send_command called!')
		command_text = ""
		if command in list(self.commands_dictionary):
			print("command is in list!")
			command_text = self.commands_dictionary[command]["code"]

			if arg is not None:
				command_text.append("%s" % arg.upper())

			for key in kwargs:
				if key in commands_dictionary.get(command).parameters:
					command_text.append(" ")
					command_text.append("%s%s" % (key.upper(),kwargs[key]))

			print("command_text:")
			print(command_text)
			print()
			self.send(command_text)
		else:
			print("command is NOT in list!")




if __name__ == '__main__':
	smooth = OpenTronsGears()
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












