from collections import defaultdict
from datetime import datetime, timedelta, time
import json
import os

from flask import Flask, render_template
import iso8601

from apiharvester import APIHarvester
from store_predictions import FORECAST_FILE
from models import prediction_models


OBSERVED_DISRUPTIONS_FILE = 'disruptions_observed.json'

app = Flask(__name__)
app.config['DEBUG'] = True
app.debug = True

if __name__ == '__main__':
    app.run()

apikey = os.environ.get('fmi_apikey')
harvester = APIHarvester(logfile="harvester.log", apikey=apikey)


@app.route('/')
def prediction():
    disruptions = defaultdict(dict)
    forecasts = harvester.fmi_forecast()

    for timestamp, values in forecasts.iteritems():
        for model in prediction_models:
            value_tuple = (float(values['Precipitation1h']), float(values['Temperature']), float(values['WindSpeedMS']))
            disruption_amount = model.predict(value_tuple)
            disruptions[timestamp].update({model.name: disruption_amount})

    return render_template('prediction.html', forecasts=forecasts, disruptions=disruptions)


@app.route('/history/')
def prediction_history():
    stored_disruptions = defaultdict(dict)
    stored_observed_disruptions = harvester.read_datafile(OBSERVED_DISRUPTIONS_FILE) or {}
    stored_forecasts = harvester.read_datafile(FORECAST_FILE) or {}

    observed_disruptions = {}

    for model in prediction_models:
        model.stored_disruptions = harvester.read_datafile(model.JSON_FILE) or {}

    for timestamp, values in stored_forecasts.iteritems():
        for model in prediction_models:
            disruption_amount = model.stored_disruptions.get(timestamp, '-')
            stored_disruptions[timestamp].update({model.name: disruption_amount})

        obs_time = iso8601.parse_date(timestamp).replace(tzinfo=None)
        now_time = datetime.utcnow()
        if timedelta(0) < now_time - obs_time < timedelta(days=2):
            observed_disruptions[timestamp] = harvester.hsl_api(iso8601.parse_date(timestamp))

    stored_observed_disruptions.update(observed_disruptions)

    with open(OBSERVED_DISRUPTIONS_FILE, 'w') as f:
        json.dump(stored_observed_disruptions, f)

    return render_template('history.html', forecasts=stored_forecasts, predicted=stored_disruptions,
                           actual=stored_observed_disruptions)


@app.route('/test/')
def prediction_test():
    forecasts = {}
    disruption_set = set()
    for rain in range(-10, 400, 1):
        for temp in range(-50, -45, 5):
            for wind in range(50, 60, 10):
                values = {'Precipitation1h': float(rain) / 10.0, 'Temperature': float(temp) / 10.0, 'WindSpeedMS': float(wind) / 10.0}
                value_tuple = (values['Precipitation1h'], values['Temperature'], values['WindSpeedMS'])
                disruptions = prediction_model.predict(value_tuple)[0]
#                if disruptions not in disruption_set:
#                    disruption_set.add(disruptions)
                values.update({'prediction': disruptions})
                forecasts.update({'%02d_%02d_%s' % (rain, temp, wind): values})

    return render_template('prediction.html', forecasts=forecasts)


