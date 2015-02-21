"""Predict traffic disruptions based on next 24h weather forecast and save predictions to file."""

import json
import os
from sklearn.externals import joblib
from apiharvester import APIHarvester

from models import prediction_models


FORECAST_FILE = 'forecasts.json'

apikey = os.environ.get('fmi_apikey')
harvester = APIHarvester(logfile="harvester.log", apikey=apikey)

forecasts = harvester.fmi_forecast()

for model in prediction_models:
    for timestamp, values in forecasts.iteritems():
        value_tuple = (float(values['Precipitation1h']), float(values['Temperature']), float(values['WindSpeedMS']))
        disruption_amount = model.predict(value_tuple)
        model.disruptions.update({timestamp: disruption_amount})

# Store weather forecasts

stored_forecasts = harvester.read_datafile(FORECAST_FILE) or {}
stored_forecasts.update(forecasts)

with open(FORECAST_FILE, 'w') as f:
    json.dump(stored_forecasts, f)

# Store predicted disruptions

for model in prediction_models:
    stored_disruptions = harvester.read_datafile(model.JSON_FILE) or {}
    stored_disruptions.update(model.disruptions)

    with open(model.JSON_FILE, 'w') as f:
        json.dump(stored_disruptions, f)

