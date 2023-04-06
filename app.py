import os
from datetime import datetime
from flask import Flask, redirect, render_template, request, send_from_directory, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
# from collections import Counter



app = Flask(__name__) #static_folder='static'

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

if __name__ == '__main__':
   app.run()




# om de server te laten configureren dat jij het bent of zo iets... google het
csrf = CSRFProtect(app)

# WEBSITE_HOSTNAME exists only in production environment
if 'WEBSITE_HOSTNAME' not in os.environ:
    # local development, where we'll use environment variables
    print("Loading config.development and environment variables from .env file.")
    app.config.from_object('azureproject.development')
else:
    # production
    print("Loading config.production.")
    app.config.from_object('azureproject.production')

app.config.update(
    SQLALCHEMY_DATABASE_URI=app.config.get('DATABASE_URI'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

# Initialize the database connection
db = SQLAlchemy(app)

# Enable Flask-Migrate commands "flask db init/migrate/upgrade" to work
migrate = Migrate(app, db)

# The import must be done after db initialization due to circular import issue
from models import SensorData



@app.context_processor
def utility_processor():
    def get_recent_sensor_readings(index, limit):
        sensordata = SensorData.query.order_by(SensorData.datetime.desc()).limit(limit).all()
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
        return lst
    
    return dict(get_recent_sensor_readings=get_recent_sensor_readings)
