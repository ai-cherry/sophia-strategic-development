/**
 * IP Context Detector
 * Determines which IP address to use based on execution environment
 * for Namecheap API whitelisting
 */

export interface IPAddresses {
    lambda_labs: string;
    github_actions: string;
    pulumi_cloud: string;
    whitelisted_ips: string[];
}

export interface ExecutionContext {
    environment: 'local_dev' | 'github_actions' | 'pulumi_cloud' | 'unknown';
    detectedIP: string;
    confidence: number;
    details: string;
}

export class IPContextDetector {
    private ipAddresses: IPAddresses;
    private context: ExecutionContext;

    constructor(ipAddresses: IPAddresses) {
        this.ipAddresses = ipAddresses;
        this.context = this.detectExecutionContext();

        console.log(`🔍 IP Context Detection Results:`);
        console.log(`  Environment: ${this.context.environment}`);
        console.log(`  Detected IP: ${this.context.detectedIP}`);
        console.log(`  Confidence: ${this.context.confidence}%`);
        console.log(`  Details: ${this.context.details}`);
    }

    /**
     * Get the current IP address to use for API calls
     */
    getCurrentIP(): string {
        return this.context.detectedIP;
    }

    /**
     * Get the execution context details
     */
    getContext(): ExecutionContext {
        return this.context;
    }

    /**
     * Detect the current execution environment and return appropriate IP
     */
    private detectExecutionContext(): ExecutionContext {
        // Check for GitHub Actions environment
        if (this.isGitHubActions()) {
            return {
                environment: 'github_actions',
                detectedIP: this.ipAddresses.github_actions,
                confidence: 95,
                details: 'GitHub Actions CI/CD environment detected'
            };
        }

        // Check for Pulumi Cloud environment
        if (this.isPulumiCloud()) {
            return {
                environment: 'pulumi_cloud',
                detectedIP: this.ipAddresses.pulumi_cloud,
                confidence: 90,
                details: 'Pulumi Cloud deployment environment detected'
            };
        }

        // Check for local Lambda Labs development
        if (this.isLocalDev()) {
            return {
                environment: 'local_dev',
                detectedIP: this.ipAddresses.lambda_labs,
                confidence: 85,
                details: 'Local development environment detected'
            };
        }

        // Fallback to Lambda Labs server
        return {
            environment: 'unknown',
            detectedIP: this.ipAddresses.lambda_labs,
            confidence: 60,
            details: 'Unknown environment, using Lambda Labs server IP as fallback'
        };
    }

    /**
     * Check if running in GitHub Actions
     */
    private isGitHubActions(): boolean {
        const indicators = [
            process.env.GITHUB_ACTIONS === 'true',
            process.env.CI === 'true' && process.env.GITHUB_REPOSITORY !== undefined,
            process.env.GITHUB_RUN_ID !== undefined,
            process.env.GITHUB_WORKFLOW !== undefined,
            process.env.RUNNER_OS !== undefined
        ];

        const matchCount = indicators.filter(Boolean).length;
        return matchCount >= 3; // Require at least 3 indicators for high confidence
    }

    /**
     * Check if running in Pulumi Cloud
     */
    private isPulumiCloud(): boolean {
        const indicators = [
            process.env.PULUMI_COMMAND !== undefined,
            process.env.PULUMI_ORGANIZATION !== undefined,
            process.env.PULUMI_STACK !== undefined,
            process.env.PULUMI_PROJECT !== undefined,
            // Check for Pulumi-specific environment variables
            process.env.PULUMI_CONFIG !== undefined,
            // Check if running in a containerized environment (common for Pulumi Cloud)
            process.env.KUBERNETES_SERVICE_HOST !== undefined,
            // Check for cloud deployment indicators
            process.env.AWS_REGION !== undefined || process.env.AZURE_LOCATION !== undefined
        ];

        const matchCount = indicators.filter(Boolean).length;
        return matchCount >= 2; // Require at least 2 indicators
    }

    /**
     * Check if running in local development environment
     */
    private isLocalDev(): boolean {
        const indicators = [
            // Local development typically has these characteristics
            process.env.USER !== undefined && process.env.HOME !== undefined,
            process.env.PWD !== undefined,
            // Not in CI/CD
            process.env.CI !== 'true',
            process.env.GITHUB_ACTIONS !== 'true',
            // Has local development tools
            process.env.TERM !== undefined,
            // Common local development environment variables
            process.env.LAMBDA_LABS_CONTEXT === 'true' || process.env.NODE_ENV === 'development'
        ];

        const matchCount = indicators.filter(Boolean).length;
        return matchCount >= 3;
    }

    /**
     * Validate that the selected IP is in the whitelist
     */
    validateIPWhitelist(): boolean {
        const currentIP = this.getCurrentIP();
        const isWhitelisted = this.ipAddresses.whitelisted_ips.includes(currentIP);

        if (!isWhitelisted) {
            console.warn(`⚠️  Current IP ${currentIP} is not in whitelist:`, this.ipAddresses.whitelisted_ips);
        } else {
            console.log(`✅ Current IP ${currentIP} is whitelisted for Namecheap API`);
        }

        return isWhitelisted;
    }

    /**
     * Get all available IP addresses and their contexts
     */
    getIPAddressMap(): Record<string, string> {
        return {
            'Local Development (Lambda Labs)': this.ipAddresses.lambda_labs,
            'GitHub Actions CI/CD': this.ipAddresses.github_actions,
            'Pulumi Cloud Deployment': this.ipAddresses.pulumi_cloud
        };
    }

    /**
     * Force a specific IP context (for testing or manual override)
     */
    overrideContext(environment: 'local_dev' | 'github_actions' | 'pulumi_cloud'): void {
        let detectedIP: string;
        let details: string;

        switch (environment) {
            case 'github_actions':
                detectedIP = this.ipAddresses.github_actions;
                details = 'Manually overridden to GitHub Actions IP';
                break;
            case 'pulumi_cloud':
                detectedIP = this.ipAddresses.pulumi_cloud;
                details = 'Manually overridden to Pulumi Cloud IP';
                break;
            case 'local_dev':
            default:
                detectedIP = this.ipAddresses.lambda_labs;
                details = 'Manually overridden to Lambda Labs IP';
                break;
        }

        this.context = {
            environment,
            detectedIP,
            confidence: 100,
            details
        };

        console.log(`🔧 IP context manually overridden:`);
        console.log(`  Environment: ${this.context.environment}`);
        console.log(`  IP: ${this.context.detectedIP}`);
    }

    /**
     * Get diagnostic information for troubleshooting
     */
    getDiagnostics(): Record<string, any> {
        return {
            context: this.context,
            environment_variables: {
                GITHUB_ACTIONS: process.env.GITHUB_ACTIONS,
                CI: process.env.CI,
                GITHUB_REPOSITORY: process.env.GITHUB_REPOSITORY,
                PULUMI_COMMAND: process.env.PULUMI_COMMAND,
                PULUMI_ORGANIZATION: process.env.PULUMI_ORGANIZATION,
                PULUMI_STACK: process.env.PULUMI_STACK,
                NODE_ENV: process.env.NODE_ENV,
                LAMBDA_LABS_CONTEXT: process.env.LAMBDA_LABS_CONTEXT,
                USER: process.env.USER,
                HOME: process.env.HOME
            },
            ip_addresses: this.ipAddresses,
            validation: {
                is_whitelisted: this.validateIPWhitelist(),
                available_ips: this.getIPAddressMap()
            }
        };
    }
} 