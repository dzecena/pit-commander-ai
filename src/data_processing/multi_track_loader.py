"""
Load and combine data from all 7 tracks

Author: GR Cup Analytics Team
Date: 2025-10-30

Tracks:
- BMP: Barber Motorsports Park
- COTA: Circuit of the Americas  
- INDY: Indianapolis
- RA: Road America
- SEB: Sebring
- SON: Sonoma
- VIR: Virginia International Raceway
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import glob
from .data_cleaner import GRCupDataCleaner
from .sector_parser import SectorAnalyzer

logger = logging.getLogger(__name__)

TRACKS = {
    'BMP': 'barber-motorsports-park',
    'COTA': 'circuit-of-the-americas', 
    'INDY': 'indianapolis',
    'RA': 'road-america',
    'SEB': 'sebring',
    'SON': 'sonoma',
    'VIR': 'virginia-international-raceway'
}


class MultiTrackLoader:
    """
    Loads data from all tracks, standardizes format
    """
    
    def __init__(self, base_path: str = "data/extracted"):
        self.base_path = Path(base_path)
        self.tracks_data = {}
        self.track_characteristics = {}
    
    def load_all_tracks(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Load telemetry, lap times, sectors, results from all 7 tracks
        Return: {track_abbrev: {telemetry: df, laps: df, sectors: df, results: df}}
        """
        logger.info("Loading data from all tracks...")
        
        for track_abbrev, track_folder in TRACKS.items():
            logger.info(f"Processing {track_abbrev} ({track_folder})")
            
            track_path = self.base_path / track_folder
            
            if not track_path.exists():
                logger.warning(f"Track folder not found: {track_path}")
                continue
            
            track_data = self._load_single_track(track_abbrev, track_path)
            self.tracks_data[track_abbrev] = track_data
        
        logger.info(f"Loaded data for {len(self.tracks_data)} tracks")
        return self.tracks_data
    
    def _load_single_track(self, track_abbrev: str, track_path: Path) -> Dict[str, pd.DataFrame]:
        """
        Load all data types for a single track
        """
        track_data = {
            'telemetry': pd.DataFrame(),
            'laps': pd.DataFrame(), 
            'sectors': pd.DataFrame(),
            'results': pd.DataFrame()
        }
        
        try:
            # Load telemetry data
            telemetry_files = list(track_path.glob("*telemetry*.csv"))
            if not telemetry_files:
                telemetry_files = list(track_path.glob("*.csv"))
            
            if telemetry_files:
                logger.info(f"Loading telemetry from {telemetry_files[0]}")
                
                # Use data cleaner
                cleaner = GRCupDataCleaner(track_abbrev)
                track_data['telemetry'] = cleaner.clean_telemetry(str(telemetry_files[0]))
            
            # Load lap times
            lap_files = list(track_path.glob("*lap*.csv"))
            if lap_files:
                logger.info(f"Loading lap data from {lap_files[0]}")
                track_data['laps'] = pd.read_csv(lap_files[0], encoding='utf-8')
            
            # Load sector data
            sector_analyzer = SectorAnalyzer(track_abbrev)
            track_data['sectors'] = sector_analyzer.load_sector_data(str(track_path))
            
            # Load results
            result_files = list(track_path.glob("*result*.csv"))
            if result_files:
                logger.info(f"Loading results from {result_files[0]}")
                track_data['results'] = pd.read_csv(result_files[0], encoding='utf-8')
            
        except Exception as e:
            logger.error(f"Error loading data for {track_abbrev}: {e}")
        
        return track_data
    
    def classify_tracks(self) -> pd.DataFrame:
        """
        Classify tracks as HIGH_SPEED or TECHNICAL based on:
        - avg_speed > 150 km/h = HIGH_SPEED
        - avg_steering_angle > 20 deg = TECHNICAL
        Return: DataFrame with track characteristics
        """
        logger.info("Classifying tracks...")
        
        classifications = []
        
        for track_abbrev, data in self.tracks_data.items():
            telemetry = data.get('telemetry', pd.DataFrame())
            
            if telemetry.empty:
                continue
            
            try:
                # Calculate average speed
                avg_speed = 0
                if 'Speed' in telemetry.columns:
                    avg_speed = telemetry['Speed'].mean()
                elif 'speed' in telemetry.columns:
                    avg_speed = telemetry['speed'].mean()
                
                # Calculate average steering angle
                avg_steering = 0
                if 'Steering_Angle' in telemetry.columns:
                    avg_steering = abs(telemetry['Steering_Angle']).mean()
                elif 'steering_angle' in telemetry.columns:
                    avg_steering = abs(telemetry['steering_angle']).mean()
                
                # Classify track
                if avg_speed > 150:
                    track_type = 'HIGH_SPEED'
                elif avg_steering > 20:
                    track_type = 'TECHNICAL'
                else:
                    track_type = 'BALANCED'
                
                classifications.append({
                    'track': track_abbrev,
                    'track_name': TRACKS[track_abbrev],
                    'avg_speed_kmh': round(avg_speed, 1),
                    'avg_steering_angle': round(avg_steering, 1),
                    'track_type': track_type
                })
                
                # Store for later use
                self.track_characteristics[track_abbrev] = {
                    'avg_speed': avg_speed,
                    'avg_steering': avg_steering,
                    'type': track_type
                }
                
            except Exception as e:
                logger.error(f"Error classifying {track_abbrev}: {e}")
        
        return pd.DataFrame(classifications)
    
    def compare_tire_degradation(self) -> pd.DataFrame:
        """
        Calculate tire degradation rate per track
        early_pace (laps 2-5) vs late_pace (laps 15+)
        Return: DataFrame with track, degradation_rate, pct_increase
        """
        logger.info("Comparing tire degradation across tracks...")
        
        degradation_data = []
        
        for track_abbrev, data in self.tracks_data.items():
            telemetry = data.get('telemetry', pd.DataFrame())
            
            if telemetry.empty or 'lap' not in telemetry.columns:
                continue
            
            try:
                # Calculate lap times from telemetry
                lap_times = self._calculate_lap_times(telemetry)
                
                if lap_times.empty:
                    continue
                
                # Early pace (laps 2-5)
                early_laps = lap_times[
                    (lap_times['lap'] >= 2) & (lap_times['lap'] <= 5)
                ]['lap_time']
                
                # Late pace (laps 15+)
                late_laps = lap_times[lap_times['lap'] >= 15]['lap_time']
                
                if len(early_laps) == 0 or len(late_laps) == 0:
                    continue
                
                early_pace = early_laps.mean()
                late_pace = late_laps.mean()
                
                degradation_rate = late_pace - early_pace
                pct_increase = (degradation_rate / early_pace) * 100
                
                degradation_data.append({
                    'track': track_abbrev,
                    'track_name': TRACKS[track_abbrev],
                    'early_pace': round(early_pace, 3),
                    'late_pace': round(late_pace, 3),
                    'degradation_rate': round(degradation_rate, 3),
                    'pct_increase': round(pct_increase, 2)
                })
                
            except Exception as e:
                logger.error(f"Error calculating degradation for {track_abbrev}: {e}")
        
        return pd.DataFrame(degradation_data)
    
    def _calculate_lap_times(self, telemetry: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate lap times from telemetry data
        """
        if 'timestamp_dt' not in telemetry.columns or 'lap' not in telemetry.columns:
            return pd.DataFrame()
        
        lap_times = []
        
        # Group by vehicle and lap
        for vehicle_id in telemetry['vehicle_id'].unique():
            if pd.isna(vehicle_id):
                continue
            
            vehicle_data = telemetry[telemetry['vehicle_id'] == vehicle_id]
            
            for lap_num in vehicle_data['lap'].unique():
                if pd.isna(lap_num) or lap_num <= 0:
                    continue
                
                lap_data = vehicle_data[vehicle_data['lap'] == lap_num]
                
                if len(lap_data) < 2:
                    continue
                
                # Calculate lap time as time difference
                start_time = lap_data['timestamp_dt'].min()
                end_time = lap_data['timestamp_dt'].max()
                lap_time = (end_time - start_time).total_seconds()
                
                if 30 < lap_time < 300:  # Reasonable lap time range
                    lap_times.append({
                        'vehicle_id': vehicle_id,
                        'lap': lap_num,
                        'lap_time': lap_time
                    })
        
        return pd.DataFrame(lap_times)
    
    def get_track_summary(self) -> pd.DataFrame:
        """
        Summary table:
        - Track name
        - Total laps
        - Avg lap time
        - Tire degradation rate
        - Track type (HIGH_SPEED/TECHNICAL)
        """
        logger.info("Generating track summary...")
        
        # Get classifications and degradation data
        classifications = self.classify_tracks()
        degradation = self.compare_tire_degradation()
        
        summary_data = []
        
        for track_abbrev, data in self.tracks_data.items():
            telemetry = data.get('telemetry', pd.DataFrame())
            
            try:
                # Basic stats
                total_laps = 0
                avg_lap_time = 0
                
                if not telemetry.empty and 'lap' in telemetry.columns:
                    total_laps = telemetry['lap'].max()
                    
                    lap_times = self._calculate_lap_times(telemetry)
                    if not lap_times.empty:
                        avg_lap_time = lap_times['lap_time'].mean()
                
                # Get track type
                track_type = 'UNKNOWN'
                if track_abbrev in self.track_characteristics:
                    track_type = self.track_characteristics[track_abbrev]['type']
                
                # Get degradation rate
                degradation_rate = 0
                deg_row = degradation[degradation['track'] == track_abbrev]
                if not deg_row.empty:
                    degradation_rate = deg_row['degradation_rate'].iloc[0]
                
                summary_data.append({
                    'track': track_abbrev,
                    'track_name': TRACKS[track_abbrev],
                    'total_laps': int(total_laps) if total_laps > 0 else 0,
                    'avg_lap_time': round(avg_lap_time, 2) if avg_lap_time > 0 else 0,
                    'degradation_rate': degradation_rate,
                    'track_type': track_type
                })
                
            except Exception as e:
                logger.error(f"Error generating summary for {track_abbrev}: {e}")
        
        return pd.DataFrame(summary_data)
    
    def save_combined_dataset(self, output_path: str = "data/cleaned/all_tracks_combined.parquet"):
        """
        Save combined dataset in efficient parquet format
        """
        logger.info("Saving combined dataset...")
        
        try:
            combined_telemetry = []
            
            for track_abbrev, data in self.tracks_data.items():
                telemetry = data.get('telemetry', pd.DataFrame())
                
                if not telemetry.empty:
                    telemetry = telemetry.copy()
                    telemetry['track'] = track_abbrev
                    telemetry['track_name'] = TRACKS[track_abbrev]
                    combined_telemetry.append(telemetry)
            
            if combined_telemetry:
                combined_df = pd.concat(combined_telemetry, ignore_index=True)
                
                # Ensure output directory exists
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                
                # Save as parquet for efficiency
                combined_df.to_parquet(output_path, index=False)
                logger.info(f"Saved combined dataset to {output_path}")
                logger.info(f"Combined dataset shape: {combined_df.shape}")
                
                return combined_df
            else:
                logger.warning("No telemetry data to combine")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error saving combined dataset: {e}")
            return pd.DataFrame()