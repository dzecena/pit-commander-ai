# 🏁 GR Cup Coaching Dashboard System

**Professional Racing Analytics & Coaching Platform for Toyota GR Cup**

A comprehensive coaching and analytics system that provides real-time performance insights, detailed telemetry analysis, and actionable coaching recommendations for driver development across 7 professional race tracks.

## 🎯 System Overview

### **Two-Dashboard Architecture**

**1. Main Coaching Dashboard** - Team overview and quick analysis
- Multi-driver performance comparison
- Real-time track selection
- Gear usage analysis with coaching
- Quick identification of problem areas

**2. Detailed Analysis Dashboard** - Deep-dive individual coaching
- Telemetry deep dive with charts
- Driver comparison analysis
- Historical performance trends
- Comprehensive gear optimization

### **Complete Data Coverage**
- **5 Drivers** - Complete performance profiles (001-005)
- **7 Tracks** - All major circuits covered
- **35 Driver-Track Combinations** - Full dataset
- **Real Track Images** - Extracted from official PDFs

### Supported Tracks
- **BMP**: Barber Motorsports Park (Technical)
- **COTA**: Circuit of the Americas (Mixed)
- **VIR**: Virginia International Raceway (High-Speed)
- **SEB**: Sebring International Raceway (Bumpy)
- **SON**: Sonoma Raceway (Elevation)
- **RA**: Road America (Long Straights)
- **INDY**: Indianapolis Motor Speedway (Oval)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- AWS CLI configured
- AWS S3 bucket access

### 1. Setup Environment

```bash
# Clone repository
git clone <repository>
cd pit-commander-ai

# Install dependencies
pip install pandas boto3 awscli

# Configure AWS
aws configure
# Enter your AWS credentials when prompted
```

### 2. Access Live Dashboards

**Main Coaching Dashboard:**
```
https://gr-cup-data-dev-us-east-1-v2.s3.amazonaws.com/dashboard/track_dashboard.html
```

**Detailed Analysis Dashboard:**
```
https://gr-cup-data-dev-us-east-1-v2.s3.amazonaws.com/dashboard/detailed_analysis.html
```

### 3. Automate Data Updates (Optional)

```bash
# Run automation script
python scripts/dashboard_automation.py

# Or use batch file (Windows)
scripts\automate_dashboard.bat
```

---

## 📊 Dashboard Features

### **Main Coaching Dashboard**

**Team Management:**
- View all 5 drivers simultaneously
- Color-coded status indicators (fast/struggling/needs-attention)
- Quick performance comparison
- Track selection dropdown

**Performance Analysis:**
- Best lap times and sector breakdown
- Speed and consistency metrics
- Gear usage distribution
- Performance vs session leader

**Coaching Insights:**
- Critical issues identification
- Specific improvement recommendations
- Strengths to maintain
- Chassis setup notes
- Track-specific coaching

**Navigation:**
- Click driver cards for detailed analysis
- "Deep Dive" buttons for quick access
- Keyboard shortcut: Ctrl+D
- Context-aware navigation

### **Detailed Analysis Dashboard**

**Four Analysis Modes:**

1. **Performance Overview**
   - Complete metrics and sector analysis
   - Gear usage with efficiency scoring
   - Track characteristics and insights
   - Advanced coaching recommendations

2. **Telemetry Deep Dive**
   - Speed vs distance charts
   - Throttle & brake analysis
   - G-force visualization
   - Technical metrics and tire data

3. **Driver Comparison**
   - Full standings table
   - Sector-by-sector comparison
   - Gear usage comparison
   - Competitive analysis

4. **Historical Trends**
   - Session-to-session improvement
   - Performance trend tracking
   - Goal setting for next sessions
   - Progress visualization

---

## 🤖 Dashboard Automation

### **Automated Data Pipeline**

The system includes complete automation for data intake and dashboard refresh:

**Quick Start:**
```bash
# Run complete automation
python scripts/dashboard_automation.py
```

**What Gets Automated:**
- ✅ Data loading from CSV files
- ✅ Performance analysis and metrics
- ✅ Dashboard data generation
- ✅ Version control and backup
- ✅ S3 deployment
- ✅ Monitoring and logging

### **Data Intake Methods**

**Method 1: CSV File Drop**
```bash
# 1. Export telemetry data as CSV
# 2. Place in data/raw/[track-name]/
# 3. Run automation
python scripts/dashboard_automation.py
```

