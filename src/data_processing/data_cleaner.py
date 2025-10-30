"""
Core data cleaning logic for GR Cup telemetry
Handles: lap errors, vehicle IDs, timestamps, missing data

Author: GR Cup Analytics Team
Date: 2025-10-30

Known Issues Handled:
- Lap count errors (32768)
- Vehicle ID parsing (GR86-chassis-carnum)
- Timestamp drift (meta_time vs timestamp)
- Missing GPS fallback

Dependencies:
- pandas >= 2.1.0
- numpy >= 1.24.3
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Tuple, Dict, Any
import json
from tqdm import tqdm

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GRCupDataCleaner:
    """
    Cleans raw telemetry data handling known quality issues
    """
    
    def __init__(self, track_name: str):
        self.track_name = track_name
        self.lap_error_value = 32768
        self.cleaning_stats = {
            'total_records': 0,
            'lap_errors_fixed': 0,
            'timestamp_corrections': 0,
            'vehicle_id_parsed': 0,
            'derived_features_added': 0
        }
    
    def parse_vehicle_id(self, vehicle_id: str) -> Tuple[str, str]:
        """
        Parse GR86-chassis-carnum format
        Returns: (chassis, car_number)
        Handle: car_number='000' means unassigned
        """
        try:
            if pd.isna(vehicle_id) or not isinstance(vehicle_id, str):
                return 'unknown', 'unknown'
            
            parts = vehicle_id.split('-')
            if len(parts) != 3 or parts[0] != 'GR86':
                logger.warning(f"Unexpected vehicle ID format: {vehicle_id}")
                return 'unknown', 'unknown'
            
            chassis = parts[1]
            car_number = parts[2]
            
            # Handle unassigned cars (000)
            if car_number == '000':
                car_number = chassis  # Fallback to chassis
            
            self.cleaning_stats['vehicle_id_parsed'] += 1
            return chassis, car_number
            
        except Exception as e:
            logger.error(f"Error parsing vehicle ID {vehicle_id}: {e}")
            return 'unknown', 'unknown'
    
    def fix_lap_errors(self, df: pd.DataFrame, threshold_seconds: int = 120) -> pd.DataFrame:
        """
        Fix lap count = 32768 errors
        Use timestamp gaps to reconstruct lap numbers
        Threshold: 120 seconds = typical lap time
        """
        logger.info(f"Fixing lap errors in {len(df)} records...")
        
        if 'lap' not in df.columns:
            logger.warning("No 'lap' column found, skipping lap error fixes")
            return df
        
        df = df.copy()
        initial_errors = (df['lap'] == self.lap_error_value).sum()
        
        if initial_errors == 0:
            logger.info("No lap errors found")
            return df
        
        # Sort by vehicle and timestamp for proper reconstruction
        df = df.sort_values(['vehicle_id', 'timestamp'])
        
        # Group by vehicle to fix laps independently
        for vehicle_id in df['vehicle_id'].unique():
            if pd.isna(vehicle_id):
                continue
                
            mask = df['vehicle_id'] == vehicle_id
            vehicle_data = df[mask].copy()
            
            # Convert timestamp to datetime for gap detection
            vehicle_data['timestamp_dt'] = pd.to_datetime(vehicle_data['timestamp'], unit='ms', errors='coerce')
            
            # Calculate time gaps
            vehicle_data['time_gap'] = vehicle_data['timestamp_dt'].diff().dt.total_seconds()
            
            # Reconstruct lap numbers
            current_lap = 1
            new_laps = []
            
            for idx, row in vehicle_data.iterrows():
                if row['lap'] == self.lap_error_value:
                    # Use time gap to detect new lap
                    if not pd.isna(row['time_gap']) and row['time_gap'] > threshold_seconds:
                        current_lap += 1
                    new_laps.append(current_lap)
                else:
                    # Use existing lap number if valid
                    if row['lap'] > 0:
                        current_lap = int(row['lap'])
                    new_laps.append(current_lap)
            
            # Update the main dataframe
            df.loc[mask, 'lap'] = new_laps
        
        final_errors = (df['lap'] == self.lap_error_value).sum()
        errors_fixed = initial_errors - final_errors
        self.cleaning_stats['lap_errors_fixed'] = errors_fixed
        
        logger.info(f"Fixed {errors_fixed} lap errors")
        return df
    
    def align_timestamps(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Use meta_time (accurate) over timestamp (ECU, may drift)
        Convert to datetime for easier manipulation
        """
        logger.info("Aligning timestamps...")
        
        df = df.copy()
        corrections = 0
        
        # Prefer meta_time over timestamp
        if 'meta_time' in df.columns:
            # Use meta_time where available
            mask = pd.notna(df['meta_time'])
            df.loc[mask, 'timestamp'] = df.loc[mask, 'meta_time']
            corrections = mask.sum()
        
        # Convert to datetime
        df['timestamp_dt'] = pd.to_datetime(df['timestamp'], unit='ms', errors='coerce')
        
        # Remove records with invalid timestamps
        valid_timestamps = pd.notna(df['timestamp_dt'])
        df = df[valid_timestamps]
        
        self.cleaning_stats['timestamp_corrections'] = corrections
        logger.info(f"Aligned {corrections} timestamps")
        
        return df
    
    def calculate_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add computed columns:
        - braking_intensity = pbrake_f * abs(accx_can.clip(upper=0))
        - cornering_force = abs(accy_can * Steering_Angle)
        - throttle_efficiency = Speed / (ath + 1)
        - rpm_per_gear = nmotor / (Gear + 1)
        """
        logger.info("Calculating derived features...")
        
        df = df.copy()
        features_added = 0
        
        # Braking intensity
        if 'pbrake_f' in df.columns and 'accx_can' in df.columns:
            df['braking_intensity'] = df['pbrake_f'] * np.abs(df['accx_can'].clip(upper=0))
            features_added += 1
        
        # Cornering force
        if 'accy_can' in df.columns and 'Steering_Angle' in df.columns:
            df['cornering_force'] = np.abs(df['accy_can'] * df['Steering_Angle'])
            features_added += 1
        
        # Throttle efficiency
        if 'Speed' in df.columns and 'ath' in df.columns:
            df['throttle_efficiency'] = df['Speed'] / (df['ath'] + 1)
            features_added += 1
        
        # RPM per gear
        if 'nmotor' in df.columns and 'Gear' in df.columns:
            df['rpm_per_gear'] = df['nmotor'] / (df['Gear'] + 1)
            features_added += 1
        
        self.cleaning_stats['derived_features_added'] = features_added
        logger.info(f"Added {features_added} derived features")
        
        return df
    
    def clean_telemetry(self, telemetry_path: str) -> pd.DataFrame:
        """
        Main cleaning pipeline - call all methods in order
        Returns: Clean DataFrame ready for analysis
        """
        logger.info(f"Starting telemetry cleaning for {self.track_name}")
        
        try:
            # Load CSV
            logger.info(f"Loading data from {telemetry_path}")
            df = pd.read_csv(telemetry_path, encoding='utf-8')
            self.cleaning_stats['total_records'] = len(df)
            
            logger.info(f"Loaded {len(df)} records with columns: {list(df.columns)}")
            
            # Parse vehicle IDs
            if 'vehicle_id' in df.columns:
                logger.info("Parsing vehicle IDs...")
                parsed_ids = df['vehicle_id'].apply(self.parse_vehicle_id)
                df['chassis'] = [x[0] for x in parsed_ids]
                df['car_number'] = [x[1] for x in parsed_ids]
            
            # Fix lap errors
            df = self.fix_lap_errors(df)
            
            # Align timestamps
            df = self.align_timestamps(df)
            
            # Calculate derived features
            df = self.calculate_derived_features(df)
            
            # Filter out invalid records
            initial_count = len(df)
            df = df.dropna(subset=['timestamp_dt'])
            final_count = len(df)
            
            logger.info(f"Removed {initial_count - final_count} invalid records")
            
            # Save cleaned data
            output_path = f"data/cleaned/{self.track_name}_telemetry_clean.csv"
            Path("data/cleaned").mkdir(parents=True, exist_ok=True)
            df.to_csv(output_path, index=False)
            logger.info(f"Saved cleaned data to {output_path}")
            
            # Save metadata (convert numpy types to native Python types)
            metadata_path = f"data/cleaned/{self.track_name}_cleaning_stats.json"
            stats_to_save = {}
            for key, value in self.cleaning_stats.items():
                if hasattr(value, 'item'):  # numpy scalar
                    stats_to_save[key] = value.item()
                else:
                    stats_to_save[key] = value
            
            with open(metadata_path, 'w') as f:
                json.dump(stats_to_save, f, indent=2)
            
            logger.info(f"Cleaning complete for {self.track_name}")
            return df
            
        except Exception as e:
            logger.error(f"Error cleaning telemetry data: {e}")
            raise