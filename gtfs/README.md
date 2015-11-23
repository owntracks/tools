# General Transit Feed Specification (GTFS) 

Via GTFS static and realtime Transit information is available.

### Static
https://developers.google.com/transit/gtfs/?hl=en

with a number of public feeds
https://code.google.com/p/googletransitdatafeed/wiki/PublicFeeds

### Realtime
https://developers.google.com/transit/gtfs-realtime/?hl=en

https://code.google.com/p/googletransitdatafeed/wiki/PublicFeedsNonGTFS

### Sample

To run the sample program
- run pip install --upgrade gtfs-realtime-bindings
- copy gtfs.sh.sample to gtfs.sh and edit 
- you will need an mta apikey and credentials of your mqtt broker

The sample programm will
- read the necessary static reference files,
- publish the content to mqtt (currently commented),
- contact the realtime server
- publish the realtime location information and info for the
	trains on the selected route

The .txt files are static files downloaded from mta
