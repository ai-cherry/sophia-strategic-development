#!/bin/bash
set -euo pipefail

# GitHub Project Setup for Monorepo Transformation
# Requires GitHub CLI (gh) to be installed and authenticated

echo "🚀 Setting up GitHub Project for Monorepo Transformation"
echo "======================================================="

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) is not installed${NC}"
    echo "Please install it from: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}Error: Not authenticated with GitHub${NC}"
    echo "Run: gh auth login"
    exit 1
fi

# Variables
ORG="ai-cherry"
REPO="sophia-main"
PROJECT_TITLE="Monorepo Transformation"

echo "Creating project board..."

# Create the project (if it doesn't exist)
PROJECT_ID=$(gh project create \
    --owner "$ORG" \
    --title "$PROJECT_TITLE" \
    --body "Transforming Sophia AI to unified monorepo with Turborepo + PNPM + UV" \
    --format json 2>/dev/null | jq -r '.id' || echo "exists")

if [ "$PROJECT_ID" = "exists" ]; then
    echo -e "${YELLOW}Project already exists, fetching ID...${NC}"
    PROJECT_ID=$(gh project list --owner "$ORG" --format json | jq -r ".[] | select(.title == \"$PROJECT_TITLE\") | .id")
fi

echo -e "${GREEN}✅ Project created/found: $PROJECT_ID${NC}"

# Create labels if they don't exist
echo ""
echo "Creating labels..."

create_label() {
    local name=$1
    local color=$2
    local description=$3

    if gh label create "$name" --color "$color" --description "$description" --repo "$ORG/$REPO" 2>/dev/null; then
        echo -e "${GREEN}✅ Created label: $name${NC}"
    else
        echo -e "${YELLOW}⚠️  Label already exists: $name${NC}"
    fi
}

# Phase labels
create_label "phase-0" "0E8A16" "Preparation & Kickoff"
create_label "phase-1" "0E8A16" "Planning & Design"
create_label "phase-2" "0E8A16" "Coding & Implementation"
create_label "phase-3" "0E8A16" "Code Review & QA"
create_label "phase-4" "0E8A16" "Documentation & Training"
create_label "phase-5" "0E8A16" "Monitoring & Improvement"

# Priority labels
create_label "priority-critical" "B60205" "Critical priority"
create_label "priority-high" "D93F0B" "High priority"
create_label "priority-medium" "FBCA04" "Medium priority"

# Team labels
create_label "team-backend" "1D76DB" "Backend team"
create_label "team-frontend" "1D76DB" "Frontend team"
create_label "team-devops" "1D76DB" "DevOps team"

# Type labels
create_label "type-migration" "5319E7" "Migration task"
create_label "type-config" "5319E7" "Configuration task"
create_label "type-docs" "5319E7" "Documentation task"

# Status labels
create_label "blocked" "E99695" "Blocked by dependency"

# Create milestones
echo ""
echo "Creating milestones..."

create_milestone() {
    local title=$1
    local due_date=$2
    local description=$3

    if gh api "repos/$ORG/$REPO/milestones" \
        --method POST \
        -f title="$title" \
        -f due_on="$due_date" \
        -f description="$description" &>/dev/null; then
        echo -e "${GREEN}✅ Created milestone: $title${NC}"
    else
        echo -e "${YELLOW}⚠️  Milestone might already exist: $title${NC}"
    fi
}

# Calculate due dates (relative to today)
TODAY=$(date -u +%Y-%m-%d)
DAY_2=$(date -u -d "+2 days" +%Y-%m-%d)
DAY_7=$(date -u -d "+7 days" +%Y-%m-%d)
WEEK_2=$(date -u -d "+14 days" +%Y-%m-%d)
WEEK_3=$(date -u -d "+21 days" +%Y-%m-%d)
WEEK_4=$(date -u -d "+28 days" +%Y-%m-%d)
WEEK_6=$(date -u -d "+42 days" +%Y-%m-%d)
WEEK_7=$(date -u -d "+49 days" +%Y-%m-%d)

