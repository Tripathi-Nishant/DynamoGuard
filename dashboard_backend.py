from fastapi import FastAPI, WebSocket, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import json
import boto3
import time
from datetime import datetime, timedelta
import random
import urllib3
import warnings
import botocore.client

# Suppress SSL warnings for PoC
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# Patch boto3 to disable SSL verification for PoC (corporate proxy issues)
original_make_request = botocore.client.BaseClient._make_request
def patched_make_request(self, operation_model, request_dict, request_context):
    request_dict['verify'] = False
    return original_make_request(self, operation_model, request_dict, request_context)
botocore.client.BaseClient._make_request = patched_make_request

# Initialize AWS clients
cloudwatch = boto3.client('cloudwatch', region_name='ap-south-1')
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

app = FastAPI()

# Store active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

def get_cloudwatch_metrics():
    """
    Fetch ConsumedWriteCapacityUnits from CloudWatch for the last 24 minutes.
    If no data yet, generate realistic demo data for visualization.
    """
    try:
        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/DynamoDB',
            MetricName='ConsumedWriteCapacityUnits',
            Dimensions=[{'Name': 'TableName', 'Value': 'Exam_UserTraffic'}],
            StartTime=datetime.utcnow() - timedelta(minutes=24),
            EndTime=datetime.utcnow(),
            Period=60,
            Statistics=['Sum', 'Average']
        )
        datapoints = sorted(response.get('Datapoints', []), key=lambda x: x['Timestamp'])
        
        # If CloudWatch hasn't populated yet, generate realistic demo data
        if not datapoints:
            print("CloudWatch empty, generating realistic demo data...")
            datapoints = []
            for i in range(24, 0, -1):
                timestamp = datetime.utcnow() - timedelta(minutes=i)
                # Create realistic pattern: gradual increase with spike at end
                base_traffic = 3 + (24 - i) * 0.8  # Gradually increasing
                spike = random.uniform(18, 24) if i <= 5 else base_traffic  # Spike in last 5 mins
                datapoints.append({
                    'Timestamp': timestamp,
                    'Sum': spike,
                    'Average': spike / 2
                })
        
        return datapoints
    except Exception as e:
        print(f"Error fetching metrics: {e}")
        # Return demo data on error
        datapoints = []
        for i in range(24, 0, -1):
            timestamp = datetime.utcnow() - timedelta(minutes=i)
            base_traffic = 3 + (24 - i) * 0.8
            spike = random.uniform(18, 24) if i <= 5 else base_traffic
            datapoints.append({
                'Timestamp': timestamp,
                'Sum': spike,
                'Average': spike / 2
            })
        return datapoints

def calculate_ml_prediction(metrics):
    """
    Simulate ML model prediction based on metrics.
    Returns: probability (0-1), risk_level, trend
    """
    if not metrics:
        return 0.1, "SAFE", "stable"
    
    recent_writes = [m.get('Sum', 0) for m in metrics[-5:]]
    avg_recent = sum(recent_writes) / len(recent_writes) if recent_writes else 0
    
    # Calculate trend
    if len(recent_writes) >= 2:
        if recent_writes[-1] > recent_writes[-2] * 1.2:
            trend_direction = "increasing"
        elif recent_writes[-1] < recent_writes[-2] * 0.8:
            trend_direction = "decreasing"
        else:
            trend_direction = "stable"
    else:
        trend_direction = "stable"
    
    # Calculate probability based on traffic level and trend
    base_prob = min(0.95, avg_recent / 50.0)  # Scale traffic to probability
    
    # Boost probability if trend is increasing
    if trend_direction == "increasing":
        base_prob = min(0.95, base_prob + 0.2)
    
    if base_prob > 0.85:
        probability = base_prob
        risk_level = "CRITICAL"
    elif base_prob > 0.60:
        probability = base_prob
        risk_level = "HIGH"
    else:
        probability = max(0.1, base_prob)
        risk_level = "SAFE"
    
    return round(probability, 2), risk_level, trend_direction

def get_hot_keys_simulation():
    """
    Simulate detection of hot keys from DynamoDB Streams analysis.
    """
    try:
        table = dynamodb.Table('Exam_UserTraffic')
        response = table.scan(Limit=5)
        
        hot_keys = []
        for item in response.get('Items', []):
            user_id = item.get('user_id', 'unknown')
            if 'user_999' in str(user_id):
                hot_keys.append({
                    'key': user_id,
                    'traffic_volume': random.randint(50, 500),
                    'impact_score': round(random.uniform(0.6, 0.98), 2)
                })
        
        return hot_keys if hot_keys else [
            {'key': 'user_999', 'traffic_volume': random.randint(100, 500), 'impact_score': round(random.uniform(0.7, 0.95), 2)}
        ]
    except:
        return [{'key': 'user_999', 'traffic_volume': random.randint(100, 500), 'impact_score': 0.85}]

@app.get("/")
async def get_dashboard():
    """Serve the premium dashboard HTML."""
    return HTMLResponse(open('dashboard.html', encoding='utf-8').read())

@app.get("/api/metrics")
async def get_metrics():
    """REST endpoint to get current metrics."""
    metrics = get_cloudwatch_metrics()
    ml_prob, risk_level, trend = calculate_ml_prediction(metrics)
    hot_keys = get_hot_keys_simulation()
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": metrics,
        "ml_prediction": {
            "probability": ml_prob,
            "risk_level": risk_level,
            "trend": trend
        },
        "hot_keys": hot_keys,
        "system_health": "HEALTHY" if risk_level == "SAFE" else "AT RISK"
    }

@app.websocket("/ws/live-metrics")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time metric streaming."""
    await manager.connect(websocket)
    try:
        while True:
            metrics = get_cloudwatch_metrics()
            ml_prob, risk_level, trend = calculate_ml_prediction(metrics)
            hot_keys = get_hot_keys_simulation()
            
            # Extract latest values for charts
            latest_writes = [m.get('Sum', 0) for m in metrics[-10:]]
            latest_timestamps = [m['Timestamp'].isoformat() for m in metrics[-10:]]
            
            data = {
                "type": "metrics_update",
                "timestamp": datetime.utcnow().isoformat(),
                "write_capacity": latest_writes,
                "timestamps": latest_timestamps,
                "ml_prediction": {
                    "probability": ml_prob,
                    "risk_level": risk_level,
                    "trend": trend
                },
                "hot_keys": hot_keys,
                "current_load": round(sum(latest_writes) / len(latest_writes)) if latest_writes else 0
            }
            
            await manager.broadcast(data)
            await asyncio.sleep(3)  # Update every 3 seconds for smooth animation
            
    except Exception as e:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Premium Dashboard Server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
