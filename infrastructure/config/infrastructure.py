"""Infrastructure configuration re-export."""

# Re-export from the main config location
from config.infrastructure import (
    InfrastructureConfig,
    ServiceType,
    LambdaInstance,
    InstanceRole
)

__all__ = ['InfrastructureConfig', 'ServiceType', 'LambdaInstance', 'InstanceRole']
