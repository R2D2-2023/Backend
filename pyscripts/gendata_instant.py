# import the necessary packages to open postgresql database connection hosted on azure
import psycopg2
# import pandas as pd
# import numpy as np
import random
import datetime
import time
import sys

passwd = input("Enter db password: ")

# define the connection string to connect to the database
conn_string = "host=m3s-sql-02.postgres.database.azure.com port=5432 dbname={your_database} user=m3s_admin password={your_password} sslmode=require".format(your_database='postgres', your_password=passwd)  

# connect to the database
conn = psycopg2.connect(conn_string)

# create a cursor object
cursor = conn.cursor()

# # Create table in the database with the following columns
# # datetime, co2 (ppm), temperature (C), humidity (%), pressure (hPa)
query = "CREATE TABLE IF NOT EXISTS sensor_data (datetime timestamp, co2 integer, temperature integer, humidity integer, pressure integer);"

cursor.execute(query)

# commit the transaction
conn.commit()

time.sleep(0.1)

co2 = random.randint(400, 1000)
temperature = random.randint(20, 30)
humidity = random.randint(40, 60)
pressure = random.randint(1000, 1100)

while True:
    # generate random data
    print("Generating random data and inserting into database...")
    while True:
        diff = random.randint(-20, 20)
        if co2 + diff < 400 or co2 + diff > 1000:
            continue
        co2 += diff
        break
    while True:
        diff = random.randint(-2, 2) * 0.5
        if temperature + diff < 20 or temperature + diff > 30:
            continue
        temperature += diff
        break
    while True:
        diff = random.randint(-1, 1)
        if humidity + diff < 40 or humidity + diff > 60:
            continue
        humidity += diff
        break
    while True:
        diff = random.randint(-5, 5)
        if pressure + diff < 1000 or pressure + diff > 1100:
            continue
        pressure += diff
        break
        
    # location = random.randint(1, 10)
    location = 1

    # create the query
    query = "INSERT INTO sensor_data (datetime, co2, temperature, humidity, pressure, location) VALUES ('{time_with_offset}', {co2}, {temperature}, {humidity}, {pressure}, {location});".format(time_with_offset=datetime.datetime.now(), co2=co2, temperature=temperature, humidity=humidity, pressure=pressure, location=location)

    # execute the query
    cursor.execute(query)

    # commit the transaction
    conn.commit()

    #sleep for 10 seconds
    # time.sleep(random.randint(1, 10))


# close the communication with the database
cursor.close()