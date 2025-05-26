import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- PENTING: st.set_page_config HARUS MENJADI PERINTAH STREAMLIT PERTAMA ---
st.set_page_config(layout="wide", page_title="E-commerce Sales Dashboard")
# Anda bisa menambahkan icon halaman, dll. di sini.

# Mengatur gaya visualisasi seaborn
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6) # Ukuran default untuk plot

# ==============================================================================
# --- BAGIAN 1, 2, 3: DATA LOADING, CLEANING, FEATURE ENGINEERING ---
# ==============================================================================

# Menggunakan cache agar data tidak di-load ulang setiap kali ada interaksi UI (lebih efisien).
@st.cache_data
def load_and_process_data():
    print("\n--- [DEBUG] Memulai load_and_process_data() ---")
    try:
        file_path = 'data.csv'
        print(f"--- [DEBUG] Mencoba membaca file: {file_path}")
        df_loaded = pd.read_csv(file_path, encoding='latin1')
        print(f"--- [DEBUG] File '{file_path}' berhasil dimuat.")

        # --- 2. Pembersihan Data (Data Cleaning) ---
        print("\n--- [DEBUG] Memulai Pembersihan Data ---")
        df_cleaned = df_loaded.copy()

        initial_rows_before_customerid = len(df_cleaned)
        df_cleaned.dropna(subset=['CustomerID'], inplace=True)
        print(f"--- [DEBUG] Baris CustomerID hilang dihapus: {initial_rows_before_customerid - len(df_cleaned)} baris")

        df_cleaned['InvoiceDate'] = pd.to_datetime(df_cleaned['InvoiceDate'])
        
        initial_rows_before_qty_price = len(df_cleaned)
        df_cleaned = df_cleaned[df_cleaned['Quantity'] > 0]
        df_cleaned = df_cleaned[df_cleaned['UnitPrice'] > 0]
        print(f"--- [DEBUG] Baris Quantity/UnitPrice <= 0 dihapus: {initial_rows_before_qty_price - len(df_cleaned)} baris")

        initial_rows_before_duplicates = len(df_cleaned)
        df_cleaned.drop_duplicates(inplace=True)
        print(f"--- [DEBUG] Duplikat dihapus: {initial_rows_before_duplicates - len(df_cleaned)} duplikat")

        df_cleaned['CustomerID'] = df_cleaned['CustomerID'].astype(str)

        print("\n--- [DEBUG] Pembersihan Data Selesai ---")

        # --- 3. Rekayasa Fitur (Feature Engineering) ---
        print("\n--- [DEBUG] Memulai Rekayasa Fitur ---")
        df_cleaned['TotalPrice'] = df_cleaned['Quantity'] * df_cleaned['UnitPrice']

        df_cleaned['Year'] = df_cleaned['InvoiceDate'].dt.year
        df_cleaned['Month'] = df_cleaned['InvoiceDate'].dt.month
        df_cleaned['Day'] = df_cleaned['InvoiceDate'].dt.day
        df_cleaned['DayOfWeek'] = df_cleaned['InvoiceDate'].dt.day_name()
        df_cleaned['Hour'] = df_cleaned['InvoiceDate'].dt.hour
        print("\n--- [DEBUG] Rekayasa Fitur Selesai ---")

        return df_cleaned, None # Mengembalikan DataFrame dan None (tidak ada error)

    except FileNotFoundError:
        print(f"--- [DEBUG ERROR] File not found: {file_path} ---")
        return pd.DataFrame(), "file_not_found" # Mengembalikan df kosong dan tipe error
    except UnicodeDecodeError as ude:
        print(f"--- [DEBUG ERROR] Encoding error: {ude} ---")
        return pd.DataFrame(), "encoding_error" # Mengembalikan df kosong dan tipe error
    except Exception as e:
        print(f"--- [DEBUG ERROR] General error during load/process: {e} ---")
        return pd.DataFrame(), "general_error" # Mengembalikan df kosong dan tipe error

# Panggil fungsi untuk memuat dan memproses data.
print("\n--- [DEBUG] Memanggil load_and_process_data() ---")
df, error_type = load_and_process_data()
print(f"--- [DEBUG] Tipe df setelah pemanggilan: {type(df)}")
print(f"--- [DEBUG] Apakah df kosong? {df.empty}")
print(f"--- [DEBUG] Tipe error setelah pemanggilan: {error_type}")

# Tangani error *setelah* st.set_page_config
if error_type == "file_not_found":
    st.error("Error: File 'data.csv' tidak ditemukan. Pastikan file berada di direktori yang sama dengan skrip Python Anda dan bernama 'data.csv'.")
    st.stop()
elif error_type == "encoding_error":
    st.error("Error encoding CSV. Coba encoding lain seperti 'ISO-8859-1' atau 'cp1252'.")
    st.stop()
elif error_type == "general_error":
    st.error(f"Error saat memuat atau memproses data. Detail: {error_type}") # Menampilkan detail error
    st.stop()
elif df.empty: # Jika tidak ada error spesifik tapi df kosong setelah pemrosesan
    st.warning("Tidak ada data yang berhasil dimuat atau diproses (DataFrame kosong). Dashboard mungkin tidak menampilkan data.")
    st.stop()

# ==============================================================================
# --- AKHIR BAGIAN DATA LOADING, CLEANING, FEATURE ENGINEERING ---
# ==============================================================================


