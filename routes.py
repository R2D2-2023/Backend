from sqlalchemy import insert, delete, and_, or_, not_
from flask import Flask, redirect, render_template, request, send_from_directory, url_for
from datetime import datetime, timedelta
import os
import re
from flask import jsonify
import cv2
import numpy as np

# The import must be done after db initialization due to circular import issue
from models import SensorData, aabbccddeeff7778, EmailAddress, aabbccddeeff7778error, LocOnly, SensorDataWithLoc
from flask_login import login_required, current_user, login_user, logout_user
from models import UserModel

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
        first_datapoint = request.args.get('first_datapoint')    
        location = request.args.get('location')       
        if last_datapoint is None or first_datapoint is None or location is None:
            return "Not the right parameters are given."
        loc_arr = []
        location = int(location)
        for i in range( 0, 10):
            if location >> i & 1:
                loc_arr.append(i+1)

        try:
            last_datapoint = datetime.strptime(last_datapoint, '%Y-%m-%dT%H:%M:%S.%f')
        except:
            last_datapoint = datetime.strptime(last_datapoint[:-6], '%Y-%m-%dT%H:%M:%S.%f')
        first_datapoint = datetime.strptime(first_datapoint, '%Y-%m-%dT%H:%M:%S.%f')
        # query for new data with and location and datetime after last_datapoint. return all columns
        raw_data = SensorDataWithLoc.query.order_by(SensorDataWithLoc.datetime.desc()).filter(SensorDataWithLoc.datetime > last_datapoint, SensorDataWithLoc.datetime < first_datapoint, SensorDataWithLoc.zone.in_(loc_arr)).all()
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
        data['co2'] = [data.co2 for data in final_data]
        data['pressure'] = [data.pressure for data in final_data]
        data['pm10'] = [data.pm10 for data in final_data]
        data['pm25'] = [data.pm25 for data in final_data]
        data['pm100'] = [data.pm100 for data in final_data]
        if timestamp == []:
            return "No new data available."
        
        return jsonify(timestamp=timestamp, data=data)
    
    @app.route('/get_recent_data')	
    def get_recent_data():
        sensordata = SensorDataWithLoc.query.order_by(SensorDataWithLoc.datetime.desc()).limit(1).all()
        timestamp = sensordata[0].datetime.strftime("%H:%M")
        data = {}
        data['temperature'] = sensordata[0].temperature
        data['humidity'] = sensordata[0].humidity
        data['co2'] = sensordata[0].co2
        data['pressure'] = sensordata[0].pressure
        data['pm'] = sensordata[0].pm10 + sensordata[0].pm25 + sensordata[0].pm100
        return jsonify(timestamp=timestamp, data=data)
    
    @app.route('/get_email_data')
    def get_email_data():
        return [email.adress for email in EmailAddress.query.all()]

    @app.route('/test_is_data_avalable')
    def test_is_data_avalable():
        SensorDataWithLoc.query.order_by(SensorDataWithLoc.datetime.desc()).limit(100).all()
        return "ok"

    # Routes for html pages
    @app.route('/')
    @login_required
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
        if min_temp is None:
            min_temp = 15
        if max_temp is None:
            max_temp = 30
        if min_temp == max_temp:
            max_temp += 1

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
        
        outline = -1
        for i, color in enumerate(colors):
            # Teken een cirkel op de heatmap-overlay op de bijbehorende positie (x, y)
            # cv2.circle(heatmap_overlay, (zones[i][0], zones[i][1]), radius, color, outline)
            cv2.rectangle(heatmap_overlay, (zones[i][0], zones[i][1]),(zones[i][0]+steps_x, zones[i][1]+steps_y), color, outline)  

        # plaatsing circle waar de auto nu is !!! locatie word nog niet goed berekend !!!
        # circle staat nu net niet op de kaart dus kan zijn dat je hem niet ziet
        max_x = 232
        max_y = 65 

        cv2.circle(heatmap_overlay, (int(heatmap_overlay.shape[1]/max_x * last_location[0].x_loc), int(heatmap_overlay.shape[0]/max_y * last_location[0].y_loc)), 100, (255,255,255), outline)

        # Combineer de originele afbeelding met de heatmap-overlay
        alpha = 0.5
        beta = 0.5
        combined_image = cv2.addWeighted(heatmap_overlay, alpha, image, beta, 0)

        # Bewaar of toon de gegenereerde afbeelding
        cv2.imwrite('static/images/kaart4de-verdieping-solid_heatmap.png', combined_image)

        return render_template('index.html')
    
 
    @app.route('/charts')
    @login_required
    def charts():
        print('Request for charts page received')
        return render_template('charts.html')

    
    @app.route('/logout')
    @login_required
    def lege_pagina():
        logout_user()  # Logout the current user
        return redirect('/login')

    @app.route('/email', methods = ['GET', 'POST'])
    @login_required
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
            print(message)
            return render_template('email.html', value=message)
            
        
        elif request.method == 'GET':
            return render_template("email.html", value="")
    
    @app.route('/get_latest_entry', methods=['GET'])
    def get_all_notifs():
        all_entries = db.session.query(aabbccddeeff7778error).all()
        data_list = []
        for entry in all_entries:
            data = {
                'id': entry.id,
                'datetime': entry.datetime,
                'message': entry.message,
                'severity': entry.severity,
                'component': entry.component
            }
            data_list.append(data)
        return jsonify(data=data_list)
   
    # Routes for static files
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                'favicon.ico', mimetype='image/vnd.microsoft.icon')
    
    @app.route('/login', methods = ['POST', 'GET'])
    def login():
        if current_user.is_authenticated:
            return redirect('/')
        
        if request.method == 'POST':
            email = request.form['email']
            user = UserModel.query.filter_by(email = email).first()
            if user is not None and user.check_password(request.form['password']):
                login_user(user)
                return redirect('/')
        
        return render_template('login.html')
 
    @app.route('/register', methods=['POST', 'GET'])
    def register():
        if current_user.is_authenticated:
            return redirect('/')

        if request.method == 'POST':
            email = request.form['email']
            username = request.form['username']
            password = request.form['password']

            if UserModel.query.filter_by(email=email).first():
                return 'Email already exists'
            if UserModel.query.filter_by(username=username).first():
                return 'Username already exists'

            user = UserModel(email=email, username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return redirect('/login')
        
        return render_template('register.html')
 
