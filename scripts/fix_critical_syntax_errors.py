#!/usr/bin/env python3
"""
Fix critical syntax errors in specific files
"""

import re
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()


class CriticalSyntaxFixer:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.fixes_applied = []

    def fix_file(self, file_path: str, fixes: list[tuple[str, str, str]]):
        """Apply fixes to a specific file"""
        full_path = self.project_root / file_path
        if not full_path.exists():
            console.print(f"[yellow]File not found: {file_path}[/yellow]")
            return

        try:
            content = full_path.read_text()
            original_content = content

            for pattern, replacement, description in fixes:
                if re.search(pattern, content, re.MULTILINE | re.DOTALL):
                    content = re.sub(
                        pattern, replacement, content, flags=re.MULTILINE | re.DOTALL
                    )
                    self.fixes_applied.append((file_path, description))
                    console.print(f"  ✅ {description}")

            if content != original_content:
                full_path.write_text(content)
                console.print(f"[green]Fixed: {file_path}[/green]")

        except Exception as e:
            console.print(f"[red]Error fixing {file_path}: {e}[/red]")

    def fix_all(self):
        """Fix all critical syntax errors"""
        console.print("[bold]Fixing Critical Syntax Errors[/bold]\n")

        # Fix tests/infrastructure/run_all_tests.py - unexpected indentation
        self.fix_file(
            "tests/infrastructure/run_all_tests.py",
            [
                (
                    r'cmd = \["pytest", str\(target\)\]\s*\n\s*# TODO: Validate input before subprocess execution\s*\n\s+subprocess\.run\(cmd, check=False\)',
                    'cmd = ["pytest", str(target)]\n    # TODO: Validate input before subprocess execution\n    subprocess.run(cmd, check=False)',
                    "Fixed indentation in run_all_tests.py",
                )
            ],
        )

        # Fix ui-ux-agent/mcp-servers/figma-dev-mode/figma_mcp_server.py - unexpected EOF
        self.fix_file(
            "ui-ux-agent/mcp-servers/figma-dev-mode/figma_mcp_server.py",
            [
                (
                    r"(uvicorn\.run\([^)]+)(\s*$)",
                    r"\1)",
                    "Fixed missing closing parenthesis in figma_mcp_server.py",
                )
            ],
        )

        # Fix unified_ai_assistant.py - multiple syntax errors
        self.fix_file(
            "unified_ai_assistant.py",
            [
                (
                    r"result = # TODO: Validate input before subprocess execution\s*\n\s*# TODO: Validate input before subprocess execution\s*\n\s*subprocess\.run\(",
                    "result = subprocess.run(",
                    "Fixed incomplete assignment in unified_ai_assistant.py",
                ),
                (
                    r"except Exception:\s*\n\s*return",
                    "except Exception:\n            return",
                    "Fixed indentation after except block",
                ),
                (
                    r"except Exception as e:\s*\n\s*return",
                    "except Exception as e:\n            return",
                    "Fixed indentation after except block with variable",
                ),
            ],
        )

        # Fix ui-ux-agent/mcp-servers/langchain-agents/ui_ux_agent.py - undefined get_config_value
        self.fix_file(
            "ui-ux-agent/mcp-servers/langchain-agents/ui_ux_agent.py",
            [
                (
                    r'OPENAI_API_KEY = get_config_value\("openai_api_key"\)',
                    'OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")',
                    "Fixed undefined get_config_value for OPENAI_API_KEY",
                ),
                (
                    r'OPENROUTER_API_KEY = get_config_value\("openrouter_api_key"\)',
                    'OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")',
                    "Fixed undefined get_config_value for OPENROUTER_API_KEY",
                ),
                (r"(import uvicorn\n)", r"import os\n\1", "Added missing os import"),
            ],
        )

        # Fix ui-ux-agent/start_ui_ux_agent_system.py - undefined get_config_value
        self.fix_file(
            "ui-ux-agent/start_ui_ux_agent_system.py",
            [
                (
                    r'figma_pat_available = bool\(\s*get_config_value\("figma_pat"\)',
                    'figma_pat_available = bool(\n            os.getenv("FIGMA_PAT")',
                    "Fixed undefined get_config_value in start_ui_ux_agent_system.py",
                )
            ],
        )

        # Fix api/ai_memory_health_routes.py - insecure random
        self.fix_file(
            "api/ai_memory_health_routes.py",
            [
                (
                    r"import random\n",
                    "import secrets\n",
                    "Replaced random with secrets import",
                ),
                (
                    r"random\.randint\((\d+),\s*(\d+)\)",
                    r"secrets.randbelow(\2 - \1 + 1) + \1",
                    "Replaced random.randint with secrets",
                ),
            ],
        )

        # Fix frontend TypeScript issue
        tsx_file = (
            self.project_root
            / "frontend/src/components/dashboard/tabs/AIMemoryHealthTab.tsx"
        )
        if tsx_file.exists():
            try:
                content = tsx_file.read_text()
                # Fix Target: <100ms being parsed as comparison
                content = content.replace("Target: <100ms", 'Target: {"<100ms"}')
                tsx_file.write_text(content)
                self.fixes_applied.append(
                    ("AIMemoryHealthTab.tsx", "Fixed <100ms comparison issue")
                )
                console.print("[green]Fixed: AIMemoryHealthTab.tsx[/green]")
            except Exception as e:
                console.print(f"[red]Error fixing TypeScript file: {e}[/red]")

        # Summary
        console.print("\n[bold]Summary[/bold]")
        table = Table(title="Fixes Applied")
        table.add_column("File", style="cyan")
        table.add_column("Fix", style="green")

        for file_path, description in self.fixes_applied:
            table.add_row(file_path, description)

        console.print(table)
        console.print(f"\nTotal fixes applied: {len(self.fixes_applied)}")


def main():
    fixer = CriticalSyntaxFixer()
    fixer.fix_all()


if __name__ == "__main__":
    main()
