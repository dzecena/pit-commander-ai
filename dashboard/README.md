# 🏁 GR Cup Dashboard System

## 📊 Two-Dashboard Architecture

### 1. Main Coaching Dashboard (`track_dashboard.html`)
**Overview and team management interface**

**Features:**
- ✅ **Multi-driver overview** - See all 5 drivers at once
- ✅ **Track selection** - Switch between all 7 tracks
- ✅ **Performance comparison** - Compare drivers side-by-side
- ✅ **Coaching insights** - Quick recommendations for each driver
- ✅ **Gear usage analysis** - Basic gear distribution charts
- ✅ **Real track images** - Actual track layouts from PDFs

**Best for:**
- Team managers and coaches
- Quick performance overview
- Driver selection and comparison
- Session management

### 2. Detailed Analysis Dashboard (`detailed_analysis.html`)
**Deep-dive analysis for specific driver-track combinations**

**Features:**
- 🔍 **Drill-down analysis** - Focus on one driver at one track
- 📈 **Telemetry deep dive** - Detailed performance metrics
- ⚙️ **Advanced gear analysis** - Comprehensive gear optimization
- 🎯 **Detailed coaching** - Specific improvement recommendations
- 📊 **Multiple analysis types** - Overview, telemetry, comparison, historical
- 📋 **Export capabilities** - Generate reports and data exports

**Best for:**
- Individual driver coaching
- Technical analysis
- Performance optimization
- Detailed reporting

## 🌐 Live URLs

**Main Dashboard:**  
https://gr-cup-data-dev-us-east-1-v2.s3.amazonaws.com/dashboard/track_dashboard.html

**Detailed Analysis:**  
https://gr-cup-data-dev-us-east-1-v2.s3.amazonaws.com/dashboard/detailed_analysis.html

## 🎯 Usage Workflow

### For Team Management:
1. **Start with Main Dashboard** - Get overview of all drivers
2. **Identify issues** - See which drivers need attention
3. **Switch tracks** - Compare performance across circuits
4. **Drill down** - Click "Detailed Analysis" for specific insights

### For Individual Coaching:
1. **Go to Detailed Analysis** - Focus on one driver
2. **Select driver and track** - Choose specific combination
3. **Choose analysis type** - Overview, telemetry, comparison, or historical
4. **Review insights** - Get specific coaching recommendations
5. **Export data** - Generate reports for further analysis

## 📋 Data Coverage

### Drivers (5 total):
- **001** - GR86-001-001 (Fast performer)
- **002** - GR86-002-002 (Session leader)
- **003** - GR86-003-003 (Struggling)
- **004** - GR86-004-004 (Needs attention)
- **005** - GR86-005-005 (Needs attention)

### Tracks (7 total):
- **BMP** - Barber Motorsports Park (Technical)
- **COTA** - Circuit of the Americas (Mixed)
- **VIR** - Virginia International Raceway (High-speed)
- **SEB** - Sebring International Raceway (Bumpy)
- **SON** - Sonoma Raceway (Elevation)
- **RA** - Road America (Long straights)
- **INDY** - Indianapolis Motor Speedway (Oval)

### Performance Metrics:
- **Lap times** - Best lap, sector times, consistency
- **Speed data** - Average speed, max speed, speed distribution
- **Gear analysis** - Usage patterns, shift frequency, optimization
- **Technical data** - G-forces, tire temps, fuel usage
- **Coaching insights** - Strengths, weaknesses, recommendations

## 🔧 Technical Implementation

### Architecture:
- **Frontend:** Pure HTML/CSS/JavaScript
- **Hosting:** AWS S3 with public access
- **Images:** Real track layouts from PDF extraction
- **Navigation:** Seamless switching between dashboards
- **Data:** Comprehensive simulated performance metrics

### Version Control:
- **Main dashboard:** Versioned with `version_manager.py`
- **Detailed dashboard:** Standalone with navigation links
- **Rollback capability:** Easy reversion to previous versions
- **Development tracking:** Complete version history

## 🚀 Future Enhancements

### Planned Features:
1. **Real-time data integration** - Connect to live telemetry
2. **Historical tracking** - Store performance over time
3. **Advanced charts** - Interactive telemetry visualization
4. **Mobile optimization** - Native mobile experience
5. **User authentication** - Driver-specific access

### Technical Improvements:
1. **Database backend** - Persistent data storage
2. **API integration** - Connect with timing systems
3. **Advanced analytics** - Machine learning insights
4. **Export formats** - PDF reports, CSV data
5. **Collaborative features** - Team sharing and notes

## 📖 Navigation Guide

### From Main Dashboard:
- **"🔍 Detailed Analysis"** button in header → Detailed Analysis Dashboard
- **Driver cards** → Click for quick analysis
- **Track selector** → Switch between tracks
- **Performance panels** → View metrics and coaching

### From Detailed Analysis:
- **"← Main Dashboard"** link → Return to overview
- **Driver selector** → Choose specific driver
- **Track selector** → Choose specific track
- **Analysis type** → Switch between analysis modes
- **"📊 Export Data"** → Generate reports

## ✅ Quality Assurance

### Tested Features:
- ✅ **Cross-dashboard navigation** - Seamless switching
- ✅ **Data consistency** - Same driver data across dashboards
- ✅ **Responsive design** - Works on all screen sizes
- ✅ **Track image loading** - Real track layouts display correctly
- ✅ **Performance metrics** - All calculations working properly

### Browser Compatibility:
- ✅ **Chrome** - Full functionality
- ✅ **Firefox** - Full functionality
- ✅ **Safari** - Full functionality
- ✅ **Edge** - Full functionality

## 🏆 Business Value

### For Racing Teams:
- **Improved driver development** - Specific coaching insights
- **Better performance tracking** - Comprehensive metrics
- **Enhanced decision making** - Data-driven strategies
- **Professional presentation** - Client-ready interface

### For Coaches:
- **Targeted coaching** - Specific improvement areas
- **Performance comparison** - Driver benchmarking
- **Technical insights** - Gear and setup optimization
- **Progress tracking** - Session-to-session improvement

### for Drivers:
- **Self-analysis** - Understand personal performance
- **Clear goals** - Specific areas to improve
- **Technical feedback** - Gear usage and technique
- **Motivation** - Visual progress tracking

---

*GR Cup Dashboard System v2.6*  
*Complete two-dashboard solution for professional racing analytics*