from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import os

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# Load trained model
MODEL_PATH = "mlr_energy_consumption_model.pkl"
if os.path.exists(MODEL_PATH):
    try:
        model = joblib.load(MODEL_PATH)
        print(" Model Loaded Successfully!")
    except Exception as e:
        print(f" Model Load Error: {e}")
        model = None
else:
    print(" Model file not found! Check deployment.")
    model = None

# Mean & Std for normalization
mean_values = {
    "Square Footage": 27672.6545,  
    "Number of Occupants": 49.4945,
    "Appliances Used": 25.8291,
    "Energy Consumption": 3995.7822
}

std_values = {
    "Square Footage": 13045.1552,
    "Number of Occupants": 28.7215,
    "Appliances Used": 14.3262,
    "Energy Consumption": 1144.5472
}

# Encoding mappings
building_types = {"Residential": [0, 0, 1], "Commercial": [1, 0, 0], "Industrial": [0, 1, 0]}
day_of_week = {"Weekday": [1, 0], "Weekend": [0, 1]}
heat_levels = {"Mild Day": [0, 1, 0], "Moderate Day": [0, 0, 1], "Hot Day": [1, 0, 0]}

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API is running!"})

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data received"}), 400

        print("📩 Received Data:", data)  # Debugging log

        # Extract and validate inputs
        square_footage = float(data.get("square_footage", 0))
        num_occupants = float(data.get("num_occupants", 0))
        appliances = float(data.get("appliances", 0))
        building_type = data.get("building_type", "Residential")
        day = data.get("day_of_week", "Weekday")
        heat = data.get("heat_level", "Mild Day")

        # Standardize numerical features
        def standardize(value, mean, std):
            return (value - mean) / std

        square_footage = standardize(square_footage, mean_values["Square Footage"], std_values["Square Footage"])
        num_occupants = standardize(num_occupants, mean_values["Number of Occupants"], std_values["Number of Occupants"])
        appliances = standardize(appliances, mean_values["Appliances Used"], std_values["Appliances Used"])

        # One-hot encode categorical variables
        building_encoded = building_types.get(building_type, [0, 0, 1])
        day_encoded = day_of_week.get(day, [1, 0])
        heat_encoded = heat_levels.get(heat, [0, 1, 0])

        # Create feature array
        features = np.array([square_footage, num_occupants, appliances] +
                            building_encoded + day_encoded + heat_encoded).reshape(1, -1)

        # Predict using model
        if model:
            standardized_prediction = float(model.predict(features)[0])
            actual_prediction = (standardized_prediction * std_values["Energy Consumption"]) + mean_values["Energy Consumption"]
            prediction = round(actual_prediction, 2)
        else:
            return jsonify({"error": "Model not loaded"}), 500

        return jsonify({"prediction": prediction})

    except Exception as e:
        print(f" Prediction Error: {e}")
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)