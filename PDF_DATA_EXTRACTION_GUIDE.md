# 📄 GR Cup PDF Data Extraction Guide

**Houston, we've got this! 🚀**

Your GR Cup data is in PDF format, which is actually very common in motorsports. Here's your complete guide to extract meaningful data for our ML model.

## 🎯 Quick Start

### Step 1: Place Your PDF Files
Put your PDF files in any of these directories:
```
📁 data/raw/           ← Recommended
📁 Track Maps/         ← For track layout PDFs  
📁 Data Files/         ← For race data PDFs
```

### Step 2: Run Analysis
```bash
python scripts/simple_pdf_extractor.py
```

This will analyze your PDFs and create a customized extraction plan.

## 📊 What We're Looking For

Our ML model needs these types of data from your PDFs:

### 🏎️ **Telemetry Data** (Most Important)
**Columns we need:**
- `Time` or `Timestamp` - When the data was recorded
- `Speed` - Vehicle speed (mph or km/h)
- `RPM` or `Engine_RPM` - Engine revolutions per minute
- `Throttle` or `Accelerator` - Throttle position (0-100%)
- `Brake` or `Brake_Pressure` - Brake pressure
- `Steering_Angle` - Steering wheel angle
- `Gear` - Current gear
- `Lap` or `Lap_Number` - Which lap this data is from
- `Car_Number` or `Vehicle_ID` - Which car

### ⏱️ **Lap Times**
**Columns we need:**
- `Lap` - Lap number
- `Lap_Time` - Total lap time
- `Sector_1`, `Sector_2`, `Sector_3` - Individual sector times
- `Car_Number` - Which car
- `Driver` - Driver name (optional)

### 🏁 **Race Results**
**Columns we need:**
- `Position` - Final position
- `Car_Number` - Car identifier
- `Driver` - Driver name
- `Total_Time` - Race total time
- `Best_Lap` - Best lap time

## 🔧 Extraction Methods

### Method 1: Automated (Recommended)
```bash
# Install PDF libraries
pip install PyPDF2 pdfplumber tabula-py

# Run automated extraction
python scripts/extract_pdf_data.py
```

### Method 2: Manual (If automated fails)

1. **Open PDF in Adobe Reader/Browser**
2. **Select table data** (Ctrl+A for all, or select specific tables)
3. **Copy to clipboard** (Ctrl+C)
4. **Paste into Excel/Google Sheets**
5. **Clean up the data:**
   - Remove empty rows/columns
   - Fix column headers
   - Ensure numeric data is properly formatted
6. **Save as CSV** with our naming convention

## 📁 File Naming Convention

Save your extracted CSV files using this format:

```
data/extracted/[track-folder]/[TRACK]_[type].csv
```

**Examples:**
```
data/extracted/virginia-international-raceway/VIR_telemetry.csv
data/extracted/sebring/SEB_lap_times.csv
data/extracted/circuit-of-the-americas/COTA_AnalysisEnduranceWithSections.csv
```

**Track Folders:**
- `barber-motorsports-park` → BMP
- `circuit-of-the-americas` → COTA  
- `indianapolis` → INDY
- `road-america` → RA
- `sebring` → SEB
- `sonoma` → SON
- `virginia-international-raceway` → VIR

## 🎯 Common PDF Formats in Racing

### Format 1: Data Acquisition Reports
```
Time    Speed   RPM    Throttle  Brake   Steering  Gear  Lap
0.00    45.2    3200   15.3      0.0     -2.1      2     1
0.10    47.8    3350   18.7      0.0     -1.8      2     1
0.20    52.1    3500   25.4      0.0     -1.2      2     1
```

### Format 2: Lap Time Sheets
```
Lap   Driver        Car   Lap_Time   Sector_1  Sector_2  Sector_3
1     John Smith    #42   1:45.234   32.123    38.456    34.655
2     John Smith    #42   1:44.987   31.987    38.234    34.766
3     John Smith    #42   1:45.456   32.234    38.567    34.655
```

### Format 3: Session Analysis
```
Car  Best_Lap   Avg_Speed  Total_Laps  Tire_Deg  Fuel_Used
#42  1:44.123   89.5 mph   25          2.3s      12.4 gal
#17  1:44.567   88.9 mph   24          2.8s      12.1 gal
```

## 🚀 Processing Pipeline

Once you have CSV files extracted:

### Step 1: Process Real Data
```bash
python scripts/process_real_data.py
```
This will:
- Clean the data (fix lap errors, timestamps)
- Standardize formats
- Generate quality reports

### Step 2: Retrain Model
```bash
python scripts/train_model.py
```
This will:
- Use your real data instead of sample data
- Achieve much better accuracy
- Generate real insights about tire degradation

### Step 3: Test System
```bash
python demo/race_demo.py
```
This will:
- Show predictions using your real data
- Demonstrate pit strategy with actual track characteristics
- Provide real insights for race strategy

## 🔍 Data Quality Checklist

Before processing, ensure your CSV files have:

✅ **Consistent column names** (Speed not Spd, RPM not Rev)  
✅ **Numeric data in numeric columns** (no text in speed column)  
✅ **Proper time formats** (1:45.234 or 105.234 seconds)  
✅ **No completely empty rows**  
✅ **Headers in first row**  
✅ **Car identifiers** (car numbers, driver names)  
✅ **Lap numbers** (1, 2, 3... not missing)  

## 🛠️ Troubleshooting

### Problem: "No tables found in PDF"
**Solutions:**
- PDF might be image-based (scanned) - try OCR tools
- Tables might be complex - try manual copy/paste
- Use different extraction method (tabula vs pdfplumber)

### Problem: "Garbled text extraction"
**Solutions:**
- PDF might be password protected
- Try opening in different PDF viewer
- Manual extraction might be needed

### Problem: "Data looks wrong after extraction"
**Solutions:**
- Check for merged cells in original PDF
- Verify column alignment
- Clean up manually in Excel before saving CSV

## 📈 Expected Results

With real GR Cup data, you should see:

🎯 **Model Performance:**
- R² > 0.95 (even better than sample data)
- RMSE < 0.3 seconds (more accurate predictions)
- Real tire degradation patterns per track

🏁 **Track Insights:**
- Actual tire degradation rates (not simulated)
- Real sector performance differences
- Genuine pit strategy opportunities

🚀 **Business Value:**
- Predictions based on real race conditions
- Strategy recommendations from actual data
- Competitive advantage using historical performance

## 💡 Pro Tips

1. **Start with one track** - Get VIR working first, then expand
2. **Focus on telemetry** - This gives the most ML value
3. **Check data quality** - 1000 good records > 10000 bad records
4. **Validate results** - Compare predictions to known lap times
5. **Iterate quickly** - Extract → Process → Train → Test → Repeat

## 🆘 Need Help?

If you run into issues:

1. **Run the analyzer first:**
   ```bash
   python scripts/simple_pdf_extractor.py
   ```

2. **Check the logs** - They'll tell you exactly what's wrong

3. **Start simple** - Even one track with basic telemetry will work

4. **Manual extraction is OK** - Sometimes faster than fighting with PDFs

## 🏆 Success Criteria

You'll know it's working when:
- ✅ CSV files load without errors
- ✅ Model trains with R² > 0.9
- ✅ Predictions make sense (lap times in reasonable range)
- ✅ Demo shows real track characteristics

---

**Remember: Real data = Real insights = Real competitive advantage! 🏁**

*The goal isn't perfect extraction - it's getting enough good data to make meaningful predictions.*