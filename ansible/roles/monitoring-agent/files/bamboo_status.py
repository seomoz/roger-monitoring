#! /usr/bin/python
# @Authors: Manish Ranjan

import collectd
import json
import urllib2
import socket
import collections

BAMBOO_HOST = "localhost"
BAMBOO_PORT = 8000
BAMBOO_URL = ""
VERBOSE_LOGGING = False

def configure_callback(conf):
    """Received configuration information"""
    global BAMBOO_HOST, BAMBOO_PORT, BAMBOO_URL, VERBOSE_LOGGING

    for node in conf.children:
        if node.key == 'Host':
            BAMBOO_HOST = node.values[0]
        elif node.key == 'Port':
            BAMBOO_PORT = int(node.values[0])
        elif node.key == 'Verbose':
            VERBOSE_LOGGING = bool(node.values[0])
        else:
            collectd.warning('bamboo plugin: Unknown config key: %s.' % node.key)
    BAMBOO_URL = "http://" +  BAMBOO_HOST + ":" +str(BAMBOO_PORT) + "/status"
    # use the below url for testing purpose by replacing directly the bambo server url
    #BAMBOO_URL = "http://localhost:8000/status"
    log_verbose_collectd('bamboo plugin configured with host=%s, port=%s, url=%s' % (BAMBOO_HOST, BAMBOO_PORT, BAMBOO_URL))


def fetch_stats():
    try:
        result = urllib2.urlopen(BAMBOO_URL, timeout=10)
        if result.read() == "OK":
            return dispatch_stat("1")
    except urllib2.URLError, e:
        collectd.error('bamboo plugin: Error connecting to %s - %r' % (BAMBOO_URL, e))
        return dispatch_stat("0")

def dispatch_stat(result):
    """Read a key from info response data and dispatch a value"""
    if result is None:
        collectd.warning('bamboo plugin: Value not found for %s' % name)
        return
    estype = 'counter'
    name = 'status'
    value = result
    log_verbose_collectd('Sending value[%s]: %s=%s' % (estype, name, value))
    val = collectd.Values(plugin='bamboo_status')
    val.type = estype
    val.type_instance = name
    val.values = [value]
    val.dispatch()


def read_callback():
    log_verbose_collectd('Read callback called')
    stats = fetch_stats()


def log_verbose_collectd(msg):
    if not VERBOSE_LOGGING:
        return
    collectd.info('bamboo plugin [verbose]: %s' % msg)

collectd.register_config(configure_callback)
collectd.register_read(read_callback)
