
import pandas as pd
import numpy as np
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score
)

# 1. Load cleaned dataset
df = pd.read_csv("data/cleaned_orders.csv")

# 2. Feature engineering
df["order_datetime"] = pd.to_datetime(
    df["order_datetime"],
    format="%d-%m-%Y %H:%M",
    errors="coerce"
)

df["order_month"] = df["order_datetime"].dt.month
df["order_hour"] = df["order_datetime"].dt.hour
df["order_dayofweek"] = df["order_datetime"].dt.day_of_week

df["address_length"] = df["address"].fillna("").astype(str).str.len()

df["address_very_short"] = (
    df["address_length"] <= 15
).astype(int)

df["pincode_prefix"] = df["pincode"].apply(
    lambda x: str(int(x))[:3] if pd.notna(x) else np.nan
)

# 3. Select input features
features = [
    "city",
    "state",
    "pincode_prefix",
    "order_value",
    "num_items",
    "customer_prior_orders",
    "customer_prior_rto",
    "utm_source",
    "courier",
    "order_month",
    "order_hour",
    "order_dayofweek",
    "address_length",
    "address_very_short"
]

X = df[features]
y = df["is_rto"]

# 4. Separate categorical and numerical columns
categorical_features = [
    "city",
    "state",
    "pincode_prefix",
    "utm_source",
    "courier"
]

numerical_features = [
    "order_value",
    "num_items",
    "customer_prior_orders",
    "customer_prior_rto",
    "order_month",
    "order_hour",
    "order_dayofweek",
    "address_length",
    "address_very_short"
]

# 5. Handle missing values and encode categories
preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("encoder", OneHotEncoder(handle_unknown="ignore"))
            ]),
            categorical_features
        ),
        (
            "numerical",
            SimpleImputer(strategy="median"),
            numerical_features
        )
    ]
)

# 6. Create Random Forest model
model = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", RandomForestClassifier(
        n_estimators=400,
        min_samples_leaf=5,
        class_weight="balanced_subsample",
        random_state=42,
        n_jobs=-1
    ))
])

# 7. Split data into training and testing
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# 8. Train model
print("Training Random Forest Model...")

model.fit(X_train, y_train)

# 9. Make predictions
predictions = model.predict(X_test)

probabilities = model.predict_proba(X_test)[:, 1]

# 10. Evaluate model
print("\nMODEL EVALUATION")

print(
    "Accuracy:",
    round(accuracy_score(y_test, predictions) * 100, 2),
    "%"
)

print(
    "ROC-AUC:",
    round(roc_auc_score(y_test, probabilities), 3)
)

print("\nClassification Report:")
print(classification_report(y_test, predictions))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, predictions))

# 11. Save trained model
os.makedirs("models", exist_ok=True)

joblib.dump(model, "models/rto_model.pkl")

print("\nModel saved successfully!")
print("Location: models/rto_model.pkl")
