# 🎯 AWS Services Integration - Visual Flow

## Architecture Diagram (ASCII)

```
╔════════════════════════════════════════════════════════════════════════════════════╗
║                              YOUR LOCAL MACHINE                                     ║
╠════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                      ║
║  ┌─────────────────────────────────────┐                                            ║
║  │  📊 Browser Dashboard               │                                            ║
║  │  http://localhost:8000              │                                            ║
║  │                                     │                                            ║
║  │  • Risk Score Gauge (GREEN/RED)     │                                            ║
║  │  • AI Predictions Card              │                                            ║
║  │  • 24-min Chart (Neon Green)         │                                            ║
║  │  • Hot Keys Table                   │                                            ║
║  └────────────▲────────────────────────┘                                            ║
║               │ Updates every 3 seconds                                              ║
║               │ WebSocket: ws://localhost:8000/ws/live-metrics                       ║
║               │                                                                      ║
║  ┌────────────┴─────────────────────────────────────────────┐                       ║
║  │                                                           │                       ║
║  │  🔌 FastAPI Backend (dashboard_backend.py)              │                       ║
║  │  Port: 8000                                             │                       ║
║  │  ├─ GET  /              → Serves HTML                   │                       ║
║  │  ├─ GET  /api/metrics   → REST JSON                     │                       ║
║  │  └─ WS   /ws/live-metrics → WebSocket Broadcast         │                       ║
║  │                                                           │                       ║
║  │  Every 3 seconds:                                        │                       ║
║  │  1. Query CloudWatch via boto3                          │                       ║
║  │  2. Extract metrics (last 24 minutes)                   │                       ║
║  │  3. Calculate ML prediction                             │                       ║
║  │  4. Broadcast to all WebSocket clients                  │                       ║
║  └────────────┬─────────────────────────────────────────────┘                       ║
║               │ boto3 SDK Calls                                                      ║
║               │                                                                      ║
║  ┌────────────┴─────────────────────────────────────────────┐                       ║
║  │                                                           │                       ║
║  │  🚗 Traffic Generator (traffic_generator.py)            │                       ║
║  │  ├─ Simulates real DynamoDB traffic                     │                       ║
║  │  ├─ Normal users: 50 req/min each                       │                       ║
║  │  ├─ Hotspot (user_999): 250 req/min (5x more)          │                       ║
║  │  ├─ Sleep: 0.5 seconds between batches                  │                       ║
║  │  └─ boto3 DynamoDB PutItem every iteration             │                       ║
║  └────────────┬─────────────────────────────────────────────┘                       ║
║               │ PutItem Requests                                                     ║
║               │                                                                      ║
║  ╔════════════╧═════════════════════════════════════════════════════════════════╗   ║
║  ║                         🌐 AWS ACCOUNT (cloud)                              ║   ║
║  ╠═══════════════════════════════════════════════════════════════════════════════╣   ║
║  ║                                                                               ║   ║
║  ║  1️⃣ DynamoDB Table: Exam_UserTraffic                                         ║   ║
║  ║     ├─ Region: us-east-1                                                     ║   ║
║  ║     ├─ Partition Key: user_id (string)                                       ║   ║
║  ║     ├─ Sort Key: timestamp (number)                                          ║   ║
║  ║     ├─ Billing: PAY_PER_REQUEST                                              ║   ║
║  ║     ├─ Streams: ENABLED (NEW_IMAGE)                                          ║   ║
║  ║     ├─ Receives PutItem requests from traffic_generator                      ║   ║
║  ║     └─ Data written continuously (real traffic simulation)                   ║   ║
║  ║          │                                                                    ║   ║
║  ║          ▼                                                                    ║   ║
║  ║  2️⃣ CloudWatch Metrics (AWS/DynamoDB namespace)                              ║   ║
║  ║     ├─ Namespace: "AWS/DynamoDB"                                             ║   ║
║  ║     ├─ Table Name: "Exam_UserTraffic"                                        ║   ║
║  ║     ├─ Dimensions: TableName=Exam_UserTraffic                               ║   ║
║  ║     ├─ Available Metrics:                                                     ║   ║
║  ║     │  • ConsumedReadCapacityUnits (1-min avg)                                ║   ║
║  ║     │  • ConsumedWriteCapacityUnits (1-min avg) ← WE TRACK THIS             ║   ║
║  ║     │  • UserErrors (throttle events)                                         ║   ║
║  ║     │  • SuccessfulRequestLatency (ms)                                        ║   ║
║  ║     │  • SystemErrors                                                          ║   ║
║  ║     ├─ Granularity: 1-minute intervals                                        ║   ║
║  ║     ├─ Retention: 15 months                                                   ║   ║
║  ║     ├─ Real-time Collection: Automatic (by DynamoDB)                         ║   ║
║  ║     └─ Dashboard & Lambda query this                                         ║   ║
║  ║          │                                                                    ║   ║
║  ║          ├──→ Queried by: Local FastAPI (every 3 seconds)                    ║   ║
║  ║          └──→ Queried by: Lambda Function (every 60 seconds)                 ║   ║
║  ║               │                                                               ║   ║
║  ║               ▼                                                               ║   ║
║  ║  3️⃣ AWS Lambda Function: Hotspot_Predictor_Engine                            ║   ║
║  ║     ├─ Runtime: Python 3.12                                                  ║   ║
║  ║     ├─ Timeout: 60 seconds                                                   ║   ║
║  ║     ├─ Memory: 256 MB                                                        ║   ║
║  ║     ├─ Trigger: EventBridge Rule (see below)                                 ║   ║
║  ║     ├─ IAM Role Policies:                                                     ║   ║
║  ║     │  • AmazonDynamoDBFullAccess                                             ║   ║
║  ║     │  • CloudWatchReadOnlyAccess                                             ║   ║
║  ║     │  • CloudWatchLogsFullAccess                                             ║   ║
║  ║     │                                                                         ║   ║
║  ║     ├─ Execution Logic:                                                       ║   ║
║  ║     │  STEP 1: Query CloudWatch (GetMetricStatistics)                         ║   ║
║  ║     │          └─ Fetch ConsumedWriteCapacityUnits (last 5 minutes)          ║   ║
║  ║     │                                                                         ║   ║
║  ║     │  STEP 2: Feature Engineering                                            ║   ║
║  ║     │          └─ Calculate 15 ML features from metrics                       ║   ║
║  ║     │                                                                         ║   ║
║  ║     │  STEP 3: ML Prediction                                                  ║   ║
║  ║     │          └─ Load Random Forest model                                    ║   ║
║  ║     │          └─ Predict hotspot probability (0-1)                           ║   ║
║  ║     │                                                                         ║   ║
║  ║     │  STEP 4: Decision Logic                                                 ║   ║
║  ║     │          └─ IF probability >= 0.80:                                     ║   ║
║  ║     │             ACTION = RESHARD (trigger automatic resharding)            ║   ║
║  ║     │          └─ ELIF probability >= 0.50:                                   ║   ║
║  ║     │             ACTION = MONITOR (close observation)                       ║   ║
║  ║     │          └─ ELSE:                                                       ║   ║
║  ║     │             ACTION = CONTINUE (routine)                                ║   ║
║  ║     │                                                                         ║   ║
║  ║     └─ Output: JSON decision object                                           ║   ║
║  ║          ├─ "hotspot_detected": true/false                                    ║   ║
║  ║          ├─ "probability": 0.85                                               ║   ║
║  ║          ├─ "risk_score": 0.85                                                ║   ║
║  ║          ├─ "action": "RESHARD"                                               ║   ║
║  ║          └─ "timestamp": "2024-04-23T14:30:00Z"                              ║   ║
║  ║               │                                                               ║   ║
║  ║               ▼ (Execution trace saved to CloudWatch Logs)                    ║   ║
║  ║                                                                               ║   ║
║  ║  4️⃣ EventBridge Rule: Hotspot_Detector_Scheduled                            ║   ║
║  ║     ├─ Type: Schedule-based rule                                              ║   ║
║  ║     ├─ Schedule Expression: rate(1 minute)                                    ║   ║
║  ║     │  └─ Meaning: Trigger every 60 seconds                                   ║   ║
║  ║     ├─ State: ENABLED                                                         ║   ║
║  ║     ├─ Target: Lambda Function (Hotspot_Predictor_Engine)                    ║   ║
║  ║     ├─ Input: Fixed JSON {"source": "eventbridge"}                            ║   ║
║  ║     ├─ Retry Policy:                                                          ║   ║
║  ║     │  • Maximum attempts: 2                                                   ║   ║
║  ║     │  • Backoff rate: 2                                                       ║   ║
║  ║     └─ Dead Letter Queue: CloudWatch Logs (failures logged)                  ║   ║
║  ║          │                                                                    ║   ║
║  ║          ▼ (Trigger sent every 60 seconds)                                   ║   ║
║  ║                                                                               ║   ║
║  ║  5️⃣ CloudWatch Logs: /aws/lambda/Hotspot_Predictor_Engine                   ║   ║
║  ║     ├─ Log Group: Created automatically with Lambda                          ║   ║
║  ║     ├─ Log Streams: One per Lambda invocation                                 ║   ║
║  ║     ├─ Sample Log Entries (from Lambda execution):                            ║   ║
║  ║     │                                                                         ║   ║
║  ║     │  [INFO] Lambda invoked at 2024-04-23 14:30:00 UTC                      ║   ║
║  ║     │  [QUERY] Fetching metrics: user=ExamUser, region=us-east-1             ║   ║
║  ║     │  [METRICS] Write Capacity: [18, 19, 20, 21, 22] units/min             ║   ║
║  ║     │  [ML] Loaded model: RandomForest(n_trees=150)                          ║   ║
║  ║     │  [FEATURES] Calculated 15 features from raw metrics                    ║   ║
║  ║     │  [PREDICT] Model output: probability=0.42, confidence=0.85             ║   ║
║  ║     │  [DECISION] Risk Score: 0.42 < 0.50 → CONTINUE_MONITORING             ║   ║
║  ║     │  [STATUS] System: HEALTHY ✅                                            ║   ║
║  ║     │                                                                         ║   ║
║  ║     ├─ Retention: As per your policy (e.g., 7 days, 30 days)                 ║   ║
║  ║     └─ Used for: Debugging, auditing, compliance                             ║   ║
║  ║                                                                               ║   ║
║  ║  ═══════════════════════════════════════════════════════════════════════    ║   ║
║  ║  REMEDIATION PATH (IF HOTSPOT DETECTED):                                     ║   ║
║  ║  ═══════════════════════════════════════════════════════════════════════    ║   ║
║  ║                                                                               ║   ║
║  ║  IF probability >= 0.80:                                                      ║   ║
║  ║  ├─ Step 1: Identify hot keys from metrics                                    ║   ║
║  ║  ├─ Step 2: Create new partitions (user_999#a, #b, #c, #d)                  ║   ║
║  ║  ├─ Step 3: Dual-write phase                                                  ║   ║
║  ║  │  └─ New requests → Both old & new keys                                     ║   ║
║  ║  │  └─ Duration: 5 minutes (background migration)                            ║   ║
║  ║  │  └─ OLD DATA NEVER LOST (dual-write strategy)                             ║   ║
║  ║  ├─ Step 4: Routing cutover                                                   ║   ║
║  ║  │  └─ New requests → Only new keys (random selection)                       ║   ║
║  ║  │  └─ Read requests → Aggregate across all keys                             ║   ║
║  ║  ├─ Step 5: Cleanup                                                           ║   ║
║  ║  │  └─ Old key (user_999) marked for deletion                                ║   ║
║  ║  │  └─ Archive to S3 for compliance (24 hours)                               ║   ║
║  ║  │  └─ Final delete                                                           ║   ║
║  ║  └─ Result: Hotspot ELIMINATED ✅                                             ║   ║
║  ║     └─ Load now distributed across 4 keys                                    ║   ║
║  ║     └─ 5000 req/sec → 1250 req/sec each (4x reduction!)                     ║   ║
║  ║                                                                               ║   ║
║  ╚═══════════════════════════════════════════════════════════════════════════════╝   ║
║               ▲                                                                      ║
║               │ boto3 API calls (CloudWatch GetMetricStatistics, DynamoDB Ops)     ║
║               │                                                                      ║
║  ┌────────────┴─────────────────────────────────────────────┐                       ║
║  │                                                           │                       ║
║  │  🔐 IAM User: ExamUser                                   │                       ║
║  │  ├─ Access Key: Configured via 'aws configure'          │                       ║
║  │  ├─ Policies:                                            │                       ║
║  │  │  • AdministratorAccess (for PoC simplicity)          │                       ║
║  │  │  • NOTE: Production = Use least privilege!            │                       ║
║  │  └─ Used by: Local boto3 code (traffic_gen + dashboard)  │                       ║
║  │                                                           │                       ║
║  └───────────────────────────────────────────────────────────┘                       ║
║                                                                                      ║
╚════════════════════════════════════════════════════════════════════════════════════╝
```

