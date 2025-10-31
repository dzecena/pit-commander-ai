# 🏁 GR Cup Analytics - Complete Setup Guide

**Get your real Toyota GR Cup data and start analyzing!**

## 📁 **File Organization (IMPORTANT!)**

### **Track Maps (PDF Format)**
**Put in:** `Track Maps/`
```
Track Maps/
├── barber-motorsports-park-map.pdf
├── circuit-of-the-americas-map.pdf
├── indianapolis-map.pdf
├── road-america-map.pdf
├── sebring-map.pdf
├── sonoma-map.pdf
└── virginia-international-raceway-map.pdf
```

### **Data Files (ZIP Format)**
**Put in:** `data/raw/`
```
data/raw/
├── barber-motorsports-park.zip
├── circuit-of-the-americas.zip
├── indianapolis.zip
├── road-america.zip
├── sebring.zip
├── sonoma.zip
└── virginia-international-raceway.zip
```

## 🚀 **Quick Start (3 Methods)**

### **Method 1: Automatic Download (Recommended)**
```bash
# Download all data files automatically
python scripts/download_data.py
```

### **Method 2: Manual Download**
1. Visit: https://trddev.com/hackathon-2025/Data files Order
2. Download each ZIP file
3. Save to `data/raw/` folder

### **Method 3: Command Line**
```powershell
# Windows PowerShell
New-Item -ItemType Directory -Force -Path "data/raw"

# Download each file
Invoke-WebRequest -Uri "https://trddev.com/hackathon-2025/barber-motorsports-park.zip" -OutFile "data/raw/barber-motorsports-park.zip"
Invoke-WebRequest -Uri "https://trddev.com/hackathon-2025/circuit-of-the-americas.zip" -OutFile "data/raw/circuit-of-the-americas.zip"
Invoke-WebRequest -Uri "https://trddev.com/hackathon-2025/indianapolis.zip" -OutFile "data/raw/indianapolis.zip"
Invoke-WebRequest -Uri "https://trddev.com/hackathon-2025/road-america.zip" -OutFile "data/raw/road-america.zip"
Invoke-WebRequest -Uri "https://trddev.com/hackathon-2025/sebring.zip" -OutFile "data/raw/sebring.zip"
Invoke-WebRequest -Uri "https://trddev.com/hackathon-2025/sonoma.zip" -OutFile "data/raw/sonoma.zip"
Invoke-WebRequest -Uri "https://trddev.com/hackathon-2025/virginia-international-raceway.zip" -OutFile "data/raw/virginia-international-raceway.zip"
```

## 🔄 **Processing Pipeline**

### **Step 1: Extract and Process Data**
```bash
# Extract ZIP files and clean data
python scripts/process_real_data.py
```

**What this does:**
- ✅ Extracts all ZIP files to `data/extracted/`
- ✅ Identifies telemetry, lap times, sector data
- ✅ Cleans data (fixes lap errors, timestamps)
- ✅ Standardizes formats
- ✅ Generates quality reports

### **Step 2: Extract PDF Data (If Needed)**
```bash
# Extract data from PDF files
python scripts/extract_pdf_data.py
```

**What this does:**
- ✅ Finds PDF files in Track Maps/ and data folders
- ✅ Extracts tables from PDFs
- ✅ Converts to CSV format
- ✅ Maps sector data (S1.a → IM1a, etc.)

### **Step 3: Train ML Model**
```bash
# Train model with real GR Cup data
python scripts/train_model.py
```

**What this does:**
- ✅ Loads all cleaned track data
- ✅ Engineers features for tire degradation
- ✅ Trains ML model (target: R² > 0.95)
- ✅ Saves model artifacts
- ✅ Generates performance reports

### **Step 4: Test System**
```bash
# Test predictions with real data
python demo/race_demo.py
```

**What this does:**
- ✅ Simulates race scenarios
- ✅ Shows real-time predictions
- ✅ Demonstrates pit strategy
- ✅ Compares tracks

### **Step 5: Start API Server**
```bash
# Start the prediction API
uvicorn src.api.main:app --reload --port 8000
```

## 📊 **Expected Data Structure**

