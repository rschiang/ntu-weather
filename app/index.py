#!/usr/bin/env python3
import os
from bottle import Bottle, view
from datetime import datetime, timedelta
from ntuweather.providers import NTUASProvider
from pytz import timezone
from .models import WeatherData, metadata
from .utils import db_session, query_weather

app = Bottle()
debug_switch = (os.environ.get('DEBUG') == '1')
tz = timezone('Asia/Taipei')
provider = NTUASProvider()

@app.route('/', template='index')
def index():
    try:
        with db_session() as session:
            weather = get_or_fetch_weather(session, max_age=900)
            daily_report = aggregate_daily_report(session)

        return {'weather': weather, 'daily': daily_report}
    except ValueError:
        return {'error': 'data_unavailable'}
    except:
        return {'error': 'server_unavailable'}

@app.route('/api')
def api():
    try:
        with db_session() as session:
            weather = get_or_fetch_weather(session, max_age=300)
        return {
            'date': weather.date.isoformat(),
            'temperature': weather.temperature,
            'pressure': weather.pressure,
            'humidity': weather.humidity,
            'wind_speed': weather.wind_speed,
            'wind_direction': weather.wind_direction,
            'rain': weather.rain_per_hour,
            'rain_minute': weather.rain_per_minute,
            'temp_ground': weather.ground_temperature,
            'provider': weather.provider,
        }
    except ValueError:
        return {'error': 'data_unavailable'}
    except:
        return {'error': 'server_unavailable'}

def get_cached_weather(session, max_age, from_date=None):
    """Returns recently acquired weather information, if available."""
    weather_data = query_weather_data(session).first()
    if weather_data:
        # Calculate the time difference to see if it’s still recent
        now_date = from_date or datetime.now(tz)
        latest_date = weather_data.date.astimezone(tz)
        if (now_date - latest_date).total_seconds() < max_age:
            # Convert to common Weather class
            weather = weather_data.weather()
            # Replace with timezone aware date and provider
            weather.date = latest_date
            weather.provder = provider.name
            return weather
    return None

def get_or_fetch_weather(session, max_age):
    """Loads recently acquired weather information or retrieves a new one."""
    weather = get_cached_weather(session, max_age)
    if not weather:
        weather = provider.get()
        weather_data = WeatherData.fromweather(weather)
        session.add(weather_data)
        session.commit()
    return weather

def aggregate_daily_report(session):
    """Queries and returns a list of weather records in the past 24 hours."""
    weather_list = []
    date = datetime.now(tz)
    delta = timedelta(hours=3)

    # Step through each time gap and seek closest record in a 30 min window.
    for _ in range(8):
        date -= delta
        weather = get_cached_weather(session, max_age=1800, from_date=date)
        weather_list.append(weather or {'date': date, 'error': 'data_unavailable'})

    # Order by oldest
    return reversed(weather_list)

if __name__ == '__main__':
    app.run(debug=debug_switch, reloader=debug_switch)
