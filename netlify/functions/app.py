import serverless_wsgi
from app import app
import sys

def handler(event, context):
    print(f"Path: {event.get('path')}, Query Params: {event.get('queryStringParameters')}")
    try:
        return serverless_wsgi.handle_request(app, event, context)
    except Exception as e:
        print(f"Error handling request: {e}")
        return {
            "statusCode": 500,
            "body": f"Internal Server Error: {str(e)}"
        }