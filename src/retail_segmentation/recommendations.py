"""Transparent product, cross-sell, and upsell recommendations."""
from __future__ import annotations

from collections import defaultdict

import pandas as pd


class RecommendationEngine:
    def __init__(self, transactions: pd.DataFrame):
        self.transactions = transactions[transactions["revenue"] > 0].copy()
        if "stock_code" in transactions.columns:
            self.product_col = "stock_code"
        elif "product_name" in transactions.columns:
            self.product_col = "product_name"
        else:
            # Product/category data is optional for a generic transaction upload.
            # Keep the core customer pipeline working without inventing product identities.
            self.product_col = "__meridian_product"
            self.transactions[self.product_col] = "Unknown product"
            self.transactions["product_name"] = "Unknown product"
        # Build the catalog without grouping by a column that is also being
        # re-inserted as an aggregate.  When a generic upload contains
        # ``product_name`` but no SKU/stock-code column, the previous
        # implementation grouped by product_name and then attempted to add
        # another product_name column during reset_index(), causing: 
        # ``cannot insert product_name, already exists``.
        if self.product_col == "product_name":
            self.catalog = (
                self.transactions.groupby("product_name", observed=True)
                .agg(
                    price=("unit_price", "median"),
                    popularity=("invoice_id", "nunique"),
                    revenue=("revenue", "sum"),
                )
                .reset_index()
                .rename(columns={"product_name": "product_id"})
            )
            self.catalog["product_name"] = self.catalog["product_id"]
            self.catalog = self.catalog[["product_id", "product_name", "price", "popularity", "revenue"]]
        else:
            self.catalog = (
                self.transactions.groupby(self.product_col, observed=True)
                .agg(
                    product_name=("product_name", "first"),
                    price=("unit_price", "median"),
                    popularity=("invoice_id", "nunique"),
                    revenue=("revenue", "sum"),
                )
                .reset_index()
                .rename(columns={self.product_col: "product_id"})
            )
        self._co_purchase = self._build_co_purchase()

    def _build_co_purchase(self) -> dict[str, dict[str, int]]:
        pairs: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        basket = self.transactions.groupby("invoice_id")[self.product_col].unique()
        for products in basket:
            for product in products:
                for other in products:
                    if product != other:
                        pairs[str(product)][str(other)] += 1
        return pairs

    def _format(self, product_ids: list[str], reason: str, limit: int) -> list[dict]:
        lookup = self.catalog.set_index("product_id")
        output = []
        for product_id in product_ids[:limit]:
            if product_id in lookup.index:
                row = lookup.loc[product_id]
                output.append({"product_id": str(product_id), "product_name": str(row["product_name"]), "price": round(float(row["price"]), 2), "reason": reason})
        return output

    def recommend_products(self, customer_id: str, limit: int = 5) -> list[dict]:
        bought = set(self.transactions.loc[self.transactions.customer_id.astype(str) == str(customer_id), self.product_col].astype(str))
        candidates: dict[str, int] = defaultdict(int)
        for product in bought:
            for related, score in self._co_purchase.get(product, {}).items():
                if related not in bought:
                    candidates[related] += score
        ranked = sorted(candidates, key=candidates.get, reverse=True)
        if not ranked:
            ranked = [str(x) for x in self.catalog.sort_values("popularity", ascending=False).product_id if str(x) not in bought]
        return self._format(ranked, "Frequently bought with your purchase history", limit)

    def cross_sell(self, product_id: str, limit: int = 5) -> list[dict]:
        related = self._co_purchase.get(str(product_id), {})
        ranked = sorted(related, key=related.get, reverse=True)
        return self._format(ranked, "Frequently bought together", limit)

    def upsell(self, product_id: str, limit: int = 3) -> list[dict]:
        catalog = self.catalog.copy()
        current = catalog[catalog.product_id.astype(str) == str(product_id)]
        if current.empty:
            return []
        price = float(current.iloc[0].price)
        products = catalog[(catalog.price > price) & (catalog.price <= price * 1.75)].sort_values(["popularity", "price"], ascending=[False, True])
        return self._format(products.product_id.astype(str).tolist(), "Higher-value alternative", limit)

