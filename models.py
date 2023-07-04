from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, DECIMAL
import os
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from sqlalchemy.orm import validates
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager
from flask_login import LoginManager


# Initialize the database connection
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
login = LoginManager()


def config_db(app):
    # Initialize the database connection
    app.config.update(
        SQLALCHEMY_DATABASE_URI=app.config.get('DATABASE_URI'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY = os.urandom(32)
    )
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    return db, migrate, csrf

def config_login(app):
    login.init_app(app)
    login.login_view = 'login'
    
 
class SensorData(db.Model):
    __tablename__ = 'sensor_data'
    datetime = Column(DateTime, primary_key=True)
    co2 = Column(Integer)
    humidity = Column(Integer)
    pressure = Column(Integer)
    temperature = Column(DECIMAL(3,1))
    location = Column(Integer)

    def __str__(self):
        return self.name
    

class LocOnly(db.Model):
    __tablename__ = 'locatie_only'
    datetime = Column(DateTime, primary_key=True)
    x_loc = Column(Integer)
    y_loc = Column(Integer)    

    def __str__(self):
        return self.name
    
    
class SensorDataWithLoc(db.Model):
    __tablename__ = 'sensor_data_with_foreign_location'
    datetime = Column(DateTime, ForeignKey('locatie_only.datetime'), primary_key=True)
    co2 = Column(Integer)
    humidity = Column(Integer)
    pressure = Column(Integer)
    temperature = Column(DECIMAL(3,1))
    pm10 = Column(Integer)
    pm25 = Column(Integer)
    pm100 = Column(Integer)
    zone = Column(Integer)
    
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
    
class aabbccddeeff7778error(db.Model):
    __tablename__ = 'aabbccddeeff7778error'
    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime)
    message = Column(String)
    severity = Column(String)
    component = Column(String)

    def __str__(self):
        return self.name

class UserModel(UserMixin, db.Model):
    __tablename__ = 'users'
 
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True)
    username = db.Column(db.String(100))
    password_hash = db.Column(db.String())
 
    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
     
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)
    
    def get_id(self):
        return str(self.id)

 
@login.user_loader
def load_user(id):
    return UserModel.query.get(int(id))