# 🤖 Dashboard Automation Guide

## 🎯 Overview

This guide explains how to automate data intake and dashboard refresh for the GR Cup Analytics system.

---

## 🔄 Automation Pipeline

### **Complete Workflow:**
```
New Telemetry Data → Process & Analyze → Generate Dashboard Data → Deploy to S3 → Live Dashboard Updated
```

---

## 🚀 Quick Start

### **Option 1: Automated Script (Recommended)**
```bash
# Run complete automation pipeline
python scripts/dashboard_automation.py
```

### **Option 2: Manual Steps**
```bash
# Step 1: Process new data
python scripts/process_real_data.py

# Step 2: Generate dashboard data
python scripts/dashboard_automation.py

# Step 3: Deploy to S3
python dashboard/version_manager.py deploy
```

---

## 📁 Data Intake Methods

### **Method 1: CSV File Drop**
**Best for:** Regular data updates from timing systems

**Process:**
1. Export telemetry data as CSV from timing system
2. Place CSV files in `data/raw/[track-name]/`
3. Run automation script
4. Dashboard automatically updates

**CSV Format Required:**
```csv
vehicle_id,timestamp,lap,Speed,Gear,throttle,brake,steering,...
GR86-001-001,1635724800000,1,158.5,5,75.2,0.0,-0.5,...
```

### **Method 2: API Integration**
**Best for:** Real-time data feeds

**Setup:**
```python
# In scripts/api_data_intake.py
import requests

def fetch_telemetry_data(session_id):
    response = requests.get(f'https://timing-api.com/session/{session_id}')
    data = response.json()
    save_to_csv(data)
    trigger_automation()
```

### **Method 3: Database Connection**
**Best for:** Existing database systems

**Setup:**
```python
# In scripts/db_data_intake.py
import psycopg2

def fetch_from_database():
    conn = psycopg2.connect("dbname=racing user=admin")
    query = "SELECT * FROM telemetry WHERE session_date = CURRENT_DATE"
    df = pd.read_sql(query, conn)
    save_and_process(df)
```

---

## ⚙️ Automation Configuration

### **Configuration File: `config/automation_config.json`**
```json
{
  "data_sources": {
    "csv_directory": "data/raw",
    "api_endpoint": "https://timing-api.com",
    "database_connection": "postgresql://localhost/racing"
  },
  "processing": {
    "auto_clean": true,
    "validate_data": true,
    "generate_reports": true
  },
  "deployment": {
    "s3_bucket": "gr-cup-data-dev-us-east-1-v2",
    "auto_deploy": true,
    "create_backup": true
  },
  "schedule": {
    "enabled": true,
    "frequency": "hourly",
    "time": "00:00"
  }
}
```

---

## 🕐 Scheduled Automation

### **Option 1: Windows Task Scheduler**

**Create Scheduled Task:**
1. Open Task Scheduler
2. Create Basic Task
3. Name: "GR Cup Dashboard Update"
4. Trigger: Daily at specific time
5. Action: Start a program
   - Program: `python`
   - Arguments: `scripts/dashboard_automation.py`
   - Start in: `C:\path\to\pit-commander-ai`

**PowerShell Command:**
```powershell
$action = New-ScheduledTaskAction -Execute 'python' -Argument 'scripts/dashboard_automation.py' -WorkingDirectory 'C:\path\to\pit-commander-ai'
$trigger = New-ScheduledTaskTrigger -Daily -At 6am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "GR Cup Dashboard Update"
```

### **Option 2: Cron Job (Linux/Mac)**
```bash
# Edit crontab
crontab -e

# Add automation job (runs every hour)
0 * * * * cd /path/to/pit-commander-ai && python scripts/dashboard_automation.py >> logs/automation.log 2>&1

# Or run after each race session (example: 6 PM daily)
0 18 * * * cd /path/to/pit-commander-ai && python scripts/dashboard_automation.py
```

### **Option 3: AWS Lambda (Cloud Automation)**
```python
# lambda_function.py
import boto3
import subprocess

def lambda_handler(event, context):
    # Trigger automation pipeline
    # Download data from S3
    # Process and update dashboards
    # Upload results back to S3
    
    return {
        'statusCode': 200,
        'body': 'Dashboard updated successfully'
    }
```

---

## 📊 Data Processing Pipeline

### **Step 1: Data Validation**
```python
def validate_telemetry_data(df):
    """Validate incoming telemetry data"""
    required_columns = ['vehicle_id', 'timestamp', 'lap', 'Speed', 'Gear']
    
    # Check required columns
    missing = set(required_columns) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    
    # Check data types
    assert df['Speed'].dtype in ['float64', 'int64']
    assert df['Gear'].dtype == 'int64'
    
    # Check value ranges
    assert df['Speed'].between(0, 200).all()
    assert df['Gear'].between(1, 6).all()
    
    return True
```

### **Step 2: Data Cleaning**
```python
def clean_telemetry_data(df):
    """Clean and prepare telemetry data"""
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Handle missing values
    df = df.fillna(method='ffill')
    
    # Filter outliers
    df = df[df['Speed'] < 200]
    
    # Sort by timestamp
    df = df.sort_values(['vehicle_id', 'timestamp'])
    
    return df
```

