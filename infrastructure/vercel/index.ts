import * as pulumi from "@pulumi/pulumi";
import * as vercel from "@pulumiverse/vercel";
import * as command from "@pulumi/command";
import * as fs from "fs";

// Get configuration
const config = new pulumi.Config();
const namecheapConfig = new pulumi.Config("namecheap");

// Configuration values
const deleteLegacyProjects = config.getBoolean("deleteLegacyOrchestraProjects") || false;
const vercelToken = config.requireSecret("vercelToken");
const vercelTeamId = process.env.VERCEL_TEAM_ID;
const namecheapApiKey = namecheapConfig.getSecret("apiKey");
const namecheapApiUser = namecheapConfig.get("apiUser");

// Project configuration
const githubRepo = "ai-cherry/sophia-main";
const rootDirectory = "frontend";
const domain = "sophia-intel.ai";

// =====================================================================
// 1. VERCEL PROJECT CLEANUP
// =====================================================================

// Create cleanup script for Vercel projects
const cleanupScript = `#!/bin/bash
set -e

echo "Starting Vercel project cleanup..."

# Always delete these projects (not Git-connected)
ALWAYS_DELETE=("frontend" "modern-admin" "dist")

# Conditionally delete these projects
CONDITIONAL_DELETE=("orchestra-main" "dashboard" "admin-interface")

# Function to delete project
delete_project() {
    local project_name=$1
    echo "Attempting to delete project: $project_name"

    # Check if project exists
    if vercel projects ls --token="$VERCEL_TOKEN" | grep -q "$project_name"; then
        echo "Found project $project_name, deleting..."
        vercel projects rm "$project_name" --yes --token="$VERCEL_TOKEN" || echo "Failed to delete $project_name (may not exist)"
    else
        echo "Project $project_name not found, skipping..."
    fi
}

# Function to remove domain from project
remove_domain() {
    local project_name=$1
    local domain_name=$2
    echo "Attempting to remove domain $domain_name from project $project_name"

    # Try to remove domain (may fail if domain doesn't exist)
    vercel domains rm "$domain_name" --yes --token="$VERCEL_TOKEN" || echo "Failed to remove domain $domain_name (may not exist)"
}

# Always delete projects
for project in "\${ALWAYS_DELETE[@]}"; do
    delete_project "$project"
done

# Conditionally delete projects if flag is set
if [ "$DELETE_LEGACY" = "true" ]; then
    echo "DELETE_LEGACY flag is set, removing legacy projects..."

    # Remove domains from legacy projects first
    remove_domain "dashboard" "dashboard.cherry-ai.me"
    remove_domain "admin-interface" "admin.cherry-ai.me"

    # Delete legacy projects
    for project in "\${CONDITIONAL_DELETE[@]}"; do
        delete_project "$project"
    done
else
    echo "DELETE_LEGACY flag not set, skipping legacy project deletion"
fi

echo "Vercel project cleanup completed!"
`;

// Write cleanup script to file
const cleanupScriptPath = "/tmp/vercel-cleanup.sh";
fs.writeFileSync(cleanupScriptPath, cleanupScript);
fs.chmodSync(cleanupScriptPath, 0o755);

// Execute cleanup script
const cleanup = new command.local.Command("vercel-cleanup", {
    create: pulumi.interpolate`VERCEL_TOKEN=${vercelToken} DELETE_LEGACY=${deleteLegacyProjects} bash ${cleanupScriptPath}`,
    environment: {
        VERCEL_TOKEN: vercelToken,
        DELETE_LEGACY: deleteLegacyProjects.toString(),
    },
});

// =====================================================================
// 2. VERCEL PROJECT CREATION - UPDATED FOR VITE
// =====================================================================

// Production project - Updated for Vite + React
const prodProject = new vercel.Project("sophia-ai-production", {
    name: "sophia-ai-unified-dashboard-prod",
    framework: "vite",
    gitRepository: {
        type: "github",
        repo: githubRepo,
        productionBranch: "main",
    },
    rootDirectory: rootDirectory,
    buildCommand: "npm run build",
    outputDirectory: "dist",
    installCommand: "npm ci",
    teamId: vercelTeamId,
}, { dependsOn: [cleanup] });

