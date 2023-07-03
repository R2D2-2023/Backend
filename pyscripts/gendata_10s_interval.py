# import the necessary packages to open postgresql database connection hosted on azure
import psycopg2
# import pandas as pd
# import numpy as np
import random
import datetime
import time
import sys


passwd = ""

try:
    with open(".env", "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith("DBPASS"):
                passwd = line.split("=")[1].strip()
                break
except:
    try:
        with open("../.env", "r") as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith("DBPASS"):
                    passwd = line.split("=")[1].strip()
                    break
    except:
        passwd = input("PASSWORD:")

# define the connection string to connect to the database
conn_string = "host=m3s-sql-02.postgres.database.azure.com port=5432 dbname={your_database} user=m3s_admin password={your_password} sslmode=require".format(your_database='postgres', your_password=passwd)  

# connect to the database
conn = psycopg2.connect(conn_string)

# create a cursor object
cursor = conn.cursor()

co2 = random.randint(400, 1000)
temperature = random.randint(20*2, 30*2) / 2.0
humidity = random.randint(40, 60)
pressure = random.randint(1000, 1100)
pm10 = random.randint(0, 50)
pm25 = random.randint(0, 50)
pm100 = random.randint(0, 50)
zone = random.randint(1, 10)

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
        if temperature + diff < 20.0 or temperature + diff > 30.0:
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
    while True:
        diff = random.randint(-2, 2)
        if pm10 + diff < 0 or pm10 + diff > 50:
            continue
        pm10 += diff
        break
    while True:
        diff = random.randint(-2, 2)
        if pm25 + diff < 0 or pm25 + diff > 50:
            continue
        pm25 += diff
        break
    while True:
        diff = random.randint(-2, 2)
        if pm100 + diff < 0 or pm100 + diff > 50:
            continue
        pm100 += diff
        break
    while True:
        diff = random.randint(-1, 1)
        if zone + diff < 1 or zone + diff > 10:
            continue
        zone += diff
        break

    # create the query
    query_location = f"INSERT INTO locatie_only (x_loc, y_loc, datetime) VALUES ({random.randint(0,232)}, {random.randint(0,65)}, CURRENT_TIMESTAMP AT TIME ZONE 'CEST');"
    query_sensor_data = f"INSERT INTO sensor_data_with_foreign_location (co2, temperature, humidity, pressure, pm10, pm25, pm100, zone, datetime) VALUES ({co2}, {temperature}, {humidity}, {pressure}, {pm10}, {pm25}, {pm100}, {zone}, CURRENT_TIMESTAMP AT TIME ZONE 'CEST');"

    # execute the query
    cursor.execute(query_location)
    cursor.execute(query_sensor_data)

    # commit the transaction
    conn.commit()

    #sleep for 10 seconds
    time.sleep(random.randint(1, 10))


# close the communication with the database
cursor.close()