from flask import Flask, render_template
from sklearn.externals import joblib
from apiharvester import APIHarvester

app = Flask(__name__)

app.debug = True

harvester = APIHarvester()
prediction_model = joblib.load('model/predictor_model.pkl')


@app.route('/')
def prediction():
    forecasts = harvester.fmi_forecast()
    return render_template('prediction.html', forecasts=forecasts)



