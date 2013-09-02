#!/bin/sh
#(@)mosquitto-setup.sh - Create a basic Mosquitto configuration w/ TLS

# Copyright (c) 2013 Jan-Piet Mens <jpmens()gmail.com>
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of mosquitto nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

set -e

MOSQHOME=/tmp/mosquitto		# FIXME: find automagically
MOSQCONF=mosquitto.conf
MOSQPATH=$MOSQHOME/$MOSQCONF
tstamp=$(date +%Y%m%d-%H%M%S)

[ -d $MOSQHOME ] || mkdir $MOSQHOME

if [ -f $MOSQPATH ]; then
	echo "Saving previous configuration as mosquitto.conf-$tstamp"
	mv $MOSQPATH $MOSQHOME/mosquitto.conf-$tstamp
fi

TARGET=$MOSQHOME TLS/generate-CA.sh

sed -Ee 's/^[ 	]+%%% //' <<!ENDMOSQUITTOCONF > $MOSQPATH
	%%% # allow_anonymous false
	%%% autosave_interval 1800
	%%% 
	%%% connection_messages true
	%%% log_dest stderr
	%%% log_dest topic
	%%% log_type error
	%%% log_type warning
	%%% log_type notice
	%%% log_type information
	%%% log_type all
	%%% log_type debug
	%%% log_timestamp true
	%%% 
	%%% #message_size_limit 10240
	%%% 
	%%% #password_file jp.pw
	%%% #acl_file jp.acl
	%%% 
	%%% persistence true
	%%% persistence_location /tmp/
	%%% persistence_file mosquitto.db
	%%% persistent_client_expiration 1m
	%%% 
	%%% #pid_file xxxx
	%%% 
	%%% retained_persistence true
	%%% 
	%%% #listener 1883
	%%% listener 1883 127.0.0.1
	%%% 
	%%% listener 8883
	%%% tls_version tlsv1
	%%% cafile $MOSQHOME/ca.crt
	%%% certfile $MOSQHOME/server.crt
	%%% keyfile $MOSQHOME/server.key
	%%% require_certificate false
!ENDMOSQUITTOCONF

chmod 640 $MOSQPATH
