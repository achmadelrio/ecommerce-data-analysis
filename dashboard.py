import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Konfigurasi halaman dashboard
st.set_page_config(
    page_title="E-Commerce Business & Customer Dashboard",
    page_icon="📊",
    layout="wide"
)
sns.set_theme(style="whitegrid")

# Memuat data bersih (main_data.csv) dengan path dinamis
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "main_data.csv")
    df = pd.read_csv(file_path)
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    return df

main_df = load_data()

# --- SIDEBAR FILTER ---
st.sidebar.header("Filter Analisis")
min_date = main_df["order_purchase_timestamp"].min().date()
max_date = main_df["order_purchase_timestamp"].max().date()

date_range = st.sidebar.date_input(
    "Rentang Tanggal Transaksi:",
    value=[pd.to_datetime("2017-01-01").date(), max_date],
    min_value=min_date,
    max_value=max_date
)

# Terapkan filter tanggal
if len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1]) + pd.Timedelta(days=1)
    filtered_df = main_df[
        (main_df["order_purchase_timestamp"] >= start_date) &
        (main_df["order_purchase_timestamp"] < end_date)
    ].copy()
else:
    filtered_df = main_df.copy()

# --- HEADER & KPI METRICS ---
st.title("📊 E-Commerce Performance & Customer Satisfaction Dashboard")
st.markdown("Dashboard interaktif untuk memantau performa kategori produk, tren pendapatan bulanan, dampak ketepatan pengiriman terhadap kepuasan pelanggan, serta analisis segmentasi pelanggan (RFM).")

# Hitung KPI tingkat pesanan unik untuk ulasan
order_reviews_unique = filtered_df.dropna(subset=["review_score"]).drop_duplicates(subset=["order_id"])

col1, col2, col3 = st.columns(3)
col1.metric("Total Pesanan (Delivered)", f"{filtered_df['order_id'].nunique():,}")
col2.metric("Total Pendapatan (BRL)", f"R$ {filtered_df['price'].sum():,.2f}")
col3.metric("Rata-Rata Review Score", f"{order_reviews_unique['review_score'].mean():.2f} / 5.00")

st.markdown("---")

# --- VISUALISASI 1: PERFORMA KATEGORI & TREN BULANAN ---
st.subheader("1. Performa Kategori Produk & Tren Pendapatan Bulanan")
c1, c2 = st.columns(2)

