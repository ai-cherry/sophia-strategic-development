#!/usr/bin/env python3
"""
Analyze Sample Data for Foundational Knowledge Schema Design
This script helps analyze real data exports to inform schema design
"""

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import pandas as pd


def analyze_csv_file(file_path: Path) -> dict[str, Any]:
    """Analyze a CSV file structure and content"""
    df = pd.read_csv(file_path)

    analysis = {
        "file_name": file_path.name,
        "row_count": len(df),
        "columns": list(df.columns),
        "data_types": df.dtypes.to_dict(),
        "null_counts": df.isnull().sum().to_dict(),
        "null_percentages": (df.isnull().sum() / len(df) * 100).round(2).to_dict(),
        "unique_counts": {col: df[col].nunique() for col in df.columns},
        "sample_data": df.head(3).to_dict("records"),
    }

    # Find potential ID fields
    potential_ids = []
    for col in df.columns:
        if "id" in col.lower() or "email" in col.lower():
            if df[col].nunique() == len(df):
                potential_ids.append(col)
    analysis["potential_id_fields"] = potential_ids

    # Find potential relationship fields
    potential_relationships = []
    for col in df.columns:
        if any(keyword in col.lower() for keyword in ["manager", "parent", "reports"]):
            potential_relationships.append(col)
    analysis["potential_relationships"] = potential_relationships

    return analysis


def analyze_json_file(file_path: Path) -> dict[str, Any]:
    """Analyze a JSON file structure"""
    with open(file_path) as f:
        data = json.load(f)

    analysis = {"file_name": file_path.name, "type": type(data).__name__}

    if isinstance(data, list):
        analysis["record_count"] = len(data)
        if data:
            # Analyze first record structure
            first_record = data[0]
            analysis["fields"] = (
                list(first_record.keys()) if isinstance(first_record, dict) else []
            )
            analysis["sample_data"] = data[:3]

            # Find common fields across all records
            if isinstance(first_record, dict):
                field_counts = defaultdict(int)
                for record in data:
                    for field in record:
                        field_counts[field] += 1

                analysis["field_consistency"] = {
                    field: f"{(count/len(data)*100):.1f}%"
                    for field, count in field_counts.items()
                }

    elif isinstance(data, dict):
        analysis["fields"] = list(data.keys())
        analysis["sample_data"] = dict(list(data.items())[:5])

    return analysis


def find_correlations(analyses: list[dict[str, Any]]) -> dict[str, Any]:
    """Find potential correlations between different data sources"""
    correlations = {
        "email_fields": {},
        "id_fields": {},
        "name_fields": {},
        "common_fields": [],
    }

    all_fields = defaultdict(list)

    for analysis in analyses:
        file_name = analysis["file_name"]
        fields = analysis.get("columns", analysis.get("fields", []))

        for field in fields:
            field_lower = field.lower()

            # Email fields
            if "email" in field_lower:
                correlations["email_fields"][file_name] = field

            # ID fields
            if "id" in field_lower and "email" not in field_lower:
                if file_name not in correlations["id_fields"]:
                    correlations["id_fields"][file_name] = []
                correlations["id_fields"][file_name].append(field)

            # Name fields
            if any(name in field_lower for name in ["name", "first", "last"]):
                if file_name not in correlations["name_fields"]:
                    correlations["name_fields"][file_name] = []
                correlations["name_fields"][file_name].append(field)

            all_fields[field].append(file_name)

    # Find fields that appear in multiple files
    for field, files in all_fields.items():
        if len(files) > 1:
            correlations["common_fields"].append({"field": field, "appears_in": files})

    return correlations


def generate_schema_suggestions(
    analyses: list[dict[str, Any]], correlations: dict[str, Any]
) -> str:
    """Generate SQL schema suggestions based on analysis"""
    suggestions = []

    suggestions.append("-- Suggested Schema Based on Data Analysis")
    suggestions.append("-- =====================================\n")

    # Employee table suggestion
    if any("employee" in a["file_name"].lower() for a in analyses):
        suggestions.append("-- EMPLOYEES Table (based on data patterns)")
        suggestions.append("CREATE TABLE EMPLOYEES (")
        suggestions.append(
            "    EMPLOYEE_ID VARCHAR(255) PRIMARY KEY DEFAULT UUID_STRING(),"
        )

        # Add email if found
        for file, field in correlations["email_fields"].items():
            if "employee" in file.lower():
                suggestions.append(
                    f"    EMAIL VARCHAR(255) UNIQUE NOT NULL, -- from {field}"
                )
                break

        # Add name fields if found
        for file, fields in correlations["name_fields"].items():
            if "employee" in file.lower():
                for field in fields:
                    if "first" in field.lower():
                        suggestions.append(
                            f"    FIRST_NAME VARCHAR(255), -- from {field}"
                        )
                    elif "last" in field.lower():
                        suggestions.append(
                            f"    LAST_NAME VARCHAR(255), -- from {field}"
                        )

        # Add ID fields for integration
        for file, fields in correlations["id_fields"].items():
            if "gong" in file.lower():
                suggestions.append(
                    f"    GONG_USER_ID VARCHAR(255), -- from {fields[0]}"
                )
            elif "slack" in file.lower():
                suggestions.append(
                    f"    SLACK_USER_ID VARCHAR(255), -- from {fields[0]}"
                )

        suggestions.append("    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        suggestions.append(");\n")

    return "\n".join(suggestions)


def main():
    """Main analysis function"""
    if len(sys.argv) < 2:
        sys.exit(1)

    data_dir = Path(sys.argv[1])
    if not data_dir.exists():
        sys.exit(1)

    analyses = []

    # Analyze all files
    for file_path in data_dir.iterdir():
        if file_path.suffix == ".csv":
            analysis = analyze_csv_file(file_path)
            analyses.append(analysis)

            # Show fields with high null rates
            high_nulls = [
                f"{col} ({pct}%)"
                for col, pct in analysis["null_percentages"].items()
                if pct > 50
            ]
            if high_nulls:
                pass

        elif file_path.suffix == ".json":
            analysis = analyze_json_file(file_path)
            analyses.append(analysis)

            if "record_count" in analysis:
                pass
            if "fields" in analysis:
                pass

    # Find correlations

    correlations = find_correlations(analyses)

    for _file, _field in correlations["email_fields"].items():
        pass

    for _file, _fields in correlations["id_fields"].items():
        pass

    for _common in correlations["common_fields"]:
        pass

    # Generate schema suggestions

    generate_schema_suggestions(analyses, correlations)

    # Save detailed analysis
    output_file = data_dir / "data_analysis_report.json"
    with open(output_file, "w") as f:
        json.dump(
            {
                "analyses": analyses,
                "correlations": correlations,
                "timestamp": pd.Timestamp.now().isoformat(),
            },
            f,
            indent=2,
            default=str,
        )


if __name__ == "__main__":
    main()
