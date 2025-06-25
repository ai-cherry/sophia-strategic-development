#!/usr/bin/env python3
"""
Knowledge Service for Sophia AI
Comprehensive knowledge management with file upload, processing, and search
"""

import asyncio
import logging
import json
import os
import csv
import io
from datetime import datetime
from typing import Dict, List, Optional, Any, BinaryIO
from uuid import uuid4
from pathlib import Path
import snowflake.connector
from snowflake.connector import DictCursor
from pydantic import BaseModel
import aiofiles
import mimetypes
# Optional imports - will fallback gracefully if not available
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    from docx import Document
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

try:
    import PyPDF2
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Snowflake Configuration
SNOWFLAKE_CONFIG = {
    "account": "ZNB04675",
    "user": "SCOOBYJAVA15",
    "password": "eyJraWQiOiI1MDg3NDc2OTQxMyIsImFsZyI6IkVTMjU2In0.eyJwIjoiMTk4NzI5NDc2OjUwODc0NzQ1NDc3IiwiaXNzIjoiU0Y6MTA0OSIsImV4cCI6MTc4MjI4MDQ3OH0.8m-fWI5rvCs6b8bvw1quiM-UzW9uPRxMUmE6VAgOFFylAhRkCzch7ojh7CRLeMdii6DD1Owqap0KoOmyxsW77A",
    "role": "ACCOUNTADMIN",
    "database": "SOPHIA_AI_PROD",
    "schema": "UNIVERSAL_CHAT",
    "warehouse": "SOPHIA_AI_WH"
}

# Data Models
class KnowledgeEntry(BaseModel):
    entry_id: str
    title: str
    content: str
    category_id: str
    category_name: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    status: str = "published"
    created_at: datetime
    updated_at: datetime

class KnowledgeStats(BaseModel):
    total_entries: int
    total_categories: int
    total_file_size: int
    recent_uploads: int
    search_queries_today: int
    most_accessed_category: Optional[str] = None

class UploadResponse(BaseModel):
    entry_id: str
    title: str
    status: str
    message: str
    processing_time: float

class SearchFilters(BaseModel):
    category_id: Optional[str] = None
    file_type: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

