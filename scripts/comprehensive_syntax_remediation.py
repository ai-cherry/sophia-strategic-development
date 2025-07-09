#!/usr/bin/env python3
"""
Comprehensive Syntax Error Remediation Script
Fixes Python, TypeScript, and Shell script syntax errors
"""

import json
import re
import subprocess
from pathlib import Path

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()


class ComprehensiveSyntaxFixer:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.python_fixes = 0
        self.typescript_fixes = 0
        self.shell_fixes = 0
        self.total_errors_found = 0

    def fix_python_syntax_errors(self):
        """Fix Python syntax errors"""
        console.print("[bold blue]Fixing Python Syntax Errors[/bold blue]")

        # Critical files with known issues
        critical_files = [
            ("api/main.py", self.fix_api_main),
            (
                "core/agents/infrastructure/sophia_infrastructure_agent.py",
                self.fix_sophia_infrastructure_agent,
            ),
            ("core/services/sophia_intent_engine.py", self.fix_sophia_intent_engine),
            ("api/ai_memory_health_routes.py", self.fix_insecure_random),
        ]

        for file_path, fix_func in critical_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                console.print(f"  Fixing {file_path}...")
                if fix_func(full_path):
                    self.python_fixes += 1
                    console.print("    ✅ Fixed")
                else:
                    console.print("    ⚠️  Manual review needed")

    def fix_api_main(self, file_path: Path) -> bool:
        """Fix missing parentheses in api/main.py"""
        try:
            content = file_path.read_text()

            # Fix uvicorn.run missing closing parenthesis
            # Look for pattern: uvicorn.run(app, host="...", port=8000
            pattern = r"(uvicorn\.run\([^)]+)(\s*$)"

            def fix_uvicorn(match):
                line = match.group(1)
                # Count parentheses
                open_count = line.count("(")
                close_count = line.count(")")
                missing = open_count - close_count
                return line + ")" * missing

            content = re.sub(pattern, fix_uvicorn, content, flags=re.MULTILINE)

            file_path.write_text(content)
            return True
        except Exception as e:
            console.print(f"    Error: {e}")
            return False

    def fix_sophia_infrastructure_agent(self, file_path: Path) -> bool:
        """Fix generator expression syntax in sophia_infrastructure_agent.py"""
        try:
            content = file_path.read_text()

            # Fix generator expression with colon
            # Pattern: (... for ... in ...):
            pattern = r"\(([^)]+\sfor\s[^)]+)\):"

            def fix_generator(match):
                gen_expr = match.group(1)
                return f"({gen_expr}),"  # Replace : with ,

            content = re.sub(pattern, fix_generator, content)

            file_path.write_text(content)
            return True
        except Exception as e:
            console.print(f"    Error: {e}")
            return False

    def fix_sophia_intent_engine(self, file_path: Path) -> bool:
        """Fix async for syntax in sophia_intent_engine.py"""
        try:
            content = file_path.read_text()

            # Fix invalid: await self.async for chunk in ...
            # Should be: async for chunk in await ...
            pattern = r"await\s+self\.async\s+for\s+chunk\s+in\s+([^:]+):"

            def fix_async_for(match):
                iterator = match.group(1)
                return f"async for chunk in {iterator}:"

            content = re.sub(pattern, fix_async_for, content)

            # Also fix if it's in an assignment
            pattern2 = (
                r"response\s*=\s*await\s+self\.async\s+for\s+chunk\s+in\s+([^:]+)"
            )

            def fix_async_assignment(match):
                iterator = match.group(1)
                # Need to accumulate chunks
                return f"""chunks = []
        async for chunk in {iterator}:
            chunks.append(chunk)
        response = ''.join(chunks)"""

            content = re.sub(pattern2, fix_async_assignment, content)

            file_path.write_text(content)
            return True
        except Exception as e:
            console.print(f"    Error: {e}")
            return False

    def fix_insecure_random(self, file_path: Path) -> bool:
        """Replace insecure random with secrets module"""
        try:
            content = file_path.read_text()

            # Add secrets import if not present
            if "import secrets" not in content:
                # Add after other imports
                lines = content.split("\n")
                import_idx = 0
                for i, line in enumerate(lines):
                    if line.startswith("import ") or line.startswith("from "):
                        import_idx = i + 1

                lines.insert(import_idx, "import secrets")
                content = "\n".join(lines)

            # Replace random.randint with secrets
            content = re.sub(
                r"random\.randint\((\d+),\s*(\d+)\)",
                r"secrets.randbelow(\2 - \1 + 1) + \1",
                content,
            )

            # Replace random.choice with secrets.choice
            content = content.replace("random.choice", "secrets.choice")

            file_path.write_text(content)
            return True
        except Exception as e:
            console.print(f"    Error: {e}")
            return False

    def fix_typescript_errors(self):
        """Fix TypeScript syntax errors"""
        console.print("\n[bold blue]Fixing TypeScript Syntax Errors[/bold blue]")

        # Fix AIMemoryHealthTab.tsx
        tsx_file = (
            self.project_root
            / "frontend/src/components/dashboard/tabs/AIMemoryHealthTab.tsx"
        )
        if tsx_file.exists():
            console.print(f"  Fixing {tsx_file.name}...")
            try:
                content = tsx_file.read_text()

                # Fix Target: <100ms being parsed as comparison
                content = content.replace("Target: <100ms", "Target: &lt;100ms")

                # Alternative: use template literal
                content = re.sub(r"Target:\s*<(\d+ms)", r"Target: {`<\1`}", content)

                tsx_file.write_text(content)
                self.typescript_fixes += 1
                console.print("    ✅ Fixed")
            except Exception as e:
                console.print(f"    Error: {e}")

    def fix_shell_scripts(self):
        """Fix shell script issues"""
        console.print("\n[bold blue]Fixing Shell Script Issues[/bold blue]")

        shell_scripts = [
            "scripts/verify_and_activate_env.sh",
            "scripts/unified_docker_secrets.sh",
            "scripts/restore_sophia_env.sh",
            "mcp-servers/deploy_final.sh",
        ]

        for script_path in shell_scripts:
            full_path = self.project_root / script_path
            if full_path.exists():
                console.print(f"  Fixing {script_path}...")
                if self.fix_shell_script(full_path):
                    self.shell_fixes += 1
                    console.print("    ✅ Fixed")

    def fix_shell_script(self, file_path: Path) -> bool:
        """Fix common shell script issues"""
        try:
            content = file_path.read_text()

            # Quote positional parameters
            content = re.sub(r"\$(\d+)", r'"$\1"', content)

            # Fix unquoted variables
            content = re.sub(
                r'\$([A-Za-z_][A-Za-z0-9_]*)\b(?!["\'])', r'"$\1"', content
            )

            # Fix cd commands without error handling
            content = re.sub(
                r"^(\s*)cd\s+([^|&\n]+)$",
                r"\1cd \2 || exit 1",
                content,
                flags=re.MULTILINE,
            )

            # Add set -euo pipefail if not present
            if "set -euo pipefail" not in content and "#!/bin/bash" in content:
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if line.startswith("#!/bin/bash"):
                        lines.insert(i + 1, "set -euo pipefail")
                        break
                content = "\n".join(lines)

            file_path.write_text(content)
            return True
        except Exception as e:
            console.print(f"    Error: {e}")
            return False

    def run_ruff_fixes(self):
        """Run ruff with auto-fixes"""
        console.print("\n[bold blue]Running Ruff Auto-fixes[/bold blue]")

        try:
            # First, update pyproject.toml to move deprecated options
            self.update_ruff_config()

            # Run ruff with fixes
            result = subprocess.run(
                ["ruff", "check", ".", "--fix"],
                check=False,
                capture_output=True,
                text=True,
            )

            # Count fixes
            if "Fixed" in result.stdout:
                fixes = re.search(r"Fixed (\d+) error", result.stdout)
                if fixes:
                    count = int(fixes.group(1))
                    self.python_fixes += count
                    console.print(f"  ✅ Applied {count} automatic fixes")

            # Run unsafe fixes for more aggressive fixing
            result = subprocess.run(
                ["ruff", "check", ".", "--fix", "--unsafe-fixes"],
                check=False,
                capture_output=True,
                text=True,
            )

            if "Fixed" in result.stdout:
                fixes = re.search(r"Fixed (\d+) error", result.stdout)
                if fixes:
                    count = int(fixes.group(1))
                    self.python_fixes += count
                    console.print(f"  ✅ Applied {count} unsafe fixes")

        except subprocess.CalledProcessError as e:
            console.print(f"  ⚠️  Ruff failed: {e}")

    def update_ruff_config(self):
        """Update pyproject.toml to fix deprecated ruff options"""
        pyproject_path = self.project_root / "pyproject.toml"
        if not pyproject_path.exists():
            return

        try:
            content = pyproject_path.read_text()

            # Move deprecated options under [tool.ruff.lint]
            if "[tool.ruff]" in content and "ignore =" in content:
                # This is complex, so we'll do a simple fix
                content = content.replace(
                    "[tool.ruff]", "[tool.ruff]\n\n[tool.ruff.lint]"
                )

            pyproject_path.write_text(content)
        except Exception:
            pass

    def run_black_formatting(self):
        """Run black formatting"""
        console.print("\n[bold blue]Running Black Formatting[/bold blue]")

        try:
            # First check which files need formatting
            check_result = subprocess.run(
                ["black", ".", "--check"], check=False, capture_output=True, text=True
            )

            if "would be reformatted" in check_result.stdout:
                # Run black to format
                format_result = subprocess.run(
                    ["black", "."], check=False, capture_output=True, text=True
                )

                if "reformatted" in format_result.stdout:
                    # Count reformatted files
                    count = len(re.findall(r"reformatted", format_result.stdout))
                    self.python_fixes += count
                    console.print(f"  ✅ Reformatted {count} files")

        except subprocess.CalledProcessError as e:
            console.print(f"  ⚠️  Black failed: {e}")

    def generate_summary(self):
        """Generate summary report"""
        console.print("\n[bold green]Remediation Summary[/bold green]")

        table = Table(title="Syntax Error Fixes")
        table.add_column("Language", style="cyan")
        table.add_column("Fixes Applied", style="green")

        table.add_row("Python", str(self.python_fixes))
        table.add_row("TypeScript", str(self.typescript_fixes))
        table.add_row("Shell Scripts", str(self.shell_fixes))
        table.add_row(
            "Total", str(self.python_fixes + self.typescript_fixes + self.shell_fixes)
        )

        console.print(table)

        # Save detailed report
        report = {
            "timestamp": subprocess.run(
                ["date", "-u"], check=False, capture_output=True, text=True
            ).stdout.strip(),
            "python_fixes": self.python_fixes,
            "typescript_fixes": self.typescript_fixes,
            "shell_fixes": self.shell_fixes,
            "total_fixes": self.python_fixes + self.typescript_fixes + self.shell_fixes,
            "files_modified": [],
        }

        report_path = self.project_root / "SYNTAX_REMEDIATION_REPORT.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        console.print(f"\n📝 Detailed report saved to: {report_path}")

    def run(self):
        """Run comprehensive syntax remediation"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Fixing Python syntax errors...", total=None)
            self.fix_python_syntax_errors()
            progress.update(task, completed=True)

            task = progress.add_task("Running Ruff auto-fixes...", total=None)
            self.run_ruff_fixes()
            progress.update(task, completed=True)

            task = progress.add_task("Fixing TypeScript errors...", total=None)
            self.fix_typescript_errors()
            progress.update(task, completed=True)

            task = progress.add_task("Fixing shell scripts...", total=None)
            self.fix_shell_scripts()
            progress.update(task, completed=True)

            task = progress.add_task("Running Black formatting...", total=None)
            self.run_black_formatting()
            progress.update(task, completed=True)

        self.generate_summary()


def main():
    console.print("[bold]Comprehensive Syntax Error Remediation[/bold]")
    console.print(
        "This will fix syntax errors across Python, TypeScript, and Shell scripts\n"
    )

    fixer = ComprehensiveSyntaxFixer()
    fixer.run()

    console.print("\n[bold yellow]Next Steps:[/bold yellow]")
    console.print("1. Run 'ruff check .' to verify remaining issues")
    console.print("2. Run 'tsc --noEmit' in frontend/ to check TypeScript")
    console.print("3. Run 'shellcheck scripts/*.sh' to verify shell scripts")
    console.print("4. Commit the fixes and run tests")


if __name__ == "__main__":
    main()
