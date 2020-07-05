from google.cloud import storage
import numpy as np
import mysql.connector
from mysql.connector import Error
# import os

# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"/home/pi/Capstone CV test-2d364b707dd7.json"
# print('Credentials from environ: {}'.format(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')))


def implicit():
    from google.cloud import storage

    # If you don't specify credentials when constructing the client, the
    # client library will look for credentials in the environment.
    storage_client = storage.Client()

    # Make an authenticated API request
    buckets = list(storage_client.list_buckets())
    print(buckets)
    
    
def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    # bucket_name = "your-bucket-name"
    # source_blob_name = "storage-object-name"
    # destination_file_name = "local/path/to/file"

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    print(np.array(blob))
    blob.download_to_filename(destination_file_name)

    print("Blob {} downloaded to {}.".format(source_blob_name, destination_file_name))
    

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print("File {} uploaded to {}.".format(source_file_name, destination_blob_name))
    
    
    
def make_blob_public(bucket_name, blob_name):
    """Makes a blob publicly accessible."""
    # bucket_name = "your-bucket-name"
    # blob_name = "your-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.make_public()

    print("Blob {} is publicly accessible at {}".format(blob.name, blob.public_url))
        
    



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




###########################################################################
###########################################################################

# implicit()
# bucket_name = "capstone_pill_us"
# destination_blob_name = "capstone_project_images/testgcloud"
# source_file_name = r"/home/pi/Desktop/gcloud_test.jpg"
# 
# upload_blob(bucket_name, source_file_name, destination_blob_name)
# make_blob_public(bucket_name, destination_blob_name)

# https://storage.googleapis.com/capstone_pill_us/capstone_project_images/testgcloud



# entry = mysqldb_select('reference','*')
# print(entry[0])