// Development project - Updated for Vite + React
const devProject = new vercel.Project("sophia-ai-development", {
    name: "sophia-ai-unified-dashboard-dev",
    framework: "vite",
    gitRepository: {
        type: "github",
        repo: githubRepo,
        productionBranch: "develop",
    },
    rootDirectory: rootDirectory,
    buildCommand: "npm run build",
    outputDirectory: "dist",
    installCommand: "npm ci",
    teamId: vercelTeamId,
}, { dependsOn: [cleanup] });

// =====================================================================
// 3. ENHANCED UNIFIED DASHBOARD ENVIRONMENT VARIABLES
// =====================================================================

// Production environment variables - Enhanced Dashboard
const prodEnvVars = [
    // Basic configuration
    { key: "VITE_DEPLOYMENT_ENV", value: "production" },
    { key: "VITE_BUILD_VERSION", value: "2.0.0" },
    { key: "VITE_BACKEND_URL", value: "https://api.sophia-intel.ai" },
    { key: "VITE_WS_URL", value: "wss://api.sophia-intel.ai" },

    // Enhanced Dashboard Features
    { key: "VITE_ENABLE_ENHANCED_DASHBOARD", value: "true" },
    { key: "VITE_ENABLE_CHART_JS_DASHBOARD", value: "true" },
    { key: "VITE_ENABLE_REAL_TIME_CHARTS", value: "true" },
    { key: "VITE_ENABLE_FIGMA_INTEGRATION", value: "true" },

    // Design System
    { key: "VITE_GLASSMORPHISM_ENABLED", value: "true" },
    { key: "VITE_DESIGN_SYSTEM_MODE", value: "production" },

    // Monitoring & Analytics
    { key: "VITE_ENABLE_PERFORMANCE_MONITORING", value: "true" },
    { key: "VITE_ANALYTICS_ENABLED", value: "false" },
    { key: "VITE_DEBUG_MODE", value: "false" },

    // Security
    { key: "VITE_UNIFIED_ACCESS_TOKEN", value: "sophia_unified_access_2024" },
    { key: "VITE_ADMIN_MODE", value: "false" }
];

// Development environment variables - Enhanced Dashboard
const devEnvVars = [
    // Basic configuration
    { key: "VITE_DEPLOYMENT_ENV", value: "development" },
    { key: "VITE_BUILD_VERSION", value: "2.0.0-dev" },
    { key: "VITE_BACKEND_URL", value: "https://dev.api.sophia-intel.ai" },
    { key: "VITE_WS_URL", value: "wss://dev.api.sophia-intel.ai" },

    // Enhanced Dashboard Features
    { key: "VITE_ENABLE_ENHANCED_DASHBOARD", value: "true" },
    { key: "VITE_ENABLE_CHART_JS_DASHBOARD", value: "true" },
    { key: "VITE_ENABLE_REAL_TIME_CHARTS", value: "true" },
    { key: "VITE_ENABLE_FIGMA_INTEGRATION", value: "true" },

    // Design System
    { key: "VITE_GLASSMORPHISM_ENABLED", value: "true" },
    { key: "VITE_DESIGN_SYSTEM_MODE", value: "development" },

    // Monitoring & Analytics
    { key: "VITE_ENABLE_PERFORMANCE_MONITORING", value: "true" },
    { key: "VITE_ANALYTICS_ENABLED", value: "false" },
    { key: "VITE_DEBUG_MODE", value: "true" },

    // Security
    { key: "VITE_UNIFIED_ACCESS_TOKEN", value: "sophia_unified_access_token_dev" },
    { key: "VITE_ADMIN_MODE", value: "true" }
];

// Create production environment variables
prodEnvVars.forEach((envVar, index) => {
    new vercel.ProjectEnvironmentVariable(`prod-${envVar.key.toLowerCase()}`, {
        projectId: prodProject.id,
        targets: ["production"],
        key: envVar.key,
        value: envVar.value,
        teamId: vercelTeamId,
    });
});

