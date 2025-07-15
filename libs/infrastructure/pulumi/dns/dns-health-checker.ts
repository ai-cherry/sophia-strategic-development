/**
 * DNS Health Checker
 * Validates DNS record propagation and monitors endpoint health
 */

import * as dns from "dns";
import * as https from "https";
import { promisify } from "util";

const dnsResolve4 = promisify(dns.resolve4);
const dnsResolveTxt = promisify(dns.resolveTxt);

export interface DNSValidationRequest {
    domain: string;
    expectedIP: string;
    subdomains: string[];
    timeout: number;
}

export interface DNSValidationResult {
    domain: string;
    allPassed: boolean;
    results: DomainValidationResult[];
    failures: string[];
    summary: {
        totalChecked: number;
        passed: number;
        failed: number;
    };
}

export interface DomainValidationResult {
    hostname: string;
    expectedIP: string;
    actualIPs: string[];
    isValid: boolean;
    responseTime: number;
    error?: string;
}

export interface EndpointHealthResult {
    url: string;
    isHealthy: boolean;
    responseTime: number;
    statusCode?: number;
    error?: string;
}

export interface MonitoringConfig {
    dns_health_check: boolean;
    ping_endpoints: string[];
    alert_email: string;
}

export class DNSHealthChecker {
    private config: MonitoringConfig;

    constructor(config: MonitoringConfig) {
        this.config = config;
        console.log(`🏥 DNS Health Checker initialized`);
        console.log(`  Health checks enabled: ${config.dns_health_check}`);
        console.log(`  Monitoring ${config.ping_endpoints.length} endpoints`);
    }

    /**
     * Validate DNS records for domain and subdomains
     */
    async validateDNSRecords(request: DNSValidationRequest): Promise<DNSValidationResult> {
        console.log(`🔍 Validating DNS records for ${request.domain}...`);

        const results: DomainValidationResult[] = [];
        const failures: string[] = [];

        // Check root domain
        const rootResult = await this.checkSingleDomain(request.domain, request.expectedIP, request.timeout);
        results.push(rootResult);
        if (!rootResult.isValid) {
            failures.push(`Root domain ${request.domain}: ${rootResult.error || 'IP mismatch'}`);
        }

        // Check subdomains
        for (const subdomain of request.subdomains) {
            const hostname = `${subdomain}.${request.domain}`;
            const subdomainResult = await this.checkSingleDomain(hostname, request.expectedIP, request.timeout);
            results.push(subdomainResult);

            if (!subdomainResult.isValid) {
                failures.push(`Subdomain ${hostname}: ${subdomainResult.error || 'IP mismatch'}`);
            }
        }

        const passed = results.filter(r => r.isValid).length;
        const failed = results.filter(r => !r.isValid).length;

        const validationResult: DNSValidationResult = {
            domain: request.domain,
            allPassed: failures.length === 0,
            results,
            failures,
            summary: {
                totalChecked: results.length,
                passed,
                failed
            }
        };

        console.log(`  📊 Validation Summary:`);
        console.log(`    Total checked: ${validationResult.summary.totalChecked}`);
        console.log(`    Passed: ${validationResult.summary.passed}`);
        console.log(`    Failed: ${validationResult.summary.failed}`);

        return validationResult;
    }

