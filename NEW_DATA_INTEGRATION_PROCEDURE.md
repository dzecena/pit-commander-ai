# 🏁 GR Cup New Data Integration Procedure

## Overview
This document outlines the automated procedure for integrating new telemetry data with existing baselines for continuous driver performance analysis.

## 📋 Required Data Format

### **Input Data Format (CSV)**
New telemetry files must follow this exact format:

```csv
vehicle_id,timestamp,meta_time,lap,Speed,pbrake_f,ath,Steering_Angle,accx_can,accy_can,nmotor,Gear,track_name,track_id
GR86-002-015,1761847091636,1761847091636,1,158.02,0.0,77.00,-0.16,-0.84,0.45,6900.42,5,Barber Motorsports Park,BMP
```

### **Required Columns:**
- `vehicle_id` - Format: GR86-{chassis}-{car_number} (e.g., GR86-002-015)
- `timestamp` - Unix timestamp in milliseconds
- `meta_time` - Message received timestamp (more accurate)
- `lap` - Lap number (1, 2, 3, etc.)
- `Speed` - Vehicle speed in mph
- `pbrake_f` - Front brake pressure (0-100)
- `ath` - Throttle position (0-100%)
- `Steering_Angle` - Steering wheel angle in degrees
- `accx_can` - Longitudinal G-force (+ = acceleration, - = braking)
- `accy_can` - Lateral G-force (+ = left turn, - = right turn)
- `nmotor` - Engine RPM
- `Gear` - Current gear (1-6)
- `track_name` - Full track name
- `track_id` - Track abbreviation (BMP, COTA, VIR, etc.)

### **File Naming Convention:**
- Format: `{TRACK_ID}_{SESSION_DATE}_{SESSION_TYPE}.csv`
- Examples: 
  - `BMP_20251104_PRACTICE.csv`
  - `COTA_20251105_QUALIFYING.csv`
  - `VIR_20251106_RACE.csv`

## 🔄 Automated Integration Process

### **Step 1: Data Upload**
```bash
# Upload new data to S3 raw bucket
aws s3 cp BMP_20251104_PRACTICE.csv s3://gr-cup-data-dev-us-east-1-v2/raw-telemetry/
```

### **Step 2: Automatic Processing**
The system automatically:
1. **Detects new file** (S3 event trigger)
2. **Runs data cleaning** (same process as baseline)
3. **Compares with existing baseline**
4. **Updates performance metrics**
5. **Generates comparison report**

## 📊 Baseline Comparison System

### **Current Baseline Structure:**
```
data/baselines/
├── BMP_baseline_metrics.json
├── COTA_baseline_metrics.json
├── VIR_baseline_metrics.json
└── ...
```

### **Baseline Metrics Stored:**
- Field average speeds by sector
- Typical braking patterns
- Cornering G-force benchmarks
- Gear usage distributions
- Lap time percentiles

### **New Data Comparison:**
1. **Individual Performance vs Baseline**
2. **New Driver vs Existing Drivers**
3. **Session-to-Session Improvement**
4. **Track Record Updates**
##
 🤖 Automated Processing Workflow

### **AWS Lambda Integration**
The system includes automated processing via AWS Lambda:

```python
# Triggered automatically when new file uploaded to S3
def lambda_handler(event, context):
    # 1. Detect new file upload
    # 2. Validate data format
    # 3. Run cleaning process
    # 4. Compare with baseline
    # 5. Update dashboard data
    # 6. Send notification
```

### **Processing Steps:**
1. **File Upload Detection** - S3 event triggers processing
2. **Data Validation** - Check format and quality
3. **Automated Cleaning** - Same process as baseline data
4. **Baseline Comparison** - Compare new vs existing performance
5. **Dashboard Update** - New data appears in live dashboard
6. **Report Generation** - Automated performance report

## 📈 Performance Comparison Features

