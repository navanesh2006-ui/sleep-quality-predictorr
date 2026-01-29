from flask import Flask, request, jsonify, render_template
import joblib
import numpy as np
import os

app = Flask(__name__)

# Load Model Artifacts
try:
    model = joblib.load('sleep_model.pkl')
    scaler = joblib.load('scaler.pkl')
    le_caffeine = joblib.load('le_caffeine.pkl')
    le_mood = joblib.load('le_mood.pkl')
    le_interruptions = joblib.load('le_interruptions.pkl')
    le_target = joblib.load('le_target.pkl')
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    # In a real scenario, handle this gracefully or fail fast.

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        print("Received data:", data)

        # Extract features
        sleep_duration = float(data['sleep_duration'])
        
        # Bedtime and Wake time processing (converting HH:MM to float hour)
        # Assuming input is "HH:MM" 24h format
        def time_to_float(t_str):
            h, m = map(int, t_str.split(':'))
            return h + m/60.0

        bedtime_hour = time_to_float(data['bedtime'])
        if bedtime_hour < 12: bedtime_hour += 24 # Handle next-day times logic if needed, but simple float is okay for now consistent with training
        
        wake_time_hour = time_to_float(data['wake_time'])
        
        caffeine = le_caffeine.transform([data['caffeine']])[0]
        exercise_duration = float(data['exercise_duration'])
        screen_time = float(data['screen_time'])
        stress_level = int(data['stress_level'])
        mood = le_mood.transform([data['mood']])[0]
        interruptions = le_interruptions.transform([data['interruptions']])[0]

        # Feature array in correct order (matching train_model.py)
        # 'Sleep Duration', 'Bedtime_Hour', 'Wake_Time_Hour', 'Caffeine Intake', 
        # 'Exercise Duration', 'Screen Time', 'Stress Level', 'Mood', 'Sleep Interruptions'
        features = np.array([[
            sleep_duration, bedtime_hour, wake_time_hour, caffeine, 
            exercise_duration, screen_time, stress_level, mood, interruptions
        ]])
        
        features_scaled = scaler.transform(features)
        prediction_idx = model.predict(features_scaled)[0]
        prediction = le_target.inverse_transform([prediction_idx])[0]
        
        # Generate Tips
        tips = []
        if sleep_duration < 7: tips.append("Try to get at least 7-8 hours of sleep.")
        if data['caffeine'] in ['Moderate', 'High']: tips.append("Consider reducing caffeine intake, especially later in the day.")
        if screen_time > 60: tips.append("Reducing screen time before bed can improve sleep quality.")
        if stress_level > 5: tips.append("Practice relaxation techniques like meditation or reading to lower stress.")
        if prediction == 'Poor' and not tips: tips.append("Maintain a consistent sleep schedule.")
        if not tips: tips.append("Keep up the great habits!")

        return jsonify({'quality': prediction, 'tips': tips})

    except Exception as e:
        print(f"Prediction Error: {e}")
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
