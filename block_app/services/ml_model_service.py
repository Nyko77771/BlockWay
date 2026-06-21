from joblib import load
import pandas as pd

class MlAnalyses:
    def __init__(self):
        self.logistic_model = load('models/logistic.pkl')
        self.r_forrest = load('models/r_forrest.pkl')

    def create_x_features(self, url):
        x_test = None
        return x_test

    def logistic_prediction(self, url):
        x_test = self.create_x_features(url)
        prediction = self.logistic_model.predict(x_test)
        return prediction[0]