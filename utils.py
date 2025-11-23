import streamlit as st
import pandas as pd

def init_session_state():
    """Initialize session state variables if they don't exist."""
    if 'parties' not in st.session_state:
        st.session_state.parties = pd.DataFrame(columns=[
            'Name', 'Phone', 'Email', 'Type', 'Tax ID', 'Opening Balance'
        ])
    
    if 'inventory' not in st.session_state:
        st.session_state.inventory = pd.DataFrame(columns=[
            'Item Name', 'SKU', 'Sale Price', 'Purchase Price', 'Tax Rate', 'Current Stock'
        ])
        
    if 'invoices' not in st.session_state:
        st.session_state.invoices = []
        
    if 'company_info' not in st.session_state:
        st.session_state.company_info = {
            'name': 'My Business',
            'address': '123 Business St, City, Country',
            'contact': '+92 300 1234567',
            'currency': 'PKR',
            'currency_symbol': '₨'
        }

def format_currency(amount):
    """Format amount with the selected currency symbol."""
    symbol = st.session_state.company_info.get('currency_symbol', '₨')
    return f"{symbol} {amount:,.2f}"

def get_currency_symbol(currency_code):
    """Get symbol for currency code."""
    symbols = {
        'PKR': '₨',
        'INR': '₹',
        'USD': '$',
        'EUR': '€'
    }
    return symbols.get(currency_code, '₨')

def get_safe_currency_symbol(symbol):
    """Get ASCII-safe symbol for PDF generation."""
    if '₨' in symbol: return 'Rs.'
    if '₹' in symbol: return 'Rs.'
    if '€' in symbol: return 'EUR'
    if '$' in symbol: return '$'
    return symbol
