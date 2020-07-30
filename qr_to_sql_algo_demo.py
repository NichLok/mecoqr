# from mysqlrpi import *
import mysql.connector
from mysql.connector import Error
# import os
from PIL import Image
import pygame
# import sys
from pygame.locals import *
import pygame.camera
from pyzbar.pyzbar import decode

'''
Desired string that is taken from QR code
2 Bilaxten 20 1591419800 1 3 1591420000 1 2
[0] - Indicates iterations required for string
[1] - Name of medication
[2] - Total quantity inserted into Meco
[3] - Dispensing Time
[4] - Indicates daily requirement
[5] - Number of pills that is required to be dispensed at timing, given at [3]
[6,7,8] - Required if there is a second, third time. Iterates [3,4,5]
'''


def read_qr_loading(compartment): #input float(compartment number)
    '''read qr using camera at each compartment and save data to compartments'''
    width = 640
    height = 480

    done = False
    error_no = 0 #initalise counting of errors
    while not done:
        if error_no <10:
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
                #pygame.image.save(init_image,'/home/pi/Desktop/Capstone_rpi_integrate/local_image/qr_scan/pill{}.jpg'.format(str(compartment)))
                #image = '/home/pi/Desktop/Capstone_rpi_integrate/local_image/qr_scan/pill{}.jpg'.format(str(compartment))
                
                #qr code decoding
                data = decode(Image.open(image)) 
                data_str = data[0][0].decode('utf-8')
                #print(data_str)
                #compartments[compartment] = data_str #not needed unless multiple compartments
                #print(compartments)
                done = True
                return data_str
            
            except IndexError:
                error_no += 1
                print('read_qr_error_{}, try number {}'.format(compartment, error_no))
        else:
            data_str = "skip"
            done = True
            return data_str
            
def mysqldb_insert(table, values):
    """table: str(table_name)
        values: tuple"""
    try:
        cnx = mysql.connector.connect(host='178.128.31.63',
                                       database='capstone', 
                                        user='capstone',
                                        password='capstone')
            
        query_insert = """INSERT INTO {} VALUES {}""".format(table, values)
        
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

def sendQRtoSQL(qr_string,compartment_number, user_id='c123',currentUnix='1590285600',table='routines (user_id, day, med_name, currentUnix, nextUnix, quantity, compartment, total_quantity)'):
    med_list = qr_string.split()
    iterations = int(med_list[0])
    med_name = med_list[1]
    total_quantity = med_list[2]
    for i in range(iterations): #to iterate the timings in a day
        timeRange_index = (i*3) + 4 #finds timeRange value position in med_list
        timeRange = med_list[timeRange_index] #finds timeRange value
        if timeRange == '1':
            day_value = 7
        for j in range(day_value): #to iterate 7 times for a daily dosage
            day = j + 1 #indicates day, starting with day = 1
            nextUnix_index= (i*3) + 3 #finds nextUnix value position in med_list
            nextUnix = med_list[nextUnix_index] #finds nextUnix value 
            quantity_index = (i*3) + 5 #finds quantity value position in med_list
            quantity = med_list[quantity_index] #finds quantity value
            values = user_id, day, med_name, currentUnix, nextUnix, quantity, compartment_number, total_quantity
            print(table,values)
            mysqldb_insert(table,values)


compartment_number = 1 #Will be set automatically in real thing
#reads QR code
qr_string = read_qr_loading(compartment_number)
if qr_string != "skip":
    #uploads QR code to database
    sendQRtoSQL(qr_string,compartment_number)