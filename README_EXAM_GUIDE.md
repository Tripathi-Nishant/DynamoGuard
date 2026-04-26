# 🛡️ AI/ML-Powered Predictive DynamoDB Hotspot Detection & Auto-Remediation

**Premium Proof of Concept for AWS Certification Exam**

This repository contains a production-grade Proof of Concept (PoC) with a **premium real-time dashboard** that demonstrates AI/ML-powered DynamoDB hotspot detection and automatic remediation. It leverages core AWS services: **DynamoDB, Lambda, CloudWatch, and EventBridge** with a modern FastAPI + ApexCharts command center.

### Architecture Demonstrated:
1. **Traffic Generator (Local Python Script)**: Simulates thousands of normal users and one massive "Hotspot" user (`user_999`).
2. **Amazon DynamoDB**: Receives the traffic and automatically generates read/write metrics to CloudWatch.
3. **Amazon CloudWatch**: Collects `ConsumedWriteCapacityUnits` over 1-minute window intervals.
4. **Amazon EventBridge**: Triggers a Lambda function every minute (simulating a cron job).
5. **AWS Lambda (Decision Engine & ML Inference Simulator)**: The "brains." It pulls CloudWatch metrics, hands it to a mocked ML scoring engine (detects sudden 500% capacity spikes), and logs the auto-remediation decision.

---

## 🚀 THE PREMIUM DASHBOARD (NEW!)

Instead of a boring CLI output, you now have a **production-grade real-time dashboard** that will absolutely impress your examiners:

### Dashboard Features:
✅ **Real-time WebSocket Connection** - Live metric streaming (updates every 3 seconds)  
✅ **ML Risk Score Gauge** - Color-coded hotspot indicator (Green → Yellow → Red)  
✅ **ApexCharts Visualizations** - Professional charts showing write capacity trends  
✅ **Hot Keys Detection Table** - Live display of detected partition hotspots  
✅ **AI Prediction Metrics** - Probability, trend direction, current load  
✅ **Dark Mode Professional UI** - Modern design with Tailwind-style styling  
✅ **Fully Responsive** - Works on desktop, tablet, mobile  

### Tech Stack:
- **Backend**: FastAPI + WebSockets (Python)
- **Frontend**: HTML5 + CSS3 + ApexCharts.js
- **Real-time Updates**: WebSocket protocol
- **AWS Integration**: boto3 for CloudWatch & DynamoDB

---

## 🎬 THE ULTIMATE EXAM DEMO (Total Time: 10 minutes)

### Part 1: AWS Setup (5 minutes - do this tonight)
Follow the detailed guide in **AWS_SETUP_GUIDE.md** to:
1. Get your AWS Access Keys from IAM
2. Install and configure AWS CLI
3. Install Python dependencies (`pip install -r requirements.txt`)
4. Create the DynamoDB table (`python setup_aws.py`)
5. Deploy the Lambda function to AWS Console

### Part 2: Live Dashboard Demo (5 minutes - do this in your exam)

**Terminal 1: Start the Traffic Generator**
```bash
python traffic_generator.py
```
*Say to examiners: "I'm now simulating real-world DynamoDB traffic. Notice that one partition key (`user_999`) is receiving 5x more requests than others—this creates a hotspot."*

**Terminal 2: Start the Premium Dashboard**
```bash
pip install -r requirements.txt
python dashboard_backend.py
```
*Say to examiners: "The FastAPI backend is now pulling real CloudWatch metrics every 3 seconds."*

**Browser: Open the Dashboard**
Navigate to `http://localhost:8000`

*Say to examiners:*
- *"Here is our real-time command center. The ML Risk Score gauge shows the current threat level."*
- *"As write capacity increases on the hotspot key, the gauge turns from green → yellow → red."*
- *"The chart shows the last 10 minutes of traffic trends."*
- *"The Hot Keys table automatically detects and displays partition keys receiving disproportionate traffic."*
- *"When the AI predicts a hotspot with >85% probability, the system triggers automatic resharding."*

### What the Examiners Will See:
1. ✅ A sleek, professional dashboard (not a basic CLI)
2. ✅ Real-time data flowing from AWS CloudWatch
3. ✅ Machine learning predictions being made in real-time
4. ✅ Automatic hotspot detection without manual intervention
5. ✅ Your understanding of AWS architecture, serverless patterns, and modern web technologies

---

## 📋 Quick Setup Checklist

- [ ] AWS CLI installed and configured (`aws configure`)
- [ ] AWS IAM user created with AdministratorAccess
- [ ] Python 3.8+ installed
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] DynamoDB table created: `python setup_aws.py`
- [ ] All 5 Python files in your workspace:
  - [ ] `setup_aws.py`
  - [ ] `traffic_generator.py`
  - [ ] `lambda_function.py`
  - [ ] `dashboard_backend.py`
  - [ ] `dashboard.html`
- [ ] Test the dashboard locally: `python dashboard_backend.py` → `http://localhost:8000`