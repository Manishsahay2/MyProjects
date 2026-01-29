# app.py
import streamlit as st
import pandas as pd

st.set_page_config(page_title="CSC-wise Order Summary", layout="wide")
st.title("📊 CSC-wise Order Summary Dashboard")

# --- CSV Upload ---
uploaded_file = st.file_uploader("Upload Orders CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    # Check necessary columns
    required_cols = ['csc_id', 'order_date', 'estore_name', 'number_of_items_in_the_order', 'total_amount']
    if not all(col in df.columns for col in required_cols):
        st.error(f"CSV must contain columns: {required_cols}")
    else:
        # Convert order_date to datetime
        df['order_date'] = pd.to_datetime(df['order_date'])

        # --- Sidebar Filters ---
        st.sidebar.header("Filters")

        # CSC multi-select
        csc_options = df['csc_id'].unique().tolist()
        selected_cscs = st.sidebar.multiselect("Select CSC(s)", options=csc_options, default=csc_options)

        # Product / eStore filter
        product_options = df['estore_name'].unique().tolist()
        selected_products = st.sidebar.multiselect("Select eStore(s)", options=product_options, default=product_options)

        # Date range
        min_date = df['order_date'].min()
        max_date = df['order_date'].max()
        start_date = st.sidebar.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date)
        end_date = st.sidebar.date_input("End Date", min_value=min_date, max_value=max_date, value=max_date)

        # --- Filter Data ---
        filtered_df = df[
            (df['csc_id'].isin(selected_cscs)) &
            (df['estore_name'].isin(selected_products)) &
            (df['order_date'] >= pd.to_datetime(start_date)) &
            (df['order_date'] <= pd.to_datetime(end_date))
        ]

        # --- CSC-wise Summary ---
        summary_df = filtered_df.groupby('csc_id').agg(
            Total_Orders=('number_of_items_in_the_order', 'sum'),
            Total_Amount=('total_amount', 'sum')
        ).reset_index()

        st.subheader("📋 CSC-wise Summary")
        st.dataframe(summary_df.style.format({"Total_Amount": "{:,.2f}", "Total_Orders": "{:,}"}))

        # --- Charts ---
        st.subheader("📈 Total Amount by CSC")
        st.bar_chart(summary_df.set_index('csc_id')['Total_Amount'])

        st.subheader("📊 Orders Trend Over Time")
        trend_df = filtered_df.groupby('order_date').agg(
            Total_Orders=('number_of_items_in_the_order','sum'),
            Total_Amount=('total_amount','sum')
        ).reset_index()
        st.line_chart(trend_df.set_index('order_date')[['Total_Orders', 'Total_Amount']])

        # --- Download Filtered Data ---
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Data",
            data=csv,
            file_name='filtered_orders.csv',
            mime='text/csv',
        )
else:
    st.info("Please upload a CSV file to proceed.")
