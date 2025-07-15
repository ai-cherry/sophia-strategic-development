/**
 * Sophia Intelligence Platform - DNS Infrastructure
 * Automated DNS management for sophia-intel.ai using Namecheap API
 * Integrates with Pulumi ESC for secret management and IP whitelisting
 */

import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import { NamecheapDNSManager } from "./namecheap-dns-manager";
import { IPContextDetector } from "./ip-context-detector";
import { DNSHealthChecker } from "./dns-health-checker";

// Load configuration from Pulumi ESC
const config = new pulumi.Config();
const stackConfig = pulumi.getStack();

// Get ESC configuration
const escConfig = config.requireObject("platform");
const ipAddresses = config.requireObject("ip_addresses");
const dnsConfig = config.requireObject("dns");
const namecheapConfig = config.requireObject("namecheap");
const sslConfig = config.requireObject("ssl");

/**
 * Main DNS Infrastructure Class
 */
export class SophiaIntelligenceDNS {
    private dnsManager: NamecheapDNSManager;
    private ipDetector: IPContextDetector;
    private healthChecker: DNSHealthChecker;
    private domain: string;
    private lambdaServerIP: string;

    constructor() {
        this.domain = escConfig.domain;
        this.lambdaServerIP = ipAddresses.lambda_labs;

        // Initialize components
        this.ipDetector = new IPContextDetector(ipAddresses);
        this.dnsManager = new NamecheapDNSManager(namecheapConfig, this.ipDetector);
        this.healthChecker = new DNSHealthChecker(dnsConfig.monitoring);

        console.log(`🚀 Initializing Sophia Intelligence DNS for domain: ${this.domain}`);
        console.log(`🎯 Lambda Labs Server IP: ${this.lambdaServerIP}`);
    }

    /**
     * Deploy all DNS infrastructure
     */
    async deploy(): Promise<void> {
        console.log("📡 Deploying DNS infrastructure...");

        try {
            // 1. Create DNS records
            await this.createDNSRecords();

            // 2. Set up SSL certificates
            await this.setupSSLCertificates();

            // 3. Configure health monitoring
            await this.setupHealthMonitoring();

            // 4. Validate deployment
            await this.validateDeployment();

            console.log("✅ DNS infrastructure deployment completed successfully");

        } catch (error) {
            console.error("❌ DNS deployment failed:", error);
            throw error;
        }
    }

    /**
     * Create all DNS records pointing to Lambda Labs server
     */
    private async createDNSRecords(): Promise<void> {
        console.log("🔧 Creating DNS records...");

        const records = dnsConfig.records;
        const createdRecords: string[] = [];

        // Create each DNS record
        for (const [recordKey, recordConfig] of Object.entries(records)) {
            try {
                const recordName = recordConfig.name === "@" ? this.domain : `${recordConfig.name}.${this.domain}`;

                await this.dnsManager.createRecord({
                    domain: this.domain,
                    name: recordConfig.name,
                    type: recordConfig.type,
                    value: recordConfig.value,
                    ttl: dnsConfig.ttl
                });

                createdRecords.push(recordName);
                console.log(`  ✅ Created ${recordConfig.type} record: ${recordName} → ${recordConfig.value}`);

            } catch (error) {
                console.error(`  ❌ Failed to create record ${recordKey}:`, error);
                throw error;
            }
        }

        // Export created records
        pulumi.all(createdRecords).apply(records => {
            return new pulumi.Output({
                domain: this.domain,
                lambdaServerIP: this.lambdaServerIP,
                createdRecords: records,
                recordsCount: records.length
            });
        });
    }

