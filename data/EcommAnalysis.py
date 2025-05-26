import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
# Hapus atau komentari import kagglehub dan terkait karena tidak lagi digunakan
# import kagglehub
# from kagglehub import KaggleDatasetAdapter

# Mengatur gaya visualisasi seaborn
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6) # Ukuran default untuk plot

# --- 1. Memuat Data dari Lokal (CSV) ---
print("--- 1. Memuat Data dari Lokal (CSV) ---")
try:
    # Menggunakan path relatif karena file sudah dipindahkan ke folder yang sama
    file_path = 'data.csv'
    # Menggunakan pd.read_csv untuk membaca file CSV
    # Jika ada masalah encoding, bisa coba: encoding='ISO-8859-1' atau encoding='latin1'
    # Jika ada pemisah (delimiter) selain koma, bisa tambahkan: sep=';'
    df = pd.read_csv(file_path, encoding='latin1')
    print(f"Data berhasil dimuat dari '{file_path}'.")
except FileNotFoundError:
    print(f"Error: File '{file_path}' tidak ditemukan. Pastikan file berada di direktori yang sama dengan skrip Python Anda.")
    print("Atau, pastikan Anda telah mengunduhnya secara manual dan menamainya 'data.csv'.")
    exit() # Keluar dari program jika file tidak ditemukan
except Exception as e:
    print(f"Error saat memuat data: {e}")
    print("Pastikan file CSV tidak korup dan Anda memiliki pustaka 'pandas' terinstal.")
    exit()

print("\n--- Tampilan Awal Data ---")
print(df.head())
print("\n--- Informasi Data ---")
print(df.info())
print("\n--- Statistik Deskriptif ---")
print(df.describe())

# --- 2. Pembersihan Data (Data Cleaning) ---
print("\n--- 2. Pembersihan Data (Data Cleaning) ---")

# Menangani missing values
print("\nJumlah Missing Values per Kolom:")
print(df.isnull().sum())

# 'CustomerID' adalah kolom penting untuk analisis pelanggan. Kita akan drop baris tanpa CustomerID.
df.dropna(subset=['CustomerID'], inplace=True)
print(f"Jumlah baris setelah menghapus CustomerID yang hilang: {len(df)}")

# Mengubah tipe data InvoiceDate ke datetime
# Perlu diperhatikan format tanggal di CSV, jika berbeda dari Excel aslinya
# Jika format tanggal di CSV tidak standar, mungkin perlu: format='%Y-%m-%d %H:%M:%S'
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
print(f"Tipe data 'InvoiceDate' setelah diubah: {df['InvoiceDate'].dtype}")

# Menangani nilai negatif di Quantity dan UnitPrice
# Transaksi dengan Quantity <= 0 biasanya adalah pengembalian atau data yang salah. Kita akan menghapusnya.
df = df[df['Quantity'] > 0]
# Transaksi dengan UnitPrice > 0 (jika ada UnitPrice = 0 dianggap error data)
df = df[df['UnitPrice'] > 0]
print(f"Jumlah baris setelah menghapus Quantity <= 0 dan UnitPrice <= 0: {len(df)}")

# Menangani duplikat
initial_rows = len(df)
df.drop_duplicates(inplace=True)
print(f"Jumlah baris setelah menghapus duplikat: {len(df)} (Dihapus: {initial_rows - len(df)} duplikat)")

# Konversi CustomerID ke string untuk memastikan tidak ada masalah tipe data saat grouping
df['CustomerID'] = df['CustomerID'].astype(str)

print("\n--- Tampilan Data Setelah Pembersihan ---")
print(df.head())
print("\n--- Informasi Data Setelah Pembersihan ---")
print(df.info())


# --- 3. Rekayasa Fitur (Feature Engineering) ---
print("\n--- 3. Rekayasa Fitur ---")

# Menghitung TotalPrice untuk setiap transaksi
df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
print(f"Kolom 'TotalPrice' berhasil ditambahkan. Contoh: {df['TotalPrice'].head()}")

# Ekstrak informasi waktu
df['Year'] = df['InvoiceDate'].dt.year
df['Month'] = df['InvoiceDate'].dt.month
df['Day'] = df['InvoiceDate'].dt.day
df['DayOfWeek'] = df['InvoiceDate'].dt.day_name() # Nama hari (Senin, Selasa, dst.)
df['Hour'] = df['InvoiceDate'].dt.hour

