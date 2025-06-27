# 🚀 Sophia AI Airbyte Integration Configuration Guide

This comprehensive guide provides both automated and manual configuration options for setting up Airbyte data integration with Gong and Slack sources flowing into Snowflake.

## 📋 Prerequisites

### Required Credentials
- **Snowflake**: Account, User, Password/Token, Role, Warehouse, Database
- **Gong**: Access Key, Secret Key
- **Slack**: Bot Token, Channel Access
- **Airbyte**: Client ID, Client Secret, Access Token

### Snowflake Configuration
```json
{
  "account": "UHDECNO-CVB64222",
  "user": "SCOOBYJAVA15", 
  "password": "[SOPHIA_AI_TOKEN]",
  "role": "ACCOUNTADMIN",
  "warehouse": "SOPHIA_AI_ANALYTICS_WH",
  "database": "SOPHIA_AI_CORE"
}
```

### Gong Configuration
```json
{
  "access_key": "TV33BPZ5UN45QKZCZ2UCAKRXHQ6Q3L5N",
  "secret": "[GONG_SECRET_TOKEN]"
}
```

## 🏗️ Infrastructure Setup Status

### ✅ Completed Infrastructure
- **Snowflake Schemas**: SOPHIA_GONG_RAW, SOPHIA_SLACK_RAW
- **Tables**: gong_calls, gong_transcripts, slack_messages, slack_channels
- **Airbyte-ready columns**: All tables include _airbyte_ab_id, _airbyte_emitted_at, _airbyte_normalized_at
- **Memory Integration**: SOPHIA_AI_MEMORY schema with unified views
- **Analytics Layer**: SOPHIA_SEMANTIC with cross-platform insights

## 🔧 Manual Airbyte Configuration

Since API authentication requires updated tokens, follow these manual steps:

