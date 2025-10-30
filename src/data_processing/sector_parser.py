"""
Parse track sector data from AnalysisEnduranceWithSections files

Author: GR Cup Analytics Team
Date: 2025-10-30

Handles 6-sector analysis per track:
- IM1a, IM1, IM2a, IM2, IM3a, FL

Dependencies:
- pandas >= 2.1.0
- matplotlib >= 3.7.2
- seaborn >= 0.12.2
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import glob

logger = logging.getLogger(__name__)

# Sector mapping for consistency
SECTOR_MAPPING = {
    'S1.a': 'IM1a',
    'S1.b': 'IM1', 
    'S2.a': 'IM2a',
    'S2.b': 'IM2',
    'S3.a': 'IM3a',
    'S3.b': 'FL'
}

SECTOR_COLUMNS = ['IM1a', 'IM1', 'IM2a', 'IM2', 'IM3a', 'FL']


class SectorAnalyzer:
    """
    Analyzes sector-level performance across 6 sectors per track
    """
    
    def __init__(self, track_name: str):
        self.track_name = track_name
        self.sector_data = None
    
    def load_sector_data(self, track_folder: str) -> pd.DataFrame:
        """
        Find and load *AnalysisEnduranceWithSections*.csv
        Columns expected: IM1a, IM1, IM2a, IM2, IM3a, FL
        """
        logger.info(f"Loading sector data from {track_folder}")
        
        try:
            # Find sector analysis file
            pattern = f"{track_folder}/*AnalysisEnduranceWithSections*.csv"
            files = glob.glob(pattern)
            
            if not files:
                logger.warning(f"No sector analysis file found in {track_folder}")
                return pd.DataFrame()
            
            # Load the first matching file
            sector_file = files[0]
            logger.info(f"Loading sector data from {sector_file}")
            
            df = pd.read_csv(sector_file, encoding='utf-8')
            logger.info(f"Loaded {len(df)} sector records")
            
            # Standardize column names
            df = self._standardize_columns(df)
            
            # Validate required columns
            missing_sectors = [col for col in SECTOR_COLUMNS if col not in df.columns]
            if missing_sectors:
                logger.warning(f"Missing sector columns: {missing_sectors}")
            
            self.sector_data = df
            return df
            
        except Exception as e:
            logger.error(f"Error loading sector data: {e}")
            return pd.DataFrame()
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize sector column names using SECTOR_MAPPING
        """
        df = df.copy()
        
        # Apply mapping
        for old_name, new_name in SECTOR_MAPPING.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        return df
    
    def calculate_sector_deltas(self, df: pd.DataFrame, car_number: str) -> Dict[str, float]:
        """
        For given car, compare each sector to session best
        Return: {'IM1a': +0.2, 'IM1': +0.1, 'IM2a': +0.5, ...}
        """
        if df.empty:
            return {}
        
        try:
            # Filter for specific car
            if 'car_number' in df.columns:
                car_data = df[df['car_number'] == car_number]
            elif 'Car' in df.columns:
                car_data = df[df['Car'] == car_number]
            else:
                logger.warning("No car number column found")
                return {}
            
            if car_data.empty:
                logger.warning(f"No data found for car {car_number}")
                return {}
            
            deltas = {}
            
            # Calculate deltas for each sector
            for sector in SECTOR_COLUMNS:
                if sector not in df.columns:
                    continue
                
                # Get session best (minimum time)
                session_best = df[sector].min()
                
                # Get car's best time in this sector
                car_best = car_data[sector].min()
                
                if pd.notna(session_best) and pd.notna(car_best):
                    delta = car_best - session_best
                    deltas[sector] = round(delta, 3)
            
            return deltas
            
        except Exception as e:
            logger.error(f"Error calculating sector deltas: {e}")
            return {}
    
    def identify_slow_sectors(self, deltas: Dict[str, float], threshold: float = 0.3) -> List[str]:
        """
        Return sectors where driver loses > threshold seconds
        Used for real-time alerts
        """
        slow_sectors = []
        
        for sector, delta in deltas.items():
            if delta > threshold:
                slow_sectors.append(sector)
        
        return slow_sectors
    
    def track_sector_degradation(self, df: pd.DataFrame, car_number: str) -> pd.DataFrame:
        """
        Show how sector times change lap-by-lap (tire wear)
        Return: DataFrame with lap_number, sector, time, delta_vs_first_lap
        """
        if df.empty:
            return pd.DataFrame()
        
        try:
            # Filter for specific car
            if 'car_number' in df.columns:
                car_data = df[df['car_number'] == car_number].copy()
            elif 'Car' in df.columns:
                car_data = df[df['Car'] == car_number].copy()
            else:
                return pd.DataFrame()
            
            if car_data.empty:
                return pd.DataFrame()
            
            # Sort by lap number
            if 'lap' in car_data.columns:
                car_data = car_data.sort_values('lap')
            elif 'Lap' in car_data.columns:
                car_data = car_data.sort_values('Lap')
                car_data['lap'] = car_data['Lap']
            
            degradation_data = []
            
            # Track degradation for each sector
            for sector in SECTOR_COLUMNS:
                if sector not in car_data.columns:
                    continue
                
                sector_times = car_data[['lap', sector]].dropna()
                
                if len(sector_times) < 2:
                    continue
                
                # Get first lap time as baseline
                first_lap_time = sector_times[sector].iloc[0]
                
                for _, row in sector_times.iterrows():
                    degradation_data.append({
                        'lap_number': row['lap'],
                        'sector': sector,
                        'time': row[sector],
                        'delta_vs_first_lap': row[sector] - first_lap_time
                    })
            
            return pd.DataFrame(degradation_data)
            
        except Exception as e:
            logger.error(f"Error tracking sector degradation: {e}")
            return pd.DataFrame()
    
    def plot_sector_heatmap(self, df: pd.DataFrame, save_path: Optional[str] = None) -> None:
        """
        Create visualization: plot sector times as heatmap
        """
        if df.empty:
            logger.warning("No data to plot")
            return
        
        try:
            # Prepare data for heatmap
            sector_data = df[SECTOR_COLUMNS].select_dtypes(include=[np.number])
            
            if sector_data.empty:
                logger.warning("No numeric sector data found")
                return
            
            # Create heatmap
            plt.figure(figsize=(12, 8))
            sns.heatmap(
                sector_data.T,
                cmap='RdYlGn_r',
                annot=True,
                fmt='.2f',
                cbar_kws={'label': 'Sector Time (seconds)'}
            )
            
            plt.title(f'{self.track_name} - Sector Performance Heatmap')
            plt.xlabel('Lap/Session')
            plt.ylabel('Sector')
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"Saved heatmap to {save_path}")
            
            plt.show()
            
        except Exception as e:
            logger.error(f"Error creating sector heatmap: {e}")
    
    def find_tire_critical_sectors(self, degradation_df: pd.DataFrame) -> List[str]:
        """
        Find "tire-critical" sectors (degrade fastest)
        Return list of sectors ordered by degradation rate
        """
        if degradation_df.empty:
            return []
        
        try:
            # Calculate degradation rate per sector
            degradation_rates = {}
            
            for sector in SECTOR_COLUMNS:
                sector_data = degradation_df[degradation_df['sector'] == sector]
                
                if len(sector_data) < 2:
                    continue
                
                # Calculate slope of degradation (time increase per lap)
                laps = sector_data['lap_number'].values
                deltas = sector_data['delta_vs_first_lap'].values
                
                if len(laps) > 1:
                    # Simple linear regression slope
                    slope = np.polyfit(laps, deltas, 1)[0]
                    degradation_rates[sector] = slope
            
            # Sort by degradation rate (highest first)
            sorted_sectors = sorted(
                degradation_rates.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            return [sector for sector, rate in sorted_sectors]
            
        except Exception as e:
            logger.error(f"Error finding tire-critical sectors: {e}")
            return []
    
    def get_sector_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate summary statistics for all sectors
        """
        if df.empty:
            return {}
        
        summary = {}
        
        for sector in SECTOR_COLUMNS:
            if sector not in df.columns:
                continue
            
            sector_times = df[sector].dropna()
            
            if len(sector_times) == 0:
                continue
            
            summary[sector] = {
                'best_time': float(sector_times.min()),
                'worst_time': float(sector_times.max()),
                'average_time': float(sector_times.mean()),
                'std_dev': float(sector_times.std()),
                'sample_count': len(sector_times)
            }
        
        return summary