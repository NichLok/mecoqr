
from mysqlrpi import *
from gstoragerpi import *
from cvrpi import *


class Pill:
    def __init__(self):
        self.name = None #str
        self.colour = None #RGB list
        self.shape = None #str
        self.size = None #sorted list in mm
        self.image = None #str(img_path)
        self.error = False #cv error
        
        
    def get_features_ref(self, compartment):
        '''input: type(compartment)= int
        retrieve pill features (name, colour, shape, size) from db'''
        
        #### !!!!!! change condition to routines.compartment
        info = mysqldb_select(table='routines rout, reference ref',
                              info='rout.med_name, ref.shape, ref.size, ref.colour',
                              condition="rout.id = '{}' and rout.med_name = ref.med_name".format(compartment))
        
        self.name, self.shape, size, colour = info[0] #cos format is [(...)]
        self.size = eval(size) # convert str to list
        self.colour = eval(colour) # convert str to tuple
    
    
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
        
        #colour tolerance of 60 each, compare the RGB
        colour_len = len(self.colour)
        for i in range(colour_len):
            colour_diff = abs(self.colour[i] - pill.colour[i])
        
        if colour_len == 3:
            colour_match = colour_diff <= 60
        
        if colour_len == 6: #multicolour
            colour_match = colour_diff <= 120
            
        return shape_match and colour_match and size_match
    
    
    def create_test(self):
        '''For testing purpose'''
        self.colour = (244, 233, 222)
        self.shape = 'capsule'
        self.size = [23, 44]
        


## INCOMPLETE !!check if need to retrieve id and user_id, img_url
#note: unixtime is time to dispense
def update_UI(id, user_id, med_name, unixtime, img_path):
    '''update mysql.history when pill is correct'''
    
    upload_blob(bucket_name, img_path, destination_blob_name)
    
    img_url = '{}{}'.format(bucket_name, destination_blob_name) #TO EDIT
    
    #delete local img afterwards??
    
    mysqldb_insert(table='history',
                   values='({}, {}, {}, {}, {})'.format(id, user_id, med_name, unixtime, img_url))
    



###########################################################################
###########################################################################

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

    
        
        
        