#!/usr/bin/env python3
"""
Archive obsolete documentation files
Generated: 2025-07-04 16:00:00
"""

import os
import shutil
from datetime import datetime

# Files to archive
ARCHIVE_FILES = {
    "docs/system_handbook/09_ENTERPRISE_MCP_STANDARDIZATION_PLAN.md": "PLAN",
    "docs/PHASE_2_FOUNDATION_IMPLEMENTATION_PLAN.md": "PLAN",
    "docs/NEXT_PHASE_PLAN.md": "PLAN",
    "docs/COMPREHENSIVE_REMEDIATION_PLAN.md": "PLAN",
    "docs/MONOREPO_TRANSFORMATION_PLAN.md": "PLAN",
    "docs/UNIFIED_CHAT_ENHANCEMENT_PLAN.md": "PLAN",
    "docs/SOPHIA_AI_FINAL_IMPLEMENTATION_PLAN.md": "PLAN",
    "docs/NEXT_PHASE_FOUNDATION_PLAN.md": "PLAN",
    "docs/PHASE_4_NEXT_PRIORITIES_DETAILED_PLAN.md": "PLAN",
    "docs/DOCKER_CLOUD_BOTTLENECK_REMEDIATION_PLAN.md": "PLAN",
    "docs/system_handbook/10_ENTERPRISE_AI_ECOSYSTEM_PLAN.md": "PLAN",
    "docs/04-deployment/DOCKER_REMEDIATION_PLAN.md": "PLAN",
    "docs/REPOSITORY_CLEANUP_AND_ALIGNMENT_PLAN.md": "PLAN",
    "docs/PHASE_2_5_HOURS_5_8_PLAN.md": "PLAN",
    "docs/PHASE_2_5_AI_ORCHESTRATOR_RESEARCH_PLAN.md": "PLAN",
    "docs/monorepo/PHASE_1_FOUNDATION_PLAN.md": "PLAN",
    "docs/monorepo/NEXT_PHASE_QUALITY_FIRST_PLAN.md": "PLAN",
    "docs/PHASE_2_5_IMPLEMENTATION_PLAN.md": "PLAN",
    "docs/PRIORITIZED_ENHANCEMENT_PLAN.md": "PLAN",
    "docs/LANGCHAIN_INTEGRATION_PLAN.md": "PLAN",
    "docs/PHASE_2_5_LLM_GATEWAY_IMPLEMENTATION_PLAN.md": "PLAN",
    "docs/PHASE_3_UNIFIED_LLM_MIGRATION_PLAN.md": "PLAN",
    "docs/system_handbook/04_PHOENIX_MEMORY_INTEGRATION_PLAN.md": "PLAN",
    "docs/DOCUMENTATION_OUTDATEDNESS_REMEDIATION_PLAN.md": "PLAN",
    "docs/architecture/SERVICE_CONSOLIDATION_PLAN.md": "PLAN",
    "docs/04-deployment/COMPREHENSIVE_INTEGRATION_PLAN_V2.0.md": "PLAN",
    "docs/APPROVED_ENHANCEMENT_PLAN.md": "PLAN",
    "docs/WEEK_1_ACTION_PLAN.md": "PLAN",
    "docs/IMMEDIATE_ACTION_PLAN.md": "PLAN",
    "docs/UNIFIED_LLM_FINAL_STATUS_REPORT.md": "STATUS",
    "docs/REPOSITORY_ALIGNMENT_STATUS_REPORT.md": "STATUS",
    "docs/PHASE_2_FOUNDATION_STATUS.md": "STATUS",
    "docs/PHASE_3_IMPLEMENTATION_STATUS.md": "STATUS",
    "docs/UNIFIED_ARCHITECTURE_FINAL_STATUS.md": "STATUS",
    "docs/AI_AGENT_ORCHESTRATION_STATUS.md": "STATUS",
    "docs/CODEBASE_OPTIMIZATION_COMPLETE.md": "COMPLETE",
    "docs/DOCKER_CLOUD_DEPLOYMENT_COMPLETE.md": "COMPLETE",
    "docs/PHASE_3_COMPLETION_REPORT.md": "COMPLETE",
    "docs/PRIORITY_ENHANCEMENTS_COMPLETE.md": "COMPLETE",
    "docs/monorepo/WEEK1_QUALITY_AUDIT_COMPLETE.md": "COMPLETE",
    "docs/CODEBASE_OPTIMIZATION_COMPLETION.md": "COMPLETE",
    "docs/IMMEDIATE_ACTIONS_COMPLETED.md": "COMPLETE",
    "docs/PHASE_2_5_AI_ORCHESTRATOR_RESEARCH_STRATEGY.md": "PHASE",
    "docs/PHASE_3_DO_LATER_TASKS.md": "PHASE",
    "docs/PHASE_2_5_LLM_GATEWAY_RESEARCH_PROMPT.md": "PHASE",
    "docs/PHASE_1_DEPLOYMENT_SUMMARY.md": "PHASE",
    "docs/PHASE_2_5_PROGRESS_REVIEW_AND_NEXT_PHASE.md": "PHASE",
    "docs/monorepo/PHASE_0_KICKOFF.md": "PHASE",
    "docs/monorepo/PHASE_0_PROGRESS.md": "PHASE",
    "docs/PHASE_2_5_QUICK_REFERENCE.md": "PHASE",
    "docs/monorepo/PHASE_1_QUALITY_FIRST_OUTLINE.md": "PHASE",
    "docs/monorepo/PHASE_1_EXECUTIVE_SUMMARY.md": "PHASE",
    "docs/PHASE_2_5_INTEGRATION_NOTES.md": "PHASE",
    "docs/03-architecture/PHASE_1_PERFORMANCE_SECURITY_ENHANCEMENTS.md": "PHASE",
    "docs/WEEK_1_IMMEDIATE_ACTIONS.md": "WEEK",
    "docs/phase1/WEEK_1_PERFORMANCE_BASELINE.md": "WEEK",
    "docs/UNIFIED_CHAT_TECHNICAL_IMPLEMENTATION.md": "IMPLEMENTATION",
    "docs/SOPHIA_AI_INFRASTRUCTURE_MODERNIZATION_IMPLEMENTATION.md": "IMPLEMENTATION",
    "docs/GONG_WEBHOOK_SERVER_IMPLEMENTATION.md": "IMPLEMENTATION",
    "docs/UNIFIED_LLM_STRATEGY_IMPLEMENTATION.md": "IMPLEMENTATION",
    "docs/PORTKEY_IMPLEMENTATION_DEEP_RESEARCH_PROMPT.md": "IMPLEMENTATION",
    "docs/STRATEGIC_ENHANCEMENTS_IMPLEMENTATION_REPORT.md": "IMPLEMENTATION",
    "docs/monorepo/WEEK_1_IMPLEMENTATION_CHECKLIST.md": "IMPLEMENTATION",
}


