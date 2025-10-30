"""
ML model to predict lap times based on tire age and track conditions

Author: GR Cup Analytics Team
Date: 2025-10-30

Features:
- tire_age: Number of laps on current tires
- driver_avg_pace: Driver's average lap time
- track_avg_speed: Track characteristic speed
- track_degradation_rate: Historical tire wear rate
- race_progress: Percentage through race
- recent_pace_3lap: Average of last 3 laps
- session_best: Best lap time in session
- track_type_encoded: 0=TECHNICAL, 1=HIGH_SPEED

Target: RMSE < 0.5 seconds, R² > 0.85
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import logging
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


class TireDegradationModel:
    """
    Predicts lap time based on tire age, track type, conditions
    """
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = [
            'tire_age',
            'driver_avg_pace',
            'track_avg_speed', 
            'track_degradation_rate',
            'race_progress',
            'recent_pace_3lap',
            'session_best',
            'track_type_encoded'  # 0=TECHNICAL, 1=HIGH_SPEED
        ]
        self.is_trained = False
        self.training_metrics = {}
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Engineer features from raw telemetry/lap data
        
        Required columns in df:
        - lap_number (for tire_age)
        - car_number
        - lap_time
        - track_name
        - Speed (from telemetry)
        """
        logger.info("Preparing features for tire degradation model...")
        
        if df.empty:
            return pd.DataFrame()
        
        try:
            features_df = df.copy()
            
            # Feature 1: tire_age (assuming pit stops reset tire age)
            features_df['tire_age'] = features_df.groupby('car_number')['lap_number'].transform(
                lambda x: x - x.min() + 1
            )
            
            # Feature 2: driver_avg_pace
            features_df['driver_avg_pace'] = features_df.groupby('car_number')['lap_time'].transform('mean')
            
            # Feature 3: track_avg_speed
            if 'Speed' in features_df.columns:
                features_df['track_avg_speed'] = features_df.groupby('track_name')['Speed'].transform('mean')
            else:
                features_df['track_avg_speed'] = 150.0  # Default value
            
            # Feature 4: track_degradation_rate (calculated from early vs late pace)
            track_degradation = self._calculate_track_degradation(features_df)
            features_df = features_df.merge(track_degradation, on='track_name', how='left')
            features_df['track_degradation_rate'] = features_df['track_degradation_rate'].fillna(0.5)
            
            # Feature 5: race_progress
            max_laps = features_df.groupby(['track_name', 'car_number'])['lap_number'].transform('max')
            features_df['race_progress'] = features_df['lap_number'] / max_laps
            
            # Feature 6: recent_pace_3lap
            features_df['recent_pace_3lap'] = features_df.groupby('car_number')['lap_time'].transform(
                lambda x: x.rolling(window=3, min_periods=1).mean()
            )
            
            # Feature 7: session_best
            features_df['session_best'] = features_df.groupby('track_name')['lap_time'].transform('min')
            
            # Feature 8: track_type_encoded
            features_df['track_type_encoded'] = features_df['track_avg_speed'].apply(
                lambda x: 1 if x > 150 else 0
            )
            
            # Select only the features we need
            feature_columns = self.feature_names + ['lap_time']
            available_columns = [col for col in feature_columns if col in features_df.columns]
            
            result_df = features_df[available_columns].copy()
            
            # Remove invalid records
            result_df = result_df.dropna()
            result_df = result_df[result_df['lap_time'] > 0]
            
            logger.info(f"Prepared {len(result_df)} feature records")
            return result_df
            
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            return pd.DataFrame()
    
    def _calculate_track_degradation(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate historical tire degradation rate per track
        """
        degradation_rates = []
        
        for track in df['track_name'].unique():
            track_data = df[df['track_name'] == track]
            
            # Early laps (2-5)
            early_laps = track_data[
                (track_data['lap_number'] >= 2) & (track_data['lap_number'] <= 5)
            ]['lap_time']
            
            # Late laps (15+)
            late_laps = track_data[track_data['lap_number'] >= 15]['lap_time']
            
            if len(early_laps) > 0 and len(late_laps) > 0:
                degradation_rate = late_laps.mean() - early_laps.mean()
            else:
                degradation_rate = 0.5  # Default
            
            degradation_rates.append({
                'track_name': track,
                'track_degradation_rate': max(0, degradation_rate)
            })
        
        return pd.DataFrame(degradation_rates)
    
    def train(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2) -> Dict[str, float]:
        """
        Train ensemble model (GradientBoosting + RandomForest)
        Use cross-validation
        Save model to models/tire_degradation_v1.pkl
        Save scaler to models/scaler_v1.pkl
        """
        logger.info("Training tire degradation model...")
        
        try:
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Hyperparameter tuning for GradientBoosting
            gb_params = {
                'n_estimators': [100, 200],
                'max_depth': [3, 5, 7],
                'learning_rate': [0.1, 0.05]
            }
            
            gb_model = GradientBoostingRegressor(random_state=42)
            gb_grid = GridSearchCV(
                gb_model, gb_params, cv=5, scoring='neg_mean_squared_error', n_jobs=-1
            )
            gb_grid.fit(X_train_scaled, y_train)
            
            # Use best GradientBoosting model
            self.model = gb_grid.best_estimator_
            
            # Make predictions
            y_pred_train = self.model.predict(X_train_scaled)
            y_pred_test = self.model.predict(X_test_scaled)
            
            # Calculate metrics
            train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
            test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
            train_r2 = r2_score(y_train, y_pred_train)
            test_r2 = r2_score(y_test, y_pred_test)
            test_mae = mean_absolute_error(y_test, y_pred_test)
            
            # Cross-validation
            cv_scores = cross_val_score(
                self.model, X_train_scaled, y_train, cv=5, scoring='r2'
            )
            
            self.training_metrics = {
                'train_rmse': train_rmse,
                'test_rmse': test_rmse,
                'train_r2': train_r2,
                'test_r2': test_r2,
                'test_mae': test_mae,
                'cv_r2_mean': cv_scores.mean(),
                'cv_r2_std': cv_scores.std(),
                'best_params': gb_grid.best_params_
            }
            
            # Save model artifacts
            Path('models').mkdir(exist_ok=True)
            joblib.dump(self.model, 'models/tire_degradation_v1.pkl')
            joblib.dump(self.scaler, 'models/scaler_v1.pkl')
            
            # Save metrics
            import json
            with open('models/training_metrics.json', 'w') as f:
                json.dump(self.training_metrics, f, indent=2)
            
            self.is_trained = True
            
            logger.info(f"Model training complete:")
            logger.info(f"  Test RMSE: {test_rmse:.3f} seconds")
            logger.info(f"  Test R²: {test_r2:.3f}")
            logger.info(f"  Test MAE: {test_mae:.3f} seconds")
            logger.info(f"  CV R² (mean±std): {cv_scores.mean():.3f}±{cv_scores.std():.3f}")
            
            # Create evaluation plots
            self._create_evaluation_plots(y_test, y_pred_test, X_test)
            
            return self.training_metrics
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            return {}
    
    def predict_lap_time(self, features: Dict[str, float]) -> Dict[str, float]:
        """
        Predict single lap time
        Return: {
            'predicted_time': float,
            'confidence': float (0-1),
            'uncertainty': float (std dev)
        }
        """
        if not self.is_trained or self.model is None:
            logger.error("Model not trained")
            return {'predicted_time': 0.0, 'confidence': 0.0, 'uncertainty': 999.0}
        
        try:
            # Prepare feature vector
            feature_vector = []
            for feature_name in self.feature_names:
                value = features.get(feature_name, 0.0)
                feature_vector.append(value)
            
            # Scale features
            feature_vector = np.array(feature_vector).reshape(1, -1)
            feature_vector_scaled = self.scaler.transform(feature_vector)
            
            # Make prediction
            prediction = self.model.predict(feature_vector_scaled)[0]
            
            # Estimate confidence based on training performance
            confidence = min(0.95, self.training_metrics.get('test_r2', 0.5))
            uncertainty = self.training_metrics.get('test_rmse', 1.0)
            
            return {
                'predicted_time': float(prediction),
                'confidence': float(confidence),
                'uncertainty': float(uncertainty)
            }
            
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            return {'predicted_time': 0.0, 'confidence': 0.0, 'uncertainty': 999.0}
    
    def get_feature_importance(self) -> pd.DataFrame:
        """
        Return feature importance scores
        Used for model explainability
        """
        if not self.is_trained or self.model is None:
            return pd.DataFrame()
        
        try:
            importances = self.model.feature_importances_
            
            importance_df = pd.DataFrame({
                'feature': self.feature_names,
                'importance': importances
            }).sort_values('importance', ascending=False)
            
            return importance_df
            
        except Exception as e:
            logger.error(f"Error getting feature importance: {e}")
            return pd.DataFrame()
    
    def _create_evaluation_plots(self, y_true: np.ndarray, y_pred: np.ndarray, X_test: pd.DataFrame) -> None:
        """
        Create evaluation plots: actual vs predicted, residuals, feature importance
        """
        try:
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            
            # Actual vs Predicted
            axes[0, 0].scatter(y_true, y_pred, alpha=0.6)
            axes[0, 0].plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--', lw=2)
            axes[0, 0].set_xlabel('Actual Lap Time (s)')
            axes[0, 0].set_ylabel('Predicted Lap Time (s)')
            axes[0, 0].set_title('Actual vs Predicted Lap Times')
            
            # Residuals
            residuals = y_true - y_pred
            axes[0, 1].scatter(y_pred, residuals, alpha=0.6)
            axes[0, 1].axhline(y=0, color='r', linestyle='--')
            axes[0, 1].set_xlabel('Predicted Lap Time (s)')
            axes[0, 1].set_ylabel('Residuals (s)')
            axes[0, 1].set_title('Residual Plot')
            
            # Feature Importance
            importance_df = self.get_feature_importance()
            if not importance_df.empty:
                axes[1, 0].barh(importance_df['feature'], importance_df['importance'])
                axes[1, 0].set_xlabel('Importance')
                axes[1, 0].set_title('Feature Importance')
            
            # Prediction Error Distribution
            axes[1, 1].hist(residuals, bins=30, alpha=0.7)
            axes[1, 1].set_xlabel('Prediction Error (s)')
            axes[1, 1].set_ylabel('Frequency')
            axes[1, 1].set_title('Prediction Error Distribution')
            
            plt.tight_layout()
            plt.savefig('models/model_evaluation.png', dpi=300, bbox_inches='tight')
            logger.info("Saved evaluation plots to models/model_evaluation.png")
            
        except Exception as e:
            logger.error(f"Error creating evaluation plots: {e}")
    
    def load_model(self, model_path: str = 'models/tire_degradation_v1.pkl', 
                   scaler_path: str = 'models/scaler_v1.pkl') -> bool:
        """
        Load pre-trained model and scaler
        """
        try:
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            self.is_trained = True
            
            # Load metrics if available
            metrics_path = 'models/training_metrics.json'
            if Path(metrics_path).exists():
                import json
                with open(metrics_path, 'r') as f:
                    self.training_metrics = json.load(f)
            
            logger.info("Model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False