# 🌐 Sophia Intelligence Platform - DNS Infrastructure

## Overview

This directory contains the complete DNS infrastructure automation for the Sophia Intelligence Platform, managing the `sophia-intel.ai` domain with enterprise-grade automation, security, and monitoring.

## 🎯 Features

- **Multi-Context IP Detection**: Automatically selects the correct IP address based on execution environment (GitHub Actions, Pulumi Cloud, Local Development)
- **Pulumi ESC Integration**: Seamless integration with Pulumi ESC for centralized secret management
- **Namecheap API Automation**: Full automation of DNS record creation and management
- **Health Monitoring**: Comprehensive DNS validation and endpoint health checking
- **SSL Certificate Management**: Automated SSL certificate provisioning via AWS ACM
- **GitHub Actions Workflow**: Complete CI/CD pipeline for DNS deployments
- **TypeScript + Python**: Dual implementation for flexibility and reliability

## 📋 Prerequisites

### Required Secrets (GitHub Organization Level)

These secrets must be configured in your GitHub Organization settings:

```bash
# IP Addresses for API Whitelisting
LAMBDA_IP_ADDRESS=170.9.9.253      # Lambda Labs production server
GH_IP_ADDRESS=140.82.112.2          # GitHub Actions CI/CD IP
PULUMI_IP_ADDRESS=34.74.88.2        # Pulumi Cloud deployment IP

# Namecheap API Credentials
NAMECHEAP_API_USER=your_api_user
NAMECHEAP_API_KEY=your_api_key
NAMECHEAP_USERNAME=your_username

# Additional Configuration
SSL_ADMIN_EMAIL=admin@sophia-intel.ai
ALERT_EMAIL=alerts@sophia-intel.ai
PULUMI_ACCESS_TOKEN=your_pulumi_token
```

### Tools Required

- **Node.js 18+** (for TypeScript infrastructure)
- **Python 3.11+** (for DNS management script)
- **Pulumi CLI** (for infrastructure deployment)
- **AWS CLI** (for SSL certificate management)

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone the repository
git clone https://github.com/ai-cherry/sophia-main.git
cd sophia-main/infrastructure/dns

# Install TypeScript dependencies
npm install

# Install Python dependencies (for script usage)
pip install requests python-dotenv aiohttp
```

### 2. Configure Pulumi ESC

Ensure your Pulumi ESC environment is properly configured:

```bash
# Set Pulumi organization
export PULUMI_ORG=scoobyjava-org

# Validate ESC configuration
pulumi env get $PULUMI_ORG/default/sophia-intelligence-platform --show-secrets
```

### 3. Deploy DNS Infrastructure

#### Option A: GitHub Actions (Recommended)

Push changes to trigger automated deployment:

```bash
git add .
git commit -m "Deploy DNS infrastructure"
git push origin main
```

Or trigger manual deployment:
- Go to GitHub Actions → "Deploy Sophia Intelligence DNS Infrastructure"
- Click "Run workflow"
- Select environment and domain
- Run deployment

#### Option B: Local Deployment

```bash
# TypeScript Infrastructure
npm run deploy

# Python DNS Management
python ../../scripts/dns-manager.py setup --domain sophia-intel.ai
```

## 📁 File Structure

```
infrastructure/dns/
├── README.md                          # This documentation
├── package.json                       # Node.js dependencies
├── tsconfig.json                      # TypeScript configuration
├── sophia-dns-infrastructure.ts       # Main infrastructure code
├── namecheap-dns-manager.ts           # Namecheap API integration
├── ip-context-detector.ts             # IP context detection
└── dns-health-checker.ts              # Health monitoring

infrastructure/esc/
└── sophia-intelligence-platform.yaml  # Pulumi ESC configuration

scripts/
└── dns-manager.py                     # Python DNS management script

.github/workflows/
└── deploy-sophia-dns.yml             # CI/CD workflow
```

## 🔧 Configuration Files

### Pulumi ESC Configuration

Located at `infrastructure/esc/sophia-intelligence-platform.yaml`:

```yaml
# IP Address Management (from GitHub Organization Secrets)
ip_addresses:
  lambda_labs:
    fn::secret: "${LAMBDA_IP_ADDRESS}"
  github_actions:
    fn::secret: "${GH_IP_ADDRESS}"
  pulumi_cloud:
    fn::secret: "${PULUMI_IP_ADDRESS}"

