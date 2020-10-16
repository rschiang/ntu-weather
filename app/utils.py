# Database utilities
# (C) Poren Chiang 2020

from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, WeatherData

# Configure database
engine = create_engine(os.environ.get('DATABASE_URL'))
Base.metadata.create_all(engine)
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

def query_weather_data(session):
    return session.query(WeatherData).order_by(WeatherData.date.desc())
