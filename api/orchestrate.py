import json
from datetime import datetime

def handler(request):
    # Simple echo response for now
    body = json.loads(request.body) if request.body else {}

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(
            {
                "response": f"I received your message: {body.get('message', 'No message')}",
                "timestamp": datetime.utcnow().isoformat(),
                "model": "sophia-ai",
                "usage": {"total_tokens": 100},
            }
        ),
    }
