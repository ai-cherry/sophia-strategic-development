"""
Business Logic Validator
Validates business logic implementations across services
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class BusinessLogicValidator:
    """
    Validates business logic implementations
    """
    
    def __init__(self):
        self.validation_rules = {
            "data_validation": self._validate_data_integrity,
            "workflow_validation": self._validate_workflow_logic,
            "calculation_validation": self._validate_calculations
        }
    
    async def validate_service_logic(self, service_name: str, 
                                   logic_type: str, 
                                   data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate business logic for a service"""
        try:
            if logic_type in self.validation_rules:
                result = await self.validation_rules[logic_type](service_name, data)
                return {
                    "service": service_name,
                    "logic_type": logic_type,
                    "valid": result["valid"],
                    "issues": result.get("issues", []),
                    "recommendations": result.get("recommendations", [])
                }
            else:
                return {
                    "service": service_name,
                    "logic_type": logic_type,
                    "valid": False,
                    "issues": [f"Unknown logic type: {logic_type}"]
                }
        except Exception as e:
            logger.error(f"Validation error for {service_name}: {e}")
            return {
                "service": service_name,
                "logic_type": logic_type,
                "valid": False,
                "issues": [f"Validation failed: {str(e)}"]
            }
    
    async def _validate_data_integrity(self, service_name: str, 
                                     data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data integrity"""
        issues = []
        recommendations = []
        
        # Check for required fields
        if not data:
            issues.append("No data provided for validation")
        
        # Check data types
        for key, value in data.items():
            if value is None:
                issues.append(f"Null value found for key: {key}")
            elif isinstance(value, str) and not value.strip():
                issues.append(f"Empty string found for key: {key}")
        
        if not issues:
            recommendations.append("Data integrity validation passed")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "recommendations": recommendations
        }
    
    async def _validate_workflow_logic(self, service_name: str, 
                                     data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate workflow logic"""
        issues = []
        recommendations = []
        
        # Check workflow steps
        if "steps" in data:
            steps = data["steps"]
            if not isinstance(steps, list):
                issues.append("Workflow steps must be a list")
            elif len(steps) == 0:
                issues.append("Workflow must have at least one step")
            else:
                for i, step in enumerate(steps):
                    if not isinstance(step, dict):
                        issues.append(f"Step {i} must be a dictionary")
                    elif "action" not in step:
                        issues.append(f"Step {i} missing required 'action' field")
        
        if not issues:
            recommendations.append("Workflow logic validation passed")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "recommendations": recommendations
        }
    
    async def _validate_calculations(self, service_name: str, 
                                   data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate calculation logic"""
        issues = []
        recommendations = []
        
        # Check numeric values
        for key, value in data.items():
            if isinstance(value, (int, float)):
                if value < 0 and key in ["amount", "quantity", "count"]:
                    issues.append(f"Negative value not allowed for {key}: {value}")
                elif isinstance(value, float) and (value != value):  # NaN check
                    issues.append(f"NaN value found for {key}")
        
        if not issues:
            recommendations.append("Calculation validation passed")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "recommendations": recommendations
        }

# Global instance
business_logic_validator = BusinessLogicValidator()
