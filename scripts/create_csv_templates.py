"""
Create CSV templates showing the exact format needed for GR Cup data

Author: GR Cup Analytics Team
Date: 2025-10-30

This creates example CSV files showing the exact column names and formats
our system expects from your PDF data extraction.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_telemetry_template():
    """
    Create telemetry data template
    """
    # Sample telemetry data showing the format we need
    telemetry_data = {
        'vehicle_id': ['GR86-001-042', 'GR86-001-042', 'GR86-001-042', 'GR86-001-042', 'GR86-001-042'],
        'timestamp': [1635724800000, 1635724800100, 1635724800200, 1635724800300, 1635724800400],  # milliseconds
        'meta_time': [1635724800000, 1635724800100, 1635724800200, 1635724800300, 1635724800400],  # milliseconds
        'lap': [1, 1, 1, 1, 1],
        'Speed': [45.2, 47.8, 52.1, 58.3, 62.7],  # mph or km/h
        'pbrake_f': [0.0, 0.0, 0.0, 15.3, 25.8],  # brake pressure
        'ath': [15.3, 18.7, 25.4, 35.2, 42.1],  # throttle position %
        'Steering_Angle': [-2.1, -1.8, -1.2, 0.5, 2.3],  # degrees
        'accx_can': [0.2, 0.3, 0.5, -0.8, -1.2],  # lateral g-force
        'accy_can': [0.1, 0.2, 0.4, 0.6, 0.3],  # longitudinal g-force
        'nmotor': [3200, 3350, 3500, 3800, 4100],  # RPM
        'Gear': [2, 2, 2, 3, 3],  # gear number
        'track_name': ['Virginia International Raceway'] * 5,
        'track_id': ['VIR'] * 5
    }
    
    df = pd.DataFrame(telemetry_data)
    return df

def create_lap_times_template():
    """
    Create lap times template
    """
    lap_times_data = {
        'car_number': ['042', '042', '042', '017', '017', '017'],
        'lap_number': [1, 2, 3, 1, 2, 3],
        'lap_time': [105.234, 104.987, 105.456, 106.123, 105.789, 106.234],  # seconds
        'track_name': ['Virginia International Raceway'] * 6,
        'driver': ['John Smith', 'John Smith', 'John Smith', 'Jane Doe', 'Jane Doe', 'Jane Doe']
    }
    
    df = pd.DataFrame(lap_times_data)
    return df

def create_sector_analysis_template():
    """
    Create sector analysis template (6 sectors per track)
    
    GR Cup Sector Mapping:
    S1.a → IM1a (First half of section 1)
    S1.b → IM1  (Second half of section 1) 
    S2.a → IM2a (First half of section 2)
    S2.b → IM2  (Second half of section 2)
    S3.a → IM3a (First half of section 3)
    S3.b → FL   (Final sector to finish line)
    """
    sector_data = {
        'Car': ['042', '042', '042', '017', '017', '017'],
        'car_number': ['042', '042', '042', '017', '017', '017'],
        'lap': [1, 2, 3, 1, 2, 3],
        'Lap': [1, 2, 3, 1, 2, 3],
        # GR Cup 6-sector format (matches "analysis with sections" files)
        'IM1a': [18.234, 18.123, 18.345, 18.456, 18.234, 18.567],  # S1.a - First half of section 1
        'IM1': [19.567, 19.456, 19.678, 19.789, 19.567, 19.890],   # S1.b - Second half of section 1
        'IM2a': [17.890, 17.789, 17.901, 18.012, 17.890, 18.123],  # S2.a - First half of section 2
        'IM2': [20.123, 20.012, 20.234, 20.345, 20.123, 20.456],   # S2.b - Second half of section 2
        'IM3a': [16.456, 16.345, 16.567, 16.678, 16.456, 16.789],  # S3.a - First half of section 3
        'FL': [12.964, 12.853, 13.075, 13.186, 12.964, 13.297]     # S3.b - Final sector to finish line
    }
    
    df = pd.DataFrame(sector_data)
    return df

def create_results_template():
    """
    Create race results template
    """
    results_data = {
        'Position': [1, 2, 3, 4, 5],
        'Car': ['042', '017', '023', '088', '156'],
        'car_number': ['042', '017', '023', '088', '156'],
        'Driver': ['John Smith', 'Jane Doe', 'Bob Johnson', 'Alice Brown', 'Charlie Wilson'],
        'Total_Time': ['32:45.234', '32:47.567', '32:52.890', '33:01.123', '33:15.456'],
        'Best_Lap': [104.987, 105.789, 106.234, 107.123, 108.456],
        'Total_Laps': [25, 25, 25, 25, 24],
        'Points': [25, 22, 20, 18, 16]
    }
    
    df = pd.DataFrame(results_data)
    return df

def create_all_templates():
    """
    Create all template files
    """
    logger.info("🏁 Creating CSV Templates for GR Cup Data")
    logger.info("=" * 50)
    
    # Create templates directory
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)
    
    # Create each template
    templates = {
        'telemetry': create_telemetry_template(),
        'lap_times': create_lap_times_template(),
        'sector_analysis': create_sector_analysis_template(),
        'results': create_results_template()
    }
    
    for template_name, df in templates.items():
        # Save template
        template_path = templates_dir / f"{template_name}_template.csv"
        df.to_csv(template_path, index=False)
        
        logger.info(f"✅ Created {template_name} template: {template_path}")
        logger.info(f"   Columns: {list(df.columns)}")
        logger.info(f"   Shape: {df.shape}")
        
        # Show sample data
        logger.info("   Sample data:")
        for i, row in df.head(2).iterrows():
            sample_row = {k: v for k, v in row.items() if k in list(df.columns)[:5]}
            logger.info(f"     Row {i+1}: {sample_row}")
        logger.info("")
    
    # Create track-specific examples
    logger.info("📁 Creating track-specific examples...")
    
    tracks = {
        'VIR': 'virginia-international-raceway',
        'SEB': 'sebring', 
        'COTA': 'circuit-of-the-americas'
    }
    
    for track_abbrev, track_folder in tracks.items():
        track_dir = Path(f"templates/{track_folder}")
        track_dir.mkdir(exist_ok=True)
        
        # Create track-specific files
        for template_name, df in templates.items():
            # Modify data for this track
            track_df = df.copy()
            
            if 'track_id' in track_df.columns:
                track_df['track_id'] = track_abbrev
            
            if 'track_name' in track_df.columns:
                track_names = {
                    'VIR': 'Virginia International Raceway',
                    'SEB': 'Sebring International Raceway',
                    'COTA': 'Circuit of the Americas'
                }
                track_df['track_name'] = track_names.get(track_abbrev, track_abbrev)
            
            # Save track-specific template
            filename = f"{track_abbrev}_{template_name}.csv"
            track_path = track_dir / filename
            track_df.to_csv(track_path, index=False)
        
        logger.info(f"✅ Created {track_abbrev} examples in {track_dir}")
    
    # Create README
    readme_content = """# CSV Templates for GR Cup Data

