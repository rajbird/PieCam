##########################################
# email sending code referenced from:
# https://dev.to/davidmm1707/how-to-send-beautiful-emails-with-attachments-yes-cat-pics-too-using-only-python-4l9e
##########################################

from email.mime.text import MIMEText
from email.utils import formataddr
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from string import Template
from PIL import Image

from datetime import datetime, timedelta

import smtplib, ssl
import threading
import logging
import shutil
import numpy
import time
import glob
import os
import zipfile

#Configuration Settings Import
import config

#need to find a way to encrypt the PASSWORD, idea: store it in .txt with encryption
MY_ADDRESS = 'piecamme@gmail.com'
PASSWORD = 'Raspberry2020'
CONTACTS_FILE = 'data/email/contacts'
MOTION_EMAIL = 'data/email/motionTemplate'
ZIP_EMAIL = 'data/email/zipTemplate'
STORAGE_PATH = "data/motion/"
BIN_PATH = "data/motion/bin"
ZIP_FILE = "data/downtime.zip"
EMAIL_ON = True
TIME_START = 0
"""
   - is-hour-up datetime for keeping track of hourly motion notification sending
   - should-i-send datatune for keeping track of when last zip email was sent
   - days, hours, minutes: is to help sent time between sending zip email
   NOTE: for testing purpose, set 'days': 0, 'hours': 0, 'minutes': 5
   and set line 101 to TIME_CHECK['is-hour-up'] = datetime.now() + timedelta(days=0, hours=0, minutes=1)
"""
TIME_CHECK = {'is-hour-up': 0, 'should-i-send': 0, 'days': 0, 'hours': 0, 'minutes': 1}

def notify(folderPath, fileName, timestamp, area):
    global TIME_START
    #minimum area = 2.5% of the frame size
    miniArea = (config.RESOLUTION_X * config.RESOLUTION_Y) * 0.025
    miniSD = miniArea/2
    miniFrameCount = 18

    #if area of motion is less than miniArea pixels, (taking the measure of spread into account)
    # or if less than 18 frames given to create a gif
    #then log motion detection but do not send email
    if((numpy.mean(area) < miniArea and numpy.std(area) < miniSD) or len(area) < miniFrameCount):
        if(TIME_START == 0):
            logging.info(f"Very minimal motion was detected at {timestamp}")
            TIME_START = time.time()
            moveFiles(folderPath, True)
        elif(int(time.time() - TIME_START) < 45):
            logging.info("continual minimal motion is happening")
            moveFiles(folderPath, False)
        elif(int(time.time() - TIME_START) > 45 and int(time.time() - TIME_START) < 60):
            notify(folderPath, fileName, timestamp, ([6000] * 19))
        else:
            TIME_START = 0
            shutil.rmtree(BIN_PATH)
        return

    TIME_START = 0

    logging.debug(f"creating thread at {timestamp} for motion notification handling")
    ##creating a child process to handle emailing
    t = threading.Thread(target=sendNotifcationEmail, args=(folderPath, fileName, timestamp,))
    t.daemon = True
    t.start()

def sendNotifcationEmail(folderPath, fileName, timestamp):
    global TIME_CHECK

    #go get the gif
    gif = STORAGE_PATH + fileName   # example name  --->   data/motion/2020-02-25 120142.873830.gif
    makeGif(folderPath, gif)

    print(gif)

    #only send an email if emailing is on and a gif was created
    if(EMAIL_ON):
        if(TIME_CHECK['is-hour-up'] != 0):
            #check if email already sent this hour
            if(datetime.now() < TIME_CHECK['is-hour-up']):
                #if email has been sent, don't delete the gif and don't send an email
                logging.info(f"Motion was detected at {timestamp}. Motion was detected this hour so no email sent")
                return

        #if times up, only send zip email and no motion notification email
        if(isTimeUp(timestamp)):
            print("here")
            return

        TIME_CHECK['is-hour-up'] = datetime.now() + timedelta(days=0, hours=0, minutes=1)
        # TIME_CHECK['is-hour-up'] = datetime.now() + timedelta(days=0, hours=1, minutes=0)
        sendAttachment(gif, MOTION_EMAIL, ("Motion was detected at " + timestamp), timestamp)
    else:
        #deletes gif if created
        logging.info(f"Motion was detected at {timestamp}, but email was not sent")
        os.remove(gif)

def isTimeUp(timestamp):
    global TIME_CHECK
    if(TIME_CHECK['should-i-send'] == 0):
        TIME_CHECK['should-i-send'] = datetime.now() + timedelta(days=TIME_CHECK['days'], hours=TIME_CHECK['hours'], minutes=TIME_CHECK['minutes'])
        return False

    if(datetime.now() > TIME_CHECK['should-i-send']):

        makeZip(ZIP_FILE, STORAGE_PATH)
        sendZipAttachment(ZIP_FILE, ZIP_EMAIL, ('Compiled Motion during downtime'), timestamp)

        """
        add stuff here to handle sending zip files
        - 1: call to create zip file: this should be deleting all .gif in STORAGE_PATH
        - 2: send zip email
        - 3: delete zip file
        NOTE: no need to create a new thread, already on a separate thread from main program
        """
        logging.info(f"{timestamp}: zip email was sent")
        #updating TIME_CHECK['should-i-send'] to next future datatime
        TIME_CHECK['should-i-send'] = datetime.now() + timedelta(days=TIME_CHECK['days'], hours=TIME_CHECK['hours'], minutes=TIME_CHECK['minutes'])
        return True

    return False

