import streamlit as st
import pandas as pd
import datetime
from fpdf import FPDF
import base64
from utils import format_currency, get_safe_currency_symbol

def generate_pdf(invoice_data, items_df):
    pdf = FPDF()
    pdf.add_page()
    
    # Colors
    primary_color = (200, 50, 50) # Red
    secondary_color = (50, 50, 200) # Blue
    
    # Header
    pdf.set_font('Arial', 'B', 20)
    pdf.set_text_color(*primary_color)
    pdf.cell(0, 10, st.session_state.company_info['name'], 0, 1, 'L')
    
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 5, st.session_state.company_info['address'], 0, 1, 'L')
    pdf.cell(0, 5, f"Contact: {st.session_state.company_info['contact']}", 0, 1, 'L')
    
    pdf.ln(10)
    
    # Invoice Details
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(100, 10, f"Bill To: {invoice_data['customer_name']}", 0, 0)
    pdf.cell(90, 10, f"Date: {invoice_data['date']}", 0, 1, 'R')
    pdf.cell(190, 10, f"Invoice #: {invoice_data['invoice_no']}", 0, 1, 'R')
    
    pdf.ln(5)
    
    # Table Header
    pdf.set_fill_color(*secondary_color)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(10, 10, '#', 1, 0, 'C', 1)
    pdf.cell(70, 10, 'Item', 1, 0, 'C', 1)
    pdf.cell(30, 10, 'Price', 1, 0, 'C', 1)
    pdf.cell(20, 10, 'Qty', 1, 0, 'C', 1)
    pdf.cell(30, 10, 'Tax', 1, 0, 'C', 1)
    pdf.cell(30, 10, 'Total', 1, 1, 'C', 1)
    
    # Table Rows
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 10)
    
    # Get currency symbol and sanitize for PDF
    raw_symbol = st.session_state.company_info.get('currency_symbol', '')
    symbol = get_safe_currency_symbol(raw_symbol)
    
    for i, item in enumerate(items_df.to_dict('records')):
        pdf.cell(10, 10, str(i+1), 1, 0, 'C')
        pdf.cell(70, 10, str(item['Item Name']), 1, 0, 'L')
        pdf.cell(30, 10, f"{symbol} {item['Price']}", 1, 0, 'R')
        pdf.cell(20, 10, str(item['Qty']), 1, 0, 'C')
        pdf.cell(30, 10, f"{symbol} {item['Tax Amount']:.2f}", 1, 0, 'R')
        pdf.cell(30, 10, f"{symbol} {item['Total']:.2f}", 1, 1, 'R')
        
    pdf.ln(5)
    
    # Totals
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(130, 10, '', 0, 0)
    pdf.cell(30, 10, 'Subtotal:', 0, 0, 'R')
    pdf.cell(30, 10, f"{symbol} {invoice_data['subtotal']:.2f}", 0, 1, 'R')
    
    pdf.cell(130, 10, '', 0, 0)
    pdf.cell(30, 10, 'Tax:', 0, 0, 'R')
    pdf.cell(30, 10, f"{symbol} {invoice_data['tax_total']:.2f}", 0, 1, 'R')
    
    pdf.cell(130, 10, '', 0, 0)
    pdf.cell(30, 10, 'Discount:', 0, 0, 'R')
    pdf.cell(30, 10, f"{symbol} {invoice_data['discount']:.2f}", 0, 1, 'R')
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(130, 10, '', 0, 0)
    pdf.cell(30, 10, 'Grand Total:', 0, 0, 'R')
    pdf.cell(30, 10, f"{symbol} {invoice_data['grand_total']:.2f}", 0, 1, 'R')
    
    # Footer
    pdf.ln(20)
    pdf.set_font('Arial', 'I', 8)
    pdf.cell(0, 5, "Thank you for your business!", 0, 1, 'C')
    pdf.cell(0, 5, "Terms & Conditions Apply.", 0, 1, 'C')
    
    return pdf.output(dest='S').encode('latin-1')

