"""
Routes untuk AI-powered insights menggunakan Gemini
Menyediakan wawasan cerdas tentang kondisi iklim mikro dan preservasi arsip
"""

from fastapi import APIRouter, Depends, Query, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional
import logging

from services.gemini_service import gemini_service
from services.trend_service import get_hourly_trend_data, get_daily_trend_data, get_monthly_trend_data
from utils.auth import get_api_key

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/insights", tags=["ai_insights"])

@router.get("/climate-analysis", summary="Analisis insight klimat menggunakan AI Gemini",
            response_model=Dict[str, Any])
async def get_climate_insights(
    parameter: str = Query("temperature", description="Parameter: 'temperature' atau 'humidity'"),
    period: str = Query("day", description="Periode analisis: 'day', 'week', atau 'month'"),
    location: Optional[str] = Query("all", description="Lokasi spesifik atau 'all'"),
    api_key: str = Depends(get_api_key)
):
    """
    Endpoint untuk mendapatkan insights AI tentang kondisi klimat mikro.
    Menganalisis data tren dan memberikan wawasan untuk preservasi arsip.
    """
    try:
        logger.info(f"Generating insights for {parameter} - {period} - {location}")
        
        # Validasi parameter
        if parameter not in ["temperature", "humidity"]:
            raise HTTPException(
                status_code=400,
                detail="Parameter harus 'temperature' atau 'humidity'"
            )
        
        if period not in ["day", "week", "month"]:
            raise HTTPException(
                status_code=400,
                detail="Period harus 'day', 'week', atau 'month'"
            )
        
        # Ambil data tren berdasarkan periode
        if period == "day":
            trend_data = await get_hourly_trend_data(parameter, location, hours=24)
        elif period == "week":
            trend_data = await get_daily_trend_data(parameter, location, days=7)
        else:  # month
            trend_data = await get_monthly_trend_data(parameter, location, days=30)
        
        # Generate insights menggunakan Gemini AI
        insights = await gemini_service.generate_climate_insights(
            trend_data=trend_data,
            parameter=parameter,
            location=location or "all"
        )
        
        return {
            "success": True,
            "parameter": parameter,
            "period": period,
            "location": location or "all",
            "trend_summary": {
                "data_points": trend_data.get("data_points", 0),
                "analysis": trend_data.get("analysis", {}),
                "period_analyzed": trend_data.get("period", period)
            },
            "insights": insights.get("insights", {}),
            "ai_confidence": insights.get("insights", {}).get("confidence_level", "unknown"),
            "generated_at": insights.get("insights", {}).get("generated_at"),
            "data_source": insights.get("insights", {}).get("data_source", "unknown")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating climate insights: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error dalam generate insights: {str(e)}"
        )

@router.get("/preservation-risk", summary="Analisis risiko preservasi arsip",
            response_model=Dict[str, Any])
async def get_preservation_risk_analysis(
    location: Optional[str] = Query("all", description="Lokasi spesifik atau 'all'"),
    api_key: str = Depends(get_api_key)
):
    """
    Endpoint untuk analisis komprehensif risiko preservasi arsip
    berdasarkan kondisi suhu dan kelembapan.
    """
    try:
        logger.info(f"Generating preservation risk analysis for location: {location}")
        
        # Ambil data tren untuk temperature dan humidity
        temp_data = await get_daily_trend_data("temperature", location, days=7)
        humidity_data = await get_daily_trend_data("humidity", location, days=7)
        
        # Generate insights untuk kedua parameter
        temp_insights = await gemini_service.generate_climate_insights(
            trend_data=temp_data,
            parameter="temperature",
            location=location or "all"
        )
        
        humidity_insights = await gemini_service.generate_climate_insights(
            trend_data=humidity_data,
            parameter="humidity",
            location=location or "all"
        )
        
        # Kombinasi analisis risiko
        combined_risk = _calculate_combined_preservation_risk(
            temp_insights.get("insights", {}),
            humidity_insights.get("insights", {})
        )
        
        return {
            "success": True,
            "location": location or "all",
            "analysis_period": "7_days",
            "temperature_analysis": temp_insights.get("insights", {}),
            "humidity_analysis": humidity_insights.get("insights", {}),
            "combined_risk_assessment": combined_risk,
            "overall_recommendation": _generate_overall_recommendation(combined_risk),
            "generated_at": temp_insights.get("insights", {}).get("generated_at")
        }
        
    except Exception as e:
        logger.error(f"Error in preservation risk analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error dalam analisis risiko preservasi: {str(e)}"
        )

@router.get("/recommendations", summary="Rekomendasi aksi berdasarkan AI insights",
            response_model=Dict[str, Any])
