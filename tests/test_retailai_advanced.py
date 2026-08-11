import pandas as pd

from retail_segmentation.data import generate_demo_transactions
from retail_segmentation.service import RetailSegmentationService
from retailai_engine.churn_pipeline import ChurnPipeline
from retailai_engine.forecast_engine import build_forecast_features
from retailai_engine.recommendation_engine import AdvancedRecommendationEngine


def _analysis():
    return RetailSegmentationService().run(generate_demo_transactions(customers=80, days=240), persist=False)


def test_churn_pipeline_has_four_models_and_metrics():
    result = _analysis()
    churn = ChurnPipeline().fit(result["customers"])
    assert {"Logistic Regression", "Decision Tree", "Random Forest"}.issubset(churn.models.keys())
    assert "XGBoost" in churn.models
    assert {"accuracy", "precision", "recall", "f1", "roc_auc"}.issubset(churn.metrics.columns)
    assert churn.confusion_matrices


def test_churn_prediction_is_batchable():
    result = _analysis()
    churn = ChurnPipeline()
    churn.fit(result["customers"])
    scored = churn.predict(result["customers"].head(12))
    assert len(scored) == 12
    assert {"churn_probability", "churn_prediction", "churn_risk_band"}.issubset(scored.columns)


def test_advanced_recommendations_provide_similarity_and_popularity():
    result = _analysis()
    engine = AdvancedRecommendationEngine(result["transactions"])
    assert not engine.popularity.empty
    customer_id = str(engine.customer_product.index[0])
    assert isinstance(engine.similar_customers(customer_id), list)
    assert isinstance(engine.recommend(customer_id), list)


def test_forecast_feature_engineering_produces_lags():
    result = _analysis()
    features = build_forecast_features(result["transactions"])
    assert {"lag_1", "lag_2", "lag_3", "rolling_3", "rolling_6", "month", "quarter", "trend"}.issubset(features.columns)