These templates show the exact format needed for your extracted PDF data.

## Files:

### Core Templates:
- `telemetry_template.csv` - Main telemetry data format
- `lap_times_template.csv` - Lap timing data format  
- `sector_analysis_template.csv` - 6-sector timing format
- `results_template.csv` - Race results format

### Track Examples:
- `virginia-international-raceway/` - VIR examples
- `sebring/` - Sebring examples
- `circuit-of-the-americas/` - COTA examples

## Usage:

1. Extract data from your PDFs
2. Format it to match these templates
3. Save with proper naming: `[TRACK]_[type].csv`
4. Place in `data/extracted/[track-folder]/`

## Key Points:

- **Column names must match exactly**
- **Numeric data should be numbers, not text**
- **Times can be in seconds (105.234) or MM:SS.sss format**
- **Vehicle IDs should follow GR86-chassis-carnum format**
- **Timestamps in milliseconds since epoch**

## Next Steps:

After creating your CSV files:
```bash
python scripts/process_real_data.py
python scripts/train_model.py
python demo/race_demo.py
```
"""
    
    readme_path = templates_dir / "README.md"
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    logger.info(f"📝 Created README: {readme_path}")
    
    logger.info(f"\n✅ All templates created in {templates_dir}/")
    logger.info("\n🎯 Next steps:")
    logger.info("1. Look at the template files to see exact format needed")
    logger.info("2. Extract your PDF data to match these formats")
    logger.info("3. Save as CSV files in data/extracted/[track]/")
    logger.info("4. Run: python scripts/process_real_data.py")

if __name__ == "__main__":
    create_all_templates()