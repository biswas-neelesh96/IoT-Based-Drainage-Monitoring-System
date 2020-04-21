import time, sys
import os
import glob
import picamera
import RPi.GPIO as GPIO
import smtplib
from time import sleep

# Importing modules for sending mail
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

sender = 'XXXX@gmail.com'               #Sender's E-mail address
password = 'XXXX'                       #Sender's E-mail password
receiver = 'XXXX@gmail.com'             #Receiver's E-mail address

DIR = './Database/'
FILE_PREFIX = 'image'

#For counting the Number of revolution of Flow Sensor
pulse_pin = 25
GPIO.setmode(GPIO.BCM)
GPIO.setup(pulse_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
count1=0
def countPulse1(channel):
        global count1
        print("Number of revolution of wheel of flow sensor:")
        count1+=1
        print(count1)
GPIO.add_event_detect(pulse_pin, GPIO.RISING, callback=countPulse1)
print("Inside while starting")
time.sleep(10)

#defining a function to send E-mails        
def send_mail():
    print ('Sending E-Mail')    # Create the directory if not exists
    if not os.path.exists(DIR):
        os.makedirs(DIR)
    # Find the largest ID of existing images.
    # Start new images after this ID value.
    
    files = sorted(glob.glob(os.path.join(DIR, FILE_PREFIX + '[0-9][0-9][0-9].jpg')))
    count = 0
    
    if len(files) > 0:
        # Grab the count from the last filename.
        count = int(files[-1][-7:-4])+1

    # Save image to file
    filename = os.path.join(DIR, FILE_PREFIX + '%03d.jpg' % count)
    # Capture the face
    with picamera.PiCamera() as camera:
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17,GPIO.OUT)
        GPIO.output(17,True)
        time.sleep(10)
        GPIO.output(17,False)
        pic = camera.capture(filename)
    # Sending mail
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = 'Overflow in Drainage System'
    
    body = "Sir/Ma'am, Overflow of water has blocked the drainage system of your area. Please kindly check this attachment"
    msg.attach(MIMEText(body, 'plain'))
    attachment = open(filename, 'rb')
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename= %s' % filename)
    msg.attach(part)
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender, password)
    text = msg.as_string()
    server.sendmail(sender, receiver, text)
    server.quit()

while True:
    if count1 < 100:  # When output from flow sensor doesn't exceed the threshold value 
        print ("No Water clog")
        sleep(0.3)
    elif count1 >= 100:  # When output from flow sensor exceeds threshold value
        print ("Water clog detected in the drainage system")
        send_mail()
        for j in range(0,2):
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(27,GPIO.OUT)
            GPIO.setup(23,GPIO.OUT)
            GPIO.output(27,True)
            GPIO.output(23,True)
            time.sleep(15)
            GPIO.output(27,False)
            GPIO.output(23,False)
            time.sleep(1)
            GPIO.cleanup()
