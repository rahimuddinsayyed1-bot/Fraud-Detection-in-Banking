import os
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# Ensure the model directory exists
os.makedirs("model", exist_ok=True)

print("Generating synthetic banking dataset...")
np.random.seed(42)
n_samples = 3000

amounts = np.random.exponential(scale=550, size=n_samples)
hours = np.random.randint(0, 24, size=n_samples)
devices = np.random.choice([0, 1], size=n_samples, p=[0.25, 0.75])
locations = np.random.choice(range(25), size=n_samples)

fraud_risk = (
    (amounts * 0.04)
    + ((hours < 5).astype(int) * 35)
    + ((devices == 0).astype(int) * 40)
)
labels = (fraud_risk > 65).astype(int)

X = np.column_stack([amounts, hours, devices, locations])
y = labels

print("Training RandomForest v2.0 AI Engine...")
model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
model.fit(X, y)

save_path = os.path.join("model", "fraud_model_v2.pkl")
with open(save_path, "wb") as f:
  pickle.dump(model, f)

print(f"Model trained successfully! Saved to '{save_path}'")
