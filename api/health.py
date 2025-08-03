import json

def handler(event, context):
    """Health check endpoint for Vercel"""
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': json.dumps({
            "status": "healthy",
            "service": "Invoice Chain Agent",
            "version": "1.0.0",
            "blockchain": {
                "canister_id": "uxrrr-q7777-77774-qaaaq-cai",
                "network": "testnet"
            },
            "serverless": True,
            "platform": "vercel"
        })
    }
