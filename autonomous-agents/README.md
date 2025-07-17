# 🤖 Sophia AI Autonomous Agents

Autonomous agents that monitor, analyze, and take intelligent actions across the Sophia AI infrastructure.

## 📋 Overview

The Autonomous Agents framework provides a foundation for building intelligent monitoring and optimization agents that can:

- 🔍 **Monitor** infrastructure resources in real-time
- 📊 **Analyze** patterns and detect anomalies
- 💡 **Recommend** optimizations and cost savings
- 🚨 **Alert** on critical issues via Slack
- 📈 **Export** metrics to Prometheus for dashboards

## 🏗️ Architecture

```
autonomous-agents/
├── infrastructure/          # Infrastructure monitoring agents
│   ├── base_infrastructure_agent.py  # Base class with common functionality
│   └── lambda_labs_monitor.py        # Lambda Labs GPU monitoring
├── monitoring/              # Monitoring utilities
│   └── prometheus_exporter.py        # Prometheus metrics export
└── README.md               # This file
```

## 🚀 Lambda Labs GPU Monitoring Agent

### Features

- **Real-time GPU Monitoring**
  - GPU utilization percentage
  - Memory usage and availability
  - Temperature monitoring
  - Power consumption tracking

- **Intelligent Anomaly Detection**
  - High GPU usage (>80% for 15+ minutes)
  - Low GPU usage (<20% for 30+ minutes)
  - High temperature warnings (>85°C)
  - Memory pressure alerts (>90%)

- **Cost Optimization**
  - Automatic cost calculations
  - Downgrade recommendations for underutilized instances
  - Monthly savings estimates
  - Instance type optimization suggestions

- **Prometheus Integration**
  - Export all metrics in Prometheus format
  - Ready for Grafana dashboards
  - Historical data tracking
  - Custom alert rules

### Configuration

All configuration is managed via Pulumi ESC environment variables:

```bash
# Monitoring intervals
LAMBDA_LABS_MONITOR_INTERVAL=300        # 5 minutes (default)

# Thresholds
LAMBDA_LABS_HIGH_GPU_THRESHOLD=80       # High usage threshold
LAMBDA_LABS_LOW_GPU_THRESHOLD=20        # Low usage threshold
LAMBDA_LABS_HIGH_TEMP_THRESHOLD=85      # Temperature warning
LAMBDA_LABS_HIGH_MEMORY_THRESHOLD=90    # Memory pressure

# Duration thresholds
LAMBDA_LABS_HIGH_USAGE_DURATION_MINS=15 # Minutes before high usage alert
LAMBDA_LABS_LOW_USAGE_DURATION_MINS=30  # Minutes before low usage alert

# Prometheus exporter
PROMETHEUS_EXPORTER_PORT=9090           # Metrics endpoint port
PROMETHEUS_EXPORTER_HOST=0.0.0.0        # Bind address
```

### Metrics Exported

The agent exports the following Prometheus metrics:

```prometheus
# GPU Metrics
lambda_labs_gpu_utilization_percent{instance_id, instance_name, instance_type}
lambda_labs_gpu_memory_percent{instance_id, instance_name, instance_type}
lambda_labs_gpu_temperature_celsius{instance_id, instance_name, instance_type}
lambda_labs_gpu_power_watts{instance_id, instance_name, instance_type}

# Cost Metrics
lambda_labs_instance_cost_dollars{instance_id, instance_type, period}

# Anomaly Detection
lambda_labs_anomaly_detected{instance_id, anomaly_type}

# Agent Health
lambda_labs_monitor_status
lambda_labs_monitor_monitoring_runs_total
lambda_labs_monitor_monitoring_errors_total
lambda_labs_monitor_monitoring_duration_seconds
lambda_labs_monitor_alerts_sent_total{severity, type}
```

## 🛠️ Usage

### Running the Test Script

```bash
# Activate virtual environment
source activate_sophia_env.sh

# Run the test script
python scripts/test_lambda_labs_monitor.py
```

### Integration with Production

