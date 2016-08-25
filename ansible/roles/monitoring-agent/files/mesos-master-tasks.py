#!/usr/bin/python

import collectd
import json
import requests

MESOS_MASTER_HOST = 'localhost'
MESOS_MASTER_PORT = 5050
VERBOSE_LOGGING = False
MESOS_MASTER_URL = ''

def get_task_counts(master_url):
    """Return counts of all the tasks in various states"""
    url = '{}/metrics/snapshot'.format(master_url)
    resp = requests.get('{}'.format(url))
    resp_data = resp.json()
    counts = {}
    for t in ['error', 'failed', 'finished', 'killed', 'lost', 'running', 'staging', 'starting']:
        counts.update({ t: resp_data['master/tasks_{}'.format(t)] })
    return counts

def get_tasks(master_url):
    """Return the a map of tasks to allocation data"""
    tasks = {}
    limit = int(sum(get_task_counts(master_url).values()))
    url = '{}/tasks?limit={}'.format(master_url, limit)
    resp = requests.get('{}'.format(url))
    resp_data = resp.json()
    for task in resp_data['tasks']:
        if task['state'] == 'TASK_RUNNING':
            tasks[task['id']] = { 'cpus': task['resources']['cpus'], 'mem': task['resources']['mem'], 'disk': task['resources']['disk'] }
    return tasks

def configure_callback(conf):
    """Received configuration information"""
    global MESOS_MASTER_HOST, MESOS_MASTER_PORT, MESOS_MASTER_URL, VERBOSE_LOGGING
    for node in conf.children:
        if node.key == 'Host':
            MESOS_MASTER_HOST = node.values[0]
        elif node.key == 'Port':
            MESOS_MASTER_PORT = int(node.values[0])
        elif node.key == 'Verbose':
            VERBOSE_LOGGING = bool(node.values[0])
        else:
            collectd.warning('mesos master task plugin: Unknown config key: %s.' % node.key)
    MESOS_MASTER_URL = "http://" + MESOS_MASTER_HOST + ":" + str(MESOS_MASTER_PORT)
    log_verbose('Configured with host=%s, port=%s, url=%s' % (MESOS_MASTER_HOST, MESOS_MASTER_PORT, MESOS_MASTER_URL))

def read_callback():
    """Read callback called"""
    log_verbose('Read callback called')
    tasks = get_tasks(MESOS_MASTER_URL)
    for taskid, allocations in tasks.items():
        dispatch_stat(taskid, 'percent', 'cpu_allocation', allocations['cpus'] * 100)
        dispatch_stat(taskid, 'memory', 'mem_allocation', allocations['mem'])
        dispatch_stat(taskid, 'bytes', 'disk_allocation', allocations['disk'])

def dispatch_stat(plugin_instance, type, type_instance, value):
    """Read a key from info response data and dispatch a value"""
    if value is None:
        collectd.warning('mesos-master-tasks plugin: Value not found for %s/%s' % (plugin_instance, type_instance))
        return
    log_verbose('Sending value[%s]: %s=%s' % (plugin_instance, type_instance, value))

    val = collectd.Values(plugin='mesos-master-tasks')
    val.plugin_instance = plugin_instance
    val.type = type
    val.type_instance = type_instance
    val.values = [value]
    # https://github.com/collectd/collectd/issues/716
    val.meta = {'0': True}
    val.dispatch()


def log_verbose(msg):
    if not VERBOSE_LOGGING:
        return
    collectd.info('mesos-master-tasks plugin [verbose]: %s' % msg)

collectd.register_config(configure_callback)
collectd.register_read(read_callback)
