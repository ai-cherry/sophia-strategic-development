# Sophia AI Infrastructure as Code Configuration
# Terraform configuration for centralized infrastructure management
# Integrates Lambda Labs, Snowflake, and Estuary Flow

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> 5.0"
    }
    http = {
      source  = "hashicorp/http"
      version = "~> 3.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }
  
  backend "remote" {
    organization = "sophia-ai"
    workspaces {
      name = "infrastructure-production"
    }
  }
}

# Variables for infrastructure configuration
variable "lambda_api_key" {
  description = "Lambda Labs API key"
  type        = string
  sensitive   = true
}

variable "estuary_access_token" {
  description = "Estuary Flow access token"
  type        = string
  sensitive   = true
}

variable "snowflake_account" {
  description = "Snowflake account identifier"
  type        = string
  default     = "ZNB04675"
}

variable "github_token" {
  description = "GitHub API token for organization secrets"
  type        = string
  sensitive   = true
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "production"
}

# Local values for configuration
locals {
  project_name = "sophia-ai"
  environment  = var.environment
  
  # Infrastructure configuration
  lambda_config = {
    region        = "us-west-1"
    instance_type = "gpu_1x_a10"
    storage_size  = 500
  }
  
  # Database configuration
  postgresql_config = {
    version         = "15"
    port           = 5432
    database_name  = "sophia_staging"
    username       = "sophia_user"
    max_connections = 100
  }
  
  # Redis configuration
  redis_config = {
    port               = 6379
    max_memory         = "2gb"
    max_memory_policy  = "allkeys-lru"
  }
  
  # Snowflake configuration
  snowflake_config = {
    account   = var.snowflake_account
    user      = "PROGRAMMATIC_SERVICE_USER"
    role      = "SYSADMIN"
    warehouse = "COMPUTE_WH"
    database  = "SOPHIA_AI"
    schema    = "PUBLIC"
  }
  
  # Common tags
  common_tags = {
    Project     = local.project_name
    Environment = local.environment
    ManagedBy   = "terraform"
    Owner       = "sophia-ai-team"
  }
}

# Generate SSH key pair for Lambda Labs instances
resource "tls_private_key" "lambda_ssh_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

# Generate secure passwords
resource "random_password" "postgresql_password" {
  length  = 32
  special = true
}

resource "random_password" "redis_password" {
  length  = 32
  special = false
}

# Lambda Labs instance configuration
data "http" "lambda_instance_types" {
  url = "https://cloud.lambdalabs.com/api/v1/instance-types"
  
  request_headers = {
    Authorization = "Bearer ${var.lambda_api_key}"
  }
}

# Create Lambda Labs instance (using HTTP API calls)
resource "null_resource" "lambda_instance" {
  triggers = {
    instance_config = jsonencode(local.lambda_config)
  }
  
  provisioner "local-exec" {
    command = <<-EOT
      python3 ${path.module}/lambda-labs-deployment.py \
        --api-key "${var.lambda_api_key}" \
        --ssh-key "${tls_private_key.lambda_ssh_key.private_key_pem}" \
        --region "${local.lambda_config.region}" \
        --instance-type "${local.lambda_config.instance_type}" \
        --postgresql-password "${random_password.postgresql_password.result}" \
        --redis-password "${random_password.redis_password.result}"
    EOT
    
    environment = {
      LAMBDA_API_KEY = var.lambda_api_key
    }
  }
}

