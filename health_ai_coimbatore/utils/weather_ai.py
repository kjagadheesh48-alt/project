import requests
import pandas as pd
import numpy as np

# Coimbatore Coordinates
LAT = 11.0168
LON = 76.9558

def fetch_weather_data(days=14):
    """
    Fetch 7-14 day weather forecast from Open-Meteo
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={LAT}&longitude={LON}"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        f"&forecast_days={days}"
        f"&timezone=Asia/Kolkata"
    )

    response = requests.get(url)
    data = response.json()

    df = pd.DataFrame({
        "date": data["daily"]["time"],
        "temp_max": data["daily"]["temperature_2m_max"],
        "temp_min": data["daily"]["temperature_2m_min"],
        "rainfall": data["daily"]["precipitation_sum"]
    })

    return df


def predict_next_day_rainfall(weather_df):
    """
    Simple AI prediction using moving average
    """
    rainfall = weather_df["rainfall"].values

    # Use last 3 days average
    if len(rainfall) >= 3:
        prediction = np.mean(rainfall[-3:])
    else:
        prediction = np.mean(rainfall)

    return round(prediction, 2)