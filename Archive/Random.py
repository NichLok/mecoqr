def load_demo(demo_compartment, no_of_compartments=6):
    '''perform QR code reading when loading button is pressed'''
    #read qr and store info into mysql.routines
    end_table_id = 1 #initialise table_id
    for i in range(no_of_compartments):
        compartment_number = i+1
        table_id = end_table_id
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
        end_table_id = sendQRtoSQL(qr_string,table_id)
        #demo_compartment = demo_compart 'done scanning