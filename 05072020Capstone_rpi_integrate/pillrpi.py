
# from mysqlrpi import *
# from gstoragerpi import *
from datainterfacerpi import *
# from cvrpi import *
from cvrpi_multitest import *
# import time


class Pill:
    def __init__(self):
        self.name = None #str
        self.colour = None #RGB list
        self.shape = None #str
        self.size = None #sorted list in mm
        self.image = None #str(img_path)
        self.error = False #cv error
        
        
    def get_features_ref(self, compartment, user_id):
        '''input: type(compartment)= int
        retrieve pill features (name, colour, shape, size) from db'''
        
        # get med_name from routines table and retrieve pill info from reference table
        info = mysqldb_select(table='routines rout, reference ref',
                              info='rout.med_name, ref.shape, ref.size, ref.colour',
                              condition="rout.compartment = '{}' and rout.user_id = '{}' and rout.med_name = ref.med_name".format(compartment, user_id))
        print('data for reference pill: {}'.format(info))
        self.name, self.shape, size, colour = info[0] #cos format is [(...)]
        self.size = eval(size) # convert str to list
        self.colour = eval(colour) # convert str to list
    
    
    def get_features_cv(self):
        '''retrieve pill features through computer vision'''
        self.shape, self.colour, self.size, self.image, self.error = pill_cv()
        
        
    def match(self, pill):
        '''check if shape, colour and size matches'''
        
        shape_match = self.shape == pill.shape
        
        #size tolerance of 2mm
        size_match = True
        for i in range(len(self.size)):
            size_match = size_match and abs(self.size[i]-pill.size[i]) <= 2
        
        #colour tolerance of 10 each, compare the RGB
        colour_tolerance = 10
        colour_len = len(self.colour)
        for i in range(colour_len):
            colour_diff = abs(self.colour[i] - pill.colour[i])
        
        if colour_len == 3:
            colour_match = colour_diff <= 3*colour_tolerance
        
        elif colour_len == 6: #multicolour
            colour_match = colour_diff <= 6*colour_tolerance
            
            # swap the two colour position and check again if colour does not match
            if colour_match == False:
                pill_colour = pill.colour[3:] + pill.colour[:3]
                for i in range(colour_len):
                    colour_diff = abs(self.colour[i] - pill_colour[i])
                colour_match = colour_diff <= 6*colour_tolerance
            
        return shape_match and colour_match and size_match
    
    
    def create_test(self):
        '''For testing purpose'''
        self.colour = [244, 233, 222]
        self.shape = 'capsule'
        self.size = [23, 44]
        



#note: unixtime is time to dispense, currently is float/int
        
def update_UI(user_id, med_name, unixtime, img_path):
    '''upload image onto gstorage and update mysql.history when pill is correct'''
    
    bucket_name = "capstone_pill_us"
    destination_blob_name = "capstone_project_images/{}{}{}".format(user_id, med_name, unixtime)

    upload_blob(bucket_name, img_path, destination_blob_name)
    make_blob_public(bucket_name, destination_blob_name)
    
    img_url = 'https://storage.googleapis.com/{}/{}'.format(bucket_name, destination_blob_name)
    
    #delete local img afterwards??
    
    mysqldb_insert(table='history (user_id, med_name, unixTime, img_url)',
                   values="('{}', '{}', {}, '{}')".format(user_id, med_name, unixtime, img_url))
    


###########################################################################
###########################################################################

# test Pill() class
# ref = Pill()
# ref.create_test()
# print(ref.shape)
# 
# b = Pill()
# b.get_features_ref(1)
# print(b.shape, b.colour, b.size, b.name)
# 
# pill_check = b.match(ref)
# print(pill_check)


# test update_UI() function
# user_id = 'c567'
# med_name = 'med5'
# unixtime = round(time.time())
# print(unixtime)
# img_path = '/home/pi/Desktop/gcloud_test.jpg'
# update_UI(user_id, med_name, unixtime, img_path)
        

        