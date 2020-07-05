from pillrpi import *
from qrrpi import *
import cv2
from datetime import datetime
import os
import RPi.GPIO as GPIO
import serial
import threading
import time
from time import sleep



##############################################################################################################
##############################################################################################################
user_id = 'c123'
no_of_compartments = 6
compartments = dict(enumerate(['NIL']*no_of_compartments,1)) #key is compartment, value is qr data
print(compartments)

demo = True
demo_compartment = '1'
state = 'dispensing'

load_button = 10





##############################################################################################################
##############################################################################################################


# SETUP
# run once - for gstorage
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"/home/pi/Capstone CV test-2d364b707dd7.json"
print('Credentials from environ: {}'.format(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')))
bucket_name = "capstone_pill_us"

# for GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(load_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# for serial comm
# ser = serial.Serial("/dev/ttyACM0",19200)
# ser.baudrate = 19200

# for TFLite 
# Load TFLite model and allocate tensors.
interpreter = tf.lite.Interpreter(model_path="/home/pi/tflite_pill_detection_trial1/pill_detection_trial1_model-export_iod_tflite-Pill_detection_tr_20200605123101-2020-06-05T08 13 13.970Z_model.tflite")

# Get input and output tensors.
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

interpreter.allocate_tensors()

# Read label names from label file.
with tf.io.gfile.GFile('/home/pi/tflite_pill_detection_trial1/pill_detection_trial1_model-export_iod_tflite-Pill_detection_tr_20200605123101-2020-06-05T08 13 13.970Z_dict.txt', 'r') as f:
    label_names = f.read().split('\n')
  
  
  


def load_demo(demo_compartment, no_of_compartments=6):
    '''perform QR code reading when loading button is pressed'''
    #read qr and store info into mysql.routines
    end_table_id = 1 #initialise table_id
    for i in range(no_of_compartments):
        compartment_number = i+1
        #table_id = end_table_id
        #gets rail to go to desired compartment number
        goto = 'goto {}'.format(str(compartment_number))
        sleep(1)
        #ser.write(goto.encode())
        print('send Arduino ' + goto)
    
        #checks if camera has reached destination
        while True:
            #x = ser.readline() #ser.readline().decode('utf-8') #to read what Arduino sent
            x = b'reached\r\n' #to remove later
            print('receive Arduino ', x)
            reach = x == b'reached\r\n'
            print('reached: ' + str(reach))
            if reach == True:
                break
        print('reached {}'.format(str(compartment_number)))

        #reads QR code
        qr_string = read_qr_loading(compartment_number)
        #uploads QR code to database
        sendQRtoSQL(qr_string,compartment_number)
    #ser.write("done scanning".encode())
    print('send Arduino done scanning')
        #demo_compartment = demo_compartment + str(compartment_number)*end_table_id
    #ser.write(demo_compartment.encode()) #uploads finalised demo_compartment into arduino





def check_pill(compartment, user_id):
    '''check the pill using cv,
    output: T/F to dispense'''
    
    #retrieve the correct pill details
    ref_pill = Pill()
    ref_pill.get_features_ref(compartment, user_id)
    
    #retrieve the dispensed pill details
    dispensed_pill = Pill()
    dispensed_pill.get_features_cv()
    
    print('Reference pill details: name: {}, colour: {}, shape: {}, size: {}'.format(ref_pill.name, ref_pill.colour, ref_pill.shape, ref_pill.size))
    print('Dispensed pill details: name: {}, colour: {}, shape: {}, size: {}'.format(dispensed_pill.name, dispensed_pill.colour, dispensed_pill.shape, dispensed_pill.size))
    
    #check if cv has error
    if dispensed_pill.error:
        return 'CV Error'
    else:
        return dispensed_pill.match(ref_pill), ref_pill, dispensed_pill
    
'''
#IGNORE FOR REVIEW 3
def dispense():
    #while True: ????
    #check time to dispense [need to start dispense 5mins beforehand? cos cv too slow]
    #generate compartment_dispense from mysql.routines IDK HOWWWWW
    
    #send to Arduino '11223' whenever, maybe check if demo==True?
    #ser.write(demo_compartment.encode())
    #print('send Arduino {}'.format(demo_compartment))
    #ser.write(compartment_sequence.encode())
    #print('send Arduino {}'.format(compartment_sequence))
    
    #when receive 'check pill x', call check_pill(x)
    #check the pill and dispense/reject accordingly
    pill_dispensed = 0
    while pill_dispensed < len(compartment_sequence):
        try:
            #arduino_read = ser.readline().decode('utf-8')
            #print('receive Arduino {}'.format(str(arduino_read)))
            pass
        except:
            pass
        if "check pill" in str(arduino_read):
            index = int(str(arduino_read[-3])) #obtain the integer index from the message
            print("checking pill from container {}".format(index))
                  
            dispense, ref_pill, dispensed_pill = check_pill(x)
            if dispense == 'Error':
                #ser.write('error'.encode())
                #print('send Arduino error')
                pass
                
            elif dispense:
                #ser.write('ok'.encode())
                print('send Arduino ok')
                update_UI(user_id=user_id, med_name=ref_pill.name, unixtime, img_path=dispensed_pill.image)
                print('updated mysql.history')
                pill_dispensed += 1
                print('pill dispensed')
        
            else:
                #send 'not ok'/'error'
                #ser.write('not ok'.encode())
                #print('send Arduino not ok')
                pass
         
    #continue waiting for instruction? until dispense certain number?
    #when time to dipsense, anything to do?
    #repeat
'''
        
def dispense_demo(demo_compartment, unixtime):
    #send Arduino compartment details
    #ser.write(demo_compartment.encode())
    print('demo send Arduino {}'.format(demo_compartment))
    
    #when receive 'check pill x', call check_pill(x)
    #check the pill and dispense/reject accordingly
    pill_dispensed = 0
    while pill_dispensed < len(demo_compartment):
        try:
            #arduino_read = ser.readline().decode('utf-8')
            #print('receive Arduino {}'.format(str(arduino_read)))
            pass
        except:
            pass
        
        arduino_read = 'check pill {}'.format(demo_compartment[pill_dispensed])

        if "check pill" in str(arduino_read):
            index = int(str(arduino_read[-1]))
            #index = int(str(arduino_read[-3])) #obtain the integer index from the message
            print("checking pill from container {}".format(index))
                  
            dispense, ref_pill, dispensed_pill = check_pill(index, user_id)
    
            if dispense == 'Error':
                #ser.write('error'.encode())
                print('send Arduino error')
                
                
            elif dispense:
                #ser.write('ok'.encode())
                print('send Arduino ok')
#                 update_UI(user_id=user_id, med_name=ref_pill.name, unixtime=unixtime, img_path=dispensed_pill.image)
                print('updated mysql.history')
                pill_dispensed += 1
                print('pill dispensed')
        
            else:
                #send 'not ok'/'error'
                #ser.write('not ok'.encode())
                print('send Arduino not ok')
                
        

            
            
            


if __name__ == "__main__":
    while True:
        while state == 'loading':
            print('loading mode starts')
            if demo:
                load_demo(demo_compartment, no_of_compartments)
            print('loading mode ends')
            state = 'idle' # or dispensing
            print('idle mode starts')
            sleep(2)
            
        while state == 'dispensing':
            print('dispensing mode starts')
            if demo:
                #time = datetime.now().time()
                time = round(time.time())
                dispense_demo(demo_compartment, time)
            else: 
                dispense()
            print('dispensing mode ends')
            state = 'idle'
            print('idle mode starts')
            sleep(2)
            
        while state == 'idle':
            key = cv2.waitKey(100)
            if key == ord('l'):
                state = 'loading'
                cv2.destroyAllWindows()
            elif key == ord('d'):
                state = 'dispensing'
                demo_compartment = input('demo compartments: ')
                cv2.destroyAllWindows()
            if GPIO.input(load_button) == GPIO.LOW:
                state = 'loading'
                cv2.destroyAllWindows()
           

            
            
    

        
        