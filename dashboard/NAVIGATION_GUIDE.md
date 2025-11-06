# 🧭 Dashboard Navigation Guide

## 🚀 Multiple Ways to Jump to Detailed Analysis

### 1. **Header Navigation** (Top Right)
- **🔍 Detailed Analysis** - Opens detailed dashboard (blank)
- **📊 Current Selection** - Opens with current driver and track pre-selected

### 2. **Driver Card Buttons** (Left Panel)
- **🔍 Deep Dive** button on each driver card
- Automatically selects that driver and current track
- Click stops card selection, goes straight to detailed analysis

### 3. **Performance Panel Button** (Center Panel)
- **🔍 View Detailed Analysis** button at bottom of performance analysis
- Pre-selects the currently analyzed driver and track

### 4. **Keyboard Shortcut**
- **Ctrl+D** - Quick access to detailed analysis with current selections

## 🎯 Smart URL Parameters

When jumping from main to detailed dashboard, the URL includes:
- `?driver=001&track=BMP` - Pre-selects Driver #001 at Barber Motorsports Park
- Detailed dashboard automatically loads the analysis
- No need to manually select driver and track again

## 🔄 Return Navigation

From detailed dashboard back to main:
- **← Main Dashboard** link in header
- Browser back button
- Direct URL navigation

## 💡 Navigation Tips

### **For Quick Analysis:**
1. Select driver on main dashboard
2. Click **🔍 Deep Dive** on their card
3. Detailed analysis opens immediately

### **For Comparison:**
1. Use main dashboard to compare drivers
2. Click **📊 Current Selection** to analyze winner
3. Use browser tabs to compare multiple drivers

### **For Team Review:**
1. Start with main dashboard overview
2. Identify problem drivers (red/orange status)
3. Use **🔍 Deep Dive** for each problem driver
4. Generate detailed coaching plans

## 🎨 Visual Indicators

- **Green status** = Fast driver (minimal detailed analysis needed)
- **Orange status** = Needs attention (good candidate for detailed analysis)
- **Red status** = Struggling (priority for detailed analysis)

## ⌨️ Keyboard Shortcuts

- **Ctrl+D** - Open detailed analysis with current selections
- **Escape** - Close any open modals or return to main view
- **Tab** - Navigate through interactive elements

## 🔗 URL Structure

### Main Dashboard:
`https://gr-cup-data-dev-us-east-1-v2.s3.amazonaws.com/dashboard/track_dashboard.html`

### Detailed Analysis:
`https://gr-cup-data-dev-us-east-1-v2.s3.amazonaws.com/dashboard/detailed_analysis.html`

### With Parameters:
`https://gr-cup-data-dev-us-east-1-v2.s3.amazonaws.com/dashboard/detailed_analysis.html?driver=001&track=BMP`

## 🎯 Best Practices

### **For Coaches:**
- Use main dashboard for team overview
- Use detailed analysis for individual coaching sessions
- Bookmark specific driver-track combinations for regular review

### **For Drivers:**
- Bookmark your detailed analysis URL with your driver ID
- Use main dashboard to see how you compare to teammates
- Focus on detailed analysis for personal improvement

### **For Team Managers:**
- Start each session with main dashboard overview
- Use detailed analysis to investigate performance issues
- Export detailed data for post-session reviews

---

*Navigation system designed for efficient workflow between overview and detailed analysis*