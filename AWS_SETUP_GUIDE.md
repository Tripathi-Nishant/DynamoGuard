# AWS Setup Guide for DynamoDB Hotspot Sentinel PoC

This guide walks you through setting up your AWS environment so the DynamoDB Hotspot Sentinel project works flawlessly.

## 📋 Prerequisites
- AWS Account (free tier is sufficient for this PoC)
- Windows/Mac/Linux with AWS CLI support
- Python 3.8 or later installed

---

## Step 1: Create an IAM User with AWS Access Keys

### Why?
Your local Python scripts need credentials to access your AWS account. Instead of using your root AWS account credentials (bad practice!), we create a dedicated IAM user with specific permissions.

### How?

1. **Log in to AWS Management Console**
   - Go to https://aws.amazon.com and click **Sign In to the Console**
   - Use your root email and password

2. **Open the IAM Console**
   - In the search bar at the top, type `IAM`
   - Click the IAM service

3. **Create a New User**
   - On the left menu, click **Users**
   - Click **Create user** button
   - User name: `ExamUser` (or any name you prefer)
   - Click **Next**

4. **Attach Permissions**
   - Select **Attach policies directly**
   - Search for and check: `AdministratorAccess`
   - *(For production, you'd be more restrictive, but for an exam PoC this is fine)*
   - Click **Next**

5. **Review and Create**
   - Click **Create user**

6. **Generate Access Keys**
   - Click on your newly created user name in the list
   - Go to **Security credentials** tab
   - Scroll to **Access keys** section
   - Click **Create access key**
   - Select **Command Line Interface (CLI)**
   - Check the confirmation checkbox
   - Click **Create access key**
   - **IMPORTANT**: Click **Show** to see both keys:
     - **Access key ID**: Copy this
     - **Secret access key**: Copy this
   - *(These are like username + password for your scripts. Keep them secret!)*

---

## Step 2: Install AWS CLI

The AWS CLI is the command-line tool that manages your AWS resources locally.

### On Windows:
1. Download the installer: [AWS CLI v2 for Windows](https://awscli.amazonaws.com/AWSCLIV2.msi)
2. Run the `.msi` file and follow the installer
3. Restart your terminal (VS Code or PowerShell)





## Step 3: Configure AWS CLI with Your Credentials

Now you'll give your local machine the credentials from Step 1.

1. **Open your terminal** (PowerShell, Terminal, or VS Code integrated terminal)

2. **Run the configuration wizard**
   ```bash
   aws configure
   ```

3. **Answer the 4 prompts:**
   - **AWS Access Key ID**: Paste the access key ID from Step 1
   - **AWS Secret Access Key**: Paste the secret access key from Step 1
   - **Default region name**: Type `us-east-1` (or your preferred AWS region)
   - **Default output format**: Type `json`

4. **Verify it worked**
   ```bash
   aws sts get-caller-identity
   ```
   If successful, you'll see output like:
   ```json
   {
       "UserId": "AIDAI...",
       "Account": "123456789012",
       "Arn": "arn:aws:iam::123456789012:user/ExamUser"
   }
   ```

✅ **Your AWS CLI is now authenticated!**

---

## Step 4: Install Python Dependencies

1. **Navigate to your project folder**
   ```bash
   cd c:\Users\HP\Desktop\dynamodb-hotspot
   ```

2. **Install all required packages**
   ```bash
   pip install -r requirements.txt
   ```

   This installs:
   - `boto3` - AWS SDK for Python
   - `fastapi` - Modern web framework
   - `uvicorn` - ASGI server
   - `websockets` - Real-time communication

---

## Step 5: Create the DynamoDB Table

1. **Run the setup script**
   ```bash
   python setup_aws.py
   ```

2. **Expected output**
   ```
   Creating table Exam_UserTraffic...
   Table Exam_UserTraffic created successfully!
   ```

3. **Verify in AWS Console**
   - Go to AWS Console → Search for `DynamoDB`
   - Click **Tables**
   - You should see `Exam_UserTraffic` in the list

✅ **Your DynamoDB table is now ready!**

---

## Step 6: Test the Dashboard Backend

1. **Start the FastAPI server**
   ```bash
   python dashboard_backend.py
   ```

2. **Expected output**
   ```
   🚀 Starting Premium Dashboard Server on http://localhost:8000
   INFO:     Application startup complete
   ```

3. **Open your browser**
   - Go to `http://localhost:8000`
   - You should see the premium dashboard

4. **Check for errors**
   - If you see errors about AWS credentials, go back to Step 3
   - If port 8000 is in use, change it in `dashboard_backend.py` line 62

✅ **Your dashboard is working!**

---

## Step 7 (Optional): Deploy Lambda to AWS

For the complete demonstration, you can deploy the Lambda function that triggers automatically via EventBridge.

1. **Go to AWS Console → Lambda**
2. **Click Create function**
   - Name: `Hotspot_Predictor_Engine`
   - Runtime: Python 3.12
   - Click **Create function**
3. **Paste the code**
   - Copy the entire contents of `lambda_function.py`
   - Paste it into the code editor in AWS Console
   - Click **Deploy**
4. **Add permissions**
   - Go to **Configuration** tab
   - Click on the role name under **Execution role**
   - Click **Add permission** → **Attach policies**
   - Search for and attach: `AmazonDynamoDBFullAccess`, `CloudWatchReadOnlyAccess`
5. **Add EventBridge trigger**
   - Click **Add trigger**
   - Select **EventBridge**
   - Create new rule: `Hotspot_Detector_Scheduled`
   - Schedule: `rate(1 minute)`
   - Click **Add**

✅ **Lambda is now running every minute in AWS!**

---

## 🆘 Troubleshooting

### "Unable to locate credentials"
**Solution**: Run `aws configure` again and make sure you entered the keys correctly

### "DynamoDB table not found"
**Solution**: Run `python setup_aws.py` again to create the table

### "Port 8000 already in use"
**Solution**: Either:
- Kill the process using port 8000
- Or change the port in `dashboard_backend.py` line 62 from `port=8000` to `port=8001`

### "WebSocket connection failed"
**Solution**: Make sure `dashboard_backend.py` is still running while accessing the dashboard

### "AWS credentials expired"
**Solution**: Run `aws configure` again with your credentials

---

## 📊 You're All Set!

Your environment is now fully configured. You can:
1. Run the traffic generator: `python traffic_generator.py`
2. Start the dashboard: `python dashboard_backend.py`
3. View the dashboard: `http://localhost:8000`

Good luck with your AWS exam! 🚀
