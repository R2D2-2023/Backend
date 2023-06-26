import psycopg2
import sys
import json
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from automationassets import get_automation_credential

credentials_postgres = get_automation_credential("postgresql")

conn = psycopg2.connect(
    host="m3s-sql-02.postgres.database.azure.com",
    database="postgres",
    user=credentials_postgres["username"],
    password=credentials_postgres["password"],
    port="5432"
)

# Create a cursor object to execute SQL statements
cur = conn.cursor()

# Read in all of the input from the webhook parameter
payload = ""
for index in range(len(sys.argv)):
    payload += str(sys.argv[index]).strip()

# Get the RequestBody so we can process it
start = payload.find("RequestBody:")
end = payload.find("RequestHeader:")
requestBody = payload[start + 12 : end - 1]

# Parse body as json string and print out the Python ojbect
print(requestBody)
jsonBody = json.loads(requestBody)

decoded_device = jsonBody["end_device_ids"]["dev_eui"]
time_received = jsonBody["received_at"]
decoded_time = datetime.datetime.strptime(time_received[:19], '%Y-%m-%dT%H:%M:%S')

if (jsonBody["uplink_message"]["f_port"] == 1):
    decoded_temp = jsonBody["uplink_message"]["decoded_payload"]["temperature"]
    decoded_humidity = jsonBody["uplink_message"]["decoded_payload"]["humidity"]
    decoded_PPM = jsonBody["uplink_message"]["decoded_payload"]["co2"]
    decoded_pressure = jsonBody["uplink_message"]["decoded_payload"]["pressure"]

    body = ""

    #check temperatures
    if decoded_temp >= 25:
        cur.execute(f"INSERT INTO logbook_abnormal_values (datetime, value, message) VALUES (CURRENT_TIMESTAMP AT TIME ZONE 'CEST', {decoded_temp}, 'De temperatuur is te hoog, de temperatuur is namelijk {decoded_temp}');")
        body += "Er is door de climaatrobot gedetecteerd dat het op locatie 5 te warm is, het is namelijk " + str(decoded_temp) + " graden celsius. Advies: zet een raam open of doe de verwarming lager / uit.\n"
    elif decoded_temp <= 19:
        cur.execute(f"INSERT INTO logbook_abnormal_values (datetime, value, message) VALUES (CURRENT_TIMESTAMP AT TIME ZONE 'CEST', {decoded_temp}, 'De temperatuur is te laag, de temperatuur is namelijk {decoded_temp}');")
        body += "Er is door de climaatrobot gedetecteerd dat het op locatie 5 te koud is, het is namelijk " + str(decoded_temp) + " graden celsius. Advies: doe een raam dicht of doe de verwarming aan.\n"

    #check decoded_humidityity
    if decoded_humidity >= 60:
        cur.execute(f"INSERT INTO logbook_abnormal_values (datetime, value, message) VALUES (CURRENT_TIMESTAMP AT TIME ZONE 'CEST', {decoded_temp}, 'De luchtvochtigheid is te hoog, de luchtvochtigheid is namelijk {decoded_humidity}');")
        body += "Er is door de climaatrobot gedetecteerd dat op locatie 5 de luchtvochtig te hoog is, het is namelijk " + str(decoded_humidity) + " %rh. Advies: zet een raam en deur open, zet een vochtvreter neer.\n"
    elif decoded_humidity <= 30:
        cur.execute(f"INSERT INTO logbook_abnormal_values (datetime, value, message) VALUES (CURRENT_TIMESTAMP AT TIME ZONE 'CEST', {decoded_temp}, 'De luchtvochtigheid is te laag, de luchtvochtigheid is namelijk {decoded_humidity}%');")
        body += "Er is door de climaatrobot gedetecteerd dat op locatie 5 de luchtvochtig te laag is, het is namelijk " + str(decoded_humidity) + " %rh. Advies: zet een luchtbevochtiger neer, zet planten neer.\n"

    #check decoded_PPM (co2)
    if decoded_PPM >= 1000:
        cur.execute(f"INSERT INTO logbook_abnormal_values (datetime, value, message) VALUES (CURRENT_TIMESTAMP AT TIME ZONE 'CEST', {decoded_temp}, 'De co2 in de lucht is te hoog, de co2 gehalte is namelijk {decoded_PPM}');")
        body += "Er is door de climaatrobot gedetecteerd dat op locatie 5 de co2 gehalte te hoog is, het is namelijk " + str(decoded_PPM) + " decoded_PPM. Advies: .\n"
    elif decoded_PPM <= 400:
        cur.execute(f"INSERT INTO logbook_abnormal_values (datetime, value, message) VALUES (CURRENT_TIMESTAMP AT TIME ZONE 'CEST', {decoded_temp}, 'De co2 in de lucht is te laag, de co2 gehalte is namelijk {decoded_PPM} decoded_PPM');")
        body += "Er is door de climaatrobot gedetecteerd dat op locatie 5 de co2 gehalte te laag is, het is namelijk " + str(decoded_PPM) + " decoded_PPM. Advies: zet een raam en deur open, laat lucht doorstromen.\n"

    #check air pressure 
    # if decoded_pressure > 23:
    #     cur.execute(f"INSERT INTO logbook_abnormal_values (datetime, value, message) VALUES (CURRENT_TIMESTAMP AT TIME ZONE 'CEST', {temp}, 'De luchtdruk is te hoog, de luchtdruk is namelijk {pressure}');")

    if(len(body) > 0):
        cur.execute("SELECT * FROM emailaddress")
        mail_adress_list = cur.fetchall()

        smtp_login = get_automation_credential("smtp_login")

        for mail in mail_adress_list:
            msg = MIMEMultipart()
            msg["From"] = smtp_login["username"]
            msg["To"] = mail[0]
            msg["Subject"] = "Waarschuwing hoge waarde"
            msg.attach(MIMEText(body, "plain"))
            with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
                smtp.starttls()
                smtp.login(smtp_login["username"], smtp_login["password"])
                text = msg.as_string()
                smtp.sendmail(smtp_login["username"], mail[0], text)        
    
    
    print(f"Device: {decoded_device}, Date/time: {decoded_time}, Temp: {decoded_temp}, decoded_humidityity: {decoded_humidity}, Co2: {decoded_PPM}, Air pressure: {decoded_pressure}")


    # Execute a SQL statement to create a table for all messages
    cur.execute(f"CREATE TABLE IF NOT EXISTS {decoded_device} (datetime TIMESTAMPTZ NOT NULL, position int, temperature FLOAT NOT NULL, decoded_humidity int, decoded_PPM int, air_pressure int);")

    # Insert SQL query
    cur.execute(f"INSERT INTO {decoded_device} (datetime, position, temperature, humidity, PPM, air_pressure) VALUES (CURRENT_TIMESTAMP AT TIME ZONE 'CEST', 1, {decoded_temp}, {decoded_humidity}, {decoded_PPM}, {decoded_pressure});")

