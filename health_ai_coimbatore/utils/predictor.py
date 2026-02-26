import os
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "model", "risk_model.pkl")


def train_dummy_model():
    """Creates a simple model if none exists"""
    X = np.array([
        [20,7.0,2.0,1],
        [80,6.5,4.0,10],
        [50,7.2,3.0,5],
        [120,6.2,5.5,15],
        [30,7.5,2.5,2]
    ])

    y = ["Low","High","Medium","High","Low"]

    model = RandomForestClassifier()
    model.fit(X, y)

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH,"wb") as f:
        pickle.dump(model,f)

    return model


def load_model():
    if not os.path.exists(MODEL_PATH):
        return train_dummy_model()

    with open(MODEL_PATH,"rb") as f:
        return pickle.load(f)


def predict(model, values):
    return model.predict([values])[0]