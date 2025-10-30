"""
Train the tire degradation model using sample data

Author: GR Cup Analytics Team
Date: 2025-10-30
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from data_processing.multi_track_loader import MultiTrackLoader
from models.tire_degradation import TireDegradationModel
from utils.config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

def prepare_training_data():
    """
    Load and prepare training data from all tracks
    """
    logger.info("Loading multi-track data...")
    
    # Load data from all tracks
    loader = MultiTrackLoader()
    tracks_data = loader.load_all_tracks()
    
    if not tracks_data:
        logger.error("No track data loaded")
        return pd.DataFrame()
    
    # Combine telemetry data
    combined_data = []
    
    for track_id, data in tracks_data.items():
        telemetry = data.get('telemetry', pd.DataFrame())
        
        if telemetry.empty:
            logger.warning(f"No telemetry data for {track_id}")
            continue
        
        # Add track information
        telemetry = telemetry.copy()
        telemetry['track_id'] = track_id
        
        # Calculate lap times from telemetry
        lap_times = calculate_lap_times_from_telemetry(telemetry)
        
        if not lap_times.empty:
            combined_data.append(lap_times)
    
    if not combined_data:
        logger.error("No valid training data found")
        return pd.DataFrame()
    
    # Combine all data
    training_df = pd.concat(combined_data, ignore_index=True)
    logger.info(f"Prepared {len(training_df)} training samples")
    
    return training_df

def calculate_lap_times_from_telemetry(telemetry_df):
    """
    Calculate lap times from telemetry data
    """
    if 'timestamp_dt' not in telemetry_df.columns:
        telemetry_df['timestamp_dt'] = pd.to_datetime(telemetry_df['timestamp'], unit='ms')
    
    lap_times = []
    
    # Group by vehicle and lap
    for vehicle_id in telemetry_df['vehicle_id'].unique():
        if pd.isna(vehicle_id):
            continue
        
        vehicle_data = telemetry_df[telemetry_df['vehicle_id'] == vehicle_id]
        
        for lap_num in sorted(vehicle_data['lap'].unique()):
            if pd.isna(lap_num) or lap_num <= 0:
                continue
            
            lap_data = vehicle_data[vehicle_data['lap'] == lap_num]
            
            if len(lap_data) < 10:  # Need sufficient data points
                continue
            
            # Calculate lap time
            start_time = lap_data['timestamp_dt'].min()
            end_time = lap_data['timestamp_dt'].max()
            lap_time = (end_time - start_time).total_seconds()
            
            # Validate lap time (reasonable range)
            if not (30 < lap_time < 300):
                continue
            
            # Get average telemetry values for this lap
            avg_speed = lap_data['Speed'].mean() if 'Speed' in lap_data.columns else 150
            
            lap_times.append({
                'vehicle_id': vehicle_id,
                'car_number': vehicle_id.split('-')[-1] if '-' in str(vehicle_id) else str(vehicle_id),
                'lap_number': int(lap_num),
                'lap_time': lap_time,
                'track_name': lap_data['track_name'].iloc[0] if 'track_name' in lap_data.columns else 'Unknown',
                'track_id': lap_data['track_id'].iloc[0] if 'track_id' in lap_data.columns else 'UNK',
                'Speed': avg_speed
            })
    
    return pd.DataFrame(lap_times)

def main():
    """
    Main training pipeline
    """
    logger.info("Starting model training pipeline...")
    
    try:
        # Prepare training data
        training_df = prepare_training_data()
        
        if training_df.empty:
            logger.error("No training data available")
            return
        
        logger.info(f"Training data shape: {training_df.shape}")
        logger.info(f"Columns: {list(training_df.columns)}")
        
        # Initialize model
        model = TireDegradationModel()
        
        # Prepare features
        features_df = model.prepare_features(training_df)
        
        if features_df.empty:
            logger.error("Feature preparation failed")
            return
        
        logger.info(f"Features prepared: {features_df.shape}")
        
        # Split features and target
        feature_columns = [col for col in model.feature_names if col in features_df.columns]
        
        if len(feature_columns) < len(model.feature_names):
            logger.warning(f"Missing features: {set(model.feature_names) - set(feature_columns)}")
        
        X = features_df[feature_columns]
        y = features_df['lap_time']
        
        logger.info(f"Training with {len(X)} samples and {len(feature_columns)} features")
        
        # Train model
        metrics = model.train(X, y)
        
        if metrics:
            logger.info("Training completed successfully!")
            logger.info(f"Test RMSE: {metrics.get('test_rmse', 'N/A'):.3f}")
            logger.info(f"Test R²: {metrics.get('test_r2', 'N/A'):.3f}")
            
            # Display feature importance
            importance_df = model.get_feature_importance()
            if not importance_df.empty:
                logger.info("Feature Importance:")
                for _, row in importance_df.head().iterrows():
                    logger.info(f"  {row['feature']}: {row['importance']:.3f}")
        else:
            logger.error("Training failed")
    
    except Exception as e:
        logger.error(f"Training pipeline failed: {e}")
        raise

if __name__ == "__main__":
    main()