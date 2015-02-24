from collections import defaultdict
from datetime import datetime, timedelta
import json
import os
import urllib2
from dateutil import tz

from flask import Flask, render_template, request
import iso8601
import pytz

from apiharvester import APIHarvester
from models import prediction_models


app = Flask(__name__)
app.config['DEBUG'] = True
app.debug = True

if __name__ == '__main__':
    app.run()

BACKEND_URL = os.environ.get('backend_url')

harvester = APIHarvester(logfile="harvester.log", apikey='dummy')

# TODO: Beaker cache

@app.route('/')
def prediction():
    disruptions = defaultdict(dict)
    url = '{backend}data/forecasts.json'.format(backend=BACKEND_URL)
    forecasts = json.loads(urllib2.urlopen(url).read())

    for model in prediction_models:
        url = '{backend}{file}'.format(backend=BACKEND_URL, file=model.JSON_FILE)
        app.logger.debug(url)
        model.stored_disruptions = json.loads(urllib2.urlopen(url).read())

    future_forecasts = {}

    now_time = datetime.utcnow().replace(tzinfo=tz.tzutc())
    app.logger.debug(now_time)
    for timestamp, values in forecasts.iteritems():

        forecast_time = iso8601.parse_date(timestamp, tz.tzutc)
        if now_time > forecast_time:
            continue

        local_time = forecast_time.astimezone(tz.gettz('Europe/Helsinki'))
        local_timestamp = local_time.isoformat()

        future_forecasts[local_timestamp] = values

        for model in prediction_models:
            disruption_amount = model.stored_disruptions.get(timestamp)
            disruptions[model.name].update({local_timestamp: disruption_amount})

    return render_template('prediction.html', forecasts=future_forecasts, disruptions=disruptions, page='forecast')


@app.route('/history/')
def prediction_history():
    predictions_history = defaultdict(dict)
    forecast_history = defaultdict(dict)

    url = '{backend}data/disruptions_observed.json'.format(backend=BACKEND_URL)
    stored_observed_disruptions = json.loads(urllib2.urlopen(url).read())

    url = '{backend}data/forecasts.json'.format(backend=BACKEND_URL)
    stored_forecasts = json.loads(urllib2.urlopen(url).read())

    for model in prediction_models:
        url = '{backend}{file}'.format(backend=BACKEND_URL, file=model.JSON_FILE)
        model.stored_disruptions = json.loads(urllib2.urlopen(url).read())

    for timestamp, values in stored_forecasts.iteritems():
        observation_time = iso8601.parse_date(timestamp, tz.tzutc)
        now_time = datetime.utcnow().replace(tzinfo=tz.tzutc())
        if now_time < observation_time:
            continue

        local_time = observation_time.astimezone(tz.gettz('Europe/Helsinki'))
        local_timestamp = local_time.isoformat()

        forecast_history[local_timestamp] = values

        for model in prediction_models:
            disruption_amount = model.stored_disruptions.get(timestamp, '')
            predictions_history[model.name].update({local_timestamp: disruption_amount})

        predictions_history[' Actual'].update({local_timestamp: stored_observed_disruptions.get(timestamp, '')})

    app.logger.debug(predictions_history)
    return render_template('prediction.html', forecasts=forecast_history, disruptions=predictions_history, page='history')

