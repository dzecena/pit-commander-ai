"""
Generate sample telemetry data for testing the GR Cup Analytics system

Author: GR Cup Analytics Team
Date: 2025-10-30

Creates realistic sample data for all 7 tracks to enable testing
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from datetime import datetime, timedelta
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from utils.config import TRACKS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_track_telemetry(track_id: str, track_config: dict, num_cars: int = 5, num_laps: int = 25) -> pd.DataFrame:
    """
    Generate realistic telemetry data for a track
    """
    logger.info(f"Generating telemetry for {track_id}")
    
    base_lap_time = track_config['typical_lap_time']
    records = []
    
    # Generate data for each car
    for car_num in range(1, num_cars + 1):
        car_id = f"GR86-00{car_num}-{car_num:03d}"
        
        # Car-specific characteristics
        driver_skill = np.random.uniform(0.95, 1.05)  # ±5% pace variation
        car_setup = np.random.uniform(0.98, 1.02)     # ±2% setup variation
        
        base_time = datetime.now()
        
        for lap in range(1, num_laps + 1):
            # Tire degradation effect
            tire_age = lap  # Simplified - no pit stops
            degradation_factor = 1 + (tire_age - 1) * 0.02  # 2% per lap
            
            # Lap time calculation
            lap_time = base_lap_time * driver_skill * car_setup * degradation_factor
            lap_time += np.random.normal(0, 0.5)  # Random variation
            
            # Generate telemetry points for this lap (100 points per lap)
            for point in range(100):
                timestamp = base_time + timedelta(seconds=lap_time * point / 100)
                
                # Speed profile (varies through lap)
                speed_factor = 0.7 + 0.3 * np.sin(2 * np.pi * point / 100)
                speed = 120 + 60 * speed_factor + np.random.normal(0, 5)
                
                # Brake pressure (higher in braking zones)
                brake_zones = [20, 40, 60, 80]  # Approximate braking points
                brake_pressure = 0
                for zone in brake_zones:
                    if abs(point - zone) < 5:
                        brake_pressure = max(brake_pressure, 80 + np.random.normal(0, 10))
                
                # Throttle position
                throttle = max(0, min(100, 70 + np.random.normal(0, 15)))
                if brake_pressure > 50:
                    throttle = max(0, throttle - 50)
                
                # Steering angle
                steering = np.sin(4 * np.pi * point / 100) * 45 + np.random.normal(0, 5)
                
                # G-forces
                accx = np.random.normal(0, 0.5)
                accy = np.random.normal(0, 0.8)
                
                # Engine data
                rpm = 4000 + speed * 20 + np.random.normal(0, 200)
                gear = min(6, max(1, int(speed / 30)))
                
                record = {
                    'vehicle_id': car_id,
                    'timestamp': int(timestamp.timestamp() * 1000),
                    'meta_time': int(timestamp.timestamp() * 1000),
                    'lap': lap,
                    'Speed': max(0, speed),
                    'pbrake_f': max(0, brake_pressure),
                    'ath': max(0, throttle),
                    'Steering_Angle': steering,
                    'accx_can': accx,
                    'accy_can': accy,
                    'nmotor': max(1000, rpm),
                    'Gear': gear,
                    'track_name': track_config['name'],
                    'track_id': track_id
                }
                
                records.append(record)
        
        # Add some lap errors for testing
        if car_num == 1:  # Add errors to first car
            error_laps = np.random.choice(range(5, 15), 3, replace=False)
            for i, record in enumerate(records):
                if record['vehicle_id'] == car_id and record['lap'] in error_laps:
                    records[i]['lap'] = 32768  # ECU error value
    
    return pd.DataFrame(records)

def generate_sector_data(track_id: str, track_config: dict, num_cars: int = 5, num_laps: int = 25) -> pd.DataFrame:
    """
    Generate sector timing data
    """
    logger.info(f"Generating sector data for {track_id}")
    
    base_lap_time = track_config['typical_lap_time']
    sector_times = []
    
    # Typical sector distribution (6 sectors)
    sector_percentages = [0.15, 0.18, 0.16, 0.19, 0.17, 0.15]
    
    for car_num in range(1, num_cars + 1):
        car_id = f"00{car_num}"
        
        for lap in range(1, num_laps + 1):
            # Tire degradation
            degradation = 1 + (lap - 1) * 0.02
            
            lap_time = base_lap_time * degradation * np.random.uniform(0.98, 1.02)
            
            # Calculate sector times
            sector_data = {
                'Car': car_id,
                'car_number': car_id,
                'lap': lap,
                'Lap': lap
            }
            
            for i, (sector, percentage) in enumerate(zip(['IM1a', 'IM1', 'IM2a', 'IM2', 'IM3a', 'FL'], sector_percentages)):
                sector_time = lap_time * percentage + np.random.normal(0, 0.1)
                sector_data[sector] = max(0.1, sector_time)
            
            sector_times.append(sector_data)
    
    return pd.DataFrame(sector_times)

def main():
    """
    Generate sample data for all tracks
    """
    logger.info("Starting sample data generation...")
    
    # Ensure directories exist
    Path("data/extracted").mkdir(parents=True, exist_ok=True)
    Path("data/cleaned").mkdir(parents=True, exist_ok=True)
    
    for track_id, track_config in TRACKS.items():
        logger.info(f"Processing {track_id} - {track_config['name']}")
        
        # Create track directory
        track_dir = Path("data/extracted") / track_config['folder']
        track_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate telemetry data
        telemetry_df = generate_track_telemetry(track_id, track_config)
        telemetry_path = track_dir / f"{track_id}_telemetry.csv"
        telemetry_df.to_csv(telemetry_path, index=False)
        logger.info(f"Saved {len(telemetry_df)} telemetry records to {telemetry_path}")
        
        # Generate sector data
        sector_df = generate_sector_data(track_id, track_config)
        sector_path = track_dir / f"{track_id}_AnalysisEnduranceWithSections.csv"
        sector_df.to_csv(sector_path, index=False)
        logger.info(f"Saved {len(sector_df)} sector records to {sector_path}")
        
        # Generate lap times (simplified)
        lap_times = []
        for car_num in range(1, 6):
            for lap in range(1, 26):
                degradation = 1 + (lap - 1) * 0.02
                lap_time = track_config['typical_lap_time'] * degradation * np.random.uniform(0.98, 1.02)
                
                lap_times.append({
                    'car_number': f"00{car_num}",
                    'lap_number': lap,
                    'lap_time': lap_time,
                    'track_name': track_config['name']
                })
        
        lap_df = pd.DataFrame(lap_times)
        lap_path = track_dir / f"{track_id}_lap_times.csv"
        lap_df.to_csv(lap_path, index=False)
        logger.info(f"Saved {len(lap_df)} lap time records to {lap_path}")
    
    logger.info("Sample data generation complete!")

if __name__ == "__main__":
    main()