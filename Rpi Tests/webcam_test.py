#Use this code to test if webcam can take picture with python code

import os
import pygame, sys

from pygame.locals import *
import pygame.camera

width = 640
height = 480

#initialise pygame   
pygame.init()
pygame.camera.init()
cam = pygame.camera.Camera("/dev/video0",(width,height))
cam.start()

#setup window (can be taken out if no display needed)
windowSurfaceObj = pygame.display.set_mode((width,height),1,16)
pygame.display.set_caption('Camera')

#take a picture
image = cam.get_image()
cam.stop()

#display the picture (can be taken out if no display needed)
catSurfaceObj = image
windowSurfaceObj.blit(catSurfaceObj,(0,0))
pygame.display.update()

#save picture
pygame.image.save(windowSurfaceObj,'picture.jpg')