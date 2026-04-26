# 🎯 AWS Account Demo Steps for Your Teacher

---

## 📋 Complete Demo Flow (15 minutes)

**Start by saying:** "Sir/Madam, ab maine apne AWS account mein dekhaata hoon sab kuch kaise set up hai aur kaise kaam kar raha hai..."

---

## ✅ STEP 1: DynamoDB Table Verification (2 minutes)

### Where to Go:
1. Open AWS Management Console
2. Search for **DynamoDB** 
3. Click **Tables** in left sidebar

### What to Show:

**Screenshot points:**
```
Tables → Exam_UserTraffic
├─ Status: Active ✓
├─ Partition Key: user_id (String)
├─ Sort Key: timestamp (Number)
├─ Billing Mode: PAY_PER_REQUEST
├─ Item Count: [Show current count - should be high, 1000+]
└─ Storage Size: [Should show data growing]
```

### What to Say:
"Sir, yeh hamara main database table hai. 
- **Exam_UserTraffic** - yeh DynamoDB table mein actual data store ho raha hai
- Partition key **user_id** hai - this identifies which user
- Sort key **timestamp** hai - multiple entries per user
- **PAY_PER_REQUEST** billing - we pay only for what we use
- Item count **constantly increasing** - traffic_generator.py har second data likha ja raha hai"

### Action to Take:
Click on table → Go to **"Items"** tab
- Shows all data being written
- Scroll to see latest entries
- Highlight entries with **user_999** key (the hotspot!)

---

## ✅ STEP 2: CloudWatch Metrics Dashboard (3 minutes)

### Where to Go:
1. Search for **CloudWatch**
2. Click **Dashboards** (left sidebar)
3. OR go to **Metrics** → **AWS/DynamoDB**

### What to Show:

**Path A: Direct Metrics View**
```
CloudWatch → Metrics → AWS/DynamoDB → TableName
├─ ConsumedReadCapacityUnits (Line Chart)
├─ ConsumedWriteCapacityUnits (Line Chart) ← IMPORTANT!
├─ UserErrors (Show throttle attempts if any)
└─ SuccessfulRequestLatency (Show response time)
```

### What to Say:
"CloudWatch automatically collect kar raha hai DynamoDB se metrics:

1. **ConsumedWriteCapacityUnits** - Kitna write capacity use ho raha hai
   - See yeh line chart? Traffic gradually build ho rahi hai
   - Last 24 hours ka trend dikhai de raha hai
   - Iska matlab ka system continuous monitor ho raha hai

2. **Read/Write Capacity** - Dono dikh rahe hain
   - Write capacity zyada hai (normal, kyun ke traffic_generator likh raha hai)
   
3. **Throttle Events** - Agar hotspot aata toh yeh spike hota
   - Right now zero hai (system healthy)
   - Lekin agar hotspot detect ho jata, toh spike aata"

### Action to Take:
- **Set time range to "Last 24 hours"** to show trend
- **Hover over metrics** to show exact values
- If available, show **custom metric** for hot keys

---

## ✅ STEP 3: Lambda Function Deployment (3 minutes)

### Where to Go:
1. Search for **Lambda**
2. Click **Functions** (left sidebar)
3. Find function: **Hotspot_Predictor_Engine**

### What to Show:

```
Function: Hotspot_Predictor_Engine
├─ Runtime: Python 3.12 ✓
├─ Memory: 256 MB
├─ Timeout: 60 seconds
├─ Code: [Show the code]
├─ Environment Variables: 
│  └─ [Any configs you set]
└─ Execution Role: [Lambda role with DynamoDB + CloudWatch permissions]
```

### What to Say:
"Yeh hamara brain hai - **Hotspot_Predictor_Engine**

1. **Runtime: Python 3.12** - Same language jisme hamara code likha tha
2. **Memory: 256 MB** - Lightweight, efficient
3. **Timeout: 60 seconds** - Har execution ke liye 60 sec available
4. **Code** - Dekho logic kya hai:
   - CloudWatch se metrics nikaalta hai
   - ML model run karta hai
   - Risk score calculate karta hai
   - Agar risk high hai toh resharding trigger karta hai"

