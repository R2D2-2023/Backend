# import the necessary packages to open postgresql database connection hosted on azure
import psycopg2
# import pandas as pd
# import numpy as np
import random
import datetime
import time
import sys

passwd = ""

with open(".env", "r") as f:
    lines = f.readlines()
    for line in lines:
        if line.startswith("DBPASS="):
            passwd = line.split("=")[1].strip()
            break

try:
    # define the connection string to connect to the database
    conn_string = "host=m3s-sql-02.postgres.database.azure.com port=5432 dbname={your_database} user=m3s_admin password={your_password} sslmode=require".format(your_database='postgres', your_password=passwd)  
except Exception as e:
    print("Error: ", e)
    passwd = input("Enter password: ")
    conn_string = "host=m3s-sql-02.postgres.database.azure.com port=5432 dbname={your_database} user=m3s_admin password={your_password} sslmode=require".format(your_database='postgres', your_password=passwd)

# connect to the database
conn = psycopg2.connect(conn_string)

# create a cursor object
cursor = conn.cursor()

# generate random data
print("Generating random data and inserting into database...")
route = [[30, 50],[100, 50],[100, 240],[20, 240],[20, 150]]

# Compress the route
# by merging two uint8_t's into an uint16_t
route_compressed = []
for i in range(len(route)):
    route_compressed.append(route[i][0] + route[i][1] * 256)
list_of_uint16_t = str(route_compressed).replace("[", "{").replace("]", "}")

# create the query
query = f"INSERT INTO aabbccddeeff7778route (datetime, route) VALUES ('{datetime.datetime.now()}', '{list_of_uint16_t}');"
print(query)

# execute the query
cursor.execute(query)

# commit the transaction
conn.commit()



# close the communication with the database
cursor.close()