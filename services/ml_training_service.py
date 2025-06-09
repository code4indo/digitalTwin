"""
ML Training Data Service
Modul ini berisi fungsi-fungsi untuk mengumpulkan dan mempersiapkan data training
dari InfluxDB untuk model machine learning prediktif
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from influxdb_client.client.exceptions import InfluxDBError
from fastapi import HTTPException

from services.stats_service import get_query_api

logger = logging.getLogger(__name__)


class TrainingDataCollector:
    """
    Class untuk mengumpulkan dan mempersiapkan data training dari InfluxDB
    """
    
    def __init__(self, bucket: str = "sensor_data_primary"):
        self.bucket = bucket
        self.query_api = get_query_api()
    
    async def collect_historical_data(
        self, 
        days_back: int = 30,
        location_filter: Optional[str] = None,
        device_filter: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Mengumpulkan data historis sensor untuk training
        
        Args:
            days_back (int): Jumlah hari ke belakang untuk mengambil data
            location_filter (str, optional): Filter berdasarkan lokasi
            device_filter (str, optional): Filter berdasarkan device_id
            
        Returns:
            pd.DataFrame: Data historis dalam format pandas DataFrame
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days_back)
        
        # Build additional filters
        additional_filters = ""
        if location_filter:
            additional_filters += f' and r.location == "{location_filter}"'
        if device_filter:
            additional_filters += f' and r.device_id == "{device_filter}"'
        
        query = f'''
        from(bucket: "{self.bucket}")
          |> range(start: {start_time.isoformat()}Z, stop: {end_time.isoformat()}Z)
          |> filter(fn: (r) => r._measurement == "sensor_reading"{additional_filters})
          |> filter(fn: (r) => r._field == "temperature" or r._field == "humidity")
          |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
          |> keep(columns: ["_time", "temperature", "humidity", "location", "device_id"])
          |> sort(columns: ["_time"])
        '''
        
        try:
            logger.info(f"Mengumpulkan data training untuk {days_back} hari terakhir")
            results = self.query_api.query_data_frame(query=query)
            
            if results.empty:
                logger.warning("Tidak ada data historis ditemukan")
                return pd.DataFrame()
            
            # Clean and prepare data
            df = self._clean_dataframe(results)
            logger.info(f"Data training terkumpul: {len(df)} records")
            
            return df
            
        except InfluxDBError as e:
            logger.error(f"InfluxDBError saat mengumpulkan data training: {e}")
            raise HTTPException(status_code=500, detail=f"Gagal mengumpulkan data training: {e.message}")
        except Exception as e:
            logger.error(f"Error saat mengumpulkan data training: {e}")
            raise HTTPException(status_code=500, detail="Gagal mengumpulkan data training")
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Membersihkan dan mempersiapkan DataFrame untuk training
        
        Args:
            df (pd.DataFrame): Raw DataFrame dari InfluxDB
            
        Returns:
            pd.DataFrame: Cleaned DataFrame
        """
        # Convert time column to datetime
        if '_time' in df.columns:
            df['_time'] = pd.to_datetime(df['_time'])
            df = df.rename(columns={'_time': 'timestamp'})
        
        # Remove rows with missing values
        df = df.dropna(subset=['temperature', 'humidity'])
        
        # Add time-based features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['month'] = df['timestamp'].dt.month
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        # Add lag features (previous values)
        df = df.sort_values('timestamp')
        df['temp_lag_1h'] = df['temperature'].shift(6)  # 1 hour ago (10min intervals)
        df['humidity_lag_1h'] = df['humidity'].shift(6)
        df['temp_lag_6h'] = df['temperature'].shift(36)  # 6 hours ago
        df['humidity_lag_6h'] = df['humidity'].shift(36)
        
        # Add moving averages
        df['temp_ma_1h'] = df['temperature'].rolling(window=6, min_periods=1).mean()
        df['humidity_ma_1h'] = df['humidity'].rolling(window=6, min_periods=1).mean()
        df['temp_ma_6h'] = df['temperature'].rolling(window=36, min_periods=1).mean()
        df['humidity_ma_6h'] = df['humidity'].rolling(window=36, min_periods=1).mean()
        
        # Add rate of change
        df['temp_change_rate'] = df['temperature'].diff() / 10  # per minute
        df['humidity_change_rate'] = df['humidity'].diff() / 10
        
        # Remove rows with NaN values after feature engineering
        df = df.dropna()
        
        return df
    
    async def prepare_training_features(
        self, 
        df: pd.DataFrame,
        target_horizon: int = 6  # predict 1 hour ahead (6 * 10min intervals)
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Mempersiapkan features dan targets untuk training
        
        Args:
            df (pd.DataFrame): Cleaned historical data
            target_horizon (int): How many time steps ahead to predict
            
        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Features and targets DataFrames
        """
        # Create target variables (future values)
        targets = pd.DataFrame()
        targets['temp_target'] = df['temperature'].shift(-target_horizon)
        targets['humidity_target'] = df['humidity'].shift(-target_horizon)
        targets['timestamp'] = df['timestamp']
        
        # Select features for training
        feature_columns = [
            'temperature', 'humidity', 'hour', 'day_of_week', 'month', 'is_weekend',
            'temp_lag_1h', 'humidity_lag_1h', 'temp_lag_6h', 'humidity_lag_6h',
            'temp_ma_1h', 'humidity_ma_1h', 'temp_ma_6h', 'humidity_ma_6h',
            'temp_change_rate', 'humidity_change_rate'
        ]
        
        features = df[['timestamp'] + feature_columns].copy()
        
        # Remove rows where targets are NaN
        valid_indices = targets[['temp_target', 'humidity_target']].notna().all(axis=1)
        features = features[valid_indices]
        targets = targets[valid_indices]
        
        logger.info(f"Training data prepared: {len(features)} samples, {len(feature_columns)} features")
        
        return features, targets
    
    async def get_external_weather_data(
        self, 
        days_back: int = 30
    ) -> pd.DataFrame:
        """
        Mengambil data cuaca eksternal dari BMKG untuk training
        
        Args:
            days_back (int): Jumlah hari ke belakang
            
        Returns:
            pd.DataFrame: Data cuaca eksternal
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days_back)
        
        query = f'''
        from(bucket: "{self.bucket}")
          |> range(start: {start_time.isoformat()}Z, stop: {end_time.isoformat()}Z)
          |> filter(fn: (r) => r._measurement == "bmkg_weather")
          |> filter(fn: (r) => r._field == "temperature" or r._field == "humidity" or r._field == "weather_code")
          |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
          |> keep(columns: ["_time", "temperature", "humidity", "weather_code"])
          |> sort(columns: ["_time"])
        '''
        
        try:
            results = self.query_api.query_data_frame(query=query)
            
            if results.empty:
                logger.warning("Tidak ada data cuaca eksternal ditemukan")
                return pd.DataFrame()
            
            df = results.copy()
            if '_time' in df.columns:
                df['_time'] = pd.to_datetime(df['_time'])
                df = df.rename(columns={'_time': 'timestamp'})
            
            # Rename columns to avoid confusion with indoor data
            df = df.rename(columns={
                'temperature': 'outdoor_temp',
                'humidity': 'outdoor_humidity'
            })
            
            logger.info(f"Data cuaca eksternal terkumpul: {len(df)} records")
            return df
            
        except Exception as e:
            logger.warning(f"Gagal mengambil data cuaca eksternal: {e}")
            return pd.DataFrame()
    
    async def merge_with_external_data(
        self, 
        indoor_df: pd.DataFrame, 
        outdoor_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Menggabungkan data indoor dengan data cuaca eksternal
        
        Args:
            indoor_df (pd.DataFrame): Data sensor indoor
            outdoor_df (pd.DataFrame): Data cuaca eksternal
            
        Returns:
            pd.DataFrame: Combined dataset
        """
        if outdoor_df.empty:
            return indoor_df
        
        # Merge based on timestamp (nearest time match)
        indoor_df['timestamp_rounded'] = indoor_df['timestamp'].dt.round('H')
        outdoor_df['timestamp_rounded'] = outdoor_df['timestamp'].dt.round('H')
        
        merged_df = pd.merge_asof(
            indoor_df.sort_values('timestamp_rounded'),
            outdoor_df[['timestamp_rounded', 'outdoor_temp', 'outdoor_humidity', 'weather_code']].sort_values('timestamp_rounded'),
            on='timestamp_rounded',
            direction='nearest'
        )
        
        # Calculate temperature and humidity differences
        merged_df['temp_diff_indoor_outdoor'] = merged_df['temperature'] - merged_df['outdoor_temp']
        merged_df['humidity_diff_indoor_outdoor'] = merged_df['humidity'] - merged_df['outdoor_humidity']
        
        # Drop the rounded timestamp column
        merged_df = merged_df.drop('timestamp_rounded', axis=1)
        
        logger.info(f"Data indoor dan outdoor berhasil digabungkan: {len(merged_df)} records")
        return merged_df
    
    async def save_training_data(
        self, 
        features: pd.DataFrame, 
        targets: pd.DataFrame,
        filepath: str = "training_data.csv"
    ) -> bool:
        """
        Menyimpan data training ke file CSV
        
        Args:
            features (pd.DataFrame): Features data
            targets (pd.DataFrame): Target data
            filepath (str): Path file untuk menyimpan
            
        Returns:
            bool: True jika berhasil disimpan
        """
        try:
            # Combine features and targets
            combined_data = pd.merge(features, targets, on='timestamp')
            combined_data.to_csv(filepath, index=False)
            
            logger.info(f"Data training berhasil disimpan ke {filepath}")
            logger.info(f"Total samples: {len(combined_data)}")
            logger.info(f"Features: {len(features.columns) - 1}")  # minus timestamp
            logger.info(f"Targets: {len(targets.columns) - 1}")    # minus timestamp
            
            return True
            
        except Exception as e:
            logger.error(f"Gagal menyimpan data training: {e}")
            return False


# Factory function untuk membuat collector
def create_training_data_collector(bucket: str = "sensor_data_primary") -> TrainingDataCollector:
    """
    Factory function untuk membuat TrainingDataCollector
    
    Args:
        bucket (str): Nama bucket InfluxDB
        
    Returns:
        TrainingDataCollector: Instance collector
    """
    return TrainingDataCollector(bucket)