// Create development environment variables
devEnvVars.forEach((envVar, index) => {
    new vercel.ProjectEnvironmentVariable(`dev-${envVar.key.toLowerCase()}`, {
        projectId: devProject.id,
        targets: ["production", "preview", "development"],
        key: envVar.key,
        value: envVar.value,
        teamId: vercelTeamId,
    });
});

// =====================================================================
// 4. FIGMA INTEGRATION ENVIRONMENT VARIABLES (SECURE)
// =====================================================================

// Note: These should be set manually in Vercel dashboard or via GitHub secrets
// as they contain sensitive tokens

// Production Figma Variables (to be set manually)
new vercel.ProjectEnvironmentVariable("prod-figma-token", {
    projectId: prodProject.id,
    targets: ["production"],
    key: "VITE_FIGMA_PERSONAL_ACCESS_TOKEN",
    value: "PLACEHOLDER_SET_IN_VERCEL_DASHBOARD",
    teamId: vercelTeamId,
});

new vercel.ProjectEnvironmentVariable("prod-figma-file-key", {
    projectId: prodProject.id,
    targets: ["production"],
    key: "VITE_FIGMA_FILE_KEY",
    value: "PLACEHOLDER_SET_IN_VERCEL_DASHBOARD",
    teamId: vercelTeamId,
});

// Development Figma Variables (to be set manually)
new vercel.ProjectEnvironmentVariable("dev-figma-token", {
    projectId: devProject.id,
    targets: ["production", "preview", "development"],
    key: "VITE_FIGMA_PERSONAL_ACCESS_TOKEN",
    value: "PLACEHOLDER_SET_IN_VERCEL_DASHBOARD",
    teamId: vercelTeamId,
});

new vercel.ProjectEnvironmentVariable("dev-figma-file-key", {
    projectId: devProject.id,
    targets: ["production", "preview", "development"],
    key: "VITE_FIGMA_FILE_KEY",
    value: "PLACEHOLDER_SET_IN_VERCEL_DASHBOARD",
    teamId: vercelTeamId,
});

// =====================================================================
// 5. CUSTOM DOMAINS
// =====================================================================

// Production domain
const prodDomain = new vercel.ProjectDomain("prod-domain", {
    projectId: prodProject.id,
    domain: `app.${domain}`,
    teamId: vercelTeamId,
});

// Development domain
const devDomain = new vercel.ProjectDomain("dev-domain", {
    projectId: devProject.id,
    domain: `dev.app.${domain}`,
    teamId: vercelTeamId,
});

// =====================================================================
// 6. ENHANCED SPA ROUTING CONFIGURATION
// =====================================================================

// Create vercel.json configuration for SPA routing
const vercelConfig = {
    version: 2,
    rewrites: [
        {
            source: "/dashboard/unified-enhanced",
            destination: "/index.html"
        },
        {
            source: "/dashboard/unified",
            destination: "/index.html"
        },
        {
            source: "/dashboard/(.*)",
            destination: "/index.html"
        },
        {
            source: "/(.*)",
            destination: "/index.html"
        }
    ],
    headers: [
        {
            source: "/assets/(.*)",
            headers: [
                {
                    key: "Cache-Control",
                    value: "public, max-age=31536000, immutable"
                }
            ]
        },
        {
            source: "/(.*\\.(js|css|png|jpg|jpeg|gif|ico|svg))",
            headers: [
                {
                    key: "Cache-Control",
                    value: "public, max-age=86400"
                }
            ]
        }
    ]
};

// Write vercel.json to frontend directory
const vercelConfigPath = "../../frontend/vercel.json";
fs.writeFileSync(vercelConfigPath, JSON.stringify(vercelConfig, null, 2));

// =====================================================================
// 7. NAMECHEAP DNS AUTOMATION (UNCHANGED)
// =====================================================================

