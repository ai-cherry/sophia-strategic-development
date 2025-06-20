from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import uuid
import os
import tempfile
from pathlib import Path

from backend.agents.specialized.insight_extraction_agent import InsightExtractionAgent, InsightType
from backend.agents.core.base_agent import AgentConfig, Task
from backend.knowledge.knowledge_manager import knowledge_manager
from backend.integrations.portkey_client import PortkeyClient
from backend.knowledge_base.ingestion import IngestionPipeline
from backend.knowledge_base.vector_store import VectorStore
from backend.knowledge_base.metadata_store import MetadataStore

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])

# Initialize components
insight_agent = InsightExtractionAgent(AgentConfig(name="InsightExtractionAgent"))
portkey_client = PortkeyClient()
vector_store = VectorStore()
metadata_store = MetadataStore()
ingestion_pipeline = IngestionPipeline(vector_store, metadata_store)


@router.post("/documents/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    category: str = Form("general"),
    tags: Optional[str] = Form(None)
):
    """Upload multiple documents to the knowledge base"""
    results = []
    
    for file in files:
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                tmp_path = Path(tmp_file.name)
            
            # Parse tags
            file_tags = tags.split(",") if tags else []
            
            # Ingest the document
            await ingestion_pipeline.ingest_document(
                file_path=tmp_path,
                document_type=category,
                tags=file_tags
            )
            
            # Clean up temp file
            os.unlink(tmp_path)
            
            results.append({
                "filename": file.filename,
                "status": "success",
                "message": "Document uploaded successfully"
            })
            
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "error",
                "message": str(e)
            })
    
    return {"results": results}


@router.get("/documents")
async def get_documents(
    search: Optional[str] = None,
    content_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50
):
    """Get documents from the knowledge base"""
    # This would integrate with the actual knowledge base
    # For now, returning mock data that matches the frontend
    documents = [
        {
            "id": "company_mission",
            "title": "Pay Ready Mission Statement",
            "content": "Pay Ready is dedicated to revolutionizing payment processing...",
            "contentType": "company_core",
            "status": "published",
            "tags": ["mission", "values", "company"],
            "createdAt": "2024-01-15",
            "updatedAt": "2024-01-20",
            "createdBy": "admin",
            "version": 2
        },
        {
            "id": "product_catalog",
            "title": "Product & Service Catalog",
            "content": "Our comprehensive suite of payment solutions includes...",
            "contentType": "products_services",
            "status": "published",
            "tags": ["products", "services", "catalog"],
            "createdAt": "2024-01-10",
            "updatedAt": "2024-01-18",
            "createdBy": "admin",
            "version": 3
        }
    ]
    
    # Apply filters
    if search:
        documents = [d for d in documents if search.lower() in d["title"].lower() or search.lower() in d["content"].lower()]
    if content_type and content_type != "all":
        documents = [d for d in documents if d["contentType"] == content_type]
    if status and status != "all":
        documents = [d for d in documents if d["status"] == status]
    
    return {"documents": documents[:limit]}


@router.post("/documents")
async def create_document(document: Dict[str, Any]):
    """Create a new document in the knowledge base"""
    doc_id = f"doc_{uuid.uuid4().hex[:8]}"
    
    # Create document with metadata
    new_doc = {
        "id": doc_id,
        "title": document["title"],
        "content": document["content"],
        "contentType": document["contentType"],
        "status": document.get("status", "draft"),
        "tags": document.get("tags", []),
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
        "createdBy": "admin",
        "version": 1
    }
    
    # TODO: Actually save to knowledge base
    
    return {"document": new_doc}


