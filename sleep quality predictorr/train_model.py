import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib

# 1. Generate Synthetic Data
# Mimicking features: Sleep Duration, Bedtime (hour), Wake Time (hour), Caffeine, Exercise, Screen Time, Stress, Mood, Interruptions
np.random.seed(42)
n_samples = 1000

data = {
    'Sleep Duration': np.random.normal(7, 1.5, n_samples).clip(3, 12),
    'Bedtime_Hour': np.random.normal(23, 1, n_samples).clip(18, 28), # 24+ means next day early morning
    'Wake_Time_Hour': np.random.normal(7, 1, n_samples).clip(4, 12),
    'Caffeine Intake': np.random.choice(['None', 'Low', 'Moderate', 'High'], n_samples, p=[0.3, 0.3, 0.3, 0.1]),
    'Exercise Duration': np.random.normal(30, 20, n_samples).clip(0, 120),
    'Screen Time': np.random.normal(60, 30, n_samples).clip(0, 180),
    'Stress Level': np.random.randint(0, 11, n_samples),
    'Mood': np.random.choice(['Happy', 'Neutral', 'Sad', 'Anxious'], n_samples),
    'Sleep Interruptions': np.random.choice(['Yes', 'No'], n_samples)
}

df = pd.DataFrame(data)

# Logic to assign Target 'Sleep Quality' based on features (for realistic training)
def assign_quality(row):
    score = 0
    if row['Sleep Duration'] >= 7 and row['Sleep Duration'] <= 9: score += 3
    elif row['Sleep Duration'] >= 5: score += 1
    
    if row['Caffeine Intake'] in ['None', 'Low']: score += 2
    if row['Exercise Duration'] > 20: score += 1
    if row['Screen Time'] < 30: score += 2
    if row['Stress Level'] < 4: score += 2
    if row['Mood'] == 'Happy': score += 1
    if row['Sleep Interruptions'] == 'No': score += 2
    
    if score >= 9: return 'Good'
    elif score >= 5: return 'Average'
    else: return 'Poor'

df['Sleep Quality'] = df.apply(assign_quality, axis=1)

print("Data Sample:\n", df.head())

# 2. Preprocessing
le_caffeine = LabelEncoder()
le_mood = LabelEncoder()
le_interruptions = LabelEncoder()
le_target = LabelEncoder()

df['Caffeine Intake'] = le_caffeine.fit_transform(df['Caffeine Intake'])
df['Mood'] = le_mood.fit_transform(df['Mood'])
df['Sleep Interruptions'] = le_interruptions.fit_transform(df['Sleep Interruptions'])
y = le_target.fit_transform(df['Sleep Quality'])

X = df.drop('Sleep Quality', axis=1)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 3. Training
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

print(f"Model Accuracy: {model.score(X_test, y_test):.2f}")

# 4. Save Artifacts
joblib.dump(model, 'sleep_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
joblib.dump(le_caffeine, 'le_caffeine.pkl')
joblib.dump(le_mood, 'le_mood.pkl')
joblib.dump(le_interruptions, 'le_interruptions.pkl')
joblib.dump(le_target, 'le_target.pkl')

print("Model and processors saved.")
