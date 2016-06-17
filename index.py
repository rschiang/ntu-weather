#!/usr/bin/env python3
import os
import pymongo
import weather
from bottle import Bottle, view
from bottle_mongo import MongoPlugin
from datetime import datetime
from pytz import timezone

app = Bottle()
debug_switch = (os.environ.get('DEBUG') == '1')
tz = timezone('Asia/Taipei')

# Configure database
mongo_plugin = MongoPlugin(uri=os.environ.get('MONGODB_URI'), db='', keyword='mongo')
app.install(mongo_plugin)

@app.route('/', template='index')
def index(mongo):
    last_doc = get_cached(mongo, timeout=900)
    if not last_doc:
        last_doc = fetch_and_cache(mongo)
    return last_doc

@app.route('/api')
def api(mongo):
    last_doc = get_cached(mongo, timeout=300)
    if not last_doc:
        last_doc = fetch_and_cache(mongo)
    last_doc['date'] = last_doc['date'].isoformat()
    return last_doc

def get_cached(mongo, timeout=600):
    all_weather = mongo['weather']
    last_doc = all_weather.find_one(sort=[('date', pymongo.DESCENDING)], projection={'_id': False})

    if last_doc:
        now_date = datetime.now(tz)
        last_date = tz.localize(last_doc['date'])
        if (now_date - last_date).total_seconds() < timeout:
            return last_doc

    return None

def fetch_and_cache(mongo):
    all_weather = mongo['weather']
    this_doc = fetch_api()
    if 'error' not in this_doc:
        all_weather.insert_one(this_doc)
        del this_doc['_id'] # pyMongo seems to be messing with our dict
    return this_doc

def fetch_api():
    try:
        response_text = weather.fetch()
    except IOError:
        return {'error': 'server_unavailable'}
    try:
        weather_dict = weather.parse(response_text)
        weather_dict['date'] = tz.localize(datetime.strptime(weather_dict['date'], '%Y/%m/%d %H:%M:%S'))
        return weather_dict
    except Exception:
        return {'error': 'data_unavailable'}

if __name__ == '__main__':
    app.run(debug=debug_switch, reloader=debug_switch)
