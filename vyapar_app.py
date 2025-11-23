import streamlit as st
import utils
from modules import dashboard, parties, inventory, billing, settings

# Page Config
st.set_page_config(
    page_title="Vyapar Clone",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Red/Blue/White Theme
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        background-color: #d32f2f;
        color: white;
        border-radius: 5px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #b71c1c;
    }
    .css-1d391kg {
        padding-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize Session State
utils.init_session_state()

# Sidebar Navigation
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2534/2534204.png", width=50)
    st.title(st.session_state.company_info['name'])
    st.markdown("---")
    
    menu = st.radio(
        "Navigation",
        ["Dashboard", "Parties", "Inventory", "Billing", "Settings"],
        index=0
    )
    
    st.markdown("---")
    st.caption(f"Current Currency: {st.session_state.company_info['currency']}")

# Routing
if menu == "Dashboard":
    dashboard.app()
elif menu == "Parties":
    parties.app()
elif menu == "Inventory":
    inventory.app()
elif menu == "Billing":
    billing.app()
elif menu == "Settings":
    settings.app()
