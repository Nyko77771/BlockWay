import pytest
import zipfile
from joblib import load

# Fake Model Set-up


class FakeModel:

    def predict(self, type):
        if type == "malicious":
            return 1
        if type == "benign":
            return 0


class FakeModelAnalysis:

    def __init__(self):
        self.logistic_model = FakeModel()
        self.random_forrest = FakeModel()

    def create_features(self, number=1):
        return [
            self._make_fake_length(number),
            self._make_fake_has_ip(number),
            self._make_fake_digit_count(number),
        ]

    def _make_fake_length(self, number):
        return number

    def _make_fake_has_ip(self, number):
        return number

    def _make_fake_digit_count(self, number):
        return number


# Unit Testing:


def test_feature_creation():
    fake_analysis = FakeModelAnalysis()

    result = fake_analysis.create_features(5)
    assert result == [5, 5, 5]


def test_feature_default():
    fake_analysis = FakeModelAnalysis()

    result = fake_analysis.create_features()
    assert result == [1, 1, 1]


def test_malicious_prediction():
    fake_analysis = FakeModelAnalysis()

    result = fake_analysis.logistic_model.predict("malicious")

    assert result == 1


def test_benign_prediction():
    fake_analysis = FakeModelAnalysis()

    result = fake_analysis.logistic_model.predict("benign")

    assert result == 0


def test_zip_opening():

    path = "block_app/models/r_forrest.zip"

    with zipfile.ZipFile(path, "r") as zObject:

        assert "r_forrest.pkl" in zObject.namelist()


def test_model_forrest_loaded():
    model = load("block_app/models/r_forrest.pkl")

    assert model is not None


def test_model_logistic_loaded():
    model = load("block_app/models/logistic.pkl")

    assert model is not None
