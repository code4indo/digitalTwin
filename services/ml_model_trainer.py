"""
ML Model Training Service
Service untuk melatih model machine learning untuk prediksi suhu dan kelembapan
"""

import logging
import numpy as np
import pandas as pd
import joblib
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from sklearn.model_selection import train_test_split, TimeSeriesSplit, cross_val_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.multioutput import MultiOutputRegressor
import warnings
warnings.filterwarnings('ignore')

from services.ml_training_service import create_training_data_collector

logger = logging.getLogger(__name__)


class ModelTrainer:
    """
    Class untuk training model machine learning prediktif
    """
    
    def __init__(self, model_storage_path: str = "/app/models"):
        self.model_storage_path = model_storage_path
        self.models = {}
        self.scalers = {}
        self.training_history = []
        self.feature_importance = {}
        
        # Create models directory
        os.makedirs(model_storage_path, exist_ok=True)
        
        # Initialize available models
        self.available_models = {
            'linear_regression': LinearRegression(),
            'ridge_regression': Ridge(alpha=1.0),
            'lasso_regression': Lasso(alpha=0.1),
            'random_forest': RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            ),
            'gradient_boosting': GradientBoostingRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
        }
    
    async def prepare_training_data(
        self,
        days_back: int = 30,
        test_size: float = 0.2,
        validation_size: float = 0.1,
        location_filter: Optional[str] = None,
        device_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Mempersiapkan data untuk training, validation, dan testing
        
        Args:
            days_back (int): Jumlah hari data historis
            test_size (float): Proporsi data untuk testing
            validation_size (float): Proporsi data untuk validation
            location_filter (str, optional): Filter lokasi
            device_filter (str, optional): Filter device
            
        Returns:
            Dict dengan train, validation, dan test sets
        """
        try:
            logger.info(f"Mempersiapkan data training untuk {days_back} hari")
            
            # Collect historical data
            collector = create_training_data_collector()
            raw_data = await collector.collect_historical_data(
                days_back=days_back,
                location_filter=location_filter,
                device_filter=device_filter
            )
            
            if raw_data.empty:
                raise ValueError("Tidak ada data historis ditemukan")
            
            # Merge with external data if available
            external_data = await collector.get_external_weather_data(days_back=days_back)
            if not external_data.empty:
                raw_data = await collector.merge_with_external_data(raw_data, external_data)
            
            # Prepare features and targets
            features, targets = await collector.prepare_training_features(raw_data)
            
            if len(features) < 100:
                raise ValueError(f"Insufficient data for training: {len(features)} samples")
            
            # Separate timestamp and features
            timestamps = features['timestamp']
            feature_cols = [col for col in features.columns if col != 'timestamp']
            X = features[feature_cols].copy()
            y = targets[['temp_target', 'humidity_target']].copy()
            
            # Handle missing values
            X = X.fillna(X.mean())
            y = y.fillna(y.mean())
            
            # Time-based split (more appropriate for time series)
            total_samples = len(X)
            test_start_idx = int(total_samples * (1 - test_size))
            val_start_idx = int(test_start_idx * (1 - validation_size))
            
            # Split data chronologically
            X_temp = X.iloc[:test_start_idx]
            X_test = X.iloc[test_start_idx:]
            y_temp = y.iloc[:test_start_idx]
            y_test = y.iloc[test_start_idx:]
            timestamps_test = timestamps.iloc[test_start_idx:]
            
            X_train = X_temp.iloc[:val_start_idx]
            X_val = X_temp.iloc[val_start_idx:]
            y_train = y_temp.iloc[:val_start_idx]
            y_val = y_temp.iloc[val_start_idx:]
            timestamps_train = timestamps.iloc[:val_start_idx]
            timestamps_val = timestamps.iloc[val_start_idx:test_start_idx]
            
            logger.info(f"Data split: Train={len(X_train)}, Val={len(X_val)}, Test={len(X_test)}")
            
            return {
                'X_train': X_train,
                'X_val': X_val,
                'X_test': X_test,
                'y_train': y_train,
                'y_val': y_val,
                'y_test': y_test,
                'timestamps_train': timestamps_train,
                'timestamps_val': timestamps_val,
                'timestamps_test': timestamps_test,
                'feature_names': feature_cols,
                'target_names': ['temp_target', 'humidity_target']
            }
            
        except Exception as e:
            logger.error(f"Error preparing training data: {e}")
            raise
    
    def train_model(
        self,
        model_name: str,
        X_train: pd.DataFrame,
        y_train: pd.DataFrame,
        X_val: pd.DataFrame = None,
        y_val: pd.DataFrame = None,
        scale_features: bool = True,
        hyperparameter_tuning: bool = False
    ) -> Dict[str, Any]:
        """
        Melatih model machine learning
        
        Args:
            model_name (str): Nama model yang akan dilatih
            X_train (pd.DataFrame): Features training
            y_train (pd.DataFrame): Targets training
            X_val (pd.DataFrame, optional): Features validation
            y_val (pd.DataFrame, optional): Targets validation
            scale_features (bool): Apakah melakukan feature scaling
            hyperparameter_tuning (bool): Apakah melakukan hyperparameter tuning
            
        Returns:
            Dict dengan informasi training
        """
        try:
            logger.info(f"Memulai training model: {model_name}")
            
            if model_name not in self.available_models:
                raise ValueError(f"Model {model_name} tidak tersedia")
            
            # Feature scaling
            if scale_features:
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_val_scaled = scaler.transform(X_val) if X_val is not None else None
                self.scalers[model_name] = scaler
            else:
                X_train_scaled = X_train.values
                X_val_scaled = X_val.values if X_val is not None else None
                self.scalers[model_name] = None
            
            # Initialize model
            base_model = self.available_models[model_name]
            
            # Use MultiOutputRegressor for multi-target prediction
            if len(y_train.columns) > 1:
                model = MultiOutputRegressor(base_model)
            else:
                model = base_model
            
            # Hyperparameter tuning (basic implementation)
            if hyperparameter_tuning:
                model = self._tune_hyperparameters(model, X_train_scaled, y_train.values)
            
            # Train model
            start_time = datetime.now()
            model.fit(X_train_scaled, y_train.values)
            training_time = (datetime.now() - start_time).total_seconds()
            
            # Evaluate on training set
            y_train_pred = model.predict(X_train_scaled)
            train_metrics = self._calculate_metrics(y_train.values, y_train_pred)
            
            # Evaluate on validation set if available
            val_metrics = {}
            if X_val is not None and y_val is not None:
                y_val_pred = model.predict(X_val_scaled)
                val_metrics = self._calculate_metrics(y_val.values, y_val_pred)
            
            # Store model
            self.models[model_name] = model
            
            # Calculate feature importance if available
            feature_importance = self._get_feature_importance(model, X_train.columns)
            self.feature_importance[model_name] = feature_importance
            
            # Training info
            training_info = {
                'model_name': model_name,
                'training_time': training_time,
                'training_samples': len(X_train),
                'validation_samples': len(X_val) if X_val is not None else 0,
                'features_count': X_train.shape[1],
                'targets_count': y_train.shape[1],
                'train_metrics': train_metrics,
                'val_metrics': val_metrics,
                'feature_importance': feature_importance,
                'hyperparameter_tuning': hyperparameter_tuning,
                'feature_scaling': scale_features,
                'trained_at': datetime.now().isoformat()
            }
            
            # Add to training history
            self.training_history.append(training_info)
            
            logger.info(f"Model {model_name} berhasil dilatih")
            logger.info(f"Train RMSE: {train_metrics.get('rmse', 'N/A')}")
            logger.info(f"Val RMSE: {val_metrics.get('rmse', 'N/A')}")
            
            return training_info
            
        except Exception as e:
            logger.error(f"Error training model {model_name}: {e}")
            raise
    
    def _tune_hyperparameters(self, model, X_train, y_train):
        """
        Basic hyperparameter tuning menggunakan cross-validation
        """
        # Simplified hyperparameter tuning
        # In production, use GridSearchCV or RandomizedSearchCV
        return model
    
    def _calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """
        Menghitung metrik evaluasi model
        """
        try:
            metrics = {}
            
            # Overall metrics
            mse = mean_squared_error(y_true, y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y_true, y_pred)
            
            metrics['mse'] = float(mse)
            metrics['rmse'] = float(rmse)
            metrics['mae'] = float(mae)
            
            # Per-target metrics
            if y_true.shape[1] == 2:  # temperature and humidity
                # Temperature metrics (target 0)
                temp_mse = mean_squared_error(y_true[:, 0], y_pred[:, 0])
                temp_mae = mean_absolute_error(y_true[:, 0], y_pred[:, 0])
                temp_r2 = r2_score(y_true[:, 0], y_pred[:, 0])
                
                metrics['temp_mse'] = float(temp_mse)
                metrics['temp_rmse'] = float(np.sqrt(temp_mse))
                metrics['temp_mae'] = float(temp_mae)
                metrics['temp_r2'] = float(temp_r2)
                
                # Humidity metrics (target 1)
                hum_mse = mean_squared_error(y_true[:, 1], y_pred[:, 1])
                hum_mae = mean_absolute_error(y_true[:, 1], y_pred[:, 1])
                hum_r2 = r2_score(y_true[:, 1], y_pred[:, 1])
                
                metrics['humidity_mse'] = float(hum_mse)
                metrics['humidity_rmse'] = float(np.sqrt(hum_mse))
                metrics['humidity_mae'] = float(hum_mae)
                metrics['humidity_r2'] = float(hum_r2)
            
            return metrics
            
        except Exception as e:
            logger.warning(f"Error calculating metrics: {e}")
            return {'error': str(e)}
    
    def _get_feature_importance(self, model, feature_names: List[str]) -> Dict[str, float]:
        """
        Mendapatkan feature importance dari model
        """
        try:
            importance_dict = {}
            
            # Handle MultiOutputRegressor
            if hasattr(model, 'estimators_'):
                # Average feature importance across estimators
                if hasattr(model.estimators_[0], 'feature_importances_'):
                    importances = np.mean([est.feature_importances_ for est in model.estimators_], axis=0)
                    importance_dict = dict(zip(feature_names, importances.astype(float)))
            elif hasattr(model, 'feature_importances_'):
                importance_dict = dict(zip(feature_names, model.feature_importances_.astype(float)))
            elif hasattr(model, 'coef_'):
                # For linear models, use absolute coefficients
                if model.coef_.ndim == 2:
                    # Multi-output: average absolute coefficients
                    importances = np.mean(np.abs(model.coef_), axis=0)
                else:
                    importances = np.abs(model.coef_)
                importance_dict = dict(zip(feature_names, importances.astype(float)))
            
            # Sort by importance
            if importance_dict:
                importance_dict = dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
            
            return importance_dict
            
        except Exception as e:
            logger.warning(f"Error getting feature importance: {e}")
            return {}
    
    def evaluate_model(
        self,
        model_name: str,
        X_test: pd.DataFrame,
        y_test: pd.DataFrame,
        timestamps_test: pd.Series = None
    ) -> Dict[str, Any]:
        """
        Evaluasi model pada test set
        """
        try:
            if model_name not in self.models:
                raise ValueError(f"Model {model_name} belum dilatih")
            
            model = self.models[model_name]
            scaler = self.scalers.get(model_name)
            
            # Scale features if needed
            if scaler is not None:
                X_test_scaled = scaler.transform(X_test)
            else:
                X_test_scaled = X_test.values
            
            # Make predictions
            y_pred = model.predict(X_test_scaled)
            
            # Calculate metrics
            test_metrics = self._calculate_metrics(y_test.values, y_pred)
            
            # Create predictions DataFrame
            predictions_df = pd.DataFrame({
                'timestamp': timestamps_test if timestamps_test is not None else range(len(y_test)),
                'temp_actual': y_test.iloc[:, 0],
                'temp_predicted': y_pred[:, 0],
                'humidity_actual': y_test.iloc[:, 1],
                'humidity_predicted': y_pred[:, 1]
            })
            
            # Calculate prediction errors
            predictions_df['temp_error'] = predictions_df['temp_actual'] - predictions_df['temp_predicted']
            predictions_df['humidity_error'] = predictions_df['humidity_actual'] - predictions_df['humidity_predicted']
            predictions_df['temp_error_abs'] = np.abs(predictions_df['temp_error'])
            predictions_df['humidity_error_abs'] = np.abs(predictions_df['humidity_error'])
            
            evaluation_result = {
                'model_name': model_name,
                'test_metrics': test_metrics,
                'predictions_sample': predictions_df.head(10).to_dict('records'),
                'error_statistics': {
                    'temp_error_mean': float(predictions_df['temp_error'].mean()),
                    'temp_error_std': float(predictions_df['temp_error'].std()),
                    'humidity_error_mean': float(predictions_df['humidity_error'].mean()),
                    'humidity_error_std': float(predictions_df['humidity_error'].std()),
                    'temp_mae': float(predictions_df['temp_error_abs'].mean()),
                    'humidity_mae': float(predictions_df['humidity_error_abs'].mean())
                },
                'evaluated_at': datetime.now().isoformat()
            }
            
            logger.info(f"Model {model_name} evaluasi selesai")
            logger.info(f"Test RMSE: {test_metrics.get('rmse', 'N/A')}")
            
            return evaluation_result
            
        except Exception as e:
            logger.error(f"Error evaluating model {model_name}: {e}")
            raise
    
    def save_model(self, model_name: str, version: str = "1.0") -> str:
        """
        Menyimpan model ke disk
        """
        try:
            if model_name not in self.models:
                raise ValueError(f"Model {model_name} belum dilatih")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_filename = f"{model_name}_v{version}_{timestamp}.joblib"
            model_path = os.path.join(self.model_storage_path, model_filename)
            
            # Save model and scaler
            model_data = {
                'model': self.models[model_name],
                'scaler': self.scalers.get(model_name),
                'feature_importance': self.feature_importance.get(model_name, {}),
                'model_name': model_name,
                'version': version,
                'trained_at': datetime.now().isoformat()
            }
            
            joblib.dump(model_data, model_path)
            
            # Save metadata
            metadata = {
                'model_name': model_name,
                'version': version,
                'filename': model_filename,
                'file_path': model_path,
                'saved_at': datetime.now().isoformat(),
                'training_history': [h for h in self.training_history if h['model_name'] == model_name]
            }
            
            metadata_path = model_path.replace('.joblib', '_metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Model {model_name} disimpan ke {model_path}")
            return model_path
            
        except Exception as e:
            logger.error(f"Error saving model {model_name}: {e}")
            raise
    
    def load_model(self, model_path: str) -> str:
        """
        Memuat model dari disk
        """
        try:
            model_data = joblib.load(model_path)
            
            model_name = model_data['model_name']
            self.models[model_name] = model_data['model']
            self.scalers[model_name] = model_data.get('scaler')
            self.feature_importance[model_name] = model_data.get('feature_importance', {})
            
            logger.info(f"Model {model_name} berhasil dimuat dari {model_path}")
            return model_name
            
        except Exception as e:
            logger.error(f"Error loading model from {model_path}: {e}")
            raise
    
    def compare_models(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Membandingkan performa semua model yang sudah dilatih
        """
        try:
            if not self.models:
                raise ValueError("Belum ada model yang dilatih")
            
            X_test = test_data['X_test']
            y_test = test_data['y_test']
            timestamps_test = test_data.get('timestamps_test')
            
            comparison_results = {}
            
            for model_name in self.models.keys():
                evaluation = self.evaluate_model(model_name, X_test, y_test, timestamps_test)
                comparison_results[model_name] = evaluation['test_metrics']
            
            # Find best model by RMSE
            best_model = min(comparison_results.keys(), key=lambda k: comparison_results[k].get('rmse', float('inf')))
            
            return {
                'comparison_results': comparison_results,
                'best_model': best_model,
                'best_rmse': comparison_results[best_model].get('rmse'),
                'models_count': len(comparison_results),
                'compared_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error comparing models: {e}")
            raise
    
    def get_training_summary(self) -> Dict[str, Any]:
        """
        Mendapatkan ringkasan training session
        """
        return {
            'trained_models': list(self.models.keys()),
            'training_history': self.training_history,
            'feature_importance': self.feature_importance,
            'models_count': len(self.models),
            'last_training': self.training_history[-1]['trained_at'] if self.training_history else None
        }


# Factory function
def create_model_trainer(model_storage_path: str = "/app/models") -> ModelTrainer:
    """
    Factory function untuk membuat ModelTrainer
    """
    return ModelTrainer(model_storage_path)
