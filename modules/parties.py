import streamlit as st
import pandas as pd
from utils import format_currency

def app():
    st.title("👥 Party Management")
    
    tab1, tab2 = st.tabs(["Add New Party", "View Parties"])
    
    with tab1:
        st.subheader("Add Customer / Supplier")
        with st.form("add_party_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Party Name")
                phone = st.text_input("Phone Number")
                email = st.text_input("Email")
            with col2:
                party_type = st.selectbox("Party Type", ["Customer", "Supplier"])
                tax_id = st.text_input("Tax ID (GST/NTN)")
                opening_balance = st.number_input("Opening Balance", min_value=0.0, value=0.0)
            
            if st.form_submit_button("Add Party"):
                if name:
                    new_party = pd.DataFrame([{
                        'Name': name,
                        'Phone': phone,
                        'Email': email,
                        'Type': party_type,
                        'Tax ID': tax_id,
                        'Opening Balance': opening_balance
                    }])
                    st.session_state.parties = pd.concat([st.session_state.parties, new_party], ignore_index=True)
                    st.success(f"{party_type} added successfully!")
                else:
                    st.error("Name is required!")

    with tab2:
        st.subheader("All Parties")
        if not st.session_state.parties.empty:
            # Display with formatted currency for balance (visual only)
            display_df = st.session_state.parties.copy()
            display_df['Opening Balance'] = display_df['Opening Balance'].apply(format_currency)
            st.dataframe(display_df, use_container_width=True)
            
            # Simple Delete Functionality
            party_to_delete = st.selectbox("Select Party to Delete", st.session_state.parties['Name'].unique(), index=None, placeholder="Select to delete...")
            if party_to_delete:
                if st.button(f"Delete {party_to_delete}"):
                    st.session_state.parties = st.session_state.parties[st.session_state.parties['Name'] != party_to_delete]
                    st.success("Party deleted!")
                    st.rerun()
        else:
            st.info("No parties added yet.")
