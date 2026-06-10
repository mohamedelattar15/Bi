"""
ETL — Validation & Business Rules Engine

Defines all data quality rules, constraints, and business logic checks.
Each rule is typed and can be evaluated against a DataFrame.
"""

import pandas as pd
import numpy as np
from typing import Callable


class ValidationRule:
    """A single validation rule with metadata."""

    def __init__(self, name: str, description: str, severity: str,
                 check_fn: Callable[[pd.DataFrame], list[str]]):
        self.name = name
        self.description = description
        self.severity = severity  # HIGH, MEDIUM, LOW
        self.check_fn = check_fn

    def evaluate(self, df: pd.DataFrame) -> list[str]:
        """Run the check and return list of issue descriptions."""
        return self.check_fn(df)


class DataValidator:
    """
    Validates datasets against all defined business rules.
    Rules are organized by table for clarity.
    """

    def __init__(self):
        self._rules: dict[str, list[ValidationRule]] = {}
        self._register_all_rules()

    def _register_all_rules(self) -> None:
        """Register all validation rules organized by table."""

        # ── Category Rules ──
        self._rules["categories"] = [
            ValidationRule(
                "pk_unique", "CategoryID must be unique", "HIGH",
                lambda df: self._check_unique(df, "CategoryID", "categories")
            ),
            ValidationRule(
                "name_not_null", "CategoryName must not be null", "HIGH",
                lambda df: self._check_not_null(df, "CategoryName")
            ),
        ]

        # ── Product Rules ──
        self._rules["products"] = [
            ValidationRule(
                "pk_unique", "ProductID must be unique", "HIGH",
                lambda df: self._check_unique(df, "ProductID", "products")
            ),
            ValidationRule(
                "price_positive", "Price must be >= 0", "HIGH",
                lambda df: self._check_min(df, "Price", 0)
            ),
            ValidationRule(
                "category_exists", "CategoryID must exist", "HIGH",
                lambda df: self._check_not_null(df, "CategoryID")
            ),
        ]

        # ── Customer Rules ──
        self._rules["customers"] = [
            ValidationRule(
                "pk_unique", "CustomerID must be unique", "HIGH",
                lambda df: self._check_unique(df, "CustomerID", "customers")
            ),
            ValidationRule(
                "city_exists", "CityID must be present", "MEDIUM",
                lambda df: self._check_not_null(df, "CityID")
            ),
        ]

        # ── Employee Rules ──
        self._rules["employees"] = [
            ValidationRule(
                "pk_unique", "EmployeeID must be unique", "HIGH",
                lambda df: self._check_unique(df, "EmployeeID", "employees")
            ),
            ValidationRule(
                "birthdate_valid", "BirthDate must be valid dates", "MEDIUM",
                lambda df: self._check_date_parseable(df, "BirthDate")
            ),
            ValidationRule(
                "hiredate_valid", "HireDate must be valid dates", "MEDIUM",
                lambda df: self._check_date_parseable(df, "HireDate")
            ),
        ]

        # ── Sales Rules ──
        self._rules["sales"] = [
            ValidationRule(
                "pk_unique", "SalesID must be unique", "HIGH",
                lambda df: self._check_unique(df, "SalesID", "sales")
            ),
            ValidationRule(
                "quantity_positive", "Quantity must be >= 0", "HIGH",
                lambda df: self._check_min(df, "Quantity", 0)
            ),
            ValidationRule(
                "totalprice_non_negative", "TotalPrice must be >= 0", "HIGH",
                lambda df: self._check_min(df, "TotalPrice", 0)
            ),
            ValidationRule(
                "discount_non_negative", "Discount must be >= 0", "HIGH",
                lambda df: self._check_min(df, "Discount", 0)
            ),
            ValidationRule(
                "salesdate_not_null", "SalesDate must not be null", "HIGH",
                lambda df: self._check_not_null(df, "SalesDate")
            ),
            ValidationRule(
                "fk_employee", "SalesPersonID must be present", "HIGH",
                lambda df: self._check_not_null(df, "SalesPersonID")
            ),
            ValidationRule(
                "fk_customer", "CustomerID must be present", "HIGH",
                lambda df: self._check_not_null(df, "CustomerID")
            ),
            ValidationRule(
                "fk_product", "ProductID must be present", "HIGH",
                lambda df: self._check_not_null(df, "ProductID")
            ),
            ValidationRule(
                "transaction_not_null", "TransactionNumber must not be null", "MEDIUM",
                lambda df: self._check_not_null(df, "TransactionNumber")
            ),
        ]

    def get_rules(self, table: str) -> list[ValidationRule]:
        """Get all validation rules for a specific table."""
        return self._rules.get(table, [])

    def get_all_rules(self) -> dict[str, list[ValidationRule]]:
        """Get all rules organized by table."""
        return self._rules

    def validate(self, df: pd.DataFrame, table: str) -> list[str]:
        """
        Validate a DataFrame against all rules for a table.

        Args:
            df: DataFrame to validate
            table: Table name (e.g. 'sales', 'customers')

        Returns:
            List of issue descriptions (empty if valid)
        """
        all_issues = []
        for rule in self.get_rules(table):
            issues = rule.evaluate(df)
            all_issues.extend(issues)
        return all_issues

    # ── Check Implementations ──

    def _check_unique(self, df: pd.DataFrame, col: str,
                      table: str) -> list[str]:
        issues = []
        if col not in df.columns:
            return [f"Column '{col}' missing in {table}"]
        dups = df[col].duplicated().sum()
        if dups > 0:
            issues.append(
                f"[HIGH] {dups:,} duplicate values in {table}.{col}"
            )
        return issues

    def _check_not_null(self, df: pd.DataFrame, col: str) -> list[str]:
        issues = []
        if col not in df.columns:
            return [f"Column '{col}' missing"]
        nulls = df[col].isnull().sum()
        if nulls > 0:
            pct = nulls / len(df) * 100
            issues.append(
                f"[HIGH] {nulls:,} null values in '{col}' ({pct:.1f}%)"
            )
        return issues

    def _check_min(self, df: pd.DataFrame, col: str,
                   min_val: float) -> list[str]:
        issues = []
        if col not in df.columns:
            return [f"Column '{col}' missing"]
        if pd.api.types.is_numeric_dtype(df[col]):
            violations = (df[col] < min_val).sum()
            if violations > 0:
                issues.append(
                    f"[HIGH] {violations:,} rows with {col} < {min_val}"
                )
        return issues

    def _check_date_parseable(self, df: pd.DataFrame,
                              col: str) -> list[str]:
        issues = []
        if col not in df.columns:
            return [f"Column '{col}' missing"]
        parsed = pd.to_datetime(df[col], errors="coerce")
        nulls = parsed.isnull().sum()
        if nulls > 0:
            issues.append(
                f"[MEDIUM] {nulls:,} unparseable dates in '{col}'"
            )
        return issues
