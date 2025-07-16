#!/usr/bin/env python3
"""
🚀 Large File Processor MCP Server
Integrates large file ingestion capabilities with Cursor IDE via MCP protocol

Tools:
- start_large_file_download: Download large files from URLs
- get_processing_status: Check status of file processing jobs
- extract_archive: Extract ZIP/TAR archives safely
- analyze_files: Analyze file contents with AI
- list_processing_jobs: List all processing jobs
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import json

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

from backend.services.large_file_ingestion_service import (
    get_large_file_service, ProcessingStatus
)
from backend.services.archive_processor import get_archive_processor
from backend.services.binary_file_handler import get_binary_file_handler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("large_file_processor_mcp")

# Create MCP server instance
server = Server("large-file-processor")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools for large file processing"""
    return [
        types.Tool(
            name="start_large_file_download",
            description="Download large files from URLs with progress tracking",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL of the file to download"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Optional custom filename for the download"
                    }
                },
                "required": ["url"]
            }
        ),
        types.Tool(
            name="get_processing_status",
            description="Get the status of a file processing job",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_id": {
                        "type": "string",
                        "description": "ID of the job to check"
                    }
                },
                "required": ["job_id"]
            }
        ),
        types.Tool(
            name="list_processing_jobs",
            description="List all file processing jobs with optional status filter",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["pending", "downloading", "processing", "completed", "failed", "cancelled"],
                        "description": "Filter jobs by status"
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 20,
                        "description": "Maximum number of jobs to return"
                    }
                }
            }
        ),
        types.Tool(
            name="extract_archive",
            description="Extract ZIP, TAR, or other archive files with security validation",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_id": {
                        "type": "string",
                        "description": "ID of the job containing the archive file"
                    },
                    "safe_mode": {
                        "type": "boolean",
                        "default": True,
                        "description": "Enable security checks during extraction"
                    }
                },
                "required": ["job_id"]
            }
        ),
        types.Tool(
            name="analyze_files",
            description="Analyze extracted files for content, metadata, and insights",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_id": {
                        "type": "string",
                        "description": "ID of the job with extracted files to analyze"
                    },
                    "extract_content": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether to extract text content from files"
                    },
                    "ai_analysis": {
                        "type": "boolean",
                        "default": False,
                        "description": "Perform AI-powered content analysis"
                    }
                },
                "required": ["job_id"]
            }
        ),
        types.Tool(
            name="get_processing_stats",
            description="Get overall statistics for all file processing operations",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="cancel_job",
            description="Cancel a running job or delete a completed job",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_id": {
                        "type": "string",
                        "description": "ID of the job to cancel"
                    }
                },
                "required": ["job_id"]
            }
        ),
        types.Tool(
            name="cleanup_old_jobs",
            description="Clean up old completed or failed jobs to free up space",
            inputSchema={
                "type": "object",
                "properties": {
                    "days_old": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 30,
                        "default": 7,
                        "description": "Remove jobs older than this many days"
                    }
                }
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls for large file processing"""
    try:
        if name == "start_large_file_download":
            return await _start_large_file_download(arguments)
        elif name == "get_processing_status":
            return await _get_processing_status(arguments)
        elif name == "list_processing_jobs":
            return await _list_processing_jobs(arguments)
        elif name == "extract_archive":
            return await _extract_archive(arguments)
        elif name == "analyze_files":
            return await _analyze_files(arguments)
        elif name == "get_processing_stats":
            return await _get_processing_stats(arguments)
        elif name == "cancel_job":
            return await _cancel_job(arguments)
        elif name == "cleanup_old_jobs":
            return await _cleanup_old_jobs(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        logger.error(f"❌ Tool call failed: {name} - {e}")
        return [types.TextContent(type="text", text=f"❌ Error: {str(e)}")]

async def _start_large_file_download(arguments: dict) -> list[types.TextContent]:
    """Start downloading a large file"""
    try:
        url = arguments["url"]
        filename = arguments.get("filename")
        
        service = await get_large_file_service()
        job_id = await service.start_download(url=url, filename=filename)
        
        job = await service.get_job_status(job_id)
        
        result = {
            "success": True,
            "job_id": job_id,
            "message": f"Started downloading {job.filename}",
            "job_details": {
                "filename": job.filename,
                "total_size": job.total_size,
                "status": job.status.value,
                "created_at": job.created_at.isoformat()
            }
        }
        
        return [types.TextContent(
            type="text", 
            text=f"🔄 **Download Started**\n\n"
                 f"**Job ID:** {job_id}\n"
                 f"**File:** {job.filename}\n"
                 f"**Size:** {job.total_size:,} bytes\n"
                 f"**Status:** {job.status.value}\n\n"
                 f"Use `get_processing_status` with job ID `{job_id}` to check progress.\n\n"
                 f"```json\n{json.dumps(result, indent=2)}\n```"
        )]
        
    except Exception as e:
        logger.error(f"❌ Failed to start download: {e}")
        return [types.TextContent(
            type="text", 
            text=f"❌ **Download Failed**\n\nError: {str(e)}"
        )]

async def _get_processing_status(arguments: dict) -> list[types.TextContent]:
    """Get status of a processing job"""
    try:
        job_id = arguments["job_id"]
        
        service = await get_large_file_service()
        job = await service.get_job_status(job_id)
        
        if not job:
            return [types.TextContent(
                type="text", 
                text=f"❌ **Job Not Found**\n\nJob ID `{job_id}` does not exist."
            )]
        
        # Status emoji mapping
        status_emoji = {
            "pending": "⏳",
            "downloading": "📥",
            "processing": "⚙️",
            "completed": "✅",
            "failed": "❌",
            "cancelled": "🛑"
        }
        
        emoji = status_emoji.get(job.status.value, "❓")
        
        status_text = f"{emoji} **Job Status: {job.status.value.title()}**\n\n"
        status_text += f"**Job ID:** {job_id}\n"
        status_text += f"**File:** {job.filename}\n"
        status_text += f"**Progress:** {job.progress_percentage:.1f}%\n"
        status_text += f"**Downloaded:** {job.downloaded_size:,} / {job.total_size:,} bytes\n"
        status_text += f"**Chunks:** {job.chunks_completed} / {job.total_chunks}\n"
        status_text += f"**Created:** {job.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        status_text += f"**Updated:** {job.updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        if job.error_message:
            status_text += f"\n⚠️ **Error:** {job.error_message}\n"
        
        if job.file_hash:
            status_text += f"\n**Hash:** `{job.file_hash}`\n"
        
        if job.metadata:
            status_text += f"\n**Metadata:**\n```json\n{json.dumps(job.metadata, indent=2)}\n```"
        
        result = {
            "job_id": job.job_id,
            "filename": job.filename,
            "status": job.status.value,
            "progress_percentage": job.progress_percentage,
            "downloaded_size": job.downloaded_size,
            "total_size": job.total_size,
            "error_message": job.error_message,
            "metadata": job.metadata
        }
        
        status_text += f"\n\n```json\n{json.dumps(result, indent=2)}\n```"
        
        return [types.TextContent(type="text", text=status_text)]
        
    except Exception as e:
        logger.error(f"❌ Failed to get job status: {e}")
        return [types.TextContent(
            type="text", 
            text=f"❌ **Status Check Failed**\n\nError: {str(e)}"
        )]

async def _list_processing_jobs(arguments: dict) -> list[types.TextContent]:
    """List all processing jobs"""
    try:
        status_filter = arguments.get("status")
        limit = arguments.get("limit", 20)
        
        service = await get_large_file_service()
        
        # Convert status string to enum if provided
        filter_enum = None
        if status_filter:
            try:
                filter_enum = ProcessingStatus(status_filter.lower())
            except ValueError:
                return [types.TextContent(
                    type="text", 
                    text=f"❌ **Invalid Status Filter**\n\nValid statuses: pending, downloading, processing, completed, failed, cancelled"
                )]
        
        jobs = await service.list_jobs(status_filter=filter_enum)
        jobs = jobs[:limit]  # Apply limit
        
        if not jobs:
            filter_text = f" with status '{status_filter}'" if status_filter else ""
            return [types.TextContent(
                type="text", 
                text=f"📋 **No Jobs Found**\n\nNo processing jobs found{filter_text}."
            )]
        
        # Create summary
        status_counts = {}
        total_size = 0
        
        for job in jobs:
            status = job.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
            if job.status == ProcessingStatus.COMPLETED:
                total_size += job.downloaded_size
        
        summary_text = f"📋 **Processing Jobs ({len(jobs)} total)**\n\n"
        
        # Status summary
        for status, count in status_counts.items():
            emoji = {"pending": "⏳", "downloading": "📥", "processing": "⚙️", 
                    "completed": "✅", "failed": "❌", "cancelled": "🛑"}.get(status, "❓")
            summary_text += f"{emoji} {status.title()}: {count}\n"
        
        summary_text += f"\n💾 **Total Size Processed:** {total_size:,} bytes\n\n"
        
        # Job list
        summary_text += "**Recent Jobs:**\n"
        for job in jobs[:10]:  # Show top 10 jobs
            emoji = {"pending": "⏳", "downloading": "📥", "processing": "⚙️", 
                    "completed": "✅", "failed": "❌", "cancelled": "🛑"}.get(job.status.value, "❓")
            
            summary_text += f"\n{emoji} **{job.filename}**\n"
            summary_text += f"   ID: `{job.job_id}`\n"
            summary_text += f"   Status: {job.status.value} ({job.progress_percentage:.1f}%)\n"
            summary_text += f"   Size: {job.downloaded_size:,} / {job.total_size:,} bytes\n"
            summary_text += f"   Created: {job.created_at.strftime('%Y-%m-%d %H:%M')}\n"
        
        if len(jobs) > 10:
            summary_text += f"\n... and {len(jobs) - 10} more jobs\n"
        
        # Add JSON data
        jobs_data = []
        for job in jobs:
            jobs_data.append({
                "job_id": job.job_id,
                "filename": job.filename,
                "status": job.status.value,
                "progress_percentage": job.progress_percentage,
                "file_size": job.total_size,
                "downloaded_size": job.downloaded_size,
                "created_at": job.created_at.isoformat()
            })
        
        summary_text += f"\n```json\n{json.dumps({'jobs': jobs_data, 'total_count': len(jobs)}, indent=2)}\n```"
        
        return [types.TextContent(type="text", text=summary_text)]
        
    except Exception as e:
        logger.error(f"❌ Failed to list jobs: {e}")
        return [types.TextContent(
            type="text", 
            text=f"❌ **Job Listing Failed**\n\nError: {str(e)}"
        )]

async def _extract_archive(arguments: dict) -> list[types.TextContent]:
    """Extract an archive file"""
    try:
        job_id = arguments["job_id"]
        safe_mode = arguments.get("safe_mode", True)
        
        service = await get_large_file_service()
        job = await service.get_job_status(job_id)
        
        if not job:
            return [types.TextContent(
                type="text", 
                text=f"❌ **Job Not Found**\n\nJob ID `{job_id}` does not exist."
            )]
        
        if job.status != ProcessingStatus.COMPLETED:
            return [types.TextContent(
                type="text", 
                text=f"❌ **Job Not Ready**\n\nJob must be completed before extraction. Current status: {job.status.value}"
            )]
        
        # Get file path
        file_path = Path(service.download_dir) / job.filename
        if not file_path.exists():
            return [types.TextContent(
                type="text", 
                text=f"❌ **File Not Found**\n\nDownloaded file not found: {job.filename}"
            )]
        
        # Extract archive
        archive_processor = await get_archive_processor()
        
        # First analyze the archive
        archive_info = await archive_processor.analyze_archive(file_path)
        
        analysis_text = f"📦 **Archive Analysis**\n\n"
        analysis_text += f"**Type:** {archive_info.archive_type.value}\n"
        analysis_text += f"**Files:** {archive_info.total_files:,}\n"
        analysis_text += f"**Total Size:** {archive_info.total_size:,} bytes\n"
        analysis_text += f"**Compressed Size:** {archive_info.compressed_size:,} bytes\n"
        analysis_text += f"**Compression Ratio:** {archive_info.compression_ratio:.1f}x\n"
        
        if archive_info.security_warnings:
            analysis_text += f"\n⚠️ **Security Warnings:**\n"
            for warning in archive_info.security_warnings[:5]:
                analysis_text += f"   • {warning}\n"
        
        # Extract the archive
        extraction_result = await archive_processor.extract_archive(
            file_path, job_id, safe_mode=safe_mode
        )
        
        if not extraction_result.success:
            return [types.TextContent(
                type="text", 
                text=f"{analysis_text}\n\n❌ **Extraction Failed**\n\nError: {extraction_result.error_message}"
            )]
        
        # Update job metadata
        job.metadata.update({
            "archive_extracted": True,
            "extracted_files_count": len(extraction_result.extracted_files),
            "extraction_path": str(extraction_result.extraction_path),
            "total_extracted_size": extraction_result.total_extracted_size,
            "security_violations": extraction_result.security_violations
        })
        
        await service._save_job_state(job)
        
        result_text = f"{analysis_text}\n\n✅ **Extraction Successful**\n\n"
        result_text += f"**Extracted Files:** {len(extraction_result.extracted_files):,}\n"
        result_text += f"**Skipped Files:** {len(extraction_result.skipped_files):,}\n"
        result_text += f"**Total Size:** {extraction_result.total_extracted_size:,} bytes\n"
        result_text += f"**Location:** `{extraction_result.extraction_path}`\n"
        
        if extraction_result.security_violations:
            result_text += f"\n🛡️ **Security Violations Detected:**\n"
            for violation in extraction_result.security_violations[:5]:
                result_text += f"   • {violation}\n"
        
        result_text += f"\nUse `analyze_files` with job ID `{job_id}` to analyze the extracted content.\n"
        
        # Add JSON data
        result_data = {
            "success": True,
            "job_id": job_id,
            "extracted_files": len(extraction_result.extracted_files),
            "skipped_files": len(extraction_result.skipped_files),
            "total_size": extraction_result.total_extracted_size,
            "extraction_path": str(extraction_result.extraction_path),
            "security_violations": extraction_result.security_violations
        }
        
        result_text += f"\n```json\n{json.dumps(result_data, indent=2)}\n```"
        
        return [types.TextContent(type="text", text=result_text)]
        
    except Exception as e:
        logger.error(f"❌ Failed to extract archive: {e}")
        return [types.TextContent(
            type="text", 
            text=f"❌ **Extraction Failed**\n\nError: {str(e)}"
        )]

async def _analyze_files(arguments: dict) -> list[types.TextContent]:
    """Analyze extracted files"""
    try:
        job_id = arguments["job_id"]
        extract_content = arguments.get("extract_content", True)
        ai_analysis = arguments.get("ai_analysis", False)
        
        service = await get_large_file_service()
        job = await service.get_job_status(job_id)
        
        if not job:
            return [types.TextContent(
                type="text", 
                text=f"❌ **Job Not Found**\n\nJob ID `{job_id}` does not exist."
            )]
        
        if not job.metadata.get("archive_extracted"):
            return [types.TextContent(
                type="text", 
                text=f"❌ **Archive Not Extracted**\n\nExtract the archive first using `extract_archive`."
            )]
        
        extraction_path = Path(job.metadata.get("extraction_path", ""))
        if not extraction_path.exists():
            return [types.TextContent(
                type="text", 
                text=f"❌ **Extraction Directory Not Found**\n\nPath: {extraction_path}"
            )]
        
        # Process all extracted files
        file_handler = await get_binary_file_handler()
        processing_results = await file_handler.process_directory(
            extraction_path, recursive=True
        )
        
        # Get statistics
        stats = file_handler.get_processing_stats(processing_results)
        
        analysis_text = f"🔍 **File Analysis Results**\n\n"
        analysis_text += f"**Total Files:** {stats['total_files']:,}\n"
        analysis_text += f"**Successful:** {stats['successful']:,}\n"
        analysis_text += f"**Failed:** {stats['failed']:,}\n"
        analysis_text += f"**Success Rate:** {stats['success_rate']:.1f}%\n"
        analysis_text += f"**Total Size:** {stats['total_size_bytes']:,} bytes\n"
        analysis_text += f"**Processing Time:** {stats['total_processing_time']:.2f}s\n\n"
        
        # Category breakdown
        if stats['categories']:
            analysis_text += f"**File Categories:**\n"
            for category, count in stats['categories'].items():
                analysis_text += f"   📄 {category.title()}: {count}\n"
        
        # Show sample files
        analysis_text += f"\n**Sample Analysis Results:**\n"
        
        successful_results = [r for r in processing_results if r.success][:5]
        for result in successful_results:
            metadata = result.metadata
            analysis_text += f"\n📄 **{metadata.filename}**\n"
            analysis_text += f"   Category: {metadata.file_category.value}\n"
            analysis_text += f"   Size: {metadata.file_size:,} bytes\n"
            analysis_text += f"   Type: {metadata.mime_type}\n"
            
            if metadata.word_count > 0:
                analysis_text += f"   Words: {metadata.word_count:,}\n"
            
            if metadata.content_summary:
                summary = metadata.content_summary[:100] + "..." if len(metadata.content_summary) > 100 else metadata.content_summary
                analysis_text += f"   Summary: {summary}\n"
            
            if metadata.extracted_entities:
                entities = ", ".join(metadata.extracted_entities[:5])
                analysis_text += f"   Entities: {entities}\n"
        
        # Update job metadata
        job.metadata.update({
            "files_analyzed": True,
            "analysis_stats": stats,
            "analysis_timestamp": datetime.now().isoformat()
        })
        await service._save_job_state(job)
        
        # Add JSON data
        analysis_data = {
            "job_id": job_id,
            "stats": stats,
            "sample_files": [
                {
                    "filename": r.metadata.filename,
                    "category": r.metadata.file_category.value,
                    "size": r.metadata.file_size,
                    "mime_type": r.metadata.mime_type,
                    "word_count": r.metadata.word_count,
                    "summary": r.metadata.content_summary[:200] if r.metadata.content_summary else None
                }
                for r in successful_results[:10]
            ]
        }
        
        analysis_text += f"\n```json\n{json.dumps(analysis_data, indent=2)}\n```"
        
        return [types.TextContent(type="text", text=analysis_text)]
        
    except Exception as e:
        logger.error(f"❌ Failed to analyze files: {e}")
        return [types.TextContent(
            type="text", 
            text=f"❌ **File Analysis Failed**\n\nError: {str(e)}"
        )]

async def _get_processing_stats(arguments: dict) -> list[types.TextContent]:
    """Get overall processing statistics"""
    try:
        service = await get_large_file_service()
        jobs = await service.list_jobs()
        
        # Calculate statistics
        total_jobs = len(jobs)
        active_jobs = len([j for j in jobs if j.status in [ProcessingStatus.PENDING, ProcessingStatus.DOWNLOADING, ProcessingStatus.PROCESSING]])
        completed_jobs = len([j for j in jobs if j.status == ProcessingStatus.COMPLETED])
        failed_jobs = len([j for j in jobs if j.status == ProcessingStatus.FAILED])
        
        total_size_processed = sum(j.downloaded_size for j in jobs if j.status == ProcessingStatus.COMPLETED)
        total_files_analyzed = sum(1 for j in jobs if j.metadata.get("files_analyzed"))
        
        # Status breakdown
        status_counts = {}
        for job in jobs:
            status = job.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        stats_text = f"📊 **Processing Statistics**\n\n"
        stats_text += f"**Total Jobs:** {total_jobs:,}\n"
        stats_text += f"**Active Jobs:** {active_jobs:,}\n"
        stats_text += f"**Completed Jobs:** {completed_jobs:,}\n"
        stats_text += f"**Failed Jobs:** {failed_jobs:,}\n"
        stats_text += f"**Success Rate:** {(completed_jobs / max(total_jobs, 1)) * 100:.1f}%\n\n"
        
        stats_text += f"**Data Processed:**\n"
        stats_text += f"   💾 Total Size: {total_size_processed:,} bytes ({total_size_processed / 1024 / 1024:.1f} MB)\n"
        stats_text += f"   📄 Files Analyzed: {total_files_analyzed:,}\n\n"
        
        if status_counts:
            stats_text += f"**Status Breakdown:**\n"
            for status, count in status_counts.items():
                emoji = {"pending": "⏳", "downloading": "📥", "processing": "⚙️", 
                        "completed": "✅", "failed": "❌", "cancelled": "🛑"}.get(status, "❓")
                stats_text += f"   {emoji} {status.title()}: {count:,}\n"
        
        # Recent activity
        recent_jobs = [j for j in jobs if j.status == ProcessingStatus.COMPLETED][-5:]
        if recent_jobs:
            stats_text += f"\n**Recent Completions:**\n"
            for job in recent_jobs:
                stats_text += f"   ✅ {job.filename} ({job.downloaded_size:,} bytes)\n"
        
        # Create JSON data
        stats_data = {
            "total_jobs": total_jobs,
            "active_jobs": active_jobs,
            "completed_jobs": completed_jobs,
            "failed_jobs": failed_jobs,
            "success_rate": (completed_jobs / max(total_jobs, 1)) * 100,
            "total_size_processed": total_size_processed,
            "files_analyzed": total_files_analyzed,
            "status_breakdown": status_counts
        }
        
        stats_text += f"\n```json\n{json.dumps(stats_data, indent=2)}\n```"
        
        return [types.TextContent(type="text", text=stats_text)]
        
    except Exception as e:
        logger.error(f"❌ Failed to get stats: {e}")
        return [types.TextContent(
            type="text", 
            text=f"❌ **Statistics Failed**\n\nError: {str(e)}"
        )]

async def _cancel_job(arguments: dict) -> list[types.TextContent]:
    """Cancel a processing job"""
    try:
        job_id = arguments["job_id"]
        
        service = await get_large_file_service()
        success = await service.cancel_job(job_id)
        
        if not success:
            return [types.TextContent(
                type="text", 
                text=f"❌ **Job Not Found**\n\nJob ID `{job_id}` does not exist."
            )]
        
        return [types.TextContent(
            type="text", 
            text=f"🛑 **Job Cancelled**\n\nJob `{job_id}` has been cancelled successfully."
        )]
        
    except Exception as e:
        logger.error(f"❌ Failed to cancel job: {e}")
        return [types.TextContent(
            type="text", 
            text=f"❌ **Cancellation Failed**\n\nError: {str(e)}"
        )]

async def _cleanup_old_jobs(arguments: dict) -> list[types.TextContent]:
    """Clean up old jobs"""
    try:
        days_old = arguments.get("days_old", 7)
        
        service = await get_large_file_service()
        cleaned_count = await service.cleanup_old_jobs(days_old=days_old)
        
        return [types.TextContent(
            type="text", 
            text=f"🧹 **Cleanup Complete**\n\nRemoved {cleaned_count:,} jobs older than {days_old} days."
        )]
        
    except Exception as e:
        logger.error(f"❌ Failed to cleanup jobs: {e}")
        return [types.TextContent(
            type="text", 
            text=f"❌ **Cleanup Failed**\n\nError: {str(e)}"
        )]

async def main():
    """Main entry point for the MCP server"""
    # Serve the MCP server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="large-file-processor",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main()) 