#!/usr/bin/env python

import websocket
import subprocess
import simplejson
import time

#PATH is bat-agent location
PATH = '/home/stephen/bat/kilo/bat-agent'
CONFIGURE_PATH = '%s/bat_agent/config/rpc_example.json'%PATH
SCRIPT_PATH = '%s/bat_agent/rpcclient/client.py'%PATH

class WakeupInstance(object):
    """docstring for WakeupInstance"""
    def __init__(self, arg=None):
        super(WakeupInstance, self).__init__()
        self.arg = arg

    def run(self):
        try:
            hostname = '127.0.0.1'
            url = "ws://" + hostname + ":3008/events"
            self._monitor_hypervisor(url)
        except Exception, e:
            print 'ERROR :%s'% e
        
    def _monitor_hypervisor(self, url):
        self.ws = websocket.WebSocketApp(url, 
                                        on_message=self.on_message,
                                        on_error=self.on_error,
                                        on_close=self.on_close)
        self.ws.on_open = self.on_open
        self.ws.run_forever()

    def on_open(self, ws):
        print '[1] on_open'
        self.ws.send("hi")

    def on_message(self, ws, message):
        print '[2] on_message:%s' % message
        message = simplejson.loads(message)
        instance_id = message.get('instance_id')
        if instance_id:
            self.wakup_instance(instance_id)

    def on_error(self, ws, error):
        print '[3] on_error:%s' % error

    def on_close(self, ws):
        print '[4] on_close' 

    def wakup_instance(self, instance_id):
        print '[INFO-2]wakup_instance id:%s , at time:%s' % (instance_id, time.ctime())
        try:
            instance_config = simplejson.loads(open(CONFIGURE_PATH).read())
            if instance_config is None and instance_config['instance_to_monitor'] is None:
                print '[ERROR-2]start instance:%s monitor failed : config is None'%instance_id
            elif instance_config['instance_to_monitor']['id'] == instance_id:
                config_result = subprocess.call(["python", SCRIPT_PATH, "configure"])
                if config_result == 0:
                    subprocess.call(["python", SCRIPT_PATH, "monitor"])
                    print '[INFO-3]start instance(%s) monitor success.'%instance_id
                else:
                    print '[ERROR-3]start instance:%s monitor failed : configure failed!'%instance_id
            else:
                print '[ERROR-4]start instance:%s monitor failed : config does not match!'%instance_id                
        except Exception, e:
            print '[ERROR-5]start monitor failed:%s'%e


def main():
    handel = WakeupInstance()
    handel.run()

if __name__ == '__main__':
    main()