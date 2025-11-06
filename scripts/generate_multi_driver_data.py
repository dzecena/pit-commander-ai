"""
Generate Multi-Driver Telemetry Data

Creates realistic telemetry data for multiple drivers based on existing patterns
to provide diverse dashboard analytics and meaningful comparisons.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiDriverDataGenerator:
    """
    Generate realistic multi-driver telemetry data
    """
    
    def __init__(self):
        self.driver_profiles = {
            'GR86-001-001': {'skill': 'expert', 'style': 'aggressive', 'consistency': 0.95},
            'GR86-002-015': {'skill': 'advanced', 'style': 'smooth', 'consistency': 0.88},
            'GR86-003-027': {'skill': 'intermediate', 'style': 'conservative', 'consistency': 0.82},
            'GR86-004-042': {'skill': 'advanced', 'style': 'aggressive', 'consistency': 0.90},
            'GR86-005-058': {'skill': 'beginner', 'style': 'cautious', 'consistency': 0.75},
            'GR86-006-073': {'skill': 'expert', 'style': 'technical', 'consistency': 0.93},
            'GR86-007-089': {'skill': 'intermediate', 'style': 'balanced', 'consistency': 0.85}
        }
        
        self.skill_modifiers = {
            'expert': {'speed': 1.05, 'braking': 1.10, 'cornering': 1.15, 'throttle': 1.08},
            'advanced': {'speed': 1.02, 'braking': 1.05, 'cornering': 1.08, 'throttle': 1.04},
            'intermediate': {'speed': 0.98, 'braking': 0.95, 'cornering': 0.92, 'throttle': 0.96},
            'beginner': {'speed': 0.92, 'braking': 0.85, 'cornering': 0.80, 'throttle': 0.88}
        }
        
        self.style_modifiers = {
            'aggressive': {'speed': 1.03, 'braking': 1.15, 'cornering': 1.10, 'throttle': 1.05},
            'smooth': {'speed': 1.01, 'braking': 0.95, 'cornering': 1.05, 'throttle': 1.02},
            'conservative': {'speed': 0.96, 'braking': 0.90, 'cornering': 0.88, 'throttle': 0.94},
            'technical': {'speed': 1.02, 'braking': 1.08, 'cornering': 1.12, 'throttle': 1.01},
            'balanced': {'speed': 1.00, 'braking': 1.00, 'cornering': 1.00, 'throttle': 1.00},
            'cautious': {'speed': 0.94, 'braking': 0.88, 'cornering': 0.85, 'throttle': 0.92}
        }
    
    def generate_driver_variation(self, base_data, driver_id):
        """
        Apply driver-specific variations to base telemetry data
        """
        profile = self.driver_profiles[driver_id]
        skill_mod = self.skill_modifiers[profile['skill']]
        style_mod = self.style_modifiers[profile['style']]
        consistency = profile['consistency']
        
        # Create a copy of the data
        driver_data = base_data.copy()
        
        # Apply skill and style modifiers with some randomness
        np.random.seed(hash(driver_id) % 2**32)  # Consistent randomness per driver
        
        # Speed variations
        speed_modifier = skill_mod['speed'] * style_mod['speed']
        speed_noise = np.random.normal(1.0, (1 - consistency) * 0.1, len(driver_data))
        driver_data['Speed'] = driver_data['Speed'] * speed_modifier * speed_noise
        
        # Braking variations
        braking_modifier = skill_mod['braking'] * style_mod['braking']
        braking_noise = np.random.normal(1.0, (1 - consistency) * 0.15, len(driver_data))
        driver_data['pbrake_f'] = driver_data['pbrake_f'] * braking_modifier * braking_noise
        
        # Throttle variations
        throttle_modifier = skill_mod['throttle'] * style_mod['throttle']
        throttle_noise = np.random.normal(1.0, (1 - consistency) * 0.08, len(driver_data))
        driver_data['ath'] = driver_data['ath'] * throttle_modifier * throttle_noise
        
        # Cornering (lateral G) variations
        cornering_modifier = skill_mod['cornering'] * style_mod['cornering']
        cornering_noise = np.random.normal(1.0, (1 - consistency) * 0.12, len(driver_data))
        driver_data['accy_can'] = driver_data['accy_can'] * cornering_modifier * cornering_noise
        
        # Steering variations (more aggressive drivers use more steering input)
        if profile['style'] in ['aggressive', 'technical']:
            steering_modifier = 1.1
        elif profile['style'] in ['conservative', 'cautious']:
            steering_modifier = 0.9
        else:
            steering_modifier = 1.0
        
        steering_noise = np.random.normal(1.0, (1 - consistency) * 0.2, len(driver_data))
        driver_data['Steering_Angle'] = driver_data['Steering_Angle'] * steering_modifier * steering_noise
        
        # Update vehicle ID and related fields
        chassis = driver_id.split('-')[1]
        car_number = driver_id.split('-')[2]
        
        driver_data['vehicle_id'] = driver_id
        driver_data['chassis'] = chassis
        driver_data['car_number'] = car_number
        
        # Add some timestamp variation (different session times)
        base_timestamp = driver_data['timestamp'].iloc[0]
        time_offset = hash(driver_id) % 3600000  # Up to 1 hour offset
        driver_data['timestamp'] = driver_data['timestamp'] + time_offset
        driver_data['meta_time'] = driver_data['meta_time'] + time_offset
        
        # Update timestamp_dt
        driver_data['timestamp_dt'] = pd.to_datetime(driver_data['timestamp'], unit='ms')
        
        # Recalculate derived features
        driver_data['braking_intensity'] = driver_data['pbrake_f'] * np.abs(np.minimum(driver_data['accx_can'], 0))
        driver_data['cornering_force'] = np.abs(driver_data['accy_can'] * driver_data['Steering_Angle'])
        driver_data['throttle_efficiency'] = driver_data['Speed'] / (driver_data['ath'] + 1)
        driver_data['rpm_per_gear'] = driver_data['nmotor'] / (driver_data['Gear'] + 1)
        
        # Ensure realistic bounds
        driver_data['Speed'] = np.clip(driver_data['Speed'], 20, 200)  # 20-200 mph
        driver_data['pbrake_f'] = np.clip(driver_data['pbrake_f'], 0, 100)  # 0-100%
        driver_data['ath'] = np.clip(driver_data['ath'], 0, 100)  # 0-100%
        driver_data['Steering_Angle'] = np.clip(driver_data['Steering_Angle'], -45, 45)  # ±45 degrees
        
        return driver_data
    
    def create_multi_driver_dataset(self, track_id):
        """
        Create multi-driver dataset for a specific track
        """
        logger.info(f"🏎️ Creating multi-driver dataset for {track_id}")
        
        # Load existing single-driver data
        input_file = f"data/cleaned/{track_id}_telemetry_clean.csv"
        if not Path(input_file).exists():
            logger.error(f"❌ Input file not found: {input_file}")
            return None
        
        base_df = pd.read_csv(input_file)
        original_driver = base_df['vehicle_id'].iloc[0]
        
        logger.info(f"📊 Base data: {len(base_df)} records from {original_driver}")
        
        # Generate data for all drivers
        all_driver_data = []
        
        for driver_id, profile in self.driver_profiles.items():
            logger.info(f"🏁 Generating data for {driver_id} ({profile['skill']}, {profile['style']})")
            
            driver_data = self.generate_driver_variation(base_df, driver_id)
            all_driver_data.append(driver_data)
        
        # Combine all driver data
        combined_df = pd.concat(all_driver_data, ignore_index=True)
        
        # Sort by timestamp for realistic session flow
        combined_df = combined_df.sort_values(['timestamp', 'lap']).reset_index(drop=True)
        
        logger.info(f"✅ Generated {len(combined_df)} total records for {len(self.driver_profiles)} drivers")
        
        return combined_df
    
    def generate_all_tracks(self):
        """
        Generate multi-driver data for all available tracks
        """
        logger.info("🏁 Generating Multi-Driver Data for All Tracks")
        logger.info("=" * 55)
        
        tracks = ['BMP', 'COTA', 'VIR', 'SEB', 'SON', 'RA', 'INDY']
        results = {}
        
        for track_id in tracks:
            try:
                multi_driver_df = self.create_multi_driver_dataset(track_id)
                
                if multi_driver_df is not None:
                    # Save the enhanced dataset
                    output_file = f"data/cleaned/{track_id}_telemetry_clean.csv"
                    multi_driver_df.to_csv(output_file, index=False)
                    
                    # Generate summary stats
                    stats = {
                        'total_records': len(multi_driver_df),
                        'unique_drivers': multi_driver_df['vehicle_id'].nunique(),
                        'total_laps': multi_driver_df['lap'].nunique(),
                        'driver_breakdown': {}
                    }
                    
                    for driver_id in multi_driver_df['vehicle_id'].unique():
                        driver_records = multi_driver_df[multi_driver_df['vehicle_id'] == driver_id]
                        profile = self.driver_profiles[driver_id]
                        
                        stats['driver_breakdown'][driver_id] = {
                            'records': len(driver_records),
                            'laps': driver_records['lap'].nunique(),
                            'max_speed': round(driver_records['Speed'].max(), 1),
                            'avg_speed': round(driver_records['Speed'].mean(), 1),
                            'skill_level': profile['skill'],
                            'driving_style': profile['style'],
                            'consistency': profile['consistency']
                        }
                    
                    results[track_id] = stats
                    
                    logger.info(f"✅ {track_id}: {stats['total_records']} records, {stats['unique_drivers']} drivers")
                    
                    # Show driver performance spread
                    speeds = [d['avg_speed'] for d in stats['driver_breakdown'].values()]
                    logger.info(f"   Speed range: {min(speeds):.1f} - {max(speeds):.1f} mph")
                    
                else:
                    results[track_id] = {'status': 'failed', 'error': 'Could not generate data'}
                    logger.error(f"❌ {track_id}: Failed to generate data")
                    
            except Exception as e:
                results[track_id] = {'status': 'error', 'error': str(e)}
                logger.error(f"❌ {track_id}: Error - {e}")
        
        # Save generation report
        report_file = f"multi_driver_generation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        successful_tracks = [t for t, r in results.items() if isinstance(r, dict) and 'total_records' in r]
        
        logger.info(f"\n📈 Multi-Driver Data Generation Summary:")
        logger.info(f"✅ Successfully processed: {len(successful_tracks)} tracks")
        logger.info(f"🏎️ Total drivers per track: {len(self.driver_profiles)}")
        logger.info(f"📊 Driver profiles: Expert(2), Advanced(2), Intermediate(2), Beginner(1)")
        logger.info(f"📋 Report saved: {report_file}")
        
        return results

def main():
    """
    Main function to generate multi-driver data
    """
    print("🏁 GR Cup Multi-Driver Data Generator")
    print("=" * 45)
    print("This will enhance existing telemetry data with multiple realistic drivers")
    print("to provide diverse dashboard analytics and meaningful comparisons.")
    print()
    
    generator = MultiDriverDataGenerator()
    
    # Show driver profiles
    print("🏎️ Driver Profiles to Generate:")
    for driver_id, profile in generator.driver_profiles.items():
        print(f"  {driver_id}: {profile['skill'].title()} | {profile['style'].title()} | {profile['consistency']*100:.0f}% consistent")
    
    print()
    confirm = input("Generate multi-driver data for all tracks? (y/N): ").strip().lower()
    
    if confirm == 'y':
        results = generator.generate_all_tracks()
        
        print("\n🎯 Next Steps:")
        print("1. Upload enhanced data to AWS:")
        print("   python scripts/upload_enhanced_data.py")
        print("2. Visit dashboard to see diverse driver analytics")
        print("3. Each driver now has unique performance characteristics!")
        
    else:
        print("❌ Generation cancelled.")

if __name__ == "__main__":
    main()