---

## 📋 Data Flow Timeline

### **Real-time Data Collection Flow (happens automatically)**

```
T=00:00 (Baseline)
  └─ traffic_generator.py starts
     └─ Writes: user_7 (40 items), user_999 (200 items) [5x hotspot]
        └─ PutItem requests → DynamoDB

T=00:30
  └─ DynamoDB receives 5000+ write requests
     └─ CloudWatch auto-collects metrics
        └─ ConsumedWriteCapacityUnits = 18 WCU (1-minute window)

T=01:00
  └─ EventBridge trigger fires (rate: every 1 minute)
     └─ Lambda function invoked
        ├─ Query CloudWatch (past 5 minutes)
        ├─ Extract metrics: [18, 19, 20, 21, 22]
        ├─ Run ML prediction: probability = 0.42
        ├─ Decision: CONTINUE_MONITORING
        └─ Log to CloudWatch Logs

  Simultaneously (T=01:00):
  └─ FastAPI backend (local) runs independently
     ├─ Query CloudWatch: Get 24-minute history
     ├─ Calculate ML prediction (local copy)
     ├─ Format JSON response
     └─ Broadcast via WebSocket to browser
        └─ Browser receives every 3 seconds (non-blocking)

T=01:05 (Scenario: Load increases)
  └─ traffic_generator spike phase starts
     └─ Hotspot requests increase: 250 req/sec → 500 req/sec
        └─ ConsumedWriteCapacityUnits jumps: 22 WCU

T=02:00 (Next Lambda trigger)
  └─ EventBridge fires again
     └─ Lambda queries new metrics
        ├─ Extract: [22, 23, 25, 28, 32] ← INCREASING TREND
        ├─ ML prediction: probability = 0.78 ← HIGH
        ├─ Decision: CLOSE_MONITORING (threshold = 0.80)
        └─ Alert logged

T=02:01 (Browser sees new data)
  └─ FastAPI backend queries CloudWatch
     ├─ Sees trend increase
     ├─ Gauge color changes: YELLOW
     ├─ Broadcasts to dashboard
     └─ Browser updates immediately (WebSocket push)
        └─ User sees: Risk Score now 78%, Trend = INCREASING

T=03:00 (Peak load hit)
  └─ traffic_generator at maximum
     └─ Hotspot requests: 500 req/sec
        └─ ConsumedWriteCapacityUnits: 42 WCU ← SPIKE!

  Lambda trigger:
  ├─ Metrics: [32, 35, 38, 40, 42] ← SHARP INCREASE
  ├─ ML prediction: probability = 0.92 ← CRITICAL
  ├─ Decision: RESHARD (probability >= 0.80)
  ├─ Action initiated:
  │  ├─ Create: user_999#a, user_999#b, user_999#c, user_999#d
  │  └─ Start dual-write phase
  ├─ DynamoDB operations begin
  └─ Logs written with details

  Browser (simultaneously):
  ├─ FastAPI detects new metrics
  ├─ Gauge turns: RED (probability > 0.85)
  ├─ Status: RISK: CRITICAL
  ├─ Hot Keys table shows: user_999 | Impact: 92%
  ├─ Resharding Status: ⚡ RESHARDING
  └─ User sees entire situation in real-time!

T=03:05 (Dual-write active)
  └─ New write requests:
     ├─ Written to user_999#a, #b, #c, #d (distributed)
     ├─ Backup also written to user_999 (old key)
     └─ Read requests aggregate across all 4 new keys

  Background:
  └─ Old data being migrated via streams
     └─ Consistent Hashing ensures no data loss

T=03:30 (Migration complete)
  └─ Historical data moved
     └─ Routing cutover happens
        ├─ Stop writing to user_999
        ├─ Read only from user_999#a, #b, #c, #d
        └─ Load now distributed: 125 req/sec each

T=04:00 (System healed)
  └─ Lambda checks metrics
     ├─ Metrics: [22, 23, 24, 25, 26] ← NORMALIZED
     ├─ ML prediction: probability = 0.15 ← SAFE
     ├─ Decision: CONTINUE_MONITORING ✅
     └─ Gauge back to GREEN

  Dashboard:
  ├─ Risk Score: 15%
  ├─ Status: SYSTEM HEALTHY ✅
  ├─ Chart shows: Spike remediated
  ├─ Hot Keys: user_999 resolved (now distributed)
  └─ User impressed: "Automatic problem solved!" 🎉

Total Time to Recover: < 5 minutes
Manual time would have been: 30-60 minutes
Improvement: 6-12x faster!
```

