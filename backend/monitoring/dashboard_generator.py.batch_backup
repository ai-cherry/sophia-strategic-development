"""
Grafana Dashboard Generator for Gong Data Quality Monitoring.

Generates JSON configurations for comprehensive Grafana dashboards
to visualize data quality metrics, alerts, and trends.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List
from enum import Enum

import structlog
from pydantic import BaseModel

logger = structlog.get_logger()


class DashboardType(str, Enum):
    """Types of dashboards to generate."""

    OVERVIEW = "overview"
    QUALITY_DETAILS = "quality_details"
    PERFORMANCE = "performance"
    ALERTS = "alerts"
    TRENDS = "trends"


class PanelType(str, Enum):
    """Grafana panel types."""

    GRAPH = "graph"
    GAUGE = "gauge"
    STAT = "stat"
    TABLE = "table"
    HEATMAP = "heatmap"
    ALERT_LIST = "alertlist"
    PIE_CHART = "piechart"
    BAR_GAUGE = "bargauge"
    TIME_SERIES = "timeseries"


class DashboardConfig(BaseModel):
    """Dashboard configuration."""

    title: str
    uid: str
    description: str
    tags: List[str]
    refresh_interval: str = "10s"
    time_range: Dict[str, str] = {"from": "now-1h", "to": "now"}
    editable: bool = True
    version: int = 1


class GrafanaDashboardGenerator:
    """
    Generates Grafana dashboard JSON configurations for data quality monitoring.
    """

    def __init__(self):
        self.logger = logger.bind(component="dashboard_generator")

    def generate_all_dashboards(self) -> Dict[str, Dict[str, Any]]:
        """Generate all dashboard configurations."""
        dashboards = {}

        dashboards["overview"] = self.generate_overview_dashboard()
        dashboards["quality_details"] = self.generate_quality_details_dashboard()
        dashboards["performance"] = self.generate_performance_dashboard()
        dashboards["alerts"] = self.generate_alerts_dashboard()
        dashboards["trends"] = self.generate_trends_dashboard()

        return dashboards

    def generate_overview_dashboard(self) -> Dict[str, Any]:
        """Generate real-time quality overview dashboard."""
        config = DashboardConfig(
            title="Gong Data Quality Overview",
            uid="gong-quality-overview",
            description="Real-time overview of Gong webhook data quality",
            tags=["gong", "quality", "overview", "monitoring"],
        )

        panels = []

        # Row 1: Key Metrics
        panels.extend(
            [
                self._create_quality_score_gauge(0, 0, 6, 8),
                self._create_api_success_gauge(6, 0, 6, 8),
                self._create_transcript_completeness_gauge(12, 0, 6, 8),
                self._create_participant_accuracy_gauge(18, 0, 6, 8),
            ]
        )

        # Row 2: Processing Metrics
        panels.extend(
            [
                self._create_webhook_reception_graph(0, 8, 12, 8),
                self._create_processing_latency_graph(12, 8, 12, 8),
            ]
        )

        # Row 3: Quality Dimensions
        panels.append(self._create_quality_dimensions_heatmap(0, 16, 24, 8))

        # Row 4: Error Tracking
        panels.extend(
            [
                self._create_error_rate_graph(0, 24, 12, 8),
                self._create_validation_violations_table(12, 24, 12, 8),
            ]
        )

        return self._build_dashboard(config, panels)

    def generate_quality_details_dashboard(self) -> Dict[str, Any]:
        """Generate detailed quality analysis dashboard."""
        config = DashboardConfig(
            title="Gong Data Quality Details",
            uid="gong-quality-details",
            description="Detailed analysis of data quality dimensions",
            tags=["gong", "quality", "details", "analysis"],
        )

        panels = []

        # Row 1: Field Coverage Analysis
        panels.extend(
            [
                self._create_field_coverage_pie_chart(0, 0, 8, 8),
                self._create_required_fields_status(8, 0, 8, 8),
                self._create_optional_fields_status(16, 0, 8, 8),
            ]
        )

        # Row 2: Transcript Analysis
        panels.extend(
            [
                self._create_transcript_quality_distribution(0, 8, 12, 8),
                self._create_speaker_attribution_stats(12, 8, 12, 8),
            ]
        )

        # Row 3: Participant Data Quality
        panels.extend(
            [
                self._create_participant_enrichment_table(0, 16, 12, 10),
                self._create_company_domain_mapping_stats(12, 16, 12, 10),
            ]
        )

        # Row 4: Metadata Quality
        panels.append(self._create_metadata_completeness_matrix(0, 26, 24, 8))

        return self._build_dashboard(config, panels)

    def generate_performance_dashboard(self) -> Dict[str, Any]:
        """Generate performance monitoring dashboard."""
        config = DashboardConfig(
            title="Gong Integration Performance",
            uid="gong-performance",
            description="Performance metrics for Gong webhook processing",
            tags=["gong", "performance", "latency", "monitoring"],
        )

        panels = []

        # Row 1: Latency Metrics
        panels.extend(
            [
                self._create_latency_histogram(0, 0, 12, 8),
                self._create_latency_percentiles(12, 0, 12, 8),
            ]
        )

        # Row 2: Throughput Metrics
        panels.extend(
            [
                self._create_webhook_throughput_graph(0, 8, 12, 8),
                self._create_api_call_rate_graph(12, 8, 12, 8),
            ]
        )

        # Row 3: Resource Utilization
        panels.extend(
            [
                self._create_memory_usage_graph(0, 16, 8, 8),
                self._create_cache_hit_ratio_gauge(8, 16, 8, 8),
                self._create_queue_depth_graph(16, 16, 8, 8),
            ]
        )

        # Row 4: SLA Compliance
        panels.append(self._create_sla_compliance_table(0, 24, 24, 10))

        return self._build_dashboard(config, panels)

    def generate_alerts_dashboard(self) -> Dict[str, Any]:
        """Generate alert management dashboard."""
        config = DashboardConfig(
            title="Gong Quality Alerts",
            uid="gong-alerts",
            description="Active alerts and alert management",
            tags=["gong", "alerts", "incidents", "monitoring"],
            refresh_interval="5s",
        )

        panels = []

        # Row 1: Alert Summary
        panels.extend(
            [
                self._create_active_alerts_count(0, 0, 6, 4),
                self._create_alerts_by_severity(6, 0, 6, 4),
                self._create_alerts_by_type(12, 0, 6, 4),
                self._create_escalation_rate(18, 0, 6, 4),
            ]
        )

        # Row 2: Active Alerts List
        panels.append(self._create_active_alerts_table(0, 4, 24, 10))

        # Row 3: Alert Timeline
        panels.append(self._create_alert_timeline(0, 14, 24, 8))

        # Row 4: Alert Statistics
        panels.extend(
            [
                self._create_alert_response_time(0, 22, 12, 8),
                self._create_alert_resolution_stats(12, 22, 12, 8),
            ]
        )

        return self._build_dashboard(config, panels)

    def generate_trends_dashboard(self) -> Dict[str, Any]:
        """Generate quality trends dashboard."""
        config = DashboardConfig(
            title="Gong Quality Trends",
            uid="gong-trends",
            description="Historical trends and predictive analytics",
            tags=["gong", "trends", "analytics", "historical"],
            time_range={"from": "now-7d", "to": "now"},
        )

        panels = []

        # Row 1: Quality Score Trends
        panels.append(self._create_quality_score_trend(0, 0, 24, 8))

        # Row 2: Dimension Trends
        panels.extend(
            [
                self._create_dimension_trends_graph(0, 8, 12, 8),
                self._create_dimension_comparison_radar(12, 8, 12, 8),
            ]
        )

        # Row 3: Weekly Patterns
        panels.extend(
            [
                self._create_weekly_quality_heatmap(0, 16, 12, 8),
                self._create_hourly_pattern_graph(12, 16, 12, 8),
            ]
        )

        # Row 4: Predictive Analytics
        panels.extend(
            [
                self._create_quality_forecast(0, 24, 12, 8),
                self._create_anomaly_detection_graph(12, 24, 12, 8),
            ]
        )

        return self._build_dashboard(config, panels)

    # Panel Creation Methods

    def _create_quality_score_gauge(
        self, x: int, y: int, w: int, h: int
    ) -> Dict[str, Any]:
        """Create overall quality score gauge."""
        return {
            "id": 1,
            "type": "gauge",
            "title": "Overall Quality Score",
            "gridPos": {"x": x, "y": y, "w": w, "h": h},
            "targets": [
                {
                    "expr": "avg(gong_data_quality_score)",
                    "refId": "A",
                    "interval": "10s",
                }
            ],
            "options": {
                "orientation": "auto",
                "showThresholdLabels": True,
                "showThresholdMarkers": True,
                "text": {"titleSize": 16, "valueSize": 48},
            },
            "fieldConfig": {
                "defaults": {
                    "unit": "percentunit",
                    "min": 0,
                    "max": 1,
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"value": 0, "color": "red"},
                            {"value": 0.6, "color": "orange"},
                            {"value": 0.8, "color": "yellow"},
                            {"value": 0.95, "color": "green"},
                        ],
                    },
                    "decimals": 2,
                }
            },
        }

    def _create_api_success_gauge(
        self, x: int, y: int, w: int, h: int
    ) -> Dict[str, Any]:
        """Create API enhancement success rate gauge."""
        return {
            "id": 2,
            "type": "gauge",
            "title": "API Enhancement Success",
            "gridPos": {"x": x, "y": y, "w": w, "h": h},
            "targets": [{"expr": "gong_api_enhancement_success_rate", "refId": "A"}],
            "options": {
                "orientation": "auto",
                "showThresholdLabels": True,
                "showThresholdMarkers": True,
            },
            "fieldConfig": {
                "defaults": {
                    "unit": "percent",
                    "min": 0,
                    "max": 100,
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"value": 0, "color": "red"},
                            {"value": 90, "color": "yellow"},
                            {"value": 98, "color": "green"},
                        ],
                    },
                    "decimals": 1,
                }
            },
        }

    def _create_transcript_completeness_gauge(
        self, x: int, y: int, w: int, h: int
    ) -> Dict[str, Any]:
        """Create transcript completeness gauge."""
        return {
            "id": 3,
            "type": "gauge",
            "title": "Transcript Completeness",
            "gridPos": {"x": x, "y": y, "w": w, "h": h},
            "targets": [{"expr": "gong_transcript_completeness_rate", "refId": "A"}],
            "options": {
                "orientation": "auto",
                "showThresholdLabels": True,
                "showThresholdMarkers": True,
            },
            "fieldConfig": {
                "defaults": {
                    "unit": "percent",
                    "min": 0,
                    "max": 100,
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"value": 0, "color": "red"},
                            {"value": 80, "color": "orange"},
                            {"value": 95, "color": "green"},
                        ],
                    },
                }
            },
        }

    def _create_participant_accuracy_gauge(
        self, x: int, y: int, w: int, h: int
    ) -> Dict[str, Any]:
        """Create participant mapping accuracy gauge."""
        return {
            "id": 4,
            "type": "gauge",
            "title": "Participant Mapping Accuracy",
            "gridPos": {"x": x, "y": y, "w": w, "h": h},
            "targets": [{"expr": "gong_participant_mapping_accuracy", "refId": "A"}],
            "options": {
                "orientation": "auto",
                "showThresholdLabels": True,
                "showThresholdMarkers": True,
            },
            "fieldConfig": {
                "defaults": {
                    "unit": "percent",
                    "min": 0,
                    "max": 100,
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"value": 0, "color": "red"},
                            {"value": 85, "color": "orange"},
                            {"value": 95, "color": "green"},
                        ],
                    },
                }
            },
        }

    def _create_webhook_reception_graph(
        self, x: int, y: int, w: int, h: int
    ) -> Dict[str, Any]:
        """Create webhook reception rate graph."""
        return {
            "id": 5,
            "type": "timeseries",
            "title": "Webhook Reception Rate",
            "gridPos": {"x": x, "y": y, "w": w, "h": h},
            "targets": [
                {
                    "expr": "rate(gong_webhook_calls_received_total[5m])",
                    "refId": "A",
                    "legendFormat": "{{webhook_type}} - {{status}}",
                }
            ],
            "fieldConfig": {
                "defaults": {
                    "unit": "reqps",
                    "custom": {
                        "lineWidth": 2,
                        "fillOpacity": 10,
                        "showPoints": "never",
                    },
                }
            },
            "options": {
                "legend": {"displayMode": "list", "placement": "bottom"},
                "tooltip": {"mode": "multi", "sort": "desc"},
            },
        }

    def _create_processing_latency_graph(
        self, x: int, y: int, w: int, h: int
    ) -> Dict[str, Any]:
        """Create processing latency graph."""
        return {
            "id": 6,
            "type": "timeseries",
            "title": "Processing Latency",
            "gridPos": {"x": x, "y": y, "w": w, "h": h},
            "targets": [
                {
                    "expr": "histogram_quantile(0.5, gong_data_processing_latency_seconds_bucket)",
                    "refId": "A",
                    "legendFormat": "p50",
                },
                {
                    "expr": "histogram_quantile(0.95, gong_data_processing_latency_seconds_bucket)",
                    "refId": "B",
                    "legendFormat": "p95",
                },
                {
                    "expr": "histogram_quantile(0.99, gong_data_processing_latency_seconds_bucket)",
                    "refId": "C",
                    "legendFormat": "p99",
                },
            ],
            "fieldConfig": {
                "defaults": {
                    "unit": "s",
                    "custom": {"lineWidth": 2, "fillOpacity": 10},
                    "min": 0,
                }
            },
            "options": {"legend": {"displayMode": "list", "placement": "right"}},
        }

    def _create_quality_dimensions_heatmap(
        self, x: int, y: int, w: int, h: int
    ) -> Dict[str, Any]:
        """Create quality dimensions heatmap."""
        return {
            "id": 7,
            "type": "heatmap",
            "title": "Quality Dimensions Heatmap",
            "gridPos": {"x": x, "y": y, "w": w, "h": h},
            "targets": [
                {
                    "expr": """
                    label_join(
                        avg by (dimension) (gong_quality_dimension_score),
                        "dimension_time", "_", "dimension", "__name__"
                    )
                """,
                    "refId": "A",
                    "format": "heatmap",
                }
            ],
            "options": {
                "calculate": False,
                "cellGap": 1,
                "color": {"scheme": "RdYlGn", "mode": "scheme"},
                "yAxis": {"axisLabel": "Quality Dimension"},
            },
            "fieldConfig": {
                "defaults": {"custom": {"scaleDistribution": {"type": "linear"}}}
            },
        }

    def _create_error_rate_graph(
        self, x: int, y: int, w: int, h: int
    ) -> Dict[str, Any]:
        """Create error rate by type graph."""
        return {
            "id": 8,
            "type": "timeseries",
            "title": "Error Rate by Type",
            "gridPos": {"x": x, "y": y, "w": w, "h": h},
            "targets": [
                {
                    "expr": "rate(gong_error_rate_by_type_total[5m])",
                    "refId": "A",
                    "legendFormat": "{{error_type}} ({{severity}})",
                }
            ],
            "fieldConfig": {
                "defaults": {
                    "unit": "errors/sec",
                    "custom": {
                        "lineWidth": 2,
                        "fillOpacity": 20,
                        "stacking": {"mode": "normal", "group": "A"},
                    },
                }
            },
        }

    def _create_validation_violations_table(
        self, x: int, y: int, w: int, h: int
    ) -> Dict[str, Any]:
        """Create validation violations table."""
        return {
            "id": 9,
            "type": "table",
            "title": "Recent Validation Violations",
            "gridPos": {"x": x, "y": y, "w": w, "h": h},
            "targets": [
                {
                    "expr": """
                    topk(10, 
                        increase(gong_validation_rule_violations_total[1h])
                    ) by (rule_name, severity)
                """,
                    "refId": "A",
                    "format": "table",
                }
            ],
            "options": {
                "showHeader": True,
                "sortBy": [{"displayName": "Value", "desc": True}],
            },
            "fieldConfig": {
                "defaults": {
                    "custom": {"align": "auto", "cellOptions": {"type": "color-text"}}
                },
                "overrides": [
                    {
                        "matcher": {"id": "byName", "options": "severity"},
                        "properties": [
                            {
                                "id": "custom.cellOptions",
                                "value": {"type": "color-background", "mode": "basic"},
                            }
                        ],
                    }
                ],
            },
        }

    def _create_field_coverage_pie_chart(
        self, x: int, y: int, w: int, h: int
    ) -> Dict[str, Any]:
        """Create field coverage pie chart."""
        return {
            "id": 10,
            "type": "piechart",
            "title": "Field Coverage Distribution",
            "gridPos": {"x": x, "y": y, "w": w, "h": h},
            "targets": [
                {
                    "expr": "gong_field_coverage_percentage",
                    "refId": "A",
                    "legendFormat": "{{field_category}}",
                }
            ],
            "options": {
                "pieType": "donut",
                "displayLabels": ["name", "percent"],
                "legendDisplayMode": "list",
                "legendPlacement": "right",
            },
        }

    def _create_active_alerts_count(
        self, x: int, y: int, w: int, h: int
    ) -> Dict[str, Any]:
        """Create active alerts count stat."""
        return {
            "id": 20,
            "type": "stat",
            "title": "Active Alerts",
            "gridPos": {"x": x, "y": y, "w": w, "h": h},
            "targets": [{"expr": "count(gong_active_alerts)", "refId": "A"}],
            "options": {
                "colorMode": "background",
                "graphMode": "none",
                "orientation": "auto",
                "reduceOptions": {"calcs": ["lastNotNull"]},
            },
            "fieldConfig": {
                "defaults": {
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"value": 0, "color": "green"},
                            {"value": 1, "color": "yellow"},
                            {"value": 5, "color": "orange"},
                            {"value": 10, "color": "red"},
                        ],
                    }
                }
            },
        }

    def _create_quality_score_trend(
        self, x: int, y: int, w: int, h: int
    ) -> Dict[str, Any]:
        """Create quality score trend graph."""
        return {
            "id": 30,
            "type": "timeseries",
            "title": "Quality Score Trend",
            "gridPos": {"x": x, "y": y, "w": w, "h": h},
            "targets": [
                {
                    "expr": "avg(gong_data_quality_score)",
                    "refId": "A",
                    "legendFormat": "Current",
                },
                {
                    "expr": "avg_over_time(gong_data_quality_score[1h])",
                    "refId": "B",
                    "legendFormat": "1h Average",
                },
                {
                    "expr": "avg_over_time(gong_data_quality_score[24h])",
                    "refId": "C",
                    "legendFormat": "24h Average",
                },
            ],
            "fieldConfig": {
                "defaults": {
                    "unit": "percentunit",
                    "min": 0,
                    "max": 1,
                    "custom": {
                        "lineWidth": 2,
                        "fillOpacity": 10,
                        "gradientMode": "opacity",
                    },
                }
            },
            "options": {
                "legend": {
                    "displayMode": "list",
                    "placement": "bottom",
                    "calcs": ["mean", "lastNotNull"],
                }
            },
        }

    # Helper methods

    def _build_dashboard(
        self, config: DashboardConfig, panels: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build complete dashboard JSON."""
        return {
            "uid": config.uid,
            "title": config.title,
            "description": config.description,
            "tags": config.tags,
            "timezone": "browser",
            "schemaVersion": 27,
            "version": config.version,
            "refresh": config.refresh_interval,
            "time": config.time_range,
            "editable": config.editable,
            "panels": panels,
            "templating": {
                "list": [
                    {
                        "name": "datasource",
                        "type": "datasource",
                        "query": "prometheus",
                        "current": {"text": "Prometheus", "value": "prometheus"},
                    }
                ]
            },
            "annotations": {
                "list": [
                    {
                        "name": "Quality Alerts",
                        "datasource": "prometheus",
                        "enable": True,
                        "expr": "gong_quality_alert_triggered",
                        "iconColor": "red",
                        "tags": ["quality", "alert"],
                    }
                ]
            },
        }

    def _create_required_fields_status(
        self, x: int, y: int, w: int, h: int
    ) -> Dict[str, Any]:
        """Create required fields status panel."""
        return {
            "id": 11,
            "type": "stat",
            "title": "Required Fields Status",
            "gridPos": {"x": x, "y": y, "w": w, "h": h},
            "targets": [
                {
                    "expr": "gong_field_coverage_percentage{field_category='required'}",
                    "refId": "A",
                }
            ],
            "options": {
                "colorMode": "value",
                "graphMode": "area",
                "orientation": "auto",
            },
            "fieldConfig": {
                "defaults": {
                    "unit": "percent",
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"value": 0, "color": "red"},
                            {"value": 95, "color": "orange"},
                            {"value": 100, "color": "green"},
                        ],
                    },
                }
            },
        }

    def _create_optional_fields_status(
        self, x: int, y: int, w: int, h: int
    ) -> Dict[str, Any]:
        """Create optional fields status panel."""
        return {
            "id": 12,
            "type": "stat",
            "title": "Optional Fields Status",
            "gridPos": {"x": x, "y": y, "w": w, "h": h},
            "targets": [
                {
                    "expr": "gong_field_coverage_percentage{field_category='all'} - gong_field_coverage_percentage{field_category='required'}",
                    "refId": "A",
                }
            ],
            "options": {
                "colorMode": "value",
                "graphMode": "area",
                "orientation": "auto",
            },
            "fieldConfig": {"defaults": {"unit": "percent"}},
        }

    def save_dashboards_to_files(
        self, output_dir: str = "infrastructure/monitoring/dashboards"
    ):
        """Save dashboard configurations to JSON files."""
        import os

        dashboards = self.generate_all_dashboards()

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        for name, dashboard in dashboards.items():
            filename = f"gong_quality_{name}_dashboard.json"
            filepath = os.path.join(output_dir, filename)

            with open(filepath, "w") as f:
                json.dump(dashboard, f, indent=2)

            self.logger.info(f"Saved dashboard to {filepath}")


