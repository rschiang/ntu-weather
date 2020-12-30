# Database utilities
# (C) Poren Chiang 2020

import os
from contextlib import contextmanager
from datetime import datetime, time
from ntuweather import Weather
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, WeatherData

# Configure database
engine = create_engine(os.environ.get('DATABASE_URL'))
Session = sessionmaker(bind=engine)

@contextmanager
def db_session():
    """Wraps a transactional scope around a newly created session."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

def initialize_db():
    """Initialize database, creating all tables if they don’t exist."""
    Base.metadata.create_all(engine)

def query_weather_data(session):
    """Returns a default query for WeatherData."""
    return session.query(WeatherData).order_by(WeatherData.date.desc())

def invalid_weather(date=None):
    """Initializes an invalid Weather class, optionally with a Date."""
    return Weather(date=date,
        temperature=0.0,
        pressure=0.0,
        humidity=0.0,
        wind_speed=0.0,
        wind_direction=0,
        rain_per_hour=0.0,
        rain_per_minute=0.0,
        ground_temperature=0.0,
        provider='',
        valid=False)

def today(tz):
    """Gets the timezone-aware midnight of a specific timezone."""
    now_date = datetime.now(tz)
    return tz.localize(datetime.combine(now_date.date(), time()))
