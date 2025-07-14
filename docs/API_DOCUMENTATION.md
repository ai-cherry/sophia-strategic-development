---
title: Sophia AI - Comprehensive API Documentation
description:
tags: security, gong, monitoring
last_updated: 2025-07-04
dependencies: none
related_docs: none
---

# Sophia AI - Comprehensive API Documentation


## Table of Contents

- [🚀 **Overview**](#🚀-**overview**)
- [🔐 **Authentication**](#🔐-**authentication**)
  - [**1. API Key Authentication**](#**1.-api-key-authentication**)
  - [**2. OAuth 2.0 (Recommended)**](#**2.-oauth-2.0-(recommended)**)
- [📋 **Core Endpoints**](#📋-**core-endpoints**)
  - [**Natural Language Query**](#**natural-language-query**)
  - [**Health Check**](#**health-check**)
- [🏗️ **Infrastructure Endpoints**](#🏗️-**infrastructure-endpoints**)
  - [**Secret Management**](#**secret-management**)
  - [**Configuration Management**](#**configuration-management**)
- [🤖 **Claude Integration Endpoints**](#🤖-**claude-integration-endpoints**)
  - [**Code Generation**](#**code-generation**)
  - [**Code Analysis**](#**code-analysis**)
- [📊 **Service-Specific Endpoints**](#📊-**service-specific-endpoints**)
  - [**Gong Integration**](#**gong-integration**)
  - [**Modern Stack Integration**](#**snowflake-integration**)
  - [**Vercel Integration**](#**vercel-integration**)
- [🔄 **Webhook Endpoints**](#🔄-**webhook-endpoints**)
  - [**GitHub Webhooks**](#**github-webhooks**)
  - [**Slack Webhooks**](#**slack-webhooks**)
- [📈 **Monitoring Endpoints**](#📈-**monitoring-endpoints**)
  - [**Metrics**](#**metrics**)
  - [**Logs**](#**logs**)
- [🚨 **Error Handling**](#🚨-**error-handling**)
  - [**Common Error Codes**](#**common-error-codes**)
- [📝 **Usage Examples**](#📝-**usage-examples**)
  - [**Natural Language Infrastructure Management**](#**natural-language-infrastructure-management**)
  - [**Code Generation with Claude**](#**code-generation-with-claude**)
  - [**Data Analysis with Modern Stack**](#**data-analysis-with-snowflake**)
- [🔧 **SDK and Libraries**](#🔧-**sdk-and-libraries**)
  - [**Python SDK**](#**python-sdk**)
  - [**JavaScript SDK**](#**javascript-sdk**)
- [📚 **Additional Resources**](#📚-**additional-resources**)

## 🚀 **Overview**

The Sophia AI API provides comprehensive access to all integrated services through a unified natural language interface. This documentation covers all endpoints, authentication, and usage examples.

## 🔐 **Authentication**

All API endpoints require authentication using one of the following methods:

### **1. API Key Authentication**
```bash
# Example usage:
bash
```python

### **2. OAuth 2.0 (Recommended)**
```bash
# Example usage:
bash
```python

## 📋 **Core Endpoints**

### **Natural Language Query**
Process natural language requests and route to appropriate services.

**Endpoint:** `POST /api/natural-query`

**Request:**
```json
# Example usage:
json
```python

**Response:**
```json
# Example usage:
json
```python

### **Health Check**
Check the health status of all integrated services.

**Endpoint:** `GET /api/health`

**Response:**
```json
# Example usage:
json
```python

## 🏗️ **Infrastructure Endpoints**

### **Secret Management**
Manage secrets through Pulumi ESC integration.

**Get Secret:** `GET /api/secrets/{service}/{key}`
**Set Secret:** `POST /api/secrets/{service}/{key}`
**Rotate Secrets:** `POST /api/secrets/rotate/{service}`

### **Configuration Management**
Manage service configurations.

**Get Config:** `GET /api/config/{service}`
**Update Config:** `PUT /api/config/{service}`
**Validate Config:** `POST /api/config/{service}/validate`

## 🤖 **Claude Integration Endpoints**

### **Code Generation**
Generate code using Claude AI.

**Endpoint:** `POST /api/claude/generate-code`

**Request:**
```json
# Example usage:
json
```python

### **Code Analysis**
Analyze code for issues and improvements.

**Endpoint:** `POST /api/claude/analyze-code`

**Request:**
```json
# Example usage:
json
```python

## 📊 **Service-Specific Endpoints**

### **Gong Integration**
Access Gong CRM data and functionality.

- `GET /api/gong/calls` - Get call recordings
- `GET /api/gong/deals` - Get deal information
- `GET /api/gong/users` - Get user data
- `POST /api/gong/search` - Search across Gong data

### **Modern Stack Integration**
Execute queries and manage Modern Stack resources.

- `POST /api/snowflake/query` - Execute SQL queries
- `GET /api/snowflake/tables` - List available tables
- `GET /api/snowflake/schema` - Get schema information

### **Vercel Integration**
Manage deployments and projects.

- `GET /api/vercel/deployments` - List deployments
- `POST /api/vercel/deploy` - Create new deployment
- `GET /api/vercel/projects` - List projects


## 🧠 Lambda GPU Endpoints

### **Embedding Generation**
Generate vector embeddings using Cortex AI.

**Endpoint:** `POST /api/cortex/embed`

**Request:**
```json
{
  "text": "Text to embed",
  "model": "e5-base-v2"
}
```

**Response:**
```json
{
  "embedding": [0.123, -0.456, ...],
  "model": "e5-base-v2",
  "dimensions": 768
}
```

### **Text Completion**
Generate text completions using Cortex models.

**Endpoint:** `POST /api/cortex/complete`

**Request:**
```json
{
  "prompt": "Complete this text",
  "model": "mixtral-8x7b",
  "max_tokens": 100
}
```

## 🔄 **Webhook Endpoints**

### **GitHub Webhooks**
Handle GitHub events for automated workflows.

**Endpoint:** `POST /api/webhooks/github`

### **Slack Webhooks**
Process Slack events and commands.

**Endpoint:** `POST /api/webhooks/slack`

## 📈 **Monitoring Endpoints**

### **Metrics**
Get system performance metrics.

**Endpoint:** `GET /api/metrics`

### **Logs**
Access system logs with filtering.

**Endpoint:** `GET /api/logs?service={service}&level={level}&since={timestamp}`

## 🚨 **Error Handling**

All endpoints return standardized error responses:

```json
# Example usage:
json
```python

### **Common Error Codes**
- `INVALID_REQUEST` (400) - Request validation failed
- `UNAUTHORIZED` (401) - Authentication required
- `FORBIDDEN` (403) - Insufficient permissions
- `NOT_FOUND` (404) - Resource not found
- `RATE_LIMITED` (429) - Too many requests
- `INTERNAL_ERROR` (500) - Server error
- `SERVICE_UNAVAILABLE` (503) - Service temporarily unavailable

## 📝 **Usage Examples**

### **Natural Language Infrastructure Management**
```bash
# Example usage:
bash
```python

### **Code Generation with Claude**
```bash
# Example usage:
bash
```python

### **Data Analysis with Modern Stack**
```bash
# Example usage:
bash
```python

## 🔧 **SDK and Libraries**

### **Python SDK**
```python
# Example usage:
python
```python

### **JavaScript SDK**
```javascript
# Example usage:
javascript
```python

## 📚 **Additional Resources**

- **Interactive API Explorer**: https://api.sophia.ai/docs
- **Postman Collection**: [Download](https://api.sophia.ai/postman)
- **OpenAPI Specification**: [Download](https://api.sophia.ai/openapi.json)
- **Rate Limits**: 1000 requests/hour for free tier, 10000/hour for pro
- **Support**: support@sophia.ai
- **Status Page**: https://status.sophia.ai
