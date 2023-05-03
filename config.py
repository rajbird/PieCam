#############################################
##  Settings and Configuration options for ##
##        PiCamera Security Camera         ##
##Only fiddle if you know what you're doing##
#############################################


#Camera Picture Settings
########################

#Resolution of frame
RESOLUTION_X = 480
RESOLUTION_Y = 360

#Framerate of video (FPS)
VIDEO_FRAMERATE = 10

#Motion Detection Settings
########################
#Default 25  --  Lower more sensitive
THRESHOLD_VALUE = 25

#Server Settings
########################

#Ephemeral port# for camera server (1024 to 65535)
PORT_NUM = 8000