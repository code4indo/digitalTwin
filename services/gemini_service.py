"""
Service untuk integrasi dengan Google Gemini AI
Menganalisis data tren klimat dan memberikan wawasan untuk preservasi arsip
"""

import os
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import google.generativeai as genai
from fastapi import HTTPException

logger = logging.getLogger(__name__)

# Konfigurasi Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-1.5-flash"

class GeminiInsightService:
    """Service untuk analisis insight menggunakan Gemini AI"""
    
    def __init__(self):
        if not GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY tidak ditemukan. Fitur insight AI akan menggunakan fallback.")
            self.client = None
        else:
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                self.model = genai.GenerativeModel(GEMINI_MODEL)
                self.client = True
                logger.info("Gemini AI berhasil dikonfigurasi")
            except Exception as e:
                logger.error(f"Error konfigurasi Gemini AI: {str(e)}")
                self.client = None

    async def generate_climate_insights(
        self, 
        trend_data: Dict[str, Any], 
        parameter: str = "temperature",
        location: str = "all"
    ) -> Dict[str, Any]:
        """
        Generate insights berdasarkan data tren klimat
        
        Args:
            trend_data: Data tren dari InfluxDB
            parameter: Parameter yang dianalisis (temperature/humidity)
            location: Lokasi ruangan
            
        Returns:
            Dict berisi insights dan rekomendasi
        """
        try:
            if not self.client:
                return self._generate_fallback_insights(trend_data, parameter, location)
            
            # Prepare data summary untuk Gemini
            data_summary = self._prepare_data_summary(trend_data, parameter, location)
            
            # Generate prompt untuk Gemini
            prompt = self._create_analysis_prompt(data_summary, parameter)
            
            # Generate response dari Gemini
            response = self.model.generate_content(prompt)
            
            # Parse response menjadi structured insights
            insights = self._parse_gemini_response(response.text, trend_data, parameter)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return self._generate_fallback_insights(trend_data, parameter, location)

    def _prepare_data_summary(self, trend_data: Dict[str, Any], parameter: str, location: str) -> Dict[str, Any]:
        """Prepare summary data untuk Gemini analysis"""
        
        analysis = trend_data.get("analysis", {})
        statistics = analysis.get("statistics", {})
        
        return {
            "parameter": parameter,
            "location": location,
            "period": trend_data.get("period", "unknown"),
            "data_points": trend_data.get("data_points", 0),
            "current_values": trend_data.get("values", [])[-10:] if trend_data.get("values") else [],
            "statistics": {
                "mean": statistics.get("mean", 0),
                "min": statistics.get("min", 0),
                "max": statistics.get("max", 0),
                "std": statistics.get("std", 0),
                "volatility": analysis.get("volatility", 0)
            },
            "trend": {
                "direction": analysis.get("trend_direction", "unknown"),
                "slope": analysis.get("slope", 0),
                "correlation": analysis.get("correlation", 0)
            },
            "anomalies": analysis.get("anomalies", []),
            "timestamp": trend_data.get("last_updated", datetime.now().isoformat())
        }

    def _create_analysis_prompt(self, data_summary: Dict[str, Any], parameter: str) -> str:
        """Create comprehensive prompt untuk Gemini analysis"""
        
        parameter_info = {
            "temperature": {
                "unit": "°C",
                "optimal_range": "18-22°C",
                "critical_low": "15°C",
                "critical_high": "25°C",
                "archive_impact": "suhu tinggi mempercepat deteriorasi, suhu rendah dapat menyebabkan kondensasi"
            },
            "humidity": {
                "unit": "%",
                "optimal_range": "45-55%",
                "critical_low": "35%",
                "critical_high": "65%",
                "archive_impact": "kelembapan tinggi menyebabkan jamur dan bakteri, kelembapan rendah membuat dokumen rapuh"
            }
        }
        
        param_info = parameter_info.get(parameter, parameter_info["temperature"])
        stats = data_summary["statistics"]
        trend = data_summary["trend"]
        
        prompt = f"""
Anda adalah ahli preservasi arsip dan klimatologi. Analisis data {parameter} berikut untuk gedung arsip:

DATA KLIMAT:
- Parameter: {parameter} ({param_info['unit']})
- Periode: {data_summary['period']}
- Lokasi: {data_summary['location']}
- Jumlah data: {data_summary['data_points']} titik
- Rata-rata: {stats['mean']:.1f}{param_info['unit']}
- Minimum: {stats['min']:.1f}{param_info['unit']}
- Maksimum: {stats['max']:.1f}{param_info['unit']}
- Standar deviasi: {stats['std']:.1f}
- Volatilitas: {stats['volatility']:.1f}
- Tren: {trend['direction']} (slope: {trend['slope']:.4f})
- Korelasi: {trend['correlation']:.3f}
- Nilai terbaru: {data_summary['current_values']}

STANDAR PRESERVASI ARSIP:
- Rentang optimal: {param_info['optimal_range']}
- Batas kritis rendah: {param_info['critical_low']}
- Batas kritis tinggi: {param_info['critical_high']}
- Dampak: {param_info['archive_impact']}

Berikan analisis dalam format JSON dengan struktur:
{{
    "status_kondisi": "optimal|warning|critical",
    "tingkat_risiko": "rendah|sedang|tinggi|kritis",
    "ringkasan_kondisi": "ringkasan singkat kondisi saat ini",
    "dampak_preservasi": "analisis dampak terhadap preservasi arsip",
    "tren_prediksi": "prediksi tren kedepan berdasarkan data",
    "rekomendasi_aksi": [
        "rekomendasi 1",
        "rekomendasi 2", 
        "rekomendasi 3"
    ],
    "prioritas_tindakan": "immediate|urgent|scheduled|monitoring",
    "estimasi_dampak_jangka_panjang": "analisis dampak jangka panjang jika kondisi tidak diperbaiki",
    "confidence_level": "tinggi|sedang|rendah"
}}

Pastikan analisis berdasarkan standar internasional preservasi arsip (ISO 11799, ASHRAE, dll).
"""
        return prompt

    def _parse_gemini_response(self, response_text: str, trend_data: Dict[str, Any], parameter: str) -> Dict[str, Any]:
        """Parse response dari Gemini menjadi structured insights"""
        
        try:
            # Extract JSON dari response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                insights_data = json.loads(json_match.group())
            else:
                # Fallback jika parsing JSON gagal
                insights_data = self._extract_insights_fallback(response_text)
            
            # Tambahkan metadata
            insights_data.update({
                "generated_at": datetime.now().isoformat(),
                "data_source": "gemini_ai",
                "parameter_analyzed": parameter,
                "data_points_analyzed": trend_data.get("data_points", 0),
                "analysis_version": "1.0"
            })
            
            return {
                "success": True,
                "insights": insights_data,
                "raw_response": response_text[:500] + "..." if len(response_text) > 500 else response_text
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing Gemini JSON response: {str(e)}")
            return self._generate_fallback_insights(trend_data, parameter, "all")
        except Exception as e:
            logger.error(f"Error processing Gemini response: {str(e)}")
            return self._generate_fallback_insights(trend_data, parameter, "all")

    def _extract_insights_fallback(self, response_text: str) -> Dict[str, Any]:
        """Fallback method untuk extract insights dari response text"""
        
        # Simple text analysis untuk extract key information
        response_lower = response_text.lower()
        
        # Determine status based on keywords
        if any(word in response_lower for word in ["critical", "kritis", "bahaya", "urgent"]):
            status = "critical"
            risk_level = "kritis"
            priority = "immediate"
        elif any(word in response_lower for word in ["warning", "peringatan", "perhatian", "sedang"]):
            status = "warning"
            risk_level = "sedang"
            priority = "urgent"
        else:
            status = "optimal"
            risk_level = "rendah"
            priority = "monitoring"
        
        return {
            "status_kondisi": status,
            "tingkat_risiko": risk_level,
            "ringkasan_kondisi": "Analisis otomatis berdasarkan pattern response",
            "dampak_preservasi": "Analisis dampak memerlukan review manual",
            "tren_prediksi": "Tren memerlukan analisis lebih lanjut",
            "rekomendasi_aksi": ["Review kondisi manual", "Monitor parameter secara berkala"],
            "prioritas_tindakan": priority,
            "estimasi_dampak_jangka_panjang": "Memerlukan evaluasi expert",
            "confidence_level": "rendah"
        }

    def _generate_fallback_insights(self, trend_data: Dict[str, Any], parameter: str, location: str) -> Dict[str, Any]:
        """Generate fallback insights jika Gemini tidak tersedia"""
        
        analysis = trend_data.get("analysis", {})
        statistics = analysis.get("statistics", {})
        mean_value = statistics.get("mean", 0)
        volatility = analysis.get("volatility", 0)
        
        # Rule-based analysis untuk fallback
        if parameter == "temperature":
            if mean_value < 15 or mean_value > 25:
                status = "critical"
                risk_level = "tinggi"
            elif mean_value < 18 or mean_value > 22:
                status = "warning"
                risk_level = "sedang"
            else:
                status = "optimal"
                risk_level = "rendah"
        else:  # humidity
            if mean_value < 35 or mean_value > 65:
                status = "critical"
                risk_level = "tinggi"
            elif mean_value < 45 or mean_value > 55:
                status = "warning"
                risk_level = "sedang"
            else:
                status = "optimal"
                risk_level = "rendah"
        
        return {
            "success": True,
            "insights": {
                "status_kondisi": status,
                "tingkat_risiko": risk_level,
                "ringkasan_kondisi": f"Kondisi {parameter} saat ini {status} dengan rata-rata {mean_value:.1f}",
                "dampak_preservasi": f"Volatilitas {volatility:.1f} menunjukkan tingkat stabilitas kondisi",
                "tren_prediksi": f"Tren {analysis.get('trend_direction', 'stable')} berdasarkan data historis",
                "rekomendasi_aksi": [
                    "Monitor kondisi secara berkala",
                    "Periksa sistem HVAC jika nilai diluar optimal",
                    "Dokumentasikan perubahan signifikan"
                ],
                "prioritas_tindakan": "monitoring" if status == "optimal" else "urgent",
                "estimasi_dampak_jangka_panjang": "Memerlukan monitoring berkelanjutan",
                "confidence_level": "sedang",
                "generated_at": datetime.now().isoformat(),
                "data_source": "rule_based_fallback",
                "parameter_analyzed": parameter,
                "data_points_analyzed": trend_data.get("data_points", 0),
                "analysis_version": "1.0"
            },
            "raw_response": "Generated using rule-based fallback system"
        }

# Singleton instance
gemini_service = GeminiInsightService()
