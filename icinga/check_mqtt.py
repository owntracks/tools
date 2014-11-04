#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import ssl
import getopt

import paho.mqtt.client as paho   # pip install paho-mqtt
import json

def usage():
    print "check-mqtt -h hostname/address -u userId -p port -w password -c cafile"

def on_disconnect(mosq, userdata, rc):
    global returnValue
    print "MQTT disconnect %d" % rc
    if returnValue == -1:
	returnValue = 2

def on_connect(mosq, userdata, rc):
    global returnValue
    print "MQTT connect %d" % rc
    if rc == 0:
	returnValue = 0
    else:
    	returnValue = 2

def main(argv):
    global returnValue
    clientID = "check-mqtt-%d" % os.getpid()
    host = 'localhost'
    userId = None
    password = None
    port = 1883
    cafile = None

    try:
       	opts, args = getopt.getopt(argv, "h:p:u:w:c:", ["host", "port", "userId", "password", "cafile"])
    except getopt.GetoptError as e:
        usage();
        print "MQTT getopt 3"
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
        if opt in ('-c', '--cafile'):
            cafile = arg

    mqttc = paho.Client(clientID, clean_session=True, userdata=None)
    mqttc.on_connect = on_connect
    mqttc.on_disconnect = on_disconnect
    if userId != None:
    	mqttc.username_pw_set(userId,password)
    if cafile != None:
    	mqttc.tls_set(cafile)
    	mqttc.tls_insecure_set(True)
    try:
    	mqttc.connect(host, port, 60)
    except:
	print "MQTT connect exception 2";
	returnValue = 2

    while returnValue == -1:
        mqttc.loop()

    mqttc.disconnect()
    exit(returnValue);

returnValue = -1

if __name__ == '__main__':
    main(sys.argv[1:])
