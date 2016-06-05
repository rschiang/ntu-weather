import os
import weather
from bottle import Bottle

app = Bottle()
debug_switch = (os.environ.get('DEBUG') == '1')

@app.route('/')
def index():
    return 'It works!'

@app.route('/api')
def api():
    try:
        response_text = weather.fetch()
    except IOError:
        return {'error': 'server_unavailable'}
    try:
        return weather.parse(response_text)
    except Exception:
        return {'error': 'data_unavailable'}

app.run(debug=debug_switch, reloader=debug_switch)
