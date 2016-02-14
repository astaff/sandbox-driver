#!/usr/bin/env python3


import json, collections
import sys
import datetime


class Publisher:

    def __init__(self, session=None):
        """
        """
        print(datetime.datetime.now(),' - publisher.__init__:')
        print('\tsession: ',session)
        
        self.topic = {
            'frontend' : 'com.opentrons.frontend',
            'driver' : 'com.opentrons.driver',
            'labware' : 'com.opentrons.labware',
            'bootloader' : 'com.opentrons.bootloader'
        }

        self.clients = {
            # uuid : 'com.opentrons.[uuid]'
        }

        self.id = str(uuid.uuid4())

        self.caller = None

        if session is not None:
            self.caller = session


    def handshake(data):
        print(datetime.datetime.now(),' - publisher.handshake:')
        print('\tdata: ',data)

        if 'id' in data:
            client_id = data['id']
            if client_id in self.clients:
                print('handshake called again on client ',client_data['uuid'],'. We could have done something here to repopulate data')
                self.publish( client_id , client_id ,'handshake','driver','result','already_connected')
            else:
                self.gen_client_id()
        else:
            self.gen_client_id()

        if 'get_ids' in data:
            publish_client_ids()


    def gen_client_id():
        if len(self.clients) > self.max_clients:
            self.publish( 'frontend', '' , 'handshake' , 'driver' , 'result' , 'fail' )
            return ''
        else:
            client_id = str(uuid.uuid4())
            self.clients[client_id] = 'com.opentrons.'+client_id
            self.publish( 'frontend' , client_id , 'handshake' , 'driver' , 'result' , 'success' )
            return client_id


    def client_check(id_):
        if id_ in self.cleints:
            return True
        else
            return False


    def publish_client_ids(id_):
        if id_ in self.clients:
            self.publish( id_ , id_ , 'handshake' , 'driver' , 'ids' , list(self.clients) )
        else:
            self.publish( 'frontend' , '' , 'handshake' , 'driver' , 'ids' , list(self.clients) )
        return list(self.clients)


    def set_caller(self, session):
        """
        """
        print(datetime.datetime.now(),' - publisher.set_caller:')
        print('\tsession: ',session)
        self.caller = session


    def publish(self,topic,to='',type_,name,message,param):
        """
        """
        print(datetime.datetime.now(),' - publisher.publish:')
        print('\ttopic: ',topic)
        print('\tto: ',to)
        print('\ttype_: ',type_)
        print('\tname: ',name)
        print('\tmessage: ',message)
        print('\tparam: ',param)
        if self.caller is not None and topic is not None and type_ is not None:
            if name is None:
                name = 'None'
            if message is None:
                message = ''
            if param is None:
                param = ''
            if self.caller._myAppSession is not None:
                msg = {'type':type_,'to':to,'from':self.id,'data':{'name':name,'message':{message:param}}}
                try:
                    if topic in self.topic:
                        self.caller._myAppSession.publish(self.topic.get(topic),json.dumps(msg))
                    elif topic in self.clients:
                        self.caller._myAppSession.publish(self.clients.get(topic),json.dumps(msg))


                except:
                    print(datetime.datetime.now(),' - publisher.py - publish - error:\n\r',sys.exc_info())
            else:
                print(datetime.datetime.now(),' - publisher.py - publish - error: caller._myAppSession is None')
        else:
            print(datetime.datetime.now(),' - publisher.py - publish - error: calller, topic, or type_ is None')

