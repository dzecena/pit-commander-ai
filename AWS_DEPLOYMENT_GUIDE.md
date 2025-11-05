# 🏁 GR Cup Analytics - AWS Deployment Guide

This guide walks you through deploying the GR Cup Analytics platform to AWS, creating a live, scalable environment to showcase your telemetry data.

## 🏗️ Architecture Overview

The deployment creates:

- **API Gateway + Lambda**: FastAPI application serving telemetry data and analytics
- **S3 Bucket**: Storage for telemetry files and analysis results  
- **DynamoDB**: Metadata storage for quick queries
- **CloudFront**: CDN for fast global access
- **Interactive Dashboard**: Web-based analytics interface

## 📋 Prerequisites

### 1. Install Required Tools

```bash
# Install Node.js and npm (for Serverless Framework)
# Download from: https://nodejs.org/

# Install Serverless Framework
npm install -g serverless

# Install AWS CLI
# Download from: https://aws.amazon.com/cli/

# Configure AWS credentials
aws configure
```

### 2. Python Dependencies

```bash
# Install deployment dependencies
pip install boto3 pandas
```

## 🚀 Deployment Steps

### Step 1: Prepare Your Environment

```bash
# Navigate to your project directory
cd pit-commander-ai

# Install Node.js dependencies for deployment
cd aws_deployment
npm install
cd ..
```

### Step 2: Run the Deployment Script

```bash
# Run the automated deployment
python aws_deployment/deploy.py
```

The script will prompt you for:
- **Deployment stage** (dev/prod) - Choose 'dev' for testing
- **AWS region** - Choose your preferred region (e.g., us-east-1)
- **Data upload option** - Choose to upload existing data or create demo data

### Step 3: Monitor Deployment

The deployment process will:

1. ✅ Check prerequisites (Serverless, AWS credentials)
2. 🚀 Deploy infrastructure using CloudFormation
3. 📊 Upload telemetry data to S3
4. 📈 Upload analysis results
5. 🌐 Provide access URLs

## 🎯 What Gets Deployed

### API Endpoints

- `GET /` - API information and health check
- `GET /tracks` - List all available tracks
- `GET /telemetry/{track_id}` - Get telemetry data for a track
- `GET /analytics/{track_id}` - Get analytics summary for a track
- `GET /dashboard` - Interactive web dashboard

### Data Storage

- **S3 Bucket**: `gr-cup-data-{stage}`
  - `processed-telemetry/` - Clean telemetry CSV files
  - `analysis-results/` - Generated charts and reports
  - `raw-telemetry/` - Original uploaded files

### Database

- **DynamoDB Table**: `gr-cup-telemetry-{stage}`
  - Stores metadata for quick queries
  - Track information and processing status

## 🌐 Accessing Your Deployment

After successful deployment, you'll receive:

```
✅ DEPLOYMENT COMPLETE!
==============================
🌐 API URL: https://abc123.execute-api.us-east-1.amazonaws.com/dev
📊 Dashboard: https://abc123.execute-api.us-east-1.amazonaws.com/dev/dashboard
🪣 S3 Bucket: gr-cup-data-dev
🏷️  Stage: dev
🌍 Region: us-east-1
```

### Dashboard Features

The web dashboard provides:

- **Track Selection**: Choose from all 7 GR Cup tracks
- **Real-time Analytics**: Speed, braking, and performance metrics
- **Interactive Charts**: Plotly-powered visualizations
- **Lap Analysis**: Per-lap performance breakdown
- **Quick Stats**: Key performance indicators

### API Usage Examples

```bash
# Get all tracks
curl https://your-api-url/tracks

# Get Barber telemetry data
curl https://your-api-url/telemetry/BMP

# Get COTA analytics
curl https://your-api-url/analytics/COTA
```

## 📊 Data Management

### Uploading New Telemetry Data

```bash
# Upload to S3 (triggers automatic processing)
aws s3 cp your_telemetry.csv s3://gr-cup-data-dev/raw-telemetry/

# Or use the AWS Console to upload files
```

### Accessing Analysis Results

All generated charts and reports are available at:
- S3 bucket: `s3://gr-cup-data-{stage}/analysis-results/`
- Web access: Via CloudFront distribution

## 🔧 Configuration

### Environment Variables

The deployment automatically sets:
- `STAGE`: Deployment stage (dev/prod)
- `REGION`: AWS region
- Bucket and table names with stage suffix

### Scaling Configuration

Default settings:
- **Lambda Memory**: 512MB
- **Lambda Timeout**: 30 seconds
- **DynamoDB**: Pay-per-request billing
- **S3**: Standard storage class

## 🛠️ Troubleshooting

### Common Issues

1. **Serverless not found**
   ```bash
   npm install -g serverless
   ```

2. **AWS credentials not configured**
   ```bash
   aws configure
   ```

3. **Deployment timeout**
   - Check AWS CloudFormation console for detailed errors
   - Ensure IAM permissions are sufficient

4. **API not responding**
   - Check Lambda logs: `serverless logs -f api`
   - Verify S3 bucket permissions

### Monitoring

- **CloudWatch Logs**: Monitor Lambda function execution
- **CloudWatch Metrics**: Track API usage and performance
- **S3 Access Logs**: Monitor data access patterns

## 💰 Cost Estimation

Estimated monthly costs for development stage:

- **Lambda**: $0-5 (first 1M requests free)
- **API Gateway**: $0-10 (first 1M requests free)
- **S3**: $1-5 (depending on data volume)
- **DynamoDB**: $0-5 (pay-per-request)
- **CloudFront**: $0-1 (first 1TB free)

**Total**: ~$5-25/month for development usage

## 🔄 Updates and Maintenance

### Updating the Application

```bash
# Make code changes, then redeploy
cd aws_deployment
serverless deploy
```

### Adding New Tracks

1. Upload telemetry data to S3
2. Update track configuration in API
3. Redeploy application

### Cleanup

```bash
# Remove all AWS resources
cd aws_deployment
serverless remove
```

## 🎯 Next Steps

After deployment:

1. **Test the Dashboard**: Visit the dashboard URL and explore analytics
2. **API Integration**: Use the API endpoints in your applications  
3. **Data Pipeline**: Set up automated telemetry data uploads
4. **Custom Analytics**: Extend the API with additional analysis endpoints
5. **Production Deployment**: Deploy to production stage when ready

## 📞 Support

For deployment issues:
1. Check AWS CloudFormation console for detailed error messages
2. Review Lambda function logs in CloudWatch
3. Verify IAM permissions and AWS service limits
4. Ensure all prerequisites are properly installed

Your GR Cup Analytics platform is now live and ready to showcase real telemetry data to stakeholders! 🏁