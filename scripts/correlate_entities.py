#!/usr/bin/env python3
"""Correlate employees across different systems (HR, Gong, Slack)."""

import argparse
import json
import logging
from difflib import SequenceMatcher

import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmployeeCorrelator:
    """Correlate employees across multiple systems."""

    def __init__(self):
        self.employees = []
        self.gong_users = []
        self.slack_users = []
        self.correlations = []

    def load_employees_csv(self, file_path: str):
        """Load employees from CSV file."""
        df = pd.read_csv(file_path)
        logger.info(f"Loaded {len(df)} employees from CSV")

        # Normalize column names
        df.columns = [col.lower().replace(" ", "_") for col in df.columns]

        self.employees = df.to_dict("records")
        return len(self.employees)

    def load_gong_json(self, file_path: str):
        """Load Gong users from JSON export."""
        with open(file_path) as f:
            data = json.load(f)

        # Handle different JSON structures
        if isinstance(data, list):
            self.gong_users = data
        elif isinstance(data, dict) and "users" in data:
            self.gong_users = data["users"]
        else:
            self.gong_users = [data]

        logger.info(f"Loaded {len(self.gong_users)} Gong users")
        return len(self.gong_users)

    def load_slack_json(self, file_path: str):
        """Load Slack users from JSON export."""
        with open(file_path) as f:
            data = json.load(f)

        # Handle different JSON structures
        if isinstance(data, list):
            self.slack_users = data
        elif isinstance(data, dict) and "members" in data:
            self.slack_users = data["members"]
        else:
            self.slack_users = [data]

        # Filter out bots and deleted users
        self.slack_users = [
            u
            for u in self.slack_users
            if not u.get("is_bot", False) and not u.get("deleted", False)
        ]

        logger.info(f"Loaded {len(self.slack_users)} Slack users")
        return len(self.slack_users)

    def normalize_email(self, email: str) -> str:
        """Normalize email for comparison."""
        if not email:
            return ""
        return email.lower().strip()

    def extract_name_parts(self, full_name: str) -> tuple[str, str]:
        """Extract first and last name from full name."""
        if not full_name:
            return "", ""

        parts = full_name.strip().split()
        if len(parts) >= 2:
            return parts[0].lower(), parts[-1].lower()
        elif len(parts) == 1:
            return parts[0].lower(), ""
        return "", ""

    def name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two names."""
        if not name1 or not name2:
            return 0.0
        return SequenceMatcher(None, name1.lower(), name2.lower()).ratio()

    def correlate_by_email(self):
        """Correlate users by email address."""
        correlations = []

        for emp in self.employees:
            correlation = {
                "employee_email": self.normalize_email(emp.get("email", "")),
                "employee_name": emp.get("full_name", emp.get("name", "")),
                "gong_match": None,
                "slack_match": None,
                "confidence": "low",
            }

            emp_email = self.normalize_email(emp.get("email", ""))

            if emp_email:
                # Match with Gong
                for gong_user in self.gong_users:
                    gong_email = self.normalize_email(gong_user.get("email", ""))
                    if emp_email == gong_email:
                        correlation["gong_match"] = {
                            "id": gong_user.get("userId", gong_user.get("id", "")),
                            "email": gong_user.get("email", ""),
                            "name": gong_user.get("name", ""),
                        }
                        correlation["confidence"] = "high"
                        break

                # Match with Slack
                for slack_user in self.slack_users:
                    slack_profile = slack_user.get("profile", {})
                    slack_email = self.normalize_email(slack_profile.get("email", ""))

                    if emp_email == slack_email:
                        correlation["slack_match"] = {
                            "id": slack_user.get("id", ""),
                            "email": slack_profile.get("email", ""),
                            "name": slack_profile.get(
                                "real_name", slack_user.get("name", "")
                            ),
                        }
                        correlation["confidence"] = "high"
                        break

            correlations.append(correlation)

        return correlations

    def correlate_by_name(self, unmatched_only: bool = True):
        """Correlate users by name similarity for unmatched records."""

        for corr in self.correlations:
            # Skip if already matched (when unmatched_only is True)
            if unmatched_only and (corr["gong_match"] or corr["slack_match"]):
                continue

            emp_name = corr["employee_name"]
            if not emp_name:
                continue

            emp_first, emp_last = self.extract_name_parts(emp_name)

            # Try to match with Gong by name
            if not corr["gong_match"]:
                best_gong_match = None
                best_gong_score = 0.0

                for gong_user in self.gong_users:
                    gong_name = gong_user.get("name", "")
                    if gong_name:
                        score = self.name_similarity(emp_name, gong_name)
                        if score > best_gong_score and score > 0.8:  # 80% threshold
                            best_gong_score = score
                            best_gong_match = gong_user

                if best_gong_match:
                    corr["gong_match"] = {
                        "id": best_gong_match.get(
                            "userId", best_gong_match.get("id", "")
                        ),
                        "email": best_gong_match.get("email", ""),
                        "name": best_gong_match.get("name", ""),
                        "match_type": "name",
                        "score": best_gong_score,
                    }
                    corr["confidence"] = "medium"

            # Try to match with Slack by name
            if not corr["slack_match"]:
                best_slack_match = None
                best_slack_score = 0.0

                for slack_user in self.slack_users:
                    slack_profile = slack_user.get("profile", {})
                    slack_name = slack_profile.get(
                        "real_name", slack_user.get("name", "")
                    )

                    if slack_name:
                        score = self.name_similarity(emp_name, slack_name)
                        if score > best_slack_score and score > 0.8:  # 80% threshold
                            best_slack_score = score
                            best_slack_match = slack_user

                if best_slack_match:
                    slack_profile = best_slack_match.get("profile", {})
                    corr["slack_match"] = {
                        "id": best_slack_match.get("id", ""),
                        "email": slack_profile.get("email", ""),
                        "name": slack_profile.get(
                            "real_name", best_slack_match.get("name", "")
                        ),
                        "match_type": "name",
                        "score": best_slack_score,
                    }
                    corr["confidence"] = "medium"

        return self.correlations

    def generate_report(self):
        """Generate correlation report."""
        total = len(self.correlations)
        matched_gong = sum(1 for c in self.correlations if c["gong_match"])
        matched_slack = sum(1 for c in self.correlations if c["slack_match"])
        fully_matched = sum(
            1 for c in self.correlations if c["gong_match"] and c["slack_match"]
        )

        report = {
            "summary": {
                "total_employees": total,
                "gong_matched": matched_gong,
                "slack_matched": matched_slack,
                "fully_matched": fully_matched,
                "unmatched": total - max(matched_gong, matched_slack),
            },
            "correlations": self.correlations,
        }

        # Log summary
        logger.info("=== Correlation Summary ===")
        logger.info(f"Total employees: {total}")
        logger.info(
            f"Matched with Gong: {matched_gong} ({matched_gong/total*100:.1f}%)"
        )
        logger.info(
            f"Matched with Slack: {matched_slack} ({matched_slack/total*100:.1f}%)"
        )
        logger.info(f"Fully matched: {fully_matched} ({fully_matched/total*100:.1f}%)")

        return report

    def save_results(self, output_file: str):
        """Save correlation results to file."""
        report = self.generate_report()

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Results saved to {output_file}")

        # Also save a CSV for easy review
        csv_file = output_file.replace(".json", ".csv")
        rows = []

        for corr in self.correlations:
            row = {
                "employee_name": corr["employee_name"],
                "employee_email": corr["employee_email"],
                "gong_id": corr["gong_match"]["id"] if corr["gong_match"] else "",
                "gong_email": corr["gong_match"]["email"] if corr["gong_match"] else "",
                "slack_id": corr["slack_match"]["id"] if corr["slack_match"] else "",
                "slack_email": (
                    corr["slack_match"]["email"] if corr["slack_match"] else ""
                ),
                "confidence": corr["confidence"],
            }
            rows.append(row)

        df = pd.DataFrame(rows)
        df.to_csv(csv_file, index=False)
        logger.info(f"CSV results saved to {csv_file}")

    def run_correlation(self):
        """Run the full correlation process."""
        # First pass: correlate by email
        self.correlations = self.correlate_by_email()
        logger.info("Completed email-based correlation")

        # Second pass: correlate by name for unmatched
        self.correlate_by_name(unmatched_only=True)
        logger.info("Completed name-based correlation")

        return self.correlations

def main():
    """Main correlation function."""
    parser = argparse.ArgumentParser(description="Correlate employees across systems")
    parser.add_argument("--employees", required=True, help="Path to employees CSV file")
    parser.add_argument("--gong", required=True, help="Path to Gong users JSON file")
    parser.add_argument("--slack", required=True, help="Path to Slack users JSON file")
    parser.add_argument(
        "--output", default="employee_correlations.json", help="Output file"
    )

    args = parser.parse_args()

    # Create correlator
    correlator = EmployeeCorrelator()

    # Load data
    correlator.load_employees_csv(args.employees)
    correlator.load_gong_json(args.gong)
    correlator.load_slack_json(args.slack)

    # Run correlation
    correlator.run_correlation()

    # Save results
    correlator.save_results(args.output)

if __name__ == "__main__":
    main()