    /**
     * Check a single domain's DNS resolution
     */
    private async checkSingleDomain(hostname: string, expectedIP: string, timeout: number): Promise<DomainValidationResult> {
        const startTime = Date.now();

        try {
            console.log(`  🔍 Checking ${hostname}...`);

            // Set up timeout
            const timeoutPromise = new Promise<never>((_, reject) => {
                setTimeout(() => reject(new Error('DNS resolution timeout')), timeout);
            });

            // Resolve DNS
            const resolvePromise = dnsResolve4(hostname);
            const actualIPs = await Promise.race([resolvePromise, timeoutPromise]);

            const responseTime = Date.now() - startTime;
            const isValid = actualIPs.includes(expectedIP);

            const result: DomainValidationResult = {
                hostname,
                expectedIP,
                actualIPs,
                isValid,
                responseTime
            };

            if (isValid) {
                console.log(`    ✅ ${hostname} → ${actualIPs.join(', ')} (${responseTime}ms)`);
            } else {
                console.log(`    ❌ ${hostname} → Expected: ${expectedIP}, Got: ${actualIPs.join(', ')} (${responseTime}ms)`);
                result.error = `Expected IP ${expectedIP} but got ${actualIPs.join(', ')}`;
            }

            return result;

        } catch (error) {
            const responseTime = Date.now() - startTime;
            const errorMessage = error instanceof Error ? error.message : String(error);

            console.log(`    ❌ ${hostname} → Error: ${errorMessage} (${responseTime}ms)`);

            return {
                hostname,
                expectedIP,
                actualIPs: [],
                isValid: false,
                responseTime,
                error: errorMessage
            };
        }
    }

    /**
     * Check health of HTTP/HTTPS endpoints
     */
    async checkEndpointHealth(urls: string[]): Promise<EndpointHealthResult[]> {
        console.log(`🌐 Checking health of ${urls.length} endpoints...`);

        const results: EndpointHealthResult[] = [];

        for (const url of urls) {
            const result = await this.checkSingleEndpoint(url);
            results.push(result);
        }

        const healthy = results.filter(r => r.isHealthy).length;
        const unhealthy = results.filter(r => !r.isHealthy).length;

        console.log(`  📊 Endpoint Health Summary:`);
        console.log(`    Total checked: ${results.length}`);
        console.log(`    Healthy: ${healthy}`);
        console.log(`    Unhealthy: ${unhealthy}`);

        return results;
    }

    /**
     * Check health of a single endpoint
     */
    private async checkSingleEndpoint(url: string): Promise<EndpointHealthResult> {
        const startTime = Date.now();

        return new Promise((resolve) => {
            console.log(`  🔍 Checking ${url}...`);

            const request = https.get(url, { timeout: 10000 }, (res) => {
                const responseTime = Date.now() - startTime;
                const isHealthy = res.statusCode !== undefined && res.statusCode >= 200 && res.statusCode < 400;

                const result: EndpointHealthResult = {
                    url,
                    isHealthy,
                    responseTime,
                    statusCode: res.statusCode
                };

                if (isHealthy) {
                    console.log(`    ✅ ${url} → ${res.statusCode} (${responseTime}ms)`);
                } else {
                    console.log(`    ❌ ${url} → ${res.statusCode} (${responseTime}ms)`);
                    result.error = `HTTP ${res.statusCode}`;
                }

                resolve(result);
            });

            request.on('error', (error) => {
                const responseTime = Date.now() - startTime;
                console.log(`    ❌ ${url} → Error: ${error.message} (${responseTime}ms)`);

                resolve({
                    url,
                    isHealthy: false,
                    responseTime,
                    error: error.message
                });
            });

            request.on('timeout', () => {
                const responseTime = Date.now() - startTime;
                console.log(`    ❌ ${url} → Timeout (${responseTime}ms)`);

                request.destroy();
                resolve({
                    url,
                    isHealthy: false,
                    responseTime,
                    error: 'Request timeout'
                });
            });
        });
    }