### Show Code:
Scroll down to **"Code"** section:
```python
# Dikhao yeh lines:
def lambda_handler(event, context):
    # 1. Query CloudWatch
    metrics = get_metrics_from_cloudwatch()
    
    # 2. Run ML prediction
    probability = run_ml_prediction(metrics)
    
    # 3. Calculate risk
    risk_score = probability * 0.8 + throttle_count * 0.2
    
    # 4. Decision logic
    if risk_score >= 0.8:
        action = "RESHARD"  # Automatic remediation!
    else:
        action = "MONITOR"
    
    return decision_json
```

### Show IAM Role Permissions:
- Click **"Execution role"** link
- Show it has:
  - `AmazonDynamoDBFullAccess` - Can read/write DynamoDB
  - `CloudWatchReadOnlyAccess` - Can read metrics
  - `CloudWatchLogsFullAccess` - Can write logs

---

## ✅ STEP 4: EventBridge Rule Trigger (2 minutes)

### Where to Go:
1. Search for **EventBridge**
2. Click **Rules** (left sidebar)
3. Find rule: **Hotspot_Detector_Scheduled**

### What to Show:

```
Rule: Hotspot_Detector_Scheduled
├─ State: ENABLED ✓
├─ Schedule Expression: rate(1 minute)
│  └─ Meaning: Trigger every 60 seconds
├─ Target: Lambda Function (Hotspot_Predictor_Engine)
├─ Description: "Scheduled trigger for hotspot detection"
└─ Last Triggered: [Should show recent timestamps]
```

### What to Say:
"Yeh **EventBridge rule** hai jo Lambda ko trigger karta hai:

1. **Schedule: rate(1 minute)** - Har 60 seconds mein execute
   - Iska matlab Lambda automatically call hota hai without manual intervention
   
2. **Target: Lambda** - Lambda function ko call karta hai
   
3. **ENABLED state** - Active hai, chal raha hai
   
4. **How it works:**
   ```
   T=00:00 → EventBridge trigger fires
            ↓
           Lambda executes
            ↓
           Metrics analyzed
            ↓
           Decision made
            ↓
   T=01:00 → EventBridge fires again
   ```

This is **Serverless Orchestration** - no servers to manage, just pay per execution!"

### Click to Show Last Invocations:
- Scroll down to **"Executions"** or **"History"**
- Show recent Lambda invocations
- Timestamps should be ~1 minute apart

---

## ✅ STEP 5: CloudWatch Logs (Recent Lambda Execution) (2 minutes)

### Where to Go:
1. From Lambda page → Scroll to **"Monitor"** tab
2. OR go to **CloudWatch → Logs → Log Groups**
3. Find: **/aws/lambda/Hotspot_Predictor_Engine**

### What to Show:

```
Log Group: /aws/lambda/Hotspot_Predictor_Engine
├─ Latest Log Stream: [Recent timestamp like 2026-04-24 01:45:00]
│
└─ Log Entries:
   ├─ [INFO] Lambda invoked at 2026-04-24 01:45:00 UTC
   ├─ [QUERY] Fetching metrics from CloudWatch
   ├─ [METRICS] Write Capacity: [18, 19, 20, 21, 22] units/min
   ├─ [ML] Running prediction on 15 features
   ├─ [PREDICT] Model output: probability=0.42, confidence=0.85
   ├─ [DECISION] Risk Score: 0.42 < 0.50 → CONTINUE_MONITORING
   ├─ [STATUS] System: HEALTHY ✅
   └─ Duration: 523 ms
```

### What to Say:
"Yeh **audit trail** hai - pata chal ta hai exact execution kya hua:

1. **Lambda executed at exact timestamp** - Log mein visible
2. **Metrics fetched** - CloudWatch se data aya
3. **ML prediction ran** - Model ne probability calculate kiya
4. **Decision made** - Risk score ke based action decided
5. **Everything logged** - Compliance ke liye important

