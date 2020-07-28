import mysql.connector
from mysql.connector import Error

def mysqldb_delete(table, column, value):
    try:
        cnx = mysql.connector.connect(host='178.128.31.63',
                                        database='capstone', 
                                        user='capstone',
                                        password='capstone')
            
        query_insert = """DELETE FROM {} WHERE {} = '{}'""".format(table, column, value)

        if cnx.is_connected():
            cursor = cnx.cursor()
            cursor.execute(query_insert)
            # cursor.executemany(query_insertm, records_to_insert) #for many inserts

            cnx.commit() #make changes persistent in DB
            cursor.close()
            cnx.close()
            print("MySQL {} deletion done".format(table))

    except Error as e:
        print("MySQL Delete Error: ", e)
        cnx.rollback() #undo all data changes from the current transaction

def delete_old_values(user = 'c123'):
    mysqldb_delete('routines', 'user_id', user)
    print("deleted {} values".format(user))

delete_old_values('c123')