# Additional helper functions for complex panels


def _create_transcript_quality_distribution(
    self, x: int, y: int, w: int, h: int
) -> Dict[str, Any]:
    """Create transcript quality distribution histogram."""
    return {
        "id": 13,
        "type": "histogram",
        "title": "Transcript Quality Distribution",
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [
            {
                "expr": "gong_transcript_quality_score_bucket",
                "refId": "A",
                "format": "heatmap",
            }
        ],
        "options": {"bucketSize": 0.05},
    }


def _create_latency_histogram(self, x: int, y: int, w: int, h: int) -> Dict[str, Any]:
    """Create processing latency histogram."""
    return {
        "id": 14,
        "type": "histogram",
        "title": "Processing Latency Distribution",
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [
            {
                "expr": "gong_data_processing_latency_seconds_bucket",
                "refId": "A",
                "format": "heatmap",
            }
        ],
    }


def _create_alert_timeline(self, x: int, y: int, w: int, h: int) -> Dict[str, Any]:
    """Create alert timeline visualization."""
    return {
        "id": 21,
        "type": "state-timeline",
        "title": "Alert Timeline",
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [
            {
                "expr": """
                gong_alert_status{} * 
                (label_replace(vector(1), "status", "active", "", "") +
                 label_replace(vector(2), "status", "acknowledged", "", "") +
                 label_replace(vector(3), "status", "resolved", "", ""))
            """,
                "refId": "A",
                "format": "time_series",
            }
        ],
        "options": {
            "mergeValues": True,
            "showValue": "never",
            "alignValue": "center",
            "legendDisplayMode": "list",
            "legendPlacement": "bottom",
        },
    }


