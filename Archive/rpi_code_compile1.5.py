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

import ast
import colorsys
import cv2
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
        

def light_control(*kwargs):
    while True:
        while state == 'loading' or state == 'dispensing':
            GPIO.output(light_loading, GPIO.HIGH)
            sleep(0.3)
            GPIO.output(light_loading, GPIO.LOW)
            sleep(0.3)
        GPIO.output(light_loading, GPIO.HIGH)

def sound_control():
    while True:
        sleep(1.5)
        if sound == True:
            os.system('mpg321 musict.mp3 &')
            sleep(9)
    
def dispense(time): #input timing
    '''send pill info as string to arduino at specific timing'''
    pill = schedules[time]
    ser.write(pill.encode())
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
    ser.write(pill.encode())
    print ('demo send {} at {}'.format(pill, time))


##########################################################################################################
def midpoint(ptA, ptB):
    return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)


def PixelsCalibration(data):
    (x1,y1),(x2,y2),(x3,y3),(x4,y4) = [(data[0].polygon[i][0],data[0].polygon[i][1]) for i in range(0,4)]

    length1 = ((x1-x2)**2 + (y1-y2)**2)**0.5
    length2 = ((x2-x3)**2 + (y2-y3)**2)**0.5
    length3 = ((x3-x4)**2 + (y3-y4)**2)**0.5
    length4 = ((x4-x1)**2 + (y4-y1)**2)**0.5
    length_avg = (length1+length2+length3+length4)/4
    return length_avg


