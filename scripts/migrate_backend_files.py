import json
import os
import shutil
import subprocess


class BackendMigrator:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.migration_log = []

    def load_migration_map(self):
        """Load the file migration mapping"""
        with open("config/file_migrations.json") as f:
            return json.load(f)

    def load_service_split(self):
        """Load service split decisions"""
        service_split = {}

        # Read the service split report
        if os.path.exists("reports/service_split_report.txt"):
            with open("reports/service_split_report.txt") as f:
                content = f.read()

            # Parse core services
            if "Core Services" in content:
                core_section = content.split("Core Services")[1].split(
                    "Infrastructure Services"
                )[0]
                for line in core_section.split("\n"):
                    if "backend/services/" in line:
                        service_path = line.strip().replace("- ", "").strip()
                        service_split[service_path] = "core"

            # Parse infrastructure services
            if "Infrastructure Services" in content:
                infra_section = content.split("Infrastructure Services")[1].split(
                    "Manual Review"
                )[0]
                for line in infra_section.split("\n"):
                    if "backend/services/" in line:
                        service_path = line.strip().replace("- ", "").strip()
                        service_split[service_path] = "infrastructure"

        return service_split

    def get_service_destination(self, file_path, service_split):
        """Determine correct destination for service files"""
        if file_path in service_split:
            if service_split[file_path] == "infrastructure":
                return file_path.replace(
                    "backend/services/", "infrastructure/services/"
                )
            else:
                return file_path.replace("backend/services/", "core/services/")

        # Default to core for services not in the split
        return file_path.replace("backend/services/", "core/services/")

    def migrate_file(self, old_path, new_path):
        """Migrate a single file using git mv to preserve history"""
        if not os.path.exists(old_path):
            self.migration_log.append(f"SKIP: {old_path} does not exist")
            return False

        # Create target directory
        new_dir = os.path.dirname(new_path)
        if not self.dry_run:
            os.makedirs(new_dir, exist_ok=True)

        # Use git mv to preserve history
        if self.dry_run:
            self.migration_log.append(f"WOULD MOVE: {old_path} -> {new_path}")
        else:
            try:
                subprocess.run(["git", "mv", old_path, new_path], check=True)
                self.migration_log.append(f"MOVED: {old_path} -> {new_path}")
                return True
            except subprocess.CalledProcessError as e:
                # Try regular move if git mv fails
                try:
                    shutil.move(old_path, new_path)
                    self.migration_log.append(
                        f"MOVED (non-git): {old_path} -> {new_path}"
                    )
                    return True
                except Exception as e2:
                    self.migration_log.append(
                        f"ERROR: Failed to move {old_path}: {e} / {e2}"
                    )
                    return False

    def run_migration(self):
        """Execute the full migration"""
        migrations = self.load_migration_map()
        service_split = self.load_service_split()

        # Adjust migrations based on service split
        adjusted_migrations = []
        for migration in migrations:
            old_path = migration["old"]
            new_path = migration["new"]

            # Special handling for service files
            if "backend/services/" in old_path and old_path.endswith(".py"):
                new_path = self.get_service_destination(old_path, service_split)
                migration["new"] = new_path

            adjusted_migrations.append(migration)

        # Phase 1: Move files
        for migration in adjusted_migrations:
            self.migrate_file(migration["old"], migration["new"])

        # Save migration log
        with open("reports/migration_log.txt", "w") as f:
            f.write("\n".join(self.migration_log))

        # Summary
        len([log for log in self.migration_log if "MOVED:" in log])
        len([log for log in self.migration_log if "SKIP:" in log])
        len([log for log in self.migration_log if "ERROR:" in log])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--execute", action="store_true", help="Execute migration (default is dry run)"
    )
    args = parser.parse_args()

    migrator = BackendMigrator(dry_run=not args.execute)
    migrator.run_migration()
