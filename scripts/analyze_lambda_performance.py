#!/usr/bin/env python3
"""Analyze Lambda Labs performance metrics."""

import asyncio
import json
from datetime import datetime
from pathlib import Path

from infrastructure.adapters.snowflake_adapter import SnowflakeConfigManager


async def analyze_performance():
    """Analyze Lambda Labs performance from Snowflake data."""
    print("📊 Analyzing Lambda Labs Performance...")

    async with SnowflakeConfigManager() as snowflake:
        # Get performance metrics
        metrics = {}

        # 1. Overall statistics
        print("\n📈 Overall Statistics (Last 30 days)")
        overall_stats = await snowflake.execute_query(
            """
            SELECT
                COUNT(*) as total_requests,
                COUNT(DISTINCT user_id) as unique_users,
                SUM(total_tokens) as total_tokens,
                SUM(cost_usd) as total_cost,
                AVG(latency_ms) as avg_latency,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY latency_ms) as p50_latency,
                PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) as p95_latency,
                PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY latency_ms) as p99_latency
            FROM LAMBDA_LABS_USAGE
            WHERE timestamp >= DATEADD('day', -30, CURRENT_TIMESTAMP())
        """
        )

        if overall_stats:
            stats = overall_stats[0]
            print(f"  Total Requests: {stats['TOTAL_REQUESTS']:,}")
            print(f"  Unique Users: {stats['UNIQUE_USERS']}")
            print(f"  Total Tokens: {stats['TOTAL_TOKENS']:,}")
            print(f"  Total Cost: ${stats['TOTAL_COST']:.2f}")
            print(f"  Avg Latency: {stats['AVG_LATENCY']:.0f}ms")
            print(f"  P50 Latency: {stats['P50_LATENCY']:.0f}ms")
            print(f"  P95 Latency: {stats['P95_LATENCY']:.0f}ms")
            print(f"  P99 Latency: {stats['P99_LATENCY']:.0f}ms")

            metrics["overall"] = stats

        # 2. Model performance comparison
        print("\n🤖 Model Performance Comparison")
        model_stats = await snowflake.execute_query(
            """
            SELECT * FROM LAMBDA_LABS_MODEL_PERFORMANCE
            ORDER BY usage_count DESC
        """
        )

        if model_stats:
            print(
                f"{'Model':<40} {'Backend':<10} {'Requests':<10} {'Avg Cost/M':<12} {'P50 Latency':<12}"
            )
            print("-" * 84)

            for model in model_stats:
                print(
                    f"{model['MODEL']:<40} {model['BACKEND']:<10} "
                    f"{model['USAGE_COUNT']:<10} ${model['AVG_COST_PER_MILLION']:<11.2f} "
                    f"{model['P50_LATENCY']:<12.0f}ms"
                )

            metrics["models"] = model_stats

        # 3. Daily trends
        print("\n📅 Daily Trends (Last 7 days)")
        daily_trends = await snowflake.execute_query(
            """
            SELECT
                DATE_TRUNC('day', timestamp) as date,
                COUNT(*) as requests,
                SUM(cost_usd) as cost,
                AVG(latency_ms) as avg_latency,
                SUM(CASE WHEN error_message IS NOT NULL THEN 1 ELSE 0 END) as errors
            FROM LAMBDA_LABS_USAGE
            WHERE timestamp >= DATEADD('day', -7, CURRENT_TIMESTAMP())
            GROUP BY 1
            ORDER BY 1 DESC
        """
        )

        if daily_trends:
            print(
                f"{'Date':<12} {'Requests':<10} {'Cost':<10} {'Avg Latency':<12} {'Errors':<8}"
            )
            print("-" * 52)

            for day in daily_trends:
                date_str = day["DATE"].strftime("%Y-%m-%d")
                print(
                    f"{date_str:<12} {day['REQUESTS']:<10} "
                    f"${day['COST']:<9.2f} {day['AVG_LATENCY']:<12.0f}ms {day['ERRORS']:<8}"
                )

            metrics["daily_trends"] = daily_trends

        # 4. Backend distribution
        print("\n🔄 Backend Distribution")
        backend_dist = await snowflake.execute_query(
            """
            SELECT
                backend,
                COUNT(*) as requests,
                SUM(cost_usd) as total_cost,
                AVG(latency_ms) as avg_latency,
                COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() as percentage
            FROM LAMBDA_LABS_USAGE
            WHERE timestamp >= DATEADD('day', -30, CURRENT_TIMESTAMP())
            GROUP BY 1
        """
        )

        if backend_dist:
            for backend in backend_dist:
                print(
                    f"  {backend['BACKEND']}: {backend['PERCENTAGE']:.1f}% "
                    f"({backend['REQUESTS']} requests, ${backend['TOTAL_COST']:.2f}, "
                    f"{backend['AVG_LATENCY']:.0f}ms avg)"
                )

            metrics["backend_distribution"] = backend_dist

        # 5. Error analysis
        print("\n⚠️ Error Analysis")
        error_stats = await snowflake.execute_query(
            """
            SELECT
                DATE_TRUNC('day', timestamp) as date,
                COUNT(*) as error_count,
                COUNT(DISTINCT error_message) as unique_errors
            FROM LAMBDA_LABS_USAGE
            WHERE error_message IS NOT NULL
                AND timestamp >= DATEADD('day', -7, CURRENT_TIMESTAMP())
            GROUP BY 1
            ORDER BY 1 DESC
        """
        )

        if error_stats:
            total_errors = sum(e["ERROR_COUNT"] for e in error_stats)
            print(f"  Total Errors (7 days): {total_errors}")

            if total_errors > 0:
                print("\n  Daily Breakdown:")
                for error in error_stats:
                    date_str = error["DATE"].strftime("%Y-%m-%d")
                    print(
                        f"    {date_str}: {error['ERROR_COUNT']} errors "
                        f"({error['UNIQUE_ERRORS']} unique)"
                    )

            metrics["errors"] = error_stats

        # 6. Cost optimization opportunities
        print("\n💡 Cost Optimization Opportunities")
        optimizations = await snowflake.execute_query(
            """
            SELECT * FROM TABLE(IDENTIFY_COST_OPTIMIZATIONS())
            ORDER BY estimated_monthly_savings DESC
            LIMIT 5
        """
        )

        if optimizations:
            total_savings = 0
            for opt in optimizations:
                print(f"\n  {opt['OPTIMIZATION_TYPE']}:")
                print(f"    Current: {opt['CURRENT_MODEL']}")
                print(f"    Recommended: {opt['RECOMMENDED_MODEL']}")
                print(f"    Monthly Savings: ${opt['ESTIMATED_MONTHLY_SAVINGS']:.2f}")
                print(f"    Affected Requests: {opt['AFFECTED_REQUESTS']}")
                print(f"    {opt['RECOMMENDATION']}")

                total_savings += opt["ESTIMATED_MONTHLY_SAVINGS"]

            print(f"\n  Total Potential Monthly Savings: ${total_savings:.2f}")

            metrics["optimizations"] = optimizations

    # Save report
    report_dir = Path("reports")
    report_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = report_dir / f"lambda_performance_{timestamp}.json"

    with open(report_path, "w") as f:
        json.dump(metrics, f, indent=2, default=str)

    print(f"\n✅ Report saved to: {report_path}")

    return metrics


if __name__ == "__main__":
    asyncio.run(analyze_performance())