### **Individual Driver Tracking:**
- **Session-to-Session Improvement**
- **Personal Best Updates**
- **Consistency Scoring**
- **Sector-by-Sector Progress**

### **Field Comparison:**
- **Percentile Ranking** - Where driver ranks vs field
- **Baseline Deviation** - How much faster/slower than average
- **Competitive Analysis** - Performance vs other drivers
- **Track Records** - New track records automatically detected

### **Coaching Insights:**
- **Improvement Areas** - Specific sectors needing work
- **Strength Building** - Leverage best performing areas
- **Setup Recommendations** - Based on performance patterns
- **Time Gain Potential** - Quantified improvement opportunities

## 🔄 Usage Examples

### **Adding New Session Data:**
```bash
# 1. Upload new telemetry file
aws s3 cp BMP_20251104_PRACTICE.csv s3://gr-cup-data-dev-us-east-1-v2/raw-telemetry/

# 2. System automatically processes (no manual intervention needed)

# 3. View results in dashboard
# https://13x5l5w5pi.execute-api.us-east-1.amazonaws.com/dev/dashboard
```

### **Manual Processing (if needed):**
```bash
# Run new data processor
python scripts/new_data_processor.py --file BMP_20251104_PRACTICE.csv

# Check processing results
cat data/baselines/BMP_baseline_metrics.json
```

## 📊 Dashboard Integration

### **Automatic Updates:**
- **New drivers appear** in dropdown menus
- **Performance comparisons** update with new baseline
- **Historical tracking** shows session-to-session progress
- **Recommendations** adapt based on latest data

### **Comparison Views:**
- **Before/After Performance** - Session comparison
- **Driver Rankings** - Updated field positions
- **Progress Tracking** - Improvement over time
- **Competitive Analysis** - How drivers stack up

## 🎯 Benefits for GR Cup Teams

### **For Drivers:**
- **Immediate Feedback** - Performance analysis within minutes
- **Specific Coaching** - Targeted improvement areas
- **Progress Tracking** - See improvement over time
- **Competitive Benchmarking** - Know where you stand

### **For Teams:**
- **Data-Driven Decisions** - Setup and strategy based on data
- **Driver Development** - Track progress and focus areas
- **Competitive Intelligence** - Understand field performance
- **Automated Workflow** - No manual data processing needed

### **For Series Organizers:**
- **Real-time Analytics** - Live performance monitoring
- **Driver Safety** - Identify risky driving patterns
- **Competitive Balance** - Monitor field competitiveness
- **Fan Engagement** - Rich data for broadcasts and apps

## 🔧 Technical Requirements

### **Data Source Requirements:**
- **Consistent Format** - Same CSV structure as baseline
- **Quality Standards** - <10% missing critical data
- **Timing Accuracy** - Proper timestamp synchronization
- **Vehicle Identification** - Correct GR86-XXX-XXX format

### **System Requirements:**
- **AWS Account** - For cloud processing and storage
- **S3 Bucket** - For data storage and triggers
- **Lambda Functions** - For automated processing
- **API Gateway** - For dashboard access

### **Monitoring & Alerts:**
- **Processing Status** - Success/failure notifications
- **Data Quality Alerts** - Warning for poor quality data
- **Performance Alerts** - New track records or safety concerns
- **System Health** - Infrastructure monitoring

## 🚀 Future Enhancements

### **Planned Features:**
- **Real-time Processing** - Live telemetry during sessions
- **Predictive Analytics** - Lap time and performance predictions
- **Advanced Coaching** - AI-powered driving recommendations
- **Mobile App** - Driver-specific performance app
- **Video Integration** - Sync telemetry with onboard footage

### **Advanced Analytics:**
- **Machine Learning Models** - Predict optimal setups
- **Weather Integration** - Performance vs conditions
- **Tire Degradation Models** - Predict pit strategy
- **Fuel Consumption Analysis** - Optimize race strategy

This system provides a complete, automated solution for continuous GR Cup performance analysis and driver development! 🏁