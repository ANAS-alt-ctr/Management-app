import streamlit as st
import pandas as pd
from utils import format_currency

def app():
    st.title("📦 Inventory Management")
    
    tab1, tab2 = st.tabs(["Add New Item", "Stock Summary"])
    
    with tab1:
        st.subheader("Add Item")
        with st.form("add_item_form"):
            col1, col2 = st.columns(2)
            with col1:
                item_name = st.text_input("Item Name")
                sku = st.text_input("SKU / Item Code")
                sale_price = st.number_input("Sale Price", min_value=0.0, value=0.0)
            with col2:
                purchase_price = st.number_input("Purchase Price", min_value=0.0, value=0.0)
                tax_rate = st.number_input("Tax Rate (%)", min_value=0.0, value=0.0)
                current_stock = st.number_input("Opening Stock", min_value=0, value=0)
            
            if st.form_submit_button("Add Item"):
                if item_name:
                    # Check if SKU already exists
                    if not st.session_state.inventory.empty and sku and sku in st.session_state.inventory['SKU'].values:
                        st.error("SKU already exists!")
                    else:
                        new_item = pd.DataFrame([{
                            'Item Name': item_name,
                            'SKU': sku,
                            'Sale Price': sale_price,
                            'Purchase Price': purchase_price,
                            'Tax Rate': tax_rate,
                            'Current Stock': current_stock
                        }])
                        st.session_state.inventory = pd.concat([st.session_state.inventory, new_item], ignore_index=True)
                        st.success("Item added successfully!")
                else:
                    st.error("Item Name is required!")

    with tab2:
        st.subheader("Current Stock")
        if not st.session_state.inventory.empty:
            # Highlight low stock
            def highlight_low_stock(s):
                is_low = s['Current Stock'] < 5 # Threshold for low stock
                return ['background-color: #ffcccc' if is_low else '' for _ in s]

            # Display with formatting
            display_df = st.session_state.inventory.copy()
            display_df['Sale Price'] = display_df['Sale Price'].apply(format_currency)
            display_df['Purchase Price'] = display_df['Purchase Price'].apply(format_currency)
            
            st.dataframe(display_df.style.apply(highlight_low_stock, axis=1), use_container_width=True)
            
            # Edit Stock
            st.divider()
            st.subheader("Quick Stock Adjustment")
            item_to_edit = st.selectbox("Select Item", st.session_state.inventory['Item Name'].unique())
            if item_to_edit:
                current_qty = st.session_state.inventory.loc[st.session_state.inventory['Item Name'] == item_to_edit, 'Current Stock'].values[0]
                new_qty = st.number_input(f"Update Stock for {item_to_edit}", value=int(current_qty))
                if st.button("Update Stock"):
                    st.session_state.inventory.loc[st.session_state.inventory['Item Name'] == item_to_edit, 'Current Stock'] = new_qty
                    st.success("Stock updated!")
                    st.rerun()
        else:
            st.info("No items in inventory.")