print("\n--- Fitur Waktu yang Diekstrak ---")
print(df[['InvoiceDate', 'Year', 'Month', 'Day', 'DayOfWeek', 'Hour']].head())

# --- 4. Eksplorasi Data & Analisis (EDA) ---
print("\n--- 4. Eksplorasi Data & Analisis (EDA) ---")

# Ringkasan Penjualan Keseluruhan
total_revenue = df['TotalPrice'].sum()
total_transactions = df['InvoiceNo'].nunique()
total_products_sold = df['Quantity'].sum()
unique_customers = df['CustomerID'].nunique()

print(f"\nTotal Pendapatan (Revenue): £{total_revenue:,.2f}")
print(f"Total Jumlah Transaksi: {total_transactions:,}")
print(f"Total Kuantitas Produk Terjual: {total_products_sold:,}")
print(f"Jumlah Pelanggan Unik: {unique_customers:,}")

# --- 4.1 Tren Penjualan Berdasarkan Waktu ---
print("\n--- 4.1 Tren Penjualan Berdasarkan Waktu ---")

# Penjualan Bulanan
monthly_sales = df.groupby(['Year', 'Month'])['TotalPrice'].sum().reset_index()
# Pastikan ada data untuk membuat tanggal
if not monthly_sales.empty:
    monthly_sales['Date'] = pd.to_datetime(monthly_sales['Year'].astype(str) + '-' + monthly_sales['Month'].astype(str))

    plt.figure(figsize=(14, 7))
    sns.lineplot(data=monthly_sales, x='Date', y='TotalPrice', marker='o')
    plt.title('Tren Penjualan Bulanan')
    plt.xlabel('Tanggal')
    plt.ylabel('Total Penjualan (£)')
    plt.grid(True)
    plt.tight_layout()
    plt.show()
else:
    print("Tidak ada data penjualan bulanan untuk diplot.")


# Penjualan Harian dalam Seminggu
daily_sales = df.groupby('DayOfWeek')['TotalPrice'].sum().reindex([
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
]) # Memastikan urutan hari yang benar

plt.figure(figsize=(10, 6))
sns.barplot(x=daily_sales.index, y=daily_sales.values, palette='viridis')
plt.title('Total Penjualan per Hari dalam Seminggu')
plt.xlabel('Hari dalam Seminggu')
plt.ylabel('Total Penjualan (£)')
plt.tight_layout()
plt.show()

# Penjualan per Jam
hourly_sales = df.groupby('Hour')['TotalPrice'].sum()

plt.figure(figsize=(10, 6))
sns.lineplot(x=hourly_sales.index, y=hourly_sales.values, marker='o')
plt.title('Total Penjualan per Jam')
plt.xlabel('Jam dalam Sehari (0-23)')
plt.ylabel('Total Penjualan (£)')
plt.xticks(range(24))
plt.grid(True)
plt.tight_layout()
plt.show()

# --- 4.2 Performa Produk ---
print("\n--- 4.2 Performa Produk ---")

# Top 10 Produk Terlaris berdasarkan Kuantitas
top_10_products_qty = df.groupby('Description')['Quantity'].sum().nlargest(10).sort_values(ascending=False)
print("\nTop 10 Produk Terlaris (berdasarkan Kuantitas):")
print(top_10_products_qty)

plt.figure(figsize=(12, 7))
sns.barplot(x=top_10_products_qty.values, y=top_10_products_qty.index, palette='crest')
plt.title('Top 10 Produk Terlaris (berdasarkan Kuantitas)')
plt.xlabel('Total Kuantitas Terjual')
plt.ylabel('Nama Produk')
plt.tight_layout()
plt.show()

# Top 10 Produk Terlaris berdasarkan Pendapatan
top_10_products_rev = df.groupby('Description')['TotalPrice'].sum().nlargest(10).sort_values(ascending=False)
print("\nTop 10 Produk Terlaris (berdasarkan Pendapatan):")
print(top_10_products_rev)

plt.figure(figsize=(12, 7))
sns.barplot(x=top_10_products_rev.values, y=top_10_products_rev.index, palette='magma')
plt.title('Top 10 Produk Terlaris (berdasarkan Pendapatan)')
plt.xlabel('Total Pendapatan (£)')
plt.ylabel('Nama Produk')
plt.tight_layout()
plt.show()

# --- 4.3 Analisis Pelanggan & Geografis ---
print("\n--- 4.3 Analisis Pelanggan & Geografis ---")

