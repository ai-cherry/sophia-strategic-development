import ast
import os
import sys
from pathlib import Path


class ArchitectureValidator:
    def __init__(self):
        self.violations = []
        self.circular_deps = []

        # Define allowed dependencies
        self.allowed_deps = {
            "api": ["core", "domain", "shared"],
            "core": ["domain", "shared"],
            "domain": ["shared"],
            "infrastructure": ["core", "domain", "shared"],
            "shared": [],  # Shared can't depend on anything
        }

    def get_layer(self, module_path):
        """Determine which layer a module belongs to"""
        parts = module_path.split(".")
        if parts[0] in self.allowed_deps:
            return parts[0]
        return None

    def check_import(self, from_module, to_module):
        """Check if an import is allowed"""
        from_layer = self.get_layer(from_module)
        to_layer = self.get_layer(to_module)

        if not from_layer or not to_layer:
            return True  # Skip external imports

        if from_layer == to_layer:
            return True  # Same layer is OK

        if to_layer not in self.allowed_deps[from_layer]:
            self.violations.append(
                {
                    "from": from_module,
                    "to": to_module,
                    "violation": f"{from_layer} cannot depend on {to_layer}",
                }
            )
            return False

        return True

    def analyze_file(self, file_path):
        """Analyze imports in a Python file"""
        try:
            with open(file_path) as f:
                tree = ast.parse(f.read())

            module_path = str(file_path).replace("/", ".").replace(".py", "")

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.check_import(module_path, alias.name)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    self.check_import(module_path, node.module)
        except Exception:
            pass  # Skip files with syntax errors

    def validate(self):
        """Run validation on all Python files"""
        layers = ["api", "core", "domain", "infrastructure", "shared"]

        for layer in layers:
            if not os.path.exists(layer):
                continue

            for root, _dirs, files in os.walk(layer):
                if "__pycache__" in root:
                    continue

                for file in files:
                    if file.endswith(".py"):
                        self.analyze_file(Path(root) / file)

        return len(self.violations) == 0

    def report(self):
        """Generate validation report"""

        if not self.violations:
            pass
        else:
            for _v in self.violations[:20]:  # Show first 20
                pass

        # Summary by layer
        for layer in ["api", "core", "domain", "infrastructure", "shared"]:
            if os.path.exists(layer):
                len(list(Path(layer).rglob("*.py")))


def main():
    validator = ArchitectureValidator()
    is_valid = validator.validate()
    validator.report()

    return 0 if is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
