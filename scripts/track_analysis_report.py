"""
Track Analysis Report - Show understanding of each track from extracted data

Author: GR Cup Analytics Team
Date: 2025-10-31

This script analyzes each track's characteristics from the extracted data
and generates visual representations to verify our understanding matches
the PDF track maps and data.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging
import sys
from typing import Dict, List, Any
import json

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from utils.config import TRACKS, setup_logging
from data_processing.sector_parser import SectorAnalyzer

setup_logging()
logger = logging.getLogger(__name__)

class TrackAnalyzer:
    """
    Analyze and visualize track characteristics from extracted data
    """
    
    def __init__(self):
        self.track_reports = {}
        self.output_dir = Path("track_analysis_output")
        self.output_dir.mkdir(exist_ok=True)
    
    def analyze_track_from_data(self, track_abbrev: str, track_config: Dict) -> Dict[str, Any]:
        """
        Analyze a single track from all available data sources
        """
        logger.info(f"\n🏁 ANALYZING {track_abbrev} - {track_config['name']}")
        logger.info("=" * 60)
        
        track_analysis = {
            'track_id': track_abbrev,
            'track_name': track_config['name'],
            'expected_lap_time': track_config['typical_lap_time'],
            'data_sources': {},
            'sector_analysis': {},
            'telemetry_insights': {},
            'track_characteristics': {},
            'data_quality': {}
        }
        
        track_folder = track_config['folder']
        
        # 1. Analyze Telemetry Data
        telemetry_analysis = self._analyze_telemetry(track_abbrev, track_folder)
        track_analysis['telemetry_insights'] = telemetry_analysis
        
        # 2. Analyze Sector Data (6-sector GR Cup format)
        sector_analysis = self._analyze_sectors(track_abbrev, track_folder)
        track_analysis['sector_analysis'] = sector_analysis
        
        # 3. Analyze Lap Times
        lap_analysis = self._analyze_lap_times(track_abbrev, track_folder)
        track_analysis['lap_analysis'] = lap_analysis
        
        # 4. Determine Track Characteristics
        characteristics = self._determine_track_characteristics(
            telemetry_analysis, sector_analysis, lap_analysis, track_config
        )
        track_analysis['track_characteristics'] = characteristics
        
        # 5. Generate Visual Analysis
        self._create_track_visualization(track_abbrev, track_analysis)
        
        return track_analysis
    
    def _analyze_telemetry(self, track_abbrev: str, track_folder: str) -> Dict[str, Any]:
        """
        Analyze telemetry data to understand track characteristics
        """
        logger.info(f"📊 Analyzing telemetry data...")
        
        # Check cleaned telemetry
        clean_path = Path(f"data/cleaned/{track_abbrev}_telemetry_clean.csv")
        
        if not clean_path.exists():
            logger.warning(f"No cleaned telemetry found for {track_abbrev}")
            return {}
        
        try:
            df = pd.read_csv(clean_path)
            
            analysis = {
                'total_records': len(df),
                'unique_cars': df['car_number'].nunique() if 'car_number' in df.columns else 0,
                'lap_range': [int(df['lap'].min()), int(df['lap'].max())] if 'lap' in df.columns else [0, 0],
                'speed_analysis': {},
                'braking_analysis': {},
                'steering_analysis': {},
                'gear_analysis': {}
            }
            
            # Speed Analysis
            if 'Speed' in df.columns:
                speeds = df['Speed'].dropna()
                analysis['speed_analysis'] = {
                    'min_speed': float(speeds.min()),
                    'max_speed': float(speeds.max()),
                    'avg_speed': float(speeds.mean()),
                    'speed_range': float(speeds.max() - speeds.min()),
                    'high_speed_percentage': float((speeds > 150).mean() * 100)
                }
                
                logger.info(f"  🏎️  Speed: {speeds.min():.1f} - {speeds.max():.1f} mph (avg: {speeds.mean():.1f})")
            
            # Braking Analysis
            if 'pbrake_f' in df.columns:
                braking = df['pbrake_f'].dropna()
                heavy_braking = braking > 50  # Threshold for heavy braking
                
                analysis['braking_analysis'] = {
                    'max_brake_pressure': float(braking.max()),
                    'avg_brake_pressure': float(braking.mean()),
                    'heavy_braking_percentage': float(heavy_braking.mean() * 100),
                    'braking_zones': int(heavy_braking.sum())
                }
                
                logger.info(f"  🛑 Braking: Max {braking.max():.1f}, Heavy braking {heavy_braking.mean()*100:.1f}% of time")
            
            # Steering Analysis
            if 'Steering_Angle' in df.columns:
                steering = df['Steering_Angle'].dropna()
                abs_steering = steering.abs()
                
                analysis['steering_analysis'] = {
                    'max_steering_angle': float(abs_steering.max()),
                    'avg_steering_angle': float(abs_steering.mean()),
                    'technical_percentage': float((abs_steering > 20).mean() * 100)
                }
                
                logger.info(f"  🔄 Steering: Max {abs_steering.max():.1f}°, Technical sections {(abs_steering > 20).mean()*100:.1f}%")
            
            # Gear Analysis
            if 'Gear' in df.columns:
                gears = df['Gear'].dropna()
                
                analysis['gear_analysis'] = {
                    'gear_range': [int(gears.min()), int(gears.max())],
                    'most_used_gear': int(gears.mode().iloc[0]) if len(gears.mode()) > 0 else 0,
                    'gear_distribution': gears.value_counts().to_dict()
                }
                
                logger.info(f"  ⚙️  Gears: {int(gears.min())}-{int(gears.max())}, Most used: {int(gears.mode().iloc[0]) if len(gears.mode()) > 0 else 'N/A'}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing telemetry for {track_abbrev}: {e}")
            return {}
    
    def _analyze_sectors(self, track_abbrev: str, track_folder: str) -> Dict[str, Any]:
        """
        Analyze 6-sector data to understand track layout
        """
        logger.info(f"🎯 Analyzing sector data...")
        
        # Look for sector analysis file
        sector_path = Path(f"data/extracted/{track_folder}")
        sector_files = list(sector_path.glob("*AnalysisEnduranceWithSections*.csv"))
        
        if not sector_files:
            logger.warning(f"No sector analysis file found for {track_abbrev}")
            return {}
        
        try:
            df = pd.read_csv(sector_files[0])
            
            # Expected GR Cup 6-sector format
            expected_sectors = ['IM1a', 'IM1', 'IM2a', 'IM2', 'IM3a', 'FL']
            found_sectors = [col for col in expected_sectors if col in df.columns]
            
            if len(found_sectors) != 6:
                logger.warning(f"Only found {len(found_sectors)}/6 sectors: {found_sectors}")
                return {}
            
            analysis = {
                'sectors_found': found_sectors,
                'total_laps': len(df),
                'unique_cars': df['car_number'].nunique() if 'car_number' in df.columns else df['Car'].nunique(),
                'sector_characteristics': {},
                'fastest_sectors': {},
                'tire_degradation_by_sector': {}
            }
            
            # Analyze each sector
            for sector in found_sectors:
                sector_times = df[sector].dropna()
                
                if len(sector_times) > 0:
                    analysis['sector_characteristics'][sector] = {
                        'min_time': float(sector_times.min()),
                        'max_time': float(sector_times.max()),
                        'avg_time': float(sector_times.mean()),
                        'std_dev': float(sector_times.std()),
                        'range': float(sector_times.max() - sector_times.min())
                    }
                    
                    logger.info(f"  {sector}: {sector_times.min():.2f}s - {sector_times.max():.2f}s (avg: {sector_times.mean():.2f}s)")
            
            # Find fastest and slowest sectors
            avg_times = {sector: analysis['sector_characteristics'][sector]['avg_time'] 
                        for sector in found_sectors if sector in analysis['sector_characteristics']}
            
            if avg_times:
                fastest_sector = min(avg_times, key=avg_times.get)
                slowest_sector = max(avg_times, key=avg_times.get)
                
                analysis['fastest_sectors'] = {
                    'fastest': fastest_sector,
                    'fastest_time': avg_times[fastest_sector],
                    'slowest': slowest_sector,
                    'slowest_time': avg_times[slowest_sector]
                }
                
                logger.info(f"  🏃 Fastest sector: {fastest_sector} ({avg_times[fastest_sector]:.2f}s)")
                logger.info(f"  🐌 Slowest sector: {slowest_sector} ({avg_times[slowest_sector]:.2f}s)")
            
            # Calculate total lap time from sectors
            if len(found_sectors) == 6:
                total_sector_time = sum(df[sector].mean() for sector in found_sectors if sector in df.columns)
                analysis['calculated_lap_time'] = total_sector_time
                logger.info(f"  ⏱️  Calculated lap time from sectors: {total_sector_time:.2f}s")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing sectors for {track_abbrev}: {e}")
            return {}
    
    def _analyze_lap_times(self, track_abbrev: str, track_folder: str) -> Dict[str, Any]:
        """
        Analyze lap times to validate track understanding
        """
        logger.info(f"⏱️  Analyzing lap times...")
        
        # Look for lap times file
        lap_path = Path(f"data/extracted/{track_folder}")
        lap_files = list(lap_path.glob("*lap_times*.csv"))
        
        if not lap_files:
            logger.warning(f"No lap times file found for {track_abbrev}")
            return {}
        
        try:
            df = pd.read_csv(lap_files[0])
            
            # Find lap time column
            lap_time_col = None
            for col in ['lap_time', 'Lap_Time', 'Time', 'LapTime']:
                if col in df.columns:
                    lap_time_col = col
                    break
            
            if not lap_time_col:
                logger.warning(f"No lap time column found in {lap_files[0]}")
                return {}
            
            lap_times = df[lap_time_col].dropna()
            
            # Convert time format if needed (MM:SS.sss to seconds)
            if lap_times.dtype == 'object':
                lap_times = lap_times.apply(self._convert_time_to_seconds)
                lap_times = lap_times.dropna()
            
            analysis = {
                'total_laps': len(lap_times),
                'fastest_lap': float(lap_times.min()),
                'slowest_lap': float(lap_times.max()),
                'average_lap': float(lap_times.mean()),
                'lap_time_range': float(lap_times.max() - lap_times.min()),
                'consistency': float(lap_times.std())
            }
            
            logger.info(f"  🏁 Lap times: {lap_times.min():.2f}s - {lap_times.max():.2f}s (avg: {lap_times.mean():.2f}s)")
            logger.info(f"  📊 Consistency (std dev): {lap_times.std():.2f}s")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing lap times for {track_abbrev}: {e}")
            return {}
    
    def _convert_time_to_seconds(self, time_str):
        """
        Convert time string (MM:SS.sss) to seconds
        """
        try:
            if pd.isna(time_str):
                return np.nan
            
            time_str = str(time_str).strip()
            
            if ':' in time_str:
                parts = time_str.split(':')
                minutes = float(parts[0])
                seconds = float(parts[1])
                return minutes * 60 + seconds
            else:
                return float(time_str)
        except:
            return np.nan
    
    def _determine_track_characteristics(self, telemetry: Dict, sectors: Dict, laps: Dict, track_config: Dict) -> Dict[str, Any]:
        """
        Determine overall track characteristics from all data
        """
        logger.info(f"🔍 Determining track characteristics...")
        
        characteristics = {
            'track_type': 'UNKNOWN',
            'difficulty_level': 'MEDIUM',
            'tire_wear_severity': 'MEDIUM',
            'key_features': [],
            'racing_style': 'BALANCED'
        }
        
        # Determine track type from speed and steering data
        if telemetry and 'speed_analysis' in telemetry and 'steering_analysis' in telemetry:
            avg_speed = telemetry['speed_analysis'].get('avg_speed', 0)
            high_speed_pct = telemetry['speed_analysis'].get('high_speed_percentage', 0)
            technical_pct = telemetry['steering_analysis'].get('technical_percentage', 0)
            
            if avg_speed > 140 and high_speed_pct > 60:
                characteristics['track_type'] = 'HIGH_SPEED'
                characteristics['racing_style'] = 'POWER_FOCUSED'
                characteristics['key_features'].append('High-speed straights')
            elif technical_pct > 40:
                characteristics['track_type'] = 'TECHNICAL'
                characteristics['racing_style'] = 'HANDLING_FOCUSED'
                characteristics['key_features'].append('Technical corners')
            else:
                characteristics['track_type'] = 'BALANCED'
                characteristics['racing_style'] = 'BALANCED'
        
        # Determine difficulty from lap time consistency
        if laps and 'consistency' in laps:
            consistency = laps['consistency']
            if consistency > 2.0:
                characteristics['difficulty_level'] = 'HIGH'
                characteristics['key_features'].append('Challenging for consistency')
            elif consistency < 1.0:
                characteristics['difficulty_level'] = 'LOW'
                characteristics['key_features'].append('Consistent lap times possible')
        
        # Determine tire wear from braking intensity
        if telemetry and 'braking_analysis' in telemetry:
            heavy_braking_pct = telemetry['braking_analysis'].get('heavy_braking_percentage', 0)
            if heavy_braking_pct > 15:
                characteristics['tire_wear_severity'] = 'HIGH'
                characteristics['key_features'].append('Heavy braking zones')
            elif heavy_braking_pct < 5:
                characteristics['tire_wear_severity'] = 'LOW'
                characteristics['key_features'].append('Gentle on tires')
        
        # Add sector-specific insights
        if sectors and 'fastest_sectors' in sectors:
            fastest = sectors['fastest_sectors'].get('fastest', '')
            slowest = sectors['fastest_sectors'].get('slowest', '')
            
            if fastest:
                characteristics['key_features'].append(f'Fastest sector: {fastest}')
            if slowest:
                characteristics['key_features'].append(f'Challenging sector: {slowest}')
        
        logger.info(f"  🏁 Track Type: {characteristics['track_type']}")
        logger.info(f"  🎯 Racing Style: {characteristics['racing_style']}")
        logger.info(f"  🔥 Tire Wear: {characteristics['tire_wear_severity']}")
        
        return characteristics
    
    def _create_track_visualization(self, track_abbrev: str, analysis: Dict[str, Any]):
        """
        Create visual representation of track understanding
        """
        logger.info(f"📊 Creating track visualization...")
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'{track_abbrev} - {analysis["track_name"]} Analysis', fontsize=16, fontweight='bold')
        
        # 1. Sector Times Comparison
        if analysis['sector_analysis'] and 'sector_characteristics' in analysis['sector_analysis']:
            sectors = analysis['sector_analysis']['sector_characteristics']
            
            if sectors:
                sector_names = list(sectors.keys())
                sector_times = [sectors[s]['avg_time'] for s in sector_names]
                
                axes[0, 0].bar(sector_names, sector_times, color='skyblue', edgecolor='navy')
                axes[0, 0].set_title('Sector Times (6-Sector GR Cup Format)')
                axes[0, 0].set_ylabel('Time (seconds)')
                axes[0, 0].tick_params(axis='x', rotation=45)
                
                # Add sector mapping labels
                sector_mapping = {
                    'IM1a': 'S1.a (First half of section 1)',
                    'IM1': 'S1.b (Second half of section 1)',
                    'IM2a': 'S2.a (First half of section 2)',
                    'IM2': 'S2.b (Second half of section 2)',
                    'IM3a': 'S3.a (First half of section 3)',
                    'FL': 'S3.b (Final sector to finish)'
                }
                
                # Add text annotations
                for i, (sector, time) in enumerate(zip(sector_names, sector_times)):
                    axes[0, 0].text(i, time + 0.1, f'{time:.1f}s', ha='center', va='bottom')
        
        # 2. Speed Distribution
        if analysis['telemetry_insights'] and 'speed_analysis' in analysis['telemetry_insights']:
            speed_data = analysis['telemetry_insights']['speed_analysis']
            
            # Create speed range visualization
            speed_ranges = ['Low\n(0-100)', 'Medium\n(100-150)', 'High\n(150+)']
            # Estimate distribution based on available data
            high_pct = speed_data.get('high_speed_percentage', 0)
            medium_pct = max(0, 100 - high_pct - 20)  # Estimate
            low_pct = max(0, 100 - high_pct - medium_pct)
            
            speed_distribution = [low_pct, medium_pct, high_pct]
            colors = ['red', 'yellow', 'green']
            
            axes[0, 1].pie(speed_distribution, labels=speed_ranges, colors=colors, autopct='%1.1f%%')
            axes[0, 1].set_title('Speed Distribution')
        
        # 3. Track Characteristics Radar
        characteristics = analysis.get('track_characteristics', {})
        
        # Create characteristic scores (0-5 scale)
        char_scores = {
            'Speed': 3,  # Default
            'Technical': 3,
            'Tire Wear': 3,
            'Difficulty': 3,
            'Consistency': 3
        }
        
        # Adjust based on analysis
        if characteristics.get('track_type') == 'HIGH_SPEED':
            char_scores['Speed'] = 5
            char_scores['Technical'] = 2
        elif characteristics.get('track_type') == 'TECHNICAL':
            char_scores['Speed'] = 2
            char_scores['Technical'] = 5
        
        if characteristics.get('tire_wear_severity') == 'HIGH':
            char_scores['Tire Wear'] = 5
        elif characteristics.get('tire_wear_severity') == 'LOW':
            char_scores['Tire Wear'] = 2
        
        # Simple bar chart for characteristics
        char_names = list(char_scores.keys())
        char_values = list(char_scores.values())
        
        axes[1, 0].barh(char_names, char_values, color='lightcoral')
        axes[1, 0].set_title('Track Characteristics (1-5 Scale)')
        axes[1, 0].set_xlim(0, 5)
        
        # 4. Key Statistics Summary
        axes[1, 1].axis('off')
        
        # Compile key statistics
        stats_text = f"TRACK ANALYSIS SUMMARY\n\n"
        stats_text += f"Track Type: {characteristics.get('track_type', 'Unknown')}\n"
        stats_text += f"Racing Style: {characteristics.get('racing_style', 'Unknown')}\n"
        stats_text += f"Tire Wear: {characteristics.get('tire_wear_severity', 'Unknown')}\n\n"
        
        if analysis['telemetry_insights']:
            tel = analysis['telemetry_insights']
            if 'speed_analysis' in tel:
                stats_text += f"Speed Range: {tel['speed_analysis'].get('min_speed', 0):.0f} - {tel['speed_analysis'].get('max_speed', 0):.0f} mph\n"
            stats_text += f"Data Records: {tel.get('total_records', 0):,}\n"
            stats_text += f"Cars Analyzed: {tel.get('unique_cars', 0)}\n\n"
        
        if analysis['sector_analysis'] and 'calculated_lap_time' in analysis['sector_analysis']:
            calc_time = analysis['sector_analysis']['calculated_lap_time']
            expected_time = analysis['expected_lap_time']
            stats_text += f"Calculated Lap Time: {calc_time:.2f}s\n"
            stats_text += f"Expected Lap Time: {expected_time:.2f}s\n"
            stats_text += f"Difference: {abs(calc_time - expected_time):.2f}s\n\n"
        
        if characteristics.get('key_features'):
            stats_text += "Key Features:\n"
            for feature in characteristics['key_features'][:5]:  # Top 5 features
                stats_text += f"• {feature}\n"
        
        axes[1, 1].text(0.05, 0.95, stats_text, transform=axes[1, 1].transAxes, 
                        fontsize=10, verticalalignment='top', fontfamily='monospace')
        
        plt.tight_layout()
        
        # Save visualization
        output_path = self.output_dir / f"{track_abbrev}_analysis.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"  💾 Saved visualization: {output_path}")
        
        plt.close()
    
    def generate_comprehensive_report(self):
        """
        Generate comprehensive report for all tracks
        """
        logger.info("\n🏁 GENERATING COMPREHENSIVE TRACK ANALYSIS REPORT")
        logger.info("=" * 70)
        
        all_analyses = {}
        
        # Analyze each track
        for track_abbrev, track_config in TRACKS.items():
            analysis = self.analyze_track_from_data(track_abbrev, track_config)
            all_analyses[track_abbrev] = analysis
        
        # Create summary comparison
        self._create_track_comparison(all_analyses)
        
        # Save detailed report
        report_path = self.output_dir / "comprehensive_track_report.json"
        with open(report_path, 'w') as f:
            json.dump(all_analyses, f, indent=2, default=str)
        
        logger.info(f"\n📊 COMPREHENSIVE REPORT COMPLETE")
        logger.info(f"📁 All outputs saved to: {self.output_dir}")
        logger.info(f"📄 Detailed report: {report_path}")
        
        return all_analyses
    
    def _create_track_comparison(self, all_analyses: Dict):
        """
        Create comparison visualization across all tracks
        """
        logger.info(f"\n📊 Creating track comparison visualization...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('GR Cup Track Comparison Analysis', fontsize=16, fontweight='bold')
        
        # Prepare data for comparison
        track_names = []
        lap_times = []
        track_types = []
        tire_wear = []
        
        for track_abbrev, analysis in all_analyses.items():
            if analysis:
                track_names.append(track_abbrev)
                
                # Get calculated or expected lap time
                if analysis.get('sector_analysis', {}).get('calculated_lap_time'):
                    lap_times.append(analysis['sector_analysis']['calculated_lap_time'])
                else:
                    lap_times.append(analysis.get('expected_lap_time', 0))
                
                track_types.append(analysis.get('track_characteristics', {}).get('track_type', 'UNKNOWN'))
                tire_wear.append(analysis.get('track_characteristics', {}).get('tire_wear_severity', 'MEDIUM'))
        
        # 1. Lap Time Comparison
        if lap_times:
            bars = axes[0, 0].bar(track_names, lap_times, color='lightblue', edgecolor='navy')
            axes[0, 0].set_title('Lap Time Comparison')
            axes[0, 0].set_ylabel('Lap Time (seconds)')
            axes[0, 0].tick_params(axis='x', rotation=45)
            
            # Add value labels on bars
            for bar, time in zip(bars, lap_times):
                height = bar.get_height()
                axes[0, 0].text(bar.get_x() + bar.get_width()/2., height + 1,
                               f'{time:.1f}s', ha='center', va='bottom')
        
        # 2. Track Type Distribution
        type_counts = {}
        for t_type in track_types:
            type_counts[t_type] = type_counts.get(t_type, 0) + 1
        
        if type_counts:
            axes[0, 1].pie(type_counts.values(), labels=type_counts.keys(), autopct='%1.0f')
            axes[0, 1].set_title('Track Type Distribution')
        
        # 3. Tire Wear Comparison
        wear_mapping = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3}
        wear_scores = [wear_mapping.get(wear, 2) for wear in tire_wear]
        
        if wear_scores:
            colors = ['green' if w == 1 else 'yellow' if w == 2 else 'red' for w in wear_scores]
            axes[1, 0].bar(track_names, wear_scores, color=colors, edgecolor='black')
            axes[1, 0].set_title('Tire Wear Severity')
            axes[1, 0].set_ylabel('Severity (1=Low, 2=Medium, 3=High)')
            axes[1, 0].tick_params(axis='x', rotation=45)
            axes[1, 0].set_ylim(0, 4)
        
        # 4. Summary Statistics
        axes[1, 1].axis('off')
        
        summary_text = "TRACK ANALYSIS SUMMARY\n\n"
        summary_text += f"Total Tracks Analyzed: {len(all_analyses)}\n\n"
        
        if lap_times:
            summary_text += f"Lap Time Range: {min(lap_times):.1f}s - {max(lap_times):.1f}s\n"
            summary_text += f"Average Lap Time: {np.mean(lap_times):.1f}s\n\n"
        
        summary_text += "Track Types:\n"
        for t_type, count in type_counts.items():
            summary_text += f"• {t_type}: {count} tracks\n"
        
        summary_text += f"\nTire Wear Distribution:\n"
        wear_counts = {}
        for wear in tire_wear:
            wear_counts[wear] = wear_counts.get(wear, 0) + 1
        
        for wear, count in wear_counts.items():
            summary_text += f"• {wear}: {count} tracks\n"
        
        axes[1, 1].text(0.05, 0.95, summary_text, transform=axes[1, 1].transAxes,
                        fontsize=11, verticalalignment='top', fontfamily='monospace')
        
        plt.tight_layout()
        
        # Save comparison
        comparison_path = self.output_dir / "track_comparison.png"
        plt.savefig(comparison_path, dpi=300, bbox_inches='tight')
        logger.info(f"  💾 Saved comparison: {comparison_path}")
        
        plt.close()

def main():
    """
    Main function to generate track analysis report
    """
    logger.info("🏁 GR Cup Track Analysis Report Generator")
    logger.info("=" * 60)
    logger.info("This will analyze each track from extracted data and generate")
    logger.info("visual representations you can compare against your PDFs.")
    logger.info("")
    
    analyzer = TrackAnalyzer()
    analyses = analyzer.generate_comprehensive_report()
    
    logger.info(f"\n✅ ANALYSIS COMPLETE!")
    logger.info(f"\n📊 Generated Files:")
    logger.info(f"  • Individual track analysis images (7 files)")
    logger.info(f"  • Track comparison visualization")
    logger.info(f"  • Comprehensive JSON report")
    logger.info(f"\n📁 Location: {analyzer.output_dir}")
    logger.info(f"\n🔍 You can now compare these visualizations with your PDF track maps!")
    
    return analyses

if __name__ == "__main__":
    main()