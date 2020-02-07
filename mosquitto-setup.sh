#!/usr/bin/env bash
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
# 
# Modifications: Louis T. Getterman IV (@LTGIV) / GotGetLLC.com / opensour.cc

echo "This program ($0) is deprecated; if you get it working, please submit patches."
exit 2

# Replace set -e and exit with non-zero status if we experience a failure
trap 'exit' ERR

# Array of paths to try and use
PATHS=( "/etc/mosquitto/conf.d/" "/etc/mosquitto/" )

# Default location - overwritten with preceding path if one of them exists
MOSQHOME=/tmp/mosquitto

# Mosquitto configuration filename
MOSQCONF=mosquitto.conf

# Time stamp format for backing up configuration files
tstamp=$(date +%Y%m%d-%H%M%S)

# Environment variable that can control who owns the files (passed to generate-CA.sh)
MOSQUITTOUSER=${MOSQUITTOUSER:=$USER}

# Iterate through array of paths to traverse for default location to use
for i in "${PATHS[@]}"
do
	if [ -d $i ]; then
		export MOSQHOME=$i
		break
	fi
done

# Fall back to default /tmp/mosquitto and create this location if it doesn't exist
[ -d $MOSQHOME ] || mkdir $MOSQHOME

# User that owns mosquitto directory that we're targeting
MOSQUSER=`ls -ld $MOSQHOME | awk '{print $3}'`

# Check ownership of the path and let us know if there's a permissions problem
if [ $USER != $MOSQUSER ]; then
	echo "FYI: File ownership for generated files in '${MOSQHOME}' is set to '${MOSQUITTOUSER}',"
	echo "but you are running as '${USER}' and '${MOSQHOME}' can only be modified by '${MOSQUSER}'."
	
	if [ $MOSQUSER == 'root' ]; then
		echo;
		echo "The most easy way to fix this error is re-running as 'sudo ${0}'"
	fi
	
	echo;
	read -p "Press [Enter] key to continue, or [Ctrl]-C to cancel."
fi

# Export environment variable to be used in subsequent (generate-CA.sh)
export MOSQUITTOUSER

# Concat of path and configuration file
MOSQPATH=$MOSQHOME/$MOSQCONF

# If file exists, move it to a timestamp-based name
if [ -f $MOSQPATH ]; then
	echo -n "Saving previous configuration: "
	mv -v $MOSQPATH $MOSQHOME/$MOSQCONF-$tstamp
fi

# Export TARGET variable for use in generate-CA.sh
export TARGET=$MOSQHOME
eval "`dirname \"$0\"`/TLS/generate-CA.sh"

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
echo "Please adjust certfile and keyfile path names in $MOSQPATH"