@router.put("/documents/{document_id}")
async def update_document(document_id: str, document: Dict[str, Any]):
    """Update an existing document"""
    # TODO: Implement actual update logic
    updated_doc = {
        "id": document_id,
        **document,
        "updatedAt": datetime.now().isoformat(),
        "version": document.get("version", 1) + 1
    }
    
    return {"document": updated_doc}


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document from the knowledge base"""
    # TODO: Implement actual deletion
    return {"message": f"Document {document_id} deleted successfully"}


@router.get("/insights/pending")
async def get_pending_insights():
    """Get pending insights from the discovery queue"""
    task = Task(task_type="get_pending_insights", task_data={})
    result = await insight_agent.process_task(task)
    
    if result.get("success"):
        return result.get("data", {})
    else:
        raise HTTPException(status_code=500, detail=result.get("error"))


@router.post("/insights/analyze")
async def analyze_call_for_insights(call_id: str):
    """Analyze a specific Gong call for insights"""
    task = Task(
        task_type="analyze_transcript_for_insights",
        task_data={"call_id": call_id}
    )
    result = await insight_agent.process_task(task)
    
    if result.get("success"):
        return result.get("data", {})
    else:
        raise HTTPException(status_code=500, detail=result.get("error"))


@router.post("/insights/batch-analyze")
async def batch_analyze_recent_calls(hours_back: int = 24):
    """Analyze recent calls for insights in batch"""
    task = Task(
        task_type="batch_analyze_recent_calls",
        task_data={"hours_back": hours_back}
    )
    result = await insight_agent.process_task(task)
    
    if result.get("success"):
        return result.get("data", {})
    else:
        raise HTTPException(status_code=500, detail=result.get("error"))


@router.put("/insights/{insight_id}/status")
async def update_insight_status(
    insight_id: str,
    status: str,
    edited_content: Optional[str] = None
):
    """Update the status of an insight (approve/reject)"""
    task = Task(
        task_type="update_insight_status",
        task_data={
            "insight_id": insight_id,
            "status": status,
            "edited_content": edited_content
        }
    )
    result = await insight_agent.process_task(task)
    
    if result.get("success"):
        return result.get("data", {})
    else:
        raise HTTPException(status_code=500, detail=result.get("error"))


@router.post("/curation/chat")
async def curation_chat(query: str):
    """Handle curation chat queries"""
    try:
        # Search the knowledge base
        search_results = await vector_store.query(query, top_k=3)
        
        if search_results:
            # Get the most relevant result
            top_result = search_results[0]
            
            # Prepare response with source citation
            response = {
                "content": top_result.get("content", "No information found"),
                "source": top_result.get("metadata", {}).get("file_name", "Unknown source"),
                "confidence": top_result.get("score", 0.0),
                "needsFeedback": True
            }
        else:
            # Use LLM to generate a response if no direct match
            llm_prompt = f"""
            The user is asking about: {query}
            
            Based on Pay Ready's business context, provide a helpful response.
            If you don't have specific information, indicate that clearly.
            """
            
            llm_response = await portkey_client.llm_call(
                prompt=llm_prompt,
                model="gpt-4",
                temperature=0.3
            )
            
            response_content = llm_response.get("choices", [{}])[0].get("message", {}).get("content", "I don't have information about that.")
            
            response = {
                "content": response_content,
                "source": "Generated response - no direct source",
                "confidence": 0.5,
                "needsFeedback": True
            }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/curation/feedback")
async def submit_curation_feedback(
    message_id: str,
    feedback: str,
    correction: Optional[str] = None
):
    """Submit feedback on a curation response"""
    if feedback == "incorrect" and correction:
        # TODO: Update the knowledge base with the correction
        # This would create a new high-priority entry
        pass
    
    return {
        "message": f"Feedback recorded: {feedback}",
        "correction_applied": bool(correction)
    }


@router.get("/analytics/stats")
async def get_knowledge_stats():
    """Get analytics stats for the knowledge base"""
    # TODO: Get real stats from the knowledge base
    return {
        "totalDocuments": 47,
        "publishedDocuments": 42,
        "draftDocuments": 5,
        "totalSearches": 1247,
        "avgResponseTime": "185ms",
        "knowledgeCoverage": 87,
        "recentActivity": [
            {
                "action": "update",
                "document": "Product Catalog",
                "timestamp": "2 hours ago"
            },
            {
                "action": "create",
                "document": "Sales Process",
                "timestamp": "1 day ago"
            },
            {
                "action": "review",
                "document": "Mission Statement",
                "timestamp": "3 days ago"
            }
        ]
    } 