with c1:
    top_categories = (
        filtered_df.groupby("product_category_name_english")["price"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    colors_cat = ["#1f77b4" if i == 0 else "#D3D3D3" for i in range(len(top_categories))]
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    sns.barplot(
        data=top_categories, x="price", y="product_category_name_english",
        hue="product_category_name_english", palette=colors_cat, legend=False, ax=ax1
    )
    ax1.set_title("Top 10 Kategori Produk Berdasarkan Revenue", fontweight="bold")
    ax1.set_xlabel("Total Pendapatan (BRL)")
    ax1.set_ylabel("Kategori Produk")
    st.pyplot(fig1)

with c2:
    filtered_df["year_month"] = filtered_df["order_purchase_timestamp"].dt.to_period("M").astype(str)
    monthly_rev = filtered_df.groupby("year_month")["price"].sum().reset_index()
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    sns.lineplot(data=monthly_rev, x="year_month", y="price", marker="o", linewidth=2.5, color="#1f77b4", ax=ax2)
    ax2.set_title("Tren Total Pendapatan Bulanan", fontweight="bold")
    ax2.set_xlabel("Bulan Transaksi")
    ax2.set_ylabel("Total Pendapatan (BRL)")
    ax2.tick_params(axis="x", rotation=45)
    st.pyplot(fig2)

st.markdown("---")

# --- VISUALISASI 2: KETEPATAN PENGIRIMAN VS REVIEW SCORE ---
st.subheader("2. Dampak Ketepatan Waktu Pengiriman terhadap Review Score")
review_summary = (
    order_reviews_unique.groupby("delivery_status")["review_score"]
    .mean()
    .reset_index()
)

fig3, ax3 = plt.subplots(figsize=(8, 4))
sns.barplot(
    data=review_summary, x="delivery_status", y="review_score",
    hue="delivery_status", palette=["#d9534f", "#2ca02c"], legend=False, ax=ax3
)
ax3.set_title("Perbandingan Rata-Rata Skor Ulasan: Terlambat vs Tepat Waktu", fontweight="bold")
ax3.set_xlabel("Status Pengiriman")
ax3.set_ylabel("Rata-Rata Skor Ulasan (1 - 5)")
ax3.set_ylim(0, 5.5)

for p in ax3.patches:
    ax3.annotate(
        f"{p.get_height():.2f}",
        (p.get_x() + p.get_width() / 2., p.get_height()),
        ha="center", va="bottom", fontsize=11, fontweight="bold"
    )
st.pyplot(fig3)

st.markdown("---")

# --- VISUALISASI 3: ANALISIS LANJUTAN (RFM ANALYSIS) ---
st.subheader("3. Analisis Lanjutan: Best Customer Berdasarkan Parameter RFM")

snapshot_date = filtered_df["order_purchase_timestamp"].max() + pd.Timedelta(days=1)
rfm_df = filtered_df.groupby("customer_unique_id").agg(
    recency=("order_purchase_timestamp", lambda x: (snapshot_date - x.max()).days),
    frequency=("order_id", "nunique"),
    monetary=("price", "sum")
).reset_index()

col_r, col_f, col_m = st.columns(3)
col_r.metric("Rata-Rata Recency", f"{rfm_df['recency'].mean():.1f} Hari")
col_f.metric("Rata-Rata Frequency", f"{rfm_df['frequency'].mean():.2f} Order")
col_m.metric("Rata-Rata Monetary", f"R$ {rfm_df['monetary'].mean():.2f}")

fig_rfm, axes_rfm = plt.subplots(1, 3, figsize=(18, 5))

# Top 5 Recency
top_r = rfm_df.sort_values(by="recency", ascending=True).head(5).copy()
top_r["short_id"] = top_r["customer_unique_id"].str[:8]
sns.barplot(data=top_r, x="short_id", y="recency", color="#1f77b4", ax=axes_rfm[0])
axes_rfm[0].set_title("Top 5 by Recency (Days)", fontweight="bold")
axes_rfm[0].set_xlabel("Customer ID")
axes_rfm[0].set_ylabel("Recency (Hari)")

# Top 5 Frequency
top_f = rfm_df.sort_values(by="frequency", ascending=False).head(5).copy()
top_f["short_id"] = top_f["customer_unique_id"].str[:8]
colors_f = ["#1f77b4" if i == 0 else "#D3D3D3" for i in range(len(top_f))]
sns.barplot(data=top_f, x="short_id", y="frequency", hue="short_id", palette=colors_f, legend=False, ax=axes_rfm[1])
axes_rfm[1].set_title("Top 5 by Frequency (Orders)", fontweight="bold")
axes_rfm[1].set_xlabel("Customer ID")
axes_rfm[1].set_ylabel("Frequency (Order)")

# Top 5 Monetary
top_m = rfm_df.sort_values(by="monetary", ascending=False).head(5).copy()
top_m["short_id"] = top_m["customer_unique_id"].str[:8]
colors_m = ["#1f77b4" if i == 0 else "#D3D3D3" for i in range(len(top_m))]
sns.barplot(data=top_m, x="short_id", y="monetary", hue="short_id", palette=colors_m, legend=False, ax=axes_rfm[2])
axes_rfm[2].set_title("Top 5 by Monetary (BRL)", fontweight="bold")
axes_rfm[2].set_xlabel("Customer ID")
axes_rfm[2].set_ylabel("Monetary (BRL)")

plt.tight_layout()
st.pyplot(fig_rfm)