**Method 2: Scheduled Automation**
```bash
# Windows Task Scheduler
# Program: python
# Arguments: scripts/dashboard_automation.py
# Trigger: Daily at 6:00 AM

# Linux/Mac Cron
0 6 * * * cd /path/to/project && python scripts/dashboard_automation.py
```

**Method 3: Manual Deployment**
```bash
# Create version backup
python dashboard/version_manager.py create v2.10 "Manual update"

# Deploy to S3
python dashboard/version_manager.py deploy
```

### **Configuration**

Edit `config/automation_config.json` to customize:
- Data sources and formats
- Processing options
- Deployment settings
- Scheduling preferences
- Notification settings

**Documentation:**
- `AUTOMATION_QUICK_START.md` - 5-minute setup
- `DASHBOARD_AUTOMATION_GUIDE.md` - Complete guide

---

## 📁 Project Structure

```
pit-commander-ai/
├── dashboard/                    # Dashboard files
│   ├── track_dashboard.html     # Main coaching dashboard
│   ├── detailed_analysis.html   # Detailed analysis dashboard
│   ├── track_images_embedded.js # Track image URLs
│   ├── version_manager.py       # Version control system
│   └── versions/                # Version backups
├── scripts/                     # Automation scripts
│   ├── dashboard_automation.py  # Main automation script
│   ├── automate_dashboard.bat   # Windows batch file
│   ├── process_real_data.py     # Data processing
│   └── extract_track_images.py  # Track image extraction
├── data/                        # Data directories
│   ├── raw/                     # Raw telemetry data
│   ├── cleaned/                 # Processed data
│   └── extracted/               # Extracted PDF data
├── config/                      # Configuration files
│   └── automation_config.json   # Automation settings
├── src/                         # Source code
│   ├── api/                     # API endpoints
│   ├── models/                  # ML models
│   └── data_processing/         # Data processors
└── docs/                        # Documentation
    ├── AUTOMATION_QUICK_START.md
    ├── DASHBOARD_AUTOMATION_GUIDE.md
    ├── NAVIGATION_GUIDE.md
    └── GEAR_ANALYSIS_GUIDE.md
```

---

## 🎯 Use Cases

### **For Coaches**
1. Open main dashboard for team overview
2. Identify drivers needing attention (red/orange status)
3. Click "Deep Dive" on problem drivers
4. Review detailed coaching recommendations
5. Focus practice on specific improvement areas

### **For Drivers**
1. Find your driver number in main dashboard
2. Review your performance metrics
3. Click "Deep Dive" for detailed analysis
4. Study gear usage and telemetry insights
5. Work on recommended improvement areas

### **For Team Managers**
1. Monitor overall team performance
2. Compare drivers across tracks
3. Track improvement trends
4. Make data-driven strategy decisions
5. Export data for post-session reviews

---

## 🔧 Advanced Features

### **Version Control**
```bash
# List all versions
python dashboard/version_manager.py list

# Rollback to previous version
python dashboard/version_manager.py rollback v2.8

# Create new version
python dashboard/version_manager.py create v2.10 "Description"

# Deploy current version
python dashboard/version_manager.py deploy
```

### **Data Processing**
```bash
# Process new telemetry data
python scripts/process_real_data.py

# Validate data quality
python scripts/validate_real_data.py

# Generate multi-driver data
python scripts/generate_multi_driver_data.py
```

### **Track Image Management**
```bash
# Extract track images from PDFs
python scripts/extract_track_images.py

# Upload track images to S3
aws s3 sync track-images/ s3://bucket/track-images/
```
```

## 📊 System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React         │    │   FastAPI        │    │   ML Models     │
│   Dashboard     │◄──►│   Backend        │◄──►│   (scikit-learn)│
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌──────────────────┐             │
         │              │   AWS Lambda     │             │
         └──────────────►│   (Serverless)   │◄────────────┘
                        │                  │
                        └──────────────────┘
                                 │
                        ┌──────────────────┐
                        │   AWS S3         │
                        │   (Data & Models)│
                        └──────────────────┘
```

## 🔧 Key Components

### Data Processing (`src/data_processing/`)
- **`data_cleaner.py`**: Handles lap errors, vehicle IDs, timestamp drift
- **`sector_parser.py`**: Analyzes 6-sector performance per track
- **`multi_track_loader.py`**: Loads and combines data from all 7 tracks

### ML Models (`src/models/`)
- **`tire_degradation.py`**: Predicts lap times based on tire age and conditions
- **`pit_strategy.py`**: Recommends optimal pit timing