Teacher se kaho:
'Sir yeh logs mein exact kya hua dekh sakte hain. Agar koi problem hota toh uska trace yahan aata hai. Production systems ke liye yeh important hai - audit trail maintain karte hain.'"

### Show Multiple Log Streams:
- Scroll up to show **multiple log streams** (different times)
- Each represents one Lambda execution every 60 seconds
- Shows it's running consistently

---

## ✅ STEP 6: IAM User & Permissions (1 minute)

### Where to Go:
1. Search for **IAM**
2. Click **Users** (left sidebar)
3. Find user: **ExamUser** (the one running our code)

### What to Show:

```
User: ExamUser
├─ Access Keys: ✓ Active
├─ Attached Policies:
│  ├─ AdministratorAccess (for demo)
│  │  NOTE: Production would use least privilege!
│  └─ [Show what permissions it has]
├─ Created Date: [When you created it]
└─ Access Details: ✓ Programmatic access enabled
```

### What to Say:
"Yeh **IAM user** hai jo hamara code use kar raha hai AWS API call karte hue.

1. **ExamUser** - Specifically created for this project
2. **Credentials** - `aws configure` se configured
3. **Permissions** - AdministratorAccess (demo ke liye)
   - Production mein hum least privilege use karte (specific permissions only)
4. **Access Keys** - Programmatic access enabled (for boto3)

**Security best practice:** 
'Sir, production mein hum specific permissions dete jaise:
- DynamoDBReadOnlyAccess (sirf read)
- CloudWatchReadOnlyAccess (sirf read)
- Lambda invoke permission (specific function only)
...na ki AdminAccess. Lekin exam demo ke liye simple rakha.'"

---

## ✅ STEP 7: Optional - Show DynamoDB Streams (Advanced)

### Where to Go:
1. DynamoDB → Tables → Exam_UserTraffic
2. Scroll to **"Exports and streams"** section
3. Look for **DynamoDB Streams**

### What to Show:
```
DynamoDB Streams:
├─ Status: ENABLED
├─ Stream Specification: NEW_IMAGE
├─ Latest Stream ARN: [arn:aws:dynamodb:ap-south-1:...]
└─ Use Case: Lambda ke through hot keys detect karne
```

### What to Say:
"**Advanced feature:** DynamoDB Streams

Yeh enable hai taaki real-time mein item changes track kar sakte hain:
- Jab bhi koyi item likha jata hai, stream activate hota hai
- Lambda directly hook kar sakte hain (hum demonstrate nahi kar rahe but production mein use hota)
- Real-time hot key detection ke liye"

---

## 🎬 Complete Presentation Script (Use This!)

### **Opening (30 seconds)**
```
"Sir/Madam, maine AWS mein ek complete hotspot detection system build kiya hai.
Dekhaata hoon sab services kaise integrate hain aur kaise live kaam kar raha hai..."
```

### **Flow (12 minutes)**

**1. DynamoDB** (1 min)
```
"Yeh hamara database hai - Exam_UserTraffic table.
Traffic generator continuously data likha ja raha hai.
user_999 ko 5x zyada requests aa rahe hain (yeh hotspot hai)."
```

**2. CloudWatch Metrics** (2 min)
```
"CloudWatch automatically metrics collect kar raha hai.
Dekho write capacity trend - gradually increase ho rahi hai.
Agar sudden spike aata toh yeh chart spike dikhai deta."
```

**3. Lambda Function** (2 min)
```
"Lambda mein prediction logic likha hai.
Har 60 seconds mein EventBridge automatically call karta hai.
Lambda metrics analyze karta hai aur decision leta hai."
```

**4. EventBridge** (1 min)
```
"Yeh orchestrator hai - job scheduler jaisa.
Har 1 minute mein Lambda trigger karta hai.
Serverless service - koi server manage nahi karna."
```

