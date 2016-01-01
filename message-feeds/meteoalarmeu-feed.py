#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Christoph Krey <krey.christoph()gmail.com>'
__copyright__ = 'Copyright 2015-2016 Christoph Krey, OwnTracks'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

import Geohash
import os
import json
import time
import datetime
import paho.mqtt.client as mqtt
import random
import feedparser

mqtt_user = os.getenv("MQTT_USER")
mqtt_pass = os.getenv("MQTT_PASS")

feedurl = 'http://www.meteoalarm.eu/documents/rss/de.rss'

client = mqtt.Client()
if mqtt_user is not None:
	client.username_pw_set(mqtt_user, password=mqtt_pass)
client.connect("localhost", 1883, 60)
client.loop_start()

lastrss = 0 
latestrss = 0 

while True:
	time.sleep(1)
	now = int(time.time())

	if now > lastrss + 60:
		lastrss = now
		d = feedparser.parse(feedurl)
		#print d
		newlatestrss = latestrss
		for feed in d.entries:
			#print feed
			if feed.has_key('published_parsed'):
				feedtime = time.mktime(feed.published_parsed)
				if feedtime > latestrss:
					if feedtime > newlatestrss:
						newlatestrss = feedtime
#
# todo interpret text for "from" and "to" values
#
					payloaddict = dict(_type='msg',tst=int(feedtime),ttl=24*3600,prio=0,icon='fa-rss',desc=feed.summary,title=feed.title,url=feed.link)
#
# todo regions are only given as text (e.g. "Brandenburg und Berlin"). Would need to interpret and calculate geohash
#
					client.publish('msg/meteoalarm.eu/u33', payload=json.dumps(payloaddict), qos=2, retain=True)
					print 'pub:' + json.dumps(payloaddict)
		latestrss = newlatestrss



