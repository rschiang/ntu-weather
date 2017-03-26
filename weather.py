#!/usr/bin/env python3
import html
import json
import requests
import re
from colorama import Fore, Style
from datetime import datetime
from sys import stderr

def fetch():
    url = 'http://140.112.66.208:8080/mopl/rt2.one?one=execute'
    request = requests.get(url)
    return request.text

def search_one(pattern, string):
    match = re.search(pattern, string)
    if match is not None:
        match = match.group(1).strip()
    return match

def print_err(text, color=Style.RESET_ALL, bright=False):
    if bright:
        stderr.write(Style.BRIGHT)
    stderr.write(color)
    stderr.write(text)
    stderr.write('\n')

def parse(text):
    date = search_one(r'觀測時間\s*:</td>\s*<td[^>]+>(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})', text)
    if not date:
        print_err('ERR: Cannot find observing time. Check service availability.', Fore.RED, bright=True)
        print_err('Original string:')
        print_err(text, Fore.WHITE, bright=True)
        print_err('\n')
        raise Exception('Parse failed')

    return {
        'date': date,
        'temperature': search_one(r'溫度\s*:</td>\s*<td[^>]+>\s*([\d\.]+)&nbsp;', text),      # (˚C)
        'pressure': search_one(r'氣壓\s*:</td>\s*<td[^>]+>\s*([\d\.]+)&nbsp;', text),         # (hPa)
        'humidity': search_one(r'相對濕度\s*:</td>\s*<td[^>]+>\s*([\d\.]+)&nbsp;', text),      # (%)
        'wind_speed': search_one(r'風速\s*:</td>\s*<td[^>]+>\s*([\d\.]+)&nbsp;', text),       # (m/s)
        'wind_direction': search_one(r'風向\s*:</td>\s*<td[^>]+>\s*([\d\.]+)&nbsp;', text),   # (˚)
        'rain': search_one(r'降雨強度\s*:</td>\s*<td[^>]+>\s*([\d\.]+)&nbsp;', text),          # (mm/h)

        'temp_max': search_one(r'本日最高溫\s*:</td>\s*<td[^>]+>\s*([\d\.]+)\s*<', text),         # (˚C)
        'temp_min': search_one(r'本日最低溫\s*:</td>\s*<td[^>]+>\s*([\d\.]+)\s*<', text),         # (˚C)
        'rain_day': search_one(r'本日降雨量\s*:</td>\s*<td[^>]+>\s*([\d\.]+)\s*<', text),        # (mm)

        'provider': '國立臺灣大學中尺度暨地形降水研究室',
    }

if __name__ == '__main__':
    from sys import stdout, exit
    text = fetch()
    data = parse(text)
    json.dump(data, stdout, ensure_ascii=False, indent=2)
