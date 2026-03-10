import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

# Load dataset
data = pd.read_csv("advisory_dataset.csv")
data = pd.read_csv("advisory_dataset.csv")

print("Columns detected:")
print(data.columns)
# Features and label
X = data.drop("advisory_class", axis=1)
y = data["advisory_class"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Create model
model = RandomForestClassifier(n_estimators=100, random_state=42)

# Train
model.fit(X_train, y_train)

# Test accuracy
y_pred = model.predict(X_test)
print("\nModel Evaluation:\n")
print(classification_report(y_test, y_pred))

# Save model
joblib.dump(model, "advisory_model.pkl")

print("\n✅ Advisory Model Trained and Saved as advisory_model.pkl")