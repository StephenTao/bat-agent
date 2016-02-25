#!/usr/bin/env python

import libvirt 
import subprocess
import simplejson
import time

#PATH is bat-agent location
PATH = '/home/stephen/bat/kilo/bat-agent'
CONFIGURE_PATH = '%s/bat_agent/config/rpc_example.json'%PATH
SCRIPT_PATH = '%s/bat_agent/rpcclient/client.py'%PATH

class WakeupInstance(object):
	"""docstring for WakeupInstance"""
	def __init__(self, uri='qemu:///system'):
		super(WakeupInstance, self).__init__()
		self.uri = uri
		self.conn = self.get_conn()
		self.active_vm_uuids = set()
		self.last_active_vm_uuids = set()

	def get_conn(self):
		try:
			conn = libvirt.open(self.uri)
			return conn
		except Exception, e:
			print '[ERROR-6] can not connect libvirt:%s'% e
		
	def get_active_vm_uuids(self):
		try:
			active_vm_uuids = set()
			for id in self.conn.listDomainsID():
				dom = self.conn.lookupByID(id)
				active_vm_uuids.add(dom.UUIDString())
			return active_vm_uuids
		except Exception, e:
			print '[ERROR-1] Error at conn quem:%s'%e


	def loop(self):
		if not self.conn:
			exit(1)
		while True:
			self.last_active_vm_uuids = self.active_vm_uuids
			self.active_vm_uuids = self.get_active_vm_uuids()

			shoutdown_instance_uuids = self.last_active_vm_uuids - self.active_vm_uuids
			if shoutdown_instance_uuids:
				print '[INFO-1]shoutdown_instance_uuids:%s , %s' % (shoutdown_instance_uuids, time.ctime())

			wakup_instance_uuids = self.active_vm_uuids - self.last_active_vm_uuids
			for instance_id in wakup_instance_uuids:
				self.wakup_instance(instance_id)
			time.sleep(1)

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
	uri = 'qemu:///system'
	handle = WakeupInstance(uri)
	handle.loop()

if __name__ == '__main__':
	main()
