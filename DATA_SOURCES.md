# 🏁 GR Cup Data Sources

**Official Toyota Racing Development (TRD) Hackathon Data**

## 📊 Data Source Information

**Main Data Portal:** https://trddev.com/hackathon-2025/

**Data Files Order Page:** https://trddev.com/hackathon-2025/Data files Order

## 📁 File Organization

### **Track Maps (PDF Format)**
**Location:** `Track Maps/`

Place your track map PDF files here:
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

**What these contain:**
- Track layouts with sector boundaries (red lines)
- Sub-sector divisions (white lines)
- Start/finish line locations
- Sector mapping: S1.a, S1.b, S2.a, S2.b, S3.a, S3.b

### **Data Files (ZIP Format)**
**Location:** `data/raw/`

Download and place ZIP files here:
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

## 🔗 Direct Download Links

### Track Data ZIP Files:
1. **Barber Motorsports Park**
   - URL: https://trddev.com/hackathon-2025/barber-motorsports-park.zip
   - Save as: `data/raw/barber-motorsports-park.zip`

2. **Circuit of the Americas**
   - URL: https://trddev.com/hackathon-2025/circuit-of-the-americas.zip
   - Save as: `data/raw/circuit-of-the-americas.zip`

3. **Indianapolis Motor Speedway**
   - URL: https://trddev.com/hackathon-2025/indianapolis.zip
   - Save as: `data/raw/indianapolis.zip`

4. **Road America**
   - URL: https://trddev.com/hackathon-2025/road-america.zip
   - Save as: `data/raw/road-america.zip`

5. **Sebring International Raceway**
   - URL: https://trddev.com/hackathon-2025/sebring.zip
   - Save as: `data/raw/sebring.zip`

6. **Sonoma Raceway**
   - URL: https://trddev.com/hackathon-2025/sonoma.zip
   - Save as: `data/raw/sonoma.zip`

7. **Virginia International Raceway**
   - URL: https://trddev.com/hackathon-2025/virginia-international-raceway.zip
   - Save as: `data/raw/virginia-international-raceway.zip`

## 📋 Download Instructions

### Method 1: Manual Download
1. Visit each URL above
2. Download the ZIP file
3. Save to the specified location in `data/raw/`

### Method 2: Command Line (Windows)
```powershell
# Create directories
New-Item -ItemType Directory -Force -Path "data/raw"
New-Item -ItemType Directory -Force -Path "Track Maps"

# Download all ZIP files
$urls = @(
    "https://trddev.com/hackathon-2025/barber-motorsports-park.zip",
    "https://trddev.com/hackathon-2025/circuit-of-the-americas.zip",
    "https://trddev.com/hackathon-2025/indianapolis.zip",
    "https://trddev.com/hackathon-2025/road-america.zip",
    "https://trddev.com/hackathon-2025/sebring.zip",
    "https://trddev.com/hackathon-2025/sonoma.zip",
    "https://trddev.com/hackathon-2025/virginia-international-raceway.zip"
)

foreach ($url in $urls) {
    $filename = Split-Path $url -Leaf
    Invoke-WebRequest -Uri $url -OutFile "data/raw/$filename"
    Write-Host "Downloaded: $filename"
}
```

### Method 3: Python Script
```python
import requests
from pathlib import Path

# Create directories
Path("data/raw").mkdir(parents=True, exist_ok=True)
Path("Track Maps").mkdir(parents=True, exist_ok=True)

# Download URLs
urls = [
    "https://trddev.com/hackathon-2025/barber-motorsports-park.zip",
    "https://trddev.com/hackathon-2025/circuit-of-the-americas.zip",
    "https://trddev.com/hackathon-2025/indianapolis.zip",
    "https://trddev.com/hackathon-2025/road-america.zip",
    "https://trddev.com/hackathon-2025/sebring.zip",
    "https://trddev.com/hackathon-2025/sonoma.zip",
    "https://trddev.com/hackathon-2025/virginia-international-raceway.zip"
]

for url in urls:
    filename = url.split('/')[-1]
    print(f"Downloading {filename}...")
    
    response = requests.get(url)
    with open(f"data/raw/{filename}", 'wb') as f:
        f.write(response.content)
    
    print(f"✅ Downloaded: {filename}")
```

## 📊 Expected Data Contents

Each ZIP file should contain:
- **Telemetry data** (speed, RPM, throttle, brake, steering)
- **Lap timing data** (lap times, sector splits)
- **"Analysis with sections" files** (6-sector timing: IM1a, IM1, IM2a, IM2, IM3a, FL)
- **Race results** (positions, drivers, times)
- **Session data** (practice, qualifying, race)

## 🔄 Processing Workflow

After downloading files:

### Step 1: Extract and Analyze
```bash
# Extract ZIP files and analyze structure
python scripts/process_real_data.py
```

### Step 2: Extract PDF Data
```bash
# Extract data from PDF files (if any)
python scripts/extract_pdf_data.py
```

### Step 3: Train Model
```bash
# Train ML model with real data
python scripts/train_model.py
```

### Step 4: Test System
```bash
# Test predictions with real data
python demo/race_demo.py
```

## 📝 File Size Information

**Note:** These files are large (>100MB each) and are excluded from Git.

**Total Download Size:** ~700MB - 1GB
**Extracted Size:** ~2-3GB

## 🔒 Data Usage Terms

This data is provided by Toyota Racing Development for the 2025 Hackathon.
- Use only for hackathon purposes
- Do not redistribute
- Respect Toyota's intellectual property

## 🆘 Troubleshooting

### Download Issues:
- **Slow downloads:** Files are large, be patient
- **Failed downloads:** Try again, servers may be busy
- **Access denied:** Ensure you're registered for the hackathon

### File Issues:
- **Corrupted ZIP:** Re-download the file
- **Can't extract:** Try different extraction tool
- **Missing files:** Check if download completed fully

## ✅ Verification Checklist

After downloading, verify you have:
- [ ] All 7 ZIP files in `data/raw/`
- [ ] Track map PDFs in `Track Maps/` (if provided)
- [ ] Files are not corrupted (can open/extract)
- [ ] Total size is reasonable (~700MB-1GB)

---

**Ready to process real GR Cup data! 🏁**

*This is the official Toyota Racing Development data that will give you genuine racing insights.*