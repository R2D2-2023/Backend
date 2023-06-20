from sqlalchemy import insert, delete
from flask import Flask, redirect, render_template, request, send_from_directory, url_for
from datetime import datetime, timedelta
import os
from flask import jsonify

# The import must be done after db initialization due to circular import issue
from models import SensorData, aabbccddeeff7778, EmailAddress

sensordata = None
cachetime = None


def config_route(app, db):

    # Routes for API's   
    @app.route('/get_new_data')
    def get_new_data():
        last_datapoint = request.args.get('last_datapoint')
        location = request.args.get('location')
        if last_datapoint is None or location is None:
            return "Not the right parameters are given."
        last_datapoint = datetime.strptime(last_datapoint, '%Y-%m-%dT%H:%M:%S.%f')
        # query for new data with and location and datetime after last_datapoint. return all columns
        new_data = SensorData.query.order_by(SensorData.datetime.desc()).filter(SensorData.datetime > last_datapoint, SensorData.location == location).all()
        # new_data = aabbccddeeff7778.query.order_by(aabbccddeeff7778.datetime.desc()).filter(aabbccddeeff7778.datetime > last_datapoint, aabbccddeeff7778.position == location).all()
        new_data.reverse()
        filter_data = []
        # if len(new_data) == 0:
        #     return jsonify(timestamp=[], data={})
        # for i in range(0, len(new_data), (len(new_data) // max_data)):
        #     filter_data.append(new_data[i])
        timestamp = [data.datetime.isoformat() for data in new_data]
        data = {}
        data['temperature'] = [data.temperature for data in new_data]
        data['humidity'] = [data.humidity for data in new_data]
        # data['co2'] = [data.ppm for data in filter_data]
        data['co2'] = [data.co2 for data in new_data]
        data['pressure'] = [data.pressure for data in new_data]
        # data['pressure'] = [data.air_pressure for data in new_data]
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
        return render_template('index.html')

    @app.route('/charts')
    def charts():
        print('Request for charts page received')
        return render_template('charts.html')

    @app.route('/lege_pagina')
    def lege_pagina():
        print('Request for lege_pagina page received')
        return render_template('lege_pagina.html')
    
    @app.route('/email')
    def email():
        print('Request for email page received')
        return render_template('email.html')

    @app.route('/submit_email', methods = ['POST'])
    def submit_email():
        newMail = EmailAddress(adress=request.form.get("email"))
        submitButton = request.form.get("submit")
        removeButton = request.form.get("remove")

        if submitButton is not None:
            print("Submit")        
            try:
                db.session.add(newMail)
                db.session.commit()
            except:
                print("Given mail adress is already in the database")
        elif removeButton is not None:
            if db.session.query(EmailAddress.adress).filter_by(adress=newMail.adress).first() is not None:
                print("Adress found")
                try:
                    print("Removed the adress form our database")
                    EmailAddress.query.filter_by(adress=newMail.adress).delete()
                    db.session.commit()
                except:
                    print("An error occurred while removing your mail adress")
            else:
                print("Mail adress not found in our database")
        else:
            print("Invalid input")
        return redirect(url_for('email'))

    # Routes for static files
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                'favicon.ico', mimetype='image/vnd.microsoft.icon')
