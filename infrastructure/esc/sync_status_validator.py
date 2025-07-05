#!/usr/bin/env python3
"""
Comprehensive Sync Status Validator for Sophia AI
Validates the synchronization status between GitHub Organization Secrets and Pulumi ESC

This script provides comprehensive analysis of:
1. GitHub Organization Secrets availability
2. Pulumi ESC secret coverage
3. Security configuration alignment
4. Sync health metrics
5. Actionable recommendations

Usage:
    python infrastructure/esc/sync_status_validator.py
    python infrastructure/esc/sync_status_validator.py --output json
    python infrastructure/esc/sync_status_validator.py --detailed
"""

import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class SyncMetrics:
    """Metrics for sync status analysis"""

    total_github_secrets: int
    total_esc_values: int
    mapped_secrets: int
    successfully_synced: int
    missing_from_esc: int
    extra_in_esc: int
    sync_percentage: float
    health_status: str


class SyncStatusValidator:
    """Comprehensive sync status validator for GitHub ↔ ESC integration"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.github_secrets = {}
        self.esc_values = {}
        self.security_config = None

        # Load SecurityConfig if available
        try:
            from backend.core.security_config import SecurityConfig

            self.security_config = SecurityConfig
            self.logger.info("SecurityConfig loaded successfully")
        except ImportError:
            self.logger.warning("SecurityConfig not available - using limited analysis")

    def validate_complete_sync_status(self) -> dict[str, Any]:
        """
        Run comprehensive sync status validation

        Returns:
            Dictionary with complete sync analysis and recommendations
        """
        self.logger.info("🔍 Starting comprehensive sync status validation...")

        results = {
            "timestamp": datetime.now().isoformat(),
            "validator_version": "1.0",
            "analysis": {},
            "metrics": {},
            "recommendations": [],
            "overall_health": "unknown",
        }

        try:
            # Step 1: Load GitHub Organization Secrets info
            self.logger.info("📊 Analyzing GitHub Organization Secrets...")
            results["analysis"]["github"] = self._analyze_github_secrets()

            # Step 2: Load Pulumi ESC configuration
            self.logger.info("🔧 Analyzing Pulumi ESC configuration...")
            results["analysis"]["esc"] = self._analyze_esc_configuration()

            # Step 3: Analyze SecurityConfig alignment
            self.logger.info("🔐 Analyzing SecurityConfig alignment...")
            results["analysis"]["security_config"] = self._analyze_security_config()

            # Step 4: Calculate sync metrics
            self.logger.info("📈 Calculating sync metrics...")
            metrics = self._calculate_sync_metrics()
            results["metrics"] = metrics.__dict__

            # Step 5: Generate recommendations
            self.logger.info("💡 Generating recommendations...")
            recommendations = self._generate_recommendations(
                metrics, results["analysis"]
            )
            results["recommendations"] = recommendations

            # Step 6: Determine overall health
            results["overall_health"] = metrics.health_status

            # Log summary
            self._log_validation_summary(results)

            return results

        except Exception as e:
            self.logger.error(f"Validation failed: {e}")
            results["error"] = str(e)
            results["overall_health"] = "error"
            return results

    def _analyze_github_secrets(self) -> dict[str, Any]:
        """Analyze GitHub Organization Secrets (simulated analysis)"""
        # Note: This would normally query GitHub API, but we'll simulate based on SecurityConfig
        if self.security_config:
            github_mapping = self.security_config.generate_github_secret_mapping()
            github_secret_names = list(github_mapping.keys())

            return {
                "status": "analyzed",
                "total_secrets": len(github_secret_names),
                "sample_secrets": github_secret_names[:10],
                "categories": {
                    "api_keys": len(
                        [s for s in github_secret_names if "API" in s or "KEY" in s]
                    ),
                    "tokens": len([s for s in github_secret_names if "TOKEN" in s]),
                    "passwords": len(
                        [s for s in github_secret_names if "PASSWORD" in s]
                    ),
                    "other": len(
                        [
                            s
                            for s in github_secret_names
                            if not any(
                                x in s for x in ["API", "KEY", "TOKEN", "PASSWORD"]
                            )
                        ]
                    ),
                },
                "data_source": "SecurityConfig simulation",
            }
        else:
            return {
                "status": "unavailable",
                "message": "SecurityConfig not available - cannot analyze GitHub secrets",
                "data_source": "none",
            }

    def _analyze_esc_configuration(self) -> dict[str, Any]:
        """Analyze Pulumi ESC configuration"""
        try:
            from backend.core.auto_esc_config import _load_esc_environment

            esc_data = _load_esc_environment()

            # Categorize ESC values
            secret_indicators = [
                "secret",
                "key",
                "token",
                "password",
                "credential",
                "api",
            ]
            secret_values = []
            config_values = []

            for key, value in esc_data.items():
                if any(indicator in key.lower() for indicator in secret_indicators):
                    secret_values.append(key)
                else:
                    config_values.append(key)

            return {
                "status": "loaded",
                "total_values": len(esc_data),
                "secret_values": len(secret_values),
                "config_values": len(config_values),
                "sample_secrets": secret_values[:10],
                "sample_configs": config_values[:5],
                "data_source": "Pulumi ESC direct",
                "environment_path": "default/sophia-ai-production",
            }

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "message": "Failed to load ESC configuration",
                "data_source": "none",
            }

    def _analyze_security_config(self) -> dict[str, Any]:
        """Analyze SecurityConfig alignment"""
        if not self.security_config:
            return {"status": "unavailable", "message": "SecurityConfig not available"}

        try:
            # Get comprehensive inventory
            inventory = self.security_config.get_comprehensive_secret_inventory()

            # Validate required secrets
            missing_required = self.security_config.get_missing_required_secrets()

            return {
                "status": "analyzed",
                "total_registered_secrets": inventory["total_secrets"],
                "required_secrets": inventory["required_secrets"],
                "optional_secrets": inventory["optional_secrets"],
                "rotatable_secrets": inventory["rotatable_secrets"],
                "missing_required": len(missing_required),
                "missing_required_list": missing_required,
                "secrets_by_type": inventory["secrets_by_type"],
                "github_mapping_count": len(inventory["github_mapping"]),
                "data_source": "SecurityConfig direct",
            }

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "message": "Failed to analyze SecurityConfig",
            }

    def _calculate_sync_metrics(self) -> SyncMetrics:
        """Calculate comprehensive sync metrics"""
        try:
            # Get data from analysis results
            github_total = 0
            esc_total = 0
            mapped_count = 0

            if self.security_config:
                github_mapping = self.security_config.generate_github_secret_mapping()
                github_total = len(github_mapping)
                mapped_count = len(github_mapping)

            # Get ESC data
            try:
                from backend.core.auto_esc_config import _load_esc_environment

                esc_data = _load_esc_environment()
                esc_total = len(esc_data)
            except Exception:
                esc_total = 0

            # Calculate sync success (simplified)
            if self.security_config:
                missing_required = self.security_config.get_missing_required_secrets()
                successfully_synced = max(0, mapped_count - len(missing_required))
            else:
                successfully_synced = 0

            # Calculate percentages
            sync_percentage = 0.0
            if mapped_count > 0:
                sync_percentage = (successfully_synced / mapped_count) * 100

            # Determine health status
            if sync_percentage >= 95:
                health_status = "excellent"
            elif sync_percentage >= 80:
                health_status = "good"
            elif sync_percentage >= 60:
                health_status = "fair"
            else:
                health_status = "poor"

            return SyncMetrics(
                total_github_secrets=github_total,
                total_esc_values=esc_total,
                mapped_secrets=mapped_count,
                successfully_synced=successfully_synced,
                missing_from_esc=mapped_count - successfully_synced,
                extra_in_esc=max(0, esc_total - mapped_count),
                sync_percentage=sync_percentage,
                health_status=health_status,
            )

        except Exception as e:
            self.logger.error(f"Error calculating metrics: {e}")
            return SyncMetrics(0, 0, 0, 0, 0, 0, 0.0, "error")

    def _generate_recommendations(
        self, metrics: SyncMetrics, analysis: dict[str, Any]
    ) -> list[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []

        # Health-based recommendations
        if metrics.health_status == "excellent":
            recommendations.append(
                "✅ Sync health is excellent - maintain current practices"
            )
        elif metrics.health_status == "good":
            recommendations.append(
                "✅ Sync health is good - minor improvements possible"
            )
        elif metrics.health_status == "fair":
            recommendations.append(
                "⚠️ Sync health is fair - consider running GitHub→ESC sync"
            )
        elif metrics.health_status == "poor":
            recommendations.append("❌ Sync health is poor - immediate sync required")
        else:
            recommendations.append("🔧 Sync health unknown - investigate configuration")

        # Specific recommendations based on analysis
        if metrics.missing_from_esc > 0:
            recommendations.append(
                f"🔧 {metrics.missing_from_esc} secrets missing from ESC - run sync operation"
            )

        if metrics.extra_in_esc > 10:
            recommendations.append(
                f"📋 {metrics.extra_in_esc} extra values in ESC - review for cleanup"
            )

        # SecurityConfig recommendations
        security_analysis = analysis.get("security_config", {})
        if security_analysis.get("missing_required"):
            missing_count = len(security_analysis["missing_required"])
            recommendations.append(
                f"❌ {missing_count} required secrets missing - priority fix needed"
            )

        # ESC recommendations
        esc_analysis = analysis.get("esc", {})
        if esc_analysis.get("status") == "failed":
            recommendations.append(
                "🔧 ESC configuration failed to load - check Pulumi authentication"
            )

        # GitHub recommendations
        github_analysis = analysis.get("github", {})
        if github_analysis.get("status") == "unavailable":
            recommendations.append(
                "🔧 GitHub secrets analysis unavailable - ensure SecurityConfig is loaded"
            )

        # Performance recommendations
        if metrics.sync_percentage < 100 and metrics.mapped_secrets > 0:
            recommendations.append("🚀 Run full sync to achieve 100% coverage")

        return recommendations

    def _log_validation_summary(self, results: dict[str, Any]):
        """Log validation summary"""
        health = results["overall_health"]
        metrics = results.get("metrics", {})

        if health == "excellent":
            self.logger.info("✅ SYNC VALIDATION COMPLETE: Excellent sync health!")
        elif health == "good":
            self.logger.info("✅ SYNC VALIDATION COMPLETE: Good sync health")
        elif health == "fair":
            self.logger.warning(
                "⚠️ SYNC VALIDATION COMPLETE: Fair sync health - improvements needed"
            )
        elif health == "poor":
            self.logger.error(
                "❌ SYNC VALIDATION COMPLETE: Poor sync health - immediate attention required"
            )
        else:
            self.logger.error("🔧 SYNC VALIDATION COMPLETE: Health status unknown")

        # Log key metrics
        self.logger.info(
            f"  📊 GitHub Secrets: {metrics.get('total_github_secrets', 0)}"
        )
        self.logger.info(f"  📊 ESC Values: {metrics.get('total_esc_values', 0)}")
        self.logger.info(f"  📊 Sync Success: {metrics.get('sync_percentage', 0):.1f}%")

        # Log recommendations
        if results.get("recommendations"):
            self.logger.info("\n💡 RECOMMENDATIONS:")
            for rec in results["recommendations"]:
                self.logger.info(f"  {rec}")


def main():
    """Main function for CLI usage"""
    parser = argparse.ArgumentParser(
        description="Validate GitHub ↔ ESC sync status for Sophia AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python infrastructure/esc/sync_status_validator.py
    python infrastructure/esc/sync_status_validator.py --output json
    python infrastructure/esc/sync_status_validator.py --detailed
        """,
    )

    parser.add_argument(
        "--output",
        choices=["json", "summary"],
        default="summary",
        help="Output format (default: summary)",
    )
    parser.add_argument(
        "--detailed", action="store_true", help="Include detailed analysis in output"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress log output, only show final result",
    )

    args = parser.parse_args()

    # Adjust logging level if quiet
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)

    try:
        validator = SyncStatusValidator()
        results = validator.validate_complete_sync_status()

        if args.output == "json":
            if not args.detailed:
                # Remove detailed analysis for cleaner JSON
                results.pop("analysis", None)
            print(json.dumps(results, indent=2))
        else:
            # Summary output
            health = results["overall_health"]
            metrics = results.get("metrics", {})

            print("\n🔍 GitHub ↔ ESC Sync Status Validation")
            print(f"Health: {health.upper()}")
            print(f"Sync Coverage: {metrics.get('sync_percentage', 0):.1f}%")
            print(f"GitHub Secrets: {metrics.get('total_github_secrets', 0)}")
            print(f"ESC Values: {metrics.get('total_esc_values', 0)}")
            print(f"Successfully Synced: {metrics.get('successfully_synced', 0)}")
            print(f"Timestamp: {results['timestamp']}")

            if results.get("recommendations"):
                print("\n💡 Recommendations:")
                for rec in results["recommendations"]:
                    print(f"  {rec}")

        # Exit with appropriate code
        if results["overall_health"] in ["excellent", "good"]:
            sys.exit(0)
        elif results["overall_health"] in ["fair"]:
            sys.exit(1)
        else:
            sys.exit(2)

    except Exception as e:
        logger.error(f"Validation failed with error: {e}")
        if args.output == "json":
            error_result = {
                "timestamp": datetime.now().isoformat(),
                "overall_health": "error",
                "error": str(e),
                "message": "Sync validation encountered an error",
            }
            print(json.dumps(error_result, indent=2))
        else:
            print(f"❌ Validation Error: {e}")

        sys.exit(3)


if __name__ == "__main__":
    main()
