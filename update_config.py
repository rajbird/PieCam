##############################################
##  Interface file for updating config file ##
##      from PiCamera Web Application       ##
##  Altering this file is not recommended   ##
##############################################

#python update_config.py -resx ### -resy ### -framer ## -thres ## -port ####
# -- Sets config file to requested variables
#python update_config.py -r hard
# -- Resets config file to basic structure
import sys

config_for_recovery = """#############################################
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
VIDEO_FRAMERATE = 20

#Motion Detection Settings
########################
#Default 25  --  Lower more sensitive
THRESHOLD_VALUE = 25

#Server Settings
########################

#Ephemeral port# for camera server (1024 to 65535)
PORT_NUM = 8000"""

#Argument check
#Config Reset
if len(sys.argv) == 3 and sys.argv[1] == '-r':
    if sys.argv[2] == 'hard':
        hard_reset_config()
    else:
        print("Attempted file reset.\nRun with '-r hard' to hard reset config file")
#Config Update
elif len(sys.argv) == 11 and sys.argv[1] == '-resx' and sys.argv[3] == '-resy' and sys.argv[5] == '-framer' and sys.argv[7] == '-thres' and sys.argv[9] == '-port':
    update_config(sys.argv[2], sys.argv[4], sys.argv[6], sys.argv[8], sys.argv[10])
else:
    print("Invocation Error.")
    print("python update_config.py -resx ### -resy ### -framer ## -thres ## -port ####\n -- Sets config file to requested variables\npython update_config.py -r hard\n -- Resets config file to default structure")

def hard_reset_config():
    print("Resetting config file to defaults.")
    f = open("config.py", "w")
    f.write(config_for_recovery)
    f.close()
    print("Done.")

def update_config(new_resx, new_resy, new_framer, new_thres, new_port):
    loc_resx = 0
    loc_resy = 0
    loc_framer = 0
    loc_thres = 0
    loc_port = 0
    resx_forward = 0
    resy_forward = 0
    framer_forward = 0
    thres_forward = 0
    port_forward = 0
    new_file = ""

    #Extract existing file structure
    with open("config.py", "r+") as f:
        old = f.read()
        loc_resx = old.index('RESOLUTION_X = ')
        resx_forward = old[loc_resx:].index('\n') + loc_resx
        loc_resy = old.index('RESOLUTION_Y = ')
        resy_forward = old[loc_resy:].index('\n') + loc_resy
        loc_framer = old.index('VIDEO_FRAMERATE = ')
        framer_forward = old[loc_framer:].index('\n') + loc_framer
        loc_thres = old.index('THRESHOLD_VALUE = ')
        thres_forward = old[loc_thres:].index('\n') + loc_thres
        loc_port = old.index('PORT_NUM = ')
        f.seek(0) # be kind, rewind

    #Constructing new file
    new_file += old[:loc_resx+15]
    new_file += str(new_resx)
    new_file += old[resx_forward:loc_resy+15]
    new_file += str(new_resy)
    new_file += old[resy_forward:loc_framer+18]
    new_file += str(new_framer)
    new_file += old[framer_forward:loc_thres+18]
    new_file += str(new_thres)
    new_file += old[thres_forward:loc_port+11]
    new_file += str(new_port)

    f = open("config.py", "w")
    f.write(new_file)
    f.close()
    print("Done")

    return True