**5. CloudWatch Logs** (2 min)
```
"Execution logs mein sab kuch visible hai.
Metrics kya the, prediction kya tha, decision kya tha.
Production audit trail ke liye zaruri."
```

**6. IAM & Security** (1 min)
```
"ExamUser credentials se sab API calls auth ho rahe hain.
Production mein least privilege policies use karte hain."
```

### **Closing (1 min)**
```
"Summary:
- DynamoDB mein real data
- CloudWatch mein metrics
- Lambda mein ML logic
- EventBridge mein orchestration
- Logs mein audit trail

Sab integrated, automated, serverless!
Questions?"
```

---

## 🎯 Key Questions Teacher Might Ask:

### **Q1: "What if Lambda fails?"**
**Answer:** "CloudWatch Logs mein error visible hoga. EventBridge 2 times retry karta hai. Agar persist issue hai toh alert setup kar sakte hain (SNS/email). Production mein dead-letter queue use karte hain."

### **Q2: "How is this different from manual monitoring?"**
**Answer:**
```
Manual (Purana):
- On-call engineer dashboards dekh ta hai (1-2 min delay)
- Decision lene mein time (2-3 min)
- Action lene mein time (5-10 min)
- Total MTTR: 30-60 minutes ❌

Automated (Hamara):
- Lambda har 60 seconds trigger hota hai
- Instant decision based on ML
- Automatic resharding trigger
- Total MTTR: < 5 minutes ✅
```

### **Q3: "Cost implications?"**
**Answer:**
```
DynamoDB: PAY_PER_REQUEST → ₹0 agar usage na ho
Lambda: ₹0.20 per 1M invocations + ₹0.0000166667 per GB-second
CloudWatch: Free tier cover karti hai metrics
EventBridge: Free tier mein 10M events free

Monthly cost estimate: < ₹100-200 for this scale
Prevention of single hotspot incident: 10+ lakh ka loss bacha sakte hain!
```

### **Q4: "How does ML model work?"**
**Answer:**
```
"Hum 5 minutes ka historical metrics data lete hain aur 15 features calculate karte hain:
- read_rolling_avg_5min
- write_rolling_avg_5min
- read_volatility
- write_volatility
- spike_magnitude
- ... aur 10 more

Yeh features Random Forest model (150 decision trees) mein pass karte hain.
Model previous patterns se trained hai (30+ days data).
Output: Probability (0-1) aur confidence level."
```

### **Q5: "What about data consistency during resharding?"**
**Answer:**
```
"Dual-write strategy use karte hain:
1. New requests both old aur new keys mein likhe jate hain (backup)
2. Background mein old data migrate hota hai
3. Reads new keys se karte hain
4. 24 hours baad old key delete karte hain
Result: Zero data loss, zero downtime ✅"
```

---

## 📸 Screenshots to Take/Show:

Create a folder with these screenshots:
```
demo_screenshots/
├─ 01_dynamodb_table.png (Items, count, schema)
├─ 02_cloudwatch_metrics.png (Write capacity trend)
├─ 03_lambda_function.png (Code, runtime)
├─ 04_eventbridge_rule.png (Schedule, enabled)
├─ 05_cloudwatch_logs.png (Recent executions)
├─ 06_iam_user.png (Permissions)
├─ 07_hot_keys_detected.png (user_999 in logs)
└─ 08_arn_references.png (Integration points)
```

---

## ✅ Preparation Checklist:

Before showing teacher:
- [ ] Traffic generator running (check DynamoDB item count increasing)
- [ ] CloudWatch showing metrics (wait 5-10 min for data)
- [ ] Lambda logs showing recent executions (check Logs group)
- [ ] EventBridge rule enabled
- [ ] All regions set to **ap-south-1** (consistent!)
- [ ] Screenshot recent Lambda execution
- [ ] Write down ARNs of each resource (for reference)
- [ ] Bookmark all AWS pages in browser (for quick navigation)

---

**Good luck with your teacher demo! 🚀**

This complete walkthrough will definitely impress a skilled AWS architect! 🎓