# Additional placeholder methods that were missing
def _create_speaker_attribution_stats(
    self, x: int, y: int, w: int, h: int
) -> Dict[str, Any]:
    """Create speaker attribution statistics panel."""
    return {
        "id": 15,
        "type": "stat",
        "title": "Speaker Attribution Rate",
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [{"expr": "avg(gong_speaker_attribution_rate)", "refId": "A"}],
        "fieldConfig": {
            "defaults": {
                "unit": "percent",
                "thresholds": {
                    "mode": "absolute",
                    "steps": [
                        {"value": 0, "color": "red"},
                        {"value": 80, "color": "orange"},
                        {"value": 95, "color": "green"},
                    ],
                },
            }
        },
    }


def _create_participant_enrichment_table(
    self, x: int, y: int, w: int, h: int
) -> Dict[str, Any]:
    """Create participant enrichment table."""
    return {
        "id": 16,
        "type": "table",
        "title": "Participant Enrichment Status",
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [
            {
                "expr": "gong_participant_enrichment_status",
                "refId": "A",
                "format": "table",
            }
        ],
    }


def _create_company_domain_mapping_stats(
    self, x: int, y: int, w: int, h: int
) -> Dict[str, Any]:
    """Create company domain mapping statistics."""
    return {
        "id": 17,
        "type": "stat",
        "title": "Company Domain Mapping Success",
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [{"expr": "avg(gong_company_domain_mapping_rate)", "refId": "A"}],
        "fieldConfig": {"defaults": {"unit": "percent"}},
    }


