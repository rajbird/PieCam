#!/usr/bin/python
# USAGE
# python main.py --ip 0.0.0.0

# import the necessary packages
from pyimagesearch.motion_detection import SingleMotionDetector
from imutils.video import VideoStream
from flask import Response, Flask, request, render_template, send_from_directory, redirect, url_for
from datetime import datetime
from importlib import reload
import socket
import sys
import os
import threading
import argparse
import time
import imutils
import logging
import cv2
import json
import psutil

#Configuration Settings Import
import config
# custom py file imports
import emailing

# User validation imports
from userAccounts.accountFunctions import authenticateUser, createUser

# Web app imports
from webapp.getdebugdata import getDebugInformation
from webapp.changesettings import parseChangeSettingsInput
from update_config import update_config, hard_reset_config

############################
#                          #
#      INITIALIZATION      #
#                          #
############################

CURRENT_USER = None

THREAD_EXIT = False

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful for multiple browsers/tabs
# are viewing tthe stream)
outputFrame = None
lock = threading.Lock()

# initialize a flask object
template_dir = os.path.abspath('webapp/public')
app = Flask(__name__, template_folder=template_dir)

# initialize the video stream. If on raspberry pi, use picamera.. else use default
vs = None
if "pi" in socket.gethostname(): # Need to check this
    vs = VideoStream(usePiCamera=1, resolution=(config.RESOLUTION_X,config.RESOLUTION_Y), framerate=config.VIDEO_FRAMERATE).start()
else:
    vs = VideoStream().start()

time.sleep(2.0) # Allow the camera's sensor to warm up

img_array = []



##############################
#                            #
#      MOTION DETECTION      #
#                            #
##############################

