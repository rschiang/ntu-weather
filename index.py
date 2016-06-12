#!/usr/bin/env python3
import os
import weather
from bottle import Bottle, view

app = Bottle()
debug_switch = (os.environ.get('DEBUG') == '1')

@app.route('/')
@view('index')
def index():
    weather_dict = fetch_api()
    if 'error' not in weather_dict:
        weather_dict['error'] = False
    return weather_dict

@app.route('/api')
def api():
    return fetch_api()

def fetch_api():
    try:
        response_text = weather.fetch()
    except IOError:
        return {'error': 'server_unavailable'}
    try:
        return weather.parse(response_text)
    except Exception:
        return {'error': 'data_unavailable'}

if __name__ == '__main__':
    app.run(debug=debug_switch, reloader=debug_switch)
