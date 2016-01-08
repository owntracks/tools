#!/bin/sh
# launcher.sh
# This will be started when the container starts

set -e

echo -- "--- BEGIN OWNTRACKS LAUNCHER ---"


mkdir -p /owntracks/recorder/store
mkdir -p /owntracks/recorder/store/last

chown -R owntracks:owntracks /owntracks/recorder
/usr/local/sbin/ot-recorder --initialize

mkdir -p /owntracks/certs

if [ -d /owntracks/certs ]; then
	cd /owntracks/certs
	export IPLIST="127.0.0.1"
	export HOSTLIST="a.example.com"

	hostname=$(hostname)
	/usr/local/sbin/generate-CA.sh
	ln -sf $hostname.crt mosquitto.crt
	ln -sf $hostname.key mosquitto.key
	chown mosquitto mosquitto.crt
	chown mosquitto mosquitto.key

fi

# --- for Mosquitto's persistence
mkdir -p /owntracks/mosquitto
chown mosquitto:mosquitto /owntracks/mosquitto

exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
