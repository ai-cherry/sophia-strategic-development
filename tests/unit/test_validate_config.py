import os
import importlib.util
from pathlib import Path
import pytest

SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "validate_sophia_config.py"
spec = importlib.util.spec_from_file_location("validate_sophia_config", SCRIPT_PATH)
validate_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_module)

validate_esc_environment = validate_module.validate_esc_environment
validate_lambda_labs_config = validate_module.validate_lambda_labs_config
validate_mcp_servers = validate_module.validate_mcp_servers
validate_business_intelligence_pipeline = validate_module.validate_business_intelligence_pipeline
validate_service_config = validate_module.validate_service_config


def test_validate_esc_environment_success(monkeypatch):
    monkeypatch.setenv("PULUMI_ACCESS_TOKEN", "token")
    monkeypatch.setenv("PULUMI_ORG", "org")
    monkeypatch.setenv("PULUMI_ESC_ENV", "org/project/stack")
    assert validate_esc_environment() is True


def test_validate_esc_environment_missing(monkeypatch):
    monkeypatch.delenv("PULUMI_ACCESS_TOKEN", raising=False)
    monkeypatch.setenv("PULUMI_ORG", "org")
    monkeypatch.setenv("PULUMI_ESC_ENV", "org/project/stack")
    with pytest.raises(EnvironmentError):
        validate_esc_environment()


def test_validate_lambda_labs_config(monkeypatch):
    monkeypatch.setenv("LAMBDA_LABS_API_KEY", "realkey")
    assert validate_lambda_labs_config() is True

    monkeypatch.setenv("LAMBDA_LABS_API_KEY", "your_lambda_labs_api_key")
    with pytest.raises(ValueError):
        validate_lambda_labs_config()


def test_validate_mcp_servers():
    servers = validate_mcp_servers()
    assert isinstance(servers, list)
    assert any(s["name"] == "pulumi" for s in servers)


def test_validate_business_intelligence_pipeline(monkeypatch):
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("POSTGRES_PASSWORD", "pass")
    monkeypatch.setenv("REDIS_HOST", "localhost")
    assert validate_business_intelligence_pipeline() is True


def test_validate_service_config(monkeypatch):
    monkeypatch.setenv("SNOWFLAKE_USER", "user")
    monkeypatch.setenv("SNOWFLAKE_PASSWORD", "pw")
    monkeypatch.setenv("SNOWFLAKE_ACCOUNT", "acc")
    assert validate_service_config("snowflake") is True

    monkeypatch.delenv("SNOWFLAKE_USER")
    with pytest.raises(EnvironmentError):
        validate_service_config("snowflake")
