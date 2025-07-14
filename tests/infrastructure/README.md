# Infrastructure as Code Testing Framework

This comprehensive testing framework ensures the reliability, performance, and security of our Infrastructure as Code (IaC) implementation using Pulumi.

## Overview

The testing framework provides multi-layer validation:
- **Unit Tests**: Test individual infrastructure components in isolation
- **Integration Tests**: Validate service connectivity and data flow
- **End-to-End Tests**: Test complete infrastructure deployment
- **Performance Tests**: Ensure scalability and performance requirements
- **Security Tests**: Validate access controls and compliance

## Directory Structure

```
tests/infrastructure/
├── conftest.py              # Shared test fixtures and configuration
├── unit/                    # Unit tests for individual components
│   ├── test_ELIMINATED_component.py
│   ├── test_pinecone_component.py
│   └── ...
├── integration/             # Integration tests for service interactions
│   ├── test_ELIMINATED_gong_integration.py
│   └── ...
├── e2e/                     # End-to-end deployment tests
│   └── test_complete_infrastructure.py
├── performance/             # Performance and scalability tests
│   └── test_performance.py
├── security/                # Security and compliance tests
│   └── test_security.py
├── run_all_tests.py         # Test orchestration script
└── README.md                # This file
```

## Running Tests

### Quick Start

Run all tests with default settings:
```bash
python tests/infrastructure/run_all_tests.py
```

### Test Options

```bash
# Run only unit tests (quick feedback)
python tests/infrastructure/run_all_tests.py --quick

# Run all tests including security
python tests/infrastructure/run_all_tests.py --full

# Run tests in parallel
python tests/infrastructure/run_all_tests.py --parallel --workers 8

# Generate coverage report
python tests/infrastructure/run_all_tests.py --coverage

# Run specific test suites
python tests/infrastructure/run_all_tests.py --skip-integration --skip-e2e
```

### Running Individual Test Suites

```bash
# Unit tests only
pytest tests/infrastructure/unit/ -v

# Integration tests only
pytest tests/infrastructure/integration/ -v -m integration

# End-to-end tests only
pytest tests/infrastructure/e2e/ -v -m e2e

# Performance tests only
pytest tests/infrastructure/performance/ -v -m performance

# Security tests only
pytest tests/infrastructure/security/ -v -m security
```

## Test Categories

### Unit Tests

Test individual infrastructure components in isolation:
- Component resource creation
- Configuration validation
- Output verification
- Environment-specific naming

Example:
```python
def test_database_creation(self, pulumi_mock, mock_pulumi_config):
    """Test that the component creates a PostgreSQL database"""
    with pulumi_mock.mocked_provider():
        component = Modern StackComponent("test-ELIMINATED")
        pulumi_mock.assert_resource_created(
            "ELIMINATED:index/database:Database",
            {"name": "SOPHIA_DB_TEST"}
        )
```

### Integration Tests

Test interactions between multiple components:
- Service connectivity
- Data flow validation
- API integration
- Cross-component functionality

Example:
```python
async def test_gong_data_flow_to_ELIMINATED(self, mock_gong_client, mock_ELIMINATED_client):
    """Test data flows correctly from Gong to Modern Stack"""
    # Send test data to Gong
    test_data = {"call_id": "test-123", "duration": 300}
    mock_gong_client.send_test_data(test_data)

    # Verify data in Modern Stack
    result = mock_ELIMINATED_client.query(
        f"SELECT * FROM gong_calls WHERE call_id = '{test_data['call_id']}'"
    )
    assert len(result) == 1
```

### End-to-End Tests

Test complete infrastructure deployment:
- Full stack deployment
- System health validation
- Component connectivity
- Overall functionality

### Performance Tests

Validate performance requirements:
- Query response times
- Concurrent load handling
- Scalability limits
- Resource utilization

Performance thresholds:
- Modern Stack queries: < 2.0s
- Pinecone searches: < 0.1s
- Gong webhooks: < 0.5s
- API responses: < 0.2s

### Security Tests

Ensure security and compliance:
- Secret management validation
- Network security configuration
- Access control verification
- Vulnerability scanning

## CI/CD Integration

The testing framework integrates with GitHub Actions:

```yaml
# .github/workflows/infrastructure-tests.yml
name: Infrastructure Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
```

### Workflow Features

- Automatic test execution on code changes
- Parallel test execution for faster feedback
- Coverage reporting with Codecov
- Performance report artifacts
- Security scanning with Bandit and Safety
- Slack notifications on failure

## Test Fixtures

Common test fixtures are defined in `conftest.py`:

- `pulumi_mock`: Mock Pulumi runtime for unit tests
- `mock_pulumi_config`: Mock configuration values
- `mock_ELIMINATED_client`: Mock Modern Stack client
- `mock_pinecone_client`: Mock Pinecone client
- `mock_gong_client`: Mock Gong client
- `test_environment_manager`: Test stack management

## Writing New Tests

### Unit Test Template

```python
class TestNewComponent:
    def test_resource_creation(self, pulumi_mock, mock_pulumi_config):
        """Test that resources are created correctly"""
        with pulumi_mock.mocked_provider():
            component = NewComponent("test-component")
            # Add assertions

    def test_component_outputs(self, pulumi_mock, mock_pulumi_config):
        """Test component outputs"""
        with pulumi_mock.mocked_provider():
            component = NewComponent("test-component")
            assert "expected_output" in component.outputs
```

### Integration Test Template

```python
@pytest.mark.integration
class TestServiceIntegration:
    @pytest.mark.asyncio
    async def test_service_connectivity(self, mock_service_a, mock_service_b):
        """Test connectivity between services"""
        # Test implementation
```

## Best Practices

1. **Test Isolation**: Each test should be independent and not rely on others
2. **Mock External Services**: Use mocks to avoid dependencies on real services
3. **Clear Assertions**: Make test failures easy to understand
4. **Performance Baselines**: Establish and maintain performance thresholds
5. **Security First**: Include security tests for all new components
6. **Documentation**: Document test purpose and expected behavior

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the project root is in the Python path
2. **Mock Failures**: Check that fixtures are properly configured
3. **Timeout Issues**: Increase timeout for slow operations
4. **Environment Variables**: Ensure required secrets are set

### Debug Mode

Run tests with verbose output:
```bash
pytest tests/infrastructure/ -vv -s --tb=long
```

## Performance Monitoring

Performance test results are saved to:
```
tests/infrastructure/performance/performance_report.json
```

Monitor trends over time to detect performance degradation.

## Security Scanning

Security reports are generated for:
- Code vulnerabilities (Bandit)
- Dependency vulnerabilities (Safety)
- Configuration security (custom tests)

## Contributing

When adding new infrastructure components:
1. Create unit tests for the component
2. Add integration tests for service interactions
3. Update end-to-end tests if needed
4. Define performance thresholds
5. Include security validations

## Continuous Improvement

The testing framework is continuously improved based on:
- Test execution metrics
- Failure analysis
- Performance trends
- Security findings
- Team feedback

For questions or improvements, please open an issue or submit a pull request.