# --- KODE STREAMLIT UI ---
st.title('Dashboard Analisis Kinerja Penjualan E-commerce') # st.title tidak perlu lagi di atas karena sudah di set_page_config

# Bagian Ringkasan
st.header('Ringkasan Penjualan Global')
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Pendapatan", "£{:,.2f}".format(df['TotalPrice'].sum()))
col2.metric("Total Transaksi", "{:,}".format(df['InvoiceNo'].nunique()))
col3.metric("Produk Terjual", "{:,}".format(df['Quantity'].sum()))
col4.metric("Pelanggan Unik", "{:,}".format(df['CustomerID'].nunique()))

st.markdown("---")

# Bagian Tren Penjualan Bulanan
st.header('Tren Penjualan Berdasarkan Waktu')
monthly_sales = df.groupby(['Year', 'Month'])['TotalPrice'].sum().reset_index()
if not monthly_sales.empty:
    monthly_sales['Date'] = pd.to_datetime(monthly_sales['Year'].astype(str) + '-' + monthly_sales['Month'].astype(str))
    fig_monthly, ax_monthly = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=monthly_sales, x='Date', y='TotalPrice', marker='o', ax=ax_monthly)
    ax_monthly.set_title('Tren Penjualan Bulanan')
    ax_monthly.set_xlabel('Tanggal')
    ax_monthly.set_ylabel('Total Penjualan (£)')
    ax_monthly.grid(True)
    st.pyplot(fig_monthly)
else:
    st.warning("Tidak ada data penjualan bulanan yang cukup untuk diplot setelah pembersihan.")


# Bagian Penjualan per Hari & Per Jam (gunakan dua kolom)
col_day, col_hour = st.columns(2)
with col_day:
    st.subheader('Penjualan per Hari dalam Seminggu')
    daily_sales = df.groupby('DayOfWeek')['TotalPrice'].sum().reindex([
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
    ])
    fig_daily, ax_daily = plt.subplots(figsize=(8, 5))
    sns.barplot(x=daily_sales.index, y=daily_sales.values, palette='viridis', ax=ax_daily)
    ax_daily.set_title('Total Penjualan per Hari')
    ax_daily.set_xlabel('Hari')
    ax_daily.set_ylabel('Total Penjualan (£)')
    st.pyplot(fig_daily)

with col_hour:
    st.subheader('Penjualan per Jam')
    hourly_sales = df.groupby('Hour')['TotalPrice'].sum()
    fig_hourly, ax_hourly = plt.subplots(figsize=(8, 5))
    sns.lineplot(x=hourly_sales.index, y=hourly_sales.values, marker='o', ax=ax_hourly)
    ax_hourly.set_title('Total Penjualan per Jam')
    ax_hourly.set_xlabel('Jam')
    ax_hourly.set_ylabel('Total Penjualan (£)')
    ax_hourly.set_xticks(range(24))
    ax_hourly.grid(True)
    st.pyplot(fig_hourly)

st.markdown("---")

# Bagian Performa Produk
st.header('Performa Produk')
top_10_products_rev = df.groupby('Description')['TotalPrice'].sum().nlargest(10).sort_values(ascending=False)
fig_prod, ax_prod = plt.subplots(figsize=(12, 7))
sns.barplot(x=top_10_products_rev.values, y=top_10_products_rev.index, palette='magma', ax=ax_prod)
ax_prod.set_title('Top 10 Produk Terlaris (berdasarkan Pendapatan)')
ax_prod.set_xlabel('Total Pendapatan (£)')
ax_prod.set_ylabel('Nama Produk')
st.pyplot(fig_prod)

st.markdown("---")

# Bagian Kesimpulan & Rekomendasi
st.header('Kesimpulan & Rekomendasi Bisnis')
st.write("""
Berdasarkan analisis data penjualan e-commerce, kami menemukan beberapa wawasan kunci:
- **Tren Penjualan:** Penjualan menunjukkan puncak di akhir tahun (sekitar November-Desember) dan cenderung lebih rendah di awal tahun. Hari Kamis adalah hari dengan penjualan tertinggi, dan penjualan aktif dari jam 10 pagi hingga 4 sore.
- **Performa Produk:** Beberapa produk seperti 'Paper Craft' dan 'JUMBO BAG' adalah kontributor utama pendapatan.
- **Analisis Pelanggan & Geografis:** Mayoritas pendapatan berasal dari Inggris, namun ada kontribusi signifikan dari negara-negara Eropa lainnya.

**Rekomendasi Bisnis:**
1.  **Optimalisasi Musiman:** Lakukan kampanye pemasaran dan promosi yang intensif, serta pastikan ketersediaan stok yang memadai menjelang akhir tahun (Oktober-Desember) untuk memaksimalkan puncak penjualan.
2.  **Fokus pada Produk Unggulan:** Promosikan lebih lanjut produk-produk terlaris melalui penempatan strategis di website, bundling produk, atau program loyalitas.
3.  **Strategi Waktu:** Manfaatkan data penjualan harian dan jam untuk menjadwalkan kampanye email atau promosi real-time.
4.  **Ekspansi Pasar Internasional:** Pertimbangkan strategi pemasaran yang ditargetkan untuk negara-negara Eropa lainnya.
5.  **Program Loyalitas Pelanggan:** Identifikasi pelanggan top dan berikan perlakuan khusus.
6.  **Manajemen Inventaris:** Gunakan data penjualan produk untuk mengoptimalkan inventaris.
""")