def _create_metadata_completeness_matrix(
    self, x: int, y: int, w: int, h: int
) -> Dict[str, Any]:
    """Create metadata completeness matrix."""
    return {
        "id": 18,
        "type": "heatmap",
        "title": "Metadata Completeness Matrix",
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [
            {
                "expr": "gong_metadata_field_completeness",
                "refId": "A",
                "format": "heatmap",
            }
        ],
    }


def _create_latency_percentiles(self, x: int, y: int, w: int, h: int) -> Dict[str, Any]:
    """Create latency percentiles panel."""
    return {
        "id": 19,
        "type": "bargauge",
        "title": "Latency Percentiles",
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [
            {
                "expr": "histogram_quantile(0.5, gong_data_processing_latency_seconds_bucket)",
                "refId": "A",
                "legendFormat": "p50",
            },
            {
                "expr": "histogram_quantile(0.75, gong_data_processing_latency_seconds_bucket)",
                "refId": "B",
                "legendFormat": "p75",
            },
            {
                "expr": "histogram_quantile(0.90, gong_data_processing_latency_seconds_bucket)",
                "refId": "C",
                "legendFormat": "p90",
            },
            {
                "expr": "histogram_quantile(0.95, gong_data_processing_latency_seconds_bucket)",
                "refId": "D",
                "legendFormat": "p95",
            },
            {
                "expr": "histogram_quantile(0.99, gong_data_processing_latency_seconds_bucket)",
                "refId": "E",
                "legendFormat": "p99",
            },
        ],
        "options": {"orientation": "horizontal", "displayMode": "gradient"},
        "fieldConfig": {"defaults": {"unit": "s", "min": 0, "max": 60}},
    }


