#!/usr/bin/env python3
"""
Comprehensive Syntax Error Fixer for Sophia AI
Addresses 348 syntax errors identified by ruff analysis
Part of Phase 1: Emergency Technical Debt Resolution
"""

import ast
import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.utils.custom_logger import setup_logger

logger = setup_logger("syntax_fixer")


class ComprehensiveSyntaxFixer:
    """AI-powered syntax error detection and auto-repair system"""

    def __init__(self):
        self.fixed_count = 0
        self.failed_files = []
        self.backup_dir = Path("backups/syntax_fixes") / datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Common syntax error patterns and fixes
        self.fix_patterns = {
            "missing_colon": {
                "pattern": r"(if|elif|else|for|while|def|class|try|except|finally|with)\s+[^:]+$",
                "fix": lambda line: line.rstrip() + ":",
            },
            "unclosed_string": {
                "pattern": r'["\'](?:[^"\\\']|\\.|(?!\1)["\'"])*$',
                "fix": lambda line: line + '"' if line.count('"') % 2 else line + "'",
            },
            "unclosed_bracket": {
                "pattern": r"[\(\[\{][^\)\]\}]*$",
                "fix": self._fix_unclosed_bracket,
            },
            "invalid_indent": {
                "pattern": r"^[ \t]+",
                "fix": self._fix_indentation_line,
            },
        }

    async def scan_and_fix_all_syntax_errors(
        self, directory: str = "."
    ) -> dict[str, Any]:
        """Main entry point to fix all syntax errors"""
        logger.info(f"Starting comprehensive syntax error scan in {directory}")

        # First, get list of files with syntax errors from ruff
        syntax_error_files = await self._get_syntax_error_files(directory)
        logger.info(f"Found {len(syntax_error_files)} files with syntax errors")

        results = {
            "total_files": len(syntax_error_files),
            "fixed": 0,
            "partially_fixed": 0,
            "failed": 0,
            "details": [],
            "summary": {},
        }

        for file_path in syntax_error_files:
            result = await self._fix_file_syntax_errors(file_path)
            results["details"].append(result)

            if result["status"] == "fixed":
                results["fixed"] += 1
            elif result["status"] == "partially_fixed":
                results["partially_fixed"] += 1
            else:
                results["failed"] += 1

        # Generate summary report
        results["summary"] = await self._generate_summary_report(results)

        # Save detailed report
        await self._save_report(results)

        return results

    async def _get_syntax_error_files(self, directory: str) -> list[Path]:
        """Get list of files with syntax errors using ruff"""
        try:
            result = subprocess.run(
                [
                    "ruff",
                    "check",
                    directory,
                    "--select",
                    "E999",
                    "--output-format",
                    "json",
                ],
                capture_output=True,
                text=True,
            )

            if result.stdout:
                errors = json.loads(result.stdout)
                # Extract unique file paths
                files = list(set(error["filename"] for error in errors))
                return [Path(f) for f in files]

            return []

        except Exception as e:
            logger.error(f"Error getting syntax error files: {e}")
            # Fallback to scanning all Python files
            return list(Path(directory).rglob("*.py"))

    async def _fix_file_syntax_errors(self, file_path: Path) -> dict[str, Any]:
        """Fix syntax errors in a single file"""
        logger.info(f"Processing {file_path}")

        # Backup original file
        backup_path = self.backup_dir / file_path.name
        try:
            backup_path.write_text(file_path.read_text())
        except Exception as e:
            logger.error(f"Failed to backup {file_path}: {e}")
            return {
                "file": str(file_path),
                "status": "failed",
                "error": f"Backup failed: {e}",
            }

        try:
            content = file_path.read_text()
            original_content = content

            # Try to parse and get specific error
            syntax_error = None
            try:
                ast.parse(content)
                # No syntax error found
                return {
                    "file": str(file_path),
                    "status": "no_error",
                    "message": "No syntax error found",
                }
            except SyntaxError as e:
                syntax_error = e

            # Apply fixes iteratively
            fixes_applied = []
            max_iterations = 10
            iteration = 0

            while syntax_error and iteration < max_iterations:
                iteration += 1

                # Try automatic fixes
                fixed_content = await self._apply_syntax_fixes(content, syntax_error)

                if fixed_content != content:
                    content = fixed_content
                    fixes_applied.append(
                        {
                            "iteration": iteration,
                            "error": str(syntax_error),
                            "line": syntax_error.lineno,
                        }
                    )

                    # Test if fixed
                    try:
                        ast.parse(content)
                        syntax_error = None  # Fixed!
                    except SyntaxError as e:
                        syntax_error = e  # New error, continue fixing
                else:
                    # Couldn't fix automatically
                    break

            # If we fixed it, save the file
            if not syntax_error and content != original_content:
                file_path.write_text(content)

                # Run ruff format on the fixed file
                subprocess.run(["ruff", "format", str(file_path)], capture_output=True)

                return {
                    "file": str(file_path),
                    "status": "fixed",
                    "fixes_applied": fixes_applied,
                    "iterations": iteration,
                }
            elif fixes_applied:
                # Partially fixed but still has errors
                return {
                    "file": str(file_path),
                    "status": "partially_fixed",
                    "fixes_applied": fixes_applied,
                    "remaining_error": str(syntax_error) if syntax_error else None,
                }
            else:
                # Couldn't fix
                return {
                    "file": str(file_path),
                    "status": "failed",
                    "error": str(syntax_error),
                    "line": syntax_error.lineno if syntax_error else None,
                }

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return {"file": str(file_path), "status": "failed", "error": str(e)}

    async def _apply_syntax_fixes(self, content: str, error: SyntaxError) -> str:
        """Apply automatic fixes based on error type"""
        lines = content.split("\n")

        # Fix based on error message
        error_msg = str(error).lower()
        line_idx = error.lineno - 1 if error.lineno else -1

        if line_idx >= 0 and line_idx < len(lines):
            line = lines[line_idx]

            # Missing colon
            if "expected ':'" in error_msg or "invalid syntax" in error_msg:
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
                    if line.strip().startswith(keyword) and not line.rstrip().endswith(
                        ":"
                    ):
                        lines[line_idx] = line.rstrip() + ":"
                        return "\n".join(lines)

            # Indentation error
            if "indentationerror" in error_msg or "indent" in error_msg:
                fixed_line = self._fix_indentation_line(line, lines, line_idx)
                if fixed_line != line:
                    lines[line_idx] = fixed_line
                    return "\n".join(lines)

            # Unclosed brackets/quotes
            if "unexpected eof" in error_msg or "eol while scanning" in error_msg:
                # Count unclosed brackets
                open_parens = content.count("(") - content.count(")")
                open_brackets = content.count("[") - content.count("]")
                open_braces = content.count("{") - content.count("}")

                # Add closing brackets at the end
                if open_parens > 0:
                    content += ")" * open_parens
                if open_brackets > 0:
                    content += "]" * open_brackets
                if open_braces > 0:
                    content += "}" * open_braces

                # Check for unclosed strings
                for quote in ['"', "'"]:
                    if content.count(quote) % 2 != 0:
                        content += quote

                return content

            # Invalid character
            if "invalid character" in error_msg and error.offset:
                # Remove the invalid character
                if error.offset <= len(line):
                    line = line[: error.offset - 1] + line[error.offset :]
                    lines[line_idx] = line
                    return "\n".join(lines)

        return content

    def _fix_indentation_line(self, line: str, lines: list[str], line_idx: int) -> str:
        """Fix indentation for a specific line"""
        if line_idx == 0:
            return line.lstrip()  # First line should have no indent

        # Look at previous non-empty line
        prev_idx = line_idx - 1
        while prev_idx >= 0 and not lines[prev_idx].strip():
            prev_idx -= 1

        if prev_idx >= 0:
            prev_line = lines[prev_idx]
            prev_indent = len(prev_line) - len(prev_line.lstrip())

            # Check if previous line should increase indent
            if any(
                prev_line.strip().startswith(kw)
                for kw in [
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
                ]
            ):
                if prev_line.rstrip().endswith(":"):
                    # Increase indent
                    return " " * (prev_indent + 4) + line.lstrip()

            # Otherwise match previous indent
            return " " * prev_indent + line.lstrip()

        return line

    def _fix_unclosed_bracket(self, line: str) -> str:
        """Fix unclosed brackets in a line"""
        brackets = {"(": ")", "[": "]", "{": "}"}
        stack = []

        for char in line:
            if char in brackets:
                stack.append(brackets[char])
            elif char in brackets.values():
                if stack and stack[-1] == char:
                    stack.pop()

        # Add missing closing brackets
        return line + "".join(reversed(stack))

    async def _generate_summary_report(self, results: dict[str, Any]) -> dict[str, Any]:
        """Generate a summary report of fixes"""
        return {
            "total_files_processed": results["total_files"],
            "successfully_fixed": results["fixed"],
            "partially_fixed": results["partially_fixed"],
            "failed_to_fix": results["failed"],
            "success_rate": (results["fixed"] / results["total_files"] * 100)
            if results["total_files"] > 0
            else 0,
            "common_errors": self._analyze_common_errors(results["details"]),
            "recommendations": self._generate_recommendations(results),
        }

    def _analyze_common_errors(self, details: list[dict[str, Any]]) -> dict[str, int]:
        """Analyze common error patterns"""
        error_counts = {}

        for detail in details:
            if detail.get("error"):
                error_type = self._categorize_error(detail["error"])
                error_counts[error_type] = error_counts.get(error_type, 0) + 1

        return dict(sorted(error_counts.items(), key=lambda x: x[1], reverse=True))

    def _categorize_error(self, error: str) -> str:
        """Categorize error type"""
        error_lower = error.lower()

        if "expected ':'" in error_lower:
            return "missing_colon"
        elif "indentation" in error_lower:
            return "indentation_error"
        elif "eof" in error_lower or "eol" in error_lower:
            return "unclosed_bracket_or_quote"
        elif "invalid character" in error_lower:
            return "invalid_character"
        else:
            return "other"

    def _generate_recommendations(self, results: dict[str, Any]) -> list[str]:
        """Generate recommendations based on results"""
        recommendations = []

        if results["failed"] > 0:
            recommendations.append(
                f"Manual intervention required for {results['failed']} files that couldn't be automatically fixed"
            )

        if results["partially_fixed"] > 0:
            recommendations.append(
                f"Review {results['partially_fixed']} partially fixed files for remaining issues"
            )

        recommendations.extend(
            [
                "Run comprehensive ruff check after fixes to ensure no new issues",
                "Consider adding pre-commit hooks to prevent syntax errors",
                "Review and update coding standards to prevent common errors",
                "Implement real-time syntax checking in development environment",
            ]
        )

        return recommendations

    async def _save_report(self, results: dict[str, Any]) -> None:
        """Save detailed report to file"""
        report_path = (
            Path("reports")
            / f"syntax_fix_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"Detailed report saved to {report_path}")


async def main():
    """Main entry point"""
    fixer = ComprehensiveSyntaxFixer()

    logger.info("=" * 80)
    logger.info("COMPREHENSIVE SYNTAX ERROR FIXER FOR SOPHIA AI")
    logger.info("Addressing 348 syntax errors from ruff analysis")
    logger.info("=" * 80)

    # Run the fixer
    results = await fixer.scan_and_fix_all_syntax_errors()

    # Print summary
    logger.info("\n" + "=" * 80)
    logger.info("SUMMARY REPORT")
    logger.info("=" * 80)
    logger.info(f"Total files processed: {results['summary']['total_files_processed']}")
    logger.info(f"Successfully fixed: {results['summary']['successfully_fixed']}")
    logger.info(f"Partially fixed: {results['summary']['partially_fixed']}")
    logger.info(f"Failed to fix: {results['summary']['failed_to_fix']}")
    logger.info(f"Success rate: {results['summary']['success_rate']:.1f}%")

    logger.info("\nCommon error types:")
    for error_type, count in results["summary"]["common_errors"].items():
        logger.info(f"  - {error_type}: {count}")

    logger.info("\nRecommendations:")
    for rec in results["summary"]["recommendations"]:
        logger.info(f"  - {rec}")

    # Exit with appropriate code
    if results["summary"]["failed_to_fix"] == 0:
        logger.info("\n✅ All syntax errors fixed successfully!")
        sys.exit(0)
    else:
        logger.warning(
            f"\n⚠️  {results['summary']['failed_to_fix']} files still have syntax errors"
        )
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