# DNS Configuration
dns:
  provider: "namecheap"
  domain: "sophia-intel.ai"
  records:
    root: { type: "A", value: "${ip_addresses.lambda_labs}", name: "@" }
    api: { type: "A", value: "${ip_addresses.lambda_labs}", name: "api" }
    webhooks: { type: "A", value: "${ip_addresses.lambda_labs}", name: "webhooks" }
    dashboard: { type: "A", value: "${ip_addresses.lambda_labs}", name: "dashboard" }
    sophia: { type: "A", value: "${ip_addresses.lambda_labs}", name: "sophia" }
    dev: { type: "A", value: "${ip_addresses.lambda_labs}", name: "dev" }
```

## 🛠️ Usage Examples

### TypeScript Infrastructure

```typescript
import { SophiaIntelligenceDNS } from './sophia-dns-infrastructure';

const dnsInfra = new SophiaIntelligenceDNS();
await dnsInfra.deploy();
```

### Python DNS Management

```bash
# Setup all DNS records
python scripts/dns-manager.py setup --domain sophia-intel.ai

# Validate DNS records
python scripts/dns-manager.py validate --domain sophia-intel.ai

# Check DNS manager status
python scripts/dns-manager.py status
```

### Manual DNS Operations

```typescript
import { NamecheapDNSManager, IPContextDetector } from './dns-components';

// Create DNS manager with context detection
const ipDetector = new IPContextDetector(ipAddresses);
const dnsManager = new NamecheapDNSManager(config, ipDetector);

// Create single DNS record
await dnsManager.createRecord({
  domain: "sophia-intel.ai",
  name: "api",
  type: "A",
  value: "170.9.9.253",
  ttl: 300
});
```

## 🏥 Health Monitoring

### DNS Health Checks

```typescript
import { DNSHealthChecker } from './dns-health-checker';

const healthChecker = new DNSHealthChecker(monitoringConfig);

// Validate all DNS records
const results = await healthChecker.validateDNSRecords({
  domain: "sophia-intel.ai",
  expectedIP: "170.9.9.253",
  subdomains: ["api", "webhooks", "dashboard", "sophia", "dev"],
  timeout: 30000
});

// Check endpoint health
const endpoints = [
  "https://sophia-intel.ai",
  "https://api.sophia-intel.ai",
  "https://dashboard.sophia-intel.ai"
];

const healthResults = await healthChecker.checkEndpointHealth(endpoints);
```

### Monitoring Dashboard

Access health monitoring through:
- DNS validation reports in GitHub Actions
- CloudWatch alarms for Route 53 health checks
- Comprehensive health scoring system

## 🔐 Security Features

### IP Whitelisting

The system automatically detects execution context and uses the appropriate IP:

- **GitHub Actions**: Uses `GH_IP_ADDRESS` (140.82.112.2)
- **Pulumi Cloud**: Uses `PULUMI_IP_ADDRESS` (34.74.88.2)
- **Local Development**: Uses `LAMBDA_IP_ADDRESS` (170.9.9.253)

### Secret Management

- All secrets managed through GitHub Organization secrets
- Automatic synchronization with Pulumi ESC
- No hardcoded credentials anywhere
- Encrypted secret storage and transmission

### SSL/TLS

- Automatic SSL certificate provisioning via AWS ACM
- Wildcard certificate for all subdomains
- DNS validation method for certificate issuance

## 📊 Monitoring & Alerting

### Health Checks

1. **DNS Propagation Monitoring**
   - Validates all DNS records point to correct IP
   - Monitors DNS resolution times
   - Detects DNS changes over time

2. **Endpoint Health Monitoring**
   - HTTPS endpoint availability
   - Response time monitoring
   - Status code validation

3. **Infrastructure Health**
   - AWS Route 53 health checks
   - CloudWatch alarms and metrics
   - Automated alert notifications

### Metrics Tracked

- DNS resolution time (<100ms target)
- Endpoint response time (<2s target)
- SSL certificate expiration
- DNS record consistency
- Overall health score (0-100)

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

The automated deployment pipeline includes:

1. **Context Detection** - Determines environment and IP context
2. **Pulumi ESC Validation** - Validates configuration and secrets
3. **DNS Validation** - Checks current DNS state
4. **Infrastructure Deployment** - Deploys TypeScript infrastructure
5. **DNS Record Deployment** - Creates/updates DNS records
6. **Post-Deployment Validation** - Validates deployment success
7. **Notification** - Sends deployment status notifications

### Deployment Environments

- **Production**: Automatic deployment on `main` branch push
- **Staging**: Manual deployment for testing
- **Development**: Validation-only mode for pull requests

## 🐛 Troubleshooting

### Common Issues

#### DNS Records Not Updating

```bash
# Check Namecheap API connectivity
python scripts/dns-manager.py status

