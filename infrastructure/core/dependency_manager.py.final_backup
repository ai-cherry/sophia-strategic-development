from typing import Any

#!/usr/bin/env python3
"""
Sophia AI - Dependency Manager
Manages dependencies and execution order between infrastructure platforms
"""

import asyncio
import contextlib
from dataclasses import dataclass
from enum import Enum


class DependencyType(Enum):
    """Types of dependencies between platforms."""

    CONFIGURATION = (
        "configuration"  # Platform B needs Platform A to be configured first
    )
    DATA_FLOW = "data_flow"  # Platform B receives data from Platform A
    AUTHENTICATION = "authentication"  # Platform B uses Platform A for auth
    NETWORKING = "networking"  # Platform B needs Platform A's network resources
    STORAGE = "storage"  # Platform B uses Platform A for storage


@dataclass
class Dependency:
    """Represents a dependency relationship between platforms."""

    source: str  # Platform that is depended upon
    target: str  # Platform that depends on source
    type: DependencyType
    critical: bool = False  # Whether this dependency is critical for operation
    description: str = ""


class DependencyManager:
    """
    Manages dependencies between infrastructure platforms.
    Provides execution ordering, validation, and impact analysis.
    """

    def __init__(self):
        self.dependencies: list[Dependency] = []
        self._initialize_default_dependencies()

    def _initialize_default_dependencies(self):
        """Initialize default dependencies based on platform relationships."""
        # Data flow dependencies
        self.add_dependency(
            "snowflake",
            "estuary",
            DependencyType.DATA_FLOW,
            critical=True,
            description="Estuary loads data into Snowflake",
        )
        self.add_dependency(
            "gong",
            "estuary",
            DependencyType.DATA_FLOW,
            description="Estuary extracts data from Gong",
        )
        self.add_dependency(
            "slack",
            "estuary",
            DependencyType.DATA_FLOW,
            description="Estuary extracts data from Slack",
        )
        self.add_dependency(
            "hubspot",
            "estuary",
            DependencyType.DATA_FLOW,
            description="Estuary extracts data from HubSpot",
        )
        self.add_dependency(
            "usergems",
            "estuary",
            DependencyType.DATA_FLOW,
            description="Estuary extracts data from UserGems",
        )
        self.add_dependency(
            "apollo",
            "estuary",
            DependencyType.DATA_FLOW,
            description="Estuary extracts data from Apollo.io",
        )

        # Configuration dependencies
        self.add_dependency(
            "snowflake",
            "gong",
            DependencyType.CONFIGURATION,
            description="Gong webhooks may send data to Snowflake",
        )
        self.add_dependency(
            "snowflake",
            "hubspot",
            DependencyType.CONFIGURATION,
            description="HubSpot integration may use Snowflake for analytics",
        )

        # Authentication dependencies
        self.add_dependency(
            "slack",
            "linear",
            DependencyType.AUTHENTICATION,
            description="Linear may use Slack for notifications",
        )
        self.add_dependency(
            "slack",
            "asana",
            DependencyType.AUTHENTICATION,
            description="Asana may use Slack for notifications",
        )

        # Storage dependencies
        self.add_dependency(
            "lambda_labs",
            "vercel",
            DependencyType.STORAGE,
            description="Vercel may use Lambda Labs for compute resources",
        )

        # AI Stack dependencies
        self.add_dependency(
            "portkey",
            "openrouter",
            DependencyType.CONFIGURATION,
            description="Portkey may route requests through OpenRouter",
        )

        # Development dependencies
        self.add_dependency(
            "figma",
            "vercel",
            DependencyType.DATA_FLOW,
            description="Vercel may deploy designs from Figma",
        )

    def add_dependency(
        self,
        source: str,
        target: str,
        dep_type: DependencyType,
        critical: bool = False,
        description: str = "",
    ):
        """Add a dependency relationship."""
        dependency = Dependency(
            source=source,
            target=target,
            type=dep_type,
            critical=critical,
            description=description,
        )

        # Avoid duplicates
        existing = next(
            (
                d
                for d in self.dependencies
                if d.source == source and d.target == target and d.type == dep_type
            ),
            None,
        )
        if not existing:
            self.dependencies.append(dependency)

    def remove_dependency(self, source: str, target: str, dep_type: DependencyType):
        """Remove a dependency relationship."""
        self.dependencies = [
            d
            for d in self.dependencies
            if not (d.source == source and d.target == target and d.type == dep_type)
        ]

    def get_dependencies_for_platform(self, platform: str) -> list[Dependency]:
        """Get all dependencies where the platform is the target (depends on others)."""
        return [d for d in self.dependencies if d.target == platform]

    def get_dependents_of_platform(self, platform: str) -> list[Dependency]:
        """Get all dependencies where the platform is the source (others depend on it)."""
        return [d for d in self.dependencies if d.source == platform]

    async def get_execution_order(self, platforms: list[str]) -> list[str]:
        """
        Get the optimal execution order for a list of platforms based on dependencies.
        Uses topological sorting to ensure dependencies are satisfied.
        """
        # Build adjacency list for the subgraph of requested platforms
        graph: dict[str, set[str]] = {platform: set() for platform in platforms}
        in_degree: dict[str, int] = dict.fromkeys(platforms, 0)

        # Add edges based on dependencies
        for dep in self.dependencies:
            if dep.source in platforms and dep.target in platforms:
                graph[dep.source].add(dep.target)
                in_degree[dep.target] += 1

        # Topological sort using Kahn's algorithm
        queue = [platform for platform in platforms if in_degree[platform] == 0]
        result = []

        while queue:
            current = queue.pop(0)
            result.append(current)

            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Check for circular dependencies
        if len(result) != len(platforms):
            remaining = [p for p in platforms if p not in result]
            raise ValueError(f"Circular dependency detected involving: {remaining}")

        return result

    async def validate_dependencies(self) -> dict[str, Any]:
        """Validate all dependencies for consistency and detect issues."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "circular_dependencies": [],
            "missing_platforms": [],
            "critical_paths": [],
        }

        # Get all unique platforms
        all_platforms = set()
        for dep in self.dependencies:
            all_platforms.add(dep.source)
            all_platforms.add(dep.target)

        # Check for circular dependencies
        try:
            await self.get_execution_order(list(all_platforms))
        except ValueError as e:
            validation_result["valid"] = False
            validation_result["errors"].append(str(e))
            validation_result[
                "circular_dependencies"
            ] = self._detect_circular_dependencies()

        # Check for missing platform definitions (would be checked against actual adapters)
        # This would be implemented when we have the full adapter registry

        # Identify critical paths
        critical_deps = [d for d in self.dependencies if d.critical]
        validation_result["critical_paths"] = self._analyze_critical_paths(
            critical_deps
        )

        return validation_result

    def _detect_circular_dependencies(self) -> list[list[str]]:
        """Detect circular dependencies in the dependency graph."""
        # Build adjacency list
        graph: dict[str, list[str]] = {}
        for dep in self.dependencies:
            if dep.source not in graph:
                graph[dep.source] = []
            graph[dep.source].append(dep.target)

        visited = set()
        rec_stack = set()
        cycles = []

        def dfs(node: str, path: list[str]) -> bool:
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycles.append([*path[cycle_start:], node])
                return True

            if node in visited:
                return False

            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                if dfs(neighbor, path):
                    return True

            path.pop()
            rec_stack.remove(node)
            return False

        for node in graph:
            if node not in visited:
                dfs(node, [])

        return cycles

    def _analyze_critical_paths(
        self, critical_deps: list[Dependency]
    ) -> list[dict[str, Any]]:
        """Analyze critical dependency paths."""
        critical_paths = []

        for dep in critical_deps:
            path_info = {
                "source": dep.source,
                "target": dep.target,
                "type": dep.type.value,
                "description": dep.description,
                "impact": self._calculate_impact(dep),
            }
            critical_paths.append(path_info)

        return critical_paths

    def _calculate_impact(self, dependency: Dependency) -> str:
        """Calculate the impact level of a dependency failure."""
        dependents = self.get_dependents_of_platform(dependency.source)

        if len(dependents) > 5:
            return "high"
        elif len(dependents) > 2:
            return "medium"
        else:
            return "low"

    async def analyze_dependencies(self) -> dict[str, Any]:
        """Provide comprehensive dependency analysis."""
        analysis = {
            "total_dependencies": len(self.dependencies),
            "dependency_types": {},
            "platform_analysis": {},
            "execution_groups": [],
            "risk_assessment": {},
        }

        # Count by type
        for dep_type in DependencyType:
            count = len([d for d in self.dependencies if d.type == dep_type])
            analysis["dependency_types"][dep_type.value] = count

        # Analyze each platform
        all_platforms = set()
        for dep in self.dependencies:
            all_platforms.add(dep.source)
            all_platforms.add(dep.target)

        for platform in all_platforms:
            dependencies = self.get_dependencies_for_platform(platform)
            dependents = self.get_dependents_of_platform(platform)

            analysis["platform_analysis"][platform] = {
                "depends_on_count": len(dependencies),
                "depended_by_count": len(dependents),
                "critical_dependencies": len([d for d in dependencies if d.critical]),
                "dependency_types": list({d.type.value for d in dependencies}),
                "risk_level": self._assess_platform_risk(
                    platform, dependencies, dependents
                ),
            }

        # Create execution groups (platforms that can be executed in parallel)
        try:
            execution_order = await self.get_execution_order(list(all_platforms))
            analysis["execution_groups"] = self._create_execution_groups(
                execution_order
            )
        except ValueError:
            analysis["execution_groups"] = []

        # Risk assessment
        analysis["risk_assessment"] = await self._assess_overall_risk()

        return analysis

    def _assess_platform_risk(
        self,
        platform: str,
        dependencies: list[Dependency],
        dependents: list[Dependency],
    ) -> str:
        """Assess the risk level of a platform based on its dependencies."""
        critical_deps = len([d for d in dependencies if d.critical])
        total_dependents = len(dependents)

        if critical_deps > 2 or total_dependents > 5:
            return "high"
        elif critical_deps > 0 or total_dependents > 2:
            return "medium"
        else:
            return "low"

    def _create_execution_groups(self, execution_order: list[str]) -> list[list[str]]:
        """Create groups of platforms that can be executed in parallel."""
        groups = []
        remaining = set(execution_order)

        while remaining:
            # Find platforms with no remaining dependencies
            current_group = []
            for platform in execution_order:
                if platform not in remaining:
                    continue

                deps = self.get_dependencies_for_platform(platform)
                if all(dep.source not in remaining for dep in deps):
                    current_group.append(platform)

            if not current_group:
                # This shouldn't happen if dependencies are valid
                current_group = list(remaining)

            groups.append(current_group)
            remaining -= set(current_group)

        return groups

    async def _assess_overall_risk(self) -> dict[str, Any]:
        """Assess overall system risk based on dependency structure."""
        critical_deps = [d for d in self.dependencies if d.critical]

        risk_assessment = {
            "critical_dependency_count": len(critical_deps),
            "single_points_of_failure": [],
            "risk_level": "low",
        }

        # Find single points of failure
        all_platforms = set()
        for dep in self.dependencies:
            all_platforms.add(dep.source)
            all_platforms.add(dep.target)

        for platform in all_platforms:
            dependents = self.get_dependents_of_platform(platform)
            critical_dependents = [d for d in dependents if d.critical]

            if len(critical_dependents) > 3:
                risk_assessment["single_points_of_failure"].append(
                    {
                        "platform": platform,
                        "critical_dependents": len(critical_dependents),
                        "total_dependents": len(dependents),
                    }
                )

        # Determine overall risk level
        if risk_assessment["single_points_of_failure"]:
            risk_assessment["risk_level"] = "high"
        elif len(critical_deps) > 5:
            risk_assessment["risk_level"] = "medium"

        return risk_assessment

    async def suggest_optimizations(self) -> list[dict[str, Any]]:
        """Suggest optimizations for the dependency structure."""
        suggestions = []

        analysis = await self.analyze_dependencies()

        # Suggest reducing single points of failure
        for spof in analysis["risk_assessment"]["single_points_of_failure"]:
            suggestions.append(
                {
                    "type": "reduce_single_point_of_failure",
                    "platform": spof["platform"],
                    "description": f"Consider adding redundancy for {spof['platform']} which has {spof['critical_dependents']} critical dependents",
                    "priority": "high",
                }
            )

        # Suggest parallel execution opportunities
        execution_groups = analysis["execution_groups"]
        if len(execution_groups) > len(execution_groups[0]) * 2:
            suggestions.append(
                {
                    "type": "parallel_execution",
                    "description": "Consider optimizing dependencies to enable more parallel execution",
                    "priority": "medium",
                }
            )

        return suggestions


# CLI interface
async def main():
    """CLI interface for dependency management."""
    import argparse

    parser = argparse.ArgumentParser(description="Infrastructure Dependency Manager")
    parser.add_argument("command", choices=["analyze", "validate", "order", "suggest"])
    parser.add_argument("--platforms", nargs="+", help="Platforms for execution order")
    parser.add_argument("--format", choices=["json", "table"], default="json")

    args = parser.parse_args()

    dep_manager = DependencyManager()

    if args.command == "analyze":
        await dep_manager.analyze_dependencies()

    elif args.command == "validate":
        await dep_manager.validate_dependencies()

    elif args.command == "order":
        if not args.platforms:
            return

        with contextlib.suppress(ValueError):
            await dep_manager.get_execution_order(args.platforms)

    elif args.command == "suggest":
        await dep_manager.suggest_optimizations()


if __name__ == "__main__":
    asyncio.run(main())