def _create_webhook_throughput_graph(
    self, x: int, y: int, w: int, h: int
) -> Dict[str, Any]:
    """Create webhook throughput graph."""
    return {
        "id": 22,
        "type": "timeseries",
        "title": "Webhook Throughput",
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [
            {
                "expr": "sum(rate(gong_webhook_calls_received_total[5m]))",
                "refId": "A",
                "legendFormat": "Total Throughput",
            }
        ],
        "fieldConfig": {"defaults": {"unit": "reqps"}},
    }


def _create_api_call_rate_graph(self, x: int, y: int, w: int, h: int) -> Dict[str, Any]:
    """Create API call rate graph."""
    return {
        "id": 23,
        "type": "timeseries",
        "title": "API Call Rate",
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [
            {
                "expr": "sum(rate(gong_api_calls_total[5m]))",
                "refId": "A",
                "legendFormat": "API Calls/sec",
            }
        ],
        "fieldConfig": {"defaults": {"unit": "calls/s"}},
    }


def _create_memory_usage_graph(self, x: int, y: int, w: int, h: int) -> Dict[str, Any]:
    """Create memory usage graph."""
    return {
        "id": 24,
        "type": "timeseries",
        "title": "Memory Usage",
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [
            {
                "expr": "process_resident_memory_bytes",
                "refId": "A",
                "legendFormat": "RSS Memory",
            }
        ],
        "fieldConfig": {"defaults": {"unit": "bytes"}},
    }


