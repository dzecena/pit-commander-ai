#!/usr/bin/env python3
"""
Dashboard Automation System for GR Cup Analytics

This script automates:
1. Data intake from CSV files
2. Data processing and analysis
3. Dashboard data generation
4. Dashboard deployment to S3

Author: GR Cup Analytics Team
Date: 2025-11-07
"""

import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import subprocess
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DashboardAutomation:
    def __init__(self):
        self.data_dir = Path("data/cleaned")
        self.dashboard_dir = Path("dashboard")
        self.output_file = self.dashboard_dir / "dashboard_data.js"
        self.s3_bucket = "gr-cup-data-dev-us-east-1-v2"
        
    def load_telemetry_data(self, track_id):
        """Load cleaned telemetry data for a specific track"""
        file_path = self.data_dir / f"{track_id}_telemetry_clean.csv"
        
        if not file_path.exists():
            logger.warning(f"No data file found for {track_id}")
            return None
            
        try:
            df = pd.read_csv(file_path)
            logger.info(f"Loaded {len(df)} records for {track_id}")
            return df
        except Exception as e:
            logger.error(f"Error loading {track_id} data: {e}")
            return None
    
    def analyze_driver_performance(self, df, driver_id, track_id):
        """Analyze performance metrics for a specific driver"""
        driver_data = df[df['car_number'] == driver_id].copy()
        
        if len(driver_data) == 0:
            return None
        
        # Calculate performance metrics
        analysis = {
            'bestLap': self.calculate_best_lap(driver_data),
            'avgSpeed': float(driver_data['Speed'].mean()),
            'consistency': self.calculate_consistency(driver_data),
            'position': self.calculate_position(df, driver_id),
            'sectors': self.calculate_sector_times(driver_data),
            'gearUsage': self.calculate_gear_usage(driver_data),
            'avgGear': float(driver_data['Gear'].mean()),
            'maxGear': int(driver_data['Gear'].max()),
            'gearShifts': self.calculate_gear_shifts(driver_data)
        }
        
        return analysis
    
    def calculate_best_lap(self, driver_data):
        """Calculate best lap time from telemetry data"""
        # Group by lap and calculate lap times
        lap_times = driver_data.groupby('lap').agg({
            'timestamp': ['min', 'max']
        })
        
        if len(lap_times) == 0:
            return "0:00.000"
        
        # Calculate lap duration in seconds
        lap_times['duration'] = (lap_times[('timestamp', 'max')] - 
                                lap_times[('timestamp', 'min')]) / 1000
        
        best_lap_seconds = lap_times['duration'].min()
        
        # Format as MM:SS.mmm
        minutes = int(best_lap_seconds // 60)
        seconds = best_lap_seconds % 60
        
        return f"{minutes}:{seconds:06.3f}"
    
    def calculate_consistency(self, driver_data):
        """Calculate consistency score based on lap time variance"""
        lap_times = driver_data.groupby('lap')['timestamp'].apply(
            lambda x: (x.max() - x.min()) / 1000
        )
        
        if len(lap_times) < 2:
            return 100
        
        # Calculate coefficient of variation
        cv = (lap_times.std() / lap_times.mean()) * 100
        
        # Convert to consistency score (lower CV = higher consistency)
        consistency = max(0, min(100, 100 - cv))
        
        return round(consistency, 1)
    
    def calculate_position(self, df, driver_id):
        """Calculate driver position based on best lap times"""
        best_laps = df.groupby('car_number').apply(
            lambda x: x.groupby('lap')['timestamp'].apply(
                lambda y: (y.max() - y.min()) / 1000
            ).min()
        ).sort_values()
        
        position = list(best_laps.index).index(driver_id) + 1
        return position
    
    def calculate_sector_times(self, driver_data):
        """Calculate sector times (simplified - assumes 6 sectors)"""
        # This is a simplified version - in production, use actual sector markers
        total_laps = driver_data['lap'].nunique()
        
        if total_laps == 0:
            return [0.0] * 6
        
        # Divide lap into 6 equal sectors for demonstration
        # In production, use actual sector timing points
        avg_lap_time = driver_data.groupby('lap')['timestamp'].apply(
            lambda x: (x.max() - x.min()) / 1000
        ).mean()
        
        # Generate realistic sector times that sum to lap time
        sector_times = []
        remaining = avg_lap_time
        
        for i in range(5):
            sector_time = remaining / (6 - i) * (0.9 + 0.2 * (i % 2))
            sector_times.append(round(sector_time, 3))
            remaining -= sector_time
        
        sector_times.append(round(remaining, 3))
        
        return sector_times
    
    def calculate_gear_usage(self, driver_data):
        """Calculate percentage of time in each gear"""
        gear_counts = driver_data['Gear'].value_counts()
        total_samples = len(driver_data)
        
        gear_usage = {}
        for gear in range(1, 7):
            percentage = (gear_counts.get(gear, 0) / total_samples) * 100
            gear_usage[f'gear{gear}'] = round(percentage, 1)
        
        return gear_usage
    
    def calculate_gear_shifts(self, driver_data):
        """Calculate number of gear shifts per lap"""
        # Count gear changes
        gear_changes = (driver_data['Gear'].diff() != 0).sum()
        total_laps = driver_data['lap'].nunique()
        
        if total_laps == 0:
            return 0
        
        shifts_per_lap = gear_changes / total_laps
        return round(shifts_per_lap)
    
    def generate_dashboard_data(self):
        """Generate complete dashboard data from all telemetry files"""
        logger.info("Starting dashboard data generation...")
        
        tracks = ['BMP', 'COTA', 'VIR', 'SEB', 'SON', 'RA', 'INDY']
        drivers = ['001', '002', '003', '004', '005']
        
        dashboard_data = {}
        
        for driver_id in drivers:
            driver_tracks = {}
            
            for track_id in tracks:
                df = self.load_telemetry_data(track_id)
                
                if df is not None:
                    analysis = self.analyze_driver_performance(df, driver_id, track_id)
                    
                    if analysis:
                        driver_tracks[track_id] = analysis
                        logger.info(f"Processed {driver_id} at {track_id}")
            
            if driver_tracks:
                dashboard_data[driver_id] = {
                    'name': f'Driver #{driver_id}',
                    'chassis': f'GR86-{driver_id}-{driver_id}',
                    'status': self.determine_status(driver_tracks),
                    'tracks': driver_tracks
                }
        
        return dashboard_data
    
    def determine_status(self, driver_tracks):
        """Determine driver status based on performance"""
        if not driver_tracks:
            return 'unknown'
        
        # Calculate average position across all tracks
        positions = [track['position'] for track in driver_tracks.values()]
        avg_position = sum(positions) / len(positions)
        
        if avg_position <= 2:
            return 'fast'
        elif avg_position <= 4:
            return 'needs-attention'
        else:
            return 'struggling'
    
    def save_dashboard_data(self, data):
        """Save dashboard data as JavaScript file"""
        js_content = f"""// Auto-generated dashboard data
// Generated: {datetime.now().isoformat()}
// DO NOT EDIT MANUALLY - Use dashboard_automation.py to regenerate

const DASHBOARD_DATA = {json.dumps(data, indent=2)};

// Export for use in dashboards
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = DASHBOARD_DATA;
}}
"""
        
        output_path = self.output_file
        with open(output_path, 'w') as f:
            f.write(js_content)
        
        logger.info(f"Dashboard data saved to {output_path}")
        return output_path
    
    def deploy_to_s3(self):
        """Deploy updated dashboards to S3"""
        logger.info("Deploying dashboards to S3...")
        
        files_to_deploy = [
            'dashboard/track_dashboard.html',
            'dashboard/detailed_analysis.html',
            'dashboard/dashboard_data.js',
            'dashboard/track_images_embedded.js'
        ]
        
        for file_path in files_to_deploy:
            if Path(file_path).exists():
                s3_key = file_path.replace('\\', '/')
                cmd = f'aws s3 cp {file_path} s3://{self.s3_bucket}/{s3_key}'
                
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    if result.returncode == 0:
                        logger.info(f"✅ Deployed {file_path}")
                    else:
                        logger.error(f"❌ Failed to deploy {file_path}: {result.stderr}")
                except Exception as e:
                    logger.error(f"Error deploying {file_path}: {e}")
    
    def run_full_automation(self):
        """Run complete automation pipeline"""
        logger.info("=" * 60)
        logger.info("GR Cup Dashboard Automation - Full Pipeline")
        logger.info("=" * 60)
        
        try:
            # Step 1: Generate dashboard data from telemetry
            logger.info("\n📊 Step 1: Generating dashboard data...")
            dashboard_data = self.generate_dashboard_data()
            
            # Step 2: Save dashboard data
            logger.info("\n💾 Step 2: Saving dashboard data...")
            self.save_dashboard_data(dashboard_data)
            
            # Step 3: Deploy to S3
            logger.info("\n🚀 Step 3: Deploying to S3...")
            self.deploy_to_s3()
            
            logger.info("\n" + "=" * 60)
            logger.info("✅ Dashboard automation completed successfully!")
            logger.info("=" * 60)
            logger.info(f"\n🌐 Dashboard URL: https://{self.s3_bucket}.s3.amazonaws.com/dashboard/track_dashboard.html")
            
            return True
            
        except Exception as e:
            logger.error(f"\n❌ Automation failed: {e}")
            return False

def main():
    """Main entry point"""
    automation = DashboardAutomation()
    success = automation.run_full_automation()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
