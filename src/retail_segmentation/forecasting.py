"""Explainable monthly revenue forecasting for inventory and budget planning."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor


def forecast_monthly_sales(transactions: pd.DataFrame, periods: int = 3, random_state: int = 42) -> tuple[pd.DataFrame, pd.DataFrame]:
    purchases = transactions[transactions.revenue > 0].copy()
    monthly = purchases.set_index("invoice_date").resample("MS").revenue.sum().rename("actual_revenue").reset_index()
    if monthly.empty:
        return pd.DataFrame(columns=["month", "forecast_revenue", "method"]), pd.DataFrame(columns=["feature", "importance"])
    history = monthly.copy()
    history["lag_1"] = history.actual_revenue.shift(1)
    history["lag_3"] = history.actual_revenue.shift(3)
    history["rolling_3"] = history.actual_revenue.shift(1).rolling(3).mean()
    history["month_number"] = history.invoice_date.dt.month
    training = history.dropna()
    features = ["lag_1", "lag_3", "rolling_3", "month_number"]
    if len(training) >= 4:
        model = RandomForestRegressor(n_estimators=200, random_state=random_state).fit(training[features], training.actual_revenue)
        importance = pd.DataFrame({"feature": features, "importance": model.feature_importances_}).sort_values("importance", ascending=False)
        values, forecasts, last_month = monthly.actual_revenue.tolist(), [], monthly.invoice_date.max()
        for step in range(1, periods + 1):
            next_month = last_month + pd.DateOffset(months=step)
            row = pd.DataFrame([[values[-1], values[-3] if len(values) >= 3 else values[-1], float(np.mean(values[-3:])), next_month.month]], columns=features)
            prediction = max(0, float(model.predict(row)[0]))
            forecasts.append({"month": next_month, "forecast_revenue": round(prediction, 2), "method": "Random Forest with lags"})
            values.append(prediction)
    else:
        average = float(monthly.actual_revenue.mean())
        forecasts = [{"month": monthly.invoice_date.max() + pd.DateOffset(months=step), "forecast_revenue": round(average, 2), "method": "Historical monthly average"} for step in range(1, periods + 1)]
        importance = pd.DataFrame([{"feature": "Historical monthly average", "importance": 1.0}])
    return pd.DataFrame(forecasts), importance
