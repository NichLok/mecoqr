'''
Notes:
-qr data: frequency_code, no._pills_each, medname, frequency, size_mm, shape_ratio, colour_HSV

Function:
-create qr code      1. scan qr      2. organise qrcode data     3. dispense pill       4. CV check

Autorun on rpi boot:
M1: terminal: sudo nano /etc/rc/local; before exit 0, python /home/pi/file.py &; ctrl x then y then enter; sudo reboot
M2: systemd
https://learn.sparkfun.com/tutorials/how-to-run-a-raspberry-pi-program-on-startup/all
'''

#'fswebcam -r 1280x720 --no-banner image.jpg' to take picture on webcam. Image found in pi/home


import ast
import colorsys
from datetime import datetime
import imutils
from imutils import perspective
import numpy as np
import os
from picamera import PiCamera
from picamera.array import PiRGBArray
from PIL import Image
from pyzbar.pyzbar import decode
import RPi.GPIO as GPIO
import schedule
from scipy.spatial import distance as dist
import serial
import threading
import time
from time import sleep
import xlrd


def update_med_freq_list_excel(excel_name, sheet_name):
    '''update med_freq from excel file'''
    med_freq_dic = {}

    wb = xlrd.open_workbook(excel_name)
    sheet = wb.sheet_by_name(sheet_name)
    sheet.cell_value(0,0)

    for i in range(2, sheet.nrows):
        row = sheet.row_values(i)
        key = int(row[0])
        value = ast.literal_eval(row[3])
        med_freq_dic[key] = value
    print(med_freq_dic)
    return med_freq_dic


def read_qr_loading(compartment): #input float(compartment number)
    '''read qr using camera at each compartment and save data to compartments'''
    goto = 'goto {}'.format(str(compartment))
    sleep(1)
    ser.write(goto.encode())
    print('send ' + goto)
    while True:
        x = ser.readline()
        print(x)
        reach = x == b'reached\r\n'
        print('reached: ' + str(reach))
        if reach == True:
            break
    print('reached {}'.format(str(compartment)))

    done = False
    while not done:
        try:
            camera = PiCamera()
            camera.start_preview()
            camera.zoom = (0.3, 0.2, 0.7, 0.7) #need to calibrate
            sleep(2)
            camera.capture('/home/pi/Desktop/pill{}.jpg'.format(str(compartment)))
            camera.stop_preview()
            camera.close()
            image = 'pill{}.jpg'.format(str(compartment))

            data = decode(Image.open(image))
            data_str = data[0][0].decode('utf-8')
            compartments[compartment] = data_str
            print(compartments)
            done = True

        except IndexError:
            print('read_qr_error_{}'.format(compartment))


def decode_qr_loading():
    '''organise saved compartments into schedules -- timing and pills'''
    for key in compartments:
        if compartments[key] != 'NIL':
            each_med_data = compartments[key].split()
            med_code = each_med_data[0]
            timing_list = med_freq_all[float(med_code)]
            qty = each_med_data[1]
            data_send = str(key) * int(float(qty))
            for timing in timing_list:
                if timing in schedules.keys():
                    schedules[timing] += data_send
                else:
                    schedules[timing] = data_send
    print('schedules: ' + str(schedules))
    return schedules
    
def dispense(time): #input timing
    '''send pill info as string to arduino at specific timing'''
    pill = schedules[time]
    print('send {} at {}'.format(pill, time))


def run_threaded(job_func, time):
    job_thread = threading.Thread(target=job_func, args=time)
    job_thread.start()


def create_schedule_all():
    '''create all the executable schedules'''
    for key in schedules: 
        schedule.every().day.at(key).do(run_threaded, dispense, time=[key]) #if one arg, then need ['08:30']
        #schedule.every(int(key)).seconds.do(run_threaded, dispense, time=[key]) #for demo


def dispense_demo(pill, time):
    print ('demo send {} at {}'.format(pill, time))




'''
morning: 08:30
aftnn: 12:30
evening: 19:30
night: 22:30

-# times per day
- every # hours
-before/after meals
-bedtime
-every alt days
-morn
-with food
'''


