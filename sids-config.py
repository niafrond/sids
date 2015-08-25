#!/usr/bin/python
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read('/media/sids/sids.cfg')


if (len(sys.argv) > 2):
    section=sys.argv[1]
    option=sys.argv[2]
    if len(sys.argv) > 3:
        valeur=sys.argv[3]
        config.set(section, option, valeur)
        with open(r'/media/sids/sids.cfg', 'wb') as configfile:
            config.write(configfile)
    else:
        
        print config.get(section, option)
else:
    for section in config.sections():
        print "######### %s ###########" % section
        for item in config.items(section):
            print "%s : %s" %( item[0],item[1] )
