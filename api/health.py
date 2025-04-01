from http.server import BaseHTTPRequestHandler
import json

def handler(request):
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "status": "healthy"
        })
    } 