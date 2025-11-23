import streamlit as st
import pandas as pd
from utils import format_currency

def app():
    st.title("📊 Dashboard")
    
    # Calculate Metrics
    total_sales = sum(inv['grand_total'] for inv in st.session_state.invoices)
    
    # Calculate Purchases (Approximation based on inventory value for MVP)
    # In a real app, we would have a separate Purchase module
    total_purchases = (st.session_state.inventory['Purchase Price'] * st.session_state.inventory['Current Stock']).sum() if not st.session_state.inventory.empty else 0.0
    
    receivables = 0.0 # Placeholder for credit sales
    payables = 0.0 # Placeholder
    
    # Display Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Sales", format_currency(total_sales))
    with col2:
        st.metric("Inventory Value", format_currency(total_purchases))
    with col3:
        st.metric("Receivables", format_currency(receivables))
    with col4:
        st.metric("Payables", format_currency(payables))
        
    st.divider()
    
    # Recent Invoices
    st.subheader("Recent Invoices")
    if st.session_state.invoices:
        recent_df = pd.DataFrame(st.session_state.invoices)
        # Select columns to display
        display_df = recent_df[['invoice_no', 'date', 'customer_name', 'grand_total']]
        display_df['grand_total'] = display_df['grand_total'].apply(format_currency)
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("No invoices generated yet.")
        
    # Low Stock Alert
    st.subheader("⚠️ Low Stock Alerts")
    if not st.session_state.inventory.empty:
        low_stock = st.session_state.inventory[st.session_state.inventory['Current Stock'] < 5]
        if not low_stock.empty:
            st.dataframe(low_stock[['Item Name', 'Current Stock']], use_container_width=True)
        else:
            st.success("All stock levels are healthy.")
    else:
        st.info("No inventory data.")
