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

# Enhanced Snowflake Configuration
ENHANCED_SNOWFLAKE_CONFIG = {
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

class EnhancedKnowledgeService:
    """Enhanced Knowledge Service with comprehensive schema support"""
    
    def __init__(self, snowflake_config: Dict[str, str] = None):
        self.snowflake_config = snowflake_config or ENHANCED_SNOWFLAKE_CONFIG
        self.connection = None
        self.upload_dir = Path("uploads/knowledge")
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def connect(self):
        """Connect to Snowflake with enhanced configuration"""
        try:
            self.connection = snowflake.connector.connect(**self.snowflake_config)
            await self._ensure_enhanced_schema_tables()
            logger.info("✅ Enhanced Knowledge Service connected with comprehensive schema support")
        except Exception as e:
            logger.error(f"❌ Enhanced Knowledge Service connection failed: {e}")
            raise

    async def _ensure_enhanced_schema_tables(self):
        """Ensure all enhanced schema tables exist"""
        cursor = self.connection.cursor()
        
        # Ensure foundational categories exist with enhanced structure
        categories = [
            ("customers", "Customer Information", "Customer lists, contact details, and relationship data", True, 2.0),
            ("products", "Product Information", "Product descriptions, specifications, and documentation", True, 2.0),
            ("employees", "Employee Information", "Employee directory, roles, and organizational structure", True, 1.8),
            ("policies", "Company Policies", "Internal policies, procedures, and guidelines", True, 1.5),
            ("financial", "Financial Information", "Financial data, reports, and analytics", True, 1.7),
            ("competitive", "Competitive Intelligence", "Competitor analysis and market research", False, 1.3),
            ("industry", "Industry Information", "Industry trends, news, and analysis", False, 1.2),
            ("general", "General Knowledge", "General business information and miscellaneous content", False, 1.0)
        ]
        
        for cat_id, name, desc, is_foundational, weight in categories:
            try:
                cursor.execute("""
                INSERT INTO KNOWLEDGE_CATEGORIES 
                (CATEGORY_ID, CATEGORY_NAME, DESCRIPTION, IS_FOUNDATIONAL, IMPORTANCE_WEIGHT, CREATED_AT, UPDATED_AT)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP())
                """, (cat_id, name, desc, is_foundational, weight))
            except Exception:
                # Category likely already exists
                pass
        
        # Ensure knowledge sources exist
        sources = [
            ("src_manual", "Manual Upload", "manual", True),
            ("src_files", "File Upload", "file", True),
            ("src_web", "Web Scraping", "url", True),
            ("src_api", "API Integration", "api", True)
        ]
        
        for src_id, name, src_type, is_active in sources:
            try:
                cursor.execute("""
                INSERT INTO KNOWLEDGE_SOURCES 
                (SOURCE_ID, SOURCE_NAME, SOURCE_TYPE, IS_ACTIVE, CREATED_AT, UPDATED_AT)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP())
                """, (src_id, name, src_type, is_active))
            except Exception:
                # Source likely already exists
                pass
        
        cursor.close()

    async def store_knowledge_entry_enhanced(
        self,
        title: str,
        content: str,
        category_id: str = "general",
        source_id: str = "src_manual",
        importance_score: float = 1.0,
        is_foundational: bool = False,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None,
        file_path: str = None,
        file_size_bytes: int = None,
        chunk_index: int = 0,
        total_chunks: int = 1,
        created_by: str = "system"
    ) -> str:
        """Store knowledge entry with enhanced schema support"""
        
        entry_id = str(uuid4())
        
        # Enhanced knowledge entry insertion
        cursor = self.connection.cursor()
        
        enhanced_metadata = {
            **(metadata or {}),
            "enhanced_processing": True,
            "schema_version": "comprehensive_v1",
            "auto_categorized": True if category_id != "general" else False,
            "processing_timestamp": datetime.now().isoformat()
        }
        
        cursor.execute("""
        INSERT INTO KNOWLEDGE_BASE_ENTRIES 
        (ENTRY_ID, TITLE, CONTENT, CATEGORY_ID, SOURCE_ID, IMPORTANCE_SCORE, 
         IS_FOUNDATIONAL, TAGS, METADATA, FILE_PATH, FILE_SIZE_BYTES,
         CHUNK_INDEX, TOTAL_CHUNKS, CREATED_BY, CREATED_AT, UPDATED_AT)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP())
        """, (
            entry_id, title, content, category_id, source_id, importance_score,
            is_foundational, json.dumps(tags or []), json.dumps(enhanced_metadata),
            file_path, file_size_bytes, chunk_index, total_chunks, created_by
        ))
        
        cursor.close()
        logger.info(f"Stored enhanced knowledge entry: {entry_id} (chunk {chunk_index + 1}/{total_chunks})")
        return entry_id

    async def process_file_with_chunking(
        self,
        filename: str,
        file_content: bytes,
        file_type: str,
        chunk_size: int = 4000,
        chunk_overlap: int = 200
    ) -> List[str]:
        """Process file with intelligent chunking for large files"""
        
        # Extract text content
        try:
            if file_type == "text/plain":
                text_content = file_content.decode('utf-8', errors='ignore')
            elif file_type == "text/csv" and HAS_PANDAS:
                df = pd.read_csv(io.BytesIO(file_content))
                text_content = f"CSV Data from {filename}:\n\n"
                text_content += f"Columns: {', '.join(df.columns)}\n"
                text_content += f"Total Records: {len(df)}\n\n"
                text_content += df.to_string(index=False)
            elif file_type == "application/json":
                data = json.loads(file_content.decode('utf-8'))
                text_content = f"JSON Data from {filename}:\n\n{json.dumps(data, indent=2)}"
            else:
                # Fallback to raw text
                text_content = file_content.decode('utf-8', errors='ignore')
        except Exception as e:
            logger.warning(f"Failed to extract text from {filename}: {e}")
            text_content = f"Content from {filename} (extraction failed)"

        # Auto-categorize based on filename and content
        category_id = self._auto_categorize_content(filename, text_content)
        
        # Determine importance score
        importance_score = self._calculate_importance_score(filename, text_content, category_id)
        
        # Create intelligent chunks
        chunks = self._create_intelligent_chunks(text_content, chunk_size, chunk_overlap)
        
        # Store each chunk as a separate entry
        entry_ids = []
        total_chunks = len(chunks)
        
        for i, chunk in enumerate(chunks):
            chunk_title = f"{filename} - Part {i + 1}"
            if i == 0:
                chunk_title = f"{filename} - Overview"
            elif i == total_chunks - 1:
                chunk_title = f"{filename} - Conclusion"
            
            # Enhanced content with metadata
            enhanced_content = f"**Source:** {filename}\n"
            enhanced_content += f"**File Type:** {file_type}\n"
            enhanced_content += f"**Part:** {i + 1} of {total_chunks}\n"
            enhanced_content += f"**File Size:** {len(file_content):,} bytes\n\n"
            enhanced_content += chunk
            
            entry_id = await self.store_knowledge_entry_enhanced(
                title=chunk_title,
                content=enhanced_content,
                category_id=category_id,
                source_id="src_files",
                importance_score=importance_score,
                is_foundational=self._is_foundational_content(category_id, text_content),
                metadata={
                    "filename": filename,
                    "file_type": file_type,
                    "file_size_bytes": len(file_content),
                    "chunk_info": {
                        "chunk_index": i,
                        "total_chunks": total_chunks,
                        "chunk_size": len(chunk),
                        "overlap_used": chunk_overlap if i > 0 else 0
                    }
                },
                file_path=f"uploads/knowledge/{filename}",
                file_size_bytes=len(file_content),
                chunk_index=i,
                total_chunks=total_chunks
            )
            
            entry_ids.append(entry_id)
        
        logger.info(f"Processed {filename} into {total_chunks} chunks with enhanced metadata")
        return entry_ids

    def _create_intelligent_chunks(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Create intelligent chunks with context preservation"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        sentences = self._split_into_sentences(text)
        
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                # Start new chunk with overlap for context
                overlap_start = max(0, len(current_chunk) - overlap)
                current_chunk = current_chunk[overlap_start:] + " " + sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences for better chunking"""
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _auto_categorize_content(self, filename: str, content: str) -> str:
        """Auto-categorize content based on filename and content analysis"""
        filename_lower = filename.lower()
        content_lower = content.lower()
        
        # Enhanced categorization with more specific rules
        category_keywords = {
            "customers": ["customer", "client", "contact", "company", "tenant", "account", "crm"],
            "products": ["product", "service", "feature", "solution", "offering", "catalog", "spec"],
            "employees": ["employee", "staff", "team", "personnel", "hr", "person", "directory"],
            "financial": ["financial", "revenue", "budget", "accounting", "payment", "invoice", "cost"],
            "policies": ["policy", "procedure", "guideline", "manual", "instruction", "compliance"],
            "competitive": ["competitor", "competition", "market share", "benchmark", "analysis"],
            "industry": ["industry", "market", "trend", "report", "research", "analysis"]
        }
        
        # Score each category
        category_scores = {}
        for category, keywords in category_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in filename_lower:
                    score += 2  # Filename matches are weighted higher
                if keyword in content_lower:
                    score += 1
            category_scores[category] = score
        
        # Return category with highest score, or "general" if no clear match
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            if category_scores[best_category] > 0:
                return best_category
        
        return "general"

    def _calculate_importance_score(self, filename: str, content: str, category_id: str) -> float:
        """Calculate importance score based on various factors"""
        base_score = 1.0
        
        # Category-based scoring
        category_weights = {
            "customers": 2.0,
            "products": 2.0,
            "employees": 1.8,
            "financial": 1.7,
            "policies": 1.5,
            "competitive": 1.3,
            "industry": 1.2,
            "general": 1.0
        }
        
        category_multiplier = category_weights.get(category_id, 1.0)
        
        # Content length factor (longer content typically more important)
        length_multiplier = min(1.5, 1.0 + (len(content) / 10000))
        
        # Filename indicators
        filename_lower = filename.lower()
        filename_multiplier = 1.0
        if any(word in filename_lower for word in ["important", "critical", "key", "main", "primary"]):
            filename_multiplier = 1.3
        elif any(word in filename_lower for word in ["archive", "old", "backup", "temp"]):
            filename_multiplier = 0.8
        
        final_score = base_score * category_multiplier * length_multiplier * filename_multiplier
        return min(3.0, final_score)  # Cap at 3.0

    def _is_foundational_content(self, category_id: str, content: str) -> bool:
        """Determine if content is foundational to the business"""
        foundational_categories = ["customers", "products", "employees", "policies", "financial"]
        
        if category_id in foundational_categories:
            # Additional checks for content quality/completeness
            if len(content) > 1000:  # Substantial content
                foundational_keywords = [
                    "core", "fundamental", "essential", "primary", "main", 
                    "key", "critical", "important", "foundation"
                ]
                if any(keyword in content.lower() for keyword in foundational_keywords):
                    return True
                # Large customer/product lists are typically foundational
                if category_id in ["customers", "products"] and len(content) > 5000:
                    return True
        
        return False

    async def search_knowledge_enhanced(
        self,
        query: str,
        category_filter: str = None,
        limit: int = 10,
        min_importance: float = 0.5,
        include_chunks: bool = True
    ) -> List[Dict[str, Any]]:
        """Enhanced knowledge search with comprehensive schema support"""
        
        cursor = self.connection.cursor(DictCursor)
        
        # Enhanced search query with all schema features
        search_query = """
        SELECT 
            k.ENTRY_ID,
            k.TITLE,
            k.CONTENT,
            k.CATEGORY_ID,
            c.CATEGORY_NAME,
            k.IMPORTANCE_SCORE,
            k.IS_FOUNDATIONAL,
            k.CHUNK_INDEX,
            k.TOTAL_CHUNKS,
            k.FILE_PATH,
            k.FILE_SIZE_BYTES,
            k.METADATA,
            k.TAGS,
            k.CREATED_AT,
            k.UPDATED_AT,
            -- Enhanced relevance scoring
            CASE 
                WHEN UPPER(k.TITLE) LIKE UPPER(?) THEN 3.0
                WHEN UPPER(k.CONTENT) LIKE UPPER(?) THEN 2.0
                ELSE 1.0
            END * k.IMPORTANCE_SCORE * 
            CASE WHEN k.IS_FOUNDATIONAL THEN 1.2 ELSE 1.0 END as RELEVANCE_SCORE
        FROM KNOWLEDGE_BASE_ENTRIES k
        JOIN KNOWLEDGE_CATEGORIES c ON k.CATEGORY_ID = c.CATEGORY_ID
        WHERE k.IMPORTANCE_SCORE >= ?
        AND (UPPER(k.TITLE) LIKE UPPER(?) OR UPPER(k.CONTENT) LIKE UPPER(?))
        """
        
        search_term = f"%{query}%"
        params = [search_term, search_term, min_importance, search_term, search_term]
        
        if category_filter:
            search_query += " AND k.CATEGORY_ID = ?"
            params.append(category_filter)
        
        search_query += " ORDER BY RELEVANCE_SCORE DESC, k.IS_FOUNDATIONAL DESC, k.CREATED_AT DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(search_query, params)
        results = cursor.fetchall()
        cursor.close()
        
        # Enhanced result processing
        enhanced_results = []
        for result in results:
            # Add compatibility fields
            result['similarity_score'] = min(result.get('RELEVANCE_SCORE', 1.0) / 3.0, 1.0)
            
            # Parse metadata
            try:
                if result.get('METADATA'):
                    result['parsed_metadata'] = json.loads(result['METADATA'])
                if result.get('TAGS'):
                    result['parsed_tags'] = json.loads(result['TAGS'])
            except Exception:
                pass
            
            # Add chunk information
            if result.get('TOTAL_CHUNKS', 1) > 1:
                result['chunk_info'] = f"Part {result.get('CHUNK_INDEX', 0) + 1} of {result.get('TOTAL_CHUNKS', 1)}"
            
            enhanced_results.append(result)
        
        return enhanced_results

    async def get_knowledge_analytics(self) -> Dict[str, Any]:
        """Get comprehensive knowledge base analytics"""
        cursor = self.connection.cursor(DictCursor)
        
        analytics = {}
        
        # Overall statistics
        cursor.execute("""
        SELECT 
            COUNT(*) as TOTAL_ENTRIES,
            COUNT(DISTINCT CATEGORY_ID) as TOTAL_CATEGORIES,
            COUNT(CASE WHEN IS_FOUNDATIONAL = TRUE THEN 1 END) as FOUNDATIONAL_ENTRIES,
            AVG(IMPORTANCE_SCORE) as AVG_IMPORTANCE,
            SUM(FILE_SIZE_BYTES) as TOTAL_SIZE_BYTES,
            COUNT(CASE WHEN TOTAL_CHUNKS > 1 THEN 1 END) as CHUNKED_FILES
        FROM KNOWLEDGE_BASE_ENTRIES
        """)
        
        overall_stats = cursor.fetchone()
        analytics['overall'] = overall_stats
        
        # Category breakdown
        cursor.execute("""
        SELECT 
            c.CATEGORY_NAME,
            c.IMPORTANCE_WEIGHT,
            COUNT(k.ENTRY_ID) as ENTRY_COUNT,
            AVG(k.IMPORTANCE_SCORE) as AVG_IMPORTANCE,
            COUNT(CASE WHEN k.IS_FOUNDATIONAL = TRUE THEN 1 END) as FOUNDATIONAL_COUNT,
            SUM(k.FILE_SIZE_BYTES) as CATEGORY_SIZE_BYTES
        FROM KNOWLEDGE_CATEGORIES c
        LEFT JOIN KNOWLEDGE_BASE_ENTRIES k ON c.CATEGORY_ID = k.CATEGORY_ID
        GROUP BY c.CATEGORY_ID, c.CATEGORY_NAME, c.IMPORTANCE_WEIGHT
        ORDER BY ENTRY_COUNT DESC
        """)
        
        category_stats = cursor.fetchall()
        analytics['by_category'] = category_stats
        
        # Recent activity
        cursor.execute("""
        SELECT 
            DATE(CREATED_AT) as ACTIVITY_DATE,
            COUNT(*) as ENTRIES_ADDED,
            SUM(FILE_SIZE_BYTES) as BYTES_ADDED
        FROM KNOWLEDGE_BASE_ENTRIES
        WHERE CREATED_AT >= DATEADD(day, -30, CURRENT_TIMESTAMP())
        GROUP BY DATE(CREATED_AT)
        ORDER BY ACTIVITY_DATE DESC
        """)
        
        recent_activity = cursor.fetchall()
        analytics['recent_activity'] = recent_activity
        
        cursor.close()
        return analytics

    async def disconnect(self):
        """Clean disconnect"""
        if self.connection:
            self.connection.close()
            logger.info("Enhanced Knowledge Service disconnected")

# Global service instance
knowledge_service = EnhancedKnowledgeService() 