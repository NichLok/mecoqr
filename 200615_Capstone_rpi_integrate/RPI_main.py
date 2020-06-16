from pillrpi import *
from qrrpi import *
import cv2
import os
import RPi.GPIO as GPIO
import serial
import threading
from time import sleep



##############################################################################################################
##############################################################################################################
user_id = 'c123'
number_of_compartment = 5
demo_compartment = '11223'

load_button = 10





##############################################################################################################
##############################################################################################################


# SETUP
# run once - for gstorage
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"/home/pi/Capstone CV test-2d364b707dd7.json"
print('Credentials from environ: {}'.format(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')))

GPIO.setmode(GPIO.BOARD)
GPIO.setup(load_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#ser = serial.Serial("/dev/ttyACM0",19200)
#ser.baudrate = 19200
state = 'loading'





def load(no_of_compartments=6):
    '''perform QR code reading when loading button is pressed'''
    #read qr and store info into mysql.routines
    end_table_id = 1 #initialise table_id
    hardcode_string = '' #for hardcode of instructions that sends arduino dispensing instructions
    for i in range(no_of_compartments):
        compartment_number = i+1
        table_id = end_table_id
        #gets rail to go to desired compartment number
        goto = 'goto {}'.format(str(compartment_number))
        sleep(1)
        ser.write(goto.encode())
        print('send ' + goto)
        #checks if camera has reached destination
        while True:
            x = ser.readline() #ser.readline().decode('utf-8') #to read what Arduino sent
            print(x)
            reach = x == b'reached\r\n'
            print('reached: ' + str(reach))
            if reach == True:
                break
        print('reached {}'.format(str(compartment_number)))

        #reads QR code
        qr_string = read_qr_loading(compartment_number)
        #uploads QR code to database
        end_table_id = sendQRtoSQL(qr_string,table_id)
        hardcode_string = hardcode_string + str(compartment_number)*end_table_id
    ser.write(hardcode_string.encode()) #uploads finalised hardcode_string into arduino

    pass



def check_pill(compartment):
    '''check the pill using cv,
    output: T/F to dispense'''
    
    #retrieve the correct pill details
    ref_pill = Pill()
    ref_pill.get_features_ref(compartment)
    
    #retrieve the dispensed pill details
    dispensed_pill = Pill()
    dispensed_pill.get_features_cv()
    
    #check if cv has error
    if dispensed_pill.error:
        return 'Error'
    else:
        return dispensed_pill.match(ref_pill)
    
    
    
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
            print('receive Arduino {}'.format(str(arduino_read)))
        except:
            pass
        if "check pill" in str(arduino_read):
            index = int(str(arduino_read[-3])) #obtain the integer index from the message
            print("checking pill from container {}".format(index))
                  
            dispense = check_pill(x)
            if dispense == 'Error':
                #ser.write('error'.encode())
                #print('send Arduino error')
                pass
                
            elif dispense:
                #ser.write('ok'.encode())
                #print('send Arduino ok')
                #update_UI(id, user_id=user_id, med_name=ref_pill.name, unixtime, img_path=dispensed_pill.image)
                #print('updated mysql.history')
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

        



if __name__ == "__main__":
    while True:
        
        while state == 'loading':
            print('loading mode starts')
            load()
            print('loading mode ends')
            state = 'dispensing'
            
        while state == 'dispensing':
            print('dispensing mode starts')
#             dispense_demo(demo_compartment)
#             dispense()
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
                cv2.destroyAllWindows()
            if GPIO.input(load_button) == GPIO.LOW:
                state = 'loading'
                cv2.destroyAllWindows()
           

            
            
    

        
        