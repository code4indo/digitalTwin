# routes/ml_routes.py
from fastapi import APIRouter, Query, Depends, HTTPException, BackgroundTasks
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import os
import json
import logging

from utils.auth import get_api_key
from services.ml_training_service import create_training_data_collector

router = APIRouter(prefix="/ml", tags=["machine_learning"])
logger = logging.getLogger(__name__)

@router.get("/training-data/collect")
async def collect_training_data(
    background_tasks: BackgroundTasks,
    days_back: int = Query(30, description="Jumlah hari ke belakang untuk mengumpulkan data"),
    location_filter: Optional[str] = Query(None, description="Filter berdasarkan lokasi"),
    device_filter: Optional[str] = Query(None, description="Filter berdasarkan device_id"),
    include_external: bool = Query(True, description="Sertakan data cuaca eksternal"),
    save_to_file: bool = Query(True, description="Simpan data ke file CSV"),
    api_key: str = Depends(get_api_key)
):
    """
    Mengumpulkan data training dari InfluxDB untuk model machine learning
    """
    try:
        collector = create_training_data_collector()
        
        # Collect historical sensor data
        indoor_data = await collector.collect_historical_data(
            days_back=days_back,
            location_filter=location_filter,
            device_filter=device_filter
        )
        
        if indoor_data.empty:
            raise HTTPException(status_code=404, detail="Tidak ada data historis ditemukan")
        
        # Merge with external weather data if requested
        final_data = indoor_data
        if include_external:
            external_data = await collector.get_external_weather_data(days_back=days_back)
            if not external_data.empty:
                final_data = await collector.merge_with_external_data(indoor_data, external_data)
        
        # Prepare training features and targets
        features, targets = await collector.prepare_training_features(final_data)
        
        # Save to file if requested
        if save_to_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"training_data_{timestamp}.csv"
            filepath = os.path.join("/app/data", filename)  # Assuming /app/data directory in container
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            background_tasks.add_task(
                collector.save_training_data, 
                features, 
                targets, 
                filepath
            )
        
        return {
            "status": "success",
            "message": "Data training berhasil dikumpulkan",
            "data_info": {
                "total_samples": len(features),
                "feature_count": len(features.columns) - 1,  # minus timestamp
                "target_count": len(targets.columns) - 1,    # minus timestamp
                "date_range": {
                    "start": features['timestamp'].min().isoformat(),
                    "end": features['timestamp'].max().isoformat()
                },
                "locations": list(final_data['location'].unique()) if 'location' in final_data.columns else [],
                "devices": list(final_data['device_id'].unique()) if 'device_id' in final_data.columns else [],
                "external_data_included": include_external and not external_data.empty if include_external else False
            },
            "preview": {
                "features_sample": features.head(5).to_dict('records'),
                "targets_sample": targets.head(5).to_dict('records')
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error mengumpulkan data training: {str(e)}")

@router.get("/training-data/stats")
async def get_training_data_stats(
    days_back: int = Query(30, description="Jumlah hari ke belakang untuk analisis"),
    api_key: str = Depends(get_api_key)
):
    """
    Mendapatkan statistik data yang tersedia untuk training
    """
    try:
        collector = create_training_data_collector()
        
        # Get basic data statistics
        data = await collector.collect_historical_data(days_back=days_back)
        
        if data.empty:
            return {
                "status": "no_data",
                "message": "Tidak ada data tersedia",
                "stats": {}
            }
        
        stats = {
            "total_records": len(data),
            "date_range": {
                "start": data['timestamp'].min().isoformat(),
                "end": data['timestamp'].max().isoformat()
            },
            "locations": list(data['location'].unique()) if 'location' in data.columns else [],
            "devices": list(data['device_id'].unique()) if 'device_id' in data.columns else [],
            "temperature_stats": {
                "mean": float(data['temperature'].mean()),
                "min": float(data['temperature'].min()),
                "max": float(data['temperature'].max()),
                "std": float(data['temperature'].std())
            },
            "humidity_stats": {
                "mean": float(data['humidity'].mean()),
                "min": float(data['humidity'].min()),
                "max": float(data['humidity'].max()),
                "std": float(data['humidity'].std())
            },
            "data_quality": {
                "missing_temperature": int(data['temperature'].isna().sum()),
                "missing_humidity": int(data['humidity'].isna().sum()),
                "duplicate_records": int(data.duplicated().sum()),
                "completeness_percentage": round((1 - data.isna().any(axis=1).sum() / len(data)) * 100, 2)
            }
        }
        
        return {
            "status": "success",
            "stats": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error mendapatkan statistik data: {str(e)}")

@router.post("/model/train")
async def train_model(
    background_tasks: BackgroundTasks,
    model_type: str = Query("random_forest", description="Jenis model ML (linear_regression, ridge_regression, lasso_regression, random_forest, gradient_boosting)"),
    days_back: int = Query(30, description="Jumlah hari data untuk training"),
    test_size: float = Query(0.2, description="Proporsi data untuk testing"),
    validation_size: float = Query(0.1, description="Proporsi data untuk validasi"),
    location_filter: Optional[str] = Query(None, description="Filter lokasi untuk training"),
    device_filter: Optional[str] = Query(None, description="Filter device untuk training"),
    scale_features: bool = Query(True, description="Apakah melakukan feature scaling"),
    save_model: bool = Query(True, description="Simpan model setelah training"),
    api_key: str = Depends(get_api_key)
):
    """
    Melatih model machine learning untuk prediksi suhu dan kelembapan
    """
    try:
        # Import trainer (lazy import to avoid sklearn dependency issues)
        try:
            from services.ml_model_trainer import create_model_trainer
        except ImportError as e:
            return {
                "status": "error",
                "message": "Machine learning dependencies tidak tersedia",
                "error": str(e),
                "solution": "Install sklearn, joblib: pip install scikit-learn joblib"
            }
        
        trainer = create_model_trainer()
        
        # Prepare training data
        training_data = await trainer.prepare_training_data(
            days_back=days_back,
            test_size=test_size,
            validation_size=validation_size,
            location_filter=location_filter,
            device_filter=device_filter
        )
        
        # Train model
        training_info = trainer.train_model(
            model_name=model_type,
            X_train=training_data['X_train'],
            y_train=training_data['y_train'],
            X_val=training_data['X_val'],
            y_val=training_data['y_val'],
            scale_features=scale_features
        )
        
        # Evaluate model on test set
        evaluation_info = trainer.evaluate_model(
            model_name=model_type,
            X_test=training_data['X_test'],
            y_test=training_data['y_test'],
            timestamps_test=training_data['timestamps_test']
        )
        
        # Save model if requested
        model_path = None
        if save_model:
            try:
                model_path = trainer.save_model(model_type)
            except Exception as e:
                logger.warning(f"Gagal menyimpan model: {e}")
        
        return {
            "status": "success",
            "message": f"Model {model_type} berhasil dilatih",
            "training_info": training_info,
            "evaluation_info": evaluation_info,
            "model_saved": model_path is not None,
            "model_path": model_path,
            "data_info": {
                "training_samples": len(training_data['X_train']),
                "validation_samples": len(training_data['X_val']),
                "test_samples": len(training_data['X_test']),
                "features_count": len(training_data['feature_names']),
                "targets_count": len(training_data['target_names']),
                "feature_names": training_data['feature_names'],
                "target_names": training_data['target_names']
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error training model: {e}")
        raise HTTPException(status_code=500, detail=f"Error training model: {str(e)}")

@router.get("/model/compare")
async def compare_models(
    days_back: int = Query(7, description="Jumlah hari data untuk evaluasi"),
    api_key: str = Depends(get_api_key)
):
    """
    Membandingkan performa semua model yang tersedia
    """
    try:
        # Import trainer
        try:
            from services.ml_model_trainer import create_model_trainer
        except ImportError:
            return {
                "status": "error",
                "message": "Machine learning dependencies tidak tersedia"
            }
        
        trainer = create_model_trainer()
        
        # Train multiple models for comparison
        model_types = ['linear_regression', 'ridge_regression', 'random_forest', 'gradient_boosting']
        comparison_results = {}
        
        # Prepare test data
        training_data = await trainer.prepare_training_data(days_back=days_back)
        
        for model_type in model_types:
            try:
                # Quick training for comparison
                training_info = trainer.train_model(
                    model_name=model_type,
                    X_train=training_data['X_train'],
                    y_train=training_data['y_train'],
                    X_val=training_data['X_val'],
                    y_val=training_data['y_val']
                )
                
                evaluation_info = trainer.evaluate_model(
                    model_name=model_type,
                    X_test=training_data['X_test'],
                    y_test=training_data['y_test']
                )
                
                comparison_results[model_type] = {
                    "training_metrics": training_info['train_metrics'],
                    "validation_metrics": training_info['val_metrics'],
                    "test_metrics": evaluation_info['test_metrics'],
                    "training_time": training_info['training_time']
                }
                
            except Exception as e:
                comparison_results[model_type] = {
                    "error": str(e),
                    "status": "failed"
                }
        
        # Find best model
        successful_models = {k: v for k, v in comparison_results.items() if 'error' not in v}
        best_model = None
        best_rmse = float('inf')
        
        if successful_models:
            for model_name, metrics in successful_models.items():
                test_rmse = metrics['test_metrics'].get('rmse', float('inf'))
                if test_rmse < best_rmse:
                    best_rmse = test_rmse
                    best_model = model_name
        
        return {
            "status": "success",
            "comparison_results": comparison_results,
            "best_model": best_model,
            "best_test_rmse": best_rmse,
            "data_info": {
                "training_samples": len(training_data['X_train']),
                "test_samples": len(training_data['X_test']),
                "features_count": len(training_data['feature_names'])
            },
            "compared_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error comparing models: {e}")
        raise HTTPException(status_code=500, detail=f"Error comparing models: {str(e)}")

@router.get("/model/list")
async def list_saved_models(
    api_key: str = Depends(get_api_key)
):
    """
    Mendapatkan daftar model yang sudah disimpan
    """
    try:
        models_dir = "/app/models"
        
        if not os.path.exists(models_dir):
            return {
                "status": "success",
                "models": [],
                "message": "Direktori models belum ada"
            }
        
        model_files = []
        for filename in os.listdir(models_dir):
            if filename.endswith('.joblib'):
                filepath = os.path.join(models_dir, filename)
                metadata_path = filepath.replace('.joblib', '_metadata.json')
                
                file_info = {
                    "filename": filename,
                    "filepath": filepath,
                    "size": os.path.getsize(filepath),
                    "created_at": datetime.fromtimestamp(os.path.getctime(filepath)).isoformat(),
                    "modified_at": datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                }
                
                # Read metadata if available
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, 'r') as f:
                            metadata = json.load(f)
                        file_info.update(metadata)
                    except Exception as e:
                        file_info["metadata_error"] = str(e)
                
                model_files.append(file_info)
        
        # Sort by creation time (newest first)
        model_files.sort(key=lambda x: x['created_at'], reverse=True)
        
        return {
            "status": "success",
            "models": model_files,
            "models_count": len(model_files)
        }
        
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing models: {str(e)}")

@router.post("/model/predict")
async def predict_with_model(
    model_name: str = Query(..., description="Nama model untuk prediksi"),
    hours_ahead: int = Query(1, description="Berapa jam ke depan untuk prediksi"),
    location: Optional[str] = Query(None, description="Lokasi untuk prediksi"),
    device: Optional[str] = Query(None, description="Device untuk prediksi"),
    api_key: str = Depends(get_api_key)
):
    """
    Membuat prediksi menggunakan model yang sudah dilatih
    """
    try:
        # Import trainer
        try:
            from services.ml_model_trainer import create_model_trainer
        except ImportError:
            return {
                "status": "error",
                "message": "Machine learning dependencies tidak tersedia"
            }
        
        trainer = create_model_trainer()
        
        # Get latest data for prediction
        collector = create_training_data_collector()
        recent_data = await collector.collect_historical_data(
            days_back=1,  # Last 24 hours
            location_filter=location,
            device_filter=device
        )
        
        if recent_data.empty:
            raise HTTPException(status_code=404, detail="Tidak ada data terbaru untuk prediksi")
        
        # Prepare features from latest data
        features, _ = await collector.prepare_training_features(recent_data)
        
        if len(features) == 0:
            raise HTTPException(status_code=404, detail="Tidak cukup data untuk membuat prediksi")
        
        # Use the latest data point
        latest_features = features.iloc[-1:].drop('timestamp', axis=1)
        
        # Load model if not in memory
        if model_name not in trainer.models:
            # Try to find and load the model
            models_dir = "/app/models"
            model_files = [f for f in os.listdir(models_dir) if f.startswith(model_name) and f.endswith('.joblib')]
            
            if not model_files:
                raise HTTPException(status_code=404, detail=f"Model {model_name} tidak ditemukan")
            
            # Load the latest model file
            latest_model_file = sorted(model_files)[-1]
            model_path = os.path.join(models_dir, latest_model_file)
            trainer.load_model(model_path)
        
        # Make prediction
        model = trainer.models[model_name]
        scaler = trainer.scalers.get(model_name)
        
        if scaler is not None:
            features_scaled = scaler.transform(latest_features)
        else:
            features_scaled = latest_features.values
        
        prediction = model.predict(features_scaled)
        
        # Format prediction result
        current_time = datetime.now()
        prediction_time = current_time + timedelta(hours=hours_ahead)
        
        result = {
            "status": "success",
            "model_name": model_name,
            "prediction_time": prediction_time.isoformat(),
            "hours_ahead": hours_ahead,
            "predictions": {
                "temperature": float(prediction[0][0]),
                "humidity": float(prediction[0][1])
            },
            "current_conditions": {
                "temperature": float(recent_data['temperature'].iloc[-1]),
                "humidity": float(recent_data['humidity'].iloc[-1]),
                "timestamp": recent_data['timestamp'].iloc[-1].isoformat()
            },
            "location": location,
            "device": device,
            "predicted_at": current_time.isoformat()
        }
        
        # Add confidence estimation (simplified)
        result["confidence"] = {
            "temperature": 0.85,  # Placeholder - calculate based on model performance
            "humidity": 0.80
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error making prediction: {e}")
        raise HTTPException(status_code=500, detail=f"Error making prediction: {str(e)}")

@router.get("/data/sample")
async def get_sample_data(
    limit: int = Query(100, description="Jumlah sample data"),
    api_key: str = Depends(get_api_key)
):
    """
    Mendapatkan sample data untuk testing dan development
    """
    try:
        collector = create_training_data_collector()
        
        # Get recent data
        data = await collector.collect_historical_data(days_back=7)
        
        if data.empty:
            return {
                "status": "no_data",
                "message": "Tidak ada data tersedia",
                "sample": []
            }
        
        # Get sample
        sample_data = data.tail(limit).to_dict('records')
        
        return {
            "status": "success",
            "total_available": len(data),
            "sample_size": len(sample_data),
            "sample": sample_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error mendapatkan sample data: {str(e)}")
