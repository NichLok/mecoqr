import sys
import mariadb

def mysqldb_select(table, info, condition=None):
    """table: str(table_name)
        info: str(info to retrieve)
        condition: str(condition)
        output: list of tuples"""
    try:
        cnx = mariadb.connect(host='178.128.31.63',
                                        database='capstone', 
                                        user='capstone',
                                        password='capstone')

        if condition == None: 
            query_select = """SELECT {} from {}""".format(info, table)
        else:
            query_select = """SELECT {} from {} WHERE {}""".format(info, table, condition)

        
        cursor = cnx.cursor()
        cursor.execute(query_select)
        records = cursor.fetchall() #for one item
            # records = records[0]
            # print(records)

        cursor.close()
        cnx.close()
        print("MySQL {} selection done".format(table))
            
    except mariadb.Error as e:
        print("Error: ", e)
        cnx.rollback() #undo all data changes from the current transaction
        records = None
    
    return records



table = 'history'
info = 'user_id'
condition = 'med_name = "med2"'
output = mysqldb_select(table, info, condition)
print(output)