After processing, you'll have:

```
data/
├── raw/                          # Your downloaded ZIP files
│   ├── barber-motorsports-park.zip
│   ├── circuit-of-the-americas.zip
│   └── ...
├── extracted/                    # Auto-extracted from ZIPs
│   ├── barber-motorsports-park/
│   │   ├── telemetry_data.csv
│   │   ├── lap_times.csv
│   │   ├── AnalysisEnduranceWithSections.csv
│   │   └── results.csv
│   └── ...
├── cleaned/                      # Processed and cleaned
│   ├── BMP_telemetry_clean.csv
│   ├── BMP_cleaning_stats.json
│   └── ...
└── extracted_from_pdf/           # From PDF extraction
    ├── track_map_data.csv
    └── ...
```

## 🎯 **Key Data We're Looking For**

### **Priority 1: Telemetry Data**
- Time, Speed, RPM, Throttle, Brake, Steering, Gear, Lap
- This gives us the most ML value

### **Priority 2: Sector Analysis ("Analysis with Sections")**
- 6-sector timing: IM1a, IM1, IM2a, IM2, IM3a, FL
- Maps to track sectors: S1.a, S1.b, S2.a, S2.b, S3.a, S3.b

### **Priority 3: Lap Times**
- Lap number, lap time, sector splits
- For validation and comparison

## 🔍 **Data Quality Checks**

Our system automatically handles:
- ✅ **Lap errors** (32768 values) → Fixed using timestamp gaps
- ✅ **Vehicle IDs** (GR86-chassis-carnum) → Parsed correctly
- ✅ **Timestamp drift** → Uses meta_time over timestamp
- ✅ **Missing data** → Intelligent fallbacks
- ✅ **Format variations** → Standardizes column names

## 📈 **Expected Results**

With real GR Cup data:

### **Model Performance:**
- R² > 0.95 (better than sample data)
- RMSE < 0.3 seconds
- Real tire degradation patterns

### **Track Insights:**
- Actual tire wear rates per track
- Real sector performance differences
- Genuine pit strategy opportunities

### **Business Value:**
- Predictions based on real race conditions
- Strategy recommendations from actual data
- Competitive advantage using historical performance

## 🆘 **Troubleshooting**

### **Download Issues:**
```bash
# Check if files downloaded correctly
ls -la data/raw/
```
- Files should be >50MB each
- Total size ~700MB-1GB

### **Extraction Issues:**
```bash
# Check extracted files
python scripts/simple_pdf_extractor.py
```
- Shows what files were found
- Identifies data types

### **Processing Issues:**
```bash
# Check logs for errors
python scripts/process_real_data.py
```
- Look for error messages
- Check data quality reports

### **Model Training Issues:**
```bash
# Validate data before training
python -c "
import pandas as pd
df = pd.read_csv('data/cleaned/VIR_telemetry_clean.csv')
print(f'Shape: {df.shape}')
print(f'Columns: {list(df.columns)}')
"
```

## ✅ **Success Checklist**

- [ ] All 7 ZIP files downloaded to `data/raw/`
- [ ] Track maps (if available) in `Track Maps/`
- [ ] ZIP files extract without errors
- [ ] Telemetry data found and cleaned
- [ ] Sector data (6 sectors) identified
- [ ] Model trains with R² > 0.9
- [ ] Demo shows realistic predictions
- [ ] API server starts successfully

## 🏆 **Final Validation**

You'll know everything is working when:
1. **Data loads cleanly** - No extraction errors
2. **Model performs well** - R² > 0.9, reasonable predictions
3. **Predictions make sense** - Lap times in expected range
4. **Track differences show** - Different degradation per track
5. **Sector analysis works** - 6 sectors with realistic times

## 🚀 **Ready for Competition!**

Once everything is working:
- ✅ Real GR Cup data processed
- ✅ ML model trained on actual race data
- ✅ API serving live predictions
- ✅ Sector-level tire strategy
- ✅ Multi-track comparison
- ✅ Production-ready system

---

**You now have a complete race analytics system powered by real Toyota GR Cup data! 🏁**

*This is the competitive advantage - real data, real insights, real strategy.*