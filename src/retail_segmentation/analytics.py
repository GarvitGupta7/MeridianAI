"""Customer analytics: RFM, customer value, churn, health, and personas."""
from __future__ import annotations

import numpy as np
import pandas as pd


def _quintile_score(values: pd.Series, ascending_good: bool = True) -> pd.Series:
    ranks = values.rank(method="first", pct=True)
    if not ascending_good:
        ranks = 1 - ranks + (1 / len(values))
    return np.ceil(ranks * 5).clip(1, 5).astype(int)


def rfm_analysis(features: pd.DataFrame) -> pd.DataFrame:
    out = features[["customer_id", "recency_days", "frequency", "monetary_value"]].copy()
    out["r_score"] = _quintile_score(out["recency_days"], ascending_good=False)
    out["f_score"] = _quintile_score(out["frequency"])
    out["m_score"] = _quintile_score(out["monetary_value"])
    out["rfm_score"] = out[["r_score", "f_score", "m_score"]].sum(axis=1)
    return out


def add_customer_scores(features: pd.DataFrame) -> pd.DataFrame:
    """Add explainable proxy CLV, churn risk, and health scores without label leakage."""
    out = features.copy()
    rfm = rfm_analysis(out)
    out = out.merge(rfm, on=["customer_id", "recency_days", "frequency", "monetary_value"])
    margin = 0.35
    retention_months = np.clip(18 - out["recency_days"] / 12 + out["purchase_rate"], 1, 36)
    out["clv_estimate"] = (out["avg_order_value"] * out["purchase_rate"] * retention_months * margin).clip(lower=0)
    recency_norm = out["recency_days"] / max(1, out["recency_days"].quantile(.90))
    frequency_norm = out["frequency"] / max(1, out["frequency"].quantile(.90))
    returns_norm = out["return_rate"] / max(.01, out["return_rate"].quantile(.90))
    out["churn_risk"] = (100 * (0.62 * np.clip(recency_norm, 0, 1) + 0.25 * (1 - np.clip(frequency_norm, 0, 1)) + 0.13 * np.clip(returns_norm, 0, 1))).round(1)
    value_norm = out["monetary_value"] / max(1, out["monetary_value"].quantile(.90))
    out["health_score"] = (100 * (0.35 * out["r_score"] / 5 + 0.25 * out["f_score"] / 5 + 0.25 * out["m_score"] / 5 + 0.15 * (1 - np.clip(out["return_rate"], 0, 1)))).clip(0, 100).round(1)
    return out


def assign_personas(customers: pd.DataFrame) -> pd.DataFrame:
    """Assign priority-based, mutually exclusive retail personas."""
    out = customers.copy()
    monetary_80 = out["monetary_value"].quantile(.80)
    frequency_80 = out["frequency"].quantile(.80)
    aov_80 = out["avg_order_value"].quantile(.80)
    recency_75 = out["recency_days"].quantile(.75)
    tenure_25 = out["tenure_days"].quantile(.25)
    diversity_75 = out["product_diversity"].quantile(.75)
    conditions = [
        (out["monetary_value"] >= monetary_80) & (out["frequency"] >= frequency_80),
        (out["frequency"] >= frequency_80) & (out["recency_days"] <= out["recency_days"].quantile(.40)),
        (out["churn_risk"] >= 65) | (out["recency_days"] >= recency_75),
        (out["tenure_days"] <= tenure_25) & (out["frequency"] <= 2),
        out["avg_order_value"] >= aov_80,
        (out["product_diversity"] >= diversity_75) & (out["avg_order_value"] < aov_80),
    ]
    labels = ["Premium customers", "Loyal customers", "At-risk customers", "New customers", "Big spenders", "Bargain shoppers"]
    out["persona"] = np.select(conditions, labels, default="Regular customers")
    return out


