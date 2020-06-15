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
            compartments[compartment] = data_str #not needed unless multiple compartments
            print(compartments)
            done = True
            return data_str
        except IndexError:
            print('read_qr_error_{}'.format(compartment))
            

#mysqldb: insert, select, update, delete
def mysqldb_insert(table, values):
    """table: str(table_name)
        values: tuple"""
    try:

        cnx = mysql.connector.connect(host='178.128.31.63',
                                        database='capstone', 
                                        user='capstone',
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

def sendQRtoSQL(qr_string,user_id='c123',currentUnix='1590285600',table='routines'):
    med_list = qr_string.split()
    iterations = int(med_list[0])
    med_name = med_list[1]

    for i in range(iterations):
        table_id = str(i+3)
        nextUnix_index= (i*2) + 2 #finds nextUnix value position in med_list
        nextUnix = med_list[nextUnix_index] #finds nextUnix value 
        timeRange_index = (i*2) + 3 #finds timeRange value position in med_list
        timeRange = med_list[timeRange_index] #finds timeRange value
        quantity_index = (i*2) + 4 #finds quantity value position in med_list
        quantity = med_list[quantity_index] #finds quantity value
        values = table_id, user_id, med_name, currentUnix, nextUnix, timeRange, quantity
        print(table,values)
        mysqldb_insert(table,values)

qr_string = read_qr_loading(1)
sendQRtoSQL(qr_string)