# GitHub Organization Secrets management
resource "github_actions_organization_secret" "infrastructure_secrets" {
  for_each = {
    # Lambda Labs secrets
    LAMBDA_API_KEY         = var.lambda_api_key
    LAMBDA_SSH_PRIVATE_KEY = tls_private_key.lambda_ssh_key.private_key_pem
    LAMBDA_SSH_PUBLIC_KEY  = tls_private_key.lambda_ssh_key.public_key_openssh
    
    # Database secrets
    POSTGRESQL_PASSWORD = random_password.postgresql_password.result
    REDIS_PASSWORD     = random_password.redis_password.result
    
    # Estuary Flow secrets
    ESTUARY_FLOW_ACCESS_TOKEN = var.estuary_access_token
    ESTUARY_FLOW_TENANT      = "sophia-ai"
    
    # Snowflake secrets
    SNOWFLAKE_ACCOUNT = local.snowflake_config.account
    SNOWFLAKE_USER    = local.snowflake_config.user
    SOPHIA_AI_TOKEN   = "eyJraWQiOiIxNzAwMTAwMDk2OSIsImFsZyI6IkVTMjU2In0.eyJwIjoiNjY0MTAwNjg6MTcwMDA5NTYyOTMiLCJpc3MiOiJTRjozMDAxIiwiZXhwIjoxNzU4MzkyMDc4fQ.HPlaOkJGlckJ8W8-GWt8lw0t8kIyvO6UctKrrv7d-kwjCOd5kveyKMspcFGIyuzKzS8X26BtDQQctk2LybXJOQ."
    SNOWFLAKE_ROLE      = local.snowflake_config.role
    SNOWFLAKE_WAREHOUSE = local.snowflake_config.warehouse
    SNOWFLAKE_DATABASE  = local.snowflake_config.database
    SNOWFLAKE_SCHEMA    = local.snowflake_config.schema
  }
  
  secret_name     = each.key
  plaintext_value = each.value
  visibility      = "all"
}

# Pulumi ESC configuration file generation
resource "local_file" "pulumi_esc_config" {
  filename = "${path.module}/generated-esc-config.yaml"
  
  content = templatefile("${path.module}/templates/esc-config.yaml.tpl", {
    project_name = local.project_name
    environment  = local.environment
    
    # Infrastructure configuration
    lambda_config     = local.lambda_config
    postgresql_config = local.postgresql_config
    redis_config      = local.redis_config
    snowflake_config  = local.snowflake_config
    
    # Generated secrets
    postgresql_password = random_password.postgresql_password.result
    redis_password     = random_password.redis_password.result
    ssh_private_key    = tls_private_key.lambda_ssh_key.private_key_pem
  })
}

# Estuary Flow configuration
resource "local_file" "estuary_flow_config" {
  filename = "${path.module}/generated-estuary-config.json"
  
  content = jsonencode({
    tenant      = "sophia-ai"
    api_url     = "https://api.estuary.dev"
    access_token = var.estuary_access_token
    
    sources = {
      hubspot = {
        connector_type = "source-hubspot"
        config = {
          start_date = "2024-01-01T00:00:00Z"
          credentials = {
            api_key = "$${HUBSPOT_API_KEY}"
          }
        }
        streams = [
          "contacts",
          "companies", 
          "deals",
          "engagements",
          "owners",
          "pipelines"
        ]
      }
      
      gong = {
        connector_type = "source-gong"
        config = {
          start_date = "2024-01-01T00:00:00Z"
          credentials = {
            access_key        = "$${GONG_ACCESS_KEY}"
            access_key_secret = "$${GONG_CLIENT_SECRET}"
          }
        }
        streams = [
          "calls",
          "users",
          "workspaces",
          "call_transcripts",
          "answered_scorecards"
        ]
      }
      
      slack = {
        connector_type = "source-slack"
        config = {
          start_date = "2024-01-01T00:00:00Z"
          credentials = {
            api_token = "$${SLACK_BOT_TOKEN}"
          }
          channel_filter = ["general", "engineering", "sales", "marketing"]
        }
        streams = [
          "channels",
          "channel_members",
          "messages",
          "users",
          "threads"
        ]
      }
    }
    
    destinations = {
      postgresql = {
        connector_type = "destination-postgres"
        config = {
          host     = "$${POSTGRESQL_HOST}"
          port     = local.postgresql_config.port
          database = local.postgresql_config.database_name
          username = local.postgresql_config.username
          password = "$${POSTGRESQL_PASSWORD}"
          ssl_mode = "require"
          schema_mapping = {
            hubspot = "hubspot_raw"
            gong    = "gong_raw"
            slack   = "slack_raw"
          }
        }
      }
      
      snowflake = {
        connector_type = "destination-snowflake"
        config = {
          account   = local.snowflake_config.account
          user      = local.snowflake_config.user
          password  = "$${SOPHIA_AI_TOKEN}"
          role      = local.snowflake_config.role
          warehouse = local.snowflake_config.warehouse
          database  = local.snowflake_config.database
          schema    = "PROCESSED_DATA"
        }
      }
    }
    
    flows = [
      {
        name        = "hubspot-to-postgresql"
        source      = "hubspot"
        destination = "postgresql"
        transforms = [
          "add_ingestion_metadata",
          "data_quality_checks"
        ]
      },
      {
        name        = "gong-to-postgresql"
        source      = "gong"
        destination = "postgresql"
        transforms = [
          "add_ingestion_metadata",
          "sentiment_analysis"
        ]
      },
      {
        name        = "slack-to-postgresql"
        source      = "slack"
        destination = "postgresql"
        transforms = [
          "add_ingestion_metadata",
          "channel_filtering"
        ]
      },
      {
        name        = "postgresql-to-snowflake"
        source      = "postgresql"
        destination = "snowflake"
        transforms = [
          "data_unification",
          "schema_normalization"
        ]
      }
    ]
  })
}

