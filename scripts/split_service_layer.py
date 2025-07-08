import ast
import os
from pathlib import Path


class ServiceAnalyzer(ast.NodeVisitor):
    """Analyze service files to determine if they're business logic or infrastructure"""

    def __init__(self):
        self.has_external_imports = False
        self.has_io_operations = False
        self.imports = []

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)
            if any(
                lib in alias.name
                for lib in [
                    "requests",
                    "httpx",
                    "boto3",
                    "snowflake",
                    "redis",
                    "psycopg2",
                    "aiohttp",
                    "gong_api_client",
                ]
            ):
                self.has_external_imports = True

    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.append(node.module)
            if any(
                lib in node.module
                for lib in [
                    "requests",
                    "httpx",
                    "boto3",
                    "snowflake",
                    "redis",
                    "psycopg2",
                    "aiohttp",
                    "gong_api_client",
                ]
            ):
                self.has_external_imports = True

    def visit_Call(self, node):
        # Check for I/O operations
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in [
                "get",
                "post",
                "put",
                "delete",
                "execute",
                "query",
                "connect",
            ]:
                self.has_io_operations = True
        self.generic_visit(node)


def analyze_service_file(file_path):
    """Determine if service file should go to core or infrastructure"""
    with open(file_path) as f:
        try:
            tree = ast.parse(f.read())
            analyzer = ServiceAnalyzer()
            analyzer.visit(tree)

            # If it has external dependencies or I/O, it's infrastructure
            if analyzer.has_external_imports or analyzer.has_io_operations:
                return "infrastructure"
            else:
                return "core"
        except:
            return "manual_review"


def split_services():
    """Split service files between core and infrastructure"""
    services_dir = Path("backend/services")

    core_services = []
    infra_services = []
    manual_review = []

    if not services_dir.exists():
        return

    for service_file in services_dir.rglob("*.py"):
        if "__pycache__" in str(service_file):
            continue

        classification = analyze_service_file(service_file)

        if classification == "core":
            core_services.append(service_file)
        elif classification == "infrastructure":
            infra_services.append(service_file)
        else:
            manual_review.append(service_file)

    # Generate report
    with open("reports/service_split_report.txt", "w") as f:
        f.write("Service Layer Split Analysis\n")
        f.write("=" * 50 + "\n\n")

        f.write(f"Core Services ({len(core_services)}):\n")
        for svc in core_services:
            f.write(f"  - {svc}\n")

        f.write(f"\nInfrastructure Services ({len(infra_services)}):\n")
        for svc in infra_services:
            f.write(f"  - {svc}\n")

        f.write(f"\nManual Review Required ({len(manual_review)}):\n")
        for svc in manual_review:
            f.write(f"  - {svc}\n")



if __name__ == "__main__":
    split_services()
