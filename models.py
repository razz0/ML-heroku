"""Prediction models for traffic disruption prediction based on weather forecast"""

import json
import os
from sklearn.externals import joblib


class PredictionModel(object):
    """Prediction model skeleton"""
    JSON_FILE = ''
    name = ''
    disruptions = {}
    stored_disruptions = {}

    def __init__(self, name, json_file):
        self.name = name
        self.JSON_FILE = json_file

    def predict(self, *args):
        return 0


class ScikitPredictor(PredictionModel):
    """Pre-calculated Scikit-learn prediction model"""

    def __init__(self, name, json_file, model_file):
        self.model = joblib.load(model_file)
        super(ScikitPredictor, self).__init__(name, json_file)

    def predict(self, *args):
        return self.model.predict(*args)[0]


def init_models():
    model0 = PredictionModel('0-model', 'disruptions_model0.json')
    model1 = ScikitPredictor('Logistic Regression', 'disruptions_logistic_regression.json', 'model/predictor_model.pkl')

    return [model0, model1]


prediction_models = init_models()

