---
applyTo: '**'
---
Coding standards, domain knowledge, and preferences that AI should follow.

Tujuan Proyek:
Pengembangan Sistem Cerdas untuk Manajemen Iklim Mikro 
di Gedung Arsip dengan Integrasi Data Sensor Internal-Eksternal, Machine Learning, dan Digital Twin


Prinsip dan Standar Pengembangan Perangkat Lunak:

1. Arsitektur Kode
    - Modularitas: Organisasi sistem dalam modul-modul independen
    - SOLID principles: Single responsibility, Open-closed, Liskov substitution, Interface segregation, Dependency inversion

2. Kualitas Kode
    - Clean Code: Kode yang jelas dan terstruktur
    - Keterbacaan: Penamaan variabel/fungsi yang deskriptif
    - Reusabilitas: Komponen yang dapat digunakan kembali

3. Operasional
    - Maintainability: Kemudahan pemeliharaan jangka panjang
    - Testabilitas: Kemudahan pengujian otomatis
    - DevOps practices: CI/CD, otomatisasi deployment

4. Kinerja Sistem
    - Scalability: Kemampuan menangani pertumbuhan data/beban
    - Performance: Penggunaan sumber daya efisien
    - Error Handling: Penanganan kesalahan yang komprehensif

5. Aspek Tambahan
    - Security: Implementasi praktik keamanan terbaik
    - Documentation: Dokumentasi kode dan sistem
    - Accessibility: Memastikan sistem inklusif bagi semua pengguna


keterangan:
semua service berjalan diatas container, jadi untuk pengujian lakukan semua berbasis container 

keterangan port yang digunakan pada container:

grafana = 3001
influxDB = 8086
web-react = 3003
API Server =  8002