def app():
    st.title("🧾 Billing & Invoicing")
    
    if st.session_state.parties.empty or st.session_state.inventory.empty:
        st.warning("Please add Parties and Inventory items first!")
        return

    # Initialize Cart
    if 'cart' not in st.session_state:
        st.session_state.cart = []

    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Billing Details")
        customer = st.selectbox("Select Customer", st.session_state.parties[st.session_state.parties['Type'] == 'Customer']['Name'].unique())
        
        st.markdown("---")
        st.write("Add Items")
        
        item_name = st.selectbox("Select Item", st.session_state.inventory['Item Name'].unique())
        
        # Get Item Details
        selected_item = st.session_state.inventory[st.session_state.inventory['Item Name'] == item_name].iloc[0]
        current_stock = selected_item['Current Stock']
        price = selected_item['Sale Price']
        tax_rate = selected_item['Tax Rate']
        
        st.info(f"Available Stock: {current_stock} | Price: {format_currency(price)}")
        
        c1, c2 = st.columns(2)
        qty = c1.number_input("Quantity", min_value=1, max_value=int(current_stock) if current_stock > 0 else 1, value=1)
        discount_per = c2.number_input("Discount %", min_value=0.0, max_value=100.0, value=0.0)
        
        if st.button("Add to Cart"):
            if current_stock >= qty:
                tax_amount = (price * qty) * (tax_rate / 100)
                total_amount = (price * qty) + tax_amount - ((price * qty) * (discount_per / 100))
                
                cart_item = {
                    'Item Name': item_name,
                    'Price': price,
                    'Qty': qty,
                    'Tax Rate': tax_rate,
                    'Tax Amount': tax_amount,
                    'Discount %': discount_per,
                    'Total': total_amount
                }
                st.session_state.cart.append(cart_item)
                st.success("Item added!")
            else:
                st.error("Insufficient Stock!")

    with col2:
        st.subheader("Live Bill Preview")
        
        if st.session_state.cart:
            cart_df = pd.DataFrame(st.session_state.cart)
            
            subtotal = sum(item['Price'] * item['Qty'] for item in st.session_state.cart)
            tax_total = cart_df['Tax Amount'].sum()
            discount_total = sum((item['Price'] * item['Qty']) * (item['Discount %'] / 100) for item in st.session_state.cart)
            grand_total = cart_df['Total'].sum()
            
            # Professional Invoice Preview
            invoice_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
                </style>
            </head>
            <body>
            <div style="border: 2px solid #ddd; padding: 20px; background-color: white; border-radius: 8px;">
                <!-- Header -->
                <div style="border-bottom: 3px solid #d32f2f; padding-bottom: 15px; margin-bottom: 15px;">
                    <h2 style="color: #d32f2f; margin: 0;">{st.session_state.company_info['name']}</h2>
                    <p style="margin: 5px 0; font-size: 12px;">{st.session_state.company_info['address']}</p>
                    <p style="margin: 5px 0; font-size: 12px;">Contact: {st.session_state.company_info['contact']}</p>
                </div>
                
                <!-- Bill To & Invoice Info -->
                <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
                    <div>
                        <strong>Bill To:</strong><br>
                        <span style="font-size: 14px;">{customer}</span>
                    </div>
                    <div style="text-align: right;">
                        <strong>Date:</strong> {datetime.date.today().strftime("%Y-%m-%d")}<br>
                        <strong>Invoice #:</strong> INV-DRAFT
                    </div>
                </div>
                
                <!-- Items Table -->
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                    <thead>
                        <tr style="background-color: #3232c8; color: white;">
                            <th style="padding: 10px; text-align: center; border: 1px solid #ddd;">#</th>
                            <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Item</th>
                            <th style="padding: 10px; text-align: right; border: 1px solid #ddd;">Price</th>
                            <th style="padding: 10px; text-align: center; border: 1px solid #ddd;">Qty</th>
                            <th style="padding: 10px; text-align: right; border: 1px solid #ddd;">Tax</th>
                            <th style="padding: 10px; text-align: right; border: 1px solid #ddd;">Total</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for i, item in enumerate(st.session_state.cart):
                invoice_html += f"""
                        <tr style="background-color: {'#f9f9f9' if i % 2 == 0 else 'white'};">
                            <td style="padding: 8px; text-align: center; border: 1px solid #ddd;">{i+1}</td>
                            <td style="padding: 8px; text-align: left; border: 1px solid #ddd;">{item['Item Name']}</td>
                            <td style="padding: 8px; text-align: right; border: 1px solid #ddd;">{format_currency(item['Price'])}</td>
                            <td style="padding: 8px; text-align: center; border: 1px solid #ddd;">{item['Qty']}</td>
                            <td style="padding: 8px; text-align: right; border: 1px solid #ddd;">{format_currency(item['Tax Amount'])}</td>
                            <td style="padding: 8px; text-align: right; border: 1px solid #ddd;"><strong>{format_currency(item['Total'])}</strong></td>
                        </tr>
                """
            
            invoice_html += f"""
                    </tbody>
                </table>
                
                <!-- Totals -->
                <div style="text-align: right; margin-top: 20px;">
                    <div style="margin: 5px 0;">
                        <span style="display: inline-block; width: 120px; text-align: right;"><strong>Subtotal:</strong></span>
                        <span style="display: inline-block; width: 120px; text-align: right;">{format_currency(subtotal)}</span>
                    </div>
                    <div style="margin: 5px 0;">
                        <span style="display: inline-block; width: 120px; text-align: right;"><strong>Tax:</strong></span>
                        <span style="display: inline-block; width: 120px; text-align: right;">{format_currency(tax_total)}</span>
                    </div>
                    <div style="margin: 5px 0;">
                        <span style="display: inline-block; width: 120px; text-align: right;"><strong>Discount:</strong></span>
                        <span style="display: inline-block; width: 120px; text-align: right;">-{format_currency(discount_total)}</span>
                    </div>
                    <div style="margin: 10px 0; padding-top: 10px; border-top: 2px solid #d32f2f;">
                        <span style="display: inline-block; width: 120px; text-align: right; font-size: 18px;"><strong>Grand Total:</strong></span>
                        <span style="display: inline-block; width: 120px; text-align: right; font-size: 18px; color: #d32f2f;"><strong>{format_currency(grand_total)}</strong></span>
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="text-align: center; margin-top: 30px; padding-top: 15px; border-top: 1px solid #ddd; font-size: 11px; color: #666;">
                    <p style="margin: 5px 0;"><em>Thank you for your business!</em></p>
                    <p style="margin: 5px 0;">Terms & Conditions Apply.</p>
                </div>
            </div>
            </body>
            </html>
            """
            
            import streamlit.components.v1 as components
            
            # Render HTML using components to ensure full styling support and avoid markdown parsing issues
            components.html(invoice_html, height=600, scrolling=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Generate Invoice & Save"):
                # Deduct Stock
                for item in st.session_state.cart:
                    idx = st.session_state.inventory[st.session_state.inventory['Item Name'] == item['Item Name']].index[0]
                    st.session_state.inventory.at[idx, 'Current Stock'] -= item['Qty']
                
                # Save Invoice
                invoice_no = f"INV-{len(st.session_state.invoices) + 1001}"
                invoice_data = {
                    'invoice_no': invoice_no,
                    'date': datetime.date.today().strftime("%Y-%m-%d"),
                    'customer_name': customer,
                    'subtotal': subtotal,
                    'tax_total': tax_total,
                    'discount': discount_total,
                    'grand_total': grand_total,
                    'items': st.session_state.cart
                }
                st.session_state.invoices.append(invoice_data)
                
                # Generate PDF
                pdf_bytes = generate_pdf(invoice_data, cart_df)
                b64_pdf = base64.b64encode(pdf_bytes).decode('latin-1')
                
                href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{invoice_no}.pdf" style="text-decoration:none;"><button style="background-color:#FF4B4B;color:white;padding:10px 20px;border:none;border-radius:5px;cursor:pointer;font-size:14px;">📄 Download PDF Invoice</button></a>'
                st.markdown(href, unsafe_allow_html=True)
                
                st.success(f"Invoice {invoice_no} Saved Successfully!")
                st.session_state.cart = [] # Clear Cart
                
            if st.button("Clear Cart"):
                st.session_state.cart = []
                st.rerun()
        else:
            st.info("Cart is empty.")
