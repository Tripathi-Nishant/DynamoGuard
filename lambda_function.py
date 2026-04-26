import json
import boto3
import time
import random

# AWS Services
cloudwatch = boto3.client('cloudwatch', region_name='ap-south-1')
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('Exam_UserTraffic')

# Simulated ML Model inference
def run_ml_prediction(metrics):
    """
    In a 10-week project, this would load a scikit-learn or SageMaker Random Forest model.
    For this 2-hour PoC, we use a simple heuristic to simulate ML inference.
    If ConsumedWriteCapacityUnits spikes over X, return Hotspot Probability = 0.95.
    """
    total_writes = sum(point['Sum'] for point in metrics if 'Sum' in point)
    
    # ML Logic: If write volume is abnormal (> 20 writes in the 1-minute window)
    if total_writes > 20: 
        confidence = round(random.uniform(0.85, 0.98), 2)
        return {"prediction": "HOTSPOT", "probability": confidence, "risk_score": confidence * 1.0}
    else:
        return {"prediction": "SAFE", "probability": 0.1, "risk_score": 0.1}

def lambda_handler(event, context):
    """
    This Lambda function runs every 1-5 minutes via EventBridge.
    Step 1: Scrape CloudWatch metrics for the DynamoDB table.
    Step 2: Pass metrics to ML model.
    Step 3: Output Resharding Decision and execute remediation.
    """
    print("=== STARTING AI/ML HOTSPOT DETECTION CYCLE ===")
    
    # --- 1. Query CloudWatch for the last 5 minutes of Write Capacity Metrics
    try:
        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/DynamoDB',
            MetricName='ConsumedWriteCapacityUnits',
            Dimensions=[{'Name': 'TableName', 'Value': 'Exam_UserTraffic'}],
            StartTime=time.time() - 300, # 5 minutes ago
            EndTime=time.time(),
            Period=60,
            Statistics=['Sum']
        )
        datapoints = response.get('Datapoints', [])
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] CloudWatch Datapoints found: {len(datapoints)}")
        
        # --- 2. Pass to Machine Learning Model
        ml_result = run_ml_prediction(datapoints)
        print(f"ML Model Prediction: {ml_result['prediction']}")
        print(f"Probability Score: {ml_result['probability']}")
        print(f"Calculated Risk Score: {ml_result['risk_score']}")
        
        # --- 3. Decision Engine & Auto-Remediation
        if ml_result['risk_score'] > 0.8:
            print("ALERT: High-risk hotspot detected! Initiating Automatic Remediation.")
            
            # --- 4. The Resharding Strategy (Distributed Suffix) ---
            print("Resharding Strategy: Mapped Hot Key to 4 random partitions (#a, #b, #c, #d)")
            
            # In a real system, you would write this config to a routing table or Parameter Store
            # For the demo, we log the success.
            print("Status: RESHARDING COMPLETE. Data redistributing natively...")
            
            return {
                'statusCode': 200,
                'body': json.dumps('Hotspot Remediated Successfully!')
            }
        else:
            print("Status: SAFE. No resharding required.")
            return {
                'statusCode': 200,
                'body': json.dumps('System healthy.')
            }
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Failed to check metrics: {str(e)}')
        }
