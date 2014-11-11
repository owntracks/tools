include config.mk

ALLPLUGINS =  check_gw.py check_mqtt.py
ALLOBJECTS = gw-commands.cfg mqtt-commands.cfg gw-generic.cfg
ALLCONFIGS = gw-hosts.cfg mqtt-hosts.cfg gw-services.cfg mqtt-services.cfg

all : $(ALLPLUGINS) $(ALLOBJECTS) $(ALLCONFIGS)


%.cfg: %.src  config.mk Makefile *.src
	sed -e s#%PLUGINS#$(PLUGINS)# \
		-e s#%USER#$(USER)# \
		-e s#%PORTNO#$(PORTNO)# \
		-e s#%BROKER#$(BROKER)# \
		-e s#%PASSWORD#$(PASSWORD)# \
		$< > $@

clean :
	rm -v -f $(ALLOBJECTS)

install : all install-plugins install-objects

install-objects : $(ALLOBJECTS) $(ALLCONFIGS)
	$(INSTALL) -v -m 644 $? ${OBJECTS}

install-plugins : $(ALLPLUGINS)
	$(INSTALL) -v -m 755 $? ${PLUGINS}

uninstall : uninstall-plugins uninstall-objects

uninstall-objects:
	(cd ${OBJECTS}; rm -v -f $(ALLOBJECTS) $(ALLCONFIGS)) 

uninstall-plugins:
	(cd ${PLUGINS}; rm -v -f $(ALLPLUGINS)) 
