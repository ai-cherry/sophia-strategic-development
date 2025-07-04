/**
 * Namecheap DNS Manager
 * Handles DNS record creation and management with IP context awareness
 */

import * as https from "https";
import * as querystring from "querystring";
import { IPContextDetector } from "./ip-context-detector";

export interface DNSRecord {
    domain: string;
    name: string;
    type: string;
    value: string;
    ttl: number;
}

export interface NamecheapAPIResponse {
    success: boolean;
    data?: any;
    error?: string;
    errors?: string[];
}

export interface NamecheapConfig {
    api_user: string;
    api_key: string;
    username: string;
    sandbox: boolean;
    endpoint: string;
    client_ip_detection: {
        local_dev: string;
        github_actions: string;
        pulumi_cloud: string;
        fallback: string;
    };
}

export class NamecheapDNSManager {
    private config: NamecheapConfig;
    private ipDetector: IPContextDetector;
    private clientIP: string;

    constructor(config: NamecheapConfig, ipDetector: IPContextDetector) {
        this.config = config;
        this.ipDetector = ipDetector;
        this.clientIP = this.ipDetector.getCurrentIP();

        console.log(`🔧 Namecheap DNS Manager initialized`);
        console.log(`🌐 Using client IP: ${this.clientIP}`);
    }

    /**
     * Create or update a DNS record
     */
    async createRecord(record: DNSRecord): Promise<NamecheapAPIResponse> {
        console.log(`📝 Creating DNS record: ${record.name}.${record.domain} → ${record.value}`);

        try {
            // First, get current host records
            const currentRecords = await this.getHostRecords(record.domain);

            // Add or update the record
            const updatedRecords = this.updateRecordInList(currentRecords, record);

            // Set all host records (Namecheap requires setting all at once)
            const result = await this.setHostRecords(record.domain, updatedRecords);

            if (result.success) {
                console.log(`  ✅ Successfully created/updated DNS record: ${record.name}.${record.domain}`);
            } else {
                console.error(`  ❌ Failed to create DNS record:`, result.error);
            }

            return result;

        } catch (error) {
            console.error(`  ❌ Error creating DNS record:`, error);
            return {
                success: false,
                error: error instanceof Error ? error.message : String(error)
            };
        }
    }

    /**
     * Get current host records for a domain
     */
    private async getHostRecords(domain: string): Promise<DNSRecord[]> {
        const params = {
            ApiUser: this.config.api_user,
            ApiKey: this.config.api_key,
            UserName: this.config.username,
            Command: "namecheap.domains.dns.getHosts",
            ClientIp: this.clientIP,
            SLD: domain.split('.')[0],
            TLD: domain.split('.').slice(1).join('.')
        };

        const response = await this.makeAPICall(params);

        if (response.success && response.data?.DomainDNSGetHostsResult?.host) {
            const hosts = Array.isArray(response.data.DomainDNSGetHostsResult.host)
                ? response.data.DomainDNSGetHostsResult.host
                : [response.data.DomainDNSGetHostsResult.host];

            return hosts.map((host: any) => ({
                domain: domain,
                name: host.Name,
                type: host.Type,
                value: host.Address,
                ttl: parseInt(host.TTL) || 300
            }));
        }

        return [];
    }

    /**
     * Set host records for a domain
     */
    private async setHostRecords(domain: string, records: DNSRecord[]): Promise<NamecheapAPIResponse> {
        const params: any = {
            ApiUser: this.config.api_user,
            ApiKey: this.config.api_key,
            UserName: this.config.username,
            Command: "namecheap.domains.dns.setHosts",
            ClientIp: this.clientIP,
            SLD: domain.split('.')[0],
            TLD: domain.split('.').slice(1).join('.')
        };

        // Add each record as numbered parameters
        records.forEach((record, index) => {
            const i = index + 1;
            params[`HostName${i}`] = record.name;
            params[`RecordType${i}`] = record.type;
            params[`Address${i}`] = record.value;
            params[`TTL${i}`] = record.ttl;
        });

        return await this.makeAPICall(params);
    }

    /**
     * Update or add a record in the existing records list
     */
    private updateRecordInList(existingRecords: DNSRecord[], newRecord: DNSRecord): DNSRecord[] {
        // Remove any existing record with the same name and type
        const filteredRecords = existingRecords.filter(
            record => !(record.name === newRecord.name && record.type === newRecord.type)
        );

        // Add the new record
        filteredRecords.push(newRecord);

        return filteredRecords;
    }

