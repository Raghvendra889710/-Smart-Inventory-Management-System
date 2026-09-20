import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor

st.set_page_config(page_title="Smart Inventory Management System", layout="wide")
st.title("📦 Smart Inventory Management Dashboard")

# 1. Load and Prepare Data
@st.cache_data
def load_data():
    # If you downloaded 'inventory_dataset.csv' from Colab, ensure it's in the repo
    # Alternatively, you can recreate the synthetic dataframe here for a seamless cloud run
    import random
    np.random.seed(42)
    categories = ['Electronics', 'Accessories', 'Office Supplies', 'Hardware']
    suppliers = ['TechCorp', 'SupplyCo', 'GlobalParts', 'ElectroMart']

    data = {
        'Product ID': [f'PRD-{i:03d}' for i in range(1, 151)],
        'Product Name': [f'Item_{i}' for i in range(1, 151)],
        'Category': [random.choice(categories) for _ in range(150)],
        'Quantity in Stock': np.random.randint(0, 250, 150),
        'Supplier': [random.choice(suppliers) for _ in range(150)],
        'Purchase Price': np.random.uniform(15, 600, 150).round(2),
        'Historical Sales': np.random.randint(40, 600, 150)
    }
    df = pd.DataFrame(data)
    df['Selling Price'] = (df['Purchase Price'] * 1.3).round(2)
    df['Total Inventory Value'] = (df['Quantity in Stock'] * df['Purchase Price']).round(2)
    df['Stock Status'] = np.where(df['Quantity in Stock'] == 0, 'Out of Stock',
                         np.where(df['Quantity in Stock'] < 25, 'Low Stock', 'In Stock'))
    return df

df = load_data()

# Sidebar Filters
st.sidebar.header("Filter & Search")
search_query = st.sidebar.text_input("Search Product Name")
selected_category = st.sidebar.multiselect("Category", df['Category'].unique(), default=df['Category'].unique())
selected_status = st.sidebar.multiselect("Stock Status", df['Stock Status'].unique(), default=df['Stock Status'].unique())

filtered_df = df[
    (df['Category'].isin(selected_category)) & 
    (df['Stock Status'].isin(selected_status)) &
    (df['Product Name'].str.contains(search_query, case=False, na=False))
]

# Dashboard Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Products", len(filtered_df))
col2.metric("Total Inventory Value", f"${filtered_df['Total Inventory Value'].sum():,.2f}")
col3.metric("Low Stock Items", len(filtered_df[filtered_df['Stock Status'] == 'Low Stock']))
col4.metric("Out of Stock", len(filtered_df[filtered_df['Stock Status'] == 'Out of Stock']))

st.markdown("---")

# Visualizations
c1, c2 = st.columns(2)
with c1:
    st.subheader("Stock Distribution by Category")
    cat_stock = filtered_df.groupby('Category')['Quantity in Stock'].sum().reset_index()
    fig_cat = px.bar(cat_stock, x='Category', y='Quantity in Stock', color='Category')
    st.plotly_chart(fig_cat, use_container_width=True)

with c2:
    st.subheader("Stock Status Proportions")
    fig_pie = px.pie(filtered_df, names='Stock Status', hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)

# Low Stock Alerts Table
st.subheader("⚠️ Low Stock & Out-of-Stock Alerts")
alerts_df = filtered_df[filtered_df['Stock Status'].isin(['Low Stock', 'Out of Stock'])]
st.dataframe(alerts_df[['Product ID', 'Product Name', 'Category', 'Quantity in Stock', 'Stock Status', 'Supplier']], use_container_width=True)
