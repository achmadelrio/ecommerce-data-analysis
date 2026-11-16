# E-Commerce Public Data Analysis Dashboard ✨

Proyek ini merupakan hasil analisis data pada **E-Commerce Public Dataset** yang mencakup analisis performa kategori produk, tren pendapatan bulanan, dampak ketepatan waktu pengiriman terhadap skor ulasan pelanggan, serta segmentasi pelanggan menggunakan metode **RFM Analysis**.

## Struktur Direktori
- `dashboard/`: Berisi `dashboard.py` (aplikasi Streamlit) dan `main_data.csv` (dataset hasil pembersihan).
- `data/`: Berisi dataset mentah format `.csv` yang digunakan dalam analisis.
- `notebook.ipynb`: Jupyter Notebook yang berisi seluruh tahapan proses analisis data (*Data Wrangling*, *EDA*, *Visualization*, *RFM Analysis*, hingga *Conclusion*).
- `requirements.txt`: Daftar *library* Python yang dibutuhkan untuk menjalankan proyek.
- `url.txt`: Tautan menuju *dashboard* yang telah di-*deploy* di Streamlit Cloud.

## Cara Menjalankan Dashboard di Lokal
1. Pastikan Python dan seluruh *library* pada `requirements.txt` sudah terinstal:
   ```bash
   pip install -r requirements.txt