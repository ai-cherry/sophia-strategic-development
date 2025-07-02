# Sophia AI Configuration Guide

## Performance Configuration Options

### Connection Pool Manager
- `health_check_interval`: Health check frequency in seconds (default: 60)
- `max_size`: Maximum connections in pool (default: 20)
- `min_size`: Minimum connections in pool (default: 5)
- `connection_timeout`: Connection timeout in seconds (default: 30)

### Data Ingestion Configuration
- `chunk_size`: Records per chunk for streaming (default: 5000)
- `batch_size`: Batch size for processing (default: 1000)
- `max_retries`: Maximum retry attempts (default: 3)

### HTTP Client Configuration
- `max_attempts`: Maximum retry attempts for HTTP requests (default: 5)
- `base_delay`: Base delay between retries in seconds (default: 1.0)
- `max_delay`: Maximum delay between retries in seconds (default: 60.0)

## Environment Variables

### Required
- `ENVIRONMENT`: Environment name (prod/staging/dev)
- `PULUMI_ORG`: Pulumi organization name
- `PULUMI_ACCESS_TOKEN`: Pulumi access token

### Optional
- `LOG_LEVEL`: Logging level (default: INFO)
- `HEALTH_CHECK_INTERVAL`: Override health check interval
- `CHUNK_SIZE`: Override data ingestion chunk size

## Best Practices

1. **Always use production environment defaults** unless specifically tuning
2. **Monitor performance metrics** to identify optimization opportunities
3. **Test configuration changes** in staging before production deployment
4. **Use chunked processing** for large datasets to prevent memory issues
5. **Configure appropriate timeouts** based on expected operation duration
