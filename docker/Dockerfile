FROM ubuntu:latest
LABEL version="0.1" description="Mosquitto and OwnTracks Recorder"
MAINTAINER Jan-Piet Mens <jpmens@gmail.com>

RUN apt-get install software-properties-common -y
RUN apt-add-repository ppa:mosquitto-dev/mosquitto-ppa
RUN apt-get update
# RUN apt-get upgrade
RUN apt-get install openssh-server supervisor wget git-core -y
RUN apt-get install build-essential libmosquitto-dev libcurl3 libcurl4-openssl-dev liblua5.2-dev mosquitto mosquitto-clients -y

RUN groupadd --system owntracks
RUN adduser --system --disabled-password --disabled-login owntracks

# data volume
RUN mkdir -p -m 775 /owntracks
RUN chown owntracks:owntracks /owntracks
VOLUME /owntracks

# Recorder
RUN mkdir -p /usr/local/src
WORKDIR /usr/local/src
RUN git clone https://github.com/owntracks/recorder.git
WORKDIR /usr/local/src/recorder
COPY config.mk /usr/local/src/recorder/config.mk
RUN make
RUN make install
RUN chown owntracks /usr/local/bin/ocat /usr/local/sbin/ot-recorder
RUN chgrp owntracks /usr/local/bin/ocat /usr/local/sbin/ot-recorder
RUN chmod 7111 /usr/local/bin/ocat /usr/local/sbin/ot-recorder

RUN adduser --system --home / --shell /bin/bash --gecos 'JP Mens' jpmens
RUN usermod --groups owntracks jpmens
RUN echo "jpmens:doc" | chpasswd

RUN mkdir -p /var/run/sshd /var/log/supervisor

COPY launcher.sh /usr/local/sbin/launcher.sh
COPY generate-CA.sh /usr/local/sbin/generate-CA.sh
RUN chmod 755 /usr/local/sbin/launcher.sh /usr/local/sbin/generate-CA.sh
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY mosquitto.conf /etc/mosquitto/mosquitto.conf

EXPOSE 22 1883 8883 8083
CMD ["/usr/local/sbin/launcher.sh"]
