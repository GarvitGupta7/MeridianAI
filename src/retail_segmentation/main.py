"""Command-line entry point."""
from __future__ import annotations

import argparse
import json

import pandas as pd

from .service import RetailSegmentationService


def main() -> None:
    parser = argparse.ArgumentParser(description="Retail customer segmentation pipeline")
    parser.add_argument("--input", help="CSV file with retail transactions")
    parser.add_argument("--demo", action="store_true", help="Run using generated demo data")
    args = parser.parse_args()
    service = RetailSegmentationService()
    if args.demo:
        result = service.run_demo()
    elif args.input:
        result = service.run(pd.read_csv(args.input))
    else:
        parser.error("provide --input PATH or --demo")
    print(json.dumps({**result["summary"], "predictive_metrics": result["predictive_metrics"]}, indent=2))


if __name__ == "__main__":
    main()
