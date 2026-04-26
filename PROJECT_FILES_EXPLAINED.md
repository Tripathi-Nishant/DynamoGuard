# 📁 Project File Structure & Explanation

This document explains what each file in your DynamoDB Hotspot Sentinel project does.

---

## 🏗️ Complete File Structure

```
dynamodb-hotspot/
├── AWS_SETUP_GUIDE.md           ← Start here! AWS credentials setup
├── README_EXAM_GUIDE.md          ← Main project overview & demo script
├── DASHBOARD_SETUP.md            ← Premium dashboard details
├── PROJECT_FILES_EXPLAINED.md    ← This file
├── requirements.txt              ← Python dependencies
│
├── setup_aws.py                  ← Create DynamoDB table
├── traffic_generator.py          ← Simulate hotspot traffic
├── lambda_function.py            ← AWS Lambda code (for optional deployment)
├── dashboard_backend.py          ← FastAPI WebSocket server
└── dashboard.html                ← Premium dashboard UI
```

---

## 📄 File-by-File Breakdown

### 1. **AWS_SETUP_GUIDE.md** ← **START HERE**
**Purpose**: Step-by-step guide to set up your AWS environment  
**What to do**:
- Get AWS Access Keys from IAM
- Install & configure AWS CLI
- Verify credentials work

**When to read**: **TONIGHT before your exam** (takes 15 minutes)

---

### 2. **README_EXAM_GUIDE.md**
**Purpose**: Main project documentation and exam demo script  
**Contains**:
- Project overview
- Architecture explanation
- Complete demo script for examiners
- Troubleshooting tips

**When to read**: Reference during your exam presentation

---

### 3. **DASHBOARD_SETUP.md**
**Purpose**: How to run the premium dashboard  
**Contains**:
- Dashboard features breakdown
- 5-minute setup guide
- Live demo script for examiners
- Dashboard components explained

**When to read**: Before running `python dashboard_backend.py`

---

### 4. **requirements.txt**
**Purpose**: List of Python packages to install  
**Usage**:
```bash
pip install -r requirements.txt
```

**Contains**:
- `boto3` - AWS SDK for Python
- `fastapi` - Web framework
- `uvicorn` - Server
- `websockets` - Real-time updates

---

### 5. **setup_aws.py** ⚙️
**Purpose**: Create the DynamoDB table in your AWS account  
**Usage**:
```bash
python setup_aws.py
```

**What it does**:
1. Connects to your AWS account using boto3
2. Creates a table named `Exam_UserTraffic`
3. Sets billing to `PAY_PER_REQUEST` (no upfront cost)

**Run this**: After AWS CLI is configured (first time only)

**Output**:
```
Creating table Exam_UserTraffic...
Table Exam_UserTraffic created successfully!
```

---

### 6. **traffic_generator.py** 🚗
**Purpose**: Simulate real-world DynamoDB traffic with hotspots  
**Usage**:
```bash
python traffic_generator.py
```

**What it does**:
1. Generates traffic from 9 normal users (`user_1` through `user_9`)
2. Generates HEAVY traffic on `user_999` (the hotspot)
3. Writes items to DynamoDB in real-time
4. Optionally reshards traffic across `user_999#a`, `#b`, `#c`, `#d`

**Feature Flag** (line 10):
- `RESHARDING_ENABLED = False` → Shows the PROBLEM (hotspot)
- `RESHARDING_ENABLED = True` → Shows the SOLUTION (resharded traffic)

**Run this**: In Terminal 1 during your exam demo

**Output**:
```
[2024-04-23 10:30:45] Wrote items. Normal: user_3 | Hotspot Target: user_999
[2024-04-23 10:30:46] Wrote items. Normal: user_7 | Hotspot Target: user_999
...
```

---

### 7. **lambda_function.py** ⚡ (Optional)
**Purpose**: AWS Lambda function that detects hotspots using CloudWatch metrics  
**Deployment**: Paste into AWS Lambda Console (optional for advanced demo)

**What it does**:
1. Queries CloudWatch for last 5 minutes of write capacity metrics
2. Passes metrics to ML prediction logic
3. Calculates risk score
4. Triggers resharding if risk > 80%

**For your exam**: You can just show examiners the code and explain how it would run

**Note**: This requires EventBridge trigger setup (see AWS_SETUP_GUIDE.md Step 7)

---

### 8. **dashboard_backend.py** 🚀
**Purpose**: FastAPI server that streams real-time metrics via WebSocket  
**Usage**:
```bash
python dashboard_backend.py
```

