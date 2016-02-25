## 1. Ceilometer notification plugin
------------------------------------

Precondition:
1. Install Openstack component Ceilometer.

2. Edit the variable PATH in the attachment file and copy the file to /path/to/ceilometer/ceilometer/compute/notifications/.

3. Edit the /path/to/ceilometer/setup.cfg file and add the plugin into the namespace `ceilometer.notification` under [entry_points] as below:
    [entry_points]
    ceilometer.notification =
        instance_wakeup = ceilometer.compute.notifications.instanceWakeup:InstanceWakeup

4. Reinstall the Ceilometer:
    cd /path/to/ceilometer/
    python setup.py install

5. Restart ceilometer-agent-notification service.
6. Must start ceilometer-agent-notification and  ceilometer-collector service




## 2. Polling way to deal with the problem. A demo of using libvirt, another using psutil.
-----------------------------------------------------------------------------------------

1. Start bat-agent rpc and listener server.

2. Run the script 'python libvirt_wakeup.py' or 'python psutil_wakeup.py '

3. Start/stop/suspend/... with openstack UI.





## 3. Nodejs
------------

1. Start bat-agent

2. Run nodejs server use cmd  'node nodejs_wakeup.js'

3. Run python script use cmd   'python nodejs_wakeup.js'