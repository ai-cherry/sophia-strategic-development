"""Infrastructure configuration re-export."""

# Re-export from the main config location
from infrastructure.config import (
    InfrastructureConfig,
    ServiceType,
    LambdaInstance,
    InstanceRole
)

__all__ = ['InfrastructureConfig', 'ServiceType', 'LambdaInstance', 'InstanceRole']
