
from flask import Flask, redirect, render_template, request, send_from_directory, url_for
from datetime import datetime, timedelta
import os
from flask import jsonify
import cv2

# The import must be done after db initialization due to circular import issue
from models import SensorData, aabbccddeeff7778, aabbccddeeff7778route

sensordata = None
cachetime = None

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

    @app.route('/drawn_route')
    def drawn_route():
        # Get the most recent route from the database: aabbccddeeff7778route
        route = aabbccddeeff7778route.query.order_by(aabbccddeeff7778route.datetime.desc()).first()
        route = route.route
        # Decompress the route
        # [4352,13090,21828,30566,39304] to { "0": [0,17], "1": [34,51], "2": [68,85], "3": [102,119], "4": [136,153] }
        # by splitting the uint16_t into two uint8_t 
        route = {str(i): [route[i] & 0xFF, route[i] >> 8] for i in range(len(route))}
        # Draw the route on the map: plategrond4.png
        img = cv2.imread('static/images/plategrond4.png')

        # Validate that the image is loaded
        if img is None:
            return "Image not found"

        # Scale the route to the size of the image
        max_x = img.shape[1]
        max_y = img.shape[0]
        max_route = 255
        for i in range(len(route)):
            route[str(i)][0] = int(route[str(i)][0] / max_route * max_x)
            route[str(i)][1] = int(route[str(i)][1] / max_route * max_y)
        
        # Draw the route
        for i in range(len(route) - 1):
            img = cv2.line(img, tuple(route[str(i)]), tuple(route[str(i+1)]), (0,0,255), 8)
            # Add point to the route
            img = cv2.circle(img, tuple(route[str(i)]), 10, (255,0,0), -1)
            # # Add number to the point
            # img = cv2.putText(img, str(i), tuple(route[str(i)]), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,0), 2, cv2.LINE_AA)
        
        # Add last point to the route
        img = cv2.circle(img, tuple(route[str(len(route) - 1)]), 10, (255,0,0), -1)
        # img = cv2.putText(img, str(len(route) - 1), tuple(route[str(len(route) - 1)]), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,0), 2, cv2.LINE_AA)
        
        # Save the image
        cv2.imwrite('static/images/plategrond4_route.png', img)
        return render_template('drawn_route.html')
    
    @app.route('/lege_pagina')
    def lege_pagina():
        return render_template('lege_pagina.html')

    # Routes for static files
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                'favicon.ico', mimetype='image/vnd.microsoft.icon')
