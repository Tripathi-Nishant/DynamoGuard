# Premium Dashboard Setup Guide

This is a production-grade, real-time dashboard built with **FastAPI**, **WebSockets**, and **ApexCharts**. It will impress your AWS examiners!

## 🎨 Features

✅ **Real-time WebSocket Updates** - Live metric streaming from CloudWatch  
✅ **Premium ApexCharts Visualizations** - Professional grade charting  
✅ **Dark Mode UI** - Modern, sleek design with gradients  
✅ **Risk Score Gauge** - Color-coded hotspot prediction (green → yellow → red)  
✅ **Hot Keys Detection Table** - Shows detected partition keys with traffic volume  
✅ **ML Predictions** - Displays probability, trend, and current load  
✅ **Auto-Refreshing Metrics** - Updates every 3 seconds without manual refresh  

## 📋 Quick Setup (5 minutes)

### 1. Install FastAPI and Uvicorn
```bash
pip install fastapi uvicorn
```

### 2. Make Sure Your DynamoDB Table is Running
Ensure you've already run:
```bash
python setup_aws.py
```
This creates the `Exam_UserTraffic` table in your AWS account.

### 3. Start the Traffic Generator (Terminal 1)
```bash
python traffic_generator.py
```
This simulates real DynamoDB traffic with hotspots on `user_999`.

### 4. Start the Dashboard Backend (Terminal 2)
```bash
python dashboard_backend.py
```
You should see:
```
🚀 Starting Premium Dashboard Server on http://localhost:8000
```

### 5. Open Your Browser
Navigate to:
```
http://localhost:8000
```

**That's it!** You now have a real-time premium dashboard showing live DynamoDB hotspot detection and AI/ML predictions.

## 🎬 Live Demo Script for Your Exam

When you're ready to present:

**Step 1:** Show the dashboard is running
- *"Here is the real-time command center. Notice the ML Risk Score gauge on the left—it's currently GREEN (safe)."*

**Step 2:** Point out the live metrics
- *"In the center, we see CloudWatch is feeding write capacity metrics. The chart shows the last 10 minutes of traffic."*

**Step 3:** Show the hot keys table
- *"This table detects hot keys in real-time. If a partition key suddenly gets disproportionate traffic, it appears here with an 'Impact Score.'"*

**Step 4:** Trigger the hotspot (Optional)
- In `traffic_generator.py`, change line 10 to: `RESHARDING_ENABLED = False` (to ensure heavy hotspot traffic)
- Watch the dashboard:
  - Risk Score gauge turns **YELLOW** (60-85%)
  - If traffic continues, it turns **RED** (85%+)
  - Hot keys table populates with `user_999` and resharding suggestions
  - The AI predicts the hotspot **before** it causes throttling

**Step 5:** Explain the AWS Architecture
- *"The FastAPI backend queries Amazon CloudWatch every 3 seconds, pulls DynamoDB metrics, runs our ML prediction logic, and broadcasts updates via WebSocket."*
- *"The frontend renders real-time charts using ApexCharts, giving us instant visibility without the 1-minute CloudWatch lag."*

---

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      AWS ACCOUNT                                 │
│                                                                   │
│  ┌──────────────────┐    ┌──────────────────┐                   │
│  │  DynamoDB Table  │───▶│  CloudWatch      │                   │
│  │ (UserTraffic)    │    │  Metrics         │                   │
│  └──────────────────┘    └────────┬─────────┘                   │
│                                    │                              │
│                                    │ boto3                        │
└────────────────────────────────────┼──────────────────────────────┘
                                     │
                          ┌──────────▼─────────────┐
                          │  FastAPI Backend      │
                          │  (dashboard_backend.py)
                          │  - Query CloudWatch   │
                          │  - Calculate ML Score │
                          │  - WebSocket Server   │
                          └──────────┬──────────────┘
                                     │
                          WebSocket  │ Real-time data
                                     │
                          ┌──────────▼──────────────┐
                          │  Premium Dashboard     │
                          │  (dashboard.html)      │
                          │  - ApexCharts          │
                          │  - Risk Gauge          │
                          │  - Hot Keys Table      │
                          │  - Live Updates        │
                          └───────────────────────┘
```

---

## 🔧 Troubleshooting

### Dashboard not loading?
- Make sure `dashboard.html` is in the same directory as `dashboard_backend.py`
- Check that port 8000 is not already in use

### WebSocket connection failed?
- Ensure the FastAPI backend is still running (Terminal 2)
- Check that your AWS credentials are valid (`aws configure`)

### No metrics appearing?
- Verify the traffic generator is still running (Terminal 1)
- Check CloudWatch console: `AWS/DynamoDB` namespace for `Exam_UserTraffic` table

### "No hot keys detected" message?
- This is normal! Hot keys only appear when traffic volume spikes
- The traffic generator defaults to mostly normal traffic with occasional hotspots
- To force a hotspot, edit `traffic_generator.py` and increase the loop count in the hotspot section

---

## 📊 Dashboard Components Explained

### 1. **ML Risk Score Gauge** (Left Card)
- **Green (0.0-0.6)**: System is safe, no action needed
- **Yellow (0.6-0.85)**: Medium risk, monitor closely
- **Red (0.85-1.0)**: Critical risk, auto-remediation triggered

### 2. **AI Predictions** (Center Card)
- **Probability**: ML model's confidence in hotspot prediction
- **Trend**: Direction of traffic (increasing/decreasing/stable)
- **Current Load**: Actual write capacity units consumed

### 3. **Write Capacity Trend Chart**
- Shows the last 10 minutes of write traffic
- Helps visualize seasonal patterns and sudden spikes

### 4. **Hot Keys Table**
- **Partition Key**: The database key experiencing unusual traffic
- **Traffic Volume**: Requests per minute on that key
- **Impact Score**: How severely this key impacts system performance
- **Resharding Status**: Whether automatic resharding is triggered

---

## 🎓 What This Demonstrates for Your AWS Exam

✅ **Real-time Data Processing** - Streaming metrics from CloudWatch  
✅ **Machine Learning Integration** - Prediction models in production  
✅ **Serverless Architecture** - Lambda + API Gateway patterns  
✅ **Database Optimization** - Handling DynamoDB hotspots  
✅ **WebSocket Communication** - Real-time web applications  
✅ **AWS Best Practices** - IAM, monitoring, auto-remediation  
✅ **Modern UI/UX** - Professional dashboard design  

---

Good luck with your AWS exam! 🚀
