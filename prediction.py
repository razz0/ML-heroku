import os
from flask import Flask, render_template
from sklearn.externals import joblib
from apiharvester import APIHarvester

app = Flask(__name__)

app.debug = True

apikey = os.environ['fmi_apikey']
harvester = APIHarvester(logfile="harvester.log", apikey=apikey)
prediction_model = joblib.load('model/predictor_model.pkl')


@app.route('/')
def prediction():
    forecasts = harvester.fmi_forecast()
    for forecast, values in forecasts.iteritems():
        value_tuple = (float(values['Precipitation1h']), float(values['Temperature']), float(values['WindSpeedMS']))
        disruptions = prediction_model.predict(value_tuple)[0]
        values.update({'prediction': disruptions})

    return render_template('prediction.html', forecasts=forecasts)


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