def moveFiles(path, first):
    #if first time function called, delete folder if still exists and create a new one
    if(first):
        if(os.path.exists(BIN_PATH)):
            shutil.rmtree(BIN_PATH)
        os.mkdir(BIN_PATH)

    globStr = path + "/*.jpg"
    imgs = glob.glob(globStr)

    for img in imgs:
        shutil.move(img, BIN_PATH)

    os.rmdir(path)

def makeGif (folderPath, fileName):
    globStr = folderPath + "/*.jpg"

    frames = []
    imgs = glob.glob(globStr)
    for i in imgs:
        newFrame = Image.open(i)
        frames.append(newFrame)

    frames[0].save(fileName, format='GIF',
                   append_images=frames[1:],
                   save_all=True,
                   duration=17, loop=0)   #duration is milliseconds delay between frames, higher # = faster

    shutil.rmtree(folderPath)
    #print("File stored at location: " + os.getcwd())

def makeZip (filePath, storage):
    downtime_zip = zipfile.ZipFile(filePath, 'w')

    for folder, subfolders, files in os.walk(storage):

        for file in files:
            if file.endswith('.gif'):
                downtime_zip.write(os.path.join(folder, file), os.path.relpath(os.path.join(folder,file), storage), compress_type = zipfile.ZIP_DEFLATED)

        try:
            for fn in files:
                if fn.endswith('.gif'):
                    os.remove(os.path.join(folder, fn))
        except:
            print("File still in use")

    downtime_zip.close()

def getContacts():
    """
    Return two lists names, emails containing names and email addresses
    read from a file specified by filename.
    """
    names = []
    emails = []
    with open(CONTACTS_FILE, mode='r', encoding='utf-8') as contacts_file:
        for a_contact in contacts_file:
            names.append(a_contact.split()[0])
            emails.append(a_contact.split()[1])
    return names, emails

def readTemplate(filename):
    """
    Returns a Template object comprising the contents of the
    file specified by filename.
    """
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)

def sendPlainMsg (templateFile, subject):
    names, emails = getContacts()
    messageTemplate = readTemplate(templateFile)

    for name, email in zip(names, emails):
        msg = MIMEMultipart()       # create a message

        # add in the actual person name to the message template
        message = messageTemplate.substitute(PERSON_NAME=name.title())

        # setup the parameters of the message
        msg['From']=MY_ADDRESS
        msg['To']=email
        msg['Subject']=subject

        # add in the message body
        msg.attach(MIMEText(message, 'plain'))

        # send the message via the server, with encryption
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            context = ssl.create_default_context()
            server.starttls(context=context)
            server.login(MY_ADDRESS, PASSWORD)
            server.send_message(msg)
            # print(message)
        except Exception as e:
            logging.error(f'Oh no! Something bad happened!n {e}')
        finally:
            logging.info('Closing the server...')
            server.quit()
        del msg

def sendAttachment (fileAttachment, templateName, subject, timestamp):
    names, emails = getContacts()
    messageTemplate = readTemplate(templateName)
    filename = timestamp + ".gif"

    for name, email in zip(names, emails):
        msg = MIMEMultipart()
        message = messageTemplate.substitute(PERSON_NAME=name.title(), TIME_STAMP=timestamp)

        msg['From']= formataddr(("Pie Cam", MY_ADDRESS))
        msg['To']= formataddr((name, email))
        msg['Subject']=subject

        msg.attach(MIMEText(message, 'plain'))

        try:
            # Open file in binary mode
            with open(fileAttachment, "rb") as attachment:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(attachment.read())

            # Encode file in ASCII characters to send by email
            encoders.encode_base64(part)

            # Add header as key/value pair to attachment part
            part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {filename}",
            )

            msg.attach(part)
        except Exception as e:
                logging.error(f'Oh no! We did not find the attachment! {e}')
                break

        # send the message via the server, with encryption
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            context = ssl.create_default_context()
            server.starttls(context=context)
            server.login(MY_ADDRESS, PASSWORD)
            server.send_message(msg)
        except Exception as e:
            logging.error(f'Oh no! Something bad happened!n {e}')
        finally:
            logging.info(f'{subject}  --> Email sent closing the server...')
            server.quit()
            os.remove(fileAttachment)
        del msg

def sendZipAttachment (fileAttachment, templateName, subject, timestamp):
    names, emails = getContacts()
    messageTemplate = readTemplate(templateName)
    filename = "downtime.zip"

    for name, email in zip(names, emails):
        msg = MIMEMultipart()
        message = messageTemplate.substitute(PERSON_NAME=name.title())

        msg['From']= formataddr(("Pie Cam", MY_ADDRESS))
        msg['To']= formataddr((name, email))
        msg['Subject']=subject

        msg.attach(MIMEText(message, 'plain'))

        try:
            # Open file in binary mode
            with open(fileAttachment, "rb") as attachment:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(attachment.read())

            # Encode file in ASCII characters to send by email
            encoders.encode_base64(part)

            # Add header as key/value pair to attachment part
            part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {filename}",
            )

            msg.attach(part)
        except Exception as e:
                logging.error(f'Oh no! We did not find the attachment! {e}')
                break

        # send the message via the server, with encryption
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            context = ssl.create_default_context()
            server.starttls(context=context)
            server.login(MY_ADDRESS, PASSWORD)
            server.send_message(msg)
        except Exception as e:
            logging.error(f'Oh no! Something bad happened!n {e}')
        finally:
            logging.info(f'{subject}  --> Email sent closing the server...')
            server.quit()
            os.remove(fileAttachment)
        del msg
