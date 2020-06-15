
'''
Desired string
2 med3 1591419800 1 1591420000 1
'''
test_string = '2 med3 1591419800 1 2 1591420000 1 3'
user_id= 'c123'
currentUnix = '1590285600'
table = 'routines'

med_list = test_string.split()
iterations = int(med_list[0])
med_name = med_list[1]

print(iterations)
for i in range(iterations):
    table_id = str(i+1)
    nextUnix_index= (i*2) + 2 #finds nextUnix value position in med_list
    nextUnix = med_list[nextUnix_index] #finds nextUnix value 
    timeRange_index = (i*2) + 3 #finds timeRange value position in med_list
    timeRange = med_list[timeRange_index] #finds timeRange value
    quantity_index = (i*2) + 4 #finds quantity value position in med_list
    quantity = med_list[quantity_index] #finds quantity value
    values = table_id, user_id, med_name, currentUnix, nextUnix, timeRange, quantity
    print(table,values)
