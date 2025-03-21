from flask import Flask, request, render_template, jsonify
import joblib
import numpy as np

app = Flask(__name__)

# Load trained model
try:
    model = joblib.load("mlr_energy_consumption_model.pkl")
    print(f"Model Loaded Successfully! Type: {type(model)}")
except Exception as e:
    print(f"Model Load Error: {e}")
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

@app.route("/", methods=["GET", "POST"])
def home():
    prediction = None  # Default value for prediction

    if request.method == "POST":
        try:
            # Fetch form data
            square_footage = float(request.form.get("square_footage", 0))
            num_occupants = float(request.form.get("num_occupants", 0))
            appliances = float(request.form.get("appliances", 0))
            building_type = request.form.get("building_type", "")
            day = request.form.get("day_of_week", "")
            heat = request.form.get("heat_level", "")

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

            print(f"Input Features: {features}")

            # Predict using model
            if model:
                standardized_prediction = float(model.predict(features)[0])
                actual_prediction = (standardized_prediction * std_values["Energy Consumption"]) + mean_values["Energy Consumption"]
                prediction = round(actual_prediction, 2)
                print(f"Predicted Energy Consumption: {prediction} kWh")
            else:
                prediction = "Model Not Found"

        except Exception as e:
            print(f"Error in Prediction: {e}")
            prediction = "Error in Prediction"

    return render_template("energy.html", prediction=prediction)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
