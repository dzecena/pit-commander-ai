# 🏁 GR Cup Sector Analysis Guide

**Perfect! You've provided the exact sector mapping used in GR Cup.**

Our system already has this mapping built-in and ready to process your "analysis with sections" files.

## 🎯 Sector Mapping System

Based on your clarification, here's the exact mapping:

### Track Layout
- **Red lines** = Section boundaries (3 main sections)
- **White lines** = Sub-section boundaries (divides each section in half)
- **Start/Finish line** = Section boundary

### Sector Correspondence
```
Track Map    →    Analysis File    →    Our System
S1.a         →    IM1a            →    IM1a
S1.b         →    IM1             →    IM1
S2.a         →    IM2a            →    IM2a
S2.b         →    IM2             →    IM2
S3.a         →    IM3a            →    IM3a
S3.b         →    FL              →    FL
```

## 📊 What This Means for Data Extraction

### From Your PDFs, Look For:
1. **Track maps** showing red and white lines
2. **"Analysis with sections" files** containing timing data
3. **Tables with columns:** IM1a, IM1, IM2a, IM2, IM3a, FL

### Expected Data Format:
```csv
Car,Lap,IM1a,IM1,IM2a,IM2,IM3a,FL
042,1,18.234,19.567,17.890,20.123,16.456,12.964
042,2,18.123,19.456,17.789,20.012,16.345,12.853
```

## 🔧 Our System Handles This Automatically

Our sector parser already:
- ✅ Maps S1.a → IM1a, S1.b → IM1, etc.
- ✅ Processes 6-sector timing data
- ✅ Calculates sector deltas vs session best
- ✅ Identifies tire-critical sectors
- ✅ Tracks sector degradation over stint

## 🎯 Extraction Priority

### High Priority Files:
1. **"Analysis with sections" files** - These contain the IM1a, IM1, IM2a, IM2, IM3a, FL data
2. **Track maps** - Help understand sector characteristics
3. **Telemetry data** - For overall lap time predictions

### What to Look For in PDFs:
- Tables with 6 timing columns (IM1a through FL)
- Car numbers and lap numbers
- Session timing data
- Sector split times

## 🚀 Processing Workflow

### Step 1: Extract Sector Data
From your PDFs, create CSV files like:
```
data/extracted/virginia-international-raceway/VIR_AnalysisEnduranceWithSections.csv
data/extracted/sebring/SEB_AnalysisEnduranceWithSections.csv
```

### Step 2: Our System Processes It
```bash
python scripts/process_real_data.py
```

This will:
- Load your sector timing files
- Apply the S1.a → IM1a mapping automatically
- Calculate sector performance metrics
- Identify which sectors are most tire-critical

### Step 3: Advanced Analytics
```bash
python scripts/train_model.py
```

This will:
- Use sector data to improve tire degradation predictions
- Identify track-specific tire wear patterns
- Calculate which sectors degrade fastest with tire age

## 📈 Expected Insights

With real GR Cup sector data, you'll discover:

### Track Characteristics:
- **Which sectors are tire-critical** (degrade fastest)
- **Optimal racing lines** (consistent fast sectors)
- **Braking zones** (IM1a, IM2a typically have heavy braking)
- **High-speed sections** (FL often shows tire wear)

### Tire Strategy:
- **Sector-specific degradation rates**
- **When each sector starts losing time**
- **Which sectors to prioritize when tires are old**
- **Optimal pit timing based on sector performance**

### Driver Coaching:
- **Sectors where drivers lose most time**
- **Consistency metrics per sector**
- **Tire management techniques per sector**

## 🔍 Data Quality Validation

Our system will automatically check:
- ✅ All 6 sectors present (IM1a through FL)
- ✅ Sector times add up to reasonable lap times
- ✅ No impossible sector times (negative, too fast)
- ✅ Consistent car numbering
- ✅ Sequential lap numbering

## 💡 Pro Tips for Extraction

### From Track Maps:
- Note which sectors have heavy braking (usually IM1a, IM2a)
- Identify high-speed sections (often IM3a, FL)
- Understand elevation changes (affect tire wear)

### From Analysis Files:
- Look for multiple cars and multiple laps
- Ensure all 6 sectors have data
- Check for session best times
- Verify lap totals make sense

### Common Issues:
- **Missing sectors** - Some files might only have 3 sectors instead of 6
- **Wrong column names** - Might use S1a instead of IM1a
- **Time formats** - Might be MM:SS.sss instead of seconds

## 🎯 Success Metrics

You'll know the sector analysis is working when:
- ✅ All 6 sectors load without errors
- ✅ Sector times sum to reasonable lap times
- ✅ System identifies tire-critical sectors
- ✅ Degradation patterns make sense (slower sectors with old tires)
- ✅ Track comparison shows realistic differences

## 🚀 Next Steps

1. **Find your "analysis with sections" files** in the PDFs
2. **Extract the 6-sector timing data** (IM1a, IM1, IM2a, IM2, IM3a, FL)
3. **Save as CSV** with proper naming
4. **Run our processing pipeline**
5. **Get real insights** about tire strategy per sector

---

**This sector mapping is gold! 🏆 It's exactly what we need for precision tire strategy analysis.**

*With 6-sector data, we can predict not just when to pit, but which sectors will be most affected by tire degradation.*