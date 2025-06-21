import pulumi_esc as esc

# Create comprehensive ESC environment for Sophia AI
sophia_esc_environment = esc.Environment("sophia-ai-production",
    definition={
        "values": {
            "github": {
                "fn::open::github-secrets": {
                    "organization": "ai-cherry",
                    "secrets": ["*"]  # Pull all organization secrets
                }
            },
            "ai_intelligence": {
                "arize": {
                    "space_id": "${github.ARIZE_SPACE_ID}",
                    "api_key": "${github.ARIZE_API_KEY}"
                },
                "openrouter": {
                    "api_key": "${github.OPENROUTER_API_KEY}"
                },
                "portkey": {
                    "api_key": "${github.PORTKEY_API_KEY}",
                    "config": "${github.PORTKEY_CONFIG}"
                },
                "huggingface": {
                    "api_token": "${github.HUGGINGFACE_API_TOKEN}"
                },
                "together_ai": {
                    "api_key": "${github.TOGETHER_AI_API_KEY}"
                }
            },
            "data_intelligence": {
                "apify": {
                    "api_token": "${github.APIFY_API_TOKEN}"
                },
                "phantombuster": {
                    "api_key": "${github.PHANTOM_BUSTER_API_KEY}"
                },
                "twingly": {
                    "api_key": "${github.TWINGLY_API_KEY}"
                },
                "tavily": {
                    "api_key": "${github.TAVILY_API_KEY}"
                },
                "zenrows": {
                    "api_key": "${github.ZENROWS_API_KEY}"
                }
            },
            "infrastructure": {
                "lambda_labs": {
                    "api_key": "${github.LAMBDA_LABS_API_KEY}",
                    "control_plane_ip": "170.9.9.253",
                    "ssh_key_name": "cherry-ai-key"
                },
                "docker": {
                    "username": "${github.DOCKER_USER_NAME}",
                    "token": "${github.DOCKER_PERSONAL_ACCESS_TOKEN}"
                },
                "pulumi": {
                    "access_token": "${github.PULUMI_ACCESS_TOKEN}",
                    "org": "scoobyjava-org"
                }
            },
            "business_intelligence": {
                "snowflake": {
                    "account": "${github.SNOWFLAKE_ACCOUNT}",
                    "user": "${github.SNOWFLAKE_USER}",
                    "password": "${github.SNOWFLAKE_PASSWORD}",
                    "warehouse": "${github.SNOWFLAKE_WAREHOUSE}",
                    "database": "${github.SNOWFLAKE_DATABASE}",
                    "schema": "${github.SNOWFLAKE_SCHEMA}"
                },
                "pinecone": {
                    "api_key": "${github.PINECONE_API_KEY}",
                    "environment": "${github.PINECONE_ENVIRONMENT}"
                }
            }
        }
    }
)