### API (`src/api/`)
- **`main.py`**: FastAPI server with WebSocket streaming
- **`lambda_handler.py`**: AWS Lambda function for serverless predictions

## 📈 Model Performance

The tire degradation model achieves:
- **RMSE**: < 0.5 seconds
- **R²**: > 0.85
- **Features**: 8 engineered features including tire age, track characteristics, and race progress

### Key Features:
1. `tire_age` - Number of laps on current tires
2. `driver_avg_pace` - Driver's average lap time
3. `track_avg_speed` - Track characteristic speed
4. `track_degradation_rate` - Historical tire wear rate
5. `race_progress` - Percentage through race
6. `recent_pace_3lap` - Average of last 3 laps
7. `session_best` - Best lap time in session
8. `track_type_encoded` - 0=TECHNICAL, 1=HIGH_SPEED

## 🌐 API Endpoints

### Core Endpoints
- `GET /` - Health check
- `GET /tracks` - List available tracks with metadata
- `GET /track/{track_id}/summary` - Track characteristics and records
- `POST /predict/lap-time` - Predict lap time based on current conditions
- `POST /strategy/pit-window` - Calculate optimal pit window
- `WebSocket /ws/telemetry/{track_id}` - Live telemetry stream

### Example Request/Response

```json
// POST /predict/lap-time
{
  "tire_age": 15,
  "track_id": "VIR",
  "driver_avg_pace": 115.5,
  "current_pace": 116.2,
  "track_avg_speed": 145.0,
  "race_progress": 0.6
}

// Response
{
  "predicted_time": 117.3,
  "confidence": 0.87,
  "recommendation": "Monitor tire performance - degradation increasing",
  "uncertainty": 0.4
}
```

## 🏗️ Data Quality Handling

The system handles known GR Cup data issues:

1. **Lap Count Errors**: Value 32768 = ECU error → Reconstructed using timestamp gaps
2. **Vehicle ID Format**: GR86-chassis-carnum → Parsed with 000 = unassigned handling
3. **Timestamp Drift**: Uses `meta_time` over `timestamp` for accuracy
4. **Missing GPS Data**: Fallback to `laptrigger_lapdist_dls`

## 🚀 Deployment

### Local Development
```bash
# Start API server
uvicorn src.api.main:app --reload --port 8000

# Start dashboard (if created)
cd dashboard && npm start
```

### AWS Deployment
```bash
# Upload data and models to S3
aws s3 sync data/cleaned/ s3://your-bucket/data/
aws s3 sync models/ s3://your-bucket/models/

# Deploy Lambda function
cd aws && ./deploy_lambda.sh

# Setup API Gateway (manual or terraform)
```

## 📊 Sample Results

### Track Comparison
- **Sebring**: Highest tire degradation (+0.8s/lap)
- **Road America**: Longest track, moderate degradation
- **COTA**: High-speed characteristics, early pit windows

### Sector Analysis
- **IM2a**: Most tire-critical sector across tracks
- **FL**: Final sector shows highest degradation variance

## 🧪 Testing

```bash
# Run data processing tests
python -m pytest tests/test_data_processing.py

# Test API endpoints
python -m pytest tests/test_api.py

# Validate model performance
python scripts/validate_model.py
```

## 📝 Known Issues & Limitations

1. **Sample Data**: Currently using generated sample data - replace with real telemetry
2. **Pit Stop Detection**: Simplified tire age calculation (no pit stop detection)
3. **Weather**: No weather integration (future enhancement)
4. **Multi-car Strategy**: Individual car focus (team strategy future work)

## 🔮 Future Enhancements

- **Weather Integration**: Rain strategy recommendations
- **Driver Coaching**: Optimal braking points and racing lines
- **Team Radio Integration**: Voice-activated strategy updates
- **Multi-car Coordination**: Team-wide strategy optimization

---

## 🤖 Dashboard Automation System

### **Automated Data Pipeline**

The system includes complete automation for seamless data intake and dashboard refresh:

**One-Command Automation:**
```bash
# Run complete pipeline
python scripts/dashboard_automation.py
```

**What It Does:**
1. ✅ Loads telemetry data from CSV files
2. ✅ Analyzes driver performance metrics
3. ✅ Calculates gear usage and sector times
4. ✅ Generates dashboard JavaScript data
5. ✅ Creates version backup
6. ✅ Deploys to S3
7. ✅ Updates live dashboards

### **Scheduled Automation**

