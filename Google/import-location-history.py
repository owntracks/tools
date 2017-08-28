#!/usr/bin/env python3

import argparse
import json
from paho.mqtt import client, publish

class ProtocolAction(argparse.Action):
	def __call__(self, parser, namespace, value, option_string=None):
		setattr(namespace, self.dest, getattr(client, value))

parser = argparse.ArgumentParser(description='Import Google Location History into OwnTracks')
parser.add_argument('-H', '--host', default='localhost', help='MQTT host (localhost)')
parser.add_argument('-p', '--port', type=int, default=1883, help='MQTT port (1883)')
parser.add_argument('--protocol', action=ProtocolAction, default=client.MQTTv31, help='MQTT protocol (MQTTv31)')
parser.add_argument('--cacerts', help='Path to files containing trusted CA certificates')
parser.add_argument('--cert', help='Path to file containing TLS client certificate')
parser.add_argument('--key', help='Path to file containing TLS client private key')
parser.add_argument('--tls-version', help='TLS protocol version')
parser.add_argument('--ciphers', help='List of TLS ciphers')
parser.add_argument('-u', '--username', help='MQTT username')
parser.add_argument('-P', '--password', help='MQTT password')
parser.add_argument('-i', '--clientid', help='MQTT client-ID')
parser.add_argument('-t', '--topic', required=True, help='MQTT topic')
parser.add_argument('filename', help='Path to file containing JSON-formatted data from Google Location History exported by Google Takeout')
args = parser.parse_args()

messages = []
with open(args.filename) as lh:
	lh_data = json.load(lh)
	for location in lh_data['locations']:
		location_keys = location.keys()
		payload = {
			'_type': 'location',
			'tid': 'Go'
		}
		if 'timestampMs' in location_keys:
			payload['tst'] = int(location['timestampMs']) // 1000
		if 'latitudeE7' in location_keys:
			payload['lat'] = location['latitudeE7'] / 10000000
		if 'longitudeE7' in location_keys:
			payload['lon'] = location['longitudeE7'] / 10000000
		if 'accuracy' in location_keys:
			payload['acc'] = location['accuracy']
		if 'altitude' in location_keys:
			payload['alt'] = location['altitude']
		messages.append(
			{
				'topic': args.topic,
				'payload': json.dumps(payload),
				'qos': 2
			}
		)
	del lh_data

if args.username != None:
	auth={
		'username': args.username,
		'password': args.password
	}
else:
	auth = None

if args.cacerts != None:
	tls = {
		'ca_certs': args.cacerts,
		'certfile': args.cert,
		'keyfile': args.key,
		'tls_version': args.tls_version,
		'ciphers': args.ciphers
	}
else:
	tls = None

publish.multiple(
	messages,
	hostname=args.host,
	port=args.port,
	client_id=args.clientid,
	auth=auth,
	tls=tls
)