def cohort_retention(transactions: pd.DataFrame) -> pd.DataFrame:
    """Calculate monthly customer-retention rates by first-purchase cohort."""
    purchases = transactions[transactions["revenue"] > 0].copy()
    if purchases.empty:
        return pd.DataFrame(columns=["cohort_month", "period", "active_customers", "retention_rate"])
    purchases["order_month"] = purchases["invoice_date"].dt.to_period("M")
    purchases["cohort_month"] = purchases.groupby("customer_id")["order_month"].transform("min")
    purchases = purchases.drop_duplicates(["customer_id", "order_month"])
    purchases["period"] = (purchases["order_month"].astype("int64") - purchases["cohort_month"].astype("int64")).astype(int)
    retained = purchases.groupby(["cohort_month", "period"], observed=True)["customer_id"].nunique().rename("active_customers").reset_index()
    initial = retained[retained.period == 0].set_index("cohort_month")["active_customers"]
    retained["retention_rate"] = (retained.active_customers / retained.cohort_month.map(initial) * 100).round(1)
    retained["cohort_month"] = retained["cohort_month"].astype(str)
    return retained


def campaign_recommendations(customers: pd.DataFrame) -> pd.DataFrame:
    """Create differentiated, value-aware campaign treatments.

    The engine deliberately avoids one-off persona -> discount rules. It first
    identifies the customer's commercial situation, then selects an action,
    offer, channel, and priority. High-value customers are protected from
    unnecessary discounting where possible.
    """
    out = customers.copy()
    churn = out["churn_risk"].fillna(0)
    health = out["health_score"].fillna(50)
    clv = out["clv_estimate"].fillna(0)
    spend90 = out.get("predicted_90d_spend", pd.Series(0, index=out.index)).fillna(0)
    recency = out["recency_days"].fillna(0)
    frequency = out["frequency"].fillna(0)
    persona = out["persona"].fillna("Regular customers")
    tier = out.get("customer_tier", pd.Series("Standard", index=out.index)).fillna("Standard")

    clv80 = clv.quantile(.80) if len(out) else 0
    spend80 = spend90.quantile(.80) if len(out) else 0
    freq80 = frequency.quantile(.80) if len(out) else 0
    recent_median = recency.quantile(.50) if len(out) else 30

    high_value = (clv >= clv80) | (spend90 >= spend80)
    severe_risk = churn >= 80
    high_risk = churn >= 65
    moderate_risk = churn.between(45, 64.999)
    recently_inactive = recency > recent_median
    very_inactive = recency >= out["recency_days"].quantile(.85) if len(out) else pd.Series(False, index=out.index)
    loyal = (frequency >= freq80) & (health >= 55)

    # Ordered from highest commercial urgency to lowest. The first matching
    # treatment wins, giving each customer one primary recommended campaign.
    conditions = [
        high_value & severe_risk,
        high_value & high_risk & (health < 50),
        (tier == "Platinum") & high_risk,
        persona.eq("Premium customers") & high_risk,
        persona.eq("Big spenders") & high_risk,
        persona.eq("Loyal customers") & moderate_risk,
        persona.eq("New customers") & high_risk,
        persona.eq("Bargain shoppers") & high_risk,
        severe_risk & very_inactive,
        high_risk & recently_inactive,
        high_risk,
        high_value & ~high_risk,
        persona.eq("Regular customers") & (health >= 65),
    ]
    strategies = [
        "VIP rescue",
        "High-value retention",
        "Premium protection",
        "VIP relationship retention",
        "Big-spender protection",
        "Loyalty recovery",
        "New-customer activation",
        "Bargain recovery",
        "Deep win-back",
        "Gentle reactivation",
        "Targeted re-engagement",
        "High-value growth",
        "Always-on engagement",
    ]
    actions = [
        "Personal outreach and premium retention treatment",
        "Protect the account with a personalized retention intervention",
        "Protect premium relationship before offering a discount",
        "Offer VIP access, service benefits, and personalized recommendations",
        "Use high-value product bundles and personal recommendations",
        "Restore purchase cadence with loyalty incentives",
        "Convert the first purchase into a repeat purchase",
        "Use price-sensitive bundles or targeted coupons",
        "Run a stronger win-back treatment for long-inactive customers",
        "Send a low-cost reminder or reactivation treatment",
        "Run a targeted re-engagement campaign",
        "Grow future value through cross-sell or premium recommendations",
        "Maintain engagement without a costly incentive",
    ]
    offers = [
        "VIP outreach + exclusive benefit; discount only if needed",
        "Personalized incentive up to 15%",
        "Early access + priority support",
        "VIP access + exclusive service benefit",
        "Premium bundle / complementary product offer",
        "Double loyalty points or milestone reward",
        "Second-order offer + free shipping",
        "Bundle deal or 5–10% targeted coupon",
        "15–20% win-back or strong bundle incentive",
        "Free shipping or 5% reactivation incentive",
        "Personalized product + limited-time incentive",
        "Cross-sell / premium upgrade; no automatic discount",
        "Personalized recommendation / loyalty content",
    ]
    channels = [
        "Personal outreach",
        "Email + personal outreach",
        "VIP email / account manager",
        "VIP email / account manager",
        "Email + personalized product recommendation",
        "Loyalty app / email",
        "Email / SMS",
        "Email / SMS",
        "Email + SMS",
        "Email / push",
        "Email / push",
        "Personalized email / onsite",
        "Email / onsite",
    ]
    incentive = [
        "High-touch",
        "Medium-high",
        "Non-discount",
        "Non-discount",
        "Medium",
        "Low",
        "Medium",
        "Medium",
        "High",
        "Low",
        "Medium",
        "Non-discount",
        "Non-discount",
    ]
    rationale = [
        "High predicted value and severe churn risk make this customer worth protecting with a high-touch intervention.",
        "The customer has substantial future value and elevated churn risk; protect value before relying on broad discounts.",
        "Premium status plus elevated risk calls for relationship protection rather than an automatic price cut.",
        "Premium customers showing risk should receive differentiated service and access benefits.",
        "A valuable spender is slipping; use relevant products and bundles before a blanket discount.",
        "Previously loyal behavior is weakening, so restore purchase cadence with a loyalty treatment.",
        "Early-stage customers need a second successful purchase more than a generic win-back campaign.",
        "Behavior suggests price sensitivity; targeted bundles are more appropriate than a broad discount.",
        "Long inactivity plus severe risk justifies a stronger reactivation treatment.",
        "The customer is showing early disengagement, so use a lower-cost intervention first.",
        "Elevated risk is present, but the customer does not qualify for a more specialized treatment.",
        "Healthy/high-value customers should be grown rather than unnecessarily discounted.",
        "Healthy customers are better served through engagement and recommendations than retention discounts.",
    ]

    out["campaign_strategy"] = np.select(conditions, strategies, default="Monitor / no incentive")
    out["recommended_action"] = np.select(conditions, actions, default="Monitor behavior and revisit when risk changes")
    out["suggested_offer"] = np.select(conditions, offers, default="No discount; personalized content only")
    out["recommended_channel"] = np.select(conditions, channels, default="Email / onsite")
    out["incentive_level"] = np.select(conditions, incentive, default="None")
    out["campaign_reason"] = np.select(conditions, rationale, default="Current health and risk do not justify an incentive-led campaign.")

    out["priority"] = np.select(
        [high_value & severe_risk, severe_risk, high_risk, high_value, health < 45],
        ["Critical", "Critical", "High", "High", "High"],
        default="Normal",
    )

    # A simple opportunity score ranks intervention attention without claiming
    # a causal response model. It combines value, risk and health deterioration.
    value_component = (clv / max(float(clv.quantile(.90)), 1)).clip(0, 1)
    risk_component = (churn / 100).clip(0, 1)
    deterioration_component = (1 - health / 100).clip(0, 1)
    out["campaign_opportunity_score"] = (100 * (0.45 * value_component + 0.40 * risk_component + 0.15 * deterioration_component)).round(1)

    columns = [
        "customer_id", "persona", "customer_tier", "priority", "campaign_strategy",
        "recommended_action", "suggested_offer", "recommended_channel", "incentive_level",
        "campaign_reason", "campaign_opportunity_score", "churn_risk", "health_score",
        "clv_estimate", "predicted_90d_spend", "recency_days", "frequency",
    ]
    return out[[column for column in columns if column in out.columns]].sort_values(
        ["priority", "campaign_opportunity_score"], ascending=[True, False]
    )


def assign_customer_tiers(customers: pd.DataFrame) -> pd.DataFrame:
    """Create business-friendly Bronze to Platinum customer value tiers."""
    out = customers.copy()
    score = (0.45 * out["m_score"] + 0.30 * out["f_score"] + 0.25 * out["r_score"]) * 20
    out["customer_intelligence_score"] = score.round(1)
    out["customer_tier"] = pd.cut(score, bins=[-1, 40, 60, 80, 101], labels=["Bronze", "Silver", "Gold", "Platinum"]).astype(str)
    return out
