"""Warehouse resource definitions for Sophia AI"""

from pulumi_snowflake import Warehouse


def create_warehouses():
    """Create compute warehouses for different workloads"""
    warehouses = {}

    # Analytics warehouse for queries and reporting
    warehouses["analytics"] = Warehouse(
        "analytics-warehouse",
        name="SOPHIA_AI_ANALYTICS_WH",
        comment="Warehouse for analytics queries and reporting",
        warehouse_size="SMALL",
        auto_suspend=300,  # 5 minutes
        auto_resume=True,
        initially_suspended=True,
        min_cluster_count=1,
        max_cluster_count=3,
        scaling_policy="STANDARD",
    )

    # ETL warehouse for data processing
    warehouses["etl"] = Warehouse(
        "etl-warehouse",
        name="SOPHIA_AI_ETL_WH",
        comment="Warehouse for ETL and data processing tasks",
        warehouse_size="MEDIUM",
        auto_suspend=60,  # 1 minute
        auto_resume=True,
        initially_suspended=True,
        min_cluster_count=1,
        max_cluster_count=2,
        scaling_policy="ECONOMY",
    )

    # ML warehouse for embeddings and AI workloads
    warehouses["ml"] = Warehouse(
        "ml-warehouse",
        name="SOPHIA_AI_ML_WH",
        comment="Warehouse for ML operations and embedding generation",
        warehouse_size="LARGE",
        auto_suspend=120,  # 2 minutes
        auto_resume=True,
        initially_suspended=True,
        min_cluster_count=1,
        max_cluster_count=1,
        scaling_policy="STANDARD",
    )

    return warehouses
