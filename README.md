# TiDB vs PostgreSQL: Eksperimen Pendahuluan 100.000 Event

Eksperimen pendahuluan membandingkan TiDB v8.5.2 (query melalui TiFlash) dan PostgreSQL 16.15 pada replay 100.000 event FHVHV tanggal 1 Januari 2025. Ada 18 konfigurasi: dua DBMS × tiga rasio replay (`1:60`, `1:288`, `1:1440`) × tiga jumlah klien query (`1`, `4`, `8`). Semua konfigurasi selesai dengan target 100.000 baris/ID unik dan tanpa query gagal.

| DBMS | Konfigurasi berhasil | Rentang median latensi query |
|---|---:|---:|
| TiDB + TiFlash | 9/9 | 45,677–180,252 ms |
| PostgreSQL | 9/9 | 124,168–484,833 ms |

TiDB mencatat median latensi lebih rendah pada kesembilan pasangan konfigurasi yang diuji. Hasil bersifat deskriptif: setiap konfigurasi dijalankan sekali dan batas sumber daya kedua sistem berbeda. Eksperimen ini **terpisah dari eksperimen formal berskala lebih besar**.

## Isi repositori

- `artifacts/replay-inputs/20250101_event_datetime_sample100k/`: input TSV, manifest pemilihan sampel sistematis, dan checksum SHA-256.
- `artifacts/runs/`: 18 direktori run valid, termasuk ringkasan metrik dan log pendukung yang tersedia pada salinan lokal. Nama run mengikuti waktu, DBMS, rasio replay, serta jumlah klien. Pilot TiDB `c=1440,k=1` adalah satu dari 18 run, bukan run tambahan.
- `scripts/verify_results.py`: pemeriksaan ulang checksum input, matriks konfigurasi, kelengkapan target, dan status hasil dengan pustaka standar Python.

Sumber dataset: [NYC TLC, High Volume For-Hire Vehicle Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page). Penggunaan data tetap mengikuti ketentuan sumber aslinya.

## Verifikasi lokal

Jalankan dengan Python yang mendukung sintaks `str | None` (Python 3.10 atau lebih baru); tidak memerlukan paket tambahan:

```powershell
python scripts/verify_results.py
```

Skrip ini **hanya memverifikasi artefak yang diunggah**, bukan menjalankan ulang database atau mereproduksi keseluruhan proses eksperimen. Runner matriks 100k asli tidak terdapat pada salinan folder sumber yang diunggah; artefak diagnosis, skrip lama, dan konfigurasi mesin tidak dipublikasikan di sini.

Penulis repositori: **Aryasatya Widyatna Akbar**.