create_milestone "Phase 0 Complete" "${DAY_2}T23:59:59Z" "Kickoff and preparation complete"
create_milestone "Phase 1 Complete" "${DAY_7}T23:59:59Z" "Planning and design complete"
create_milestone "Python Migration" "${WEEK_2}T23:59:59Z" "All Python services migrated to UV"
create_milestone "JavaScript Migration" "${WEEK_3}T23:59:59Z" "Frontend migrated to PNPM workspace"
create_milestone "CI/CD Complete" "${WEEK_4}T23:59:59Z" "CI/CD templates implemented"
create_milestone "QA Signoff" "${WEEK_6}T23:59:59Z" "QA validation complete"
create_milestone "Training Complete" "${WEEK_7}T23:59:59Z" "Documentation and training delivered"

# Create initial issues
echo ""
echo "Creating initial issues..."

# Phase 0 issues
gh issue create \
    --title "Form cross-functional task force" \
    --body "Identify and confirm team members for:
- Backend Lead
- Frontend Lead
- DevOps Lead
- QA Lead
- Security Lead
- Documentation Owner
- Performance Engineer
- Release Manager" \
    --label "phase-0,priority-critical" \
    --milestone "Phase 0 Complete" \
    --repo "$ORG/$REPO" || true

gh issue create \
    --title "Set up communication channels" \
    --body "- [ ] Create #monorepo-transformation Slack channel
- [ ] Add all task force members
- [ ] Pin transformation plan document
- [ ] Set channel topic with timeline
- [ ] Create meeting calendar
- [ ] Send kickoff invites" \
    --label "phase-0,priority-critical" \
    --milestone "Phase 0 Complete" \
    --repo "$ORG/$REPO" || true

gh issue create \
    --title "Conduct kickoff meeting" \
    --body "**Agenda:**
1. Introduction & Goals (10 min)
2. Review Transformation Plan (20 min)
3. Discuss Roles & Responsibilities (15 min)
4. Address Concerns & Questions (10 min)
5. Next Steps & Action Items (5 min)

**Materials needed:**
- Executive summary slides
- Role assignment matrix
- Timeline visualization
- Risk register" \
    --label "phase-0,priority-critical" \
    --milestone "Phase 0 Complete" \
    --repo "$ORG/$REPO" || true

# Phase 1 planning issues
gh issue create \
    --title "Complete requirements gathering" \
    --body "- [ ] Inventory existing tools and workflows
- [ ] Document current CI/CD pipelines
- [ ] List all services and dependencies
- [ ] Identify integration points
- [ ] Document pain points with metrics
- [ ] Confirm technology choices" \
    --label "phase-1,priority-high,type-docs" \
    --milestone "Phase 1 Complete" \
    --repo "$ORG/$REPO" || true

gh issue create \
    --title "Design monorepo architecture" \
    --body "- [ ] Create detailed directory structure
- [ ] Define naming conventions
- [ ] Design import path strategy
- [ ] Plan shared library structure
- [ ] Create migration mapping
- [ ] Update System Handbook" \
    --label "phase-1,priority-high,type-docs" \
    --milestone "Phase 1 Complete" \
    --repo "$ORG/$REPO" || true

# Migration tracking issues
gh issue create \
    --title "Migrate backend API service" \
    --body "- [ ] Move backend/api to apps/api
- [ ] Update imports
- [ ] Update Dockerfile
- [ ] Test build and startup
- [ ] Update documentation
- [ ] Validate CI/CD" \
    --label "phase-2,priority-critical,type-migration,team-backend" \
    --milestone "Python Migration" \
    --repo "$ORG/$REPO" || true

gh issue create \
    --title "Migrate frontend to PNPM workspace" \
    --body "- [ ] Convert to PNPM
- [ ] Extract shared UI components
- [ ] Update build configuration
- [ ] Test development workflow
- [ ] Update deployment scripts
- [ ] Validate production build" \
    --label "phase-2,priority-critical,type-migration,team-frontend" \
    --milestone "JavaScript Migration" \
    --repo "$ORG/$REPO" || true

echo ""
echo -e "${GREEN}✨ GitHub Project Setup Complete!${NC}"
echo ""
echo "View your project at: https://github.com/orgs/$ORG/projects"
echo "View issues at: https://github.com/$ORG/$REPO/issues"
echo ""
echo "Next steps:"
echo "1. Assign team members to issues"
echo "2. Add issues to project board"
echo "3. Set up automation rules"
echo "4. Schedule kickoff meeting"