```python
from autonomous_agents.infrastructure.lambda_labs_monitor import LambdaLabsMonitorAgent
from autonomous_agents.monitoring.prometheus_exporter import exporter, collector

# Create and start the agent
agent = LambdaLabsMonitorAgent()
collector.register_agent("lambda_labs_monitor", agent)

await exporter.start()  # Start Prometheus endpoint
await agent.start()     # Start monitoring

# Access metrics at http://localhost:9090/metrics
```

### Prometheus Configuration

Add to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'sophia_autonomous_agents'
    static_configs:
      - targets: ['localhost:9090']
    scrape_interval: 30s
```

### Grafana Dashboard

Import the dashboard JSON (to be created) for visualizing:
- GPU utilization heatmap
- Memory usage trends
- Temperature monitoring
- Cost tracking over time
- Anomaly detection alerts

## 🔧 Development

### Creating New Agents

1. **Inherit from BaseInfrastructureAgent**:
```python
from autonomous_agents.infrastructure.base_infrastructure_agent import BaseInfrastructureAgent

class MyNewAgent(BaseInfrastructureAgent):
    def __init__(self):
        super().__init__(
            name="my_new_agent",
            description="Description of what this agent does"
        )
    
    async def initialize(self):
        # Setup resources
        pass
    
    async def monitor(self):
        # Perform monitoring tasks
        pass
    
    async def cleanup(self):
        # Cleanup resources
        pass
```

2. **Add Prometheus Metrics**:
```python
from prometheus_client import Gauge, Counter

self.my_metric = Gauge(
    'my_agent_metric_name',
    'Description of the metric',
    ['label1', 'label2']
)
```

3. **Implement Anomaly Detection**:
```python
async def _check_anomalies(self, metrics):
    if metrics.value > threshold:
        await self.send_alert(
            AlertSeverity.WARNING,
            "Anomaly detected",
            {"value": metrics.value, "threshold": threshold}
        )
```

## 🚨 Alert Integration

### Slack Integration (Coming Soon)

The agent will integrate with the Slack MCP server to send alerts:

```python
# Future implementation
await self.slack_client.send_message(
    channel="#sophia-infrastructure",
    text=f"[{severity}] {message}",
    attachments=[...]
)
```

### Alert Types

- **INFO**: Optimization recommendations, low usage notifications
- **WARNING**: High usage, temperature warnings, memory pressure
- **ERROR**: API failures, connection issues
- **CRITICAL**: Multiple failures, system-wide issues

## 📊 Monitoring Best Practices

1. **Set Appropriate Thresholds**
   - Adjust based on your workload patterns
   - Consider time-of-day variations
   - Account for batch job schedules

2. **Configure Alert Fatigue Prevention**
   - Use duration thresholds to avoid flapping
   - Implement hysteresis for state changes
   - Group related alerts

3. **Cost Optimization Strategy**
   - Review recommendations weekly
   - Consider workload consolidation
   - Plan for reserved instances

4. **Performance Monitoring**
   - Track GPU utilization trends
   - Monitor memory usage patterns
   - Watch for temperature spikes

## 🔒 Security Considerations

- API keys stored in Pulumi ESC (never in code)
- Metrics endpoint can be secured with authentication
- No sensitive data in metrics labels
- Audit trail for all autonomous actions

## 🗺️ Roadmap

- [ ] Slack MCP server integration for alerts
- [ ] Automated instance scaling recommendations
- [ ] Historical trend analysis
- [ ] Predictive anomaly detection
- [ ] Cost forecasting models
- [ ] Multi-cloud support (AWS, GCP)
- [ ] Grafana dashboard templates
- [ ] Integration with n8n workflows

## 📚 Related Documentation

- [Sophia AI Agent Development Guide](../AGENT_DEVELOPMENT.md)
- [Pulumi ESC Configuration](../docs/99-reference/PERMANENT_SECRET_MANAGEMENT_SOLUTION.md)
- [MCP Server Integration](../docs/99-reference/MCP_COMPREHENSIVE_PORT_STRATEGY.md)
- [Lambda Labs API Documentation](https://docs.lambdalabs.com/cloud/api)

## 🤝 Contributing

When adding new agents:
1. Follow the established patterns
2. Add comprehensive documentation
3. Include Prometheus metrics
4. Implement proper error handling
5. Add tests for critical functionality

---

**Built with ❤️ for the Sophia AI Platform**