def checking_Pills():
    ## Enable the capturing of video
    #video = cv2.VideoCapture(1)
    camera = PiCamera()
    rawCapture = PiRGBArray(camera)
    sleep(0.1)
    waitframe = False

    ## To calibrate the background of the dispensing area
    #To capture a continuous frame
    for frame in camera.capture_continuous(rawCapture,format="bgr", use_video_port=True):
            #get the raw NumPy array representing the image
            background = frame.array
            cv2.imshow("Mai camera", background)
            
            #check if there is QRcode in the background
            data = decode(background)
            #print (data)
            if data == []: #If there is no QR code detected, do nothing
                pass
            elif str(data[0][0]) == "b'Pablo and Subbu are the best instructors. Thanks for the A.'" :
                
                #Send  a message
                print("Dispenser reached")
                
                #add a delay, then read the frame again
                if waitframe == False:
                    sleep(1.5)
                    rawCapture.truncate(0) #clear the stream in preperation for the next frame
                    waitframe = True
                    continue
                else:
                    background = frame.array
                    data = decode(background) #take reference frame of QR code from the new frame
                
                #Calibration of the "ruler" with reference to QR code
                pixelsPermm = PixelsCalibration(data)/19.6
                print("Calibration: {}pixels/mm".format(pixelsPermm))

                ## Parameters for cropping of the image##
                #define the coordinates of the topleft of the QR code
                qrleft = data[0][2][0]
                qrtop = data[0][2][1]
                print (qrleft,qrtop)

                #define the coordinates to shift the QRcode
                shifLeftmm = 30
                shiftTopmm = 25
                dispWidthmm = 40
                dispTopmm = 50
                
                y, x, h, w = (int(qrtop+(shiftTopmm-dispTopmm)*pixelsPermm), 
                            int(qrleft+(shifLeftmm*pixelsPermm)), 
                            int(dispTopmm*pixelsPermm), int(dispWidthmm*pixelsPermm))
                print(y, y+h, x, x+w)

                background = background[y:y+h, x:x+w] #ref from top left of screen
                sleep(6) # wait for pill to drop
                rawCapture.truncate(0) #clear the stream in preparation for the nextframe
                waitframe = False #reset the waitframe variable
                break

            #clear the stream in preparation for the nextframe
            rawCapture.truncate(0)

    ## Extract the image
    camera.capture(rawCapture,format="bgr") # Read in your image in colour
    img = rawCapture.array
    #cv2.imshow("Sub camera", img)
    img = img[y:y+h, x:x+w] #ref from top left of screen
    cv2.imshow("cropped img", img)
    
    ## close the camera
    camera.close()
    

    index = 0

    cv2.destroyAllWindows()


    ##Pre-pocessing of the image
    #Convert image to black and white
    background_bw = cv2.cvtColor(background,cv2.COLOR_BGR2GRAY)
    background_hsv = cv2.cvtColor(background,cv2.COLOR_BGR2HSV)
    background_hsv[:,:,2] = 90 #for shadow reduction
    background2 = cv2.cvtColor(background_hsv,cv2.COLOR_HSV2BGR)
    img_bw = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    img_hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    img_hsv[:,:,2] = 90 #for shadow rreduction
    img2 = cv2.cvtColor(img_hsv,cv2.COLOR_HSV2BGR)

    ##compare the background and foreground, highlight the difffernce in white

    #calculates the diff btwn the first frame and other frames
    img_delta = cv2.absdiff(img2,background2)
    #cv2.imshow('thresh_delta', img_delta) #ghjkl
    #cv2.waitKey(0)

    #provides threshold value, convert difference valiue <30 to black, >30 to white.
    _, img_delta = cv2.threshold(img_delta, 35 , 255, cv2.THRESH_BINARY)

    #convert to black and white
    img_delta = cv2.cvtColor(img_delta,cv2.COLOR_BGR2GRAY)
    _, img_delta = cv2.threshold(img_delta, 20, 255, cv2.THRESH_BINARY)

    #cv2.imshow('thresh_delta2', img_delta) #ghjkl
    #cv2.waitKey(0)

    ##Find contour of the object detected in img_delta
    contours, _ = cv2.findContours(img_delta.copy(), cv2.RETR_EXTERNAL, 
                                    cv2.CHAIN_APPROX_SIMPLE)

    #create mask to store pixels of contours cropped
    mask_all = np.zeros_like(img_bw)
    out_all = np.zeros_like(img)
 
    # Find the colour in each contour of the mask
    for cnt in contours:
        #Skip the contour if the contour is small, noise reduction
        if cv2.contourArea(cnt) <300:
            #print("small contour, skipped")
            continue
        ## Record the number of contours found
        index +=1
        print(index)

        ##Colour identification:

        #create a temp mask
        mask = np.zeros_like(img_bw) # Create mask where white is what we want, black otherwise


        approx = cv2.approxPolyDP(curve=cnt, epsilon=0.02*cv2.arcLength(cnt,True), 
                                    closed=True) #The larger the epsilon, the less it fills into gaps in the shape      
        x = approx.ravel()[0]
        y = approx.ravel()[1]

        #Label the contour
        cv2.putText(img_delta, "Cnt {}".format(index), (x, y), cv2.FONT_HERSHEY_COMPLEX, 1, (100, 100, 130))
        
        #Draw the contour in masks
        cv2.drawContours(mask_all, [cnt], 0, 255, -1) # Draw filled contour in mask_all
        cv2.drawContours(mask, [cnt], 0, 255, -1) # Draw filled contour in mask

        # Extract out the object and place into output image
        out = np.zeros_like(img)
        out_all[mask == 255] = img[mask == 255]
        out[mask == 255] = img[mask == 255]

        # Seperate the colours
        out_edge = cv2.Canny(out, 20, 150)
        out_edge = cv2.dilate(out_edge, None, iterations=2)
        out_edge = cv2.bitwise_not(out_edge)
        out_edge = cv2.bitwise_and(out_edge, mask)
        # out_edge =  cv2.bitwise_not(out_edge)
        contours2, _ = cv2.findContours(out_edge.copy(), cv2.RETR_EXTERNAL, 
                                    cv2.CHAIN_APPROX_SIMPLE)
        if contours2 == []:
            continue #skip this loop if there are no colours detected

        print("Number of colour contours found {}".format(len(contours2)))

        colour_total = 0
        hsvcolor = 999
        hsvcolor2 = 999
        for cnt2 in contours2:
            if cv2.contourArea(cnt2) < 0.2*cv2.contourArea(cnt):
                hsvcolor = 0
                continue
            ## Record the number of colours found
            colour_total +=1
            out = np.zeros_like(img)
            mask2 = np.zeros_like(img_bw)
            cv2.drawContours(mask2, [cnt2], 0, 255, -1) # Draw filled contour in mask
            out[mask2 == 255] = img[mask2 == 255]


            hist_b = cv2.calcHist([out], channels=[0], mask=None, histSize=[256-1], ranges=[1,256])
            hist_g = cv2.calcHist([out], channels=[1], mask=None, histSize=[256-1], ranges=[1,256])
            hist_r = cv2.calcHist([out], channels=[2], mask=None, histSize=[256-1], ranges=[1,256])
            print("Contour {}:".format(index))
            blue = hist_b.tolist().index(max(hist_b))
            green = hist_g.tolist().index(max(hist_g))
            red = hist_r.tolist().index(max(hist_r))

            hsv_value = colorsys.rgb_to_hsv(red/255.0, green/255.0, blue/255.0)
            hsv_value = [hsv_value[0]*360, hsv_value[1]*100, hsv_value[2]*100]
            print(red,green,blue)
            print(hsv_value)
            
            if hsvcolor == 999:
                hsvcolor = hsv_value[0]
            else:
                hsvcolor2 = hsv_value[0]
            

        ##Size identification

        # compute the rotated bounding box of the contour
        orig = img.copy()
        box = cv2.minAreaRect(cnt)
        box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
        box = np.array(box, dtype="int")
        # print(box)

        # order the points in the contour such that they appear
        # in top-left, top-right, bottom-right, and bottom-left
        # order, then draw the outline of the rotated bounding
        # box
        box = perspective.order_points(box)
        cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)
     
        # loop over the original points and draw them
        for (x, y) in box:
            cv2.circle(orig, (int(x), int(y)), 5, (0, 0, 255), -1)
        # unpack the ordered bounding box, then compute the midpoint
        # between the top-left and top-right coordinates, followed by
        # the midpoint between bottom-left and bottom-right coordinates
        (tl, tr, br, bl) = box
        (tltrX, tltrY) = midpoint(tl, tr)
        (blbrX, blbrY) = midpoint(bl, br)
     
        # compute the midpoint between the top-left and top-right points,
        # followed by the midpoint between the top-righ and bottom-right
        (tlblX, tlblY) = midpoint(tl, bl)
        (trbrX, trbrY) = midpoint(tr, br)
     
        # draw the midpoints on the image
        cv2.circle(orig, (int(tltrX), int(tltrY)), 5, (255, 0, 0), -1)
        cv2.circle(orig, (int(blbrX), int(blbrY)), 5, (255, 0, 0), -1)
        cv2.circle(orig, (int(tlblX), int(tlblY)), 5, (255, 0, 0), -1)
        cv2.circle(orig, (int(trbrX), int(trbrY)), 5, (255, 0, 0), -1)
     
        # draw lines between the midpoints
        cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),
            (255, 0, 255), 2)
        cv2.line(orig, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)),
            (255, 0, 255), 2)

        # compute the Euclidean distance between the midpoints
        dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
        dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))

        # compute the size of the object
        dimA = dA / pixelsPermm
        dimB = dB / pixelsPermm
        length = max(0.001,dimA,dimB)
        width = min(999999,dimA,dimB)
        ratio = length/width
        print("The length is {}".format(length))
        print("The ratio is {}".format(ratio))
     
        # draw the object sizes on the image
        cv2.putText(orig, "{:.1f}mm".format(dimA),
            (int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX,
            0.65, (100, 200, 0), 2)
        cv2.putText(orig, "{:.1f}mm".format(dimB),
            (int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX,
            0.65, (100, 200, 0), 2)
        cv2.putText(orig, "Hue:{}".format(int(hsvcolor)),
            (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
            0.65, (100, 200, 0), 2)

        #show the output image
        cv2.imshow('bounding', orig)
        cv2.imshow('thresh_delta', img_delta)
        cv2.imshow('mask', mask_all)
        cv2.imshow('Output', out_all)
        cv2.imwrite( "/home/pi/Desktop/img/{}.jpg".format(time.time()), mask_all)
        cv2.imwrite( "/home/pi/Desktop/img/o{}.jpg".format(time.time()), orig)
        cv2.imwrite( "/home/pi/Desktop/img/d{}.jpg".format(time.time()), img_delta)
        #cv2.waitKey(0)
        return length, ratio, hsvcolor, hsvcolor2
    return 0,0,999,999 #if there is no object detected


def verifying_Pills (index, detected_size, detected_ratio, detected_color=0, detected_color2=999):
    container = int(index)
    try:
        size, ratio, hsvcolor, hsvcolor2 = get_pill_data2(container)
    #if from excel uncomment below
    except:
        #raise
        print("dictionary decoding error")
        size, ratio, hsvcolor, hsvcolor2 = get_pill_data(container)
        
    #for dispensing skittles
    if hsvcolor == 361.0:
       return True, True, True

    size_tolerance = 0.7
    ratio_tolerance = 0.6
    hsv_tolerance = 22

    print ("size:" + str(size) + "ratio:" + str(ratio) + "hsv1:" + str(hsvcolor) + " hsv2:" + str(hsvcolor2))
    if abs(size-detected_size) < size_tolerance:
        print("size within range")
        size_correct = True
    else:
        print("size out of range")
        size_correct = False
    if abs(ratio-detected_ratio) < ratio_tolerance:
        print("ratio within range")
        ratio_correct = True
    else:
        print("ratio out of range")
        ratio_correct = False

    #Contigency for dectecting only the darker colour
    if hsvcolor2 !=999:
       hsvcolor = max(hsvcolor, hsvcolor2)
       hsvcolor2 = 999

    #2nd condition inserted incase the number is very close to 360
    if (abs(hsvcolor - detected_color) < hsv_tolerance) or  (
        detected_color < (hsvcolor+hsv_tolerance)%360):
        print("colour1 within range. (Con1)")
        colour_correct = True
    else:
        print("colour1 out of range. (Con1)")
        colour_correct = False

    if hsvcolor2 != 999:
        if colour_correct == False:
            #check if the previous colour is the current colour
            if (abs(hsvcolor2 - detected_color) < hsv_tolerance*2) or  (
                detected_color < (hsvcolor2+hsv_tolerance*2)%360):
                print("colour2 within range. (Con2.1)")
                colour_correct = True
            if (abs(hsvcolor - detected_color2) > hsv_tolerance) or  (
                detected_color2 > (hsvcolor+hsv_tolerance)%360):
                print("colour1 not within range. (Con2.2)")
                colour_correct = False
            else: 
                colour_correct = True
                print("colour2 within range. (Con2.3)")
        else:
            if (abs(hsvcolor2 - detected_color2) > hsv_tolerance*2) or  (
                detected_color2 > (hsvcolor2+hsv_tolerance*2)%360):
                print("colour2 not within range. (Con3.1)")
                colour_correct = False
            else: 
                colour_correct = True
                print("colour2 within range. (Con3.2)")

    #for dispensing white pills
    if hsvcolor == 225.0:
        colour_correct = True

    return size_correct, ratio_correct, colour_correct


def get_pill_data (container): #retriving from excel
    excel_name = "medicinefrequency.xlsx"
    sheet_name = "med"
    wb = xlrd.open_workbook(excel_name)
    sheet = wb.sheet_by_name(sheet_name)
    for row in range(sheet.nrows):
        if sheet.cell_value(row, 0) == container:
            pill_row = row
            pill_size= sheet.cell_value(pill_row, 6)
            pill_ratio= sheet.cell_value(pill_row, 7)
            hsv_data = sheet.cell_value(pill_row, 8)
            if "," in str(hsv_data):
                pill_hsv, pill_hsv2 = hsv_data.split(",")
            else:
                pill_hsv = hsv_data
                pill_hsv2 = 999
    return float(pill_size), float(pill_ratio), float(pill_hsv), float(pill_hsv2)

def get_pill_data2 (container): #retriving from dictionary
    data = compartments[int(container)] #Declare variable compartment in setup
    _ , info = data.split("? ") #get the string behind "? "
    print(info)
    info = info.strip()
    pill_size, pill_ratio, hsv_data = info.split(" ") #spilt by spacing
    if "," in str(hsv_data):
        pill_hsv, pill_hsv2 = hsv_data.split(",")
    else:
        pill_hsv = hsv_data
        pill_hsv2 = 999
    return float(pill_size), float(pill_ratio), float(pill_hsv), float(pill_hsv2)

def tell_arduino_pill_is_correct (size_correct, ratio_correct, colour_correct):
    if size_correct and ratio_correct and colour_correct:
        ser.write("ok".encode())
        print('send ok')
        return 1
    elif incorrect_pill == 2:
        ser.write("error".encode())
        print('send error')
        return 0
    else:
        ser.write("not ok".encode())
        print('send not ok')
        return 0

########################################################################################################


#setup
button_loading = 10
light_loading = 8
GPIO.setmode(GPIO.BOARD)
GPIO.setup(button_loading, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(light_loading, GPIO.OUT)

compartment_total = 5
compartments = dict(enumerate(['NIL']*compartment_total,1)) #key is compartment, value is qr data
#compartments = {1: '2.0 1.0 red capsule 3 times a day ? 21.5 2.91 355.0 ', 2: '4.0 3.0 yellow tic tac evening ? 11.6 1.73 47.0 ', 3: '5.0 2.0 small white round pill once a day ? 6.1 1.0 225.0 ', 4: '3.0 1.0 green-green capsule 4 times a day ? 17.7 2.85 168, 105 ', 5: '1.0 2.0 red pill 2 times a day ? 19.5 3.0 350.0 '}
schedules = {} #key is time, value is compartment

excel_name = 'medicinefrequency.xlsx'
sheet_name = 'med'
med_freq_all = update_med_freq_list_excel(excel_name, sheet_name) #key is code no., value is list of timing

ser = serial.Serial("/dev/ttyACM0",19200)
ser.baudrate = 19200
state = 'idle' #default is loading
sound = False

light_thread = threading.Thread(target= light_control)
light_thread.start()
sound_thread = threading.Thread(target= sound_control)
sound_thread.start()

#for demo only
pill_demo = '1' #Computer vision is also using this variable
time_now = datetime.now().time()
time_demo = str(time_now.hour) + ':' + str(time_now.minute)

#dummy image
blank = np.zeros((100,100,1),np.uint8)
blank[:] = [0]


if __name__ == "__main__":
    while True:
        #loading
        while state == 'loading':
            print('loading part')
            schedule.clear()
            for i in range(compartment_total):
                read_qr_loading(i+1)
            ser.write('goto 0'.encode())
            print('send goto 0')
            decode_qr_loading()
            create_schedule_all()
            state = 'dispensing'
        
        #dispense
        while state == 'dispensing':
            print('dispense part')
            schedule.run_pending()
            sleep(5)
            dispense_demo(pill_demo, time_demo) #for demo purpose
            index = None
            pill_dispensed = 0
            incorrect_pill = 0
            while pill_dispensed < len(pill_demo):
                correct_pill=-1 #Boolean
                try:
                    index = ser.readline().decode('utf-8') #get from arduino serial
                    print(str(index))
                    print('cv index: ' + str(index))
                except:
                    pass
                if "check pill" in str(index):
                    index = int(str(index[-3])) #obtain the integer index from the message
                    print("checking pill from container {}".format(index))
                    length, ratio, hsvcolor, hsvcolor2 = checking_Pills()
                    size_correct, ratio_correct, colour_correct = verifying_Pills (index, length, ratio, hsvcolor, hsvcolor2)
                    print("\nPress any key to destroy the screens or wait for 4 secs\n\n")
                    cv2.waitKey(86)
                    cv2.destroyAllWindows()
                    correct_pill = tell_arduino_pill_is_correct(size_correct, ratio_correct, colour_correct)
                if correct_pill == 1:
                    pill_dispensed = (pill_dispensed + correct_pill)
                    incorrect_pill = 0
                elif correct_pill == 0:
                    incorrect_pill += 1
                    print('incorrect pill: ' + str(incorrect_pill))
                    if incorrect_pill == 3:
                        while True:
                            os.system('mpg321 error.mp3 &')
                            sleep(5)
                        #pill_dispensed = (pill_dispensed + 1) #The system will move on to the next pill if there is 3 failures
                        #incorrect_pill = 0
                print('pill_dispensed: ' + str(pill_dispensed))
            done = ser.readline()
            print('done: '+str(done))
            sound = done == b'done\r\n'
            print ("sound:" + str(sound))
            pill_dispensed=0
            state = 'idle'
            print('idle state part')
            sleep(2)
        
        #not loading and dispensing
        cv2.imshow("blank",blank)
        while state == 'idle':
            sound = False
            key = cv2.waitKey(100)
            if key == ord('l'):
                state = 'loading'
                cv2.destroyAllWindows()
            elif key == ord('d'):
                state = 'dispensing'
                cv2.destroyAllWindows()
            if GPIO.input(button_loading) == GPIO.LOW:
                state = 'loading'
                cv2.destroyAllWindows()
            #in_waiting returns int(number of bytes in the input buffer)



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


