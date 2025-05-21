# Menggunakan image Python resmi sebagai basis
FROM python:3.10-slim

# Menginstal paket sistem yang diperlukan, termasuk iputils-ping untuk perintah ping
RUN apt-get update && apt-get install -y iputils-ping && rm -rf /var/lib/apt/lists/*

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

# Menyalin semua file Python yang dibutuhkan ke direktori kerja
COPY . /app/

# Create an empty __init__.py file to make the directory a Python package
RUN touch /app/__init__.py

# Default command bisa diberikan di docker-compose
CMD ["python", "bmkg_data_collector.py"]