def archive_docs():
    """Move obsolete docs to archive"""
    archive_dir = f"docs/archive/cleanup_{datetime.now().strftime('%Y%m%d')}"

    # Create archive directories
    os.makedirs(f"{archive_dir}/plans", exist_ok=True)
    os.makedirs(f"{archive_dir}/status", exist_ok=True)
    os.makedirs(f"{archive_dir}/completed", exist_ok=True)
    os.makedirs(f"{archive_dir}/phases", exist_ok=True)
    os.makedirs(f"{archive_dir}/other", exist_ok=True)

    archived_count = 0
    for src, category in ARCHIVE_FILES.items():
        if os.path.exists(src):
            # Determine destination
            if category == "PLAN":
                dst_dir = f"{archive_dir}/plans"
            elif category == "STATUS":
                dst_dir = f"{archive_dir}/status"
            elif category == "COMPLETE":
                dst_dir = f"{archive_dir}/completed"
            elif category in ["PHASE", "WEEK"]:
                dst_dir = f"{archive_dir}/phases"
            else:
                dst_dir = f"{archive_dir}/other"

            dst = os.path.join(dst_dir, os.path.basename(src))

            try:
                shutil.move(src, dst)
                archived_count += 1
            except Exception:
                pass

    # Create index
    with open(f"{archive_dir}/INDEX.md", "w") as f:
        f.write("# Documentation Archive Index\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d')}\n\n")
        f.write("## Summary\n")
        f.write(f"- Total files archived: {archived_count}\n")
        f.write(f"- Archive location: {archive_dir}\n\n")
        f.write("## Files\n")
        for src, category in sorted(ARCHIVE_FILES.items()):
            f.write(f"- {src} ({category})\n")


if __name__ == "__main__":
    archive_docs()
