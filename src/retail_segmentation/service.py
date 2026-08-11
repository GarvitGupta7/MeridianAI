"""Orchestration layer for the complete retail segmentation workflow."""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd

from .analytics import add_customer_scores, assign_personas, assign_customer_tiers, campaign_recommendations, cohort_retention
from .clustering import ClusterResult, cluster_customers
from .config import Settings, settings
from .data import auto_map_transaction_schema, build_customer_features, clean_transactions, generate_demo_transactions, validate_transactions
from .database import RetailRepository
from .predictive import PredictiveBundle, score_predictions, train_predictive_models
from .recommendations import RecommendationEngine
from .forecasting import forecast_monthly_sales
from .eda import cleaning_audit, profile_dataset, quality_comparison, retail_eda


class RetailSegmentationService:
    def __init__(self, config: Settings = settings):
        self.config = config
        self.repository = RetailRepository(config.database_path)
        self._engine: RecommendationEngine | None = None

    def run(self, raw_transactions: pd.DataFrame, persist: bool = True) -> dict:
        mapped_transactions, _, missing_columns = auto_map_transaction_schema(raw_transactions)
        if missing_columns:
            raise ValueError("Could not detect required transaction fields: " + ", ".join(sorted(missing_columns)))
        normalized_report = validate_transactions(mapped_transactions)
        raw_overview, raw_columns = profile_dataset(mapped_transactions)
        transactions = clean_transactions(mapped_transactions)
        cleaned_overview, cleaned_columns = profile_dataset(transactions)
        quality = quality_comparison(mapped_transactions, transactions)
        cleaning = cleaning_audit(mapped_transactions, transactions)
        eda = retail_eda(transactions)
        features = build_customer_features(transactions)
        customers = assign_customer_tiers(assign_personas(add_customer_scores(features)))
        clusters: ClusterResult = cluster_customers(customers, self.config.min_clusters, self.config.max_clusters, self.config.random_state)
        bundle: PredictiveBundle = train_predictive_models(clusters.customers, self.config.random_state)
        customers = score_predictions(clusters.customers, bundle)
        campaigns = campaign_recommendations(customers)
        retention = cohort_retention(transactions)
        forecast, forecast_importance = forecast_monthly_sales(transactions)
        model_explanations = self._model_explanations(bundle)
        self._engine = RecommendationEngine(transactions)
        summary = self._summary(transactions, customers, clusters.evaluation, normalized_report, bundle.metrics)
        if persist:
            self.repository.save_frame("transactions", transactions)
            self.repository.save_frame("customers", customers)
            self.repository.save_frame("cluster_evaluation", clusters.evaluation)
            self.repository.save_frame("campaign_recommendations", campaigns)
            self.repository.save_frame("cohort_retention", retention)
            self.repository.save_frame("sales_forecast", forecast)
            self.repository.save_frame("forecast_feature_importance", forecast_importance)
            self.repository.save_frame("model_explanations", model_explanations)
            self.repository.save_frame("raw_data_overview", raw_overview)
            self.repository.save_frame("raw_column_profile", raw_columns)
            self.repository.save_frame("cleaned_data_overview", cleaned_overview)
            self.repository.save_frame("cleaned_column_profile", cleaned_columns)
            self.repository.save_frame("data_quality_comparison", quality)
            self.repository.save_frame("cleaning_audit", cleaning)
            for table_name, frame in eda.items():
                self.repository.save_frame(table_name, frame)
            self.repository.save_frame("catalog", self._engine.catalog)
            joblib.dump(clusters.model, self.config.artifacts_dir / "cluster_model.joblib")
            joblib.dump(clusters.scaler, self.config.artifacts_dir / "cluster_scaler.joblib")
            joblib.dump(bundle.models, self.config.artifacts_dir / "predictive_models.joblib")
            (self.config.artifacts_dir / "run_summary.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
        return {"transactions": transactions, "customers": customers, "evaluation": clusters.evaluation, "campaigns": campaigns, "retention": retention, "forecast": forecast, "eda": eda, "quality": quality, "cleaning_audit": cleaning, "raw_overview": raw_overview, "raw_columns": raw_columns, "cleaned_overview": cleaned_overview, "cleaned_columns": cleaned_columns, "summary": summary, "predictive_metrics": bundle.metrics, "model_explanations": model_explanations }

    def load_recommendation_engine(self) -> RecommendationEngine:
        if self._engine is None:
            self._engine = RecommendationEngine(self.repository.load_frame("transactions"))
        return self._engine

    @staticmethod
    def _summary(transactions: pd.DataFrame, customers: pd.DataFrame, evaluation: pd.DataFrame, report, predictive_metrics: dict | None = None) -> dict:
        best = evaluation[evaluation.method == "kmeans"].sort_values("silhouette", ascending=False).iloc[0]
        return {
            "data_quality": {"valid": report.valid, "warnings": report.warnings, "input_rows": report.rows, "clean_rows": len(transactions)},
            "kpis": {"revenue": round(float(transactions.revenue.sum()), 2), "customers": int(len(customers)), "orders": int(transactions.invoice_id.nunique()), "average_health": round(float(customers.health_score.mean()), 1), "at_risk_customers": int((customers.persona == "At-risk customers").sum())},
            "cluster_selection": {"algorithm": "K-Means", "clusters": int(best.n_clusters), "silhouette": round(float(best.silhouette), 3)},
            "predictive_metrics": predictive_metrics or {},
        }

    def run_demo(self) -> dict:
        return self.run(generate_demo_transactions(), persist=True)

    @staticmethod
    def _model_explanations(bundle: PredictiveBundle) -> pd.DataFrame:
        rows = []
        for name, model in bundle.models.items():
            if hasattr(model, "feature_importances_"):
                rows.extend({"model": name, "feature": feature, "importance": round(float(value), 4)} for feature, value in zip(model.feature_names_in_, model.feature_importances_))
        return pd.DataFrame(rows).sort_values(["model", "importance"], ascending=[True, False]) if rows else pd.DataFrame(columns=["model", "feature", "importance"])
