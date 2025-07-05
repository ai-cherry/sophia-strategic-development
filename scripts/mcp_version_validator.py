#!/usr/bin/env python3
"""
MCP Version Validator
Automated validation of semantic versioning and compatibility rules for MCP servers
"""

import json
import re
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

import yaml


class ValidationSeverity(Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class ValidationResult:
    """Result of version validation"""

    severity: ValidationSeverity
    server_name: str
    message: str
    details: Optional[dict] = None


class MCPVersionValidator:
    """
    Validates MCP server versions against semantic versioning rules
    and compatibility requirements
    """

    def __init__(self, config_path: str = "config/mcp_version_management.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.validation_results: list[ValidationResult] = []

        # Semantic version regex pattern
        self.semver_pattern = re.compile(
            r"^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9\-\.]+))?(?:\+([a-zA-Z0-9\-\.]+))?$"
        )

    def _load_config(self) -> dict:
        """Load version management configuration"""
        try:
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config {self.config_path}: {e}")
            sys.exit(1)

    def validate_all_servers(self) -> list[ValidationResult]:
        """Validate all MCP servers in the configuration"""
        self.validation_results = []

        server_versions = self.config.get("server_versions", {})
        version_policy = self.config.get("version_policy", {})
        compatibility_matrix = self.config.get("compatibility_matrix", {})

        print(f"🔍 Validating {len(server_versions)} MCP servers...")

        for server_name, server_config in server_versions.items():
            self._validate_server(server_name, server_config, version_policy)

        # Validate compatibility matrix
        self._validate_compatibility_matrix(compatibility_matrix, server_versions)

        # Validate deprecation schedule
        self._validate_deprecation_schedule()

        return self.validation_results

    def _validate_server(
        self, server_name: str, server_config: dict, version_policy: dict
    ) -> None:
        """Validate individual server version configuration"""

        # 1. Validate semantic versioning format
        current_version = server_config.get("current")
        if not current_version:
            self._add_result(
                ValidationSeverity.ERROR, server_name, "Missing current version"
            )
            return

        if not self._is_valid_semver(current_version):
            self._add_result(
                ValidationSeverity.ERROR,
                server_name,
                f"Invalid semantic version format: {current_version}",
            )

        # 2. Validate supported versions
        supported_versions = server_config.get("supported", [])
        for version in supported_versions:
            if not self._is_valid_version_pattern(version):
                self._add_result(
                    ValidationSeverity.WARNING,
                    server_name,
                    f"Invalid version pattern in supported: {version}",
                )

        # 3. Validate deprecated versions
        deprecated_versions = server_config.get("deprecated", [])
        for version in deprecated_versions:
            if not self._is_valid_version_pattern(version):
                self._add_result(
                    ValidationSeverity.WARNING,
                    server_name,
                    f"Invalid version pattern in deprecated: {version}",
                )

        # 4. Check if current version is in supported list
        if not self._version_in_patterns(current_version, supported_versions):
            self._add_result(
                ValidationSeverity.ERROR,
                server_name,
                f"Current version {current_version} not in supported versions",
            )

        # 5. Check if current version is deprecated
        if self._version_in_patterns(current_version, deprecated_versions):
            self._add_result(
                ValidationSeverity.WARNING,
                server_name,
                f"Current version {current_version} is deprecated",
            )

        # 6. Validate API version
        api_version = server_config.get("api_version")
        if not api_version:
            self._add_result(
                ValidationSeverity.WARNING, server_name, "Missing API version"
            )
        elif not re.match(r"^v\d+$", api_version):
            self._add_result(
                ValidationSeverity.WARNING,
                server_name,
                f"API version should follow vN format: {api_version}",
            )

        # 7. Validate capabilities
        capabilities = server_config.get("capabilities", [])
        if not capabilities:
            self._add_result(
                ValidationSeverity.INFO, server_name, "No capabilities defined"
            )
        elif not isinstance(capabilities, list):
            self._add_result(
                ValidationSeverity.ERROR, server_name, "Capabilities must be a list"
            )

    def _validate_compatibility_matrix(
        self, compatibility_matrix: dict, server_versions: dict
    ) -> None:
        """Validate compatibility matrix consistency"""

        # Check if all servers referenced in compatibility matrix exist
        for server_name, compatibility_config in compatibility_matrix.items():
            if server_name == "api_versions":
                continue

            if server_name not in server_versions:
                self._add_result(
                    ValidationSeverity.ERROR,
                    "compatibility_matrix",
                    f"Server {server_name} referenced but not defined",
                )
                continue

            # Validate compatibility entries
            if isinstance(compatibility_config, dict):
                for version, compatibility_info in compatibility_config.items():
                    if isinstance(compatibility_info, dict):
                        # Check compatible_with references
                        compatible_with = compatibility_info.get("compatible_with", [])
                        for compat_ref in compatible_with:
                            self._validate_compatibility_reference(
                                compat_ref, server_versions
                            )

                        # Check incompatible_with references
                        incompatible_with = compatibility_info.get(
                            "incompatible_with", []
                        )
                        for incompat_ref in incompatible_with:
                            self._validate_compatibility_reference(
                                incompat_ref, server_versions
                            )

    def _validate_compatibility_reference(
        self, reference: str, server_versions: dict
    ) -> None:
        """Validate a compatibility reference like 'server_name:version_pattern'"""
        if ":" not in reference:
            self._add_result(
                ValidationSeverity.WARNING,
                "compatibility_matrix",
                f"Compatibility reference should include version: {reference}",
            )
            return

        server_name, version_pattern = reference.split(":", 1)

        if server_name not in server_versions:
            self._add_result(
                ValidationSeverity.ERROR,
                "compatibility_matrix",
                f"Referenced server {server_name} not defined",
            )

        if not self._is_valid_version_pattern(version_pattern):
            self._add_result(
                ValidationSeverity.WARNING,
                "compatibility_matrix",
                f"Invalid version pattern: {version_pattern}",
            )

    def _validate_deprecation_schedule(self) -> None:
        """Validate deprecation schedule entries"""
        deprecation_schedule = self.config.get("deprecation_schedule", {})

        for period, deprecations in deprecation_schedule.items():
            # Validate period format (should be YYYY-QN)
            if not re.match(r"^\d{4}-Q[1-4]$", period):
                self._add_result(
                    ValidationSeverity.WARNING,
                    "deprecation_schedule",
                    f"Invalid period format: {period} (should be YYYY-QN)",
                )

            # Validate deprecation entries
            if isinstance(deprecations, list):
                for deprecation in deprecations:
                    if isinstance(deprecation, dict):
                        server = deprecation.get("server")
                        versions = deprecation.get("versions", [])
                        replacement = deprecation.get("replacement")
                        reason = deprecation.get("reason")

                        if not server:
                            self._add_result(
                                ValidationSeverity.ERROR,
                                "deprecation_schedule",
                                f"Missing server name in {period}",
                            )

                        if not versions:
                            self._add_result(
                                ValidationSeverity.ERROR,
                                "deprecation_schedule",
                                f"Missing versions in {period} for {server}",
                            )

                        if not replacement:
                            self._add_result(
                                ValidationSeverity.WARNING,
                                "deprecation_schedule",
                                f"Missing replacement version in {period} for {server}",
                            )

                        if not reason:
                            self._add_result(
                                ValidationSeverity.WARNING,
                                "deprecation_schedule",
                                f"Missing deprecation reason in {period} for {server}",
                            )

    def _is_valid_semver(self, version: str) -> bool:
        """Check if version follows semantic versioning format"""
        return bool(self.semver_pattern.match(version))

    def _is_valid_version_pattern(self, pattern: str) -> bool:
        """Check if version pattern is valid (e.g., '1.x.x', '2.0.x', '1.2.3')"""
        # Exact version
        if self.semver_pattern.match(pattern):
            return True

        # Pattern with x (e.g., '1.x.x', '2.0.x')
        pattern_regex = re.compile(r"^(\d+|x)\.(\d+|x)\.(\d+|x)$")
        return bool(pattern_regex.match(pattern))

    def _version_in_patterns(self, version: str, patterns: list[str]) -> bool:
        """Check if version matches any of the patterns"""
        for pattern in patterns:
            if self._version_matches_pattern(version, pattern):
                return True
        return False

    def _version_matches_pattern(self, version: str, pattern: str) -> bool:
        """Check if version matches a specific pattern"""
        if version == pattern:
            return True

        # Parse version and pattern
        version_match = self.semver_pattern.match(version)
        if not version_match:
            return False

        version_parts = version_match.groups()[:3]  # major, minor, patch

        # Handle pattern matching
        if "x" in pattern:
            pattern_parts = pattern.split(".")
            if len(pattern_parts) != 3:
                return False

            for i, (v_part, p_part) in enumerate(
                zip(version_parts, pattern_parts, strict=False)
            ):
                if p_part != "x" and v_part != p_part:
                    return False
            return True

        return False

    def _add_result(
        self,
        severity: ValidationSeverity,
        server_name: str,
        message: str,
        details: Optional[dict] = None,
    ) -> None:
        """Add validation result"""
        self.validation_results.append(
            ValidationResult(
                severity=severity,
                server_name=server_name,
                message=message,
                details=details or {},
            )
        )

    def generate_report(self) -> dict:
        """Generate validation report"""
        error_count = sum(
            1 for r in self.validation_results if r.severity == ValidationSeverity.ERROR
        )
        warning_count = sum(
            1
            for r in self.validation_results
            if r.severity == ValidationSeverity.WARNING
        )
        info_count = sum(
            1 for r in self.validation_results if r.severity == ValidationSeverity.INFO
        )

        return {
            "timestamp": str(Path.cwd()),
            "total_issues": len(self.validation_results),
            "errors": error_count,
            "warnings": warning_count,
            "info": info_count,
            "validation_passed": error_count == 0,
            "results": [
                {
                    "severity": r.severity.value,
                    "server": r.server_name,
                    "message": r.message,
                    "details": r.details,
                }
                for r in self.validation_results
            ],
        }

    def print_results(self) -> None:
        """Print validation results to console"""
        if not self.validation_results:
            print("✅ All MCP version validations passed!")
            return

        # Group by severity
        errors = [
            r for r in self.validation_results if r.severity == ValidationSeverity.ERROR
        ]
        warnings = [
            r
            for r in self.validation_results
            if r.severity == ValidationSeverity.WARNING
        ]
        info = [
            r for r in self.validation_results if r.severity == ValidationSeverity.INFO
        ]

        if errors:
            print(f"\n❌ ERRORS ({len(errors)}):")
            for result in errors:
                print(f"  {result.server_name}: {result.message}")

        if warnings:
            print(f"\n⚠️  WARNINGS ({len(warnings)}):")
            for result in warnings:
                print(f"  {result.server_name}: {result.message}")

        if info:
            print(f"\n💡 INFO ({len(info)}):")
            for result in info:
                print(f"  {result.server_name}: {result.message}")

        print(
            f"\n📊 Summary: {len(errors)} errors, {len(warnings)} warnings, {len(info)} info"
        )

        if errors:
            print("❌ Validation FAILED - fix errors before proceeding")
        else:
            print("✅ Validation PASSED - warnings should be addressed when possible")


def main():
    """Main CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Validate MCP server versions")
    parser.add_argument(
        "--config",
        default="config/mcp_version_management.yaml",
        help="Path to version management config",
    )
    parser.add_argument("--output", help="Output report to JSON file")
    parser.add_argument("--quiet", action="store_true", help="Only show errors")

    args = parser.parse_args()

    validator = MCPVersionValidator(args.config)
    validator.validate_all_servers()

    if not args.quiet:
        validator.print_results()

    # Generate report if requested
    if args.output:
        report = validator.generate_report()
        with open(args.output, "w") as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to {args.output}")

    # Exit with error code if validation failed
    error_count = sum(
        1
        for r in validator.validation_results
        if r.severity == ValidationSeverity.ERROR
    )

    if error_count > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