    /**
     * Run comprehensive health check
     */
    async runComprehensiveHealthCheck(domain: string, expectedIP: string, subdomains: string[]): Promise<{
        dns: DNSValidationResult;
        endpoints: EndpointHealthResult[];
        overall: {
            isHealthy: boolean;
            score: number;
            issues: string[];
        };
    }> {
        console.log(`🏥 Running comprehensive health check for ${domain}...`);

        // DNS validation
        const dnsResult = await this.validateDNSRecords({
            domain,
            expectedIP,
            subdomains,
            timeout: 30000
        });

        // Endpoint health checks
        const endpointResults = await this.checkEndpointHealth(this.config.ping_endpoints);

        // Calculate overall health
        const dnsScore = dnsResult.allPassed ? 50 : (dnsResult.summary.passed / dnsResult.summary.totalChecked) * 50;
        const endpointScore = endpointResults.length > 0
            ? (endpointResults.filter(r => r.isHealthy).length / endpointResults.length) * 50
            : 0;

        const overallScore = Math.round(dnsScore + endpointScore);
        const isHealthy = overallScore >= 80;

        const issues: string[] = [];
        if (!dnsResult.allPassed) {
            issues.push(...dnsResult.failures);
        }
        endpointResults.filter(r => !r.isHealthy).forEach(r => {
            issues.push(`Endpoint ${r.url}: ${r.error || 'Unhealthy'}`);
        });

        console.log(`📊 Overall Health Score: ${overallScore}/100 ${isHealthy ? '✅' : '❌'}`);
        if (issues.length > 0) {
            console.log(`🚨 Issues found:`);
            issues.forEach(issue => console.log(`  - ${issue}`));
        }

        return {
            dns: dnsResult,
            endpoints: endpointResults,
            overall: {
                isHealthy,
                score: overallScore,
                issues
            }
        };
    }

    /**
     * Monitor DNS changes over time
     */
    async monitorDNSChanges(domain: string, intervalSeconds: number = 300): Promise<void> {
        console.log(`📊 Starting DNS monitoring for ${domain} (interval: ${intervalSeconds}s)`);

        let previousIPs: Record<string, string[]> = {};

        const monitor = async () => {
            try {
                const currentIPs = await dnsResolve4(domain);
                const currentIPsStr = currentIPs.sort().join(',');
                const previousIPsStr = (previousIPs[domain] || []).sort().join(',');

                if (currentIPsStr !== previousIPsStr) {
                    console.log(`🔄 DNS change detected for ${domain}:`);
                    console.log(`  Previous: ${previousIPsStr || 'none'}`);
                    console.log(`  Current: ${currentIPsStr}`);

                    previousIPs[domain] = currentIPs;
                } else {
                    console.log(`✅ DNS stable for ${domain}: ${currentIPsStr}`);
                }

            } catch (error) {
                console.error(`❌ DNS monitoring error for ${domain}:`, error);
            }
        };

        // Initial check
        await monitor();

        // Set up monitoring interval
        setInterval(monitor, intervalSeconds * 1000);
    }

    /**
     * Generate health report
     */
    generateHealthReport(domain: string, results: DNSValidationResult, endpoints: EndpointHealthResult[]): string {
        const timestamp = new Date().toISOString();

        let report = `# DNS Health Report - ${domain}\n`;
        report += `Generated: ${timestamp}\n\n`;

        report += `## DNS Validation Summary\n`;
        report += `- Total checked: ${results.summary.totalChecked}\n`;
        report += `- Passed: ${results.summary.passed}\n`;
        report += `- Failed: ${results.summary.failed}\n`;
        report += `- Overall: ${results.allPassed ? '✅ PASS' : '❌ FAIL'}\n\n`;

        if (results.failures.length > 0) {
            report += `## DNS Issues\n`;
            results.failures.forEach(failure => {
                report += `- ${failure}\n`;
            });
            report += '\n';
        }

        report += `## DNS Records\n`;
        results.results.forEach(result => {
            report += `- ${result.hostname}: ${result.actualIPs.join(', ')} (${result.responseTime}ms) ${result.isValid ? '✅' : '❌'}\n`;
        });

        if (endpoints.length > 0) {
            report += `\n## Endpoint Health\n`;
            endpoints.forEach(endpoint => {
                report += `- ${endpoint.url}: ${endpoint.statusCode || 'ERROR'} (${endpoint.responseTime}ms) ${endpoint.isHealthy ? '✅' : '❌'}\n`;
            });
        }

        return report;
    }
}
