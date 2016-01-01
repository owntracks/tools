import json
import paho.mqtt.client as mqtt
import csv
import time
from os import getenv
from time import sleep
from google.transit import gtfs_realtime_pb2
import urllib

username = getenv('USER')
password = getenv('PASS')
apikey = getenv('APIKEY')
match = getenv('MATCH')

disconnected = False
connected = False
sent = 0
tst = int(time.time())
stops = {}
trips = {}

def on_connect(client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        global connected
        connected = True

def on_publish(client, userdata, mid):
        #print("published(%d)" % mid)
        global sent
        sent = sent + 1

def on_disconnect(client, userdata, rc):
        print("disconnected %d" % rc)
        global disconnected
        disconnected = True

client = mqtt.Client()
client.on_connect = on_connect
client.on_publish = on_publish
client.on_disconnect = on_disconnect
if username != None:
	client.username_pw_set(username, password=password)
client.connect("localhost", 1883, 60)
client.loop_start()

while connected == False:
	print 'connecting'
	sleep(1)

agency_id = 'agency_id'

#ignoring shapes.txt
#ignoring calendar.txt
#ignoring calendar_dates.txt
#ignoring transfers.txt
#ignoring stop_times.txt

input = open('agency.txt', 'rb')
reader = csv.reader(input)
for line in reader:
	(agency_id,agency_name,agency_url,agency_timezone,agency_lang,agency_phone)=line
	payloaddict = dict(_type='agency',agency_id = agency_id, agency_name = agency_name, agency_url = agency_url, agency_timezone = agency_timezone, agency_lang = agency_lang ,agency_phone = agency_phone)
	#client.publish('gtfs/%s' % (agency_id), payload=json.dumps(payloaddict), qos=0, retain=True)
	#print 'pub: ' + 'gtfs/%s' % (agency_id)
input.close()

input = open('stops.txt', 'rb')
reader = csv.reader(input)
for line in reader:
	#print line
	(stop_id,stop_code,stop_name,stop_desc,stop_lat,stop_lon,zone_id,stop_url,location_type,parent_station)=line

	#print "%s %s %s" % (stop_id, stop_lat, stop_lon)
	payloaddict = dict(_type='stop',stop_id = stop_id, stop_code = stop_code, stop_name = stop_name, stop_desc = stop_desc, stop_lat = stop_lat ,stop_lon = stop_lon,zone_id = zone_id,stop_url = stop_url,location_type = location_type ,parent_station = parent_station)
	stops[stop_id] = payloaddict
	#client.publish('gtfs/%s/stops/%s' % (agency_id, stop_id), payload=json.dumps(payloaddict), qos=0, retain=True)
	#print 'pub: ' + 'gtfs/%s/stops/%s' % (agency_id, stop_id)

	if parent_station == '':
		payloaddict = dict(_type='location', tid = stop_id, lat = stop_lat, lon = stop_lon,parent_station = parent_station, tst = tst)
		#client.publish('owntracks/%s/%s' % (agency_id, stop_id), payload=json.dumps(payloaddict), qos=0, retain=True)
		#print 'pub: ' + 'owntracks/%s/%s' % (agency_id, stop_id)
		payloaddict = dict(_type='card', name = stop_name)
		#client.publish('owntracks/%s/%s/info' % (agency_id, stop_id), payload=json.dumps(payloaddict), qos=0, retain=True)
		#print 'pub: ' + 'owntracks/%s/%s/info' % (agency_id, stop_id)
input.close()

input = open('trips.txt', 'rb')
reader = csv.reader(input)
for line in reader:
	(route_id,service_id,trip_id,trip_headsign,direction_id,block_id,shape_id)=line
	payloaddict = dict(_type='trip',route_id = route_id, service_id = service_id, trip_id = trip_id, trip_headsign = trip_headsign, direction_id = direction_id ,block_id = block_id,shape_id = shape_id)
	trips[trip_id[13:]] = payloaddict
	#client.publish('gtfs/%s/routes/%s/%s' % (agency_id, route_id, trip_id), payload=json.dumps(payloaddict), qos=0, retain=True)
	#print 'pub: ' + 'gtfs/%s/routes/%s/%s' % (agency_id, route_id, trip_id)
	#client.publish('ontracks/%s/%s' % (agency_id, trip_id[13:]), payload=None, qos=0, retain=True)
	#print 'pub: ' + 'owntracks/%s/%s' % (agency_id, trip_id)
input.close()

input = open('routes.txt', 'rb')
reader = csv.reader(input)
for line in reader:
	(route_id,agency_id,route_short_name,route_long_name,route_desc,route_type,route_url,route_color,route_text_color)=line
	payloaddict = dict(_type='route',route_id = route_id, agency_id = agency_id, route_short_name = route_short_name, route_long_name = route_long_name, route_desc = route_desc ,route_type = route_type,route_url = route_url, route_color = route_color, route_text_color = route_text_color)
	#client.publish('gtfs/%s/routes/%s' % (agency_id, route_id), payload=json.dumps(payloaddict), qos=0, retain=True)
	#print 'pub: ' + 'gtfs/%s/routes/%s' % (agency_id, route_id)
input.close()

while True:

	feed = gtfs_realtime_pb2.FeedMessage()
	response = urllib.urlopen('http://datamine.mta.info/mta_esi.php?key=%s&feed_id=1' % apikey)
	print 'parsing'
	feed.ParseFromString(response.read())
	for entity in feed.entity:
		print entity
		if entity.HasField('trip_update'):
			trip_update = entity.trip_update
			#print trip_update
			if trip_update.HasField('trip'):
				trip = trip_update.trip
				#print trip
				trip_id = trip.trip_id
				route_id = trip.route_id
				if route_id == match:
					#print trip_id
					for StopTimeUpdate in trip_update.stop_time_update:
						#print StopTimeUpdate
						stop_id = StopTimeUpdate.stop_id
						if StopTimeUpdate.HasField('arrival'):
							arrival = StopTimeUpdate.arrival
							#print arrival
							if arrival.HasField('time'):
								#print time
								time = arrival.time
								stop = stops[stop_id]
								stop_lat = stop['stop_lat']							
								stop_lon = stop['stop_lon']							
								#print stop_lat, stop_lon
								trip = trips.get(trip_id)
								if trip != None:
									direction_id = trip['direction_id']
									trip_headsign = trip['trip_headsign']							
									payloaddict = dict(_type='card', name = trip_headsign)
									client.publish('owntracks/%s/%s/info' % (agency_id, trip_id), payload=json.dumps(payloaddict), qos=0, retain=True)
									print 'pub: ' + 'owntracks/%s/%s/info' % (agency_id, trip_id)
								else:
									direction_id = 0
								if direction_id == 0:
									cog = 0
								else:
									cog = 180
								payloaddict = dict(_type='location', tid = route_id, lat = stop_lat, lon = stop_lon, tst = time, cog = cog)
								client.publish('owntracks/%s/%s' % (agency_id, trip_id), payload=json.dumps(payloaddict), qos=0, retain=True)
								print 'pub: ' + 'owntracks/%s/%s' % (agency_id, trip_id)
								break


	for n in range(1, 6):
		print 'sleeping'
		sleep(10)

client.disconnect()
while disconnected == False:
	print "disconnecting"
	sleep(1)



