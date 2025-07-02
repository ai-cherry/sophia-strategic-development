/**
 * Sophia AI - Monitoring Infrastructure Components
 * 
 * This module provides monitoring infrastructure components for the Sophia AI platform,
 * including CloudWatch dashboards, alarms, and custom metrics for ML workloads.
 */

import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import * as k8s from "@pulumi/kubernetes";

/**
 * Monitoring component arguments
 */
export interface MonitoringArgs {
    /**
     * Environment name (e.g., dev, staging, prod)
     */
    environment: string;
    
    /**
     * Resources to monitor
     */
    resources: {
        /**
         * EKS cluster name
         */
        eksClusterName?: string;
        
        /**
         * Auto Scaling Group names for ML workloads
         */
        mlAutoScalingGroups?: string[];
        
        /**
         * ElastiCache cluster IDs
         */
        elasticacheClusters?: string[];
        
        /**
         * S3 bucket names
         */
        s3Buckets?: string[];
        
        /**
         * Lambda function names
         */
        lambdaFunctions?: string[];
        
        /**
         * API Gateway names
         */
        apiGateways?: string[];
    };
    
    /**
     * Alerting configuration
     */
    alerting?: {
        /**
         * SNS topic ARN for alerts
         */
        snsTopicArn?: string;
        
        /**
         * Email addresses for alerts
         */
        emails?: string[];
        
        /**
         * Webhook URLs for alerts
         */
        webhooks?: string[];
    };
    
    /**
     * Kubernetes provider for Kubernetes monitoring
     */
    k8sProvider?: k8s.Provider;
    
    /**
     * Enable cost monitoring
     */
    enableCostMonitoring?: boolean;
    
    /**
     * Enable ML-specific monitoring (model performance, inference latency)
     */
    enableMlMonitoring?: boolean;
    
    /**
     * Tags to apply to all resources
     */
    tags?: { [key: string]: string };
}

/**
 * Monitoring threshold configuration
 */
export interface MonitoringThresholds {
    /**
     * CPU utilization threshold (percentage)
     */
    cpuUtilization: number;
    
    /**
     * Memory utilization threshold (percentage)
     */
    memoryUtilization: number;
    
    /**
     * GPU utilization threshold (percentage)
     */
    gpuUtilization: number;
    
    /**
     * Disk utilization threshold (percentage)
     */
    diskUtilization: number;
    
    /**
     * Model inference latency threshold (ms)
     */
    modelInferenceLatency: number;
    
    /**
     * API response time threshold (ms)
     */
    apiResponseTime: number;
    
    /**
     * Daily cost threshold (USD)
     */
    dailyCost: number;
}

/**
 * Monitoring infrastructure components
 */
export class MonitoringComponents extends pulumi.ComponentResource {
    /**
     * CloudWatch log groups
     */
    public readonly logGroups: aws.cloudwatch.LogGroup[];
    
    /**
     * CloudWatch dashboards
     */
    public readonly dashboards: {
        main: aws.cloudwatch.Dashboard;
        ml: aws.cloudwatch.Dashboard;
        cost: aws.cloudwatch.Dashboard;
    };
    
    /**
     * CloudWatch alarms
     */
    public readonly alarms: aws.cloudwatch.MetricAlarm[];
    
    /**
     * SNS topics for alerting
     */
    public readonly snsTopic: aws.sns.Topic;
    
    /**
     * CloudWatch Logs metrics filters
     */
    public readonly metricsFilters: aws.cloudwatch.LogMetricFilter[];
    
    /**
     * Prometheus resources (if Kubernetes provider is available)
     */
    public readonly prometheusResources?: {
        namespace: k8s.core.v1.Namespace;
        serviceAccount: k8s.core.v1.ServiceAccount;
        configMap: k8s.core.v1.ConfigMap;
        deployment: k8s.apps.v1.Deployment;
        service: k8s.core.v1.Service;
    };
    
    /**
     * ML metrics resources (if ML monitoring is enabled)
     */
    public readonly mlMetricsResources?: {
        logGroup: aws.cloudwatch.LogGroup;
        dashboard: aws.cloudwatch.Dashboard;
        alarms: aws.cloudwatch.MetricAlarm[];
    };
    
    /**
     * Cost monitoring resources (if cost monitoring is enabled)
     */
    public readonly costMonitoringResources?: {
        budgets: aws.budgets.Budget[];
        dashboard: aws.cloudwatch.Dashboard;
        alarms: aws.cloudwatch.MetricAlarm[];
    };
    
