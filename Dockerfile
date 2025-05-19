# Menggunakan image Python resmi sebagai basis
FROM python:3.10-slim

# Menetapkan direktori kerja di dalam kontainer
WORKDIR /app

# Menyalin file manajemen dependensi (pyproject.toml dan poetry.lock)
COPY pyproject.toml poetry.lock* /app/

# Menginstal Poetry dan dependensi proyek
# Memperbarui pip, menginstal poetry, dan menggunakan --without dev
# virtualenvs.create false agar poetry menginstal paket di environment sistem image
RUN pip install --upgrade pip \
    && pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --without dev --no-interaction --no-ansi

# Menyalin skrip kolektor data BMKG ke direktori kerja
COPY bmkg_data_collector.py /app/

# Perintah untuk menjalankan aplikasi ketika kontainer dimulai
CMD ["python", "bmkg_data_collector.py"]
