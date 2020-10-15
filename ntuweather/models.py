# Models
# (C) Poren Chiang 2020

from dataclasses import dataclass
from datetime import datetime

@dataclass
class Weather:
    """Weather information retrieved for a specific time of day."""
    date: datetime
    temperature: float
    pressure: float
    humidity: float
    wind_speed: float
    wind_direction: int
    rain_per_hour: float
    rain_per_minute: float
    ground_temperature: float
    provider: str

    def __str__(self):
        if not self.date:
            return '<Weather: invalid>'

        date_str = self.date.isoformat(sep=' ', timespec='minutes')
        return f'<Weather: {date_str} {self.temperature}°>'

class Provider(object):
    """Base class for a weather information provider."""

    def __init__(self, name=None):
        self.name = name

    def get(self):
        raise NotImplemented
