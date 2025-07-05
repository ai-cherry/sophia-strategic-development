#!/usr/bin/env python3
"""
Simple Syntax Error Fixer for Sophia AI
Addresses 348 syntax errors identified by ruff analysis
"""

import ast
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


class SimpleSyntaxFixer:
    """Simple syntax error detection and auto-repair"""

    def __init__(self):
        self.backup_dir = Path("backups/syntax_fixes") / datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def get_syntax_error_files(self) -> list[Path]:
        """Get list of files with syntax errors using ruff"""
        print("🔍 Scanning for syntax errors...")

        result = subprocess.run(
            ["ruff", "check", ".", "--select", "E999"], capture_output=True, text=True
        )

        if result.stdout:
            # Parse the output to find files with syntax errors
            files = []
            for line in result.stdout.strip().split("\n"):
                if line and ":" in line:
                    file_path = line.split(":")[0]
                    if file_path not in [str(f) for f in files]:
                        files.append(Path(file_path))

            print(f"📊 Found {len(files)} files with syntax errors")
            return files

        print("✅ No syntax errors found!")
        return []

    def fix_file(self, file_path: Path) -> dict[str, Any]:
        """Try to fix syntax errors in a single file"""
        print(f"\n📄 Processing: {file_path}")

        # Backup the file
        backup_path = self.backup_dir / file_path.name
        try:
            content = file_path.read_text()
            backup_path.write_text(content)
        except Exception as e:
            print(f"❌ Failed to backup {file_path}: {e}")
            return {"file": str(file_path), "status": "failed", "error": str(e)}

        # Try to parse and identify the error
        try:
            ast.parse(content)
            print(f"✅ No syntax error in {file_path}")
            return {"file": str(file_path), "status": "no_error"}
        except SyntaxError as e:
            print(f"   Error: {e.msg} at line {e.lineno}")

            # Try some simple fixes
            fixed = False
            lines = content.split("\n")

            if e.lineno and e.lineno <= len(lines):
                line_idx = e.lineno - 1
                line = lines[line_idx]

                # Fix missing colons
                if "expected ':'" in str(e).lower():
                    for keyword in [
                        "if",
                        "elif",
                        "else",
                        "for",
                        "while",
                        "def",
                        "class",
                        "try",
                        "except",
                        "finally",
                        "with",
                    ]:
                        if line.strip().startswith(
                            keyword
                        ) and not line.rstrip().endswith(":"):
                            lines[line_idx] = line.rstrip() + ":"
                            fixed = True
                            print(f"   ✅ Added missing colon at line {e.lineno}")
                            break

                # Fix unclosed brackets/quotes at end of file
                elif "unexpected EOF" in str(e) or "EOL while scanning" in str(e):
                    # Count unclosed brackets
                    open_parens = content.count("(") - content.count(")")
                    open_brackets = content.count("[") - content.count("]")
                    open_braces = content.count("{") - content.count("}")

                    additions = []
                    if open_parens > 0:
                        additions.extend([")"] * open_parens)
                    if open_brackets > 0:
                        additions.extend(["]"] * open_brackets)
                    if open_braces > 0:
                        additions.extend(["}"] * open_braces)

                    if additions:
                        content = content + "".join(additions)
                        fixed = True
                        print(f"   ✅ Added missing brackets: {''.join(additions)}")

                    # Check for unclosed strings
                    for quote in ['"', "'"]:
                        if content.count(quote) % 2 != 0:
                            content += quote
                            fixed = True
                            print(f"   ✅ Added missing quote: {quote}")

            if fixed:
                # Write the fixed content
                new_content = (
                    "\n".join(lines) if not fixed or "EOF" not in str(e) else content
                )
                file_path.write_text(new_content)

                # Verify the fix
                try:
                    ast.parse(new_content)
                    print(f"   ✅ Successfully fixed {file_path}")
                    return {"file": str(file_path), "status": "fixed"}
                except SyntaxError as e2:
                    print(f"   ⚠️  Still has error after fix: {e2.msg}")
                    return {
                        "file": str(file_path),
                        "status": "partially_fixed",
                        "remaining_error": str(e2),
                    }
            else:
                print("   ❌ Could not automatically fix this error")
                return {"file": str(file_path), "status": "failed", "error": str(e)}

    def run(self):
        """Main entry point"""
        print("=" * 80)
        print("🚀 SIMPLE SYNTAX ERROR FIXER FOR SOPHIA AI")
        print("=" * 80)

        # Get files with syntax errors
        error_files = self.get_syntax_error_files()

        if not error_files:
            return

        # Process each file
        results = {"fixed": 0, "partially_fixed": 0, "failed": 0, "no_error": 0}

        for file_path in error_files:
            result = self.fix_file(file_path)
            results[result["status"]] = results.get(result["status"], 0) + 1

        # Print summary
        print("\n" + "=" * 80)
        print("📊 SUMMARY")
        print("=" * 80)
        print(f"Total files processed: {len(error_files)}")
        print(f"✅ Successfully fixed: {results['fixed']}")
        print(f"⚠️  Partially fixed: {results['partially_fixed']}")
        print(f"❌ Failed to fix: {results['failed']}")
        print(f"ℹ️  No error found: {results['no_error']}")

        if results["fixed"] > 0:
            print(
                f"\n✅ Fixed {results['fixed']} files! Run ruff again to check remaining issues."
            )

        if results["failed"] > 0:
            print(f"\n⚠️  {results['failed']} files need manual intervention.")


if __name__ == "__main__":
    fixer = SimpleSyntaxFixer()
    fixer.run()
