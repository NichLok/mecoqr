def load(no_of_compartments=6):
    '''perform QR code reading when loading button is pressed'''
    #read qr and store info into mysql.routines
    end_table_id = 1 #initialise table_id
    hardcode_string = '' #for hardcode of instructions that sends arduino dispensing instructions
    for i in range(no_of_compartments):
        compartment_number = i+1
        end_table_id = i
        hardcode_string = hardcode_string + str(compartment_number)*end_table_id
    print(hardcode_string)

load()