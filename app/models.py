# Data Models
# (C) Poren Chiang 2020

import dataclasses
from ntuweather import Weather
from sqlalchemy import Table, Column, DateTime, Integer, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class WeatherData(Base):
    """Represents a weather record saved in the database."""

    __tablename__ = 'weather_data'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime(timezone=True), index=True)
    temperature = Column(Float)
    pressure = Column(Float)
    humidity = Column(Float)
    wind_speed = Column(Float)
    wind_direction = Column(Integer)
    rain_per_hour = Column(Float)
    rain_per_minute = Column(Float)
    ground_temperature = Column(Float)

    def __repr__(self):
        return f"<WeatherData(date='{self.date.isoformat()}', temperature={self.temperature})>"

    def weather(self):
        self_dict = {field.name: self.__dict__[field.name] for field in dataclasses.fields(Weather)}

    @classmethod
    def fromweather(cls, weather):
        return cls(**dataclasses.asdict(weather))
