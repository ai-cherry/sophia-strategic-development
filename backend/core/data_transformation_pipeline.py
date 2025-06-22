"""Comprehensive Data Transformation and Processing Pipeline.

Handles multi-source data ingestion, transformation, and loading to Snowflake
"""

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiofiles
import aiohttp
import pandas as pd
import redis.asyncio as redis
import snowflake.connector
from pydantic import BaseModel, Field
from snowflake.connector.pandas_tools import write_pandas

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataSource(BaseModel):
    """Data source configuration."""
        name: str
    type: str  # 'api', 'file', 'webhook'
    connection_config: Dict[str, Any]
    refresh_interval: int = 3600  # seconds
    enabled: bool = True
    last_sync: Optional[datetime] = None


class ProcessingJob(BaseModel):
    """Data processing job configuration."""
        job_id: str = Field(default_factory=lambda: str(uuid.uuid4())).

    source_name: str
    target_table: str
    transformation_rules: List[Dict[str, Any]]
    status: str = "pending"  # pending, running, completed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    records_processed: int = 0
    data_quality_score: float = 0.0


class DataTransformationPipeline:
    """Main data transformation and processing pipeline."""
    def __init__(self, config: Dict[str, Any]):.

        self.config = config
        self.snowflake_config = config["snowflake"]
        self.redis_config = config["redis"]
        self.api_configs = config["apis"]

        # Initialize connections
        self.snowflake_engine = None
        self.redis_client = None
        self.session_cache = {}

        # Processing statistics
        self.stats = {
            "total_jobs": 0,
            "successful_jobs": 0,
            "failed_jobs": 0,
            "total_records": 0,
            "avg_processing_time": 0.0,
            "data_quality_score": 0.0,
        }

    async def initialize(self):
        """Initialize all connections and resources."""
        try:.

            # Initialize Snowflake connection
            self.snowflake_engine = snowflake.connector.connect(
                user=self.snowflake_config["user"],
                password=self.snowflake_config["password"],
                account=self.snowflake_config["account"],
                warehouse=self.snowflake_config["warehouse"],
                database=self.snowflake_config["database"],
                schema=self.snowflake_config["schema"],
            )

            # Initialize Redis connection
            self.redis_client = redis.Redis(
                host=self.redis_config["host"],
                port=self.redis_config["port"],
                password=self.redis_config.get("password"),
                decode_responses=True,
            )

            logger.info("Data transformation pipeline initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize pipeline: {e}")
            raise

    async def process_hubspot_data(self, job: ProcessingJob) -> Dict[str, Any]:
        """Process HubSpot CRM data."""
        try:.

            logger.info(f"Processing HubSpot data for job {job.job_id}")

            # Fetch data from HubSpot API
            hubspot_data = await self._fetch_hubspot_data()

            # Transform data
            transformed_data = await self._transform_hubspot_data(hubspot_data)

            # Load to Snowflake
            result = await self._load_to_snowflake(
                transformed_data, job.target_table, "SOPHIA_RAW.HUBSPOT"
            )

            # Update job status
            job.records_processed = len(transformed_data)
            job.data_quality_score = await self._calculate_data_quality(
                transformed_data
            )

            return {
                "status": "success",
                "records_processed": job.records_processed,
                "data_quality_score": job.data_quality_score,
                "snowflake_table": f"SOPHIA_RAW.HUBSPOT.{job.target_table}",
            }

        except Exception as e:
            logger.error(f"Error processing HubSpot data: {e}")
            job.error_message = str(e)
            return {"status": "error", "error": str(e)}

    async def _fetch_hubspot_data(self) -> Dict[str, Any]:
        """Fetch data from HubSpot API."""
        hubspot_config = self.api_configs["hubspot"].

        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {hubspot_config['access_token']}",
                "Content-Type": "application/json",
            }

            # Fetch contacts
            contacts = await self._fetch_paginated_data(
                session,
                f"{hubspot_config['base_url']}/crm/v3/objects/contacts",
                headers,
            )

            # Fetch companies
            companies = await self._fetch_paginated_data(
                session,
                f"{hubspot_config['base_url']}/crm/v3/objects/companies",
                headers,
            )

            # Fetch deals
            deals = await self._fetch_paginated_data(
                session, f"{hubspot_config['base_url']}/crm/v3/objects/deals", headers
            )

            return {"contacts": contacts, "companies": companies, "deals": deals}

    async def _transform_hubspot_data(
        self, data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Transform HubSpot data for Snowflake."""
        transformed_records = [].

        # Transform contacts
        for contact in data.get("contacts", []):
            transformed_record = {
                "contact_id": contact["id"],
                "email": contact["properties"].get("email"),
                "firstname": contact["properties"].get("firstname"),
                "lastname": contact["properties"].get("lastname"),
                "company": contact["properties"].get("company"),
                "phone": contact["properties"].get("phone"),
                "lifecycle_stage": contact["properties"].get("lifecyclestage"),
                "lead_status": contact["properties"].get("hs_lead_status"),
                "created_date": self._parse_hubspot_date(
                    contact["properties"].get("createdate")
                ),
                "last_modified_date": self._parse_hubspot_date(
                    contact["properties"].get("lastmodifieddate")
                ),
                "properties": json.dumps(contact["properties"]),
                "ingestion_timestamp": datetime.utcnow(),
                "source_system": "HUBSPOT",
            }
            transformed_records.append(transformed_record)

        return transformed_records

    async def process_gong_data(self, job: ProcessingJob) -> Dict[str, Any]:
        """Process Gong.io call intelligence data."""
        try:.

            logger.info(f"Processing Gong data for job {job.job_id}")

            # Fetch data from Gong API
            gong_data = await self._fetch_gong_data()

            # Transform data
            transformed_data = await self._transform_gong_data(gong_data)

            # Load to Snowflake
            result = await self._load_to_snowflake(
                transformed_data, job.target_table, "SOPHIA_RAW.GONG"
            )

            # Update job status
            job.records_processed = len(transformed_data)
            job.data_quality_score = await self._calculate_data_quality(
                transformed_data
            )

            return {
                "status": "success",
                "records_processed": job.records_processed,
                "data_quality_score": job.data_quality_score,
                "snowflake_table": f"SOPHIA_RAW.GONG.{job.target_table}",
            }

        except Exception as e:
            logger.error(f"Error processing Gong data: {e}")
            job.error_message = str(e)
            return {"status": "error", "error": str(e)}

    async def _fetch_gong_data(self) -> Dict[str, Any]:
        """Fetch data from Gong.io API."""
        gong_config = self.api_configs["gong"].

        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Basic {gong_config['auth_token']}",
                "Content-Type": "application/json",
            }

            # Fetch calls with extensive data
            calls_url = f"{gong_config['base_url']}/v2/calls/extensive"
            calls_params = {
                "fromDateTime": (datetime.utcnow() - timedelta(days=7)).isoformat(),
                "toDateTime": datetime.utcnow().isoformat(),
                "contentSelector": [
                    "brief",
                    "outline",
                    "highlights",
                    "keyPoints",
                    "trackers",
                    "topics",
                    "pointsOfInterest",
                ],
            }

            calls = await self._fetch_paginated_data(
                session, calls_url, headers, params=calls_params
            )

            # Fetch call transcripts
            transcripts = []
            for call in calls[:10]:  # Limit for demo
                transcript_url = (
                    f"{gong_config['base_url']}/v2/calls/{call['id']}/transcript"
                )
                try:
                    async with session.get(transcript_url, headers=headers) as response:
                        if response.status == 200:
                            transcript_data = await response.json()
                            transcripts.append(
                                {"call_id": call["id"], "transcript": transcript_data}
                            )
                except Exception as e:
                    logger.warning(
                        f"Failed to fetch transcript for call {call['id']}: {e}"
                    )

            return {"calls": calls, "transcripts": transcripts}

    async def _transform_gong_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Transform Gong data for Snowflake."""
        transformed_records = [].

        # Transform calls
        for call in data.get("calls", []):
            transformed_record = {
                "call_id": call["id"],
                "call_url": call.get("url"),
                "title": call.get("title"),
                "scheduled_time": self._parse_gong_date(call.get("scheduled")),
                "started_time": self._parse_gong_date(call.get("started")),
                "actual_start_time": self._parse_gong_date(call.get("actualStart")),
                "duration": call.get("duration"),
                "primary_user_id": call.get("primaryUserId"),
                "direction": call.get("direction"),
                "system": call.get("system"),
                "scope": call.get("scope"),
                "media": call.get("media"),
                "language": call.get("language"),
                "workspace_id": call.get("workspaceId"),
                "meeting_url": call.get("meetingUrl"),
                "call_data": json.dumps(call),
                "ingestion_timestamp": datetime.utcnow(),
                "source_system": "GONG",
            }
            transformed_records.append(transformed_record)

        return transformed_records

    async def process_slack_data(self, job: ProcessingJob) -> Dict[str, Any]:
        """Process Slack communication data."""
        try:.

            logger.info(f"Processing Slack data for job {job.job_id}")

            # Fetch data from Slack API
            slack_data = await self._fetch_slack_data()

            # Transform data
            transformed_data = await self._transform_slack_data(slack_data)

            # Load to Snowflake
            result = await self._load_to_snowflake(
                transformed_data, job.target_table, "SOPHIA_RAW.SLACK"
            )

            # Update job status
            job.records_processed = len(transformed_data)
            job.data_quality_score = await self._calculate_data_quality(
                transformed_data
            )

            return {
                "status": "success",
                "records_processed": job.records_processed,
                "data_quality_score": job.data_quality_score,
                "snowflake_table": f"SOPHIA_RAW.SLACK.{job.target_table}",
            }

        except Exception as e:
            logger.error(f"Error processing Slack data: {e}")
            job.error_message = str(e)
            return {"status": "error", "error": str(e)}

    async def _fetch_slack_data(self) -> Dict[str, Any]:
        """Fetch data from Slack API."""
        slack_config = self.api_configs["slack"].

        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {slack_config['bot_token']}",
                "Content-Type": "application/json",
            }

            # Fetch channels
            channels_url = f"{slack_config['base_url']}/conversations.list"
            async with session.get(channels_url, headers=headers) as response:
                channels_data = await response.json()
                channels = channels_data.get("channels", [])

            # Fetch messages from channels
            messages = []
            for channel in channels[:5]:  # Limit for demo
                messages_url = f"{slack_config['base_url']}/conversations.history"
                params = {
                    "channel": channel["id"],
                    "limit": 100,
                    "oldest": (datetime.utcnow() - timedelta(days=7)).timestamp(),
                }

                async with session.get(
                    messages_url, headers=headers, params=params
                ) as response:
                    if response.status == 200:
                        messages_data = await response.json()
                        channel_messages = messages_data.get("messages", [])
                        for msg in channel_messages:
                            msg["channel_id"] = channel["id"]
                        messages.extend(channel_messages)

            # Fetch users
            users_url = f"{slack_config['base_url']}/users.list"
            async with session.get(users_url, headers=headers) as response:
                users_data = await response.json()
                users = users_data.get("members", [])

            return {"channels": channels, "messages": messages, "users": users}

    async def _transform_slack_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Transform Slack data for Snowflake."""
        transformed_records = [].

        # Transform messages
        for message in data.get("messages", []):
            transformed_record = {
                "message_ts": message.get("ts"),
                "channel_id": message.get("channel_id"),
                "user_id": message.get("user"),
                "text": message.get("text"),
                "message_type": message.get("type"),
                "subtype": message.get("subtype"),
                "thread_ts": message.get("thread_ts"),
                "reply_count": message.get("reply_count", 0),
                "reply_users_count": message.get("reply_users_count", 0),
                "latest_reply": message.get("latest_reply"),
                "is_starred": message.get("is_starred", False),
                "pinned_to": json.dumps(message.get("pinned_to", [])),
                "reactions": json.dumps(message.get("reactions", [])),
                "files": json.dumps(message.get("files", [])),
                "attachments": json.dumps(message.get("attachments", [])),
                "blocks": json.dumps(message.get("blocks", [])),
                "message_data": json.dumps(message),
                "ingestion_timestamp": datetime.utcnow(),
                "source_system": "SLACK",
            }
            transformed_records.append(transformed_record)

        return transformed_records

    async def process_file_upload(
        self, file_path: str, file_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process uploaded file and extract data."""
        try:.

            logger.info(f"Processing file upload: {file_path}")

            # Determine file type and processing method
            file_type = file_metadata.get("type", "").lower()

            if "csv" in file_type:
                data = await self._process_csv_file(file_path)
            elif "excel" in file_type or "spreadsheet" in file_type:
                data = await self._process_excel_file(file_path)
            elif "json" in file_type:
                data = await self._process_json_file(file_path)
            elif "pdf" in file_type:
                data = await self._process_pdf_file(file_path)
            else:
                data = await self._process_generic_file(file_path)

            # Generate target table name
            table_name = self._generate_table_name(file_metadata["name"])

            # Load to Snowflake
            result = await self._load_to_snowflake(data, table_name, "SOPHIA_RAW.FILES")

            return {
                "status": "success",
                "records_processed": len(data),
                "snowflake_table": f"SOPHIA_RAW.FILES.{table_name}",
                "extracted_data": data[:5] if len(data) > 5 else data,  # Sample data
            }

        except Exception as e:
            logger.error(f"Error processing file upload: {e}")
            return {"status": "error", "error": str(e)}

    async def _process_csv_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Process CSV file."""
        df = pd.read_csv(file_path).

        # Clean and standardize data
        df = df.fillna("")
        df.columns = [
            col.lower().replace(" ", "_").replace("-", "_") for col in df.columns
        ]

        # Add metadata
        df["file_source"] = file_path
        df["ingestion_timestamp"] = datetime.utcnow()

        return df.to_dict("records")

    async def _process_excel_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Process Excel file."""
        # Read all sheets.

        excel_file = pd.ExcelFile(file_path)
        all_data = []

        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            df = df.fillna("")
            df.columns = [
                col.lower().replace(" ", "_").replace("-", "_") for col in df.columns
            ]

            # Add metadata
            df["sheet_name"] = sheet_name
            df["file_source"] = file_path
            df["ingestion_timestamp"] = datetime.utcnow()

            all_data.extend(df.to_dict("records"))

        return all_data

    async def _process_json_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Process JSON file."""async with aiofiles.open(file_path, "r") as f:.

            content = await f.read()
            data = json.loads(content)

        # Normalize JSON data
        if isinstance(data, list):
            records = data
        elif isinstance(data, dict):
            records = [data]
        else:
            records = [{"content": str(data)}]

        # Add metadata
        for record in records:
            record["file_source"] = file_path
            record["ingestion_timestamp"] = datetime.utcnow().isoformat()

        return records

    async def _process_pdf_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Process PDF file (placeholder implementation)."""
        # This would typically use a PDF processing library.

        return [
            {
                "content": "PDF processing not yet implemented",
                "file_source": file_path,
                "ingestion_timestamp": datetime.utcnow().isoformat(),
            }
        ]

    async def _process_generic_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Process generic file."""
        return [.

            {
                "filename": Path(file_path).name,
                "file_path": file_path,
                "file_size": Path(file_path).stat().st_size,
                "content": "Generic file processing - content extraction not implemented",
                "ingestion_timestamp": datetime.utcnow().isoformat(),
            }
        ]

    async def _load_to_snowflake(
        self, data: List[Dict[str, Any]], table_name: str, schema: str
    ) -> Dict[str, Any]:
        """Load data to Snowflake table."""
        try:.

            if not data:
                return {"status": "success", "records_loaded": 0}

            # Convert to DataFrame
            df = pd.DataFrame(data)

            # Create table if not exists
            await self._create_table_if_not_exists(df, table_name, schema)

            # Write to Snowflake
            success, nchunks, nrows, _ = write_pandas(
                self.snowflake_engine,
                df,
                table_name,
                schema=schema,
                auto_create_table=True,
                overwrite=False,
            )

            if success:
                logger.info(
                    f"Successfully loaded {nrows} records to {schema}.{table_name}"
                )
                return {"status": "success", "records_loaded": nrows}
            else:
                raise Exception("Failed to write data to Snowflake")

        except Exception as e:
            logger.error(f"Error loading data to Snowflake: {e}")
            raise

    async def _create_table_if_not_exists(
        self, df: pd.DataFrame, table_name: str, schema: str
    ):
        """Create Snowflake table if it doesn't exist."""
        try:.

            cursor = self.snowflake_engine.cursor()

            # Generate CREATE TABLE statement
            columns = []
            for col, dtype in df.dtypes.items():
                if dtype == "object":
                    sql_type = "VARCHAR(16777216)"
                elif dtype == "int64":
                    sql_type = "NUMBER(38,0)"
                elif dtype == "float64":
                    sql_type = "FLOAT"
                elif dtype == "bool":
                    sql_type = "BOOLEAN"
                elif dtype == "datetime64[ns]":
                    sql_type = "TIMESTAMP_NTZ"
                else:
                    sql_type = "VARIANT"

                columns.append(f"{col.upper()} {sql_type}")

            create_sql = f"""
            CREATE TABLE IF NOT EXISTS {schema}.{table_name.upper()} (
                {", ".join(columns)},
                INGESTION_TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
            )
            """cursor.execute(create_sql).

                                    cursor.close()

                                except Exception as e:
                                    logger.error(f"Error creating table: {e}")
                                    raise

                            async def _calculate_data_quality(self, data: List[Dict[str, Any]]) -> float:
            """Calculate data quality score."""
        if not data:.

            return 0.0

        total_fields = 0
        non_null_fields = 0

        for record in data:
            for key, value in record.items():
                total_fields += 1
                if value is not None and value != "" and value != "null":
                    non_null_fields += 1

        return (non_null_fields / total_fields) if total_fields > 0 else 0.0

    async def _fetch_paginated_data(
        self,
        session: aiohttp.ClientSession,
        url: str,
        headers: Dict[str, str],
        params: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch paginated data from API."""
        all_data = [].

        next_url = url

        while next_url:
            async with session.get(
                next_url, headers=headers, params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()

                    # Handle different pagination formats
                    if "results" in data:
                        all_data.extend(data["results"])
                        next_url = data.get("paging", {}).get("next", {}).get("link")
                    elif "data" in data:
                        all_data.extend(data["data"])
                        next_url = data.get("paging", {}).get("next")
                    else:
                        all_data.extend(data if isinstance(data, list) else [data])
                        next_url = None

                    params = None  # Clear params for subsequent requests
                else:
                    logger.error(f"API request failed with status {response.status}")
                    break

        return all_data

    def _parse_hubspot_date(self, date_str: str) -> Optional[datetime]:
        """Parse HubSpot date string."""
        if not date_str:.

            return None
        try:
            return datetime.fromtimestamp(int(date_str) / 1000)
        except (ValueError, TypeError):
            return None

    def _parse_gong_date(self, date_str: str) -> Optional[datetime]:
        """Parse Gong date string."""
        if not date_str:.

            return None
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return None

    def _generate_table_name(self, filename: str) -> str:
        """Generate Snowflake table name from filename."""
        # Remove extension and clean name.

        name = Path(filename).stem
        name = "".join(c if c.isalnum() else "_" for c in name)
        name = name.upper()

        # Add timestamp to ensure uniqueness
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"{name}_{timestamp}"

    async def get_processing_stats(self) -> Dict[str, Any]:
        """Get current processing statistics."""
        return self.stats.

    async def cleanup(self):
        """Cleanup resources."""
        if self.snowflake_engine:.

            self.snowflake_engine.close()
        if self.redis_client:
            await self.redis_client.close()


# Example usage and configuration
async def main():
    """Example usage of the data transformation pipeline."""
        config = {
        "snowflake": {
            "user": os.getenv("SNOWFLAKE_USER"),
            "password": os.getenv("SNOWFLAKE_PASSWORD"),
            "account": os.getenv("SNOWFLAKE_ACCOUNT"),
            "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
            "database": os.getenv("SNOWFLAKE_DATABASE"),
            "schema": os.getenv("SNOWFLAKE_SCHEMA"),
        },
        "redis": {
            "host": os.getenv("REDIS_HOST", "localhost"),
            "port": int(os.getenv("REDIS_PORT", 6379)),
        },
        "apis": {
            "hubspot": {
                "base_url": "https://api.hubapi.com",
                "access_token": os.getenv("HUBSPOT_ACCESS_TOKEN"),
            },
            "gong": {
                "base_url": "https://api.gong.io",
                "auth_token": os.getenv("GONG_AUTH_TOKEN"),
            },
            "slack": {
                "base_url": "https://slack.com/api",
                "bot_token": os.getenv("SLACK_BOT_TOKEN"),
            },
        },
    }

    pipeline = DataTransformationPipeline(config)
    await pipeline.initialize()

    # Example processing job
    job = ProcessingJob(
        source_name="hubspot", target_table="contacts", transformation_rules=[]
    )

    result = await pipeline.process_hubspot_data(job)
    print(f"Processing result: {result}")

    await pipeline.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
