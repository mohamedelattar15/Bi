"""
ETL — Extract Module

Responsible for reading raw CSV files from the dataset directory.
Validates file existence, headers, and basic structure before passing
data to the transformer.
"""

import os
import pandas as pd
from typing import Optional


class DataExtractor:
    """Reads raw CSV files and validates their structure."""

    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path

    def extract(self, filename: str, **kwargs) -> pd.DataFrame:
        """
        Read a CSV file from the dataset directory.

        Args:
            filename: CSV filename (e.g. 'categories.csv')
            **kwargs: Additional arguments passed to pd.read_csv()

        Returns:
            DataFrame with raw data

        Raises:
            FileNotFoundError: If the CSV file doesn't exist
            ValueError: If the CSV is empty or has no columns
        """
        path = os.path.join(self.dataset_path, filename)

        if not os.path.exists(path):
            raise FileNotFoundError(f"Dataset file not found: {path}")

        df = pd.read_csv(path, **kwargs)

        if df.empty:
            raise ValueError(f"CSV file is empty: {filename}")

        return df

    def validate_columns(self, df: pd.DataFrame, expected: list[str],
                         filename: str) -> list[str]:
        """
        Validate that required columns exist in the DataFrame.

        Args:
            df: DataFrame to validate
            expected: List of expected column names
            filename: Source filename (for error messages)

        Returns:
            List of missing columns (empty if all present)
        """
        missing = [col for col in expected if col not in df.columns]
        if missing:
            print(f"  ⚠️  {filename}: missing columns {missing}")
        return missing
