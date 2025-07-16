from fastapi.responses import JSONResponse

async def handler(request, response):
    return JSONResponse(
        {"status": "healthy", "service": "sophia-ai-backend", "version": "4.0.0"}
    )
