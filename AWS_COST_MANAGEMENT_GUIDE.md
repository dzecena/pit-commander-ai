# 💰 GR Cup Analytics - AWS Cost Management Guide

## Overview
This guide helps you manage AWS costs for the GR Cup Analytics platform, including cleanup procedures when the competition ends.

## 📊 Expected Monthly Costs

### **Development Stage (Current Deployment):**
- **Lambda Functions**: $0-5/month (first 1M requests free)
- **API Gateway**: $0-10/month (first 1M requests free) 
- **S3 Storage**: $1-15/month (depends on data volume)
- **DynamoDB**: $0-5/month (pay-per-request pricing)
- **CloudWatch Logs**: $1-3/month (log storage and monitoring)
- **Data Transfer**: $0-3/month (first 1GB free)

**Total Estimated Cost: $5-40/month for active usage**

### **Production Stage (If Deployed):**
- Similar costs but potentially higher due to increased usage
- Consider Reserved Instances for predictable workloads
- Monitor usage patterns and optimize accordingly

## 🚨 Cost Cleanup - When Competition Ends

### **Immediate Cleanup (Stops All Charges):**

**Option 1: Automated Cleanup Script**
```bash
# Run the comprehensive cleanup script
python scripts/aws_cleanup.py

# Follow prompts to confirm cleanup
# This removes ALL resources and stops charges
```

**Option 2: Manual Serverless Removal**
```bash
# Navigate to deployment directory
cd aws_deployment

# Remove entire stack
serverless remove --stage dev --region us-east-1
```

### **What Gets Removed:**
- ✅ **All Lambda Functions** - No more compute charges
- ✅ **API Gateway** - No more API call charges  
- ✅ **S3 Bucket & Data** - No more storage charges
- ✅ **DynamoDB Tables** - No more database charges
- ✅ **CloudWatch Logs** - No more log storage charges
- ✅ **All Associated Resources** - Complete cleanup

### **Backup Before Cleanup:**
The cleanup script automatically backs up:
- Performance baselines (`data/baselines/`)
- Deployment configuration (`deployment_info.json`)
- Serverless configuration (`serverless.yml`)

## 📈 Cost Monitoring

### **AWS Cost Explorer:**
1. Go to AWS Console → Cost Management → Cost Explorer
2. Filter by Service: Lambda, API Gateway, S3, DynamoDB
3. Set time range to monitor monthly costs
4. Create cost alerts for budget management

### **Recommended Cost Alerts:**
```bash
# Set up billing alerts in AWS Console
# Recommended thresholds:
# - $10/month: Early warning
# - $25/month: Investigation needed
# - $50/month: Immediate action required
```

### **Cost Optimization Tips:**
- **S3 Lifecycle Policies**: Move old data to cheaper storage classes
- **Lambda Memory**: Right-size memory allocation for functions
- **DynamoDB**: Use on-demand pricing for variable workloads
- **CloudWatch**: Set log retention periods (7-30 days)

## 🔄 Temporary Shutdown (Preserve Data)

### **If you want to pause without losing data:**

**Option 1: Scale Down Lambda**
```bash
# Reduce Lambda memory and timeout
# Edit aws_deployment/serverless.yml:
# memorySize: 128  # Minimum
# timeout: 10      # Reduced
```

**Option 2: S3 Only Mode**
```bash
# Remove compute resources, keep data
serverless remove --stage dev
# Keep S3 bucket manually for data preservation
```

## 💡 Cost-Effective Alternatives

### **For Long-Term Storage:**
- **S3 Glacier**: $1/TB/month for archival
- **S3 Intelligent Tiering**: Automatic cost optimization
- **Local Backup**: Download data for offline storage

### **For Occasional Use:**
- **On-Demand Deployment**: Deploy only when needed
- **Scheduled Shutdown**: Automate cleanup after events
- **Development-Only**: Use dev stage for testing

## 🎯 Cleanup Scenarios

### **End of Season Cleanup:**
```bash
# Complete removal - stops all charges
python scripts/aws_cleanup.py
# Estimated savings: $5-40/month
```

### **Between Events:**
```bash
# Keep data, remove compute
serverless remove --stage dev
# Keep S3 bucket manually
# Estimated savings: $3-25/month
```

### **Demo/Presentation Mode:**
```bash
# Deploy temporarily for demos
jupyter notebook notebooks/01_GR_Cup_Core_Deployment.ipynb
# Run cleanup after presentation
python scripts/aws_cleanup.py
```

## 📋 Cleanup Checklist

### **Before Cleanup:**
- [ ] **Backup Important Data** - Baselines, configurations
- [ ] **Export Reports** - Download any needed analytics
- [ ] **Notify Stakeholders** - Inform users of shutdown
- [ ] **Document Deployment** - Save configuration for future use

### **During Cleanup:**
- [ ] **Run Cleanup Script** - Use automated tool
- [ ] **Verify Removal** - Check AWS Console
- [ ] **Confirm Zero Charges** - Monitor billing
- [ ] **Save Backup Location** - Note where data is stored

### **After Cleanup:**
- [ ] **Monitor Billing** - Ensure charges stopped
- [ ] **Store Backup Safely** - Preserve important data
- [ ] **Document Process** - Note any issues for next time
- [ ] **Plan Redeployment** - If needed for future seasons

## 🚀 Redeployment Process

### **To Redeploy After Cleanup:**
```bash
# Use the Core Deployment Notebook
jupyter notebook notebooks/01_GR_Cup_Core_Deployment.ipynb

# Or manual deployment
cd aws_deployment
serverless deploy --stage dev --region us-east-1
```

### **Restore Data:**
```bash
# Copy backed up baselines
cp backup_*/baselines/* data/baselines/

# Upload to new S3 bucket
aws s3 sync data/cleaned/ s3://new-bucket-name/processed-telemetry/
```

## 💰 Cost Summary

### **Active Platform:**
- **Monthly Cost**: $5-40 depending on usage
- **Per Session**: ~$0.50-2.00 for processing
- **Per Driver**: ~$0.10-0.50 for analytics

### **After Cleanup:**
- **Monthly Cost**: $0 (complete removal)
- **Redeployment**: ~10 minutes using notebooks
- **Data Recovery**: Available from backups

### **Best Practices:**
- **Monitor Monthly**: Check costs regularly
- **Clean Up Promptly**: Remove resources when not needed
- **Use Automation**: Leverage cleanup scripts
- **Plan Ahead**: Budget for competition seasons

## 🎯 Emergency Cost Control

### **If Costs Spike Unexpectedly:**
```bash
# Immediate shutdown
python scripts/aws_cleanup.py

# Or quick manual removal
cd aws_deployment && serverless remove --stage dev
```

### **Investigation Steps:**
1. **Check AWS Cost Explorer** - Identify expensive services
2. **Review CloudWatch Metrics** - Look for unusual activity
3. **Check API Gateway Logs** - Monitor request volumes
4. **Verify S3 Usage** - Check storage and transfer costs

The cleanup system ensures you can **stop all AWS charges immediately** when the competition ends, while preserving the ability to redeploy quickly for future seasons! 🏁