import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

# menyiapkan sum_order_category_df
def create_sum_orders_category_df(df):
    sum_orders_category_df = df.groupby("product_category_name").order_id.nunique().sort_values(ascending=False).reset_index()
    return sum_orders_category_df

# menyiapkan bypayment_df
def create_bypayment_df(df):
    bypayment_df = df.groupby(by="payment_type").customer_id.nunique().reset_index()
    bypayment_df.rename(columns={
        "customer_id": "customer_count",
        "payment_type": "payment",
    }, inplace=True)
    
    return bypayment_df

# menyiapkan bystate_df
def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count",
        "customer_state": "state",
    }, inplace=True)
    
    return bystate_df

# menyiapkan rfm_df
def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max", # mengambil tanggal order terakhir
        "order_id": "nunique", # menghitung jumlah order
        "payment_value": "sum" # menghitung jumlah revenue yang dihasilkan
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]

    # menghitung kapan terakhir pelanggan melakukan transaksi (hari)
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)

    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df

# load berkas
all_df = pd.read_csv("all_data.csv")

datetime_columns = ["order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
  all_df[column] = pd.to_datetime(all_df[column])


min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()
 
with st.sidebar:
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]

# memanggil helper function
sum_orders_category_df = create_sum_orders_category_df(main_df)
bypayment_df = create_bypayment_df(main_df)
bystate_df = create_bystate_df(main_df)
rfm_df = create_rfm_df(main_df)

st.header('E-commerce Dashboard :sparkles:')

# menampilkan 5 kategori produk paling sering dipesan dan paling sedikit dipesan
st.subheader("Best & Worst Performing Category by Number of Orders")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="order_id", y="product_category_name", data=sum_orders_category_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Orders", fontsize=30)
ax[0].set_title("Best Performing Category", loc="center", fontsize=50)
ax[0].tick_params(axis ='y', labelsize=35)
ax[0].tick_params(axis ='x', labelsize=30)

sns.barplot(x="order_id", y="product_category_name", data=sum_orders_category_df.sort_values(by="order_id", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Orders", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Category", loc="center", fontsize=50)
ax[1].tick_params(axis ='y', labelsize=35)
ax[1].tick_params(axis ='x', labelsize=30)

st.pyplot(fig)

# pelanggan yang menggunakan metode pemebayaran
st.subheader("Metode pembayaran yang digunakan Pelanggan")
fig, ax = plt.subplots(figsize=(20, 10))
colors_ = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="payment",
    y="customer_count",
    data=bypayment_df.sort_values(by="customer_count", ascending=False),
    palette=colors_,
    ax=ax
)
ax.set_title("Jumlah pelanggan yang menggunakan beberapa metode pembayaran", loc="center", fontsize=35)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=35)
ax.tick_params(axis='y', labelsize=30)
st.pyplot(fig)

# persebaran pelanggan berdasarkan state
st.subheader("Persebaran Pelanggan")
fig, ax = plt.subplots(figsize=(20, 10))
colors_ = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="state",
    y="customer_count",
    data=bystate_df.sort_values(by="customer_count", ascending=False),
    palette=colors_,
    ax=ax
)
ax.set_title("Jumlah persebaran Pelanggan berdasarkan State ", loc="center", fontsize=35)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=20)
ax.tick_params(axis='y', labelsize=30)
st.pyplot(fig)

# RFM
st.subheader("Best Customer Based on RFM Parameters")
 
col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
 
sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=14, rotation=300)
 
sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=14, rotation=300)
 
sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=14, rotation=300)
 
st.pyplot(fig)

st.caption('Copyright (c) Irham Maulana 2023')