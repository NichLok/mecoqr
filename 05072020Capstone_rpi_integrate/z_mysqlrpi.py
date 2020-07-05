import mysql.connector
from mysql.connector import Error


#mysqldb: insert, select, update, delete

def mysqldb_insert(table, values):
    """table: str(table_name)
        values: tuple"""
    try:
        cnx = mysql.connector.connect(host='178.128.31.63',
                                       database='capstone', 
                                        user='capstone',
                                        password='capstone')
            
        query_insert = """INSERT INTO {} VALUES {}""".format(table, values)
        
        # query_insertm = """INSERT INTO TestTable VALUES (%s,%s)"""
        # records_to_insert = [('v1', 1), ('v2', 2)]

        if cnx.is_connected():
            cursor = cnx.cursor()
            cursor.execute(query_insert)
            # cursor.executemany(query_insertm, records_to_insert) #for many inserts

            cnx.commit() #make changes persistent in DB
            cursor.close()
            cnx.close()
            print("MySQL {} insertion done".format(table))

    except Error as e:
        print("MySQL Insert Error: ", e)
        cnx.rollback() #undo all data changes from the current transaction


def mysqldb_select(table, info, condition=None):
    """table: str(table_name)
        info: str(info to retrieve)
        condition: str(condition)
        output: list of tuples"""
    try:
        cnx = mysql.connector.connect(host='178.128.31.63',
                                        database='capstone', 
                                        user='capstone',
                                        password='capstone')

        if condition == None: 
            query_select = """SELECT {} from {}""".format(info, table)
        else:
            query_select = """SELECT {} from {} WHERE {}""".format(info, table, condition)

        if cnx.is_connected():
            cursor = cnx.cursor()
            cursor.execute(query_select)
            records = cursor.fetchall() #for one item
            # records = records[0]
            # print(records)

            cursor.close()
            cnx.close()
            print("MySQL {} selection done".format(table))

    except Error as e:
        print("MySQL Select error: ", e)
        cnx.rollback() #undo all data changes from the current transaction
        records = None
    
    return records


########################################################################################
########################################################################################

# entry = mysqldb_select('reference','*')
# print(entry[0])