// Create Namecheap DNS management script
const namecheapScript = `#!/usr/bin/env python3
import requests
import sys
import xml.etree.ElementTree as ET
from urllib.parse import urlencode

class NamecheapAPI:
    def __init__(self, api_user, api_key, client_ip="127.0.0.1"):
        self.api_user = api_user
        self.api_key = api_key
        self.client_ip = client_ip
        self.base_url = "https://api.namecheap.com/xml.response"

    def _make_request(self, command, extra_params=None):
        params = {
            "ApiUser": self.api_user,
            "ApiKey": self.api_key,
            "UserName": self.api_user,
            "Command": command,
            "ClientIp": self.client_ip,
        }

        if extra_params:
            params.update(extra_params)

        response = requests.get(self.base_url, params=params)
        response.raise_for_status()

        root = ET.fromstring(response.content)

        # Check for API errors
        if root.get("Status") != "OK":
            errors = root.find(".//Errors")
            if errors is not None:
                error_msg = errors.find("Error").text if errors.find("Error") is not None else "Unknown error"
                raise Exception(f"Namecheap API Error: {error_msg}")

        return root

    def get_hosts(self, domain):
        """Get existing DNS records for domain"""
        sld, tld = domain.split(".", 1)

        response = self._make_request("namecheap.domains.dns.getHosts", {
            "SLD": sld,
            "TLD": tld
        })

        hosts = []
        for host in response.findall(".//host"):
            hosts.append({
                "Name": host.get("Name"),
                "Type": host.get("Type"),
                "Address": host.get("Address"),
                "TTL": host.get("TTL")
            })

        return hosts

    def set_hosts(self, domain, hosts):
        """Set DNS records for domain"""
        sld, tld = domain.split(".", 1)

        params = {
            "SLD": sld,
            "TLD": tld
        }

        # Add host records to params
        for i, host in enumerate(hosts, 1):
            params[f"HostName{i}"] = host["Name"]
            params[f"RecordType{i}"] = host["Type"]
            params[f"Address{i}"] = host["Address"]
            params[f"TTL{i}"] = str(host["TTL"])

        response = self._make_request("namecheap.domains.dns.setHosts", params)
        return response.get("Status") == "OK"

def main():
    if len(sys.argv) < 6:
        print("Usage: python3 namecheap_dns.py <api_user> <api_key> <domain> <prod_verification> <dev_verification>")
        sys.exit(1)

    api_user = sys.argv[1]
    api_key = sys.argv[2]
    domain = sys.argv[3]
    prod_verification = sys.argv[4]
    dev_verification = sys.argv[5]

    try:
        api = NamecheapAPI(api_user, api_key)

        # Get existing hosts
        existing_hosts = api.get_hosts(domain)
        print(f"Found {len(existing_hosts)} existing DNS records")

        # Filter out any existing Vercel-related records
        filtered_hosts = [
            host for host in existing_hosts
            if not (
                (host["Name"] == "app" and host["Type"] == "CNAME") or
                (host["Name"] == "dev.app" and host["Type"] == "CNAME") or
                (host["Name"] == "_vercel.app" and host["Type"] == "TXT") or
                (host["Name"] == "_vercel.dev.app" and host["Type"] == "TXT")
            )
        ]

        # Add new Vercel records
        new_hosts = filtered_hosts + [
            {
                "Name": "app",
                "Type": "CNAME",
                "Address": "cname.vercel-dns.com.",
                "TTL": 300
            },
            {
                "Name": "dev.app",
                "Type": "CNAME",
                "Address": "cname.vercel-dns.com.",
                "TTL": 300
            }
        ]

        # Add verification records if provided
        if prod_verification and prod_verification != "PLACEHOLDER":
            new_hosts.append({
                "Name": "_vercel.app",
                "Type": "TXT",
                "Address": prod_verification,
                "TTL": 300
            })

        if dev_verification and dev_verification != "PLACEHOLDER":
            new_hosts.append({
                "Name": "_vercel.dev.app",
                "Type": "TXT",
                "Address": dev_verification,
                "TTL": 300
            })

        # Update DNS records
        success = api.set_hosts(domain, new_hosts)

        if success:
            print("DNS records updated successfully!")
            print("Added records:")
            print("- app.sophia-intel.ai CNAME cname.vercel-dns.com.")
            print("- dev.app.sophia-intel.ai CNAME cname.vercel-dns.com.")
            if prod_verification != "PLACEHOLDER":
                print(f"- _vercel.app.sophia-intel.ai TXT {prod_verification}")
            if dev_verification != "PLACEHOLDER":
                print(f"- _vercel.dev.app.sophia-intel.ai TXT {dev_verification}")
        else:
            print("Failed to update DNS records")
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
`;

