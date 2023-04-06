from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import validates

from app import db


class SensorData(db.Model):
    __tablename__ = 'sensor_data'
    datetime = Column(DateTime, primary_key=True)
    co2 = Column(Integer)
    humidity = Column(Integer)
    pressure = Column(Integer)
    temperature = Column(Integer)

    def __str__(self):
        return self.name