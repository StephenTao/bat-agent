import subprocess
import simplejson

from ceilometer.openstack.common import log
from ceilometer.compute import notifications
from ceilometer import sample


LOG = log.getLogger('[Start Monitor]')

#PATH is bat-agent location
PATH = '/path/to/bat-agent'
CONFIGURE_PATH = '%s/bat_agent/config/rpc_example.json'%PATH
SCRIPT_PATH = '%s/bat_agent/rpcclient/client.py'%PATH

class InstanceWakeup(notifications.ComputeNotificationBase):
 
    #instance will turn to running after below notification event_types 
    event_types = ['compute.instance.power_on.end',
                    'compute.instance.resume.end',
                    'compute.instance.reboot.end',
                    'compute.instance.finish_resize.end',
                    'compute.instance.rebuild.end']

    def process_notification(self, message):
        instance_properties = self.get_instance_properties(message)
        if isinstance(instance_properties.get('metadata'), dict):
            src_metadata = instance_properties['metadata']
            del instance_properties['metadata']
            util.add_reserved_user_metadata(src_metadata, instance_properties)

        self._handle_monitor(message)
        return self.get_sample(message)

    def get_instance_properties(self, message):
        """Retrieve instance properties from notification payload."""
        return message['payload']

    def get_sample(self, message):
        yield sample.Sample.from_notification(
            name='instance',
            type=sample.TYPE_GAUGE,
            unit='instance',
            volume=1,
            user_id=message['payload']['user_id'],
            project_id=message['payload']['tenant_id'],
            resource_id=message['payload']['instance_id'],
            message=message)

    def _handle_monitor(self, message):
        instance_id = message['payload']['instance_id']
        LOG.info('Instance id: %s' % instance_id)
        event_type = message['event_type']
        LOG.info('Instance event_type: %s' % event_type)

        if event_type:
            #wakeup instance monitor
            try:
                instance_config=simplejson.loads(open(CONFIGURE_PATH).read())
                if instance_config is None and instance_config['instance_to_monitor'] is None:
                    LOG.error('[1]start instance:%s monitor failed : config is None'%instance_id)
                elif instance_config['instance_to_monitor']['id'] == instance_id:
                    LOG.info(SCRIPT_PATH)
                    config_result = subprocess.call(["python", SCRIPT_PATH, "configure"])
                    if config_result == 0:
                        subprocess.call(["python", SCRIPT_PATH, "monitor"])
                        LOG.info('start instance(%s) monitor success.'%instance_id)
                    else:
                        LOG.error('[2]start instance:%s monitor failed : configure failed!'%instance_id)
                else:
                    LOG.error('[3]start instance:%s monitor failed : config does not match!'%instance_id)
                    
            except Exception, e:
                LOG.error('start monitor failed:%s'%e)
        else:
            pass