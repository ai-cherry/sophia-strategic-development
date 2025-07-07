import logging

import pandas as pd

logger = logging.getLogger(__name__)


class DataValidationError(Exception):
    pass


class EmptyResultError(Exception):
    pass


class DataTransformer:
    """Transform and validate data from various sources"""

    @staticmethod
    def transform_snowflake_results(results: list[dict]) -> pd.DataFrame:
        """Transform Snowflake results to standardized format"""
        if not results:
            raise EmptyResultError("Received empty results from Snowflake")

        df = pd.DataFrame(results)

        # Standardize column names
        df.columns = [str(col).lower().replace(" ", "_") for col in df.columns]

        # Convert data types
        for col in df.columns:
            if "date" in col or "time" in col:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        # Handle nulls for common columns
        if "amount" in df.columns:
            df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
        if "probability" in df.columns:
            df["probability"] = pd.to_numeric(
                df["probability"], errors="coerce"
            ).fillna(0)
        if "stage" in df.columns:
            df["stage"] = df["stage"].fillna("Unknown")

        logger.info(f"Transformed Snowflake results. Shape: {df.shape}")
        return df

    @staticmethod
    def validate_sales_data(data: pd.DataFrame) -> bool:
        """Validate sales data structure and content"""
        required_columns = ["deal_id", "deal_name", "amount", "stage"]

        if data.empty:
            raise EmptyResultError("Sales data DataFrame is empty.")

        # Check required columns
        missing_cols = [col for col in required_columns if col not in data.columns]
        if missing_cols:
            raise DataValidationError(f"Missing required sales columns: {missing_cols}")

        # Check data types
        if not pd.api.types.is_numeric_dtype(data["amount"]):
            raise DataValidationError("'amount' column must be numeric")

        # Check data freshness (example: deals should have recent activity)
        if "last_activity_date" in data.columns:
            # Ensure the column is datetime
            if not pd.api.types.is_datetime64_any_dtype(data["last_activity_date"]):
                data["last_activity_date"] = pd.to_datetime(
                    data["last_activity_date"], errors="coerce"
                )

            # Drop rows where date conversion failed
            valid_dates = data.dropna(subset=["last_activity_date"])
            if not valid_dates.empty:
                latest_activity = valid_dates["last_activity_date"].max()
                if pd.Timestamp.now() - latest_activity > pd.Timedelta(days=30):
                    logger.warning(
                        "Sales data may be stale (last activity > 30 days ago)"
                    )

        logger.info("Sales data validation passed.")
        return True

    @staticmethod
    def transform_gong_calls(calls: list[dict]) -> pd.DataFrame:
        """Transforms Gong call data."""
        if not calls:
            raise EmptyResultError("Received no calls from Gong")

        df = pd.DataFrame(calls)
        # Select and rename columns for standardization
        if "records" in df.columns:
            df = pd.json_normalize(df["records"])

        # Basic transformation
        df.columns = [str(col).lower().replace(" ", "_") for col in df.columns]

        logger.info(f"Transformed Gong calls. Shape: {df.shape}")
        return df
