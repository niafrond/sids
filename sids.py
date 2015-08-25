#!/usr/bin/python
import sys
print "Python %s" %(sys.version)
import io
from PIL import Image
import urllib2
import  base64
import time
import subprocess	
import datetime
import os.path
import logging
import ConfigParser
import string
print "Libraries loaded"
config = ConfigParser.RawConfigParser()
config.read('/media/sids/sids.cfg')
testHeight = config.getint('analysis','testHeight')
testWidth = config.getint('analysis','testWidth')

logging.basicConfig(filename= config.get('dev','log'),level=logging.DEBUG)


# this is the default setting, if the whole image should be scanned for changed pixel
testAreaCount = 1
testBorders = [ [[1,testWidth],[1,testHeight]] ]

def log(message):
    logging.info("%s ## %s" % (datetime.datetime.now(),message))
    print "%s ## %s" % (datetime.datetime.now(),message)


#En prevision on efface le flag, car on est sur une relance
#subprocess.call("rm /media/sids/monitor.disable", shell=True)
def getImage():
    username = config.get('image','username')
    password = config.get('image','password')
    request = urllib2.Request(config.get('image','url'))
    base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)   
    fd = urllib2.urlopen(request)
    image_file = io.BytesIO(fd.read())
    return Image.open(image_file)
    

def no_flag():
    
    flagName=config.get('flag','path')
    return os.path.isfile(flagName)
    
def detect_motion():
    global prior_image
    global duree
    
    threshold = config.getfloat('analysis','threshold')
    sensitivity= config.getfloat('analysis','sensitivity')
   
    #log("Capture %s" % datetime.datetime.now())
    
    
    if prior_image is None:
        prior_image = getImage()
        return False
    else:
        current_image = getImage()
        buffer1 = prior_image.load()
        buffer2 = current_image.load()
        changedPixels = 0
        takePicture = False 
		# Compare current_image to prior_image to detect motion. This is
        # left as an exercise for the reader!
        for z in xrange(0, testAreaCount): # = xrange(0,1) with default-values = z will only have the value of 0 = only one scan-area = whole picture
            for x in xrange(testBorders[z][0][0]-1, testBorders[z][0][1]): # = xrange(0,100) with default-values
                for y in xrange(testBorders[z][1][0]-1, testBorders[z][1][1]):   # = xrange(0,75) with default-values; testBorders are NOT zero-based, buffer1[x,y] are zero-based (0,0 is top left of image, testWidth-1,testHeight-1 is botton right)
                    #print "X %s Y%s Z%s" %( x, y,z)
                    # Just check green channel as it's the highest quality channel
                    pixdiff = abs(buffer1[x,y][1] - buffer2[x,y][1])
                    if pixdiff > threshold:
                        changedPixels += 1
					# Save an image if pixels changed
                    if (changedPixels > sensitivity):
                        takePicture = True # will shoot the photo later
                        
                        
                    if ((changedPixels > sensitivity)):
                        break  # break the y loop
                if ((changedPixels > sensitivity)):
                    break  # break the x loop
            if ((changedPixels > sensitivity)):
                break  # break the z loop
        if takePicture:          
            log("Motion detected !!!!!!")

        else:
            log("No Motion detected")
        # Once motion detection is done, make the prior image the current
        prior_image = current_image
        return takePicture

prior_image = getImage()
potentialSIDS = False
try:
    log("##################Debut de surveillance#########################")
    
    lastMovementTime = time.time()
    alertVolume = config.getint('alert','defaultVolume')
    while True:
        #Update the values
        config.read('/media/sids/sids.cfg')

        
        if not no_flag():
            
            if detect_motion():
                lastMovementTime = time.time()
                if potentialSIDS:
                    subprocess.call("%s" % config.get('alert','cmdBackNormal'), shell=True)
                    
                    potentialSIDS = False
                    alertVolume = config.getint('alert','defaultVolume')
                    
            heure = time.time()
            if ((heure - lastMovementTime) <= config.getint('alert','abandonTime')):
                if ((heure - lastMovementTime) >= config.getint('alert','criticalThreshold')):
                    alertVolume += config.getint('alert','volumeIncrement')
                    cmdVolume = config.get('alert','cmdVolumeChange')
                    cmdVolume = cmdVolume.replace('VOLUME',str(alertVolume))
                    subprocess.call("%s" % (cmdVolume), shell=True)  
                    potentialSIDS = True
                    
                    log("ALERTE pas de changement depuis %s" % (heure - lastMovementTime))
                   
                    subprocess.call(" %s " % config.get('alert','cmdAlert'), shell=True)
                    
            else:
                log("Abandon")
        else:
            log("%s" % config.get('flag','msgFlag'))
            time.sleep(5)
            lastMovementTime = time.time()
            potentialSIDS = False
            alertVolume = config.getint('alert','defaultVolume')
except KeyboardInterrupt:
    pass
    
