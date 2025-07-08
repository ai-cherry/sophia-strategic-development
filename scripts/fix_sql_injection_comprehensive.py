#!/usr/bin/env python3
"""
Comprehensive SQL injection fix script
Fixes SQL injection vulnerabilities by using parameterized queries
"""

import re
from pathlib import Path


class SQLInjectionFixer:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.fixed_count = 0

    def find_sql_files(self) -> list[Path]:
        """Find Python files that might contain SQL"""
        sql_files = []

        # Common patterns that indicate SQL usage
        sql_patterns = [
            "*snowflake*.py",
            "*sql*.py",
            "*database*.py",
            "*query*.py",
            "*etl*.py",
            "*gong*.py",
            "*hubspot*.py",
        ]

        for pattern in sql_patterns:
            sql_files.extend(self.project_root.rglob(pattern))

        # Filter out dead_code and .venv
        sql_files = [
            f for f in sql_files if "dead_code" not in str(f) and ".venv" not in str(f)
        ]

        return sql_files

    def fix_sql_injection(self, file_path: Path) -> bool:
        """Fix SQL injection vulnerabilities in a file"""
        try:
            content = file_path.read_text()
            original_content = content

            # Pattern 1: f-string SQL queries
            # Convert f"SELECT * FROM {table}" to parameterized queries
            pattern1 = r'(execute|query)\s*\(\s*f["\']([^"\']*\{[^}]+\}[^"\']*)["\']'

            def replace_fstring_sql(match):
                method = match.group(1)
                query = match.group(2)

                # Extract variables from f-string
                variables = re.findall(r"\{([^}]+)\}", query)

                # Replace {var} with %s
                new_query = query
                for var in variables:
                    new_query = new_query.replace(f"{{{var}}}", "%s")

                # Build the new call
                var_list = ", ".join(variables)
                return f'{method}("{new_query}", ({var_list},))'

            content = re.sub(pattern1, replace_fstring_sql, content)

            # Pattern 2: String formatting with %
            # Convert "SELECT * FROM %s" % table to proper parameterized
            pattern2 = r'(execute|query)\s*\(\s*["\']([^"\']*%s[^"\']*)["\'][\s\n]*%[\s\n]*\(([^)]+)\)'

            def replace_percent_sql(match):
                method = match.group(1)
                query = match.group(2)
                params = match.group(3)
                return f'{method}("{query}", ({params}))'

            content = re.sub(pattern2, replace_percent_sql, content)

            # Pattern 3: String concatenation
            # Convert "SELECT * FROM " + table to parameterized
            pattern3 = (
                r'(execute|query)\s*\(\s*["\']([^"\']+)["\'][\s\n]*\+[\s\n]*([^,\)]+)'
            )

            def replace_concat_sql(match):
                method = match.group(1)
                query_part = match.group(2)
                var_part = match.group(3).strip()

                # Simple case: just appending a variable
                if query_part.endswith(" "):
                    new_query = query_part.rstrip() + " %s"
                    return f'{method}("{new_query}", ({var_part},))'
                else:
                    # Keep original if complex
                    return match.group(0)

            content = re.sub(pattern3, replace_concat_sql, content)

            # Pattern 4: .format() SQL queries
            # Convert "SELECT * FROM {}".format(table) to parameterized
            pattern4 = r'(execute|query)\s*\(\s*["\']([^"\']*\{\}[^"\']*)["\']\.format\s*\(([^)]+)\)'

            def replace_format_sql(match):
                method = match.group(1)
                query = match.group(2)
                params = match.group(3)

                # Replace {} with %s
                new_query = query.replace("{}", "%s")
                return f'{method}("{new_query}", ({params}))'

            content = re.sub(pattern4, replace_format_sql, content)

            # Add comment about SQL injection fix
            if content != original_content:
                # Add import if needed
                if "from typing import" not in content:
                    content = "from typing import Any, Tuple\n\n" + content

                # Add comment at the top of the file
                if "# SQL injection fixes applied" not in content:
                    lines = content.split("\n")
                    # Find the first non-comment, non-import line
                    insert_pos = 0
                    for i, line in enumerate(lines):
                        if (
                            line.strip()
                            and not line.startswith("#")
                            and not line.startswith("import")
                            and not line.startswith("from")
                        ):
                            insert_pos = i
                            break

                    lines.insert(
                        insert_pos,
                        "# SQL injection fixes applied - using parameterized queries",
                    )
                    content = "\n".join(lines)

                file_path.write_text(content)
                return True

        except Exception as e:
            print(f"Error fixing {file_path}: {e}")

        return False

    def run(self):
        """Run the SQL injection fix"""
        print("🔍 Finding files with potential SQL injection vulnerabilities...")

        sql_files = self.find_sql_files()
        print(f"Found {len(sql_files)} files to check")

        for file_path in sql_files:
            if self.fix_sql_injection(file_path):
                self.fixed_count += 1
                print(
                    f"✅ Fixed SQL injection in {file_path.relative_to(self.project_root)}"
                )

        print(f"\n✅ Fixed {self.fixed_count} files")

        # Also fix specific known files
        known_vulnerable_files = [
            "shared/utils/snowflake_gong_connector.py",
            "shared/utils/snowflake_hubspot_connector.py",
            "shared/utils/snowflake_estuary_connector.py",
            "infrastructure/etl/gong/ingest_gong_data.py",
            "infrastructure/core/snowflake_abstraction.py",
        ]

        print("\n🔧 Fixing known vulnerable files...")
        for file_path in known_vulnerable_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                if self.fix_sql_injection(full_path):
                    print(f"✅ Fixed {file_path}")
                else:
                    print(f"⚠️  No changes needed in {file_path}")
            else:
                print(f"❌ File not found: {file_path}")


def main():
    fixer = SQLInjectionFixer()
    fixer.run()


if __name__ == "__main__":
    main()