def _create_cache_hit_ratio_gauge(
    self, x: int, y: int, w: int, h: int
) -> Dict[str, Any]:
    """Create cache hit ratio gauge."""
    return {
        "id": 25,
        "type": "gauge",
        "title": "Cache Hit Ratio",
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [{"expr": "avg(gong_cache_hit_ratio)", "refId": "A"}],
        "fieldConfig": {
            "defaults": {
                "unit": "percent",
                "min": 0,
                "max": 100,
                "thresholds": {
                    "mode": "absolute",
                    "steps": [
                        {"value": 0, "color": "red"},
                        {"value": 60, "color": "orange"},
                        {"value": 80, "color": "green"},
                    ],
                },
            }
        },
    }


def _create_queue_depth_graph(self, x: int, y: int, w: int, h: int) -> Dict[str, Any]:
    """Create queue depth graph."""
    return {
        "id": 26,
        "type": "timeseries",
        "title": "Processing Queue Depth",
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [
            {
                "expr": "gong_processing_queue_depth",
                "refId": "A",
                "legendFormat": "Queue Size",
            }
        ],
        "fieldConfig": {"defaults": {"unit": "short", "min": 0}},
    }


def _create_sla_compliance_table(
    self, x: int, y: int, w: int, h: int
) -> Dict[str, Any]:
    """Create SLA compliance table."""
    return {
        "id": 27,
        "type": "table",
        "title": "SLA Compliance",
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [
            {
                "expr": """
                avg by (sla_type) (gong_sla_compliance_rate)
            """,
                "refId": "A",
                "format": "table",
            }
        ],
        "options": {"showHeader": True},
        "fieldConfig": {"defaults": {"unit": "percent", "custom": {"align": "center"}}},
    }


