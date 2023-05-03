import sys
import os
import socket
import json
import psutil

def getDebugInformation():
    ret = {
        'hostname': '',
        'cpu_percent': 0.0,
        'memory_percent': 0.0,
        'disk_percent': 0.0,
        'free_space': 0,
        'temperatures': '',
        'error': ''
    }

    ret['hostname'] = socket.gethostname()
    if ret['hostname'] == '':
        ret['hostname'] = 'Error getting hostname.'
    
    ret['cpu_percent'] = psutil.cpu_percent()
    if ret['cpu_percent'] == 0.0:
        ret['error'] += 'Error getting cpu percent.\n'

    virtual_memory = psutil.virtual_memory()
    ret['memory_percent'] = virtual_memory[2]
    if ret['memory_percent'] == 0.0:
        ret['error'] += 'Error getting memory percent.\n'
    
    disk_usage = psutil.disk_usage('/')
    ret['disk_percent'] = disk_usage[3]
    if ret['disk_percent'] == 0.0:
        ret['error'] += 'Error getting disk space percentage.\n'
    
    ret['free_space'] = disk_usage[2]
    if ret['free_space'] == 0:
        ret['error'] += 'Error getting free disk space.\n'

    if 'pi' in ret['hostname']:
        sensor_temperatures = psutil.sensors_temperatures()
        ret['temperatures'] = json.dumps(sensor_temperatures)
    else:
        ret['temperatures'] = 'Temperature monitoring only supported on Linux.'
    
    
    if ret['error'] == '':
        ret['error'] = 'None.'
    
    return json.dumps(ret)