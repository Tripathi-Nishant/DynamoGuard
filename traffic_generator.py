import boto3
import time
import random
from datetime import datetime
import urllib3
import warnings

# Suppress SSL warnings for PoC (corporate proxy/antivirus may intercept)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# Initialize connection with SSL verification disabled for PoC
import botocore.client
original_make_request = botocore.client.BaseClient._make_request

def patched_make_request(self, operation_model, request_dict, request_context):
    request_dict['verify'] = False
    return original_make_request(self, operation_model, request_dict, request_context)

botocore.client.BaseClient._make_request = patched_make_request

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1') # Change region if needed
table = dynamodb.Table('Exam_UserTraffic')

# Feature Flag: When true, we apply resharding logic
RESHARDING_ENABLED = False

def get_shard_suffix(user_id):
    """
    If resharding is enabled, we append a random suffix to distribute load.
    Otherwise, we hit the original user_id (causing a hotspot).
    """
    if RESHARDING_ENABLED and user_id == "user_999": # user_999 is our hotspot key
        shards = ['#a', '#b', '#c', '#d']
        return user_id + random.choice(shards)
    return user_id

def simulate_traffic():
    print("Starting simulated DynamoDB traffic stream...")
    print("Press Ctrl+C to stop.")
    
    users = [f"user_{i}" for i in range(1, 10)]
    retry_count = 0
    max_retries = 3
    
    try:
        while True:
            try:
                # 1. Normal Traffic
                normal_user = random.choice(users)
                normal_key = get_shard_suffix(normal_user)
                table.put_item(Item={
                    'user_id': normal_key,
                    'timestamp': int(time.time() * 1000),
                    'action': 'login',
                    'latency_ms': random.randint(10, 50)
                })
                
                # 2. Hotspot Traffic (Huge spike on user_999)
                hot_key = get_shard_suffix("user_999")
                
                # Write 5x more data to the hot key
                for _ in range(5):
                    table.put_item(Item={
                        'user_id': hot_key,
                        'timestamp': int(time.time() * 1000) + random.randint(1, 999), 
                        'action': 'heavy_query',
                        'payload': 'x' * 1024 # 1KB payload
                    })
                
                print(f"[{datetime.now()}] Wrote items. Normal: {normal_key} | Hotspot Target: {hot_key}")
                retry_count = 0  # Reset retry count on success
                time.sleep(0.5)
                
            except Exception as e:
                retry_count += 1
                if retry_count <= max_retries:
                    print(f"[WARNING] Write failed (attempt {retry_count}/{max_retries}): {str(e)[:100]}")
                    time.sleep(1)  # Wait before retry
                else:
                    raise  # Re-raise after max retries
            
    except KeyboardInterrupt:
        print("\nTraffic simulation stopped.")

if __name__ == "__main__":
    simulate_traffic()
