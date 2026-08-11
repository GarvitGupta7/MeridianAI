"""Forecast feature engineering, model comparison and uncertainty estimates."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

try:
    from xgboost import XGBRegressor
except Exception:  # pragma: no cover
    XGBRegressor = None


FORECAST_FEATURES = ["lag_1", "lag_2", "lag_3", "rolling_3", "rolling_6", "month", "quarter", "trend"]


def build_forecast_features(transactions: pd.DataFrame) -> pd.DataFrame:
    frame = transactions[transactions.revenue > 0].copy()
    if frame.empty:
        return pd.DataFrame(columns=["invoice_date", "revenue", *FORECAST_FEATURES])
    monthly = frame.set_index("invoice_date").resample("MS").revenue.sum().rename("revenue").reset_index()
    monthly["lag_1"] = monthly.revenue.shift(1)
    monthly["lag_2"] = monthly.revenue.shift(2)
    monthly["lag_3"] = monthly.revenue.shift(3)
    monthly["rolling_3"] = monthly.revenue.shift(1).rolling(3).mean()
    monthly["rolling_6"] = monthly.revenue.shift(1).rolling(6).mean()
    monthly["month"] = monthly.invoice_date.dt.month
    monthly["quarter"] = monthly.invoice_date.dt.quarter
    monthly["trend"] = np.arange(len(monthly))
    return monthly


def compare_forecast_models(transactions: pd.DataFrame, random_state: int = 42) -> tuple[pd.DataFrame, dict]:
    frame = build_forecast_features(transactions)
    training = frame.dropna().copy()
    if len(training) < 8:
        return pd.DataFrame(columns=["model", "mae", "rmse", "r2"]), {"features": FORECAST_FEATURES}
    split = max(3, int(len(training) * .2))
    train, test = training.iloc[:-split], training.iloc[-split:]
    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=300, min_samples_leaf=1, random_state=random_state),
    }
    if XGBRegressor is not None:
        models["XGBoost"] = XGBRegressor(n_estimators=250, max_depth=4, learning_rate=.05, subsample=.9, colsample_bytree=.9, objective="reg:squarederror", random_state=random_state, n_jobs=2)
    rows = []
    fitted = {}
    for name, model in models.items():
        model.fit(train[FORECAST_FEATURES], train.revenue)
        pred = model.predict(test[FORECAST_FEATURES])
        rows.append({"model": name, "mae": round(float(mean_absolute_error(test.revenue, pred)), 2), "rmse": round(float(np.sqrt(mean_squared_error(test.revenue, pred))), 2), "r2": round(float(r2_score(test.revenue, pred)), 4)})
        fitted[name] = model
    return pd.DataFrame(rows).sort_values(["rmse", "mae"]).reset_index(drop=True), {"features": FORECAST_FEATURES, "models": fitted, "history": frame}


def forecast_with_uncertainty(transactions: pd.DataFrame, periods: int = 3, random_state: int = 42) -> pd.DataFrame:
    frame = build_forecast_features(transactions)
    if len(frame.dropna()) < 8:
        average = float(frame.revenue.mean()) if not frame.empty else 0.0
        return pd.DataFrame([{"month": frame.invoice_date.max() + pd.DateOffset(months=i) if not frame.empty else pd.Timestamp.today().to_period("M").to_timestamp() + pd.DateOffset(months=i), "forecast_revenue": round(average, 2), "lower_bound": round(max(0, average * .8), 2), "upper_bound": round(average * 1.2, 2), "model": "Historical average"} for i in range(1, periods + 1)])
    comparison, meta = compare_forecast_models(transactions, random_state)
    best_name = str(comparison.iloc[0].model)
    model = meta["models"][best_name]
    history = meta["history"].copy()
    values = history.revenue.tolist()
    last = history.invoice_date.max()
    residuals = history.revenue.iloc[3:].to_numpy() - model.predict(history.dropna()[FORECAST_FEATURES])
    spread = float(np.std(residuals)) if len(residuals) else float(np.std(history.revenue) * .1)
    rows = []
    for step in range(1, periods + 1):
        next_month = last + pd.DateOffset(months=step)
        row = pd.DataFrame([{
            "lag_1": values[-1],
            "lag_2": values[-2] if len(values) >= 2 else values[-1],
            "lag_3": values[-3] if len(values) >= 3 else values[-1],
            "rolling_3": float(np.mean(values[-3:])),
            "rolling_6": float(np.mean(values[-6:])),
            "month": next_month.month,
            "quarter": next_month.quarter,
            "trend": len(history) + step - 1,
        }])
        prediction = max(0.0, float(model.predict(row[FORECAST_FEATURES])[0]))
        rows.append({"month": next_month, "forecast_revenue": round(prediction, 2), "lower_bound": round(max(0, prediction - 1.96 * spread), 2), "upper_bound": round(prediction + 1.96 * spread, 2), "model": best_name})
        values.append(prediction)
    return pd.DataFrame(rows)
