# 🚀 Dashboard Automation - Quick Start Guide

## ⚡ 5-Minute Setup

### **Step 1: Install Dependencies**
```bash
pip install pandas boto3 awscli
```

### **Step 2: Configure AWS**
```bash
aws configure
# Enter your AWS credentials when prompted
```

### **Step 3: Test Automation**
```bash
python scripts/dashboard_automation.py
```

### **Step 4: Set Up Scheduled Updates**

**Windows:**
```bash
# Run as Administrator
scripts\automate_dashboard.bat
```

**Linux/Mac:**
```bash
chmod +x scripts/automate_dashboard.sh
./scripts/automate_dashboard.sh
```

---

## 📊 Data Intake Options

### **Option A: Drop CSV Files**
1. Export telemetry data as CSV
2. Place in `data/raw/[track-name]/`
3. Run automation script
4. Dashboard updates automatically

### **Option B: Automated Schedule**
1. Edit `config/automation_config.json`
2. Set `schedule.enabled: true`
3. Configure frequency and time
4. Automation runs automatically

### **Option C: Manual Trigger**
```bash
# Quick update
python scripts/dashboard_automation.py

# With deployment
python dashboard/version_manager.py deploy
```

---

## 🔄 Typical Workflow

### **After Each Race Session:**
```bash
# 1. Export data from timing system
# 2. Place CSV in data/raw/
# 3. Run automation
python scripts/dashboard_automation.py

# 4. Verify dashboard
# Open: https://gr-cup-data-dev-us-east-1-v2.s3.amazonaws.com/dashboard/track_dashboard.html
```

### **Daily Updates:**
```bash
# Set up Windows Task Scheduler
# Task: Run scripts\automate_dashboard.bat
# Trigger: Daily at 6:00 AM
# Action: Start a program
```

---

## 🎯 What Gets Automated

✅ **Data Processing**
- Load new telemetry data
- Clean and validate
- Calculate performance metrics

✅ **Dashboard Generation**
- Generate driver statistics
- Calculate gear usage
- Create sector analysis

✅ **Deployment**
- Upload to S3
- Create version backup
- Update live dashboard

✅ **Monitoring**
- Log all operations
- Alert on failures
- Track data freshness

---

## 🛠️ Configuration

### **Edit `config/automation_config.json`:**

**Enable Auto-Deploy:**
```json
{
  "deployment": {
    "auto_deploy": true
  }
}
```

**Enable Scheduling:**
```json
{
  "schedule": {
    "enabled": true,
    "frequency": "daily",
    "time": "06:00"
  }
}
```

**Enable Notifications:**
```json
{
  "notifications": {
    "enabled": true,
    "email": {
      "enabled": true,
      "recipients": ["your-email@example.com"]
    }
  }
}
```

---

## 📋 Checklist

### **Initial Setup:**
- [ ] Python 3.7+ installed
- [ ] AWS CLI configured
- [ ] Dependencies installed
- [ ] Test automation script
- [ ] Configure automation settings

### **Regular Use:**
- [ ] Export telemetry data
- [ ] Place in data/raw/
- [ ] Run automation script
- [ ] Verify dashboard updates
- [ ] Check logs for errors

---

## 🆘 Troubleshooting

**Problem: Script fails to run**
```bash
# Check Python version
python --version

# Reinstall dependencies
pip install -r requirements.txt
```

**Problem: AWS deployment fails**
```bash
# Verify AWS credentials
aws sts get-caller-identity

# Test S3 access
aws s3 ls s3://gr-cup-data-dev-us-east-1-v2/
```

**Problem: Data not updating**
```bash
# Check data files exist
dir data\cleaned

# Manually process data
python scripts/process_real_data.py

# Check logs
type logs\automation.log
```

---

## 📞 Support

**Need Help?**
- Check `DASHBOARD_AUTOMATION_GUIDE.md` for detailed documentation
- Review logs in `logs/automation.log`
- Contact: support@grcup.com

---

## 🎉 Success!

Once set up, your dashboard will:
- ✅ Automatically process new data
- ✅ Update performance metrics
- ✅ Deploy to live dashboard
- ✅ Create version backups
- ✅ Monitor for issues

**Live Dashboard:**  
https://gr-cup-data-dev-us-east-1-v2.s3.amazonaws.com/dashboard/track_dashboard.html

---

*Setup Time: ~5 minutes*  
*Automation saves: ~30 minutes per update*