def _create_alerts_by_severity(self, x: int, y: int, w: int, h: int) -> Dict[str, Any]:
    """Create alerts by severity panel."""
    return {
        "id": 28,
        "type": "piechart",
        "title": "Alerts by Severity",
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [
            {
                "expr": "count by (severity) (gong_active_alerts)",
                "refId": "A",
                "legendFormat": "{{severity}}",
            }
        ],
        "options": {"pieType": "pie", "displayLabels": ["name", "value"]},
    }


def _create_alerts_by_type(self, x: int, y: int, w: int, h: int) -> Dict[str, Any]:
    """Create alerts by type panel."""
    return {
        "id": 29,
        "type": "piechart",
        "title": "Alerts by Type",
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [
            {
                "expr": "count by (alert_type) (gong_active_alerts)",
                "refId": "A",
                "legendFormat": "{{alert_type}}",
            }
        ],
        "options": {"pieType": "donut"},
    }


def _create_escalation_rate(self, x: int, y: int, w: int, h: int) -> Dict[str, Any]:
    """Create escalation rate panel."""
    return {
        "id": 31,
        "type": "stat",
        "title": "Escalation Rate",
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [{"expr": "avg(gong_alert_escalation_rate)", "refId": "A"}],
        "fieldConfig": {
            "defaults": {
                "unit": "percent",
                "thresholds": {
                    "mode": "absolute",
                    "steps": [
                        {"value": 0, "color": "green"},
                        {"value": 10, "color": "yellow"},
                        {"value": 25, "color": "red"},
                    ],
                },
            }
        },
    }


def _create_active_alerts_table(self, x: int, y: int, w: int, h: int) -> Dict[str, Any]:
    """Create active alerts table."""
    return {
        "id": 32,
        "type": "table",
        "title": "Active Alerts",
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [{"expr": "gong_active_alerts", "refId": "A", "format": "table"}],
        "options": {
            "showHeader": True,
            "sortBy": [{"displayName": "created_at", "desc": True}],
        },
    }


def _create_alert_response_time(self, x: int, y: int, w: int, h: int) -> Dict[str, Any]:
    """Create alert response time panel."""
    return {
        "id": 33,
        "type": "timeseries",
        "title": "Alert Response Time",
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [
            {
                "expr": "avg(gong_alert_response_time_seconds)",
                "refId": "A",
                "legendFormat": "Avg Response Time",
            }
        ],
        "fieldConfig": {"defaults": {"unit": "s"}},
    }


