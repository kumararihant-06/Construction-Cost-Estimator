import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from data_pipeline import load_and_process, FEATURE_COLUMNS

# Module-level variables — live in memory after training
MODEL = None
TRAINING_COLUMNS = None

def train():
    global MODEL, TRAINING_COLUMNS

    df = load_and_process()

    # Split into features (X) and target (y)
    X = df.drop(columns=['total_cost'])
    y = df['total_cost']

    # Save training columns for prediction alignment
    TRAINING_COLUMNS = X.columns.tolist()

    # Split into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train Linear Regression
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    lr_score = r2_score(y_test, lr.predict(X_test))

    # Train Random Forest
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    rf_score = r2_score(y_test, rf.predict(X_test))

    print(f"Linear Regression R2: {lr_score:.4f}")
    print(f"Random Forest R2:     {rf_score:.4f}")

    # Keep the better model
    MODEL = rf if rf_score > lr_score else lr
    print(f"Selected: {'Random Forest' if MODEL == rf else 'Linear Regression'}")

def predict(input_dict):
    global MODEL, TRAINING_COLUMNS

    # Convert input to DataFrame
    input_df = pd.DataFrame([input_dict])

    # One-hot encode with drop_first=False so all categories appear
    input_df = pd.get_dummies(input_df,
                               columns=['project_type', 'location_tier', 'material_grade'],
                               drop_first=False)

    # Manually drop the same baseline columns dropped during training
    # Training used drop_first=True which drops: Commercial, Tier1, Budget
    cols_to_drop = ['project_type_Commercial', 'location_tier_Tier1', 'material_grade_Budget']
    for col in cols_to_drop:
        if col in input_df.columns:
            input_df = input_df.drop(columns=[col])

    # Align columns with training data — fills any missing columns with 0
    input_df = input_df.reindex(columns=TRAINING_COLUMNS, fill_value=0)

    prediction = MODEL.predict(input_df)[0]
    prediction = max(float(prediction), 500000)
    return round(float(prediction), 2)

def confidence_interval(prediction):
    low = round(max(prediction * 0.85, 500000), 2)
    high = round(prediction * 1.15, 2)
    return {"low": low, "high": high}

def get_model_name():
    from sklearn.ensemble import RandomForestRegressor
    return "RandomForestRegressor" if isinstance(MODEL, RandomForestRegressor) else "LinearRegression"

if __name__ == '__main__':
    train()

    # Test prediction
    sample = {
        'project_type': 'Commercial',
        'location_tier': 'Tier1',
        'size_sqft': 25000,
        'num_floors': 5,
        'material_grade': 'Premium',
        'duration_weeks': 40,
        'labor_cost': 0,
        'material_cost': 0
    }
    result = predict(sample)
    print(f"\nSample prediction: ₹{result:,.2f}")
    print(f"Confidence interval: {confidence_interval(result)}")