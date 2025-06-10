# Panduan Mengatur Gemini API Key untuk AI Insights

## Status Saat Ini

Sistem AI Insights Digital Twin sudah dikonfigurasi dengan **rule-based fallback** yang berfungsi dengan baik. Untuk mengaktifkan **Gemini AI yang sesungguhnya**, Anda perlu mengatur API key Gemini.

## Cara Mendapatkan Gemini API Key

1. **Kunjungi Google AI Studio**: https://makersuite.google.com/app/apikey
2. **Login** dengan akun Google Anda
3. **Buat API key baru** dengan klik "Create API Key"
4. **Copy API key** yang dihasilkan

## Cara Mengatur API Key

### Opsi 1: Menggunakan Script Otomatis (Recommended)

```bash
./setup-gemini-api.sh
```

Script ini akan memandu Anda untuk:
- Memasukkan API key secara interaktif
- Mengatur file .env
- Restart container API

### Opsi 2: Manual via File .env

1. **Edit file .env**:
```bash
nano .env
```

2. **Tambahkan atau uncomment baris**:
```properties
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

3. **Restart container API**:
```bash
docker-compose restart api
```

### Opsi 3: Environment Variable

```bash
export GEMINI_API_KEY="your_actual_gemini_api_key_here"
docker-compose restart api
```

## Verifikasi Setup

### Test endpoint untuk memastikan AI berfungsi:

```bash
curl -X GET "http://localhost:8002/insights/climate-analysis?parameter=temperature&period=day&location=all" \
  -H "x-api-key: development_key_for_testing"
```

### Indikator yang menunjukkan Gemini AI aktif:
- `"data_source": "gemini_ai"` (bukan "rule_based_fallback")
- Insight yang lebih natural dan detail
- `"confidence_level"` yang lebih tinggi

## Fallback System

Jika API key tidak diatur atau ada masalah dengan Gemini AI:
- ✅ Sistem tetap berfungsi dengan rule-based insights
- ✅ Tidak ada error atau downtime
- ⚠️ Insights kurang natural dan detail

## Endpoint AI Insights

### 1. Climate Analysis
```bash
GET /insights/climate-analysis?parameter=temperature&period=day&location=all
```

### 2. Preservation Risk Assessment
```bash
GET /insights/preservation-risk?parameter=humidity&period=week&location=archive
```

### 3. Recommendations
```bash
GET /insights/recommendations?parameter=temperature&condition=high
```

## Troubleshooting

### Jika API key tidak bekerja:
1. Pastikan API key valid di Google AI Studio
2. Cek log container: `docker-compose logs api`
3. Pastikan tidak ada typo di .env file
4. Restart container setelah mengubah .env

### Jika masih menggunakan fallback:
1. Cek apakah GEMINI_API_KEY terset: `docker-compose exec api env | grep GEMINI`
2. Cek log untuk error messages
3. Verifikasi API key dengan test request langsung ke Gemini API

## File yang Terkait

- `.env` - Environment variables
- `docker-compose.yml` - Container configuration
- `services/gemini_service.py` - AI service implementation
- `routes/insights_routes.py` - API endpoints
- `setup-gemini-api.sh` - Setup script

## Keamanan

⚠️ **Jangan commit API key ke Git!**
- File `.env` sudah ada di `.gitignore`
- Gunakan environment variables di production
- Rotate API key secara berkala
