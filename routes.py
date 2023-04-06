
from flask import Flask, redirect, render_template, request, send_from_directory, url_for
from datetime import datetime
import os
from flask import jsonify

# The import must be done after db initialization due to circular import issue
from models import SensorData

sensordata = None
cachetime = None

def config_route(app, csrf, db):

    # Routes for API's   
    @app.route('/get_new_data')
    def get_new_data():
        last_datapoint = request.args.get('last_datapoint')
        if last_datapoint is None:
            return ""
        location = request.args.get('location')
        last_datapoint = datetime.strptime(last_datapoint, '%Y-%m-%dT%H:%M:%S.%f')
        # query for new data with and location and datetime after last_datapoint. return all columns
        new_data = SensorData.query.order_by(SensorData.datetime.desc()).filter(SensorData.datetime > last_datapoint, SensorData.location == location).all()
        timestamp = [data.datetime.isoformat() for data in new_data]
        data = {}
        data['temperature'] = [data.temperature for data in new_data]
        data['humidity'] = [data.humidity for data in new_data]
        data['co2'] = [data.co2 for data in new_data]
        data['pressure'] = [data.pressure for data in new_data]
        
        return jsonify(timestamp=timestamp, data=data)
        

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

    @app.context_processor
    def utility_processor():
        def get_recent_sensor_readings(index, limit):
            global sensordata
            global cachetime 
            curr_time = datetime.now()
            disable = False
            if sensordata is None or (datetime.now() - cachetime).total_seconds() > 30 or limit > len(sensordata) or disable:
                sensordata = SensorData.query.order_by(SensorData.datetime.desc()).limit(limit).all()
                cachetime = curr_time
            if index == 0:
                lst = [data.datetime.isoformat() for data in sensordata]
            elif index == 1:
                lst = [data.temperature for data in sensordata]
            elif index == 2:
                lst = [data.co2 for data in sensordata]
            elif index == 3:
                lst = [data.humidity for data in sensordata]
            elif index == 4:
                lst = [data.pressure for data in sensordata]
            else:
                return None
            print("get_recent_sensor_readings time taken", datetime.now() - curr_time)
            return lst
         
        return dict(get_recent_sensor_readings=get_recent_sensor_readings)

    # Routes for static files
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                'favicon.ico', mimetype='image/vnd.microsoft.icon')
