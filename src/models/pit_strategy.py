"""
Recommends optimal pit window based on predictions

Author: GR Cup Analytics Team
Date: 2025-10-30

Strategy Logic:
- Simulate pitting at different laps
- Consider tire degradation vs pit stop time loss
- Account for track position and gaps
- Recommend optimal timing
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional
import matplotlib.pyplot as plt
from .tire_degradation import TireDegradationModel

logger = logging.getLogger(__name__)


class PitStrategyOptimizer:
    """
    Calculates optimal pit timing based on tire degradation predictions
    """
    
    def __init__(self, tire_model: TireDegradationModel):
        self.tire_model = tire_model
        self.pit_loss_seconds = 30  # Average pit stop time loss
        self.position_loss_threshold = 2  # Don't pit if losing >2 positions
    
    def simulate_pit_scenarios(self, current_lap: int, max_laps: int,
                             current_position: int, gap_ahead: float,
                             gap_behind: float, track_features: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Simulate pitting at different laps
        Return: List of scenarios with predicted final position
        
        For each potential pit lap:
        1. Predict lap times on old tires (don't pit)
        2. Predict lap times on new tires (pit now)
        3. Calculate position change
        4. Return best strategy
        """
        logger.info(f"Simulating pit scenarios from lap {current_lap}")
        
        scenarios = []
        
        # Current tire age
        current_tire_age = track_features.get('tire_age', current_lap)
        
        # Simulate pit windows (current lap to max_laps - 5)
        pit_window_end = min(max_laps - 5, current_lap + 15)
        
        for pit_lap in range(current_lap, pit_window_end + 1):
            scenario = self._simulate_single_scenario(
                pit_lap, current_lap, max_laps, current_position,
                gap_ahead, gap_behind, track_features, current_tire_age
            )
            scenarios.append(scenario)
        
        # Sort by predicted final position (lower is better)
        scenarios.sort(key=lambda x: x['predicted_final_position'])
        
        return scenarios
    
    def _simulate_single_scenario(self, pit_lap: int, current_lap: int, max_laps: int,
                                current_position: int, gap_ahead: float, gap_behind: float,
                                track_features: Dict[str, float], current_tire_age: int) -> Dict[str, Any]:
        """
        Simulate a single pit scenario
        """
        total_time = 0
        position_changes = 0
        
        # Phase 1: Current lap to pit lap (on current tires)
        for lap in range(current_lap, pit_lap + 1):
            tire_age = current_tire_age + (lap - current_lap)
            
            features = track_features.copy()
            features['tire_age'] = tire_age
            features['race_progress'] = lap / max_laps
            
            prediction = self.tire_model.predict_lap_time(features)
            lap_time = prediction['predicted_time']
            total_time += lap_time
        
        # Add pit stop time
        if pit_lap > current_lap:
            total_time += self.pit_loss_seconds
            
            # Estimate position loss during pit stop
            # Assume cars behind gain pit_loss_seconds / avg_lap_time positions
            avg_lap_time = track_features.get('session_best', 120) * 1.05
            positions_lost_in_pit = int(self.pit_loss_seconds / avg_lap_time)
            position_changes += positions_lost_in_pit
        
        # Phase 2: After pit to end of race (on fresh tires)
        fresh_tire_age = 1
        for lap in range(pit_lap + 1, max_laps + 1):
            tire_age = fresh_tire_age + (lap - pit_lap - 1)
            
            features = track_features.copy()
            features['tire_age'] = tire_age
            features['race_progress'] = lap / max_laps
            
            prediction = self.tire_model.predict_lap_time(features)
            lap_time = prediction['predicted_time']
            total_time += lap_time
        
        # Estimate final position
        predicted_final_position = max(1, current_position + position_changes)
        
        return {
            'pit_lap': pit_lap,
            'total_time': total_time,
            'position_changes': position_changes,
            'predicted_final_position': predicted_final_position,
            'pit_now': pit_lap == current_lap,
            'laps_to_pit': pit_lap - current_lap
        }
    
    def get_recommendation(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return: {
            'action': 'PIT_NOW' | 'PIT_IN_X_LAPS' | 'STAY_OUT',
            'laps_remaining': int,
            'confidence': float,
            'reasoning': str,
            'position_impact': str (e.g., 'Stay P3' or 'Gain to P2')
        }
        """
        logger.info("Generating pit strategy recommendation")
        
        try:
            # Extract current state
            current_lap = current_state.get('current_lap', 1)
            max_laps = current_state.get('max_laps', 30)
            current_position = current_state.get('position', 5)
            gap_ahead = current_state.get('gap_ahead', 5.0)
            gap_behind = current_state.get('gap_behind', 5.0)
            track_features = current_state.get('track_features', {})
            
            # Simulate scenarios
            scenarios = self.simulate_pit_scenarios(
                current_lap, max_laps, current_position,
                gap_ahead, gap_behind, track_features
            )
            
            if not scenarios:
                return self._default_recommendation()
            
            # Get best scenario
            best_scenario = scenarios[0]
            current_scenario = next((s for s in scenarios if s['pit_now']), scenarios[0])
            
            # Determine recommendation
            if best_scenario['pit_now']:
                action = 'PIT_NOW'
                laps_remaining = 0
                reasoning = f"Optimal window - tire degradation exceeds pit loss"
            elif best_scenario['laps_to_pit'] <= 3:
                action = f"PIT_IN_{best_scenario['laps_to_pit']}_LAPS"
                laps_remaining = best_scenario['laps_to_pit']
                reasoning = f"Pit in {best_scenario['laps_to_pit']} laps for optimal strategy"
            else:
                action = 'STAY_OUT'
                laps_remaining = best_scenario['laps_to_pit']
                reasoning = f"Stay out {best_scenario['laps_to_pit']} more laps"
            
            # Position impact
            if best_scenario['predicted_final_position'] < current_position:
                position_impact = f"Gain to P{best_scenario['predicted_final_position']}"
            elif best_scenario['predicted_final_position'] > current_position:
                position_impact = f"Drop to P{best_scenario['predicted_final_position']}"
            else:
                position_impact = f"Stay P{current_position}"
            
            # Confidence based on tire degradation rate
            tire_age = track_features.get('tire_age', current_lap)
            degradation_rate = track_features.get('track_degradation_rate', 0.5)
            
            if tire_age > 15 and degradation_rate > 1.0:
                confidence = 0.9  # High confidence - tires are old and degrading fast
            elif tire_age > 10:
                confidence = 0.7  # Medium confidence
            else:
                confidence = 0.5  # Lower confidence - tires still good
            
            return {
                'action': action,
                'laps_remaining': laps_remaining,
                'confidence': confidence,
                'reasoning': reasoning,
                'position_impact': position_impact,
                'scenarios': scenarios[:3],  # Top 3 scenarios
                'tire_cliff_lap': self.calculate_tire_cliff(track_features)
            }
            
        except Exception as e:
            logger.error(f"Error generating recommendation: {e}")
            return self._default_recommendation()
    
    def calculate_tire_cliff(self, features: Dict[str, float]) -> int:
        """
        Predict at which lap tire performance falls off dramatically
        (>1 second slower than fresh tires)
        """
        try:
            cliff_threshold = 1.0  # 1 second slower than fresh
            
            # Simulate tire degradation over laps
            for tire_age in range(1, 31):  # Check up to 30 laps
                test_features = features.copy()
                test_features['tire_age'] = tire_age
                
                # Compare to fresh tire performance
                fresh_features = features.copy()
                fresh_features['tire_age'] = 1
                
                current_prediction = self.tire_model.predict_lap_time(test_features)
                fresh_prediction = self.tire_model.predict_lap_time(fresh_features)
                
                degradation = current_prediction['predicted_time'] - fresh_prediction['predicted_time']
                
                if degradation > cliff_threshold:
                    return tire_age
            
            return 25  # Default cliff at 25 laps
            
        except Exception as e:
            logger.error(f"Error calculating tire cliff: {e}")
            return 20
    
    def _default_recommendation(self) -> Dict[str, Any]:
        """
        Return default recommendation when calculation fails
        """
        return {
            'action': 'STAY_OUT',
            'laps_remaining': 5,
            'confidence': 0.3,
            'reasoning': 'Insufficient data for optimal strategy',
            'position_impact': 'Unknown',
            'scenarios': [],
            'tire_cliff_lap': 20
        }
    
    def visualize_scenarios(self, scenarios: List[Dict[str, Any]], save_path: Optional[str] = None) -> None:
        """
        Create visualization: plot scenarios as lines showing projected lap times
        """
        if not scenarios:
            logger.warning("No scenarios to visualize")
            return
        
        try:
            plt.figure(figsize=(12, 8))
            
            # Plot top 3 scenarios
            colors = ['green', 'blue', 'red']
            
            for i, scenario in enumerate(scenarios[:3]):
                pit_lap = scenario['pit_lap']
                total_time = scenario['total_time']
                position = scenario['predicted_final_position']
                
                label = f"Pit Lap {pit_lap} → P{position} ({total_time:.1f}s total)"
                
                # Simple visualization - just show pit lap vs final position
                plt.scatter(pit_lap, position, color=colors[i], s=100, label=label)
            
            plt.xlabel('Pit Lap')
            plt.ylabel('Predicted Final Position')
            plt.title('Pit Strategy Scenarios')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            # Invert y-axis (lower position is better)
            plt.gca().invert_yaxis()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"Saved scenario visualization to {save_path}")
            
            plt.show()
            
        except Exception as e:
            logger.error(f"Error visualizing scenarios: {e}")
    
    def analyze_track_position_risk(self, current_position: int, gap_ahead: float, 
                                  gap_behind: float, avg_lap_time: float) -> Dict[str, Any]:
        """
        Analyze risk of losing positions during pit stop
        """
        try:
            # Calculate how many cars could pass during pit stop
            cars_that_could_pass = int(self.pit_loss_seconds / avg_lap_time)
            
            # Risk assessment
            if gap_behind < self.pit_loss_seconds:
                risk_level = 'HIGH'
                positions_at_risk = min(cars_that_could_pass, 3)
            elif gap_behind < self.pit_loss_seconds * 1.5:
                risk_level = 'MEDIUM'
                positions_at_risk = 1
            else:
                risk_level = 'LOW'
                positions_at_risk = 0
            
            return {
                'risk_level': risk_level,
                'positions_at_risk': positions_at_risk,
                'gap_behind': gap_behind,
                'pit_loss_time': self.pit_loss_seconds,
                'recommendation': 'AVOID_PIT' if risk_level == 'HIGH' and positions_at_risk > self.position_loss_threshold else 'PIT_OK'
            }
            
        except Exception as e:
            logger.error(f"Error analyzing position risk: {e}")
            return {'risk_level': 'UNKNOWN', 'positions_at_risk': 0, 'recommendation': 'PIT_OK'}