    constructor(name: string, args: MonitoringArgs, opts?: pulumi.ComponentResourceOptions) {
        super("sophia:monitoring:MonitoringComponents", name, {}, opts);
        
        // Assign default tags
        const tags = {
            Environment: args.environment,
            Project: "sophia-ai-platform",
            ManagedBy: "pulumi",
            Component: "monitoring",
            CreatedAt: new Date().toISOString(),
            ...args.tags,
        };
        
        // Initialize arrays
        this.logGroups = [];
        this.alarms = [];
        this.metricsFilters = [];
        
        // Create log groups
        const applicationLogGroup = new aws.cloudwatch.LogGroup(`${name}-application-logs`, {
            name: `/sophia-ai/${args.environment}/application`,
            retentionInDays: 30,
            tags: {
                ...tags,
                Name: `${name}-application-logs-${args.environment}`,
                Type: "ApplicationLogs",
            },
        }, { parent: this });
        
        const apiLogGroup = new aws.cloudwatch.LogGroup(`${name}-api-logs`, {
            name: `/sophia-ai/${args.environment}/api`,
            retentionInDays: 30,
            tags: {
                ...tags,
                Name: `${name}-api-logs-${args.environment}`,
                Type: "APILogs",
            },
        }, { parent: this });
        
        const mlLogGroup = new aws.cloudwatch.LogGroup(`${name}-ml-logs`, {
            name: `/sophia-ai/${args.environment}/ml`,
            retentionInDays: 30,
            tags: {
                ...tags,
                Name: `${name}-ml-logs-${args.environment}`,
                Type: "MLLogs",
            },
        }, { parent: this });
        
        this.logGroups.push(applicationLogGroup, apiLogGroup, mlLogGroup);
        
        // Create SNS topic for alerting
        this.snsTopic = new aws.sns.Topic(`${name}-alerts`, {
            name: `sophia-ai-${args.environment}-alerts`,
            tags: {
                ...tags,
                Name: `${name}-alerts-${args.environment}`,
                Type: "AlertingTopic",
            },
        }, { parent: this });
        
        // Create SNS subscriptions if alerting is configured
        if (args.alerting) {
            if (args.alerting.emails && args.alerting.emails.length > 0) {
                args.alerting.emails.forEach((email, i) => {
                    new aws.sns.TopicSubscription(`${name}-email-subscription-${i + 1}`, {
                        topic: this.snsTopic.arn,
                        protocol: "email",
                        endpoint: email,
                    }, { parent: this });
                });
            }
            
            if (args.alerting.webhooks && args.alerting.webhooks.length > 0) {
                args.alerting.webhooks.forEach((webhook, i) => {
                    new aws.sns.TopicSubscription(`${name}-webhook-subscription-${i + 1}`, {
                        topic: this.snsTopic.arn,
                        protocol: "https",
                        endpoint: webhook,
                    }, { parent: this });
                });
            }
        }
        
        // Create metrics filters for log groups
        
        // Error count metric filter
        const errorMetricFilter = new aws.cloudwatch.LogMetricFilter(`${name}-error-metric-filter`, {
            logGroupName: applicationLogGroup.name,
            name: `${args.environment}-error-count`,
            pattern: "ERROR",
            metricTransformation: {
                name: "ErrorCount",
                namespace: `SophiaAI/${args.environment}`,
                value: "1",
                defaultValue: 0,
            },
        }, { parent: this });
        
        // API latency metric filter
        const apiLatencyMetricFilter = new aws.cloudwatch.LogMetricFilter(`${name}-api-latency-metric-filter`, {
            logGroupName: apiLogGroup.name,
            name: `${args.environment}-api-latency`,
            pattern: "[time, requestId, latency]",
            metricTransformation: {
                name: "APILatency",
                namespace: `SophiaAI/${args.environment}`,
                value: "$latency",
                defaultValue: 0,
            },
        }, { parent: this });
        
        // ML model inference latency metric filter
        const mlLatencyMetricFilter = new aws.cloudwatch.LogMetricFilter(`${name}-ml-latency-metric-filter`, {
            logGroupName: mlLogGroup.name,
            name: `${args.environment}-ml-latency`,
            pattern: "[time, modelId, latency]",
            metricTransformation: {
                name: "ModelInferenceLatency",
                namespace: `SophiaAI/${args.environment}`,
                value: "$latency",
                defaultValue: 0,
            },
        }, { parent: this });
        
        // Model cold start metric filter
        const mlColdStartMetricFilter = new aws.cloudwatch.LogMetricFilter(`${name}-ml-cold-start-metric-filter`, {
            logGroupName: mlLogGroup.name,
            name: `${args.environment}-ml-cold-start`,
            pattern: "[time, modelId, coldStart=true, duration]",
            metricTransformation: {
                name: "ModelColdStartDuration",
                namespace: `SophiaAI/${args.environment}`,
                value: "$duration",
                defaultValue: 0,
            },
        }, { parent: this });
        
        this.metricsFilters.push(
            errorMetricFilter,
            apiLatencyMetricFilter,
            mlLatencyMetricFilter,
            mlColdStartMetricFilter
        );
        
        // Create CloudWatch alarms
        
        // Error rate alarm
        const errorRateAlarm = new aws.cloudwatch.MetricAlarm(`${name}-error-rate-alarm`, {
            alarmDescription: `High error rate in ${args.environment} environment`,
            comparisonOperator: "GreaterThanThreshold",
            evaluationPeriods: 2,
            metricName: "ErrorCount",
            namespace: `SophiaAI/${args.environment}`,
            period: 300,
            statistic: "Sum",
            threshold: 5,
            alarmActions: [this.snsTopic.arn],
            okActions: [this.snsTopic.arn],
            dimensions: {
                Environment: args.environment,
            },
            tags: {
                ...tags,
                Name: `${name}-error-rate-alarm-${args.environment}`,
                Type: "ErrorRateAlarm",
            },
        }, { parent: this });
        
        // API latency alarm
        const apiLatencyAlarm = new aws.cloudwatch.MetricAlarm(`${name}-api-latency-alarm`, {
            alarmDescription: `High API latency in ${args.environment} environment`,
            comparisonOperator: "GreaterThanThreshold",
            evaluationPeriods: 2,
            metricName: "APILatency",
            namespace: `SophiaAI/${args.environment}`,
            period: 300,
            statistic: "Average",
            threshold: 1000, // 1 second
            alarmActions: [this.snsTopic.arn],
            okActions: [this.snsTopic.arn],
            dimensions: {
                Environment: args.environment,
            },
            tags: {
                ...tags,
                Name: `${name}-api-latency-alarm-${args.environment}`,
                Type: "APILatencyAlarm",
            },
        }, { parent: this });
        
        // ML model inference latency alarm
        const mlLatencyAlarm = new aws.cloudwatch.MetricAlarm(`${name}-ml-latency-alarm`, {
            alarmDescription: `High ML model inference latency in ${args.environment} environment`,
            comparisonOperator: "GreaterThanThreshold",
            evaluationPeriods: 2,
            metricName: "ModelInferenceLatency",
            namespace: `SophiaAI/${args.environment}`,
            period: 300,
            statistic: "Average",
            threshold: 2000, // 2 seconds
            alarmActions: [this.snsTopic.arn],
            okActions: [this.snsTopic.arn],
            dimensions: {
                Environment: args.environment,
            },
            tags: {
                ...tags,
                Name: `${name}-ml-latency-alarm-${args.environment}`,
                Type: "MLLatencyAlarm",
            },
        }, { parent: this });
        
        this.alarms.push(
            errorRateAlarm,
            apiLatencyAlarm,
            mlLatencyAlarm
        );
        
        // Create resource-specific alarms if resources are provided
        
        // Monitor ML Auto Scaling Groups
        if (args.resources.mlAutoScalingGroups && args.resources.mlAutoScalingGroups.length > 0) {
            args.resources.mlAutoScalingGroups.forEach((asgName, i) => {
                const cpuAlarm = new aws.cloudwatch.MetricAlarm(`${name}-ml-asg-cpu-alarm-${i + 1}`, {
                    alarmDescription: `High CPU utilization for ML ASG ${asgName}`,
                    comparisonOperator: "GreaterThanThreshold",
                    evaluationPeriods: 2,
                    metricName: "CPUUtilization",
                    namespace: "AWS/EC2",
                    period: 300,
                    statistic: "Average",
                    threshold: 80,
                    alarmActions: [this.snsTopic.arn],
                    okActions: [this.snsTopic.arn],
                    dimensions: {
                        AutoScalingGroupName: asgName,
                    },
                    tags: {
                        ...tags,
                        Name: `${name}-ml-asg-cpu-alarm-${i + 1}-${args.environment}`,
                        Type: "ASGCPUAlarm",
                    },
                }, { parent: this });
                
                this.alarms.push(cpuAlarm);
            });
        }
        
        // Monitor ElastiCache clusters
        if (args.resources.elasticacheClusters && args.resources.elasticacheClusters.length > 0) {
            args.resources.elasticacheClusters.forEach((clusterId, i) => {
                const cpuAlarm = new aws.cloudwatch.MetricAlarm(`${name}-elasticache-cpu-alarm-${i + 1}`, {
                    alarmDescription: `High CPU utilization for ElastiCache cluster ${clusterId}`,
                    comparisonOperator: "GreaterThanThreshold",
                    evaluationPeriods: 2,
                    metricName: "CPUUtilization",
                    namespace: "AWS/ElastiCache",
                    period: 300,
                    statistic: "Average",
                    threshold: 80,
                    alarmActions: [this.snsTopic.arn],
                    okActions: [this.snsTopic.arn],
                    dimensions: {
                        CacheClusterId: clusterId,
                    },
                    tags: {
                        ...tags,
                        Name: `${name}-elasticache-cpu-alarm-${i + 1}-${args.environment}`,
                        Type: "ElastiCacheCPUAlarm",
                    },
                }, { parent: this });
                
                const memoryAlarm = new aws.cloudwatch.MetricAlarm(`${name}-elasticache-memory-alarm-${i + 1}`, {
                    alarmDescription: `High memory usage for ElastiCache cluster ${clusterId}`,
                    comparisonOperator: "GreaterThanThreshold",
                    evaluationPeriods: 2,
                    metricName: "DatabaseMemoryUsagePercentage",
                    namespace: "AWS/ElastiCache",
                    period: 300,
                    statistic: "Average",
                    threshold: 80,
                    alarmActions: [this.snsTopic.arn],
                    okActions: [this.snsTopic.arn],
                    dimensions: {
                        CacheClusterId: clusterId,
                    },
                    tags: {
                        ...tags,
                        Name: `${name}-elasticache-memory-alarm-${i + 1}-${args.environment}`,
                        Type: "ElastiCacheMemoryAlarm",
                    },
                }, { parent: this });
                
                this.alarms.push(cpuAlarm, memoryAlarm);
            });
        }
        
        // Create CloudWatch dashboards
        
        // Main dashboard
        const mainDashboardBody = {
            widgets: [
                {
                    type: "text",
                    x: 0,
                    y: 0,
                    width: 24,
                    height: 1,
                    properties: {
                        markdown: `# Sophia AI Platform - ${args.environment} Environment`,
                    },
                },
                {
                    type: "metric",
                    x: 0,
                    y: 1,
                    width: 12,
                    height: 6,
                    properties: {
                        view: "timeSeries",
                        stacked: false,
                        metrics: [
                            ["SophiaAI/" + args.environment, "ErrorCount"],
                        ],
                        region: "us-east-1",
                        title: "Error Count",
                    },
                },
                {
                    type: "metric",
                    x: 12,
                    y: 1,
                    width: 12,
                    height: 6,
                    properties: {
                        view: "timeSeries",
                        stacked: false,
                        metrics: [
                            ["SophiaAI/" + args.environment, "APILatency", "Environment", args.environment],
                        ],
                        region: "us-east-1",
                        title: "API Latency",
                    },
                },
                {
                    type: "log",
                    x: 0,
                    y: 7,
                    width: 24,
                    height: 6,
                    properties: {
                        query: `SOURCE '${applicationLogGroup.name}' | filter @message like /ERROR/\n| sort @timestamp desc\n| limit 20`,
                        region: "us-east-1",
                        title: "Recent Error Logs",
                        view: "table",
                    },
                },
            ],
        };
        
        const mainDashboard = new aws.cloudwatch.Dashboard(`${name}-main-dashboard`, {
            dashboardName: `sophia-ai-${args.environment}-main`,
            dashboardBody: JSON.stringify(mainDashboardBody),
        }, { parent: this });
        
        // ML dashboard
        const mlDashboardBody = {
            widgets: [
                {
                    type: "text",
                    x: 0,
                    y: 0,
                    width: 24,
                    height: 1,
                    properties: {
                        markdown: `# Sophia AI ML Performance - ${args.environment} Environment`,
                    },
                },
                {
                    type: "metric",
                    x: 0,
                    y: 1,
                    width: 12,
                    height: 6,
                    properties: {
                        view: "timeSeries",
                        stacked: false,
                        metrics: [
                            ["SophiaAI/" + args.environment, "ModelInferenceLatency", "Environment", args.environment],
                        ],
                        region: "us-east-1",
                        title: "Model Inference Latency",
                    },
                },
                {
                    type: "metric",
                    x: 12,
                    y: 1,
                    width: 12,
                    height: 6,
                    properties: {
                        view: "timeSeries",
                        stacked: false,
                        metrics: [
                            ["SophiaAI/" + args.environment, "ModelColdStartDuration", "Environment", args.environment],
                        ],
                        region: "us-east-1",
                        title: "Model Cold Start Duration",
                    },
                },
                {
                    type: "log",
                    x: 0,
                    y: 7,
                    width: 24,
                    height: 6,
                    properties: {
                        query: `SOURCE '${mlLogGroup.name}' | filter @message like /latency/\n| sort @timestamp desc\n| limit 20`,
                        region: "us-east-1",
                        title: "Recent ML Performance Logs",
                        view: "table",
                    },
                },
            ],
        };
        
        const mlDashboard = new aws.cloudwatch.Dashboard(`${name}-ml-dashboard`, {
            dashboardName: `sophia-ai-${args.environment}-ml`,
            dashboardBody: JSON.stringify(mlDashboardBody),
        }, { parent: this });
        
        // Cost dashboard (if cost monitoring is enabled)
        let costDashboard: aws.cloudwatch.Dashboard;
        let costMonitoringResources: {
            budgets: aws.budgets.Budget[];
            dashboard: aws.cloudwatch.Dashboard;
            alarms: aws.cloudwatch.MetricAlarm[];
        } | undefined;
        
        if (args.enableCostMonitoring) {
            const costDashboardBody = {
                widgets: [
                    {
                        type: "text",
                        x: 0,
                        y: 0,
                        width: 24,
                        height: 1,
                        properties: {
                            markdown: `# Sophia AI Cost Monitoring - ${args.environment} Environment`,
                        },
                    },
                    {
                        type: "metric",
                        x: 0,
                        y: 1,
                        width: 12,
                        height: 6,
                        properties: {
                            view: "timeSeries",
                            stacked: false,
                            metrics: [
                                ["AWS/Billing", "EstimatedCharges", "ServiceName", "AmazonECR"],
                                [".", ".", ".", "AmazonECS"],
                                [".", ".", ".", "AmazonEKS"],
                                [".", ".", ".", "AmazonEC2"],
                                [".", ".", ".", "AmazonS3"],
                            ],
                            region: "us-east-1",
                            title: "Estimated Charges by Service",
                        },
                    },
                    {
                        type: "metric",
                        x: 12,
                        y: 1,
                        width: 12,
                        height: 6,
                        properties: {
                            view: "timeSeries",
                            stacked: true,
                            metrics: [
                                ["AWS/Billing", "EstimatedCharges", "ServiceName", "AmazonECR", { label: "ECR" }],
                                [".", ".", ".", "AmazonECS", { label: "ECS" }],
                                [".", ".", ".", "AmazonEKS", { label: "EKS" }],
                                [".", ".", ".", "AmazonEC2", { label: "EC2" }],
                                [".", ".", ".", "AmazonS3", { label: "S3" }],
                                [".", ".", ".", "AmazonCloudWatch", { label: "CloudWatch" }],
                                [".", ".", ".", "AWSLambda", { label: "Lambda" }],
                                [".", ".", ".", "AmazonSNS", { label: "SNS" }],
                            ],
                            region: "us-east-1",
                            title: "Total Estimated Charges",
                        },
                    },
                ],
            };
            
            costDashboard = new aws.cloudwatch.Dashboard(`${name}-cost-dashboard`, {
                dashboardName: `sophia-ai-${args.environment}-cost`,
                dashboardBody: JSON.stringify(costDashboardBody),
            }, { parent: this });
            
            // Create cost budget
            const dailyBudget = new aws.budgets.Budget(`${name}-daily-budget`, {
                name: `sophia-ai-${args.environment}-daily-budget`,
                budgetType: "COST",
                limitAmount: "100", // $100 per day
                limitUnit: "USD",
                timePeriod: {
                    start: pulumi.interpolate`${new Date().toISOString().split("T")[0]}_00:00`,
                    end: pulumi.interpolate`${new Date(new Date().setFullYear(new Date().getFullYear() + 1)).toISOString().split("T")[0]}_00:00`,
                },
                timeUnit: "DAILY",
                
                // Notifications when 80% of budget is reached
                notifications: [{
                    comparisonOperator: "GREATER_THAN",
                    notificationType: "ACTUAL",
                    threshold: 80,
                    thresholdType: "PERCENTAGE",
                    subscriberEmailAddresses: args.alerting?.emails || [],
                }],
            }, { parent: this });
            
            // Create cost alarm
            const costAlarm = new aws.cloudwatch.MetricAlarm(`${name}-cost-alarm`, {
                alarmDescription: `Daily cost threshold exceeded for ${args.environment} environment`,
                comparisonOperator: "GreaterThanThreshold",
                evaluationPeriods: 1,
                metricName: "EstimatedCharges",
                namespace: "AWS/Billing",
                period: 86400, // 1 day
                statistic: "Maximum",
                threshold: 100, // $100
                alarmActions: [this.snsTopic.arn],
                okActions: [this.snsTopic.arn],
                dimensions: {
                    Currency: "USD",
                },
                tags: {
                    ...tags,
                    Name: `${name}-cost-alarm-${args.environment}`,
                    Type: "CostAlarm",
                },
            }, { parent: this });
            
            costMonitoringResources = {
                budgets: [dailyBudget],
                dashboard: costDashboard,
                alarms: [costAlarm],
            };
            
            this.alarms.push(costAlarm);
        }
        
        // Create ML-specific monitoring resources (if ML monitoring is enabled)
        let mlMetricsResources: {
            logGroup: aws.cloudwatch.LogGroup;
            dashboard: aws.cloudwatch.Dashboard;
            alarms: aws.cloudwatch.MetricAlarm[];
        } | undefined;
        
        if (args.enableMlMonitoring) {
            // Create ML metrics log group
            const mlMetricsLogGroup = new aws.cloudwatch.LogGroup(`${name}-ml-metrics-logs`, {
                name: `/sophia-ai/${args.environment}/ml-metrics`,
                retentionInDays: 30,
                tags: {
                    ...tags,
                    Name: `${name}-ml-metrics-logs-${args.environment}`,
                    Type: "MLMetricsLogs",
                },
            }, { parent: this });
            
            // Create ML metrics filters
            const modelAccuracyMetricFilter = new aws.cloudwatch.LogMetricFilter(`${name}-model-accuracy-metric-filter`, {
                logGroupName: mlMetricsLogGroup.name,
                name: `${args.environment}-model-accuracy`,
                pattern: "[time, modelId, accuracy]",
                metricTransformation: {
                    name: "ModelAccuracy",
                    namespace: `SophiaAI/${args.environment}/ML`,
                    value: "$accuracy",
                    defaultValue: 0,
                },
            }, { parent: this });
            
            const modelPrecisionMetricFilter = new aws.cloudwatch.LogMetricFilter(`${name}-model-precision-metric-filter`, {
                logGroupName: mlMetricsLogGroup.name,
                name: `${args.environment}-model-precision`,
                pattern: "[time, modelId, precision]",
                metricTransformation: {
                    name: "ModelPrecision",
                    namespace: `SophiaAI/${args.environment}/ML`,
                    value: "$precision",
                    defaultValue: 0,
                },
            }, { parent: this });
            
            const modelRecallMetricFilter = new aws.cloudwatch.LogMetricFilter(`${name}-model-recall-metric-filter`, {
                logGroupName: mlMetricsLogGroup.name,
                name: `${args.environment}-model-recall`,
                pattern: "[time, modelId, recall]",
                metricTransformation: {
                    name: "ModelRecall",
                    namespace: `SophiaAI/${args.environment}/ML`,
                    value: "$recall",
                    defaultValue: 0,
                },
            }, { parent: this });
            
            const modelF1MetricFilter = new aws.cloudwatch.LogMetricFilter(`${name}-model-f1-metric-filter`, {
                logGroupName: mlMetricsLogGroup.name,
                name: `${args.environment}-model-f1`,
                pattern: "[time, modelId, f1]",
                metricTransformation: {
                    name: "ModelF1",
                    namespace: `SophiaAI/${args.environment}/ML`,
                    value: "$f1",
                    defaultValue: 0,
                },
            }, { parent: this });
            
            this.metricsFilters.push(
                modelAccuracyMetricFilter,
                modelPrecisionMetricFilter,
                modelRecallMetricFilter,
                modelF1MetricFilter
            );
            
            // Create ML metrics dashboard
            const mlMetricsDashboardBody = {
                widgets: [
                    {
                        type: "text",
                        x: 0,
                        y: 0,
                        width: 24,
                        height: 1,
                        properties: {
                            markdown: `# Sophia AI ML Metrics - ${args.environment} Environment`,
                        },
                    },
                    {
                        type: "metric",
                        x: 0,
                        y: 1,
                        width: 8,
                        height: 6,
                        properties: {
                            view: "timeSeries",
                            stacked: false,
                            metrics: [
                                ["SophiaAI/" + args.environment + "/ML", "ModelAccuracy"],
                            ],
                            region: "us-east-1",
                            title: "Model Accuracy",
                        },
                    },
                    {
                        type: "metric",
                        x: 8,
                        y: 1,
                        width: 8,
                        height: 6,
                        properties: {
                            view: "timeSeries",
                            stacked: false,
                            metrics: [
                                ["SophiaAI/" + args.environment + "/ML", "ModelPrecision"],
                            ],
                            region: "us-east-1",
                            title: "Model Precision",
                        },
                    },
                    {
                        type: "metric",
                        x: 16,
                        y: 1,
                        width: 8,
                        height: 6,
                        properties: {
                            view: "timeSeries",
                            stacked: false,
                            metrics: [
                                ["SophiaAI/" + args.environment + "/ML", "ModelRecall"],
                            ],
                            region: "us-east-1",
                            title: "Model Recall",
                        },
                    },
                    {
                        type: "metric",
                        x: 0,
                        y: 7,
                        width: 8,
                        height: 6,
                        properties: {
                            view: "timeSeries",
                            stacked: false,
                            metrics: [
                                ["SophiaAI/" + args.environment + "/ML", "ModelF1"],
                            ],
                            region: "us-east-1",
                            title: "Model F1 Score",
                        },
                    },
                    {
                        type: "metric",
                        x: 8,
                        y: 7,
                        width: 8,
                        height: 6,
                        properties: {
                            view: "timeSeries",
                            stacked: false,
                            metrics: [
                                ["SophiaAI/" + args.environment, "ModelInferenceLatency"],
                            ],
                            region: "us-east-1",
                            title: "Model Inference Latency",
                        },
                    },
                    {
                        type: "metric",
                        x: 16,
                        y: 7,
                        width: 8,
                        height: 6,
                        properties: {
                            view: "timeSeries",
                            stacked: false,
                            metrics: [
                                ["SophiaAI/" + args.environment, "ModelColdStartDuration"],
                            ],
                            region: "us-east-1",
                            title: "Model Cold Start Duration",
                        },
                    },
                ],
            };
            
            const mlMetricsDashboard = new aws.cloudwatch.Dashboard(`${name}-ml-metrics-dashboard`, {
                dashboardName: `sophia-ai-${args.environment}-ml-metrics`,
                dashboardBody: JSON.stringify(mlMetricsDashboardBody),
            }, { parent: this });
            
            // Create ML metrics alarms
            const modelAccuracyAlarm = new aws.cloudwatch.MetricAlarm(`${name}-model-accuracy-alarm`, {
                alarmDescription: `Low model accuracy in ${args.environment} environment`,
                comparisonOperator: "LessThanThreshold",
                evaluationPeriods: 2,
                metricName: "ModelAccuracy",
                namespace: `SophiaAI/${args.environment}/ML`,
                period: 300,
                statistic: "Average",
                threshold: 0.8, // 80% accuracy
                alarmActions: [this.snsTopic.arn],
                okActions: [this.snsTopic.arn],
                dimensions: {
                    Environment: args.environment,
                },
                tags: {
                    ...tags,
                    Name: `${name}-model-accuracy-alarm-${args.environment}`,
                    Type: "ModelAccuracyAlarm",
                },
            }, { parent: this });
            
            const modelPrecisionAlarm = new aws.cloudwatch.MetricAlarm(`${name}-model-precision-alarm`, {
                alarmDescription: `Low model precision in ${args.environment} environment`,
                comparisonOperator: "LessThanThreshold",
                evaluationPeriods: 2,
                metricName: "ModelPrecision",
                namespace: `SophiaAI/${args.environment}/ML`,
                period: 300,
                statistic: "Average",
                threshold: 0.8, // 80% precision
                alarmActions: [this.snsTopic.arn],
                okActions: [this.snsTopic.arn],
                dimensions: {
                    Environment: args.environment,
                },
                tags: {
                    ...tags,
                    Name: `${name}-model-precision-alarm-${args.environment}`,
                    Type: "ModelPrecisionAlarm",
                },
            }, { parent: this });
            
            mlMetricsResources = {
                logGroup: mlMetricsLogGroup,
                dashboard: mlMetricsDashboard,
                alarms: [modelAccuracyAlarm, modelPrecisionAlarm],
            };
            
            this.logGroups.push(mlMetricsLogGroup);
            this.alarms.push(modelAccuracyAlarm, modelPrecisionAlarm);
        }
        
        // Create Prometheus resources for Kubernetes monitoring if k8sProvider is available
        let prometheusResources: {
            namespace: k8s.core.v1.Namespace;
            serviceAccount: k8s.core.v1.ServiceAccount;
            configMap: k8s.core.v1.ConfigMap;
            deployment: k8s.apps.v1.Deployment;
            service: k8s.core.v1.Service;
        } | undefined;
        
        if (args.k8sProvider) {
            // Create Prometheus namespace
            const prometheusNamespace = new k8s.core.v1.Namespace(`${name}-prometheus-namespace`, {
                metadata: {
                    name: "monitoring",
                    labels: {
                        name: "monitoring",
                    },
                },
            }, { provider: args.k8sProvider, parent: this });
            
            // Create Prometheus service account
            const prometheusServiceAccount = new k8s.core.v1.ServiceAccount(`${name}-prometheus-service-account`, {
                metadata: {
                    name: "prometheus",
                    namespace: prometheusNamespace.metadata.name,
                },
            }, { provider: args.k8sProvider, parent: this });
            
            // Create Prometheus config map
            const prometheusConfigMap = new k8s.core.v1.ConfigMap(`${name}-prometheus-config-map`, {
                metadata: {
                    name: "prometheus-config",
                    namespace: prometheusNamespace.metadata.name,
                },
                data: {
                    "prometheus.yml": `
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'kubernetes-apiservers'
    kubernetes_sd_configs:
    - role: endpoints
    scheme: https
    tls_config:
      ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
    relabel_configs:
    - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
      action: keep
      regex: default;kubernetes;https

  - job_name: 'kubernetes-nodes'
    kubernetes_sd_configs:
    - role: node
    scheme: https
    tls_config:
      ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
    relabel_configs:
    - action: labelmap
      regex: __meta_kubernetes_node_label_(.+)

  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
    - role: pod
    relabel_configs:
    - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
      action: keep
      regex: true
    - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
      action: replace
      target_label: __metrics_path__
      regex: (.+)
    - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
      action: replace
      regex: ([^:]+)(?::\\d+)?;(\\d+)
      replacement: $1:$2
      target_label: __address__
    - action: labelmap
      regex: __meta_kubernetes_pod_label_(.+)
    - source_labels: [__meta_kubernetes_namespace]
      action: replace
      target_label: kubernetes_namespace
    - source_labels: [__meta_kubernetes_pod_name]
      action: replace
      target_label: kubernetes_pod_name

  - job_name: 'ml-metrics'
    kubernetes_sd_configs:
    - role: pod
    relabel_configs:
    - source_labels: [__meta_kubernetes_pod_label_app]
      action: keep
      regex: sophia-ai-ml.*
    - action: labelmap
      regex: __meta_kubernetes_pod_label_(.+)
    - source_labels: [__meta_kubernetes_namespace]
      action: replace
      target_label: kubernetes_namespace
    - source_labels: [__meta_kubernetes_pod_name]
      action: replace
      target_label: kubernetes_pod_name
    `,
                },
            }, { provider: args.k8sProvider, parent: this });
            
            // Create Prometheus deployment
            const prometheusDeployment = new k8s.apps.v1.Deployment(`${name}-prometheus-deployment`, {
                metadata: {
                    name: "prometheus",
                    namespace: prometheusNamespace.metadata.name,
                    labels: {
                        app: "prometheus",
                    },
                },
                spec: {
                    replicas: 1,
                    selector: {
                        matchLabels: {
                            app: "prometheus",
                        },
                    },
                    template: {
                        metadata: {
                            labels: {
                                app: "prometheus",
                            },
                        },
                        spec: {
                            serviceAccountName: prometheusServiceAccount.metadata.name,
                            containers: [
                                {
                                    name: "prometheus",
                                    image: "prom/prometheus:v2.40.0",
                                    args: [
                                        "--config.file=/etc/prometheus/prometheus.yml",
                                        "--storage.tsdb.path=/prometheus",
                                        "--storage.tsdb.retention.time=15d",
                                        "--web.console.libraries=/usr/share/prometheus/console_libraries",
                                        "--web.console.templates=/usr/share/prometheus/consoles",
                                    ],
                                    ports: [
                                        {
                                            containerPort: 9090,
                                        },
                                    ],
                                    volumeMounts: [
                                        {
                                            name: "prometheus-config-volume",
                                            mountPath: "/etc/prometheus/",
                                        },
                                        {
                                            name: "prometheus-storage-volume",
                                            mountPath: "/prometheus/",
                                        },
                                    ],
                                    resources: {
                                        requests: {
                                            cpu: "500m",
                                            memory: "500Mi",
                                        },
                                        limits: {
                                            cpu: "1",
                                            memory: "1Gi",
                                        },
                                    },
                                },
                            ],
                            volumes: [
                                {
                                    name: "prometheus-config-volume",
                                    configMap: {
                                        defaultMode: 420,
                                        name: prometheusConfigMap.metadata.name,
                                    },
                                },
                                {
                                    name: "prometheus-storage-volume",
                                    emptyDir: {},
                                },
                            ],
                        },
                    },
                },
            }, { provider: args.k8sProvider, parent: this });
            
            // Create Prometheus service
            const prometheusService = new k8s.core.v1.Service(`${name}-prometheus-service`, {
                metadata: {
                    name: "prometheus",
                    namespace: prometheusNamespace.metadata.name,
                    annotations: {
                        "prometheus.io/scrape": "true",
                        "prometheus.io/port": "9090",
                    },
                },
                spec: {
                    selector: {
                        app: "prometheus",
                    },
                    ports: [
                        {
                            port: 9090,
                            targetPort: 9090,
                            name: "http",
                        },
                    ],
                },
            }, { provider: args.k8sProvider, parent: this });
            
            prometheusResources = {
                namespace: prometheusNamespace,
                serviceAccount: prometheusServiceAccount,
                configMap: prometheusConfigMap,
                deployment: prometheusDeployment,
                service: prometheusService,
            };
        }
        
        // Assign dashboards
        this.dashboards = {
            main: mainDashboard,
            ml: mlDashboard,
            cost: costDashboard!,
        };
        
        // Assign ML metrics resources
        this.mlMetricsResources = mlMetricsResources;
        
        // Assign cost monitoring resources
        this.costMonitoringResources = costMonitoringResources;
        
        // Assign Prometheus resources
        this.prometheusResources = prometheusResources;
        
        // Register outputs
        this.registerOutputs({
            logGroups: this.logGroups,
            dashboards: this.dashboards,
            alarms: this.alarms,
            snsTopic: this.snsTopic,
            metricsFilters: this.metricsFilters,
            prometheusResources: this.prometheusResources,
            mlMetricsResources: this.mlMetricsResources,
            costMonitoringResources: this.costMonitoringResources,
        });
    }
}