### **Step 3: Performance Analysis**
```python
def analyze_performance(df):
    """Analyze driver performance metrics"""
    metrics = {
        'best_lap': calculate_best_lap(df),
        'avg_speed': df['Speed'].mean(),
        'consistency': calculate_consistency(df),
        'gear_usage': calculate_gear_usage(df)
    }
    return metrics
```

### **Step 4: Dashboard Generation**
```python
def generate_dashboard_data(metrics):
    """Generate JavaScript data for dashboards"""
    js_data = f"const DASHBOARD_DATA = {json.dumps(metrics)};"
    save_to_file(js_data, 'dashboard/dashboard_data.js')
```

---

## 🔄 Real-Time Updates

### **WebSocket Integration (Advanced)**
```python
# Real-time data streaming
import websocket

def on_message(ws, message):
    """Handle incoming telemetry data"""
    data = json.loads(message)
    process_telemetry(data)
    update_dashboard()

def on_error(ws, error):
    logger.error(f"WebSocket error: {error}")

def on_close(ws):
    logger.info("WebSocket connection closed")

# Connect to timing system
ws = websocket.WebSocketApp(
    "wss://timing-system.com/live",
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)
```

---

## 📈 Monitoring & Alerts

### **Automation Monitoring Script**
```python
# scripts/monitor_automation.py
def check_automation_health():
    """Monitor automation pipeline health"""
    checks = {
        'last_update': check_last_update_time(),
        'data_freshness': check_data_freshness(),
        's3_deployment': check_s3_status(),
        'error_rate': check_error_logs()
    }
    
    if any(not v for v in checks.values()):
        send_alert("Automation pipeline issue detected")
    
    return checks
```

### **Email Alerts**
```python
import smtplib
from email.mime.text import MIMEText

def send_alert(message):
    """Send email alert for automation issues"""
    msg = MIMEText(message)
    msg['Subject'] = 'GR Cup Dashboard Alert'
    msg['From'] = 'alerts@grcup.com'
    msg['To'] = 'admin@grcup.com'
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('user', 'password')
        server.send_message(msg)
```

---

## 🛠️ Troubleshooting

### **Common Issues:**

**Issue 1: Data Not Updating**
```bash
# Check last automation run
cat logs/automation.log | tail -20

# Manually trigger update
python scripts/dashboard_automation.py

# Verify S3 deployment
aws s3 ls s3://gr-cup-data-dev-us-east-1-v2/dashboard/
```

**Issue 2: Invalid Data Format**
```bash
# Validate CSV format
python scripts/validate_real_data.py

# Check data cleaning logs
cat logs/data_cleaning.log
```

**Issue 3: S3 Deployment Failure**
```bash
# Check AWS credentials
aws sts get-caller-identity

# Test S3 access
aws s3 ls s3://gr-cup-data-dev-us-east-1-v2/

# Manually deploy
python dashboard/version_manager.py deploy
```

---

## 📋 Automation Checklist

### **Initial Setup:**
- [ ] Install required Python packages
- [ ] Configure AWS credentials
- [ ] Set up data directories
- [ ] Test automation script manually
- [ ] Configure scheduled task/cron job
- [ ] Set up monitoring and alerts

### **Regular Maintenance:**
- [ ] Review automation logs weekly
- [ ] Verify data quality monthly
- [ ] Update automation scripts as needed
- [ ] Monitor S3 storage costs
- [ ] Test backup and recovery procedures

---

## 🎯 Best Practices

1. **Always Validate Data** - Check data quality before processing
2. **Create Backups** - Version control and S3 versioning
3. **Monitor Performance** - Track automation execution time
4. **Log Everything** - Comprehensive logging for troubleshooting
5. **Test Changes** - Test automation updates in dev environment
6. **Document Updates** - Keep automation guide current

---

## 🚀 Advanced Features

### **Multi-Source Data Aggregation**
```python
def aggregate_data_sources():
    """Combine data from multiple sources"""
    csv_data = load_csv_data()
    api_data = fetch_api_data()
    db_data = query_database()
    
    combined = pd.concat([csv_data, api_data, db_data])
    return deduplicate_and_merge(combined)
```

### **Incremental Updates**
```python
def incremental_update():
    """Update only changed data"""
    last_update = get_last_update_timestamp()
    new_data = fetch_data_since(last_update)
    
    if new_data:
        process_and_deploy(new_data)
    else:
        logger.info("No new data to process")
```

### **A/B Testing**
```python
def deploy_with_testing():
    """Deploy to staging first, then production"""
    deploy_to_staging()
    run_automated_tests()
    
    if tests_pass():
        deploy_to_production()
    else:
        rollback_and_alert()
```

---

## 📞 Support

**For automation issues:**
- Check logs in `logs/automation.log`
- Review error messages
- Consult troubleshooting section
- Contact: support@grcup.com

---

*Last Updated: November 7, 2025*  
*Automation System v1.0*