#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Christoph Krey <krey.christoph()gmail.com>'
__copyright__ = 'Copyright 2015-2016 Christoph Krey, OwnTracks'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

import Geohash
import forecastio
import os
import json
import time
import datetime
import paho.mqtt.client as mqtt
import random

mqtt_user = os.getenv("MQTT_USER")
mqtt_pass = os.getenv("MQTT_PASS")

forecast_io_api_key = os.getenv("FORECAST_IO_API_KEY")
if forecast_io_api_key is None:
	print "Requires FORECAST_IO_API_KEY in environment"
	sys.exit(2)

client = mqtt.Client()
if mqtt_user is not None:
	client.username_pw_set(mqtt_user, password=mqtt_pass)
client.connect("localhost", 1883, 60)
client.loop_start()

last = 0 

while True:
	time.sleep(1)
	now = int(time.time())

# 1000 API calls per day are free -> every 86 seconds. So 100 seconds sleep
	if now > last + 100: 
		last = now
		lat = random.randint(35,60)
		lon = random.randint(-11,30)
		print 'coords: %d,%d' % (lat,lon)
		try:
			forecast = forecastio.manual('https://api.forecast.io/forecast/%s/%d,%d?exclude=minutely,hourly,daily,flags' % (forecast_io_api_key, lat, lon))
		except:
			forecast = None
			pass
		if forecast != None:
			#print forecast.json

# geohash 3 has a lat/lon error of 0.7, so it should be ok for lat and lon as int
			geohash = Geohash.encode(lat, lon, precision=3)

			if forecast.json.has_key('alerts'):
				alerts = forecast.json['alerts']
				for alert in alerts:
					print alert
					ttl = alert['expires'] - now
					payloaddict = dict(_type='msg',tst=now,ttl=ttl,prio=2,icon='fa-exclamation-triangle',desc=alert['description'],title=alert['title'], url=alert['uri'])
					client.publish('msg/forecast.io/%s' % geohash, payload=json.dumps(payloaddict), qos=2, retain=True)
					print 'pub: ' + 'msg/forecast.io/%s' % geohash
			else:
				if forecast.json.has_key('currently'):
					currently = forecast.json['currently']
					weather = '%s' % (currently['summary'])
					payloaddict = dict(_type='msg',tst=currently['time'],ttl=24*3600,prio=1,icon='fa-exclamation-triangle',title='Local Weather',desc=weather, url='http://forecast.io')
				else:
					payloaddict = dict(_type='msg',tst=now,ttl=24*3600,prio=0,icon='fa-exclamation-triangle',desc='no alerts',title='forecast.io', url='http://forecast.io')
				client.publish('msg/forecast.io/%s' % geohash, payload=json.dumps(payloaddict), qos=2, retain=True)
				print 'pub: ' + 'msg/forecast.io/%s' % geohash


