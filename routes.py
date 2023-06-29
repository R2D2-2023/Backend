from sqlalchemy import insert, delete
from flask import Flask, redirect, render_template, request, send_from_directory, url_for
from datetime import datetime, timedelta
import os
import re
from flask import jsonify
import cv2
import numpy as np

# The import must be done after db initialization due to circular import issue
from models import SensorData, aabbccddeeff7778, EmailAddress, LocOnly, SensorDataWithLoc

sensordata = None
cachetime = None
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

def validate_mail(mail_adress):
    if (re.fullmatch(regex, mail_adress)):
        return
    else:
        return False

def config_route(app, csrf, db):

    # Routes for API's   
    @app.route('/get_new_data')
    def get_new_data():
        last_datapoint = request.args.get('last_datapoint')
        location = request.args.get('location')
        if last_datapoint is None or location is None:
            return "Not the right parameters are given."
        last_datapoint = datetime.strptime(last_datapoint, '%Y-%m-%dT%H:%M:%S.%f')
        # query for new data with and location and datetime after last_datapoint. return all columns
        raw_data = SensorData.query.order_by(SensorData.datetime.desc()).filter(SensorData.datetime > last_datapoint, SensorData.location == location).all()
        raw_data.reverse()
        # if len(raw_data) == 0:
        #     return jsonify(timestamp=[], data={})
        final_data = []
        if len(raw_data) > 1000:
            filter_step_size = len(raw_data) / 1000
            filter_step_count = 0
            for data in raw_data:
                filter_step_count += 1
                if filter_step_count > filter_step_size:
                    filter_step_count -= filter_step_size
                    final_data.append(data)
            print(len(raw_data), len(final_data))
        else:
            final_data = raw_data
        

        timestamp = [data.datetime.isoformat() for data in final_data]
        data = {}
        data['temperature'] = [data.temperature for data in final_data]
        data['humidity'] = [data.humidity for data in final_data]
        # data['co2'] = [data.ppm for data in final_data]
        data['co2'] = [data.co2 for data in final_data]
        data['pressure'] = [data.pressure for data in final_data]
        # data['pressure'] = [data.air_pressure for data in final_data]
        if timestamp == []:
            return "No new data available."
        
        return jsonify(timestamp=timestamp, data=data)
    
    @app.route('/get_recent_data')	
    def get_recent_data():
        limit = request.args.get('limit')
        location = request.args.get('location')
        # global sensordata
        # global cachetime 
        curr_time = datetime.now()
        # disable = False
        # if sensordata is None or (datetime.now() - cachetime).total_seconds() > 30 or int(limit) > len(sensordata) or disable:
        sensordata = SensorData.query.order_by(SensorData.datetime.desc()).filter(SensorData.location == location).limit(limit).all()
        # cachetime = curr_time
        timestamp = [data.datetime.strftime("%H:%M") for data in sensordata]
        data = {}
        data['temperature'] = [data.temperature for data in sensordata]
        data['humidity'] = [data.humidity for data in sensordata]
        data['co2'] = [data.co2 for data in sensordata]
        data['pressure'] = [data.pressure for data in sensordata]
        print("get_recent_sensor_readings time taken", datetime.now() - curr_time)
        return jsonify(timestamp=timestamp, data=data)
    
    @app.route('/get_email_data')
    def get_email_data():

        return [data.address for data in EmailAddress]



    @app.route('/test_is_data_avalable')
    def test_is_data_avalable():
        SensorData.query.order_by(SensorData.datetime.desc()).limit(100).all()
        return "ok"

    # Routes for html pages
    @app.route('/')
    def index():
        print('Request for index page received')

        # Haal de temperatuurgegevens op uit de SQL-database
        last_location = LocOnly.query.order_by(LocOnly.datetime.desc()).limit(1).all()
        # per locatie en dan de temperatuur index 0 is zone 0 enz..
        sens_data = []
        for i in range(1,11):
            sens_data.append(SensorDataWithLoc.query.order_by(SensorDataWithLoc.datetime.desc()).filter(SensorDataWithLoc.zone == i).limit(1).all())
        
        i = 0
        temp = []
        for zone_data in sens_data:
            if zone_data:
                sensor_data = zone_data[0]
                temp.append(sensor_data.temperature)
                print(i)
                i += 1


        # Definieer de kleuren voor de temperatuurgradient
        color_min = (0, 0, 255)  # Blauw (lage temperatuur)
        color_max = (255, 0, 0)  # Rood (hoge temperatuur)

        min_temp = min(temp)
        max_temp = max(temp)

        intensities = []
        colors = []
        for temperature in temp:
            # logica om de intensiteit te berekenen op basis van de temperatuur
            intensity = (temperature - min_temp) / (max_temp - min_temp)
            # intensity = (temperature-10)*12  # Bereken de intensiteit op basis van de temperatuur
            intensities.append(intensity)

            # Bereken de kleur op basis van de temperatuurwaarde en de kleurengradient
            color = tuple(int(c_min + (c_max - c_min) * intensity) for c_min, c_max in zip(color_min, color_max))
            colors.append(color)



        # Laad de afbeelding
        image = cv2.imread('static/images/kaart4de-verdieping-solid.png', cv2.IMREAD_UNCHANGED)
        # Maak een lege heatmap-overlay
        heatmap_overlay = np.zeros_like(image)

        # # zone's waneer je circles gebruikt     
        # steps_y = int(heatmap_overlay.shape[0]/5)
        # steps_x = int(heatmap_overlay.shape[1]/10)
        # zones = [
        #     [steps_x*1, steps_y*1],
        #     [steps_x*3, steps_y*1],
        #     [steps_x*5, steps_y*1],
        #     [steps_x*7, steps_y*1],
        #     [steps_x*9, steps_y*1],
        #     [steps_x*1, steps_y*4],
        #     [steps_x*3, steps_y*4],
        #     [steps_x*5, steps_y*4],
        #     [steps_x*7, steps_y*4],
        #     [steps_x*9, steps_y*4]]

        # zone's bij het gebruik van rectangles
        steps_x = int(heatmap_overlay.shape[1]/5)
        steps_y = int(heatmap_overlay.shape[0]/2)
        zones = [
            [steps_x*0, steps_y*0],
            [steps_x*1, steps_y*0],
            [steps_x*2, steps_y*0],
            [steps_x*3, steps_y*0],
            [steps_x*4, steps_y*0],
            [steps_x*0, steps_y*1],
            [steps_x*1, steps_y*1],
            [steps_x*2, steps_y*1],
            [steps_x*3, steps_y*1],
            [steps_x*4, steps_y*1]]
        
        i = 0
        outline = -1
        for color in colors:
            # Teken een cirkel op de heatmap-overlay op de bijbehorende positie (x, y)
            # cv2.circle(heatmap_overlay, (zones[i][0], zones[i][1]), radius, color, outline)
            cv2.rectangle(heatmap_overlay, (zones[i][0], zones[i][1]),(zones[i][0]+steps_x, zones[i][1]+steps_y), color, outline)
            print(i)
            i += 1

        # plaatsing circle waar de auto nu is !!! locatie word nog niet goed berekend !!!
        # circle staat nu net niet op de kaart dus kan zijn dat je hem niet ziet
        cv2.circle(heatmap_overlay, (int(heatmap_overlay.shape[1]/100*last_location[0].x_loc), int(heatmap_overlay.shape[0]/100*last_location[0].y_loc)), 100, (255,255,255), outline)

        # Combineer de originele afbeelding met de heatmap-overlay
        alpha = 0.5
        beta = 0.5
        combined_image = cv2.addWeighted(heatmap_overlay, alpha, image, beta, 0)

        # Bewaar of toon de gegenereerde afbeelding
        cv2.imwrite('static/images/kaart4de-verdieping-solid_heatmap.png', combined_image)

        return render_template('index.html')



    @app.route('/charts')
    def charts():
        print('Request for charts page received')
        return render_template('charts.html')

    @app.route('/lege_pagina')
    def lege_pagina():
        print('Request for lege_pagina page received')
        return render_template('lege_pagina.html')

    @app.route('/email', methods = ['GET', 'POST'])
    def email():
        if request.method == 'POST':
            message = ""
            newMail = EmailAddress(adress=request.form.get("email"))
            if (len(newMail.adress) > 255):
                message = "The input has too many characters"
                return render_template('email.html', value=message)
            
            submitButton = request.form.get("submit")
            removeButton = request.form.get("remove")

            if (validate_mail(newMail.adress) == False):
                message = "Not a valid mail adress"
                return render_template("email.html", value=message)


            if submitButton is not None:        
                try:
                    db.session.add(newMail)
                    db.session.commit()
                    message = "Given e-mail has been added to our database" 
                except:
                    message = "Your e-mail is already in our database"
            
            elif removeButton is not None:
                if db.session.query(EmailAddress.adress).filter_by(adress=newMail.adress).first() is not None:
                    try:
                        EmailAddress.query.filter_by(adress=newMail.adress).delete()
                        db.session.commit()
                        message = "The given e-mail has been removed from our database"
                    except:
                        message = "An error occurred while removing your mail adress"
                else:
                    message = "Mail adress not found in our database"
            else:
                print("Invalid input")
            return render_template('email.html', value=message)
            
        
        elif request.method == 'GET':
            return render_template("email.html", value="")

    # Routes for static files
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                'favicon.ico', mimetype='image/vnd.microsoft.icon')