**What it does**:
1. Starts HTTP server on `http://localhost:8000`
2. Serves the `dashboard.html` file
3. Connects to CloudWatch API
4. Fetches write capacity metrics
5. Runs ML prediction logic on metrics
6. Broadcasts updates via WebSocket every 3 seconds
7. Clients (dashboard.html) receive live updates

**Run this**: In Terminal 2 during your exam demo

**Output**:
```
🚀 Starting Premium Dashboard Server on http://localhost:8000
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**The server is ready when you see the last line ↑**

---

### 9. **dashboard.html** 🎨
**Purpose**: Premium real-time dashboard UI  
**Usage**: Open in browser at `http://localhost:8000`

**What you see**:
- **Left Card**: ML Risk Score gauge (color-coded)
- **Center Card**: AI predictions (probability, trend, load)
- **Right Card**: System metrics
- **Large Chart**: Write capacity trend over last 10 minutes
- **Bottom Table**: Detected hot keys with traffic volume

**How it works**:
1. Loads when you visit `http://localhost:8000`
2. Connects to WebSocket on the FastAPI backend
3. Receives real-time metric updates
4. Updates ApexCharts visualization
5. Refreshes hot keys table every 3 seconds

**No need to edit**: This file is complete and production-ready

---

## 🎬 How to Use These Files During Your Exam

### Timeline:

**TONIGHT (1 hour before bed)**:
1. Read `AWS_SETUP_GUIDE.md`
2. Run `aws configure` with your credentials
3. Run `python setup_aws.py`
4. Verify DynamoDB table exists in AWS Console

**EXAM DAY (15 minutes before presentation)**:
1. Start Terminal 1: `python traffic_generator.py`
2. Start Terminal 2: `python dashboard_backend.py`
3. Open browser: `http://localhost:8000`
4. Have `README_EXAM_GUIDE.md` handy for your talking points

**DURING EXAM (5-minute live demo)**:
1. Show traffic generator running (Terminal 1)
2. Show dashboard updating in real-time (Browser)
3. Point out risk score gauge, predictions, hot keys table
4. Explain AWS architecture (Lambda, CloudWatch, DynamoDB)
5. Show `lambda_function.py` code on your editor
6. Explain the resharding strategy

---

## 🔧 File Dependencies

```
AWS Account
    ↓
aws configure (AWS_SETUP_GUIDE.md)
    ↓
setup_aws.py → Creates Exam_UserTraffic table
    ↓
traffic_generator.py → Writes data to table
    ↓
dashboard_backend.py → Reads from CloudWatch
    ↓
dashboard.html → Shows real-time visualization
```

---

## 📊 What Each Component Does

| Component | File | Purpose | AWS Service |
|-----------|------|---------|-------------|
| Table Setup | `setup_aws.py` | Create DynamoDB table | DynamoDB |
| Traffic Simulation | `traffic_generator.py` | Generate hotspot traffic | DynamoDB |
| Backend Server | `dashboard_backend.py` | Stream metrics via WebSocket | CloudWatch + FastAPI |
| Frontend UI | `dashboard.html` | Display real-time metrics | ApexCharts |
| Lambda Function | `lambda_function.py` | Detect hotspots & trigger remediation | Lambda |

---

## ✅ Checklist Before Your Exam

- [ ] Read `AWS_SETUP_GUIDE.md`
- [ ] Run `aws configure` successfully
- [ ] Run `python setup_aws.py` and see "Table created successfully!"
- [ ] Verify table in AWS Console
- [ ] Run `python traffic_generator.py` and see traffic output
- [ ] Run `python dashboard_backend.py` and see "Application startup complete"
- [ ] Open `http://localhost:8000` and see the dashboard
- [ ] Dashboard shows live metrics updating
- [ ] All 5 Python files are present:
  - [ ] setup_aws.py
  - [ ] traffic_generator.py
  - [ ] lambda_function.py
  - [ ] dashboard_backend.py
  - [ ] dashboard.html

---

## 🆘 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| "AWS credentials not found" | Run `aws configure` |
| "Table already exists" | Normal! Just run traffic_generator.py |
| "Port 8000 in use" | Change to `port=8001` in dashboard_backend.py line 62 |
| "Dashboard won't load" | Make sure `dashboard_backend.py` is running |
| "No metrics in dashboard" | Make sure `traffic_generator.py` is running in another terminal |

---

Good luck with your AWS exam! You've got this! 🚀
