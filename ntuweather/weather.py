#!/usr/bin/env python3
# Standalone weather CLI script
# (C) Poren Chiang 2020

import os
from sys import stderr
from . import get
from .exceptions import WeatherParseError

COLORED = (os.environ.get('COLOR') != '0')
COLOR_ERROR = ''
COLOR_TEXT = ''
COLOR_SUNNY = ''
COLOR_RAIN = ''
COLOR_NOTE = ''
COLOR_RESET = ''
ARROWS = {337: '↑', 292: '↖', 247: '←', 202: '↙', 157: '↓', 112: '↘', 67: '→', 22: '↗'}

try:
    from colorama import Fore, Style, init
    if COLORED:
        init()
        COLOR_ERROR = Fore.RED
        COLOR_TEXT = Style.BRIGHT
        COLOR_SUNNY = Style.BRIGHT + Fore.YELLOW
        COLOR_RAIN = Style.BRIGHT + Fore.CYAN
        COLOR_NOTE = Style.DIM + Fore.WHITE
        COLOR_RESET = Style.RESET_ALL
except ModuleNotFoundError:
    # Not using colorama to color the output
    COLORED = false

def main():
    try:
        weather = get()
    except WeatherParseError as e:
        print(COLOR_ERROR, 'ERR: Failed to parse weather information from source.', file=stderr)
        print('Original string:', file=stderr)
        print(COLOR_TEXT, e.text, file=stderr)
        raise

    print('Weather for National Taiwan University, Taiwan')
    print('Currently', COLOR_TEXT, round(weather.temperature, 1), COLOR_RESET, '°C',
        '(Ground', weather.ground_temperature, '°C)')
    print('Humidity', round(weather.humidity), '%', '|', round(weather.pressure, 1), 'hPa')

    wind_icon = '↑'
    for deg in ARROWS:
        if weather.wind_direction > deg:
            wind_icon = ARROWS[deg]
            break

    print(COLOR_TEXT, wind_icon, COLOR_RESET, weather.wind_speed, 'm/s')

    print('Precipitation',
        COLOR_RAIN if weather.rain_per_minute > 0 else COLOR_TEXT, weather.rain_per_minute,
        COLOR_RESET, 'mm', '|',
        COLOR_SUNNY if weather.rain_per_hour < 0.1 else COLOR_TEXT, weather.rain_per_hour,
        COLOR_RESET, 'mm/h')

    print(COLOR_NOTE, weather.date.isoformat(sep=' ', timespec='minutes'), '@', weather.provider)

if __name__ == '__main__':
    main()
