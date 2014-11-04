#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import time
import ssl
import getopt
import datetime
import json

import paho.mqtt.client as paho
import json

topic = None
mode = None
switched = False

def usage():
    print "check-gw -m mode -h hostname/address -p port -t topic [-u userId -w password] [-c cafile] [-s]"

def aged(msg):
    fmt = "%s %-14s %-40s %s"

    topic = str(msg.topic)
    payload = str(msg.payload)

    try:
        data = json.loads(payload)
    except:
	try:
		values = payload.split(',')
		try:
			tstamp = int(values[1], 16)
		except:
			tstamp = 0
		if tstamp  > time.time() - 6 * 1.5 * 3600:
		    return 0
                else:
                    return 1
	except:
        	print fmt % (retained, tstamp, topic, payload)
		return 2

    if type(data) is not dict:
        print fmt % (retained, tstamp, topic, payload)
        return

    time_str = None
    if '_type' in data:
        if data['_type'] == 'location':
            if 'tst' in data:
		try:
                    tstamp = int(data['tst'])
		except:
		    tstamp = 0
		if tstamp  > time.time() - 6 * 1.5 * 3600:
		    return 0
                else:
                    return 1
	    else:
		return 2
        else:
	    return 2
    else:
	return 2

def on_connect(mosq, userdata, rc):
    global returnValue
    if rc != 0:
	    sys.exit(3)
    else:
	if mode == 'status':
	    mosq.subscribe('%s/status' % topic)
	elif mode == 'gpio7':
	    mosq.subscribe('%s/gpio/7' % topic)
	elif mode == 'vbatt':
	    mosq.subscribe('%s/voltage/batt' % topic)
	elif mode == 'vext':
	    mosq.subscribe('%s/voltage/ext' % topic)
	elif mode == 'age':
	    mosq.subscribe('%s' % topic)
	else:
	    usage()
	    returnValue = 3

def on_disconnect(mosq, userdata, rc):
    global returnValue
    print "GW disconnect %d" % rc
    if returnValue == -1:
	returnValue = 2

def on_subscribe(client, userdata, mid, granted_qos):
    pass

def on_message(mosq, userdata, message):
    global returnValue
    print message.payload
    if mode == 'status':
        if message.payload == "0":
	    returnValue = 2
	elif message.payload == "1":
	    returnValue = 0
        else:
	    if switched:
		returnValue = 0
	    else:
    		returnValue = 1
    elif mode == 'gpio7':
        if message.payload == "0":
    	    returnValue = 1
        else:
    	    returnValue = 0
    elif mode == 'vbatt':
	try:
           voltage = float(message.payload)
	except:
	    voltage = 0
        if voltage > 3.6:
    	    returnValue = 0
        else:
    	    returnValue = 1
    elif mode == 'vext':
	try:
            voltage = float(message.payload)
	except:
	    voltage = 0
        if voltage >= 12.0:
    	    returnValue = 0
        else:
	    if switched:
		returnValue = 0
	    else:
    		returnValue = 1
    elif mode == 'age':
	returnValue = aged(message)
    else:
	returnValue = 3

def main(argv):
    global returnValue
    clientID = "check-gw-%d" % os.getpid()
    host = 'localhost'
    userId = None
    password = None
    port = 1883
    cafile = None

    try:
       	opts, args = getopt.getopt(argv, "sm:h:p:u:w:t:c:", ["switched", "mode", "host", "port", "userId", "password", "topic", "cafile"])
    except getopt.GetoptError as e:
        usage()
        print "GW getopt 3"
        sys.exit(3)

    for opt, arg in opts:
        if opt in ('-h', '--host'):
            host = arg
        if opt in ('-p', '--port'):
            port = arg
        if opt in ('-u', '--userId'):
            userId = arg
        if opt in ('-w', '--password'):
            password = arg
        if opt in ('-t', '--topic'):
            global topic
	    topic = arg
        if opt in ('-c', '--cafile'):
            cafile = arg
        if opt in ('-m', '--mode'):
	    global mode
            mode = arg
        if opt in ('-s', '--switched'):
	    global switched
            switched = True

    mosq = paho.Client(clientID, clean_session=True, userdata=None)
    mosq.on_connect = on_connect
    mosq.on_disconnect = on_disconnect
    mosq.on_subscribe = on_subscribe
    mosq.on_message = on_message
    if userId != None:
    	mosq.username_pw_set(userId,password)
    if cafile != None:
	mosq.tls_set(cafile)
        mosq.tls_insecure_set(True)

    try:
    	mosq.connect(host, port, 60)
    except:
	print "GW connect exception 2"
	sys.exit(2)

    timeout = time.time() + 3
    while returnValue == -1:
	if time.time() > timeout:
            print "GW timeout"
	    returnValue = 2
        mosq.loop()

    mosq.disconnect()
    exit(returnValue)

returnValue = -1

if __name__ == '__main__':
    main(sys.argv[1:])