// Write Namecheap script to file
const namecheapScriptPath = "/tmp/namecheap_dns.py";
fs.writeFileSync(namecheapScriptPath, namecheapScript);

// =====================================================================
// 8. DOMAIN VERIFICATION RETRIEVAL
// =====================================================================

// Script to get verification values from Vercel
const verificationScript = `#!/bin/bash
set -e

get_verification_value() {
    local domain=$1
    local project_id=$2

    echo "Getting verification value for domain: $domain"

    # Use Vercel CLI to get domain info
    vercel domains inspect "$domain" --token="$VERCEL_TOKEN" --output json 2>/dev/null | \
        jq -r '.verification[]? | select(.type == "TXT") | .value' || echo "PLACEHOLDER"
}

# Get verification values
PROD_VERIFICATION=$(get_verification_value "app.sophia-intel.ai" "$PROD_PROJECT_ID")
DEV_VERIFICATION=$(get_verification_value "dev.app.sophia-intel.ai" "$DEV_PROJECT_ID")

echo "Production verification: $PROD_VERIFICATION"
echo "Development verification: $DEV_VERIFICATION"

# Run Namecheap DNS update if API credentials are available
if [ -n "$NAMECHEAP_API_USER" ] && [ -n "$NAMECHEAP_API_KEY" ]; then
    echo "Updating Namecheap DNS records..."
    python3 /tmp/namecheap_dns.py "$NAMECHEAP_API_USER" "$NAMECHEAP_API_KEY" "sophia-intel.ai" "$PROD_VERIFICATION" "$DEV_VERIFICATION"
else
    echo "Namecheap API credentials not provided, skipping DNS automation"
    echo ""
    echo "Manual DNS Records Required:"
    echo "=========================="
    echo "Domain: sophia-intel.ai"
    echo ""
    echo "CNAME Records:"
    echo "Host: app"
    echo "Value: cname.vercel-dns.com"
    echo "TTL: 300"
    echo ""
    echo "Host: dev.app"
    echo "Value: cname.vercel-dns.com"
    echo "TTL: 300"
    echo ""
    if [ "$PROD_VERIFICATION" != "PLACEHOLDER" ]; then
        echo "TXT Record (Production Verification):"
        echo "Host: _vercel.app"
        echo "Value: $PROD_VERIFICATION"
        echo "TTL: 300"
        echo ""
    fi
    if [ "$DEV_VERIFICATION" != "PLACEHOLDER" ]; then
        echo "TXT Record (Development Verification):"
        echo "Host: _vercel.dev.app"
        echo "Value: $DEV_VERIFICATION"
        echo "TTL: 300"
        echo ""
    fi
fi
`;

// Write verification script
const verificationScriptPath = "/tmp/domain-verification.sh";
fs.writeFileSync(verificationScriptPath, verificationScript);
fs.chmodSync(verificationScriptPath, 0o755);

// Execute domain verification and DNS setup
const dnsSetup = new command.local.Command("dns-setup", {
    create: pulumi.all([prodProject.id, devProject.id, namecheapApiUser, namecheapApiKey]).apply(
        ([prodId, devId, apiUser, apiKey]) =>
            `VERCEL_TOKEN=${vercelToken} PROD_PROJECT_ID=${prodId} DEV_PROJECT_ID=${devId} NAMECHEAP_API_USER=${apiUser || ""} NAMECHEAP_API_KEY=${apiKey || ""} bash ${verificationScriptPath}`
    ),
    environment: {
        VERCEL_TOKEN: vercelToken,
    },
}, { dependsOn: [prodDomain, devDomain] });