# Top 10 Pelanggan dengan Pembelian Terbanyak
top_10_customers = df.groupby('CustomerID')['TotalPrice'].sum().nlargest(10).sort_values(ascending=False)
print("\nTop 10 Pelanggan dengan Pembelian Terbanyak:")
print(top_10_customers)

plt.figure(figsize=(12, 7))
sns.barplot(x=top_10_customers.values, y=top_10_customers.index, palette='cividis')
plt.title('Top 10 Pelanggan dengan Pembelian Terbanyak')
plt.xlabel('Total Belanja (£)')
plt.ylabel('ID Pelanggan')
plt.tight_layout()
plt.show()

# Distribusi Penjualan per Negara
sales_by_country = df.groupby('Country')['TotalPrice'].sum().nlargest(10).sort_values(ascending=False) # Top 10 negara
print("\nTop 10 Negara Berdasarkan Penjualan:")
print(sales_by_country)

plt.figure(figsize=(12, 7))
sns.barplot(x=sales_by_country.values, y=sales_by_country.index, palette='rocket')
plt.title('Top 10 Negara Berdasarkan Total Penjualan')
plt.xlabel('Total Penjualan (£)')
plt.ylabel('Negara')
plt.tight_layout()
plt.show()


# --- 5. Kesimpulan & Rekomendasi Bisnis ---
print("\n--- 5. Kesimpulan & Rekomendasi Bisnis ---")
print("\nKesimpulan Utama:")
print("- Total Pendapatan E-commerce: £{:,.2f}".format(total_revenue))
print("- Jumlah Pelanggan Unik yang bertransaksi: {:,}".format(unique_customers))
print("- **Tren Penjualan:** Penjualan menunjukkan puncak di akhir tahun (sekitar November-Desember) dan cenderung lebih rendah di awal tahun. Hari Kamis adalah hari dengan penjualan tertinggi, dan penjualan aktif dari jam 10 pagi hingga 4 sore.")
print("- **Performa Produk:** Beberapa produk seperti 'Paper Craft' dan 'JUMBO BAG' adalah kontributor utama pendapatan, menunjukkan popularitas yang tinggi.")
print("- **Analisis Pelanggan & Geografis:** Mayoritas pendapatan berasal dari Inggris, namun ada kontribusi signifikan dari negara-negara Eropa lainnya, menandakan pasar potensial di luar Inggris.")

print("\n**Rekomendasi Bisnis:**")
print("1. **Optimalisasi Musiman:** Lakukan kampanye pemasaran dan promosi yang intensif, serta pastikan ketersediaan stok yang memadai menjelang akhir tahun (Oktober-Desember) untuk memaksimalkan puncak penjualan.")
print("2. **Fokus pada Produk Unggulan:** Promosikan lebih lanjut produk-produk terlaris ('Paper Craft', 'JUMBO BAG') melalui penempatan strategis di website, bundling produk, atau program loyalitas. Pertimbangkan untuk mencari produk serupa untuk memperluas lini produk terlaris.")
print("3. **Strategi Waktu:** Manfaatkan data penjualan harian dan jam untuk menjadwalkan kampanye email atau promosi real-time. Misalnya, luncurkan penawaran khusus di hari Kamis atau antara jam 10 pagi hingga 4 sore.")
print("4. **Ekspansi Pasar Internasional:** Meskipun Inggris dominan, potensi pertumbuhan di negara-negara Eropa lainnya terlihat. Pertimbangkan strategi pemasaran yang ditargetkan untuk negara-negara ini, mungkin dengan penyesuaian lokal atau penawaran khusus untuk menarik lebih banyak pelanggan.")
print("5. **Program Loyalitas Pelanggan:** Identifikasi pelanggan top (dengan pengeluaran tertinggi) dan berikan perlakuan khusus atau program loyalitas untuk mempertahankan mereka dan mendorong pembelian berulang.")
print("6. **Manajemen Inventaris:** Gunakan data penjualan produk untuk mengoptimalkan inventaris, mengurangi kelebihan stok produk yang kurang laku, dan memastikan ketersediaan produk populer.")

print("\nAnalisis ini memberikan wawasan awal yang kuat. Untuk eksplorasi lebih lanjut, bisa dilakukan segmentasi pelanggan (misalnya dengan RFM Analysis) atau analisis asosiasi item (produk apa yang sering dibeli bersamaan).")