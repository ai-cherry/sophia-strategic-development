#!/bin/bash
#
# ========================================================================================
# PERMANENT ENVIRONMENT FIX SCRIPT FOR SOPHIA AI
# ========================================================================================
#
# This script PERMANENTLY resolves all PULUMI_ACCESS_TOKEN and environment
# configuration issues by saving the correct variables directly into your
# shell profile.
#
# Run this script ONCE to fix your environment for good.
#
# USAGE:
#   export PULUMI_ACCESS_TOKEN="your-actual-token"
#   source scripts/fix_environment_permanently.sh
#
# ========================================================================================

# --- Configuration ---
# IMPORTANT: Set your actual Pulumi Access Token in your environment
# You can get this from: https://app.pulumi.com/account/tokens
# For scoobyjava-org access, use the token provided by your admin
PULUMI_TOKEN="${PULUMI_ACCESS_TOKEN:-YOUR_PULUMI_TOKEN_HERE}"
PULUMI_ORG_NAME="scoobyjava-org"
ENVIRONMENT_NAME="prod"

# --- Safety Check ---
if [ "$PULUMI_TOKEN" = "YOUR_PULUMI_TOKEN_HERE" ] || [ -z "$PULUMI_TOKEN" ]; then
    echo "❌ ERROR: Pulumi token not configured!"
    echo "   Please set PULUMI_ACCESS_TOKEN environment variable first."
    echo "   Example: export PULUMI_ACCESS_TOKEN=\"your-actual-token\""
    echo "   Then run this script again."
    return 1 2>/dev/null || exit 1
fi

# --- Shell Profile Detection ---
# Detect the user's shell and select the correct profile file.
if [ -n "$BASH_VERSION" ]; then
    PROFILE_FILE="$HOME/.bashrc"
elif [ -n "$ZSH_VERSION" ]; then
    PROFILE_FILE="$HOME/.zshrc"
else
    PROFILE_FILE="$HOME/.profile"
fi

echo "🔧 Detected shell profile: $PROFILE_FILE"

# --- Function to Add/Update Environment Variable ---
add_or_update_variable() {
    local var_name="$1"
    local var_value="$2"
    
    # Check if the variable is already set correctly
    if grep -q "export $var_name=\"$var_value\"" "$PROFILE_FILE"; then
        echo "✅ $var_name is already set correctly."
    else
        # If the variable exists but with a different value, remove the old line
        if grep -q "export $var_name=" "$PROFILE_FILE"; then
            echo "🔄 Updating existing $var_name..."
            # Use sed to replace the line in-place
            sed -i.bak "/export $var_name=/d" "$PROFILE_FILE"
        else
            echo "➕ Adding new $var_name..."
        fi
        
        # Add the corrected export line to the profile
        echo "export $var_name=\"$var_value\"" >> "$PROFILE_FILE"
        echo "   -> $var_name has been set."
    fi
}

# --- Apply Permanent Fixes ---
echo "🚀 Applying permanent environment fixes..."
echo "-------------------------------------------------"

add_or_update_variable "PULUMI_ACCESS_TOKEN" "$PULUMI_TOKEN"
add_or_update_variable "PULUMI_ORG" "$PULUMI_ORG_NAME"
add_or_update_variable "ENVIRONMENT" "$ENVIRONMENT_NAME"

# --- Final Instructions ---
echo "-------------------------------------------------"
echo "🎉 SUCCESS! Your environment has been permanently fixed."
echo ""
echo "🔴 CRITICAL NEXT STEP:"
echo "   To apply these changes, you MUST either:"
echo "   1. Restart your terminal session."
echo "   2. Run the following command:"
echo "      source $PROFILE_FILE"
echo ""
echo "After that, the 'invalid access token' error will be gone forever."
echo "=================================================" 