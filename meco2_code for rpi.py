import os
import pygame, sys
from pyzbar.pyzbar import decode
from PIL import Image

from pygame.locals import *
import pygame.camera

import mysql.connector
from mysql.connector import Error

'''
Code sequence
1. Get data from QR code (read qr loading)
2. Break down data (decode qr loading)
3. Insert updated data
'''


#setup
compartment_total = 5
compartments = dict(enumerate(['NIL']*compartment_total,1)) #key is compartment, value is qr data
#compartments = {1: '2.0 1.0 red capsule 3 times a day ? 21.5 2.91 355.0 ', 2: '4.0 3.0 yellow tic tac evening ? 11.6 1.73 47.0 ', 3: '5.0 2.0 small white round pill once a day ? 6.1 1.0 225.0 ', 4: '3.0 1.0 green-green capsule 4 times a day ? 17.7 2.85 168, 105 ', 5: '1.0 2.0 red pill 2 times a day ? 19.5 3.0 350.0 '}
schedules = {} #key is time, value is compartment


def read_qr_loading(compartment): #input float(compartment number)
    '''read qr using camera at each compartment and save data to compartments'''
    width = 640
    height = 480

    done = False
    while not done:
        try:
            #initialise pygame   
            pygame.init()
            pygame.camera.init()
            cam = pygame.camera.Camera("/dev/video0",(width,height))
            cam.start()
            #take a picture
            init_image = cam.get_image()
            cam.stop()
            #save picture
            pygame.image.save(init_image,'/home/pi/Desktop/pill{}.jpg'.format(str(compartment)))
            image = 'pill{}.jpg'.format(str(compartment))
            #qr code decoding
            data = decode(Image.open(image)) 
            data_str = data[0][0].decode('utf-8')
            print(data_str)
            compartments[compartment] = data_str
            print(compartments)
            done = True
        except IndexError:
            print('read_qr_error_{}'.format(compartment))
            
def decode_qr_loading():
    '''organise saved compartments into schedules -- timing and pills'''
    for key in compartments: #key is timing, value is pills
        if compartments[key] != 'NIL':
            each_med_data = compartments[key].split()
            med_code = each_med_data[0]
            
            qty = each_med_data[1]
    
    print(each_med_data)
    print(med_code)
    print(qty)

#mysqldb: insert, select, update, delete
def mysqldb_insert(table, values):
    """table: str(table_name)
        values: tuple"""
    try:

        cnx = mysql.connector.connect(host='178.128.31.63',
                                        database='capstone', 
                                        user='wendy',
                                        password='capstone')
            
        query_insert = """INSERT INTO {} VALUES {}""".format(table, values)
        
        # insert multiple things
        # query_insertm = """INSERT INTO TestTable VALUES (%s,%s)"""
        # records_to_insert = [('v1', 1), ('v2', 2)]

        if cnx.is_connected():
            cursor = cnx.cursor()
            cursor.execute(query_insert)
            # cursor.executemany(query_insertm, records_to_insert) #for many inserts

            cnx.commit() #make changes persistent in DB
            cursor.close()
            cnx.close()
            print("MySQL {} insertion done".format(table))

    except Error as e:
        print("MySQL Insert Error: ", e)
        cnx.rollback() #undo all data changes from the current transaction

read_qr_loading(1.0)
decode_qr_loading()

table = 'routines'
table_id = '3'
user_id = 'c123'
med_name = 'med3'
currentUnix = '1590285600'
nextUnix = '1591419800'
timeRange = '1'
values = (table_id, user_id, med_name, currentUnix, nextUnix, timeRange)
mysqldb_insert(table,values)