### Step 1: Access Airbyte Cloud
1. Navigate to [https://cloud.airbyte.com/](https://cloud.airbyte.com/)
2. Login with: `lynn@payready.com` / `Huskers1983$`

### Step 2: Create Snowflake Destination
1. Go to **Destinations** → **+ New Destination**
2. Select **Snowflake**
3. Configure:
   ```
   Name: Sophia AI Snowflake
   Host: UHDECNO-CVB64222.snowflakecomputing.com
   Role: ACCOUNTADMIN
   Warehouse: SOPHIA_AI_ANALYTICS_WH
   Database: SOPHIA_AI_CORE
   Schema: PUBLIC
   Username: SCOOBYJAVA15
   Password: [Use PAT Token]
   ```

### Step 3: Create Gong Source
1. Go to **Sources** → **+ New Source**
2. Select **Gong**
3. Configure:
   ```
   Name: Sophia AI Gong
   Access Key: TV33BPZ5UN45QKZCZ2UCAKRXHQ6Q3L5N
   Access Key Secret: [GONG_SECRET]
   Start Date: 2024-01-01T00:00:00Z
   ```

### Step 4: Create Slack Source
1. Go to **Sources** → **+ New Source**
2. Select **Slack**
3. Configure:
   ```
   Name: Sophia AI Slack
   API Token: [SLACK_BOT_TOKEN]
   Start Date: 2024-01-01T00:00:00Z
   Join Channels: true
   Lookback Window: 1
   ```

### Step 5: Create Connections
1. **Gong to Snowflake**:
   - Source: Sophia AI Gong
   - Destination: Sophia AI Snowflake
   - Schedule: Every 6 hours
   - Destination Schema: SOPHIA_GONG_RAW

2. **Slack to Snowflake**:
   - Source: Sophia AI Slack
   - Destination: Sophia AI Snowflake
   - Schedule: Every 6 hours
   - Destination Schema: SOPHIA_SLACK_RAW

## 🔄 Data Flow Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    Gong     │───▶│   Airbyte   │───▶│  Snowflake  │
│   Calls     │    │ Integration │    │ GONG_RAW    │
│ Transcripts │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
                                               │
┌─────────────┐    ┌─────────────┐           ▼
│   Slack     │───▶│   Airbyte   │    ┌─────────────┐
│  Messages   │    │ Integration │───▶│  Snowflake  │
│  Channels   │    │             │    │ SLACK_RAW   │
└─────────────┘    └─────────────┘    └─────────────┘
                                               │
                                               ▼
                                    ┌─────────────┐
                                    │ AI_MEMORY   │
                                    │ Integration │
                                    │   Layer     │
                                    └─────────────┘
                                               │
                                               ▼
                                    ┌─────────────┐
                                    │  SEMANTIC   │
                                    │  Analytics  │
                                    │    Layer    │
                                    └─────────────┘
```

## 📊 Expected Data Tables

### Gong Tables (SOPHIA_GONG_RAW)
- **gong_calls**: Call metadata, participants, duration, recordings
- **gong_transcripts**: Speaker-level transcripts with sentiment analysis

### Slack Tables (SOPHIA_SLACK_RAW)
- **slack_messages**: Message content, channels, users, threads
- **slack_channels**: Channel metadata, member counts, topics

### Integration Views (SOPHIA_AI_MEMORY)
- **unified_conversations**: Cross-platform conversation aggregation
- **conversation_insights**: AI-generated insights and analysis

### Analytics Views (SOPHIA_SEMANTIC)
- **conversation_analytics**: Daily/weekly conversation metrics
- **cross_platform_insights**: Unified business intelligence

## 🧪 Testing and Validation

### Post-Setup Validation
1. **Check Data Flow**:
   ```sql
   -- Verify Gong data
   SELECT COUNT(*) FROM SOPHIA_GONG_RAW.gong_calls;
   SELECT COUNT(*) FROM SOPHIA_GONG_RAW.gong_transcripts;
   
   -- Verify Slack data
   SELECT COUNT(*) FROM SOPHIA_SLACK_RAW.slack_messages;
   SELECT COUNT(*) FROM SOPHIA_SLACK_RAW.slack_channels;
   
   -- Check integration views
   SELECT source_type, COUNT(*) 
   FROM SOPHIA_AI_MEMORY.unified_conversations 
   GROUP BY source_type;
   ```

2. **Monitor Sync Status**:
   - Check Airbyte dashboard for sync frequency and success rates
   - Verify data freshness in Snowflake tables
   - Monitor for any sync errors or failures

## 🔧 CLI Management Tools

### Snowflake Configuration Manager
```bash
# Sync schemas with GitHub
python3 scripts/snowflake_config_manager.py sync

# Get system status
python3 scripts/snowflake_config_manager.py status

# Optimize performance
python3 scripts/snowflake_config_manager.py optimize
```

### MCP Server Integration
The Snowflake Admin MCP Server (port 9012) provides programmatic access to:
- Schema synchronization
- Performance optimization
- Query execution
- System status monitoring

## 🚨 Troubleshooting

### Common Issues
1. **Authentication Failures**:
   - Verify PAT token is current and has proper permissions
   - Check Gong API credentials are active
   - Ensure Slack bot token has required scopes

2. **Schema Errors**:
   - Run schema sync: `python3 scripts/snowflake_config_manager.py sync`
   - Verify table structures match expected format
   - Check for column name conflicts

3. **Data Sync Issues**:
   - Monitor Airbyte connection logs
   - Verify source API rate limits
   - Check destination table permissions

## 📈 Performance Optimization

### Recommended Settings
- **Sync Frequency**: Every 6 hours for balanced performance
- **Clustering Keys**: Applied to timestamp and ID columns
- **Search Optimization**: Enabled for text content fields
- **Warehouse Auto-Suspend**: 5 minutes for cost optimization

## 🔒 Security Considerations

### Credential Management
- All credentials managed via Pulumi ESC and GitHub Secrets
- PAT tokens used for programmatic access
- API keys rotated regularly
- Access logs monitored for unusual activity

## 🎯 Next Steps

1. **Complete Manual Setup**: Follow steps 1-5 above
2. **Validate Data Flow**: Run test queries to verify data ingestion
3. **Monitor Performance**: Set up alerts for sync failures
4. **Integrate with AI**: Connect to Sophia AI memory and processing systems
5. **Scale Operations**: Adjust sync frequencies based on data volume

## 📞 Support

For technical issues:
- Check Airbyte documentation: [https://docs.airbyte.com/](https://docs.airbyte.com/)
- Snowflake support: [https://support.snowflake.com/](https://support.snowflake.com/)
- Gong API documentation: [https://us-66463.app.gong.io/settings/api/documentation](https://us-66463.app.gong.io/settings/api/documentation)

---

**Status**: Infrastructure Ready ✅ | Manual Configuration Required ⏳ | API Integration Pending 🔄