def _create_alert_resolution_stats(
    self, x: int, y: int, w: int, h: int
) -> Dict[str, Any]:
    """Create alert resolution statistics."""
    return {
        "id": 34,
        "type": "stat",
        "title": "Alert Resolution Stats",
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [
            {
                "expr": "avg(gong_alert_resolution_time_seconds)",
                "refId": "A",
                "legendFormat": "Avg Resolution Time",
            },
            {
                "expr": "sum(increase(gong_alerts_resolved_total[24h]))",
                "refId": "B",
                "legendFormat": "Resolved (24h)",
            },
        ],
        "options": {"colorMode": "value", "graphMode": "area"},
    }


def _create_dimension_trends_graph(
    self, x: int, y: int, w: int, h: int
) -> Dict[str, Any]:
    """Create quality dimension trends graph."""
    return {
        "id": 35,
        "type": "timeseries",
        "title": "Quality Dimension Trends",
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [
            {
                "expr": "avg by (dimension) (gong_quality_dimension_score)",
                "refId": "A",
                "legendFormat": "{{dimension}}",
            }
        ],
        "fieldConfig": {"defaults": {"unit": "percentunit", "min": 0, "max": 1}},
    }


def _create_dimension_comparison_radar(
    self, x: int, y: int, w: int, h: int
) -> Dict[str, Any]:
    """Create dimension comparison radar chart (placeholder)."""
    # Note: Grafana doesn't have native radar charts, using table as placeholder
    return {
        "id": 36,
        "type": "table",
        "title": "Quality Dimensions Comparison",
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [
            {
                "expr": "avg by (dimension) (gong_quality_dimension_score)",
                "refId": "A",
                "format": "table",
            }
        ],
    }


def _create_weekly_quality_heatmap(
    self, x: int, y: int, w: int, h: int
) -> Dict[str, Any]:
    """Create weekly quality heatmap."""
    return {
        "id": 37,
        "type": "heatmap",
        "title": "Weekly Quality Patterns",
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [
            {
                "expr": """
                avg by (dayofweek, hour) (
                    label_join(
                        gong_data_quality_score,
                        "dayofweek", "", "dayofweek"
                    )
                )
            """,
                "refId": "A",
                "format": "heatmap",
            }
        ],
    }


def _create_hourly_pattern_graph(
    self, x: int, y: int, w: int, h: int
) -> Dict[str, Any]:
    """Create hourly pattern graph."""
    return {
        "id": 38,
        "type": "timeseries",
        "title": "Hourly Quality Patterns",
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [
            {
                "expr": "avg by (hour) (gong_data_quality_score)",
                "refId": "A",
                "legendFormat": "Hour {{hour}}",
            }
        ],
        "fieldConfig": {"defaults": {"unit": "percentunit"}},
    }


def _create_quality_forecast(self, x: int, y: int, w: int, h: int) -> Dict[str, Any]:
    """Create quality forecast panel."""
    return {
        "id": 39,
        "type": "timeseries",
        "title": "Quality Score Forecast",
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [
            {
                "expr": "avg(gong_data_quality_score)",
                "refId": "A",
                "legendFormat": "Actual",
            },
            {
                "expr": "predict_linear(gong_data_quality_score[1h], 3600)",
                "refId": "B",
                "legendFormat": "Forecast (1h)",
            },
        ],
        "fieldConfig": {
            "defaults": {
                "unit": "percentunit",
                "custom": {"lineStyle": {"dash": [10, 10]}},
            },
            "overrides": [
                {
                    "matcher": {"id": "byName", "options": "Forecast (1h)"},
                    "properties": [
                        {"id": "custom.lineStyle", "value": {"dash": [10, 10]}}
                    ],
                }
            ],
        },
    }


def _create_anomaly_detection_graph(
    self, x: int, y: int, w: int, h: int
) -> Dict[str, Any]:
    """Create anomaly detection graph."""
    return {
        "id": 40,
        "type": "timeseries",
        "title": "Quality Anomaly Detection",
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [
            {
                "expr": "avg(gong_data_quality_score)",
                "refId": "A",
                "legendFormat": "Quality Score",
            },
            {
                "expr": "avg(gong_data_quality_score) - 2 * stddev_over_time(gong_data_quality_score[1h])",
                "refId": "B",
                "legendFormat": "Lower Bound",
            },
            {
                "expr": "avg(gong_data_quality_score) + 2 * stddev_over_time(gong_data_quality_score[1h])",
                "refId": "C",
                "legendFormat": "Upper Bound",
            },
        ],
        "fieldConfig": {"defaults": {"unit": "percentunit"}},
    }
