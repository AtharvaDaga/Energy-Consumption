import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(EnergyPredictionApp());
}

class EnergyPredictionApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: EnergyForm(),
    );
  }
}

class EnergyForm extends StatefulWidget {
  @override
  _EnergyFormState createState() => _EnergyFormState();
}

class _EnergyFormState extends State<EnergyForm> {
  final TextEditingController squareFootageController = TextEditingController();
  final TextEditingController numOccupantsController = TextEditingController();
  final TextEditingController appliancesController = TextEditingController();

  String buildingType = 'Residential';
  String dayOfWeek = 'Weekday';
  String heatLevel = 'Mild Day';
  String result = '';

  Future<void> sendData() async {
    final String apiUrl = "https://energy-consumption-prediction-8dx5.onrender.com/predict"; // Correct API URL

    final Map<String, dynamic> data = {
      "square_footage": double.tryParse(squareFootageController.text) ?? 0.0,
      "num_occupants": double.tryParse(numOccupantsController.text) ?? 0.0,
      "appliances": double.tryParse(appliancesController.text) ?? 0.0,
      "building_type": buildingType,
      "day_of_week": dayOfWeek,
      "heat_level": heatLevel
    };

    try {
      final response = await http.post(
        Uri.parse(apiUrl),
        headers: {"Content-Type": "application/json"},
        body: json.encode(data),
      );

      print("Response status: ${response.statusCode}"); // Debugging
      print("Response body: ${response.body}"); // Debugging

      if (response.statusCode == 200) {
        final responseData = json.decode(response.body);
        setState(() {
          result = "Predicted Energy: ${responseData["prediction"]} kWh";
        });
      } else {
        setState(() {
          result = "Error: ${response.body}";
        });
      }
    } catch (e) {
      setState(() {
        result = "Network Error: Unable to reach server.";
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Energy Consumption Prediction')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: SingleChildScrollView(
          child: Column(
            children: [
              TextField(
                controller: squareFootageController,
                decoration: InputDecoration(labelText: 'Square Footage'),
                keyboardType: TextInputType.number,
              ),
              TextField(
                controller: numOccupantsController,
                decoration: InputDecoration(labelText: 'Number of Occupants'),
                keyboardType: TextInputType.number,
              ),
              TextField(
                controller: appliancesController,
                decoration: InputDecoration(labelText: 'Appliances Used'),
                keyboardType: TextInputType.number,
              ),
              DropdownButtonFormField(
                value: buildingType,
                onChanged: (value) => setState(() => buildingType = value.toString()),
                items: ['Residential', 'Commercial', 'Industrial'].map((type) {
                  return DropdownMenuItem(value: type, child: Text(type));
                }).toList(),
                decoration: InputDecoration(labelText: 'Building Type'),
              ),
              DropdownButtonFormField(
                value: dayOfWeek,
                onChanged: (value) => setState(() => dayOfWeek = value.toString()),
                items: ['Weekday', 'Weekend'].map((day) {
                  return DropdownMenuItem(value: day, child: Text(day));
                }).toList(),
                decoration: InputDecoration(labelText: 'Day of Week'),
              ),
              DropdownButtonFormField(
                value: heatLevel,
                onChanged: (value) => setState(() => heatLevel = value.toString()),
                items: ['Mild Day', 'Moderate Day', 'Hot Day'].map((heat) {
                  return DropdownMenuItem(value: heat, child: Text(heat));
                }).toList(),
                decoration: InputDecoration(labelText: 'Heat Level'),
              ),
              SizedBox(height: 20),
              ElevatedButton(
                onPressed: sendData,
                child: Text('Predict Energy Consumption'),
              ),
              SizedBox(height: 20),
              Text(
                result,
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