elif (jsonBody["uplink_message"]["f_port"] == 2):
    decoded_device_route = decoded_device + "route"

    list_of_uint16_t = []
    for i in range(len(jsonBody["uplink_message"]["decoded_payload"])):
        list_of_uint16_t.append(jsonBody["uplink_message"]["decoded_payload"][str(i)]["0"])
        list_of_uint16_t[-1] += jsonBody["uplink_message"]["decoded_payload"][str(i)]["1"] << 8

    list_of_uint16_t = str(list_of_uint16_t).replace("[", "{").replace("]", "}")
    print(list_of_uint16_t)

    try:
        cur.execute(f"CREATE TABLE IF NOT EXISTS {decoded_device_route} (datetime TIMESTAMPTZ NOT NULL, route integer[] NOT NULL);")
        cur.execute(f"INSERT INTO {decoded_device_route} (datetime, route) VALUES (CURRENT_TIMESTAMP AT TIME ZONE 'CEST', '{list_of_uint16_t}');")
    except Exception as inst:
        print(inst)
        
elif (jsonBody["uplink_message"]["f_port"] == 3):
    decoded_device_error = decoded_device + "error"

    # Byte	    Bit	    Severity	Component	Wat
    # Byte 0	Bit 0	Error	    Sensoren	BME280 sensor kapot
    # Byte 0	Bit 1	Warning	    Sensoren	temperatuur out of safe range
    # Byte 0	Bit 2	Warning	    Sensoren	luchtvochtigheid out of safe range
    # Byte 0	Bit 3	Warning	    Sensoren	luchtdruk out of safe range
    # Byte 0	Bit 4	Error	    Sensoren	SCD30 sensor kapot
    # Byte 0	Bit 5	Warning	    Sensoren	CO2 out of safe range
    # Byte 0	Bit 6	Error	    Sensoren	SPS30 sensor kapot
    # Byte 0	Bit 7	Warning	    Sensoren	PM1.0 out of safe range
    # Byte 1	Bit 0	Warning	    Sensoren	PM2.5 out of safe range
    # Byte 1	Bit 1	Warning	    Sensoren	PM10 out of safe range
    # Byte 1	Bit 2	Error	    Sensoren	Batterij kapot
    # Byte 1	Bit 3	Warning	    Sensoren	Batterij low
    # Byte 1	Bit 4	Error	    Locatie	    Locatie not found
    # Byte 1	Bit 5	Warning	    Locatie	    Locatie Inaccurate
    # Byte 1	Bit 6	Warning	    Locatie	    Locatie onveranderd (staan stil)
    # Byte 1	Bit 7	Error	    Sensoren	Reading timeout

    messages = []
    if (jsonBody["uplink_message"]["decoded_payload"]["0"] & 0b00000001):
        messages.append({"discription":"BME280 sensor kapot", "severity":"error", "component":"sensoren"})
    if (jsonBody["uplink_message"]["decoded_payload"]["0"] & 0b00000010):
        messages.append({"discription":"temperatuur out of safe range", "severity":"warning", "component":"sensoren"})
    if (jsonBody["uplink_message"]["decoded_payload"]["0"] & 0b00000100):
        messages.append({"discription":"luchtvochtigheid out of safe range", "severity":"warning", "component":"sensoren"})
    if (jsonBody["uplink_message"]["decoded_payload"]["0"] & 0b00001000):
        messages.append({"discription":"luchtdruk out of safe range", "severity":"warning", "component":"sensoren"})
    if (jsonBody["uplink_message"]["decoded_payload"]["0"] & 0b00010000):
        messages.append({"discription":"SCD30 sensor kapot", "severity":"error", "component":"sensoren"})
    if (jsonBody["uplink_message"]["decoded_payload"]["0"] & 0b00100000):
        messages.append({"discription":"CO2 out of safe range", "severity":"warning", "component":"sensoren"})
    if (jsonBody["uplink_message"]["decoded_payload"]["0"] & 0b01000000):
        messages.append({"discription":"SPS30 sensor kapot", "severity":"error", "component":"sensoren"})
    if (jsonBody["uplink_message"]["decoded_payload"]["0"] & 0b10000000):
        messages.append({"discription":"PM1.0 out of safe range", "severity":"warning", "component":"sensoren"})
    if (jsonBody["uplink_message"]["decoded_payload"]["1"] & 0b00000001):
        messages.append({"discription":"PM2.5 out of safe range", "severity":"warning", "component":"sensoren"})
    if (jsonBody["uplink_message"]["decoded_payload"]["1"] & 0b00000010):
        messages.append({"discription":"PM10 out of safe range", "severity":"warning", "component":"sensoren"})
    if (jsonBody["uplink_message"]["decoded_payload"]["1"] & 0b00000100):
        messages.append({"discription":"Batterij kapot", "severity":"error", "component":"sensoren"})
    if (jsonBody["uplink_message"]["decoded_payload"]["1"] & 0b00001000):
        messages.append({"discription":"Batterij low", "severity":"warning", "component":"sensoren"})
    if (jsonBody["uplink_message"]["decoded_payload"]["1"] & 0b00010000):
        messages.append({"discription":"Locatie not found", "severity":"error", "component":"locatie"})
    if (jsonBody["uplink_message"]["decoded_payload"]["1"] & 0b00100000):
        messages.append({"discription":"Locatie Inaccurate", "severity":"warning", "component":"locatie"})
    if (jsonBody["uplink_message"]["decoded_payload"]["1"] & 0b01000000):
        messages.append({"discription":"Locatie onveranderd (staan stil)", "severity":"warning", "component":"locatie"})
    if (jsonBody["uplink_message"]["decoded_payload"]["1"] & 0b10000000):
        messages.append({"discription":"Reading timeout", "severity":"error", "component":"sensoren"})
    
    cur.execute(f"CREATE TABLE IF NOT EXISTS {decoded_device_error} (datetime TIMESTAMPTZ NOT NULL, message VARCHAR(255) NOT NULL, severity VARCHAR(255) NOT NULL, component VARCHAR(255) NOT NULL);")

    for message in messages:
        cur.execute(f"INSERT INTO {decoded_device_error} (datetime, message, severity, component) VALUES (CURRENT_TIMESTAMP AT TIME ZONE 'CEST', '{message['discription']}', '{message['severity']}', '{message['component']}');")
    

# Commit the changes to the database
conn.commit()
cur.close()