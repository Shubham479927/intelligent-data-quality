import pandas as pd

from src.anomaly_detection.anomaly_detector import (
    select_features,
    preprocess_features,
    train_model,
    detect_anomalies,
    calculate_anomaly_scores,
)


def test_feature_selection_excludes_id_columns():
    df = pd.DataFrame({
        "order_id": [1, 2, 3],
        "customer_id": [101, 102, 103],
        "quantity": [2, 3, 1],
        "unit_price": [100.0, 200.0, 50.0],
        "customer_age": [25, 30, 28]
    })

    X = select_features(df)

    assert "order_id" not in X.columns
    assert "customer_id" not in X.columns
    assert "quantity" in X.columns
    assert "unit_price" in X.columns
    assert "customer_age" in X.columns


def test_anomaly_detection_returns_predictions_and_scores():
    df = pd.DataFrame({
        "order_id": range(1, 21),
        "customer_id": range(101, 121),
        "quantity": [2] * 19 + [100],
        "unit_price": [100.0] * 20,
        "customer_age": [30] * 20
    })

    X = select_features(df)
    X = preprocess_features(X)

    model = train_model(X)
    predictions = detect_anomalies(model, X)
    scores = calculate_anomaly_scores(model, X)

    assert len(predictions) == len(df)
    assert len(scores) == len(df)
    assert set(predictions).issubset({-1, 1})