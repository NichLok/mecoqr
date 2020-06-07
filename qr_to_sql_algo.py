
'''
2.0 1.0 red capsule 3 times a day ? 21.5 2.91 355.0 
{1: '2.0 1.0 red capsule 3 times a day ? 21.5 2.91 355.0 ', 2: 'NIL', 3: 'NIL', 4: 'NIL', 5: 'NIL'}
['2.0', '1.0', 'red', 'capsule', '3', 'times', 'a', 'day', '?', '21.5', '2.91', '355.0']
2.0
1.0
'''

'''
Desired string
2 med3 1591419800 1 1591420000 1
'''
test_string = '2 med3 1591419800 1 1591420000 1'
user_id= 'c123'
currentUnix = '1590285600'
table = 'routines'

med_list = test_string.split()
iterations = int(med_list[0])
med_name = med_list[1]

print(iterations)
for i in range(iterations):
    table_id = str(i+1)
    nextUnix_index= (i*2) + 2 #finds nextUnix value position
    nextUnix = med_list[nextUnix_index] #finds nextUnix value 
    timeRange_index = (i*2) + 3 #finds timeRange value position
    timeRange = med_list[timeRange_index] #finds timeRange value
    print(table_id, user_id, med_name, currentUnix, nextUnix, timeRange)