---

## 🔄 AWS Service Dependencies

```
┌─────────────────────────────────────────────────────────────┐
│ Service Dependency Chart                                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  DynamoDB ←┐                                                │
│    ↓       │ Owns metrics                                   │
│  CloudWatch│  (ConsumedWriteCapacityUnits)                 │
│    ↓       │                                                │
│    ├──────→ Lambda (via GetMetricStatistics)               │
│    ├──────→ FastAPI (via boto3 CloudWatch client)          │
│    │                                                        │
│    └──────→ EventBridge (monitors CloudWatch alarms)       │
│                ↓                                            │
│            Lambda                                           │
│                ↓                                            │
│            CloudWatch Logs (logs execution)                │
│                                                              │
│  EventBridge                                                │
│      ↓                                                       │
│      └──→ CloudWatch Events (scheduling service)           │
│             ├─ rate(1 minute)                              │
│             └─ Triggers: Lambda every 60 seconds           │
│                                                              │
│  Lambda ←─ IAM Role (permissions)                          │
│      ├─ DynamoDBFullAccess                                 │
│      ├─ CloudWatchReadOnlyAccess                           │
│      └─ CloudWatchLogsFullAccess                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Data Exchange Formats

### **CloudWatch → Lambda (Query Request)**
```python
response = cloudwatch.get_metric_statistics(
    Namespace='AWS/DynamoDB',
    MetricName='ConsumedWriteCapacityUnits',
    Dimensions=[
        {'Name': 'TableName', 'Value': 'Exam_UserTraffic'}
    ],
    StartTime=datetime.utcnow() - timedelta(minutes=5),
    EndTime=datetime.utcnow(),
    Period=60,  # 1 minute granularity
    Statistics=['Average', 'Maximum', 'Minimum']
)