async def get_actionable_recommendations(
    parameter: str = Query("temperature", description="Parameter: 'temperature' atau 'humidity'"),
    location: Optional[str] = Query("all", description="Lokasi spesifik atau 'all'"),
    api_key: str = Depends(get_api_key)
):
    """
    Endpoint untuk mendapatkan rekomendasi aksi yang dapat dilakukan
    berdasarkan analisis AI kondisi klimat.
    """
    try:
        # Ambil data tren terbaru
        trend_data = await get_hourly_trend_data(parameter, location, hours=24)
        
        # Generate insights
        insights = await gemini_service.generate_climate_insights(
            trend_data=trend_data,
            parameter=parameter,
            location=location or "all"
        )
        
        insights_data = insights.get("insights", {})
        
        # Format rekomendasi untuk aksi
        recommendations = {
            "immediate_actions": [],
            "short_term_actions": [],
            "long_term_actions": [],
            "monitoring_actions": []
        }
        
        # Kategorisasi rekomendasi berdasarkan prioritas
        priority = insights_data.get("prioritas_tindakan", "monitoring")
        actions = insights_data.get("rekomendasi_aksi", [])
        
        if priority == "immediate":
            recommendations["immediate_actions"] = actions[:2] if len(actions) >= 2 else actions
            recommendations["short_term_actions"] = actions[2:] if len(actions) > 2 else []
        elif priority == "urgent":
            recommendations["short_term_actions"] = actions[:2] if len(actions) >= 2 else actions
            recommendations["long_term_actions"] = actions[2:] if len(actions) > 2 else []
        else:
            recommendations["monitoring_actions"] = actions
        
        # Tambahkan rekomendasi standar monitoring
        recommendations["monitoring_actions"].extend([
            "Catat pembacaan sensor secara berkala",
            "Review trend data mingguan",
            "Dokumentasikan perubahan kondisi signifikan"
        ])
        
        return {
            "success": True,
            "parameter": parameter,
            "location": location or "all",
            "risk_level": insights_data.get("tingkat_risiko", "unknown"),
            "priority_level": priority,
            "status": insights_data.get("status_kondisi", "unknown"),
            "recommendations": recommendations,
            "impact_assessment": insights_data.get("dampak_preservasi", ""),
            "confidence": insights_data.get("confidence_level", "unknown"),
            "generated_at": insights_data.get("generated_at")
        }
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error dalam generate rekomendasi: {str(e)}"
        )

def _calculate_combined_preservation_risk(temp_insights: Dict[str, Any], humidity_insights: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate combined preservation risk dari temperature dan humidity analysis"""
    
    temp_risk = temp_insights.get("tingkat_risiko", "rendah")
    humidity_risk = humidity_insights.get("tingkat_risiko", "rendah")
    
    # Risk level mapping
    risk_levels = {"rendah": 1, "sedang": 2, "tinggi": 3, "kritis": 4}
    temp_score = risk_levels.get(temp_risk, 1)
    humidity_score = risk_levels.get(humidity_risk, 1)
    
    # Calculate combined risk (weighted average, humidity slightly more important)
    combined_score = (temp_score * 0.4 + humidity_score * 0.6)
    
    if combined_score >= 3.5:
        combined_risk = "kritis"
        severity = "Risiko kerusakan arsip sangat tinggi"
    elif combined_score >= 2.5:
        combined_risk = "tinggi"
        severity = "Risiko kerusakan arsip tinggi"
    elif combined_score >= 1.5:
        combined_risk = "sedang"
        severity = "Risiko kerusakan arsip moderat"
    else:
        combined_risk = "rendah"
        severity = "Risiko kerusakan arsip minimal"
    
    return {
        "overall_risk_level": combined_risk,
        "risk_score": round(combined_score, 2),
        "severity_description": severity,
        "primary_concern": "humidity" if humidity_score > temp_score else "temperature",
        "contributing_factors": {
            "temperature_risk": temp_risk,
            "humidity_risk": humidity_risk,
            "temperature_score": temp_score,
            "humidity_score": humidity_score
        }
    }

def _generate_overall_recommendation(combined_risk: Dict[str, Any]) -> Dict[str, Any]:
    """Generate overall recommendation berdasarkan combined risk assessment"""
    
    risk_level = combined_risk.get("overall_risk_level", "rendah")
    primary_concern = combined_risk.get("primary_concern", "temperature")
    
    if risk_level == "kritis":
        return {
            "urgency": "immediate",
            "action_required": "Tindakan darurat diperlukan",
            "focus_area": f"Prioritas utama: stabilisasi {primary_concern}",
            "timeline": "Dalam 24 jam",
            "escalation": "Hubungi tim maintenance segera"
        }
    elif risk_level == "tinggi":
        return {
            "urgency": "urgent",
            "action_required": "Tindakan perbaikan segera",
            "focus_area": f"Fokus pada optimisasi {primary_concern}",
            "timeline": "Dalam 48-72 jam",
            "escalation": "Koordinasi dengan tim operasional"
        }
    elif risk_level == "sedang":
        return {
            "urgency": "scheduled",
            "action_required": "Perencanaan perbaikan",
            "focus_area": f"Monitor dan sesuaikan {primary_concern}",
            "timeline": "Dalam 1 minggu",
            "escalation": "Review rutin dengan supervisor"
        }
    else:
        return {
            "urgency": "monitoring",
            "action_required": "Monitoring berkelanjutan",
            "focus_area": "Pertahankan kondisi optimal",
            "timeline": "Review bulanan",
            "escalation": "Laporan rutin"
        }
