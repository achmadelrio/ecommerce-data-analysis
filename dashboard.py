import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.set_page_config(
    page_title="E-Commerce Business & Customer Dashboard",
    page_icon="📊",
    layout="wide"
)
sns.set_theme(style="whitegrid")

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

if len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1]) + pd.Timedelta(days=1)
    filtered_df = main_df[
        (main_df["order_purchase_timestamp"] >= start_date) &
        (main_df["order_purchase_timestamp"] < end_date)
    ].copy()
else:
    filtered_df = main_df.copy()

# --- HEADER & KPI ---
st.title("📊 E-Commerce Performance & Customer Satisfaction Dashboard")
order_reviews_unique = filtered_df.dropna(subset=["review_score"]).drop_duplicates(subset=["order_id"])

col1, col2, col3 = st.columns(3)
col1.metric("Total Pesanan (Delivered)", f"{filtered_df['order_id'].nunique():,}")
col2.metric("Total Pendapatan (BRL)", f"R$ {filtered_df['price'].sum():,.2f}")
col3.metric("Rata-Rata Review Score", f"{order_reviews_unique['review_score'].mean():.2f} / 5.00")

st.markdown("---")

# --- VISUALISASI 1 ---
st.subheader("1. Performa Kategori Produk (Revenue & Volume Pesanan) serta Tren Bulanan")
cat_summary = filtered_df.groupby("product_category_name_english").agg(
    total_revenue=("price", "sum"),
    total_orders=("order_id", "nunique")
).reset_index()

top_rev = cat_summary.sort_values(by="total_revenue", ascending=False).head(10)
top_ord = cat_summary.sort_values(by="total_orders", ascending=False).head(10)

c1, c2 = st.columns(2)
with c1:
    colors_rev = ["#1f77b4" if i == 0 else "#D3D3D3" for i in range(len(top_rev))]
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    sns.barplot(data=top_rev, x="total_revenue", y="product_category_name_english", hue="product_category_name_english", palette=colors_rev, legend=False, ax=ax1)
    ax1.set_title("Top 10 Kategori by Total Revenue (BRL)", fontweight="bold")
    ax1.set_xlabel("Total Pendapatan (BRL)")
    ax1.set_ylabel("Kategori Produk")
    st.pyplot(fig1)

with c2:
    colors_ord = ["#1f77b4" if i == 0 else "#D3D3D3" for i in range(len(top_ord))]
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    sns.barplot(data=top_ord, x="total_orders", y="product_category_name_english", hue="product_category_name_english", palette=colors_ord, legend=False, ax=ax2)
    ax2.set_title("Top 10 Kategori by Volume Pesanan", fontweight="bold")
    ax2.set_xlabel("Jumlah Pesanan Unik")
    ax2.set_ylabel("Kategori Produk")
    st.pyplot(fig2)

filtered_df["year_month"] = filtered_df["order_purchase_timestamp"].dt.to_period("M").astype(str)
monthly_rev = filtered_df.groupby("year_month")["price"].sum().reset_index()
fig_trend, ax_trend = plt.subplots(figsize=(14, 4))
sns.lineplot(data=monthly_rev, x="year_month", y="price", marker="o", linewidth=2.5, color="#1f77b4", ax=ax_trend)
ax_trend.set_title("Tren Total Pendapatan Bulanan", fontweight="bold")
ax_trend.set_xlabel("Bulan Transaksi")
ax_trend.set_ylabel("Total Pendapatan (BRL)")
ax_trend.tick_params(axis="x", rotation=45)
st.pyplot(fig_trend)

st.markdown("---")

# --- VISUALISASI 2 ---
st.subheader("2. Perbandingan Rata-Rata Review Score Berdasarkan Ketepatan Pengiriman")
review_summary = order_reviews_unique.groupby("delivery_status")["review_score"].mean().reset_index()
fig3, ax3 = plt.subplots(figsize=(8, 4))
sns.barplot(data=review_summary, x="delivery_status", y="review_score", hue="delivery_status", palette=["#d9534f", "#2ca02c"], legend=False, ax=ax3)
ax3.set_title("Perbandingan Rata-Rata Skor Ulasan: Terlambat vs Tepat Waktu", fontweight="bold")
ax3.set_xlabel("Status Pengiriman")
ax3.set_ylabel("Rata-Rata Skor Ulasan (1 - 5)")
ax3.set_ylim(0, 5.5)
for p in ax3.patches:
    ax3.annotate(f"{p.get_height():.2f}", (p.get_x() + p.get_width() / 2., p.get_height()), ha="center", va="bottom", fontweight="bold")
st.pyplot(fig3)

st.markdown("---")

# --- VISUALISASI 3: RFM SEGMENTATION ---
st.subheader("3. Analisis Lanjutan: Segmentasi Pelanggan Berdasarkan RFM")
snapshot_date = filtered_df["order_purchase_timestamp"].max() + pd.Timedelta(days=1)
rfm_df = filtered_df.groupby("customer_unique_id").agg(
    recency=("order_purchase_timestamp", lambda x: (snapshot_date - x.max()).days),
    frequency=("order_id", "nunique"),
    monetary=("price", "sum")
).reset_index()

def classify_customer(row):
    if row["frequency"] > 1 and row["recency"] <= 180:
        return "Loyal Active Customers"
    elif row["frequency"] > 1 and row["recency"] > 180:
        return "At-Risk Repeat Customers"
    elif row["frequency"] == 1 and row["recency"] <= 90:
        return "Recent One-Time Buyers"
    else:
        return "Inactive One-Time Buyers"

rfm_df["customer_segment"] = rfm_df.apply(classify_customer, axis=1)
segment_summary = rfm_df["customer_segment"].value_counts().reset_index()
segment_summary.columns = ["customer_segment", "customer_count"]

col_r, col_f, col_m = st.columns(3)
col_r.metric("Rata-Rata Recency", f"{rfm_df['recency'].mean():.2f} Hari")
col_f.metric("Rata-Rata Frequency", f"{rfm_df['frequency'].mean():.2f} Order")
col_m.metric("Rata-Rata Monetary", f"R$ {rfm_df['monetary'].mean():.2f}")

fig_seg, ax_seg = plt.subplots(figsize=(10, 4))
colors_seg = ["#1f77b4" if i == 0 else "#D3D3D3" for i in range(len(segment_summary))]
sns.barplot(data=segment_summary, x="customer_count", y="customer_segment", hue="customer_segment", palette=colors_seg, legend=False, ax=ax_seg)
ax_seg.set_title("Distribusi Segmen Pelanggan (RFM Manual Grouping)", fontweight="bold")
ax_seg.set_xlabel("Jumlah Pelanggan Unik")
ax_seg.set_ylabel("Segmen Pelanggan")
st.pyplot(fig_seg)