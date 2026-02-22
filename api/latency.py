import json
import numpy as np
import os

def handler(request, context):

    # CORS preflight
    if request.method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            },
            "body": ""
        }

    if request.method != "POST":
        return {
            "statusCode": 405,
            "headers": {
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({"error": "Method not allowed"})
        }

    # Proper body parsing for Vercel
    try:
        body = json.loads(request.body.decode())
    except:
        body = {}

    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 0)

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(BASE_DIR, "q-vercel-latency.json")

    with open(file_path) as f:
        data = json.load(f)

    response = {}

    for region in regions:
        records = [r for r in data if r["region"] == region]
        if not records:
            continue

        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime"] for r in records]

        response[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": sum(1 for l in latencies if l > threshold),
        }

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Content-Type": "application/json",
        },
        "body": json.dumps(response),
    }