import json
from backend.services.sophia_unified_orchestrator import get_unified_orchestrator
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

async def handler(request, response):
    if request.method != "POST":
        return JSONResponse({"error": "Method not allowed"}, status_code=405)

    try:
        body = json.loads(request.body)
        orchestrator = get_unified_orchestrator()
        result = await orchestrator.process_request(
            query=body.get("query", ""),
            user_id=body.get("user_id", "user_default"),
            conversation_id=body.get("conversation_id"),
            context=body.get("context", {}),
        )
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
