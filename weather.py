#!/usr/bin/env python3
import html
import json
import requests
import re
from colorama import Fore, Style
from datetime import datetime
from sys import stderr

def fetch():
    url = 'http://140.112.67.180/data.php'
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
    date = search_one(r'資料擷取時間：\s*(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', text)
    if not date:
        print_err('ERR: Cannot find observing time. Check service availability.', Fore.RED, bright=True)
        print_err('Original string:')
        print_err(text, Fore.WHITE, bright=True)
        print_err('\n')
        raise Exception('Parse failed')

    return {
        'date': date,
        'temperature': search_one(r'氣溫\(℃\)：\s*([\d\.]+)\s*</div>', text),
        'pressure': search_one(r'海平面氣壓\(hPa\)：\s*([\d\.]+)\s*</div>', text),
        'humidity': search_one(r'相對溼度\(％\)：\s*([\d\.]+)\s*</div>', text),
        'wind_speed': search_one(r'風速\(推移十分鐘平均\)\(m/s\)：\s*([\d\.]+)\s*</div>', text),
        'wind_direction': search_one(r'風向\(推移十分鐘平均\)\(方位\)：\s*([\d\.]+)\s*</div>', text),
        'rain': search_one(r'小時累積降雨量\(mm\)：\s*([\d\.]+)\s*</div>', text),

        # The following data has become unavailable and need manual calculation
        # 'temp_max': search_one(r'本日最高溫\s*:</td>\s*<td[^>]+>\s*([\d\.]+)\s*<', text),         # (˚C)
        # 'temp_min': search_one(r'本日最低溫\s*:</td>\s*<td[^>]+>\s*([\d\.]+)\s*<', text),         # (˚C)
        # 'rain_day': search_one(r'本日降雨量\s*:</td>\s*<td[^>]+>\s*([\d\.]+)\s*<', text),
        'rain_minute': search_one(r'分鐘降雨量\(mm\)：\s*([\d\.]+)\s*</div>', text),
        'temp_ground': search_one(r'0cm地溫\(℃\)：\s*([\d\.]+)\s*</div>', text),

        'provider': '國立臺灣大學中尺度暨地形降水研究室',
    }

if __name__ == '__main__':
    from sys import stdout, exit
    text = fetch()
    data = parse(text)
    json.dump(data, stdout, ensure_ascii=False, indent=2)