class KnowledgeService:
    """Comprehensive knowledge management service"""
    
    def __init__(self):
        self.connection = None
        self.upload_dir = Path("uploads/knowledge")
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def connect(self):
        """Connect to Snowflake"""
        try:
            self.connection = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
            logger.info("✅ Knowledge Service connected to Snowflake")
        except Exception as e:
            logger.error(f"❌ Knowledge Service Snowflake connection failed: {e}")
            raise

    async def disconnect(self):
        """Disconnect from Snowflake"""
        if self.connection:
            self.connection.close()
            logger.info("Knowledge Service disconnected from Snowflake")

    async def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute Snowflake query"""
        try:
            cursor = self.connection.cursor(DictCursor)
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

    def extract_text_from_file(self, file_content: bytes, file_type: str, filename: str) -> str:
        """Extract text content from various file types"""
        try:
            if file_type == "text/plain" or file_type == "text/csv":
                content = file_content.decode('utf-8')
                if file_type == "text/csv" and HAS_PANDAS:
                    try:
                        # Parse CSV and create structured text
                        df = pd.read_csv(io.StringIO(content))
                        text = f"CSV Data from {filename}:\n\n"
                        text += f"Columns: {', '.join(df.columns)}\n\n"
                        text += f"Total Records: {len(df)}\n\n"
                        text += "Sample Data:\n"
                        text += df.head(10).to_string(index=False)
                        return text
                    except Exception:
                        # Fallback to raw content if pandas fails
                        pass
                return content
            
            elif file_type == "application/json":
                data = json.loads(file_content.decode('utf-8'))
                text = f"JSON Data from {filename}:\n\n"
                text += json.dumps(data, indent=2)
                return text
            
            elif file_type == "application/pdf":
                # Simple PDF text extraction
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
                text = f"PDF Document: {filename}\n\n"
                for page_num, page in enumerate(pdf_reader.pages):
                    text += f"Page {page_num + 1}:\n{page.extract_text()}\n\n"
                return text
            
            elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                # DOCX file handling
                doc = Document(io.BytesIO(file_content))
                text = f"Word Document: {filename}\n\n"
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text
            
            else:
                # Try to decode as text for other types
                return file_content.decode('utf-8', errors='ignore')
                
        except Exception as e:
            logger.error(f"Text extraction failed for {filename}: {e}")
            return f"Content from {filename} (text extraction failed)"

    def auto_categorize_content(self, title: str, content: str, filename: str) -> str:
        """Automatically categorize content based on title and content"""
        title_lower = title.lower()
        content_lower = content.lower()
        filename_lower = filename.lower()
        
        # Customer-related keywords
        if any(keyword in title_lower or keyword in content_lower or keyword in filename_lower 
               for keyword in ['customer', 'client', 'contact', 'company', 'tenant', 'property owner']):
            return "customers"
        
        # Product-related keywords
        elif any(keyword in title_lower or keyword in content_lower or keyword in filename_lower 
                for keyword in ['product', 'service', 'feature', 'solution', 'offering', 'pricing']):
            return "products"
        
        # Employee-related keywords
        elif any(keyword in title_lower or keyword in content_lower or keyword in filename_lower 
                for keyword in ['employee', 'staff', 'team', 'personnel', 'hr', 'human resources']):
            return "employees"
        
        # Policy/Process keywords
        elif any(keyword in title_lower or keyword in content_lower or keyword in filename_lower 
                for keyword in ['policy', 'process', 'procedure', 'workflow', 'guidelines', 'manual']):
            return "processes"
        
        # Financial keywords
        elif any(keyword in title_lower or keyword in content_lower or keyword in filename_lower 
                for keyword in ['financial', 'revenue', 'budget', 'accounting', 'invoice', 'payment']):
            return "financial"
        
        # Default to general category
        else:
            return "general"

    async def ensure_category_exists(self, category_id: str) -> str:
        """Ensure category exists, create if it doesn't"""
        # Check if category exists
        check_query = "SELECT CATEGORY_ID FROM KNOWLEDGE_CATEGORIES WHERE CATEGORY_ID = %s"
        existing = await self.execute_query(check_query, (category_id,))
        
        if existing:
            return category_id
        
        # Create category if it doesn't exist
        category_names = {
            "customers": "Customer Information",
            "products": "Products & Services",
            "employees": "Employee Directory",
            "processes": "Business Processes",
            "financial": "Financial Information",
            "general": "General Knowledge"
        }
        
        category_name = category_names.get(category_id, category_id.title())
        
        create_query = """
        INSERT INTO KNOWLEDGE_CATEGORIES (CATEGORY_ID, CATEGORY_NAME, DESCRIPTION, CREATED_AT)
        VALUES (%s, %s, %s, %s)
        """
        
        await self.execute_query(create_query, (
            category_id,
            category_name,
            f"Auto-created category for {category_name}",
            datetime.now()
        ))
        
        logger.info(f"Created new category: {category_id}")
        return category_id

    async def upload_knowledge_entry(
        self,
        title: str,
        content: str,
        category_id: Optional[str] = None,
        file_data: Optional[bytes] = None,
        filename: Optional[str] = None,
        file_type: Optional[str] = None
    ) -> UploadResponse:
        """Upload and process a knowledge entry"""
        start_time = datetime.now()
        entry_id = str(uuid4())
        
        try:
            # Process file if provided
            if file_data and filename:
                if not file_type:
                    file_type, _ = mimetypes.guess_type(filename)
                
                # Extract text content
                extracted_content = self.extract_text_from_file(file_data, file_type, filename)
                content = extracted_content if not content else f"{content}\n\n{extracted_content}"
                
                # Auto-categorize if no category provided
                if not category_id:
                    category_id = self.auto_categorize_content(title, content, filename)
            
            # Default category if still not set
            if not category_id:
                category_id = "general"
            
            # Ensure category exists
            await self.ensure_category_exists(category_id)
            
            # Prepare metadata
            metadata = {
                "file_type": file_type,
                "file_size": len(file_data) if file_data else 0,
                "filename": filename,
                "auto_categorized": True,
                "upload_source": "knowledge_service"
            }
            
            # Insert knowledge entry
            insert_query = """
            INSERT INTO KNOWLEDGE_BASE_ENTRIES 
            (ENTRY_ID, TITLE, CONTENT, CATEGORY_ID, STATUS, METADATA, CREATED_AT, UPDATED_AT)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            now = datetime.now()
            await self.execute_query(insert_query, (
                entry_id,
                title,
                content,
                category_id,
                "published",
                json.dumps(metadata),
                now,
                now
            ))
            
            # Generate and store embedding placeholder
            await self.generate_and_store_embedding(entry_id, content)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Successfully uploaded knowledge entry: {entry_id}")
            
            return UploadResponse(
                entry_id=entry_id,
                title=title,
                status="success",
                message="Knowledge entry uploaded and processed successfully",
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Failed to upload knowledge entry: {e}")
            return UploadResponse(
                entry_id=entry_id,
                title=title,
                status="error",
                message=f"Upload failed: {str(e)}",
                processing_time=(datetime.now() - start_time).total_seconds()
            )

    async def generate_and_store_embedding(self, entry_id: str, content: str):
        """Generate and store embedding for content"""
        try:
            # Placeholder - would use Snowflake Cortex EMBED_TEXT_768 function
            insert_query = """
            INSERT INTO KNOWLEDGE_EMBEDDINGS (ENTRY_ID, EMBEDDING_MODEL, CREATED_AT)
            VALUES (%s, %s, %s)
            """
            await self.execute_query(insert_query, (
                entry_id,
                "snowflake-arctic-embed-m",
                datetime.now()
            ))
        except Exception as e:
            logger.warning(f"Failed to generate embedding for {entry_id}: {e}")

    async def search_knowledge(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[SearchFilters] = None
    ) -> List[KnowledgeEntry]:
        """Search knowledge base with filters"""
        try:
            # Build search query with filters
            where_conditions = ["k.STATUS = 'published'"]
            params = []
            
            # Text search
            where_conditions.append("(UPPER(k.TITLE) LIKE UPPER('%' || %s || '%') OR UPPER(k.CONTENT) LIKE UPPER('%' || %s || '%'))")
            params.extend([query, query])
            
            # Apply filters
            if filters:
                if filters.category_id:
                    where_conditions.append("k.CATEGORY_ID = %s")
                    params.append(filters.category_id)
            
            search_query = f"""
            SELECT 
                k.ENTRY_ID,
                k.TITLE,
                k.CONTENT,
                k.CATEGORY_ID,
                c.CATEGORY_NAME,
                k.STATUS,
                k.METADATA,
                k.CREATED_AT,
                k.UPDATED_AT
            FROM KNOWLEDGE_BASE_ENTRIES k
            JOIN KNOWLEDGE_CATEGORIES c ON k.CATEGORY_ID = c.CATEGORY_ID
            WHERE {' AND '.join(where_conditions)}
            ORDER BY k.UPDATED_AT DESC
            LIMIT %s
            """
            
            params.append(limit)
            results = await self.execute_query(search_query, tuple(params))
            
            # Convert to KnowledgeEntry objects
            entries = []
            for row in results:
                metadata = json.loads(row['METADATA']) if row['METADATA'] else {}
                entry = KnowledgeEntry(
                    entry_id=row['ENTRY_ID'],
                    title=row['TITLE'],
                    content=row['CONTENT'],
                    category_id=row['CATEGORY_ID'],
                    category_name=row['CATEGORY_NAME'],
                    file_type=metadata.get('file_type'),
                    file_size=metadata.get('file_size'),
                    metadata=metadata,
                    status=row['STATUS'],
                    created_at=row['CREATED_AT'],
                    updated_at=row['UPDATED_AT']
                )
                entries.append(entry)
            
            return entries
            
        except Exception as e:
            logger.error(f"Knowledge search failed: {e}")
            return []

    async def get_knowledge_stats(self) -> KnowledgeStats:
        """Get knowledge base statistics"""
        try:
            # Get total entries and categories
            stats_query = """
            SELECT 
                COUNT(DISTINCT k.ENTRY_ID) as total_entries,
                COUNT(DISTINCT k.CATEGORY_ID) as total_categories
            FROM KNOWLEDGE_BASE_ENTRIES k
            WHERE k.STATUS = 'published'
            """
            
            stats_result = await self.execute_query(stats_query)
            stats = stats_result[0] if stats_result else {}
            
            # Get recent uploads (last 7 days)
            recent_query = """
            SELECT COUNT(*) as recent_uploads
            FROM KNOWLEDGE_BASE_ENTRIES
            WHERE STATUS = 'published' 
            AND CREATED_AT >= DATEADD(day, -7, CURRENT_TIMESTAMP())
            """
            
            recent_result = await self.execute_query(recent_query)
            recent_uploads = recent_result[0]['RECENT_UPLOADS'] if recent_result else 0
            
            return KnowledgeStats(
                total_entries=stats.get('TOTAL_ENTRIES', 0),
                total_categories=stats.get('TOTAL_CATEGORIES', 0),
                total_file_size=0,  # Placeholder
                recent_uploads=recent_uploads,
                search_queries_today=0,  # Placeholder
                most_accessed_category="customers"  # Placeholder
            )
            
        except Exception as e:
            logger.error(f"Failed to get knowledge stats: {e}")
            return KnowledgeStats(
                total_entries=0,
                total_categories=0,
                total_file_size=0,
                recent_uploads=0,
                search_queries_today=0
            )

    async def delete_knowledge_entry(self, entry_id: str):
        """Delete knowledge entry"""
        try:
            delete_query = """
            UPDATE KNOWLEDGE_BASE_ENTRIES 
            SET STATUS = 'deleted', UPDATED_AT = %s 
            WHERE ENTRY_ID = %s
            """
            await self.execute_query(delete_query, (datetime.now(), entry_id))
            logger.info(f"Deleted knowledge entry: {entry_id}")
        except Exception as e:
            logger.error(f"Failed to delete knowledge entry {entry_id}: {e}")
            raise

# Global service instance
knowledge_service = KnowledgeService() 