def detect_motion(frameCount):
    # grab global references to the video stream, output frame, and
    # lock variables
    global vs, outputFrame, lock, THREAD_EXIT

    # initialize the motion detector and the total number of frames
    # read thus far
    md = SingleMotionDetector(accumWeight=0.1)
    total = 0
    start = 0
    MOTIONPATH = "data/motion"
    area = []

    #os.chdir("data/bin")

    # loop over frames from the video stream
    while not THREAD_EXIT:
        # read the next frame from the video stream, resize it,
        # convert the frame to grayscale, and blur it
        frame = vs.read()
        frame = imutils.resize(frame, width=600)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)

        # grab the current timestamp and draw it on the frame
        timestamp = datetime.now()
        cv2.putText(frame, timestamp.strftime(
            "%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

        # if the total number of frames has reached a sufficient
        # number to construct a reasonable background model, then
        # continue to process the frame
        if total > frameCount:
            # detect motion in the image
            motion = md.detect(gray)

            # check to see if motion was found in the frame
            if motion is not None:
                if(start == 0):
                    currentPATH = MOTIONPATH + '/' + getTimeStamp('folder')
                    makeFolder(currentPATH)
                    start=time.time()
                    motionTime = time.ctime()
                    del area[:]

                # unpack the tuple and draw the box surrounding the
                # "motion area" on the output frame
                (thresh, (minX, minY, maxX, maxY)) = motion
                cv2.rectangle(frame, (minX, minY), (maxX, maxY), (0, 0, 255), 2)

                logging.debug(f"min: {minX} {minY}   max: {maxX} {maxY}   area: {(maxX-minX) * (maxY-minY)}")
                # calculating the area of rectangle drawn and appending it area list
                area.append( (maxX-minX) * (maxY-minY) )
                if (int(time.time() - start) < 4):
                    cv2.imwrite((currentPATH + '/' + getTimeStamp('jpg')), frame)
                else:
                    emailing.notify(currentPATH, getTimeStamp('gif'), motionTime, area)
                    start=0
                    del area[:]
            else:
                if start != 0:
                    emailing.notify(currentPATH, getTimeStamp('gif'), motionTime, area)
                start = 0
                del area[:]
            # height, width, layers = frame.shape
            # size = (width,height)
            # out = cv2.VideoWriter('project.avi',cv2.VideoWriter_fourcc(*'DIVX'), 15, size)

            # for i in range(len(img_array)):
            #     out.write(img_array[i])
            # out.release()

        # update the background model and increment the total number
        # of frames read thus far
        md.update(gray)
        total += 1

        # acquire the lock, set the output frame, and release the
        # lock
        with lock:
            outputFrame = frame.copy()

def getTimeStamp(fileType):
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    stamp = str(datetime.fromtimestamp(timestamp)).replace(':', '')
    if fileType == 'jpg':
        return stamp + '.jpg'
    elif fileType == 'gif':
        return stamp + '.gif'
    else:
        return stamp

#path = the folder path  ex. data/motion/2020-02-18 162853.278578
def makeFolder(path):
    try:
        os.mkdir(path)
    except Exception as e:
        logging.error(f"Creation of the directory {path} failed, due to {e}")
    #else:
    #    print ("successfully  C R E A T E D  the directory %s" % path)


#####################
#                   #
#      WEB APP      #
#                   #
#####################

def generate():
    # grab global references to the output frame and lock variables
    global outputFrame, lock

    # loop over frames from the output stream
    while not THREAD_EXIT:
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if outputFrame is None:
                continue

            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

            # ensure the frame was successfully encoded
            if not flag:
                continue

        # yield the output frame in the byte format
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
            bytearray(encodedImage) + b'\r\n')

@app.route('/', methods=['GET', 'POST'])
def login():
    global CURRENT_USER
    error = None
    if request.method == 'POST':
        user_fp = open('userAccounts/users.txt', 'r')
        if user_fp:
            loginRes = authenticateUser(request.form['username'], request.form['password'], user_fp)
            if loginRes:
                CURRENT_USER = loginRes
                user_fp.close()
                return redirect('/index.html')
            else:
                error = 'Invalid Credentials. Please try again.'
        else:
            error = 'Error in users db file. Contact administrator.'
        user_fp.close()
        

    return render_template('login.html', error=error)

@app.route("/index.html")
def index():
    global CURRENT_USER
    if CURRENT_USER:
        # return the rendered template
        return render_template("index.html")
    else:
        return redirect("/")

@app.route("/style/<path:path>")
def send_style(path):
    return send_from_directory('webapp/public/style', path)

@app.route("/script/<path:path>")
def send_script(path):
    return send_from_directory('webapp/public/script', path)

@app.route("/assets/<path:path>")
def send_asset(path):
    return send_from_directory('webapp/public/assets', path)

@app.route("/video_feed")
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    return Response(generate(),
        mimetype = "multipart/x-mixed-replace; boundary=frame")

@app.route("/debug")
def debug():
    return render_template("debug.html")

@app.route("/settings.html")
def settings():
    return render_template("settings.html")

@app.route("/debug_refresh")
def debug_refresh():
    return getDebugInformation()

@app.route("/change_settings")
def change_settings():
    global config
    user_input = request.args.get('input')
    parse_ret = parseChangeSettingsInput(user_input)
    logging.info(parse_ret)

    ret = {'success': False}

    if parse_ret['valid']:
        logging.info("CHANGING SETTINGS")
        resx = parse_ret['value'] if parse_ret['setting'] == 'resx' else config.RESOLUTION_X
        resy = parse_ret['value'] if parse_ret['setting'] == 'resy' else config.RESOLUTION_Y
        framerate = parse_ret['value'] if parse_ret['setting'] == 'framerate' else config.VIDEO_FRAMERATE
        threshold = parse_ret['value'] if parse_ret['setting'] == 'threshold' else config.THRESHOLD_VALUE
        port = parse_ret['value'] if parse_ret['setting'] == 'port' else config.PORT_NUM
        # Need to connect the parts
        update_ret = update_config(resx, resy, framerate, threshold, port)
        if update_ret:
            config = reload(config)
            ret['success'] = True
    return json.dumps(ret)

@app.route("/get_settings")
def get_settings():
    return json.dumps({
        'resx': config.RESOLUTION_X,
        'resy': config.RESOLUTION_Y,
        'framerate': config.VIDEO_FRAMERATE,
        'threshold': config.THRESHOLD_VALUE,
        'port': config.PORT_NUM
    })

#############################
#                           #
#      PROGRAM RESTART      #
#                           #
#############################
@app.route("/restart_program")
def restart_program():
    logging.info("This will restart the system (?)")
    # ATTEMPT 1 (Didn't work)
    # Restarts the current program, with file objects and descriptors cleanup
    # try:
    #     p = psutil.Process(os.getpid())
    #     for handler in p.open_files() + p.connections():
    #         os.close(handler.fd)
    # except Exception as e:
    #     print("FATAL ERROR RESTARTING PROGRAM:")
    #     print(e)
    #     exit(-1)

    # ATTEMPT 2+ (Didn't work)
    global vs, THREAD_EXIT
    # restart_lock = True

    THREAD_EXIT = True

    print(dir(vs.stream))
    print("###")
    # vs.stream.close()
    vs.stop()
    # vs = None
    time.sleep(2.0)
    # config = reload(config)

    python = sys.executable
    os.execl(python, python, *sys.argv)

    return json.dumps({'test': 'test'})


###########################
#                         #
#      PROGRAM ENTRY      #
#                         #
###########################

# check to see if this is the main thread of execution
if __name__ == '__main__':
    # construct the argument parser and parse command line arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=True,
        help="ip address of the device")
    ap.add_argument("-f", "--frame-count", type=int, default=32,
        help="# of frames used to construct the background model")
    ap.add_argument("-l", "--log", type=str, default="log",
        help="where log will out put, enter a file name or cmd to log to terminal")
    args = vars(ap.parse_args())


    format = "%(asctime)s -  %(levelname)s: %(message)s"
    if args["log"] == "cmd":
        logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    elif args["log"] == "log":
        logging.basicConfig(filename="log.txt", filemode='w', format=format, level=logging.INFO, datefmt="%H:%M:%S")
    else:
        logging.basicConfig(filename=args["log"], filemode='w', format=format, level=logging.INFO, datefmt="%H:%M:%S")

    logging.debug("Thread starting to perform motion detection")
    # start a thread that will perform motion detection
    t = threading.Thread(target=detect_motion, args=(
        args["frame_count"],))
    t.daemon = True
    t.start()
    
    # start the flask app
    app.run(host=args["ip"], port=config.PORT_NUM, debug=True,
        threaded=True, use_reloader=False)

    print("\n Time to setup your account\n")

    #user_email = input("Please enter your email: ")
    #p = getpass.getpass()




    # release the video stream pointer
vs.stop()
