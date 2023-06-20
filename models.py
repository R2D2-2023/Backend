from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
import os
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from sqlalchemy.orm import validates

# Initialize the database connection
db = SQLAlchemy()
migrate = Migrate()
# csrf = CSRFProtect()

def config_db(app):
    # Initialize the database connection
    app.config.update(
        SQLALCHEMY_DATABASE_URI=app.config.get('DATABASE_URI'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY = os.urandom(32)
    )
    db.init_app(app)
    migrate.init_app(app, db)
    # csrf.init_app(app)
    return db, migrate

    
class SensorData(db.Model):
    __tablename__ = 'sensor_data'
    datetime = Column(DateTime, primary_key=True)
    co2 = Column(Integer)
    humidity = Column(Integer)
    pressure = Column(Integer)
    temperature = Column(Integer)
    location = Column(Integer)

    def __str__(self):
        return self.name
 

class aabbccddeeff7778(db.Model):
    __tablename__ = 'aabbccddeeff7778'
    datetime = Column(DateTime, primary_key=True)
    ppm = Column(Integer)
    humidity = Column(Integer)
    air_pressure = Column(Integer)
    temperature = Column(Integer)
    position = Column(Integer)

    def __str__(self):
        return self.name
    

class EmailAddress(db.Model):
    __tablename__ = 'emailaddress'
    adress = Column(String, primary_key=True)

    def __str__(self):
        return self.name
    