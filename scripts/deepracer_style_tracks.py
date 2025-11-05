"""
DeepRacer-Style Track Coordinate System for GR Cup

This creates track maps using the same waypoint system that AWS DeepRacer uses.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import json

class DeepRacerStyleTrack:
    """
    Create tracks using DeepRacer's waypoint system
    """
    
    def __init__(self, track_name, waypoints, track_width=15.0):
        self.track_name = track_name
        self.waypoints = np.array(waypoints)
        self.track_width = track_width
        self.track_length = self._calculate_track_length()
    
    def _calculate_track_length(self):
        """Calculate total track length from waypoints"""
        distances = []
        for i in range(len(self.waypoints)):
            p1 = self.waypoints[i]
            p2 = self.waypoints[(i + 1) % len(self.waypoints)]
            dist = np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
            distances.append(dist)
        return sum(distances)
    
    def get_track_boundaries(self):
        """Calculate left and right track boundaries"""
        left_boundary = []
        right_boundary = []
        
        for i in range(len(self.waypoints)):
            # Get current point and next point
            current = self.waypoints[i]
            next_point = self.waypoints[(i + 1) % len(self.waypoints)]
            
            # Calculate direction vector
            direction = next_point - current
            direction_norm = np.linalg.norm(direction)
            
            if direction_norm > 0:
                # Normalize direction
                direction = direction / direction_norm
                
                # Calculate perpendicular vector (90 degrees)
                perpendicular = np.array([-direction[1], direction[0]])
                
                # Calculate boundary points
                half_width = self.track_width / 2
                left_point = current + perpendicular * half_width
                right_point = current - perpendicular * half_width
                
                left_boundary.append(left_point)
                right_boundary.append(right_point)
        
        return np.array(left_boundary), np.array(right_boundary)
    
    def create_track_map(self, output_dir):
        """Create track visualization"""
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Get track boundaries
        left_boundary, right_boundary = self.get_track_boundaries()
        
        # Plot track surface
        # Create closed polygon for track surface
        track_polygon_x = np.concatenate([left_boundary[:, 0], right_boundary[::-1, 0]])
        track_polygon_y = np.concatenate([left_boundary[:, 1], right_boundary[::-1, 1]])
        
        ax.fill(track_polygon_x, track_polygon_y, color='lightgray', alpha=0.7, label='Track surface')
        
        # Plot boundaries
        ax.plot(left_boundary[:, 0], left_boundary[:, 1], 'k-', linewidth=3, label='Track boundaries')
        ax.plot(right_boundary[:, 0], right_boundary[:, 1], 'k-', linewidth=3)
        
        # Plot centerline (waypoints)
        waypoint_x = self.waypoints[:, 0]
        waypoint_y = self.waypoints[:, 1]
        
        # Close the loop
        waypoint_x = np.append(waypoint_x, waypoint_x[0])
        waypoint_y = np.append(waypoint_y, waypoint_y[0])
        
        ax.plot(waypoint_x, waypoint_y, 'b--', linewidth=2, alpha=0.8, label='Centerline')
        
        # Plot waypoints as dots
        ax.scatter(self.waypoints[:, 0], self.waypoints[:, 1], 
                  c='red', s=30, alpha=0.7, label='Waypoints')
        
        # Add waypoint numbers
        for i, (x, y) in enumerate(self.waypoints[::5]):  # Every 5th waypoint
            ax.annotate(f'{i*5}', (x, y), xytext=(5, 5), 
                       textcoords='offset points', fontsize=8)
        
        # Start/finish line
        start_point = self.waypoints[0]
        ax.plot([start_point[0]-10, start_point[0]+10], 
               [start_point[1]-5, start_point[1]+5], 
               'red', linewidth=6, label='Start/Finish')
        
        # Formatting
        ax.set_aspect('equal')
        ax.set_title(f'{self.track_name} - DeepRacer Style Layout\n'
                    f'Length: {self.track_length:.1f}m, Width: {self.track_width}m', 
                    fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('X Coordinate (meters)')
        ax.set_ylabel('Y Coordinate (meters)')
        
        # Save
        output_path = output_dir / f"{self.track_name.lower().replace(' ', '_')}_deepracer_style.png"
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path

def get_barber_waypoints():
    """
    Barber Motorsports Park waypoints (approximated from real track)
    These would ideally come from GPS survey data
    """
    waypoints = [
        # Start/finish straight
        [0, 0], [50, 0], [100, 0], [150, 0], [200, 0],
        
        # Turn 1 approach and hairpin
        [250, 0], [300, -10], [350, -30], [400, -60],
        [430, -100], [440, -150], [430, -200], [400, -240],
        [350, -270], [300, -280], [250, -270], [200, -240],
        
        # Esses section
        [180, -200], [160, -160], [150, -120], [160, -80],
        [180, -40], [200, -20], [220, -40], [240, -80],
        [250, -120], [240, -160], [220, -200],
        
        # Back section
        [200, -220], [150, -240], [100, -250], [50, -240],
        [20, -200], [10, -150], [20, -100], [50, -60],
        
        # Final corners back to start
        [80, -30], [120, -10], [160, 0], [200, 5],
        [240, 0], [280, -10], [300, -30], [280, -50],
        [240, -60], [200, -50], [160, -30], [120, -10],
        [80, 0], [40, 0]
    ]
    
    return waypoints

def main():
    print("🏁 Creating DeepRacer-Style Track Maps")
    print("=" * 45)
    print("Using waypoint system like AWS DeepRacer...")
    
    # Create Barber track using waypoints
    barber_waypoints = get_barber_waypoints()
    barber_track = DeepRacerStyleTrack("Barber Motorsports Park", barber_waypoints, track_width=15.0)
    
    output_path = barber_track.create_track_map("deepracer_style_maps")
    
    print(f"\n✅ Created DeepRacer-style track map!")
    print(f"📁 Location: {output_path}")
    print(f"📊 Track Stats:")
    print(f"   • Waypoints: {len(barber_waypoints)}")
    print(f"   • Length: {barber_track.track_length:.1f} meters")
    print(f"   • Width: {barber_track.track_width} meters")
    
    # Save waypoint data
    waypoint_file = Path("deepracer_style_maps") / "barber_waypoints.json"
    with open(waypoint_file, 'w') as f:
        json.dump({
            'track_name': 'Barber Motorsports Park',
            'waypoints': barber_waypoints,
            'track_width': 15.0,
            'track_length': barber_track.track_length
        }, f, indent=2)
    
    print(f"💾 Waypoint data saved: {waypoint_file}")

if __name__ == "__main__":
    main()