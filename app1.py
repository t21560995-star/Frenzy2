#!/usr/bin/env python
# coding: utf-8

# In[5]:


import streamlit as st
import numpy as np
import pandas as pd
import requests
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import to_categorical

# Load the trained model
model = load_model('improved_roulette_lstm_model.h5')

# Function to map input features
def get_dozen(number):
    if 1 <= number <= 12:
        return 0  # Dozen 1
    elif 13 <= number <= 24:
        return 1  # Dozen 2
    elif 25 <= number <= 36:
        return 2  # Dozen 3
    else:
        return 3  # Green (0)

def get_color(number):
    red_numbers = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
    if number == 0:
        return "Green"
    elif number in red_numbers:
        return "Red"
    else:
        return "Black"

def get_parity(number):
    return "Even" if number % 2 == 0 else "Odd"

def get_high_low(number):
    return "Low" if 1 <= number <= 18 else "High"

def preprocess_input(last_10_spins):
    # Prepare the input data for prediction
    features = []
    for number in last_10_spins:
        color = get_color(number)
        parity = get_parity(number)
        high_low = get_high_low(number)
        dozen = get_dozen(number)
        
        # Normalize features and encode them numerically
        normalized_number = number / 36
        distance_from_zero = abs(number - 0)
        
        color_mapping = {"Red": 1, "Black": 0, "Green": 2}
        parity_mapping = {"Even": 1, "Odd": 0}
        high_low_mapping = {"Low": 1, "High": 0}
        
        features.append([
            number, 
            color_mapping[color], 
            parity_mapping[parity], 
            high_low_mapping[high_low],
            np.random.choice([0, 1]),  # Random dummy feature for racetrack_0
            np.random.choice([0, 1]),  # Random dummy feature for racetrack_1
            np.random.choice([0, 1]),  # Random dummy feature for racetrack_2
            distance_from_zero, 
            normalized_number
        ])
    
    features = np.array(features)
    features = features.reshape((1, 10, 9))  # Shape it to (1, lag_count, feature_count)
    return features

# Function to fetch the last 10 spins from the API
def fetch_last_10_spins():
    base_url = "https://api.casinoscores.com/svc-evolution-game-events/api/xxxtremelightningroulette"
    params = {
        "size": 10,  # Fetch only the last 10 spins
        "sort": "data.settledAt,desc",  # Sort by descending settlement time
        "duration": 72,  # Optional: Filter based on the duration (72 hours)
        "isLightningNumberMatched": "false"  # Optional: Filter out lightning numbers
    }
    
    try:
        # Send GET request to the API
        response = requests.get(base_url, params=params)
        
        # Check if the response status is OK (200)
        if response.status_code == 200:
            data = response.json()
            # Extract the 'number' from each event if available
            numbers = [
                event["data"]["result"]["outcome"]["number"]
                for event in data
                if "data" in event and "result" in event["data"] and "outcome" in event["data"]["result"]
            ]
            # Ensure the latest spin appears first (reverse the list)
            numbers.reverse()
            return numbers
        else:
            st.error(f"Failed to fetch data. Status code: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return []

# Function to get human-readable output for the predictions
def get_human_readable_prediction(predictions):
    # Map the dozens to human-readable labels
    dozen_mapping = {0: "Dozen 1 (1-12)", 1: "Dozen 2 (13-24)", 2: "Dozen 3 (25-36)", 3: "Green (0)"}
    
    # Get the top 2 predicted dozens and their probabilities
    top_2_predictions = np.argsort(predictions, axis=1)[:, -2:]
    top_2_probabilities = np.sort(predictions, axis=1)[:, -2:]
    
    # Prepare human-readable output
    prediction_result = [
        f"1. {dozen_mapping[top_2_predictions[0][1]]} with a probability of {top_2_probabilities[0][1]:.2f}",
        f"2. {dozen_mapping[top_2_predictions[0][0]]} with a probability of {top_2_probabilities[0][0]:.2f}"
    ]
    
    return prediction_result

# Streamlit app layout
st.title("Roulette Prediction AI")

# Button to fetch the last 10 spins from the API
if st.button("Fetch Last 10 Spins"):
    last_10_spins = fetch_last_10_spins()

    if last_10_spins:
        # Display the fetched spins
        st.write(f"Last 10 Spins: {last_10_spins}")

        # Preprocess the input data for prediction
        input_data = preprocess_input(last_10_spins)
        
        # Get predictions from the model
        predictions = model.predict(input_data)
        
        # Get human-readable prediction results
        prediction_result = get_human_readable_prediction(predictions)
        
        # Display results in a human-readable format
        st.write("Prediction Results for the Next Spin:")
        st.write("\n".join(prediction_result))


# In[ ]:




