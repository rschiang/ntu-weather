# Weather source
# (C) Poren Chiang 2016–2020

import re
import requests
from datetime import datetime
from pytz import timezone
from .models import Weather, Provider
from .exceptions import WeatherParseError

class NTUASProvider(Provider):
    """Weather information provider for NTU AS."""

    def __init__(self, url=None):
        """Initialize NTU AS Provider, optionally with an alternative data feed."""
        super().__init__(name='國立臺灣大學中尺度暨地形降水研究室')
        self.url = url or 'http://140.112.67.180/data.php'
        self.timezone = timezone('Asia/Taipei')

    def get(self):
        """Acquire weather information from NTU AS."""

        # Reset state
        self.text = None

        # Retrieve the information for the website
        request = requests.get(self.url)
        request.raise_for_status()

        # Test if the data is valid
        self.text = request.text
        if not self.text:
            raise WeatherParseError(text=self.text)

        # Initialize and return the object
        return Weather(
            date=self._search_date(r'資料擷取時間：\s*(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', 'date'),
            temperature=self._search_float(r'氣溫\(℃\)：\s*([\d\.]+)\s*</div>', 'temperature'),
            pressure=self._search_float(r'海平面氣壓\(hPa\)：\s*([\d\.]+)\s*</div>', 'pressure'),
            humidity=self._search_float(r'相對溼度\(％\)：\s*([\d\.]+)\s*</div>', 'humidity'),
            wind_speed=self._search_float(r'風速\(推移十分鐘平均\)\(m/s\)：\s*([\d\.]+)\s*</div>', 'wind_speed'),
            wind_direction=self._search_int(r'風向\(推移十分鐘平均\)\(方位\)：\s*([\d\.]+)\s*</div>', 'wind_direction'),
            rain_per_hour=self._search_float(r'小時累積降雨量\(mm\)：\s*([\d\.]+)\s*</div>', 'rain_per_hour'),
            rain_per_minute=self._search_float(r'分鐘降雨量\(mm\)：\s*([\d\.]+)\s*</div>', 'rain_per_minute'),
            ground_temperature=self._search_float(r'0cm地溫\(℃\)：\s*([\d\.]+)\s*</div>', 'ground_temperature'),
            provider=self.name,
        )

    # Utilities

    def _search(self, pattern):
        """Matches a specific pattern from the stored text."""
        match = re.search(pattern, self.text)
        if match is not None:
            return match.group(1).strip()
        return None

    def _search_date(self, pattern, arg=None):
        """Matches and returns a DateTime object from the stored text."""
        string = self._search(pattern)
        if string:
            try:
                date = datetime.strptime(string, '%Y-%m-%d %H:%M:%S')
                return self.timezone.localize(date)
            except ValueError: pass
        raise WeatherParseError(text=self.text, arg=arg)

    def _search_int(self, pattern, arg=None):
        """Matches and returns an int value from the stored text."""
        string = self._search(pattern)
        if string:
            try:
                return int(string)
            except: pass
        raise WeatherParseError(text=self.text, arg=arg)

    def _search_float(self, pattern, arg=None):
        """Matches and returns a float value from the stored text."""
        string = self._search(pattern)
        if string:
            try:
                return float(string)
            except: pass
        raise WeatherParseError(text=self.text, arg=arg)


class NTUSAProvider(Provider):
    """Weather information provider from NTUSA weather relay."""

    def __init__(self, url=None):
        """Initialize NTUSA Provider, optionally with an alternative data feed."""
        super().__init__(name='第28屆臺大學生會福利部')
        self.url = url or 'http://weather.ntustudents.org/api'

    def get(self):
        """Acquire weather information from NTUSA weather relay."""

        # Retrieve the information for the website
        request = requests.get(self.url)
        request.raise_for_status()

        self.data = request.json()

        return Weather(
            date=datetime.fromisoformat(self.data['date']),
            temperature=float(self.data['temperature']),
            pressure=float(self.data['pressure']),
            humidity=float(self.data['humidity']),
            wind_speed=float(self.data['wind_speed']),
            wind_direction=int(self.data['wind_direction']),
            rain_per_hour=float(self.data['rain']),
            rain_per_minute=float(self.data['rain_minute']),
            ground_temperature=float(self.data['temp_ground']),
            provider=self.data['provider'] or self.name)