# Infrastructure monitoring configuration
resource "local_file" "monitoring_config" {
  filename = "${path.module}/generated-monitoring-config.yaml"
  
  content = yamlencode({
    monitoring = {
      health_checks = {
        postgresql = {
          endpoint = "http://$${LAMBDA_IP_ADDRESS}:8080/health"
          interval = "60s"
          timeout  = "10s"
        }
        redis = {
          endpoint = "redis://$${REDIS_HOST}:${local.redis_config.port}"
          interval = "60s"
          timeout  = "5s"
        }
        estuary_flow = {
          endpoint = "https://api.estuary.dev/v1/health"
          interval = "300s"
          timeout  = "30s"
        }
        snowflake = {
          query    = "SELECT 1"
          interval = "300s"
          timeout  = "30s"
        }
      }
      
      alerts = {
        channels = [
          {
            type = "slack"
            webhook_url = "$${SLACK_WEBHOOK_URL}"
          },
          {
            type = "email"
            recipients = ["alerts@sophia-ai.com"]
          }
        ]
        
        rules = [
          {
            name        = "Database Connection Failure"
            condition   = "postgresql.status != 'healthy'"
            severity    = "critical"
            description = "PostgreSQL database is not responding"
          },
          {
            name        = "Data Pipeline Failure"
            condition   = "estuary_flow.last_success > 1h"
            severity    = "high"
            description = "Estuary Flow pipeline has not succeeded in over 1 hour"
          },
          {
            name        = "Snowflake Query Performance"
            condition   = "snowflake.query_time > 30s"
            severity    = "medium"
            description = "Snowflake queries are taking longer than expected"
          }
        ]
      }
    }
  })
}

# Output important configuration values
output "infrastructure_summary" {
  description = "Summary of deployed infrastructure"
  value = {
    project_name = local.project_name
    environment  = local.environment
    
    lambda_config = {
      region        = local.lambda_config.region
      instance_type = local.lambda_config.instance_type
    }
    
    database_config = {
      postgresql_port = local.postgresql_config.port
      postgresql_db   = local.postgresql_config.database_name
      redis_port      = local.redis_config.port
    }
    
    snowflake_config = {
      account   = local.snowflake_config.account
      database  = local.snowflake_config.database
      warehouse = local.snowflake_config.warehouse
    }
    
    generated_files = [
      local_file.pulumi_esc_config.filename,
      local_file.estuary_flow_config.filename,
      local_file.monitoring_config.filename
    ]
  }
}

output "github_secrets_created" {
  description = "List of GitHub organization secrets created"
  value       = keys(github_actions_organization_secret.infrastructure_secrets)
}

output "ssh_public_key" {
  description = "SSH public key for Lambda Labs instances"
  value       = tls_private_key.lambda_ssh_key.public_key_openssh
}

output "deployment_commands" {
  description = "Commands to complete deployment"
  value = [
    "# Deploy Pulumi ESC configuration:",
    "pulumi env init scoobyjava-org/default/sophia-ai-production --file ${local_file.pulumi_esc_config.filename}",
    "",
    "# Deploy Lambda Labs infrastructure:",
    "python3 infrastructure/lambda-labs-deployment.py",
    "",
    "# Configure Estuary Flow:",
    "# Upload ${local_file.estuary_flow_config.filename} to Estuary Flow dashboard",
    "",
    "# Set up monitoring:",
    "# Deploy ${local_file.monitoring_config.filename} to monitoring system"
  ]
}

