from mysqlrpi import *
# import os
from PIL import Image
import pygame
# import sys
from pygame.locals import *
import pygame.camera
from pyzbar.pyzbar import decode


# !!!! dk if needed
# compartments = dict(enumerate(['NIL']*compartment_total,1)) #key is compartment, value is qr data


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
            #print(data_str)
            compartments[compartment] = data_str #not needed unless multiple compartments
            #print(compartments)
            done = True
            return data_str
        
        except IndexError:
            print('read_qr_error_{}'.format(compartment))
            


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
        values = table_id, user_id, med_name, currentUnix, nextUnix, timeRange
        #print(table,values)
        mysqldb_insert(table,values)
        
        
        

# qr_string = read_qr_loading(1)
# sendQRtoSQL(qr_string)