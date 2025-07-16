from fastapi.responses import HTMLResponse

async def handler(request, response):
    return HTMLResponse(
        """
    <html>
    <head><title>Sophia AI API</title></head>
    <body>
        <h1>Sophia AI Backend API</h1>
        <h2>Available Endpoints:</h2>
        <ul>
            <li>GET /api/health - Health check</li>
            <li>POST /api/chat - Chat with AI</li>
            <li>GET /api/status - System status</li>
        </ul>
    </body>
    </html>
    """
    )
