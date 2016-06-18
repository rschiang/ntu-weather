#!/usr/bin/env python3
import os
import pymongo
import weather
from bottle import Bottle, view
from bottle_mongo import MongoPlugin
from datetime import datetime, timedelta
from pytz import timezone

app = Bottle()
debug_switch = (os.environ.get('DEBUG') == '1')
tz = timezone('Asia/Taipei')

# Configure database
mongo_plugin = MongoPlugin(uri=os.environ.get('MONGODB_URI'), db='', keyword='mongo', tz_aware=True)
app.install(mongo_plugin)

@app.route('/', template='index')
def index(mongo):
    last_doc = get_cached(mongo, timeout=900)
    if not last_doc:
        last_doc = fetch_and_cache(mongo)
    last_doc['daily'] = aggregate_daily(mongo, datetime.now(tz))
    return last_doc

@app.route('/api')
def api(mongo):
    last_doc = get_cached(mongo, timeout=300)
    if not last_doc:
        last_doc = fetch_and_cache(mongo)
    last_doc['date'] = last_doc['date'].isoformat()
    return last_doc

def get_cached(mongo, timeout=600):
    last_doc = get_one(mongo)

    if last_doc:
        now_date = datetime.now(tz)
        last_date = last_doc['date'].astimezone(tz)
        if (now_date - last_date).total_seconds() < timeout:
            last_doc['date'] = last_date
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

def get_one(mongo, filters=None):
    all_weather = mongo['weather']
    return all_weather.find_one(filters, sort=[('date', pymongo.DESCENDING)], projection={'_id': False})

def aggregate_daily(mongo, date):
    doc_list = []
    for i in range(8):
        date -= timedelta(hours=3)
        doc = get_one(mongo, {'date': { '$lte': date }})
        if not doc:
            doc = {'date': date, 'error': 'data_unavailable' }
        doc_list.append(doc)
    return reversed(doc_list)

if __name__ == '__main__':
    app.run(debug=debug_switch, reloader=debug_switch)