# Validate IP context detection
python -c "
from scripts.dns_manager import IPContextDetector
detector = IPContextDetector({'lambda_labs': '170.9.9.253'})
print(detector.detect_context())
"

# Force specific IP context
export LAMBDA_LABS_CONTEXT=true
python scripts/dns-manager.py setup --domain sophia-intel.ai
```

#### SSL Certificate Issues

```bash
# Check certificate status
aws acm list-certificates --region us-east-1

# Validate domain validation records
dig _acme-challenge.sophia-intel.ai TXT
```

#### Pulumi ESC Configuration Issues

```bash
# Validate ESC access
pulumi whoami
pulumi env get scoobyjava-org/default/sophia-intelligence-platform

# Check secret availability
pulumi config get LAMBDA_IP_ADDRESS --stack scoobyjava-org/default/sophia-intelligence-platform
```

### Debug Mode

Enable debug logging:

```bash
# TypeScript
DEBUG=true npm run deploy

# Python
export DEBUG=1
python scripts/dns-manager.py setup --domain sophia-intel.ai
```

## 📚 API Reference

### TypeScript Classes

#### `SophiaIntelligenceDNS`
Main infrastructure deployment class.

```typescript
class SophiaIntelligenceDNS {
  constructor()
  async deploy(): Promise<void>
  private async createDNSRecords(): Promise<void>
  private async setupSSLCertificates(): Promise<void>
  private async setupHealthMonitoring(): Promise<void>
  private async validateDeployment(): Promise<void>
}
```

#### `NamecheapDNSManager`
Namecheap API integration.

```typescript
class NamecheapDNSManager {
  constructor(config: NamecheapConfig, ipDetector: IPContextDetector)
  async createRecord(record: DNSRecord): Promise<NamecheapAPIResponse>
  async validateConfiguration(): Promise<boolean>
}
```

#### `IPContextDetector`
Execution environment detection.

```typescript
class IPContextDetector {
  constructor(ipAddresses: IPAddresses)
  getCurrentIP(): string
  getContext(): ExecutionContext
  overrideContext(environment: string): void
}
```

#### `DNSHealthChecker`
Health monitoring and validation.

```typescript
class DNSHealthChecker {
  constructor(config: MonitoringConfig)
  async validateDNSRecords(request: DNSValidationRequest): Promise<DNSValidationResult>
  async checkEndpointHealth(urls: string[]): Promise<EndpointHealthResult[]>
  async runComprehensiveHealthCheck(): Promise<HealthCheckResult>
}
```

### Python Classes

#### `SophiaDNSManager`
Main DNS management class.

```python
class SophiaDNSManager:
  def __init__(self)
  async def initialize(self) -> None
  async def setup_domain_records(self, domain: str, server_ip: str) -> bool
  async def validate_dns_records(self, domain: str, expected_ip: str) -> List[Dict]
```

## 🎯 Roadmap

### Planned Features

- [ ] **Multi-Domain Support** - Support for additional domains
- [ ] **Advanced Health Checks** - Custom health check endpoints
- [ ] **Geo-DNS Support** - Geographic DNS routing
- [ ] **CDN Integration** - CloudFlare/AWS CloudFront integration
- [ ] **Advanced Monitoring** - Grafana dashboards
- [ ] **Disaster Recovery** - Automated failover scenarios

### Version History

- **v1.0.0** - Initial DNS infrastructure with Namecheap integration
- **v1.1.0** - Added health monitoring and SSL automation
- **v1.2.0** - Enhanced GitHub Actions workflow and Python script

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📞 Support

For issues and questions:

- **GitHub Issues**: [Create an issue](https://github.com/ai-cherry/sophia-main/issues)
- **Documentation**: Check this README and inline code comments
- **Discord**: Join the Sophia AI community Discord

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ by the Sophia AI Team**

*Transforming Pay Ready into a unified AI-driven organization through intelligent infrastructure automation.* 