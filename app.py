
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from Visualizer import Visualizer
from finance_engine import InventoryManager, CashFlowManager, FinancialAnalyzer, Sale, InventoryItem, save_sale

st.html('<meta name="google-site-verification" content="CIAZXu0C3FeZ4TIzuwUCndmw7okvAxVh7Uzo3TGk7MA" />')
# ... (rest of the file until Operations Center)

# Load the store salesdata
@st.cache_data
def load_store_sales():
    df = pd.read_csv('store_sales.csv')
    # Standardize column names
    rename_map = {
        'ItemPurchased': 'Description',
        'Amount': 'Price'
    }
    df = df.rename(columns=rename_map)
    
    # Ensure Quantity exists
    if 'Quantity' not in df.columns:
        df['Quantity'] = 1
        
    return df

# Load data at startup
df_store_sales = load_store_sales()

# Initialize modules
visualizer = Visualizer()
inventory_manager = InventoryManager()
cash_flow_manager = CashFlowManager()
financial_analyzer = FinancialAnalyzer()

# Streamlit page configuration
st.set_page_config(
    page_title="Small Business Supply And Cash Flow Analyzer",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for modern look
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        background-color: #f0f2f6;
    }
    
    /* Card styling */
    .metric-card {
        background-color: #ffffff;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid #3498db;
        margin-bottom: 20px;
    }
    
    .metric-label {
        color: #7f8c8d;
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 5px;
    }
    
    .metric-value {
        color: #2c3e50;
        font-size: 24px;
        font-weight: 700;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #2c3e50;
    }
    section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] .stHeader {
        color: #ecf0f1;
    }
    
    /* Title styling */
    .main-title {
        color: #FFFFFF;
        font-weight: 900;
        font-size: 52px;
        text-align: center;
        margin-top: 20px;
        margin-bottom: 40px;
        letter-spacing: -1px;
        line-height: 1.2;
        text-shadow: 0 2px 8px rgba(0,0,0,0.4);
    }
    /* Custom tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #ffffff;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3498db !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">Small Business Supply And Cash Flow Analyzer</div>', unsafe_allow_html=True)

# Sidebar navigation and Filters
with st.sidebar:
    st.header("Control Panel")
    
    page = st.radio("Navigation", [
        "Executive Dashboard",
        "Inventory Explorer",
        "Financial Analytics",
        "Operations Center"
    ])
    
    st.divider()
    st.subheader("Analysis Settings")
    weightage_threshold = st.slider("Revenue Weightage Threshold (%)", 0.0, 20.0, 10.0, help="Products below this % of total revenue will be discarded from core analysis.")
    
    st.subheader("Global Filters")
    st.write(" Category Filter")
    if 'Category' in df_store_sales.columns:
        categories = ["All"] + sorted(df_store_sales['Category'].unique().tolist())
        selected_cat = st.selectbox("Category Filter", categories)
    else:
        selected_cat = "All"
        
    st.write(" Season Filter")
    if 'Season' in df_store_sales.columns:
         seasons = ["All"] + sorted(df_store_sales['Season'].unique().tolist())
         selected_season = st.selectbox("Season Filter", seasons)
    else:
        selected_season = "All"

# Apply basic filters
df_base_filtered = df_store_sales.copy()
if selected_cat != "All":
    df_base_filtered = df_base_filtered[df_base_filtered['Category'] == selected_cat]
if selected_season != "All":
    df_base_filtered = df_base_filtered[df_base_filtered['Season'] == selected_season]

df_base_filtered['Revenue'] = df_base_filtered['Price'] * df_base_filtered['Quantity']

# Apply Weightage Discard Condition
product_revenue = df_base_filtered.groupby('Description')['Revenue'].sum()
total_rev = product_revenue.sum()
product_weightage = (product_revenue / total_rev) * 100
significant_products = product_weightage[product_weightage >= weightage_threshold].index

# Final Filtered DataFrame (Discarding low weightage products)
df_filtered = df_base_filtered[df_base_filtered['Description'].isin(significant_products)].copy()

# Dashboard Page
if page == "Executive Dashboard":
    # Discard Alert
    discarded_count = len(product_weightage) - len(significant_products)
    if discarded_count > 0:
        st.warning(f"Discarding {discarded_count} products with revenue weightage below {weightage_threshold}%")

    # Top Level Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_rev_val = df_filtered['Revenue'].sum()
        st.metric("Filtered Revenue", f"${total_rev_val:,.2f}", delta=f"{len(df_filtered)} Sales")
    with col2:
        if not df_filtered.empty:
            best_cash_product = df_filtered.groupby('Description')['Revenue'].sum().idxmax()
            st.metric("Best Cash Inflow", best_cash_product)
        else:
            st.metric("Best Cash Inflow", "N/A")
    with col3:
        unique_items = df_filtered['Description'].nunique()
        st.metric("Active Products", unique_items)
    with col4:
        avg_rating = df_filtered['ItemRating'].mean() if 'ItemRating' in df_filtered.columns else 0
        st.metric("Avg Rating", f"{avg_rating:.1f} / 5.0")

    tab1, tab2, tab3, tab4 = st.tabs(["Sales Analysis", "Customer Insights", "Evergreen Assets", "Raw Data View"])
    
    with tab1:
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Seasonal Revenue Distribution")
            fig_season = visualizer.plot_sales_by_season(df_filtered)
            if fig_season:
                st.pyplot(fig_season)
                plt.close(fig_season)
        with col_b:
            st.subheader("Revenue by Category")
            fig_cat = visualizer.plot_product_categories(df_filtered)
            if fig_cat:
                st.pyplot(fig_cat)
                plt.close(fig_cat)

        st.divider()
        col_c, col_d = st.columns(2)
        with col_c:
            st.subheader("Top 10 Products by Revenue")
            top_rev = df_filtered.groupby('Description')['Revenue'].sum().nlargest(10)
            st.bar_chart(top_rev)
        with col_d:
            st.subheader("Top 10 Products by Volume")
            top_vol = df_filtered.groupby('Description')['Quantity'].sum().nlargest(10)
            st.bar_chart(top_vol)
            
    with tab2:
        col_e, col_f = st.columns(2)
        with col_e:
            st.subheader("Payment Method Usage")
            fig_payment = visualizer.plot_payment_methods(df_filtered)
            if fig_payment:
                st.pyplot(fig_payment)
                plt.close(fig_payment)
        with col_f:
            st.subheader("Customer Age Distribution")
            if 'Age' in df_filtered.columns:
                fig_age, ax_age = plt.subplots()
                sns.histplot(df_filtered['Age'], bins=20, kde=True, ax=ax_age, color='#3498db')
                st.pyplot(fig_age)
                plt.close(fig_age)

    with tab3:
        st.subheader("Top 10 Evergreen Products")
        st.write("Products with high consistent demand and customer satisfaction.")
        if 'ItemRating' in df_filtered.columns:
            evergreen = df_filtered.groupby('Description').agg({
                'ItemRating': 'mean',
                'Quantity': 'sum',
                'Revenue': 'sum'
            }).query('ItemRating >= 3.5').nlargest(10, 'Quantity')
            st.dataframe(evergreen, use_container_width=True)
        else:
            st.info("ItemRating data required for Evergreen analysis")

    with tab4:
        st.subheader("Filtered Transaction Data")
        st.dataframe(df_filtered, use_container_width=True)

# Inventory Explorer Page
elif page == "Inventory Explorer":
    st.header("Inventory & Product Analysis")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Stock and Sales Insights")
        stock_summary = df_filtered.groupby('Description').agg({
            'Quantity': 'sum',
            'Revenue': 'sum',
            'Price': 'mean'
        }).rename(columns={'Quantity': 'Total Units Sold', 'Price': 'Avg Unit Price'})
        st.dataframe(stock_summary)
        
    with col2:
        st.subheader("Product Deep Dive")
        product_list = sorted(df_filtered['Description'].unique())
        if product_list:
            selected_prod = st.selectbox("Select Product", product_list)
            prod_data = df_filtered[df_filtered['Description'] == selected_prod]
            
            st.metric("Units Sold", int(prod_data['Quantity'].sum()))
            st.metric("Total Generated", f"${prod_data['Revenue'].sum():,.2f}")
        else:
            st.warning("No products available after filtering.")

# Financial Analytics Page
elif page == "Financial Analytics":
    st.header("Financial Performance & Profitability")
    
    col1, col2, col3 = st.columns(3)
    total_revenue_calc = df_filtered['Revenue'].sum()
    # Assuming 60% Cost of Goods Sold for profit calculation
    est_cogs = total_revenue_calc * 0.60 
    total_profit = total_revenue_calc - est_cogs
    
    with col1:
        st.metric("Total Revenue", f"${total_revenue_calc:,.2f}")
    with col2:
        st.metric("Estimated COGS", f"${est_cogs:,.2f}")
    with col3:
        st.metric("Total Profit", f"${total_profit:,.2f}", delta=f"40% Margin")
        
    st.divider()
    st.subheader("Cost vs. Return Analysis")
    st.write("Identifying products that are costly but give low returns (High Price / Low Volume).")
    
    # ROI Score = Price / (Quantity + 1) -> Higher score means more "costly/inefficient"
    roi_analysis = df_filtered.groupby('Description').agg({
        'Price': 'max',
        'Quantity': 'sum'
    })
    roi_analysis['ROI_Inefficiency_Score'] = roi_analysis['Price'] / (roi_analysis['Quantity'] + 1)
    costly_low_return = roi_analysis.nlargest(5, 'ROI_Inefficiency_Score')
    
    st.warning("Costly Products with Low Sales Volume (To Review):")
    st.dataframe(costly_low_return)

    st.subheader("Best Cash Inflow Sources")
    cash_inflow = df_filtered.groupby('Description')['Revenue'].sum().nlargest(5)
    st.bar_chart(cash_inflow)

# Operations Center Page
elif page == "Operations Center":
    st.header("Business Operations")
    
    tab_a, tab_b = st.tabs(["📝 Record Transaction", "📤 Export & Reports"])
    
    with tab_a:
        st.subheader("New Sale Entry")
        with st.form("new_sale"):
            col1, col2 = st.columns(2)
            with col1:
                new_item = st.text_input("Item Name")
                new_qty = st.number_input("Quantity", min_value=1)
            with col2:
                new_price = st.number_input("Unit Price", min_value=0.0)
                new_cat = st.selectbox("Category", ["Electronics", "Clothing", "Food", "Other"])
            
            if st.form_submit_button("Submit Transaction"):
                if new_item:
                    from finance_engine import get_record_by_id, save_inventory_item
                    
                    sale_id = f"SALE-{int(datetime.now().timestamp())}"
                    item_id = new_item.upper().replace(" ", "_")
                    
                    # Ensure item exists in inventory first
                    item = get_record_by_id(InventoryItem, item_id)
                    if not item:
                        # Create a new inventory entry if it doesn't exist
                        new_inv_item = InventoryItem(item_id, new_item, f"Category: {new_cat}", new_price*0.6, new_price, new_qty + 10, 5)
                        save_inventory_item(new_inv_item)
                    
                    # Record the sale
                    new_sale = Sale(sale_id, item_id, new_qty, new_price, datetime.now())
                    save_sale(new_sale)
                    
                    # Update stock levels
                    inventory_manager.update_inventory_after_sale(new_sale)
                    
                    st.success(f"✅ Successfully recorded sale of {new_item} and updated database!")
                    st.balloons()
                else:
                    st.error("Please enter an Item Name.")
                
    with tab_b:
        st.subheader("Generate Financial Statement")
        report_format = st.selectbox("Format", ["CSV", "Excel", "PDF"])
        
        if report_format == "CSV":
            csv_data = df_filtered.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Filtered Report (CSV)",
                data=csv_data,
                file_name=f'finance_report_{datetime.now().strftime("%Y%m%d")}.csv',
                mime='text/csv',
            )
        else:
            if st.button("Generate & Download"):
                st.warning(f"Note: {report_format} export requires additional libraries. Please use CSV for the evaluation.")
