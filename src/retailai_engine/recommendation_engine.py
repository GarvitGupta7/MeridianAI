"""Collaborative, similarity and popularity recommendation engine."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class RecommendationArtifacts:
    customer_similarity: pd.DataFrame
    product_similarity: pd.DataFrame
    popularity: pd.DataFrame


class AdvancedRecommendationEngine:
    """Hybrid recommendation engine built from transaction co-occurrence."""

    def __init__(self, transactions: pd.DataFrame):
        required = {"customer_id", "invoice_id", "revenue"}
        missing = required - set(transactions.columns)
        if missing:
            raise ValueError(f"Missing recommendation columns: {', '.join(sorted(missing))}")
        self.transactions = transactions[transactions.revenue > 0].copy()
        self.product_col = "stock_code" if "stock_code" in self.transactions.columns else "product_name"
        if self.product_col not in self.transactions.columns:
            self.transactions["product_name"] = "Unknown product"
            self.product_col = "product_name"
        self.transactions[self.product_col] = self.transactions[self.product_col].fillna("Unknown").astype(str)
        self.customer_product = pd.crosstab(self.transactions["customer_id"].astype(str), self.transactions[self.product_col])
        self.product_customer = self.customer_product.T
        self.customer_similarity = pd.DataFrame(cosine_similarity(self.customer_product), index=self.customer_product.index, columns=self.customer_product.index)
        self.product_similarity = pd.DataFrame(cosine_similarity(self.product_customer), index=self.product_customer.index, columns=self.product_customer.index)
        popularity = self.transactions.groupby(self.product_col, observed=True).agg(
            purchases=("invoice_id", "nunique"),
            customers=("customer_id", "nunique"),
            revenue=("revenue", "sum"),
        ).reset_index().rename(columns={self.product_col: "product_id"})
        self.popularity = popularity.sort_values(["customers", "purchases", "revenue"], ascending=False).reset_index(drop=True)

    def artifacts(self) -> RecommendationArtifacts:
        return RecommendationArtifacts(self.customer_similarity, self.product_similarity, self.popularity)

    def popular_products(self, limit: int = 10) -> list[dict]:
        return self.popularity.head(limit).to_dict(orient="records")

    def similar_customers(self, customer_id: str, limit: int = 10) -> list[dict]:
        customer_id = str(customer_id)
        if customer_id not in self.customer_similarity.index:
            return []
        row = self.customer_similarity.loc[customer_id].drop(index=customer_id).sort_values(ascending=False).head(limit)
        return [{"customer_id": str(idx), "similarity": round(float(value), 4)} for idx, value in row.items()]

    def similar_products(self, product_id: str, limit: int = 10) -> list[dict]:
        product_id = str(product_id)
        if product_id not in self.product_similarity.index:
            return []
        row = self.product_similarity.loc[product_id].drop(index=product_id).sort_values(ascending=False).head(limit)
        return [{"product_id": str(idx), "similarity": round(float(value), 4)} for idx, value in row.items()]

    def recommend(self, customer_id: str, limit: int = 10) -> list[dict]:
        customer_id = str(customer_id)
        if customer_id not in self.customer_product.index:
            return self.popular_products(limit)
        purchased = set(self.customer_product.loc[customer_id][lambda s: s > 0].index)
        neighbours = self.customer_similarity.loc[customer_id].drop(index=customer_id).sort_values(ascending=False).head(20)
        scores: dict[str, float] = {}
        for neighbour, similarity in neighbours.items():
            if similarity <= 0:
                continue
            for product, quantity in self.customer_product.loc[neighbour][lambda s: s > 0].items():
                if product not in purchased:
                    scores[product] = scores.get(product, 0.0) + float(similarity) * float(quantity)
        ranked = sorted(scores, key=scores.get, reverse=True)
        if not ranked:
            return self.popular_products(limit)
        popularity = self.popularity.set_index("product_id")
        output = []
        for product in ranked[:limit]:
            row = popularity.loc[product] if product in popularity.index else None
            output.append({
                "product_id": str(product),
                "score": round(float(scores[product]), 4),
                "customers": int(row.customers) if row is not None else 0,
                "revenue": round(float(row.revenue), 2) if row is not None else 0.0,
                "reason": "Customers with similar purchase patterns also bought this product",
            })
        return output