/**
 * Create CloudWatch dashboard for a specific component
 */
export function createComponentDashboard(
    name: string,
    environment: string,
    component: string,
    metrics: Array<{
        namespace: string;
        metricName: string;
        dimensions?: { [key: string]: string };
        statistic?: string;
        label?: string;
    }>,
    region: string = "us-east-1",
    parent?: pulumi.Resource,
): aws.cloudwatch.Dashboard {
    const widgets: any[] = [
        {
            type: "text",
            x: 0,
            y: 0,
            width: 24,
            height: 1,
            properties: {
                markdown: `# Sophia AI ${component} Dashboard - ${environment} Environment`,
            },
        },
    ];
    
    // Add metric widgets dynamically
    metrics.forEach((metric, i) => {
        const x = (i % 2) * 12;
        const y = Math.floor(i / 2) * 6 + 1;
        
        const metricConfig: any[] = [
            [
                metric.namespace,
                metric.metricName,
            ],
        ];
        
        // Add dimensions if present
        if (metric.dimensions) {
            Object.entries(metric.dimensions).forEach(([key, value]) => {
                metricConfig[0].push(key, value);
            });
        }
        
        // Add label if present
        if (metric.label) {
            metricConfig[0].push({ label: metric.label });
        }
        
        widgets.push({
            type: "metric",
            x,
            y,
            width: 12,
            height: 6,
            properties: {
                view: "timeSeries",
                stacked: false,
                metrics: metricConfig,
                region,
                title: metric.label || metric.metricName,
                stat: metric.statistic || "Average",
            },
        });
    });
    
    return new aws.cloudwatch.Dashboard(`${name}-${component}-dashboard`, {
        dashboardName: `sophia-ai-${environment}-${component}`,
        dashboardBody: JSON.stringify({ widgets }),
    }, { parent });
}

/**
 * Create CloudWatch alarm for a specific metric
 */
export function createMetricAlarm(
    name: string,
    metricName: string,
    namespace: string,
    environment: string,
    threshold: number,
    comparisonOperator: string,
    dimensions: { [key: string]: string },
    alarmDescription: string,
    snsTopicArn: pulumi.Input<string>,
    period: number = 300,
    evaluationPeriods: number = 2,
    statistic: string = "Average",
    tags?: { [key: string]: string },
    parent?: pulumi.Resource,
): aws.cloudwatch.MetricAlarm {
    return new aws.cloudwatch.MetricAlarm(`${name}-alarm`, {
        alarmDescription,
        comparisonOperator,
        evaluationPeriods,
        metricName,
        namespace,
        period,
        statistic,
        threshold,
        alarmActions: [snsTopicArn],
        okActions: [snsTopicArn],
        dimensions: {
            Environment: environment,
            ...dimensions,
        },
        tags,
    }, { parent });
}