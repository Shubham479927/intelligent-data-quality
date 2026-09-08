import pandas as pd
from sklearn.ensemble import IsolationForest


def load_data():

    file_path = "data/processed/cleaned_data.csv"

    df = pd.read_csv(file_path)

    print("Data loaded successfully!")
    print("Rows:", len(df))
    print("Columns:", len(df.columns))

    return df


def select_features(df):

    features = [
        "quantity",
        "unit_price",
        "total_amount",
        "customer_age"
    ]

    X = df[features]

    print("\nFeatures selected:")
    print(X.head())

    return X

def preprocess_features(X):

    print("\nMissing values:")
    print(X.isnull().sum())

    X = X.fillna(X.median())

    print("\nPreprocessing completed!")

    return X

def train_model(X):

    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42
    )

    model.fit(X)

    print("\nIsolation Forest model trained successfully!")

    return model

def detect_anomalies(model, X):

    predictions = model.predict(X)

    print("\nAnomaly detection completed!")

    print("Normal records:", sum(predictions == 1))
    print("Anomalous records:", sum(predictions == -1))

    return predictions

def calculate_anomaly_scores(model, X):

    scores = model.decision_function(X)

    print("\nAnomaly scores calculated!")

    print("First 10 anomaly scores:")
    print(scores[:10])

    return scores

def save_results(df, predictions, scores):

    results_df = df.copy()

    results_df["anomaly_prediction"] = predictions
    results_df["anomaly_score"] = scores

    results_df["anomaly_status"] = results_df["anomaly_prediction"].map({
        1: "Normal",
        -1: "Anomaly"
    })

    output_path = "data/anomaly_results.csv"

    results_df.to_csv(output_path, index=False)

    print("\nAnomaly results saved successfully!")
    print("Output:", output_path)

    print("\nAnomaly summary:")
    print(results_df["anomaly_status"].value_counts())

    return results_df

if __name__ == "__main__":

    df = load_data()

    X = select_features(df)

    X = preprocess_features(X)

    model = train_model(X)

    predictions = detect_anomalies(model, X)

    scores = calculate_anomaly_scores(model, X)

    results_df = save_results(df, predictions, scores)