    /**
     * Set up SSL certificates for all domains
     */
    private async setupSSLCertificates(): Promise<void> {
        console.log("🔒 Setting up SSL certificates...");

        const sslDomains = sslConfig.domains;

        // Create ACM certificate request
        const certificate = new aws.acm.Certificate("sophia-intel-ssl-cert", {
            domainName: this.domain,
            subjectAlternativeNames: [
                `*.${this.domain}`, // Wildcard for all subdomains
                `api.${this.domain}`,
                `webhooks.${this.domain}`,
                `dashboard.${this.domain}`,
                `sophia.${this.domain}`,
                `dev.${this.domain}`
            ],
            validationMethod: "DNS",
            tags: {
                Name: `${this.domain}-ssl-certificate`,
                Environment: stackConfig,
                Project: "sophia-intelligence-platform",
                ManagedBy: "pulumi"
            }
        });

        // Export certificate details
        return pulumi.all([certificate.arn, certificate.domainName]).apply(([arn, domain]) => {
            console.log(`  ✅ SSL certificate created: ${domain} (${arn})`);
            return {
                certificateArn: arn,
                domain: domain,
                subjectAlternativeNames: certificate.subjectAlternativeNames
            };
        });
    }

    /**
     * Set up health monitoring for DNS records
     */
    private async setupHealthMonitoring(): Promise<void> {
        console.log("📊 Setting up DNS health monitoring...");

        const endpoints = dnsConfig.monitoring.ping_endpoints;
        const healthChecks: aws.route53.HealthCheck[] = [];

        for (const endpoint of endpoints) {
            const healthCheck = new aws.route53.HealthCheck(`health-check-${endpoint.replace(/[^a-zA-Z0-9]/g, '-')}`, {
                type: "HTTPS",
                fqdn: endpoint.replace("https://", ""),
                port: 443,
                requestInterval: 30,
                failureThreshold: 3,
                tags: {
                    Name: `Health check for ${endpoint}`,
                    Environment: stackConfig,
                    Project: "sophia-intelligence-platform"
                }
            });

            healthChecks.push(healthCheck);
        }

        // Set up CloudWatch alarms for health checks
        for (const healthCheck of healthChecks) {
            const alarm = new aws.cloudwatch.MetricAlarm(`dns-health-alarm-${healthCheck.id}`, {
                comparisonOperator: "LessThanThreshold",
                evaluationPeriods: 2,
                metricName: "HealthCheckStatus",
                namespace: "AWS/Route53",
                period: 60,
                statistic: "Minimum",
                threshold: 1,
                alarmDescription: `Health check alarm for ${healthCheck.fqdn}`,
                dimensions: {
                    HealthCheckId: healthCheck.id
                },
                tags: {
                    Environment: stackConfig,
                    Project: "sophia-intelligence-platform"
                }
            });
        }

        console.log(`  ✅ Created ${healthChecks.length} health checks with CloudWatch alarms`);
    }

    /**
     * Validate the deployment by checking DNS propagation
     */
    private async validateDeployment(): Promise<void> {
        console.log("🔍 Validating DNS deployment...");

        const validationResults = await this.healthChecker.validateDNSRecords({
            domain: this.domain,
            expectedIP: this.lambdaServerIP,
            subdomains: ["api", "webhooks", "dashboard", "sophia", "dev"],
            timeout: 30000
        });

        if (validationResults.allPassed) {
            console.log("  ✅ All DNS records validated successfully");
        } else {
            console.warn("  ⚠️  Some DNS records failed validation:", validationResults.failures);
        }

        return validationResults;
    }
}

/**
 * Deploy the infrastructure
 */
async function deployInfrastructure() {
    const dnsInfra = new SophiaIntelligenceDNS();
    await dnsInfra.deploy();
}

// Export key outputs
export const sophiaIntelDNSOutputs = pulumi.all([
    escConfig.domain,
    ipAddresses.lambda_labs,
    dnsConfig.records
]).apply(([domain, serverIP, records]) => ({
    domain: domain,
    lambdaServerIP: serverIP,
    dnsRecords: Object.keys(records).map(key => ({
        name: records[key].name === "@" ? domain : `${records[key].name}.${domain}`,
        type: records[key].type,
        value: records[key].value
    })),
    endpoints: {
        main: `https://${domain}`,
        api: `https://api.${domain}`,
        webhooks: `https://webhooks.${domain}`,
        dashboard: `https://dashboard.${domain}`,
        sophia: `https://sophia.${domain}`,
        dev: `https://dev.${domain}`
    },
    deployment: {
        timestamp: new Date().toISOString(),
        stack: stackConfig,
        environment: escConfig.environment
    }
}));

// Run deployment if this file is executed directly
if (require.main === module) {
    deployInfrastructure().catch(console.error);
}