**Windows Task Scheduler:**
```powershell
# Create scheduled task (run as Administrator)
$action = New-ScheduledTaskAction -Execute 'python' -Argument 'scripts/dashboard_automation.py' -WorkingDirectory 'C:\path\to\pit-commander-ai'
$trigger = New-ScheduledTaskTrigger -Daily -At 6am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "GR Cup Dashboard Update"
```

**Linux/Mac Cron:**
```bash
# Edit crontab
crontab -e

# Add automation job (runs daily at 6 AM)
0 6 * * * cd /path/to/pit-commander-ai && python scripts/dashboard_automation.py >> logs/automation.log 2>&1
```

### **Data Intake Workflow**

**After Each Race Session:**
1. Export telemetry data as CSV from timing system
2. Place CSV files in `data/raw/[track-name]/`
3. Run automation: `python scripts/dashboard_automation.py`
4. Dashboard automatically updates with new data
5. Review updated coaching insights

**Supported Data Formats:**
- CSV files with telemetry data
- JSON format telemetry
- Direct database connections
- API integrations

### **Configuration**

Edit `config/automation_config.json` to customize:
```json
{
  "data_sources": {
    "csv_directory": "data/raw"
  },
  "deployment": {
    "s3_bucket": "gr-cup-data-dev-us-east-1-v2",
    "auto_deploy": true
  },
  "schedule": {
    "enabled": true,
    "frequency": "daily",
    "time": "06:00"
  }
}
```

---

## 📚 Documentation

### **Dashboard Guides**
- `dashboard/README.md` - Dashboard system overview
- `dashboard/NAVIGATION_GUIDE.md` - Navigation instructions
- `dashboard/GEAR_ANALYSIS_GUIDE.md` - Gear coaching guide
- `dashboard/VERSION_GUIDE.md` - Version management

### **Automation Guides**
- `AUTOMATION_QUICK_START.md` - 5-minute setup
- `DASHBOARD_AUTOMATION_GUIDE.md` - Complete automation guide
- `config/automation_config.json` - Configuration reference

### **Technical Guides**
- `AWS_DEPLOYMENT_GUIDE.md` - AWS setup and deployment
- `NEW_DATA_INTEGRATION_GUIDE.md` - Data integration procedures
- `PDF_DATA_EXTRACTION_GUIDE.md` - Track image extraction

---

## 🏆 System Capabilities

### **Coaching Features**
✅ **Multi-driver analysis** - 5 drivers with complete profiles  
✅ **Multi-track support** - 7 professional race tracks  
✅ **Gear usage coaching** - Comprehensive optimization insights  
✅ **Sector analysis** - 6-sector breakdown per track  
✅ **Performance comparison** - Driver vs driver analysis  
✅ **Real track images** - Actual track layouts from PDFs  
✅ **Telemetry visualization** - Speed, throttle, brake, G-force charts  
✅ **Historical tracking** - Performance trends over time  

### **Technical Features**
✅ **Automated data processing** - One-command pipeline  
✅ **Version control** - Complete backup and rollback system  
✅ **AWS S3 hosting** - Public dashboard access  
✅ **Real-time updates** - Live performance changes  
✅ **Responsive design** - Works on all devices  
✅ **Context-aware navigation** - Smart dashboard switching  
✅ **Export capabilities** - Data and report generation  

---

## 🎯 Quick Reference

### **Live Dashboards**
- Main: https://gr-cup-data-dev-us-east-1-v2.s3.amazonaws.com/dashboard/track_dashboard.html
- Detailed: https://gr-cup-data-dev-us-east-1-v2.s3.amazonaws.com/dashboard/detailed_analysis.html

### **Common Commands**
```bash
# Automate dashboard update
python scripts/dashboard_automation.py

# Deploy dashboards
python dashboard/version_manager.py deploy

# List versions
python dashboard/version_manager.py list

# Rollback version
python dashboard/version_manager.py rollback v2.8

# Process new data
python scripts/process_real_data.py
```

### **Navigation Shortcuts**
- **Ctrl+D** - Quick access to detailed analysis
- **Click driver cards** - Select driver for analysis
- **Deep Dive buttons** - Jump to detailed analysis
- **Track selector** - Switch between tracks

---

## 👥 Team

**GR Cup Analytics Team**
- Dashboard Development & UX
- Data Engineering & Automation
- Performance Analysis & Coaching
- AWS Infrastructure & Deployment

## 📄 License

MIT License - See LICENSE file for details

---

**GR Cup Coaching Dashboard System**  
*Professional racing analytics and driver development platform*  
*Version 2.9 - Complete Automation System*