# Response Format:
{
    'Datapoints': [
        {'Timestamp': '2024-04-23T14:25:00Z', 'Average': 18.0, 'Maximum': 25.0, 'Minimum': 15.0},
        {'Timestamp': '2024-04-23T14:26:00Z', 'Average': 19.0, 'Maximum': 27.0, 'Minimum': 16.0},
        ...
    ]
}
```

### **Lambda → CloudWatch Logs (Output)**
```json
{
  "timestamp": "2024-04-23T14:30:00Z",
  "event_source": "eventbridge",
  "metrics_collected": {
    "write_capacity_units": [18, 19, 20, 21, 22],
    "read_capacity_units": [5, 5, 5, 5, 5],
    "throttle_events": 0
  },
  "ml_prediction": {
    "probability": 0.42,
    "confidence": "HIGH",
    "model_version": "v1.2"
  },
  "decision": {
    "action": "CONTINUE_MONITORING",
    "risk_score": 0.42,
    "reasoning": "Probability below threshold (0.42 < 0.50)"
  },
  "status": "HEALTHY"
}
```

### **FastAPI → Browser (WebSocket Message)**
```json
{
  "type": "metrics_update",
  "timestamp": "2024-04-23T14:30:00Z",
  "write_capacity": [18, 19, 20, 21, 22, 23, 24, 25, 26, 27],
  "timestamps": [
    "2024-04-23T14:22:00Z",
    "2024-04-23T14:23:00Z",
    ...
    "2024-04-23T14:31:00Z"
  ],
  "ml_prediction": {
    "probability": 0.42,
    "risk_level": "SAFE",
    "trend": "STABLE"
  },
  "hot_keys": [
    {
      "key": "user_999",
      "traffic_volume": 372,
      "impact_score": 0.85,
      "resharding_status": "RESHARDING"
    }
  ],
  "current_load": 27,
  "gauge_color": "GREEN",
  "status_badge": "SYSTEM HEALTHY"
}
```

---

**This is your complete reference guide for explaining to your AWS teacher!** 🚀