// =====================================================================
// 9. DOMAIN VERIFICATION STATUS CHECK
// =====================================================================

// Script to check domain verification status
const statusCheckScript = `#!/bin/bash
check_domain_status() {
    local domain=$1
    echo "Checking status for domain: $domain"

    # Get domain status from Vercel
    status=$(vercel domains inspect "$domain" --token="$VERCEL_TOKEN" --output json 2>/dev/null | jq -r '.verified // false')
    echo "$domain: $status"
}

echo "Enhanced Unified Dashboard Deployment Status:"
echo "========================================"
echo "Projects Created:"
echo "- Production: sophia-ai-unified-dashboard-prod"
echo "- Development: sophia-ai-unified-dashboard-dev"
echo ""
echo "Framework: Vite + React"
echo "Build Output: dist/"
echo "Features Enabled:"
echo "- Enhanced Unified Dashboard"
echo "- Chart.js Dashboard"
echo "- Figma Integration"
echo "- Real-time Charts"
echo "- Glassmorphism Design"
echo ""
echo "Domain Verification Status:"
echo "=========================="
check_domain_status "app.sophia-intel.ai"
check_domain_status "dev.app.sophia-intel.ai"
echo ""
echo "Manual Configuration Required:"
echo "============================"
echo "1. Set VITE_FIGMA_PERSONAL_ACCESS_TOKEN in Vercel dashboard"
echo "2. Set VITE_FIGMA_FILE_KEY in Vercel dashboard"
echo "3. Configure backend API endpoints"
echo "4. Test dashboard routes:"
echo "   - /dashboard/unified (Chart.js Dashboard)"
echo "   - /dashboard/unified-enhanced (Figma + Enhanced Dashboard)"
`;

const statusCheckPath = "/tmp/status-check.sh";
fs.writeFileSync(statusCheckPath, statusCheckScript);
fs.chmodSync(statusCheckPath, 0o755);

const statusCheck = new command.local.Command("status-check", {
    create: `VERCEL_TOKEN=${vercelToken} bash ${statusCheckPath}`,
    environment: {
        VERCEL_TOKEN: vercelToken,
    },
}, { dependsOn: [dnsSetup] });

// =====================================================================
// 10. EXPORTS
// =====================================================================

export const productionProjectId = prodProject.id;
export const developmentProjectId = devProject.id;
export const productionProjectName = prodProject.name;
export const developmentProjectName = devProject.name;
export const productionUrl = `https://${prodProject.name}.vercel.app`;
export const developmentUrl = `https://${devProject.name}.vercel.app`;
export const productionCustomDomain = `https://app.${domain}`;
export const developmentCustomDomain = `https://dev.app.${domain}`;
export const cleanupStatus = cleanup.stdout;
export const dnsSetupStatus = dnsSetup.stdout;
export const verificationStatus = statusCheck.stdout;

// Enhanced Configuration Summary
export const configurationSummary = {
    repository: githubRepo,
    rootDirectory: rootDirectory,
    framework: "vite",
    buildOutput: "dist",
    domain: domain,
    features: {
        enhancedDashboard: true,
        chartJsDashboard: true,
        figmaIntegration: true,
        realTimeCharts: true,
        glassmorphism: true
    },
    routes: {
        enhancedUnified: "/dashboard/unified-enhanced",
        originalUnified: "/dashboard/unified",
        unifiedHub: "/dashboard"
    },
    deleteLegacyProjects: deleteLegacyProjects,
    automatedDNS: pulumi.all([namecheapApiUser, namecheapApiKey]).apply(
        ([user, key]) => !!(user && key)
    ),
};

// For easy access in other parts of the Pulumi program
export const outputs = {
    ...configurationSummary,
    endpoints: {
        health: "/health",
        unifiedEnhanced: "/dashboard/unified-enhanced",
        originalUnified: "/dashboard/unified",
    },
};