    /**
     * Make API call to Namecheap
     */
    private async makeAPICall(params: Record<string, any>): Promise<NamecheapAPIResponse> {
        return new Promise((resolve, reject) => {
            const queryParams = querystring.stringify(params);
            const url = `${this.config.endpoint}?${queryParams}`;

            console.log(`🌐 Making Namecheap API call from IP: ${this.clientIP}`);

            https.get(url, (res) => {
                let data = '';

                res.on('data', (chunk) => {
                    data += chunk;
                });

                res.on('end', () => {
                    try {
                        // Namecheap returns XML, we need to parse it
                        const result = this.parseNamecheapResponse(data);
                        resolve(result);
                    } catch (error) {
                        reject(error);
                    }
                });

            }).on('error', (error) => {
                console.error(`❌ Namecheap API call failed:`, error);
                reject(error);
            });
        });
    }

    /**
     * Parse Namecheap XML response
     */
    private parseNamecheapResponse(xmlData: string): NamecheapAPIResponse {
        // Simple XML parsing for Namecheap responses
        // In production, you might want to use a proper XML parser

        const isSuccess = xmlData.includes('Status="OK"');
        const hasError = xmlData.includes('<Errors>');

        if (isSuccess && !hasError) {
            return {
                success: true,
                data: this.extractDataFromXML(xmlData)
            };
        } else {
            const errors = this.extractErrorsFromXML(xmlData);
            return {
                success: false,
                error: errors.join(', '),
                errors: errors
            };
        }
    }

    /**
     * Extract data from XML response (simplified)
     */
    private extractDataFromXML(xmlData: string): any {
        // This is a simplified XML parser
        // In production, use a proper XML parsing library like xml2js
        try {
            // Extract host records if present
            const hostMatches = xmlData.match(/<host[^>]*>(.*?)<\/host>/gs);
            if (hostMatches) {
                const hosts = hostMatches.map(hostMatch => {
                    const name = this.extractXMLValue(hostMatch, 'Name');
                    const type = this.extractXMLValue(hostMatch, 'Type');
                    const address = this.extractXMLValue(hostMatch, 'Address');
                    const ttl = this.extractXMLValue(hostMatch, 'TTL');

                    return { Name: name, Type: type, Address: address, TTL: ttl };
                });

                return {
                    DomainDNSGetHostsResult: {
                        host: hosts.length === 1 ? hosts[0] : hosts
                    }
                };
            }

            return {};
        } catch (error) {
            console.warn('Failed to parse XML data:', error);
            return {};
        }
    }

    /**
     * Extract errors from XML response
     */
    private extractErrorsFromXML(xmlData: string): string[] {
        const errors: string[] = [];

        // Extract error messages
        const errorMatches = xmlData.match(/<Error Number="\d+">(.*?)<\/Error>/g);
        if (errorMatches) {
            errorMatches.forEach(errorMatch => {
                const message = errorMatch.replace(/<Error Number="\d+">(.*?)<\/Error>/, '$1');
                errors.push(message);
            });
        }

        return errors.length > 0 ? errors : ['Unknown API error'];
    }

    /**
     * Extract value from XML element
     */
    private extractXMLValue(xmlString: string, elementName: string): string {
        const match = xmlString.match(new RegExp(`${elementName}="([^"]*)"`, 'i'));
        return match ? match[1] : '';
    }

    /**
     * Validate API configuration
     */
    async validateConfiguration(): Promise<boolean> {
        try {
            console.log('🔍 Validating Namecheap API configuration...');

            const params = {
                ApiUser: this.config.api_user,
                ApiKey: this.config.api_key,
                UserName: this.config.username,
                Command: "namecheap.domains.getList",
                ClientIp: this.clientIP
            };

            const response = await this.makeAPICall(params);

            if (response.success) {
                console.log('  ✅ Namecheap API configuration is valid');
                return true;
            } else {
                console.error('  ❌ Namecheap API configuration is invalid:', response.error);
                return false;
            }

        } catch (error) {
            console.error('  ❌ Failed to validate Namecheap API configuration:', error);
            return false;
        }
    }
}
