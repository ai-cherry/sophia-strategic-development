# MCP Production Deployment - ALL SERVERS
Timestamp: 2025-07-06 16:46:39 UTC
Target: Lambda Labs Production (165.1.69.44)
Registry: scoobyjava15
Environment: prod

## DEPLOYING ALL 20 MCP SERVERS TO LAMBDA LABS

### Critical Servers (Production Essential):
- **ai_memory** (Port: 9000) - 🔴 CRITICAL
- **codacy** (Port: 3008) - 🔴 CRITICAL
- **linear** (Port: 9004) - 🔴 CRITICAL
- **github** (Port: 9001) - 🔴 CRITICAL
- **slack_unified** (Port: 9002) - 🔴 CRITICAL
- **hubspot_unified** (Port: 9003) - 🔴 CRITICAL
- **snowflake_unified** (Port: 9005) - 🔴 CRITICAL

### Standard Servers (Extended Functionality):
- **notion** (Port: 9006) - 🟢 STANDARD
- **asana** (Port: 9007) - 🟢 STANDARD
- **lambda_labs_cli** (Port: 9008) - 🟢 STANDARD
- **postgres** (Port: 9009) - 🟢 STANDARD
- **pulumi** (Port: 9010) - 🟢 STANDARD
- **playwright** (Port: 9011) - 🟢 STANDARD
- **figma_context** (Port: 9012) - 🟢 STANDARD
- **ui_ux_agent** (Port: 9013) - 🟢 STANDARD
- **v0dev** (Port: 9014) - 🟢 STANDARD
- **intercom** (Port: 9015) - 🟢 STANDARD
- **apollo** (Port: 9016) - 🟢 STANDARD
- **bright_data** (Port: 9017) - 🟢 STANDARD
- **salesforce** (Port: 9018) - 🟢 STANDARD

## Deployment Configuration:
- **Registry**: scoobyjava15
- **Environment**: prod
- **Target Host**: 165.1.69.44
- **Deployment Method**: GitHub Actions Automated Pipeline
- **Docker Images**: sophia-[server]-mcp:latest format

## Expected Deployment Results:
- All 20 MCP servers built and pushed to registry
- All servers deployed to Lambda Labs production infrastructure
- Health endpoints active and monitored
- Production logging and monitoring enabled
- Automatic restart policies configured

## Health Check URLs (Post-Deployment):
- ai_memory: http://165.1.69.44:9000/health
- codacy: http://165.1.69.44:3008/health
- linear: http://165.1.69.44:9004/health
- github: http://165.1.69.44:9001/health
- slack_unified: http://165.1.69.44:9002/health
- hubspot_unified: http://165.1.69.44:9003/health
- snowflake_unified: http://165.1.69.44:9005/health
- notion: http://165.1.69.44:9006/health
- asana: http://165.1.69.44:9007/health
- lambda_labs_cli: http://165.1.69.44:9008/health
- postgres: http://165.1.69.44:9009/health
- pulumi: http://165.1.69.44:9010/health
- playwright: http://165.1.69.44:9011/health
- figma_context: http://165.1.69.44:9012/health
- ui_ux_agent: http://165.1.69.44:9013/health
- v0dev: http://165.1.69.44:9014/health
- intercom: http://165.1.69.44:9015/health
- apollo: http://165.1.69.44:9016/health
- bright_data: http://165.1.69.44:9017/health
- salesforce: http://165.1.69.44:9018/health
