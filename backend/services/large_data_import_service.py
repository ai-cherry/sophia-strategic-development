"""
Large Data Import Service
Handles bulk imports of large datasets from various sources including Gong email/calendar data,
Slack message exports, and other large file uploads for the knowledge base.
"""

import asyncio
import json
import logging
import os
import tempfile
import zipfile
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import uuid
import pandas as pd

import aiofiles

from backend.utils.snowflake_cortex_service import SnowflakeCortexService
from backend.services.knowledge_service import KnowledgeService
from backend.core.logger import logger

logger = logging.getLogger(__name__)


class ImportDataType(Enum):
    """Types of data that can be imported"""

    GONG_EMAIL = "gong_email"
    GONG_CALENDAR = "gong_calendar"
    SLACK_EXPORT = "slack_export"
    HUBSPOT_EXPORT = "hubspot_export"
    CSV_BULK = "csv_bulk"
    JSON_BULK = "json_bulk"
    EMAIL_ARCHIVE = "email_archive"
    DOCUMENT_ARCHIVE = "document_archive"


class ImportStatus(Enum):
    """Import job status"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ImportJob:
    """Represents a large data import job"""

    job_id: str
    data_type: ImportDataType
    source_file: str
    total_records: int
    processed_records: int
    status: ImportStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None


class LargeDataImportService:
    """Service for handling large data imports"""

    def __init__(self):
        self.cortex_service = SnowflakeCortexService()
        self.knowledge_service = KnowledgeService()
        self.temp_dir = tempfile.mkdtemp(prefix="sophia_import_")
        self.max_file_size = 5 * 1024 * 1024 * 1024  # 5GB
        self.batch_size = 1000  # Process in batches

    async def create_import_job(
        self,
        file_path: str,
        data_type: ImportDataType,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ImportJob:
        """
        Create a new import job for large data processing

        Args:
            file_path: Path to the source file
            data_type: Type of data being imported
            metadata: Additional metadata for the import

        Returns:
            ImportJob instance
        """
        job_id = str(uuid.uuid4())

        # Validate file
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Source file not found: {file_path}")

        file_size = os.path.getsize(file_path)
        if file_size > self.max_file_size:
            raise ValueError(
                f"File too large: {file_size} bytes (max: {self.max_file_size})"
            )

        # Estimate total records
        total_records = await self._estimate_record_count(file_path, data_type)

        job = ImportJob(
            job_id=job_id,
            data_type=data_type,
            source_file=file_path,
            total_records=total_records,
            processed_records=0,
            status=ImportStatus.PENDING,
            started_at=datetime.now(),
            metadata=metadata or {},
        )

        # Store job in database
        await self._store_import_job(job)

        logger.info(
            f"Created import job {job_id} for {data_type.value}: {total_records} estimated records"
        )
        return job

    async def process_import_job(self, job_id: str) -> ImportJob:
        """
        Process a large data import job

        Args:
            job_id: ID of the import job

        Returns:
            Updated ImportJob instance
        """
        try:
            # Get job from database
            job = await self._get_import_job(job_id)
            if not job:
                raise ValueError(f"Import job not found: {job_id}")

            # Update status to processing
            job.status = ImportStatus.PROCESSING
            await self._update_import_job(job)

            logger.info(f"Starting processing of import job {job_id}")

            # Process based on data type
            if job.data_type == ImportDataType.GONG_EMAIL:
                await self._process_gong_email_import(job)
            elif job.data_type == ImportDataType.GONG_CALENDAR:
                await self._process_gong_calendar_import(job)
            elif job.data_type == ImportDataType.SLACK_EXPORT:
                await self._process_slack_export_import(job)
            elif job.data_type == ImportDataType.CSV_BULK:
                await self._process_csv_bulk_import(job)
            elif job.data_type == ImportDataType.JSON_BULK:
                await self._process_json_bulk_import(job)
            elif job.data_type == ImportDataType.EMAIL_ARCHIVE:
                await self._process_email_archive_import(job)
            elif job.data_type == ImportDataType.DOCUMENT_ARCHIVE:
                await self._process_document_archive_import(job)
            else:
                raise ValueError(f"Unsupported data type: {job.data_type}")

            # Mark as completed
            job.status = ImportStatus.COMPLETED
            job.completed_at = datetime.now()
            await self._update_import_job(job)

            logger.info(
                f"Completed import job {job_id}: {job.processed_records} records processed"
            )
            return job

        except Exception as e:
            logger.error(f"Import job {job_id} failed: {str(e)}")

            # Update job with error
            job.status = ImportStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.now()
            await self._update_import_job(job)

            raise

    async def _process_gong_email_import(self, job: ImportJob) -> None:
        """Process Gong email data import"""
        logger.info(f"Processing Gong email import for job {job.job_id}")

        # Extract email data from file
        emails = await self._extract_gong_email_data(job.source_file)

        # Process in batches
        for i in range(0, len(emails), self.batch_size):
            batch = emails[i : i + self.batch_size]

            # Transform and load batch
            await self._process_email_batch(batch, job)

            # Update progress
            job.processed_records += len(batch)
            await self._update_import_job(job)

            # Small delay to prevent overwhelming the system
            await asyncio.sleep(0.1)

    async def _process_gong_calendar_import(self, job: ImportJob) -> None:
        """Process Gong calendar data import"""
        logger.info(f"Processing Gong calendar import for job {job.job_id}")

        # Extract calendar data from file
        events = await self._extract_gong_calendar_data(job.source_file)

        # Process in batches
        for i in range(0, len(events), self.batch_size):
            batch = events[i : i + self.batch_size]

            # Transform and load batch
            await self._process_calendar_batch(batch, job)

            # Update progress
            job.processed_records += len(batch)
            await self._update_import_job(job)

            await asyncio.sleep(0.1)

    async def _process_slack_export_import(self, job: ImportJob) -> None:
        """Process Slack workspace export"""
        logger.info(f"Processing Slack export import for job {job.job_id}")

        # Extract Slack data from export file (usually a zip)
        slack_data = await self._extract_slack_export_data(job.source_file)

        # Process channels, users, and messages
        for channel_data in slack_data["channels"]:
            await self._process_slack_channel_batch(channel_data, job)

            # Update progress
            job.processed_records += len(channel_data.get("messages", []))
            await self._update_import_job(job)

    async def _process_csv_bulk_import(self, job: ImportJob) -> None:
        """Process bulk CSV import"""
        logger.info(f"Processing CSV bulk import for job {job.job_id}")

        # Read CSV in chunks
        chunk_size = self.batch_size

        async with aiofiles.open(job.source_file, "r", encoding="utf-8") as file:
            content = await file.read()

        # Use pandas to process CSV efficiently
        df = pd.read_csv(job.source_file, chunksize=chunk_size)

        for chunk in df:
            # Convert chunk to records
            records = chunk.to_dict("records")

            # Process batch
            await self._process_generic_batch(records, job)

            # Update progress
            job.processed_records += len(records)
            await self._update_import_job(job)

    async def _process_json_bulk_import(self, job: ImportJob) -> None:
        """Process bulk JSON import"""
        logger.info(f"Processing JSON bulk import for job {job.job_id}")

        async with aiofiles.open(job.source_file, "r", encoding="utf-8") as file:
            content = await file.read()

        # Parse JSON
        data = json.loads(content)

        # Handle different JSON structures
        if isinstance(data, list):
            records = data
        elif isinstance(data, dict) and "records" in data:
            records = data["records"]
        elif isinstance(data, dict) and "data" in data:
            records = data["data"]
        else:
            records = [data]

        # Process in batches
        for i in range(0, len(records), self.batch_size):
            batch = records[i : i + self.batch_size]

            await self._process_generic_batch(batch, job)

            job.processed_records += len(batch)
            await self._update_import_job(job)

    async def _process_email_archive_import(self, job: ImportJob) -> None:
        """Process email archive import (MBOX, PST, etc.)"""
        logger.info(f"Processing email archive import for job {job.job_id}")

        # Extract emails from archive
        emails = await self._extract_email_archive_data(job.source_file)

        for i in range(0, len(emails), self.batch_size):
            batch = emails[i : i + self.batch_size]

            await self._process_email_batch(batch, job)

            job.processed_records += len(batch)
            await self._update_import_job(job)

    async def _process_document_archive_import(self, job: ImportJob) -> None:
        """Process document archive import (ZIP with multiple files)"""
        logger.info(f"Processing document archive import for job {job.job_id}")

        # Extract documents from archive
        documents = await self._extract_document_archive_data(job.source_file)

        for i in range(0, len(documents), self.batch_size):
            batch = documents[i : i + self.batch_size]

            await self._process_document_batch(batch, job)

            job.processed_records += len(batch)
            await self._update_import_job(job)

    async def _extract_gong_email_data(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract email data from Gong export file"""
        # This would parse Gong's email export format
        # For now, return mock data structure

        emails = []

        # Gong email exports are typically CSV or JSON
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
            for _, row in df.iterrows():
                email = {
                    "email_id": row.get("id", str(uuid.uuid4())),
                    "subject": row.get("subject", ""),
                    "sender": row.get("from", ""),
                    "recipients": row.get("to", "").split(",") if row.get("to") else [],
                    "sent_time": row.get("date", ""),
                    "body": row.get("body", ""),
                    "thread_id": row.get("thread_id", ""),
                    "gong_conversation_id": row.get("conversation_id", ""),
                    "attachments": (
                        json.loads(row.get("attachments", "[]"))
                        if row.get("attachments")
                        else []
                    ),
                }
                emails.append(email)

        return emails

    async def _extract_gong_calendar_data(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract calendar data from Gong export file"""
        events = []

        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
            for _, row in df.iterrows():
                event = {
                    "event_id": row.get("id", str(uuid.uuid4())),
                    "title": row.get("title", ""),
                    "start_time": row.get("start_time", ""),
                    "end_time": row.get("end_time", ""),
                    "attendees": (
                        row.get("attendees", "").split(",")
                        if row.get("attendees")
                        else []
                    ),
                    "location": row.get("location", ""),
                    "description": row.get("description", ""),
                    "gong_call_id": row.get("call_id", ""),
                    "meeting_type": row.get("type", "meeting"),
                }
                events.append(event)

        return events

    async def _extract_slack_export_data(self, file_path: str) -> Dict[str, Any]:
        """Extract data from Slack workspace export (ZIP file)"""
        slack_data = {"channels": [], "users": [], "metadata": {}}

        with zipfile.ZipFile(file_path, "r") as zip_file:
            # Read users.json
            if "users.json" in zip_file.namelist():
                users_content = zip_file.read("users.json").decode("utf-8")
                slack_data["users"] = json.loads(users_content)

            # Read channels.json
            if "channels.json" in zip_file.namelist():
                channels_content = zip_file.read("channels.json").decode("utf-8")
                channels = json.loads(channels_content)

                # For each channel, read its message files
                for channel in channels:
                    channel_name = channel["name"]
                    channel_data = {"channel_info": channel, "messages": []}

                    # Read message files for this channel
                    channel_files = [
                        f
                        for f in zip_file.namelist()
                        if f.startswith(f"{channel_name}/")
                    ]

                    for file_name in channel_files:
                        if file_name.endswith(".json"):
                            messages_content = zip_file.read(file_name).decode("utf-8")
                            daily_messages = json.loads(messages_content)
                            channel_data["messages"].extend(daily_messages)

                    slack_data["channels"].append(channel_data)

        return slack_data

    async def _extract_email_archive_data(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract emails from email archive file"""
        # This would use libraries like mailbox for MBOX files
        # For now, return empty list
        return []

    async def _extract_document_archive_data(
        self, file_path: str
    ) -> List[Dict[str, Any]]:
        """Extract documents from archive file"""
        documents = []

        with zipfile.ZipFile(file_path, "r") as zip_file:
            for file_name in zip_file.namelist():
                if not file_name.endswith("/"):  # Skip directories
                    file_content = zip_file.read(file_name)

                    document = {
                        "document_id": str(uuid.uuid4()),
                        "file_name": os.path.basename(file_name),
                        "file_path": file_name,
                        "file_size": len(file_content),
                        "content": file_content,
                        "extracted_at": datetime.now().isoformat(),
                    }
                    documents.append(document)

        return documents

    async def _process_email_batch(
        self, emails: List[Dict[str, Any]], job: ImportJob
    ) -> None:
        """Process a batch of emails"""
        for email in emails:
            try:
                # Transform email to knowledge base document
                document = {
                    "id": f"email_{email['email_id']}",
                    "title": email["subject"],
                    "content": email["body"],
                    "source": "email_import",
                    "source_type": job.data_type.value,
                    "metadata": {
                        "sender": email["sender"],
                        "recipients": email["recipients"],
                        "sent_time": email["sent_time"],
                        "thread_id": email.get("thread_id"),
                        "gong_conversation_id": email.get("gong_conversation_id"),
                    },
                    "tags": ["email", "communication", job.data_type.value],
                    "category": "communication",
                    "importance_score": 0.6,
                    "auto_detected": False,
                }

                # Add to knowledge base
                await self.knowledge_service.add_document_to_knowledge_base(document)

            except Exception as e:
                logger.error(
                    f"Failed to process email {email.get('email_id')}: {str(e)}"
                )

    async def _process_calendar_batch(
        self, events: List[Dict[str, Any]], job: ImportJob
    ) -> None:
        """Process a batch of calendar events"""
        for event in events:
            try:
                # Transform event to knowledge base document
                document = {
                    "id": f"calendar_{event['event_id']}",
                    "title": event["title"],
                    "content": f"Meeting: {event['title']}\nDescription: {event.get('description', '')}\nAttendees: {', '.join(event.get('attendees', []))}",
                    "source": "calendar_import",
                    "source_type": job.data_type.value,
                    "metadata": {
                        "start_time": event["start_time"],
                        "end_time": event["end_time"],
                        "attendees": event["attendees"],
                        "location": event.get("location"),
                        "gong_call_id": event.get("gong_call_id"),
                        "meeting_type": event.get("meeting_type"),
                    },
                    "tags": ["calendar", "meeting", job.data_type.value],
                    "category": "meetings",
                    "importance_score": 0.7,
                    "auto_detected": False,
                }

                # Add to knowledge base
                await self.knowledge_service.add_document_to_knowledge_base(document)

            except Exception as e:
                logger.error(
                    f"Failed to process calendar event {event.get('event_id')}: {str(e)}"
                )

    async def _process_slack_channel_batch(
        self, channel_data: Dict[str, Any], job: ImportJob
    ) -> None:
        """Process a batch of Slack channel data"""
        channel_info = channel_data["channel_info"]
        messages = channel_data["messages"]

        # Create document for channel information
        channel_doc = {
            "id": f"slack_channel_{channel_info['id']}",
            "title": f"Slack Channel: #{channel_info['name']}",
            "content": f"Channel: {channel_info['name']}\nPurpose: {channel_info.get('purpose', {}).get('value', '')}\nTopic: {channel_info.get('topic', {}).get('value', '')}",
            "source": "slack_import",
            "source_type": job.data_type.value,
            "metadata": {
                "channel_id": channel_info["id"],
                "channel_name": channel_info["name"],
                "is_private": channel_info.get("is_private", False),
                "member_count": len(channel_info.get("members", [])),
                "created": channel_info.get("created"),
            },
            "tags": ["slack", "channel", job.data_type.value],
            "category": "communication",
            "importance_score": 0.5,
            "auto_detected": False,
        }

        await self.knowledge_service.add_document_to_knowledge_base(channel_doc)

        # Process messages in smaller batches
        for i in range(0, len(messages), 100):
            message_batch = messages[i : i + 100]
            await self._process_slack_message_batch(message_batch, channel_info, job)

    async def _process_slack_message_batch(
        self,
        messages: List[Dict[str, Any]],
        channel_info: Dict[str, Any],
        job: ImportJob,
    ) -> None:
        """Process a batch of Slack messages"""
        for message in messages:
            try:
                if message.get("type") == "message" and message.get("text"):
                    # Transform message to knowledge base document
                    document = {
                        "id": f"slack_message_{message.get('ts', str(uuid.uuid4()))}",
                        "title": f"Slack Message in #{channel_info['name']}",
                        "content": message["text"],
                        "source": "slack_import",
                        "source_type": job.data_type.value,
                        "metadata": {
                            "channel_id": channel_info["id"],
                            "channel_name": channel_info["name"],
                            "user_id": message.get("user"),
                            "timestamp": message.get("ts"),
                            "thread_ts": message.get("thread_ts"),
                            "reply_count": message.get("reply_count", 0),
                        },
                        "tags": [
                            "slack",
                            "message",
                            "communication",
                            job.data_type.value,
                        ],
                        "category": "communication",
                        "importance_score": 0.4,
                        "auto_detected": False,
                    }

                    # Add to knowledge base
                    await self.knowledge_service.add_document_to_knowledge_base(
                        document
                    )

            except Exception as e:
                logger.error(f"Failed to process Slack message: {str(e)}")

    async def _process_generic_batch(
        self, records: List[Dict[str, Any]], job: ImportJob
    ) -> None:
        """Process a generic batch of records"""
        for record in records:
            try:
                # Transform record to knowledge base document
                document = {
                    "id": f"import_{job.data_type.value}_{str(uuid.uuid4())}",
                    "title": record.get(
                        "title", f"Imported Record from {job.data_type.value}"
                    ),
                    "content": json.dumps(record, indent=2),
                    "source": "bulk_import",
                    "source_type": job.data_type.value,
                    "metadata": record,
                    "tags": ["bulk_import", job.data_type.value],
                    "category": "imported_data",
                    "importance_score": 0.5,
                    "auto_detected": False,
                }

                # Add to knowledge base
                await self.knowledge_service.add_document_to_knowledge_base(document)

            except Exception as e:
                logger.error(f"Failed to process generic record: {str(e)}")

    async def _process_document_batch(
        self, documents: List[Dict[str, Any]], job: ImportJob
    ) -> None:
        """Process a batch of documents"""
        for doc in documents:
            try:
                # Transform document to knowledge base document
                document = {
                    "id": f"doc_{doc['document_id']}",
                    "title": doc["file_name"],
                    "content": (
                        doc["content"].decode("utf-8", errors="ignore")
                        if isinstance(doc["content"], bytes)
                        else str(doc["content"])
                    ),
                    "source": "document_import",
                    "source_type": job.data_type.value,
                    "metadata": {
                        "file_name": doc["file_name"],
                        "file_path": doc["file_path"],
                        "file_size": doc["file_size"],
                        "extracted_at": doc["extracted_at"],
                    },
                    "tags": ["document", "file", job.data_type.value],
                    "category": "documents",
                    "importance_score": 0.6,
                    "auto_detected": False,
                }

                # Add to knowledge base
                await self.knowledge_service.add_document_to_knowledge_base(document)

            except Exception as e:
                logger.error(
                    f"Failed to process document {doc.get('file_name')}: {str(e)}"
                )

    async def _estimate_record_count(
        self, file_path: str, data_type: ImportDataType
    ) -> int:
        """Estimate the number of records in a file"""
        try:
            file_size = os.path.getsize(file_path)

            # Rough estimates based on data type and file size
            if data_type in [ImportDataType.CSV_BULK]:
                # Estimate ~1KB per CSV row
                return max(1, file_size // 1024)
            elif data_type in [ImportDataType.JSON_BULK]:
                # Estimate ~2KB per JSON record
                return max(1, file_size // 2048)
            elif data_type in [ImportDataType.SLACK_EXPORT]:
                # Slack exports can have many small messages
                return max(1, file_size // 512)
            elif data_type in [ImportDataType.EMAIL_ARCHIVE, ImportDataType.GONG_EMAIL]:
                # Estimate ~5KB per email
                return max(1, file_size // 5120)
            else:
                # Default estimate
                return max(1, file_size // 1024)

        except Exception:
            return 1000  # Default estimate

    async def _store_import_job(self, job: ImportJob) -> None:
        """Store import job in database"""
        # This would store the job in Snowflake or another database
        pass

    async def _get_import_job(self, job_id: str) -> Optional[ImportJob]:
        """Get import job from database"""
        # This would retrieve the job from database
        # For now, return a mock job
        return ImportJob(
            job_id=job_id,
            data_type=ImportDataType.CSV_BULK,
            source_file="/tmp/test.csv",
            total_records=1000,
            processed_records=0,
            status=ImportStatus.PENDING,
            started_at=datetime.now(),
        )

    async def _update_import_job(self, job: ImportJob) -> None:
        """Update import job in database"""
        # This would update the job in database
        pass

    async def get_import_job_status(self, job_id: str) -> Optional[ImportJob]:
        """Get the current status of an import job"""
        return await self._get_import_job(job_id)

    async def cancel_import_job(self, job_id: str) -> bool:
        """Cancel a running import job"""
        try:
            job = await self._get_import_job(job_id)
            if job and job.status in [ImportStatus.PENDING, ImportStatus.PROCESSING]:
                job.status = ImportStatus.CANCELLED
                job.completed_at = datetime.now()
                await self._update_import_job(job)
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to cancel import job {job_id}: {str(e)}")
            return False

    async def list_import_jobs(self, limit: int = 50) -> List[ImportJob]:
        """List recent import jobs"""
        # This would query the database for recent jobs
        # For now, return empty list
        return []

    def cleanup(self):
        """Cleanup temporary files"""
        try:
            import shutil

            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception as e:
            logger.error(f"Failed to cleanup temp directory: {str(e)}")
