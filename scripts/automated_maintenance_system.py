#!/usr/bin/env python3
"""
Automated Maintenance System for Sophia AI Platform
Comprehensive automation for updates, maintenance, and improvements
"""

import argparse
import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class MaintenanceSystem:
    """Comprehensive automated maintenance system"""

    def __init__(self, config_file: str = "maintenance_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.setup_logging()

    def setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler("maintenance.log"), logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)

    def load_config(self) -> dict:
        """Load maintenance configuration"""
        default_config = {
            "schedules": {
                "health_check": {"interval_minutes": 15},
                "performance_check": {"interval_minutes": 60},
                "security_scan": {"interval_hours": 24},
                "backup": {"interval_hours": 6},
                "update_check": {"interval_hours": 12},
                "cleanup": {"interval_hours": 168},  # Weekly
            },
            "thresholds": {
                "cpu_warning": 80,
                "memory_warning": 85,
                "disk_warning": 90,
                "response_time_warning": 500,
                "error_rate_warning": 5,
            },
            "notifications": {
                "slack_webhook": None,
                "email_enabled": False,
                "github_issues": True,
            },
            "maintenance_windows": {
                "daily_start": "02:00",
                "daily_end": "04:00",
                "timezone": "UTC",
            },
        }

        try:
            if Path(self.config_file).exists():
                with open(self.config_file) as f:
                    config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            else:
                self.save_config(default_config)
                return default_config
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            return default_config

    def save_config(self, config: dict):
        """Save maintenance configuration"""
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")

    def run_command(self, command: list[str], timeout: int = 300) -> tuple[bool, str]:
        """Run system command with timeout"""
        try:
            result = subprocess.run(
                command, capture_output=True, text=True, timeout=timeout
            )
            return result.returncode == 0, result.stdout.strip()
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)

    def check_system_health(self) -> dict:
        """Comprehensive system health check"""
        self.logger.info("🔍 Running system health check...")

        health_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "healthy",
            "components": {},
        }

        # Check Docker Swarm
        success, output = self.run_command(["docker", "node", "ls"])
        health_report["components"]["docker_swarm"] = {
            "status": "healthy" if success and "Ready" in output else "unhealthy",
            "details": output if success else "Failed to check Docker Swarm",
        }

        # Check services
        success, output = self.run_command(
            ["docker", "service", "ls", "--format", "json"]
        )
        if success:
            services = []
            healthy_services = 0
            for line in output.split("\n"):
                if line.strip():
                    try:
                        service = json.loads(line)
                        services.append(service)
                        replicas = service.get("Replicas", "0/0")
                        if "/" in replicas:
                            current, desired = replicas.split("/")
                            if current == desired and current != "0":
                                healthy_services += 1
                    except json.JSONDecodeError:
                        continue

            health_report["components"]["services"] = {
                "status": "healthy"
                if healthy_services > len(services) * 0.8
                else "degraded",
                "healthy_count": healthy_services,
                "total_count": len(services),
                "details": f"{healthy_services}/{len(services)} services healthy",
            }

        # Check system resources
        success, output = self.run_command(["free", "-m"])
        if success:
            lines = output.split("\n")
            if len(lines) > 1:
                mem_line = lines[1].split()
                if len(mem_line) >= 3:
                    total = int(mem_line[1])
                    used = int(mem_line[2])
                    usage_percent = (used / total) * 100

                    health_report["components"]["memory"] = {
                        "status": "healthy"
                        if usage_percent < self.config["thresholds"]["memory_warning"]
                        else "warning",
                        "usage_percent": round(usage_percent, 1),
                        "details": f"{used}MB/{total}MB used",
                    }

        # Check disk usage
        success, output = self.run_command(["df", "-h", "/"])
        if success:
            lines = output.split("\n")
            if len(lines) > 1:
                disk_line = lines[1].split()
                if len(disk_line) >= 5:
                    usage_str = disk_line[4].rstrip("%")
                    usage_percent = int(usage_str)

                    health_report["components"]["disk"] = {
                        "status": "healthy"
                        if usage_percent < self.config["thresholds"]["disk_warning"]
                        else "warning",
                        "usage_percent": usage_percent,
                        "details": f"{disk_line[2]} used of {disk_line[1]}",
                    }

        # Determine overall status
        component_statuses = [
            comp.get("status", "unknown")
            for comp in health_report["components"].values()
        ]
        if any(status == "unhealthy" for status in component_statuses):
            health_report["overall_status"] = "unhealthy"
        elif any(status == "warning" for status in component_statuses):
            health_report["overall_status"] = "warning"

        return health_report

    def run_security_scan(self) -> dict:
        """Run comprehensive security scan"""
        self.logger.info("🔒 Running security scan...")

        security_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "scan_type": "comprehensive",
            "findings": [],
        }

        # Check for vulnerable packages
        success, output = self.run_command(
            ["pip", "list", "--outdated", "--format=json"]
        )
        if success:
            try:
                outdated = json.loads(output)
                if outdated:
                    security_report["findings"].append(
                        {
                            "type": "outdated_packages",
                            "severity": "medium",
                            "count": len(outdated),
                            "details": f"{len(outdated)} packages need updates",
                        }
                    )
            except json.JSONDecodeError:
                pass

        # Check Docker security
        success, output = self.run_command(["docker", "secret", "ls"])
        if success:
            secret_count = len(output.split("\n")) - 1  # Subtract header
            if secret_count < 10:
                security_report["findings"].append(
                    {
                        "type": "insufficient_secrets",
                        "severity": "high",
                        "details": f"Only {secret_count} Docker secrets configured",
                    }
                )

        # Check for exposed ports
        success, output = self.run_command(["netstat", "-tuln"])
        if success:
            listening_ports = []
            for line in output.split("\n"):
                if "LISTEN" in line and "0.0.0.0:" in line:
                    port = line.split("0.0.0.0:")[1].split()[0]
                    listening_ports.append(port)

            # Common dangerous ports
            dangerous_ports = ["22", "23", "25", "53", "80", "443", "993", "995"]
            exposed_dangerous = [p for p in listening_ports if p in dangerous_ports]

            if exposed_dangerous:
                security_report["findings"].append(
                    {
                        "type": "exposed_ports",
                        "severity": "medium",
                        "ports": exposed_dangerous,
                        "details": f"Potentially dangerous ports exposed: {', '.join(exposed_dangerous)}",
                    }
                )

        return security_report

    def run_performance_optimization(self) -> dict:
        """Run performance optimization tasks"""
        self.logger.info("⚡ Running performance optimization...")

        optimization_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "optimizations_applied": [],
        }

        # Clean Docker system
        success, output = self.run_command(["docker", "system", "prune", "-f"])
        if success:
            optimization_report["optimizations_applied"].append(
                {
                    "type": "docker_cleanup",
                    "details": "Cleaned unused Docker resources",
                    "output": output,
                }
            )

        # Clean package cache
        success, output = self.run_command(["pip", "cache", "purge"])
        if success:
            optimization_report["optimizations_applied"].append(
                {
                    "type": "pip_cache_cleanup",
                    "details": "Cleaned pip cache",
                    "output": output,
                }
            )

        # Restart unhealthy services
        success, output = self.run_command(
            ["docker", "service", "ls", "--format", "json"]
        )
        if success:
            for line in output.split("\n"):
                if line.strip():
                    try:
                        service = json.loads(line)
                        replicas = service.get("Replicas", "0/0")
                        if "/" in replicas:
                            current, desired = replicas.split("/")
                            if current != desired or current == "0":
                                service_name = service.get("Name", "")
                                self.logger.info(
                                    f"Restarting unhealthy service: {service_name}"
                                )
                                restart_success, restart_output = self.run_command(
                                    [
                                        "docker",
                                        "service",
                                        "update",
                                        "--force",
                                        service_name,
                                    ]
                                )
                                if restart_success:
                                    optimization_report["optimizations_applied"].append(
                                        {
                                            "type": "service_restart",
                                            "service": service_name,
                                            "details": "Restarted unhealthy service",
                                        }
                                    )
                    except json.JSONDecodeError:
                        continue

        return optimization_report

    def run_backup(self) -> dict:
        """Run comprehensive backup"""
        self.logger.info("💾 Running backup...")

        backup_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "backup_type": "automated",
            "items_backed_up": [],
        }

        backup_dir = Path(
            f"backups/automated_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Backup configuration files
        config_files = [
            "config/cursor_enhanced_mcp_config.json",
            "docker-compose.yml",
            ".github/workflows/unified-deployment.yml",
            "maintenance_config.json",
        ]

        for config_file in config_files:
            if Path(config_file).exists():
                success, output = self.run_command(
                    ["cp", config_file, str(backup_dir / Path(config_file).name)]
                )
                if success:
                    backup_report["items_backed_up"].append(
                        {
                            "type": "configuration",
                            "file": config_file,
                            "status": "success",
                        }
                    )

        # Backup Docker secrets list
        success, output = self.run_command(
            ["docker", "secret", "ls", "--format", "json"]
        )
        if success:
            with open(backup_dir / "docker_secrets.json", "w") as f:
                f.write(output)
            backup_report["items_backed_up"].append(
                {"type": "docker_secrets", "status": "success"}
            )

        # Backup service list
        success, output = self.run_command(
            ["docker", "service", "ls", "--format", "json"]
        )
        if success:
            with open(backup_dir / "docker_services.json", "w") as f:
                f.write(output)
            backup_report["items_backed_up"].append(
                {"type": "docker_services", "status": "success"}
            )

        return backup_report

    def check_for_updates(self) -> dict:
        """Check for available updates"""
        self.logger.info("🔄 Checking for updates...")

        update_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "updates_available": [],
        }

        # Check for pip updates
        success, output = self.run_command(
            ["pip", "list", "--outdated", "--format=json"]
        )
        if success:
            try:
                outdated = json.loads(output)
                for package in outdated:
                    update_report["updates_available"].append(
                        {
                            "type": "python_package",
                            "name": package["name"],
                            "current_version": package["version"],
                            "latest_version": package["latest_version"],
                        }
                    )
            except json.JSONDecodeError:
                pass

        # Check for Docker image updates
        success, output = self.run_command(
            ["docker", "image", "ls", "--format", "json"]
        )
        if success:
            for line in output.split("\n"):
                if line.strip():
                    try:
                        image = json.loads(line)
                        # Check if image is more than 7 days old
                        created = image.get("CreatedAt", "")
                        if "days ago" in created:
                            days_str = created.split("days ago")[0].strip().split()[-1]
                            try:
                                days = int(days_str)
                                if days > 7:
                                    update_report["updates_available"].append(
                                        {
                                            "type": "docker_image",
                                            "repository": image.get("Repository", ""),
                                            "tag": image.get("Tag", ""),
                                            "age_days": days,
                                        }
                                    )
                            except ValueError:
                                pass
                    except json.JSONDecodeError:
                        continue

        return update_report

    def send_notification(self, report: dict, report_type: str):
        """Send notification about maintenance report"""
        # Simple console notification for now
        self.logger.info(f"📢 {report_type.title()} Report Generated")

        # Could be extended to send Slack/email notifications
        # based on configuration

    def run_maintenance_cycle(self):
        """Run complete maintenance cycle"""
        self.logger.info("🚀 Starting automated maintenance cycle...")

        maintenance_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "cycle_type": "automated",
            "reports": {},
        }

        try:
            # Health check
            health_report = self.check_system_health()
            maintenance_report["reports"]["health"] = health_report
            self.send_notification(health_report, "health")

            # Performance optimization
            if health_report["overall_status"] in ["warning", "unhealthy"]:
                optimization_report = self.run_performance_optimization()
                maintenance_report["reports"]["optimization"] = optimization_report
                self.send_notification(optimization_report, "optimization")

            # Security scan (daily)
            security_report = self.run_security_scan()
            maintenance_report["reports"]["security"] = security_report
            self.send_notification(security_report, "security")

            # Backup
            backup_report = self.run_backup()
            maintenance_report["reports"]["backup"] = backup_report
            self.send_notification(backup_report, "backup")

            # Update check
            update_report = self.check_for_updates()
            maintenance_report["reports"]["updates"] = update_report
            self.send_notification(update_report, "updates")

            # Save complete report
            report_file = f"maintenance_reports/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            Path("maintenance_reports").mkdir(exist_ok=True)

            with open(report_file, "w") as f:
                json.dump(maintenance_report, f, indent=2)

            self.logger.info(f"✅ Maintenance cycle completed. Report: {report_file}")

        except Exception as e:
            self.logger.error(f"❌ Maintenance cycle failed: {e}")
            raise

    def run_continuous_monitoring(self):
        """Run continuous monitoring loop"""
        self.logger.info("🔄 Starting continuous monitoring...")

        last_health_check = datetime.min
        last_security_scan = datetime.min
        last_backup = datetime.min
        last_update_check = datetime.min

        while True:
            try:
                now = datetime.utcnow()

                # Health check
                if (now - last_health_check).total_seconds() >= self.config[
                    "schedules"
                ]["health_check"]["interval_minutes"] * 60:
                    health_report = self.check_system_health()
                    if health_report["overall_status"] != "healthy":
                        self.logger.warning(
                            f"⚠️ System health: {health_report['overall_status']}"
                        )
                        self.send_notification(health_report, "health_alert")
                    last_health_check = now

                # Security scan
                if (now - last_security_scan).total_seconds() >= self.config[
                    "schedules"
                ]["security_scan"]["interval_hours"] * 3600:
                    security_report = self.run_security_scan()
                    if security_report["findings"]:
                        self.logger.warning(
                            f"🔒 Security findings: {len(security_report['findings'])}"
                        )
                        self.send_notification(security_report, "security_alert")
                    last_security_scan = now

                # Backup
                if (now - last_backup).total_seconds() >= self.config["schedules"][
                    "backup"
                ]["interval_hours"] * 3600:
                    backup_report = self.run_backup()
                    self.logger.info("💾 Automated backup completed")
                    last_backup = now

                # Update check
                if (now - last_update_check).total_seconds() >= self.config[
                    "schedules"
                ]["update_check"]["interval_hours"] * 3600:
                    update_report = self.check_for_updates()
                    if update_report["updates_available"]:
                        self.logger.info(
                            f"🔄 {len(update_report['updates_available'])} updates available"
                        )
                        self.send_notification(update_report, "update_alert")
                    last_update_check = now

                # Sleep for 1 minute before next check
                time.sleep(60)

            except KeyboardInterrupt:
                self.logger.info("⏹️ Continuous monitoring stopped by user")
                break
            except Exception as e:
                self.logger.error(f"❌ Monitoring error: {e}")
                time.sleep(60)  # Continue after error


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Sophia AI Automated Maintenance System"
    )
    parser.add_argument(
        "--mode",
        choices=["cycle", "continuous", "health", "security", "backup", "updates"],
        default="cycle",
        help="Maintenance mode to run",
    )
    parser.add_argument(
        "--config", default="maintenance_config.json", help="Configuration file path"
    )

    args = parser.parse_args()

    maintenance = MaintenanceSystem(args.config)

    try:
        if args.mode == "cycle":
            maintenance.run_maintenance_cycle()
        elif args.mode == "continuous":
            maintenance.run_continuous_monitoring()
        elif args.mode == "health":
            report = maintenance.check_system_health()
            print(json.dumps(report, indent=2))
        elif args.mode == "security":
            report = maintenance.run_security_scan()
            print(json.dumps(report, indent=2))
        elif args.mode == "backup":
            report = maintenance.run_backup()
            print(json.dumps(report, indent=2))
        elif args.mode == "updates":
            report = maintenance.check_for_updates()
            print(json.dumps(report, indent=2))
    except Exception as e:
        logging.error(f"❌ Maintenance failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
