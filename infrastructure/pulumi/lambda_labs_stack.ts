"""TypeScript Pulumi stack for Lambda Labs hybrid infrastructure."""

import * as pulumi from "@pulumi/pulumi";  // type: ignore[import-not-found]
import * as aws from "@pulumi/aws";  // type: ignore[import-not-found]

// Configuration
const config = new pulumi.Config();
const environment = config.require("environment");
const lambdaApiKey = config.requireSecret("lambdaApiKey");
const slackWebhook = config.requireSecret("slackWebhook");

// S3 bucket for usage data backup
const usageBucket = new aws.s3.Bucket("lambda-labs-usage", {
    bucket: `sophia-ai-lambda-usage-${environment}`,
    acl: "private",
    versioning: {
        enabled: true,
    },
    lifecycleRules: [{
        enabled: true,
        transitions: [{
            days: 30,
            storageClass: "INTELLIGENT_TIERING",
        }],
    }],
    tags: {
        Name: "Lambda Labs Usage Data",
        Environment: environment,
        Project: "sophia-ai",
    },
});

// DynamoDB table for real-time usage tracking
const usageTable = new aws.dynamodb.Table("lambda-labs-usage", {
    name: `sophia-ai-lambda-usage-${environment}`,
    billingMode: "PAY_PER_REQUEST",
    hashKey: "requestId",
    rangeKey: "timestamp",
    attributes: [
        { name: "requestId", type: "S" },
        { name: "timestamp", type: "N" },
        { name: "userId", type: "S" },
        { name: "model", type: "S" },
    ],
    globalSecondaryIndexes: [
        {
            name: "userId-timestamp-index",
            hashKey: "userId",
            rangeKey: "timestamp",
            projectionType: "ALL",
        },
        {
            name: "model-timestamp-index",
            hashKey: "model",
            rangeKey: "timestamp",
            projectionType: "INCLUDE",
            nonKeyAttributes: ["cost", "tokens"],
        },
    ],
    pointInTimeRecovery: { enabled: true },
    tags: {
        Name: "Lambda Labs Usage Tracking",
        Environment: environment,
    },
});

// Lambda function for cost monitoring
const costMonitorFunction = new aws.lambda.Function("lambda-labs-cost-monitor", {
    runtime: "python3.11",
    code: new pulumi.asset.AssetArchive({
        ".": new pulumi.asset.FileArchive("./lambda_functions/cost_monitor"),
    }),
    handler: "index.handler",
    timeout: 60,
    memorySize: 256,
    environment: {
        variables: {
            USAGE_TABLE: usageTable.name,
            SLACK_WEBHOOK: slackWebhook,
            DAILY_BUDGET: "50",
            MONTHLY_BUDGET: "1000",
        },
    },
    tags: {
        Name: "Lambda Labs Cost Monitor",
        Environment: environment,
    },
});

// CloudWatch Events rule to run cost monitor every hour
const costMonitorSchedule = new aws.cloudwatch.EventRule("lambda-labs-cost-monitor-schedule", {
    description: "Trigger Lambda Labs cost monitor hourly",
    scheduleExpression: "rate(1 hour)",
});

const costMonitorTarget = new aws.cloudwatch.EventTarget("lambda-labs-cost-monitor-target", {
    rule: costMonitorSchedule.name,
    arn: costMonitorFunction.arn,
});

const costMonitorPermission = new aws.lambda.Permission("lambda-labs-cost-monitor-permission", {
    action: "lambda:InvokeFunction",
    function: costMonitorFunction.name,
    principal: "events.amazonaws.com",
    sourceArn: costMonitorSchedule.arn,
});

// CloudWatch dashboard
const dashboard = new aws.cloudwatch.Dashboard("lambda-labs-dashboard", {
    dashboardName: `sophia-ai-lambda-labs-${environment}`,
    dashboardBody: pulumi.interpolate`{
        "widgets": [
            {
                "type": "metric",
                "properties": {
                    "metrics": [
                        ["AWS/Lambda", "Invocations", {"stat": "Sum"}],
                        [".", "Errors", {"stat": "Sum"}],
                        [".", "Duration", {"stat": "Average"}]
                    ],
                    "period": 300,
                    "stat": "Average",
                    "region": "us-east-1",
                    "title": "Lambda Labs Cost Monitor"
                }
            }
        ]
    }`,
});

// Exports
export const usageBucketName = usageBucket.id;
export const usageTableName = usageTable.name;
export const costMonitorFunctionName = costMonitorFunction.name;
export const dashboardUrl = pulumi.interpolate`https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=${dashboard.dashboardName}`;
