import streamlit as st
from utils import get_currency_symbol

def app():
    st.title("⚙️ Global Settings")
    
    st.subheader("Company Profile")
    
    with st.form("company_settings"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Business Name", value=st.session_state.company_info['name'])
            contact = st.text_input("Contact Number", value=st.session_state.company_info['contact'])
            
        with col2:
            address = st.text_area("Business Address", value=st.session_state.company_info['address'])
            
        st.subheader("Currency Settings")
        currency_options = ['PKR', 'INR', 'USD', 'EUR']
        current_currency = st.session_state.company_info['currency']
        
        # Find index of current currency
        try:
            curr_index = currency_options.index(current_currency)
        except ValueError:
            curr_index = 0
            
        selected_currency = st.selectbox("Select Currency", currency_options, index=curr_index)
        
        if st.form_submit_button("Save Settings"):
            st.session_state.company_info['name'] = name
            st.session_state.company_info['contact'] = contact
            st.session_state.company_info['address'] = address
            st.session_state.company_info['currency'] = selected_currency
            st.session_state.company_info['currency_symbol'] = get_currency_symbol(selected_currency)
            st.success("Settings saved successfully!")
            st.rerun()

    st.divider()
    st.subheader("⚠️ Danger Zone")
    if st.button("Reset Application Data", type="primary"):
        # Confirm reset
        if 'confirm_reset' not in st.session_state:
            st.session_state.confirm_reset = True
            st.warning("Are you sure? This will delete all data (Parties, Inventory, Invoices). Click again to confirm.")
        else:
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
