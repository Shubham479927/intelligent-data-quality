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
    """
    Automatically select suitable numeric features
    for anomaly detection.
    """

    numeric_columns = df.select_dtypes(
        include=["number"]
    ).columns.tolist()

    # Exclude identifier-like columns
    features = [
        column
        for column in numeric_columns
        if not any(
            keyword in column.lower()
            for keyword in ["id", "code", "zip", "postal"]
        )
    ]

    if not features:
        raise ValueError(
            "No suitable numeric features found "
            "for anomaly detection."
        )

    X = df[features]

    print("\nFeatures selected:")
    print(features)

    print("\nFeature preview:")
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

def calculate_feature_unusualness(X):

    feature_scores = pd.DataFrame(index=X.index)

    for column in X.columns:
        median = X[column].median()
        mad = (X[column] - median).abs().median()

        if mad == 0:
            feature_scores[column] = 0
        else:
            feature_scores[column] = (
                (X[column] - median).abs() / mad
            )

    print("\nFeature unusualness calculated!")

    return feature_scores

def save_results(df, X, predictions, scores):

    results_df = df.copy()

    results_df["anomaly_prediction"] = predictions
    results_df["anomaly_score"] = scores

    results_df["anomaly_status"] = results_df["anomaly_prediction"].map({
        1: "Normal",
        -1: "Anomaly"
    })

    feature_scores = calculate_feature_unusualness(X)

    for column in feature_scores.columns:
        results_df[f"{column}_unusualness"] = feature_scores[column]

    results_df["top_unusual_feature"] = feature_scores.idxmax(axis=1)
    results_df["top_unusualness_score"] = feature_scores.max(axis=1)
    def explain_anomaly(row):

        if row["anomaly_status"] != "Anomaly":
            return "No significant anomaly detected"

        feature = row["top_unusual_feature"]
        value = row[feature]
        median = X[feature].median()

        if value > median:
            direction = "high"
        else:
            direction = "low"

        return (
            f"{feature} = {value:.2f} is unusually {direction} "
            f"(median = {median:.2f})"
        )


    results_df["anomaly_explanation"] = results_df.apply(
        explain_anomaly,
        axis=1
    )

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

    results_df = save_results(df, X, predictions, scores)
