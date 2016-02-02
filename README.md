# sandbox-driver
testing new driver code for communication with smoothieboard


This code handles communication with "Drivers" using Crossbar.io and Ser2net. Crossbar.io 
is used for communication with other areas of code within Docker containers, such as Bootloader, 
Frontend, and Labware. Ser2net is used for serial communication with the devices. There is 
currently only one device, the Smoothieboard, however there will be others.

The code is made up of the following modules:
- [driver_client.py](#driver_clientpy)
- [subscriber.py](#subscriberpy)
- [publisher.py](#publisherpy)
- [driver_harness.py](#driver_harnesspy)
- [driver.py](#driverpy)


---
## driver_client.py:

This module initiates the others and sets up communication over Crossbar.io, listening on 
url topic 'com.opentrons.driver'. When used in other sections of code, the url topic 
listened on should be adjusted, for example, in Labware it should listen on url topic 
'com.opentrons.labware'. It is also important to note that this is also where callbacks are 
defined and added for communication back to other sections of code based on particular messages 
received from the device. There is more on callbacks below.


---
## subscriber.py

This module is where messages coming in on the listened to url topic get routed first. Its 
main feature is a dictionary called in_dispatcher. In_dispatcher is used to route messages based 
on their 'type'. In Driver, there are only two types, 'command' and 'meta', and both lead to 
driver_harness.py. There was some thought as to moving all of subscriber.py into driver_harness.py, 
however it was decided not to because there is a good chance more in_dispatcher entries will be 
useful in other sections of code and possibly require other modules besides the driver_harness module.
It is also useful to separate out these types of messages before entry into driver_harness.py.

Incoming Data Format:

```
{
	'type': string,
	'data':
	{
		'name': string,
		'message':{message:param}
	}
}
```


---
## driver_harness.py

This module uses the word harness because it harnesses the drivers for the various devices, 
although there is currently only one device, Smoothieboard, aka 'smoothie' for short.
Messages sent to driver_harness.py are divided into two categories, "command" and "meta".
Meta messages are messages about the driver and drivers, and commands are messages to the 
devices via their drivers. Driver_harness has two important dictionary objects, driver_dict 
and meta_dict. driver_dict maps the driver names to the drivers, for example 
{ 'smoothie' : "smoothie driver object" }. Meta_dict is similar to in_dispatcher in subscriber.py, 
except that it is for meta commands, and they are:

	'drivers': Publish a list of the drivers.

	'add_driver': Add a given drivername and driver to the driver_dict as a key-value pair, and return 'drivers'.

	'remove_driver': Remove a given drivername and driver pair from the driver_dict, and return 'drivers'.

	'callbacks': Publish a dictionary made up of callback name and messages key-value pairs from a given driver.

	'meta_callbacks': Publish a dictionary of the meta callbacks for a given driver in the form meta-callback-name : name-of-callback. The meta-callback-names are:
		'on_raw_data'
		'on_connect'
		'on_empty_queue'
		'on_disconnect'

	'set_meta_callback': Set a callback for a given meta-callback for a given driver, and return 'meta_callbacks'.

	'add_callback': Add a callback to a given driver, and return 'callbacks.

	'remove_callback': Remove a given callback from a given driver, and return 'callbacks'.

	'flow': Publish flow control/state data, a copy of the driver's state_dict, for a given driver.

	'clear_queue': Clears the command queue for a given driver, and returns 'flow'.

	'connect': Call the connect command on the given driver.

	'configs': Publish the configs data, a copy of the driver's config_dict, for a given driver.

	'set_config': Set a config to a given value, and return 'configs'.


[sandbox-driver](#sandbox-driver)

---
## publisher.py

This module publishes to a given url topic. The url topics are given in the topic dictionary:

topic = {
    'frontend' : 'com.opentrons.frontend',
    'driver' : 'com.opentrons.driver',
    'labware' : 'com.opentrons.labware',
    'bootloader' : 'com.opentrons.bootloader'
}

Outgoing Data Format:
```
{
	'type': "string",
	'data':
	{
		'name': "string",
		'message':{message:param}
	}
}
```

* Note, this is the same as the incoming data format because it is possible, and likely, that outgoing 
data here will be incoming data to similar communication code elsewhere, only mildly adjusted, and 
not just to the Frontend.


[sandbox-driver](#sandbox-driver)

---
## driver.py

The driver module communicates directly with the Smoothieboard and serves as a template for 
communication with other devices. As such, there are several pieces that are critical to its 
operation, but they can be adjusted for use with other devices.

The first set of criticial pieces are the dictionaries used for various purposes. They are 
outlined here:

state_dict:
* 'name' - a device should have a name so it can be referenced
* 'simulation' - is the device is running in simulation mode?
* 'connected' - is the device connected?
* 'transport' - is the transport there? (asyncio)
* 'locked' - is the driver locked from sending data to device? (flow control)
* 'ack_received' - is there acknowledgement data received from device
* 'ack_ready' - is there acknowledgement device is ready to receive data
* 'queue_size' - size of the command queue


config_dict:
* 'delimiter' - delimiter to use when parsing incoming data into individual messages (default is "\n")
* 'message_ender' - suffix to put on all data going to device (terminator string)
* 'ack_received_message' - message used to acknowledge data received from device (Smoothieboard uses "ok")
* 'ack_received_parameter' - parameter used to acknowledge data received from device (Smoothieboard does not use this)
* 'ack_received_value' - parameter or message value used to acknowledge data received from device (Smoothieboard does not use this)
* 'ack_ready_message' - message used to acknowledge device ready to receive data (Smoothieboard uses 'stat' for this)
* 'ack_ready_parameter' - parameter used to acknowledge device ready to receive data (Smoothieboard does not use this)
* 'ack_ready_value' - parameter or message value used to acknowledge device ready to receive data (Smoothieboard uses 0 for this)


callbacks_dict:

The callbacks_dict is where custom callbacks are stored to listen for particular messages and then transmit 
data accordingly. This dictionary starts out empty but has the following format:

```
{
	callback name:
	{
		'callback': callback oeject,
		'messages': [ list of messags ]
	},
	...
}
```

All data then transmitted to a given callback is of the form:

{ message: { param:value, ... } }

It is important to note that a large amount of useful data comes back without a "message". By default, such 
data gets attached to the message 'None', so almost all devices should have a callback for 'None' messages. 
For the Smoothieboard, that callback is called none.


meta_callbacks_dict:

The meta_callbacks_dict is important for triggering callbacks based on the driver itself, not data coming 
from the device. The meta-callback-names, previously listed as well, are:
		'on_raw_data'
		'on_connect'
		'on_empty_queue'
		'on_disconnect'

The names correspond with the event that triggers them. It is important to note that 'on_empty_queue' is 
useful for other sections of code to know that a particular set of commands has completed running, for 
instance, when running a protocol.


commands_dict:

This dictionary has all of the commands that can be sent to the device and varies by device. 
The dictionary of commands for the Smoothieboard is too long to include here, but this is the format:

```
{
	command:
	{
		'code': string code,
		'parameters': [ list of acceptable parameter strings ]
	},
	...
}
```




Another critical piece of driver.py is the command_queue, a list used to buffer commands to 
be sent to the device. It is also therefore important to be able to clear the command_queue
with the clear_queue function.

* The Smoothieboard does not use checksums to verify messages, however other boards, like TinyG do. A mechanism for 
handling that could be added




[sandbox-driver](#sandbox-driver)

---
TODO: 
* The commands dictionary for Smoothieboard is not complete yet. Will be soon.
* Some examples of commands and their responses.











