"""
GR Cup Telemetry Analysis Dashboard

Create comprehensive analysis based on actual telemetry data we have,
without trying to create fake track maps.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import json

class TelemetryAnalysisDashboard:
    """
    Analyze telemetry data and create meaningful visualizations
    """
    
    def __init__(self):
        self.data_dir = Path("data/cleaned")
        self.output_dir = Path("telemetry_analysis")
        self.output_dir.mkdir(exist_ok=True)
        
        # Track information
        self.tracks = {
            'BMP': 'Barber Motorsports Park',
            'COTA': 'Circuit of the Americas', 
            'VIR': 'Virginia International Raceway',
            'SEB': 'Sebring International Raceway',
            'SON': 'Sonoma Raceway',
            'RA': 'Road America',
            'INDY': 'Indianapolis Motor Speedway'
        }
    
    def load_track_data(self, track_abbrev):
        """Load telemetry data for a specific track"""
        file_path = self.data_dir / f"{track_abbrev}_telemetry_clean.csv"
        if file_path.exists():
            return pd.read_csv(file_path)
        return None
    
    def analyze_speed_profiles(self):
        """Analyze speed profiles across all tracks"""
        print("📊 Analyzing speed profiles across tracks...")
        
        fig, axes = plt.subplots(2, 4, figsize=(20, 10))
        axes = axes.flatten()
        
        speed_stats = {}
        
        for i, (track_abbrev, track_name) in enumerate(self.tracks.items()):
            df = self.load_track_data(track_abbrev)
            if df is not None:
                ax = axes[i]
                
                # Speed distribution
                ax.hist(df['Speed'], bins=30, alpha=0.7, color='skyblue', edgecolor='black')
                ax.set_title(f'{track_name}\nSpeed Distribution')
                ax.set_xlabel('Speed (mph)')
                ax.set_ylabel('Frequency')
                
                # Calculate stats
                speed_stats[track_abbrev] = {
                    'track_name': track_name,
                    'max_speed': df['Speed'].max(),
                    'avg_speed': df['Speed'].mean(),
                    'min_speed': df['Speed'].min(),
                    'speed_variance': df['Speed'].var()
                }
                
                # Add stats text
                stats_text = f"Max: {df['Speed'].max():.1f} mph\n"
                stats_text += f"Avg: {df['Speed'].mean():.1f} mph\n"
                stats_text += f"Min: {df['Speed'].min():.1f} mph"
                ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                       verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "speed_profiles_all_tracks.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        return speed_stats
    
    def analyze_braking_patterns(self):
        """Analyze braking patterns across tracks"""
        print("🛑 Analyzing braking patterns...")
        
        fig, axes = plt.subplots(2, 4, figsize=(20, 10))
        axes = axes.flatten()
        
        braking_stats = {}
        
        for i, (track_abbrev, track_name) in enumerate(self.tracks.items()):
            df = self.load_track_data(track_abbrev)
            if df is not None:
                ax = axes[i]
                
                # Braking intensity analysis
                braking_data = df[df['pbrake_f'] > 0]['pbrake_f']
                
                if len(braking_data) > 0:
                    ax.hist(braking_data, bins=20, alpha=0.7, color='red', edgecolor='black')
                    ax.set_title(f'{track_name}\nBraking Intensity')
                    ax.set_xlabel('Brake Pressure')
                    ax.set_ylabel('Frequency')
                    
                    braking_stats[track_abbrev] = {
                        'track_name': track_name,
                        'max_braking': braking_data.max(),
                        'avg_braking': braking_data.mean(),
                        'braking_events': len(braking_data),
                        'braking_percentage': (len(braking_data) / len(df)) * 100
                    }
                    
                    stats_text = f"Max: {braking_data.max():.1f}\n"
                    stats_text += f"Avg: {braking_data.mean():.1f}\n"
                    stats_text += f"Events: {len(braking_data)}\n"
                    stats_text += f"% of lap: {(len(braking_data) / len(df)) * 100:.1f}%"
                    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                           verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "braking_patterns_all_tracks.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        return braking_stats
    
    def analyze_cornering_performance(self):
        """Analyze cornering performance using steering and G-forces"""
        print("🏎️ Analyzing cornering performance...")
        
        fig, axes = plt.subplots(2, 4, figsize=(20, 10))
        axes = axes.flatten()
        
        cornering_stats = {}
        
        for i, (track_abbrev, track_name) in enumerate(self.tracks.items()):
            df = self.load_track_data(track_abbrev)
            if df is not None:
                ax = axes[i]
                
                # Scatter plot: Steering angle vs lateral G-force
                ax.scatter(df['Steering_Angle'], df['accy_can'], alpha=0.5, s=1)
                ax.set_title(f'{track_name}\nSteering vs Lateral G')
                ax.set_xlabel('Steering Angle')
                ax.set_ylabel('Lateral G-Force')
                
                cornering_stats[track_abbrev] = {
                    'track_name': track_name,
                    'max_steering': abs(df['Steering_Angle']).max(),
                    'max_lateral_g': abs(df['accy_can']).max(),
                    'avg_cornering_force': df['cornering_force'].mean(),
                    'steering_variance': df['Steering_Angle'].var()
                }
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "cornering_performance_all_tracks.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        return cornering_stats 
   
    def create_track_comparison_dashboard(self):
        """Create comprehensive track comparison dashboard"""
        print("📈 Creating track comparison dashboard...")
        
        # Load all track data
        all_data = {}
        for track_abbrev in self.tracks.keys():
            df = self.load_track_data(track_abbrev)
            if df is not None:
                all_data[track_abbrev] = df
        
        if not all_data:
            print("❌ No data available for analysis")
            return
        
        # Create comparison metrics
        comparison_data = []
        for track_abbrev, df in all_data.items():
            comparison_data.append({
                'Track': self.tracks[track_abbrev],
                'Abbrev': track_abbrev,
                'Max Speed': df['Speed'].max(),
                'Avg Speed': df['Speed'].mean(),
                'Max Braking': df['pbrake_f'].max(),
                'Max Lateral G': abs(df['accy_can']).max(),
                'Max Steering': abs(df['Steering_Angle']).max(),
                'Data Points': len(df),
                'Unique Laps': df['lap'].nunique(),
                'Avg Throttle': df['ath'].mean()
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        
        # Create multi-panel comparison dashboard
        fig = plt.figure(figsize=(20, 12))
        
        # 1. Speed comparison
        ax1 = plt.subplot(2, 3, 1)
        bars1 = ax1.bar(comparison_df['Abbrev'], comparison_df['Max Speed'], color='skyblue')
        ax1.set_title('Maximum Speed by Track', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Speed (mph)')
        ax1.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.0f}', ha='center', va='bottom')
        
        # 2. Average speed comparison
        ax2 = plt.subplot(2, 3, 2)
        bars2 = ax2.bar(comparison_df['Abbrev'], comparison_df['Avg Speed'], color='lightgreen')
        ax2.set_title('Average Speed by Track', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Speed (mph)')
        ax2.tick_params(axis='x', rotation=45)
        
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.0f}', ha='center', va='bottom')
        
        # 3. Braking intensity
        ax3 = plt.subplot(2, 3, 3)
        bars3 = ax3.bar(comparison_df['Abbrev'], comparison_df['Max Braking'], color='red', alpha=0.7)
        ax3.set_title('Maximum Braking Intensity', fontsize=14, fontweight='bold')
        ax3.set_ylabel('Brake Pressure')
        ax3.tick_params(axis='x', rotation=45)
        
        # 4. Lateral G-forces
        ax4 = plt.subplot(2, 3, 4)
        bars4 = ax4.bar(comparison_df['Abbrev'], comparison_df['Max Lateral G'], color='orange', alpha=0.7)
        ax4.set_title('Maximum Lateral G-Force', fontsize=14, fontweight='bold')
        ax4.set_ylabel('G-Force')
        ax4.tick_params(axis='x', rotation=45)
        
        # 5. Data coverage
        ax5 = plt.subplot(2, 3, 5)
        bars5 = ax5.bar(comparison_df['Abbrev'], comparison_df['Data Points'], color='purple', alpha=0.7)
        ax5.set_title('Data Points Available', fontsize=14, fontweight='bold')
        ax5.set_ylabel('Number of Data Points')
        ax5.tick_params(axis='x', rotation=45)
        
        # 6. Track characteristics radar chart
        ax6 = plt.subplot(2, 3, 6, projection='polar')
        
        # Normalize metrics for radar chart
        metrics = ['Max Speed', 'Avg Speed', 'Max Braking', 'Max Lateral G', 'Max Steering']
        normalized_data = comparison_df[metrics].copy()
        for col in metrics:
            normalized_data[col] = (normalized_data[col] - normalized_data[col].min()) / (normalized_data[col].max() - normalized_data[col].min())
        
        # Plot first few tracks on radar
        angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
        angles += angles[:1]  # Complete the circle
        
        colors = ['red', 'blue', 'green', 'orange']
        for i, (_, row) in enumerate(normalized_data.head(4).iterrows()):
            values = row.tolist()
            values += values[:1]  # Complete the circle
            ax6.plot(angles, values, 'o-', linewidth=2, label=comparison_df.iloc[i]['Abbrev'], color=colors[i])
            ax6.fill(angles, values, alpha=0.25, color=colors[i])
        
        ax6.set_xticks(angles[:-1])
        ax6.set_xticklabels(metrics)
        ax6.set_title('Track Characteristics Comparison', fontsize=14, fontweight='bold')
        ax6.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "track_comparison_dashboard.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # Save comparison data
        comparison_df.to_csv(self.output_dir / "track_comparison_data.csv", index=False)
        
        return comparison_df
    
    def create_lap_analysis(self, track_abbrev):
        """Analyze individual lap performance"""
        print(f"🏁 Analyzing lap performance for {track_abbrev}...")
        
        df = self.load_track_data(track_abbrev)
        if df is None:
            return None
        
        # Group by lap
        lap_stats = []
        for lap_num in df['lap'].unique():
            lap_data = df[df['lap'] == lap_num]
            
            lap_stats.append({
                'lap': lap_num,
                'max_speed': lap_data['Speed'].max(),
                'avg_speed': lap_data['Speed'].mean(),
                'min_speed': lap_data['Speed'].min(),
                'max_braking': lap_data['pbrake_f'].max(),
                'avg_throttle': lap_data['ath'].mean(),
                'max_lateral_g': abs(lap_data['accy_can']).max(),
                'data_points': len(lap_data)
            })
        
        lap_df = pd.DataFrame(lap_stats)
        
        # Create lap analysis visualization
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Speed progression
        axes[0, 0].plot(lap_df['lap'], lap_df['max_speed'], 'o-', color='blue', label='Max Speed')
        axes[0, 0].plot(lap_df['lap'], lap_df['avg_speed'], 'o-', color='green', label='Avg Speed')
        axes[0, 0].set_title(f'{self.tracks[track_abbrev]} - Speed by Lap')
        axes[0, 0].set_xlabel('Lap Number')
        axes[0, 0].set_ylabel('Speed (mph)')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Braking analysis
        axes[0, 1].plot(lap_df['lap'], lap_df['max_braking'], 'o-', color='red')
        axes[0, 1].set_title('Braking Intensity by Lap')
        axes[0, 1].set_xlabel('Lap Number')
        axes[0, 1].set_ylabel('Max Brake Pressure')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Throttle usage
        axes[1, 0].plot(lap_df['lap'], lap_df['avg_throttle'], 'o-', color='orange')
        axes[1, 0].set_title('Average Throttle by Lap')
        axes[1, 0].set_xlabel('Lap Number')
        axes[1, 0].set_ylabel('Throttle %')
        axes[1, 0].grid(True, alpha=0.3)
        
        # G-force analysis
        axes[1, 1].plot(lap_df['lap'], lap_df['max_lateral_g'], 'o-', color='purple')
        axes[1, 1].set_title('Maximum Lateral G by Lap')
        axes[1, 1].set_xlabel('Lap Number')
        axes[1, 1].set_ylabel('G-Force')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / f"{track_abbrev}_lap_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        return lap_df
    
    def generate_comprehensive_report(self):
        """Generate comprehensive telemetry analysis report"""
        print("📋 Generating comprehensive telemetry analysis report...")
        
        # Run all analyses
        speed_stats = self.analyze_speed_profiles()
        braking_stats = self.analyze_braking_patterns()
        cornering_stats = self.analyze_cornering_performance()
        comparison_df = self.create_track_comparison_dashboard()
        
        # Generate individual lap analyses
        lap_analyses = {}
        for track_abbrev in self.tracks.keys():
            lap_df = self.create_lap_analysis(track_abbrev)
            if lap_df is not None:
                lap_analyses[track_abbrev] = lap_df
        
        # Create summary report
        report = {
            'analysis_date': pd.Timestamp.now().isoformat(),
            'tracks_analyzed': list(self.tracks.keys()),
            'speed_statistics': speed_stats,
            'braking_statistics': braking_stats,
            'cornering_statistics': cornering_stats,
            'summary': {
                'fastest_track': comparison_df.loc[comparison_df['Max Speed'].idxmax(), 'Track'],
                'most_technical_track': comparison_df.loc[comparison_df['Max Lateral G'].idxmax(), 'Track'],
                'hardest_braking_track': comparison_df.loc[comparison_df['Max Braking'].idxmax(), 'Track'],
                'total_data_points': comparison_df['Data Points'].sum(),
                'total_laps_analyzed': comparison_df['Unique Laps'].sum()
            }
        }
        
        # Save report
        with open(self.output_dir / "comprehensive_telemetry_report.json", 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n✅ COMPREHENSIVE TELEMETRY ANALYSIS COMPLETE!")
        print(f"📁 All files saved to: {self.output_dir}")
        print(f"📊 Tracks analyzed: {len(self.tracks)}")
        print(f"📈 Total data points: {comparison_df['Data Points'].sum():,}")
        print(f"🏁 Total laps: {comparison_df['Unique Laps'].sum()}")
        
        return report

def main():
    print("🏁 GR Cup Telemetry Analysis Dashboard")
    print("=" * 50)
    print("Analyzing REAL telemetry data from all 7 tracks...")
    print("Creating comprehensive performance analysis...")
    print()
    
    dashboard = TelemetryAnalysisDashboard()
    report = dashboard.generate_comprehensive_report()
    
    print(f"\n🎯 KEY INSIGHTS:")
    print(f"🚀 Fastest Track: {report['summary']['fastest_track']}")
    print(f"🏎️ Most Technical: {report['summary']['most_technical_track']}")
    print(f"🛑 Hardest Braking: {report['summary']['hardest_braking_track']}")

if __name__ == "__main__":
    main()