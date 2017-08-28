# OwnTracks Tools

### mosquitto-setup.sh

Shell script to create a default OwnTracks configuration for the Mosquitto broker

### TLS/

Utility to create TLS CA Certificate and server certificate for OwnTracks

### icinga/

Icinga / Nagios check scripts and sample configurations to monitor MQTT broker and Greenwich devices

### message-feeds/

experimental message feeds for OwnTracks (GeoHash) Messaging

### General Transit Feed Specification (GTFS)

Via GTFS static and realtime Transit information is available.
A demo for NYC public transport.

### Google/import-location-history.py
Reads a JSON export of Google Location History from
[Google Takeout](https://takeout.google.com/settings/takeout) and publishes all of its locations
to MQTT. Useful for importing Google Location History into OwnTracks Recorder
