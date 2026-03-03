import streamlit as st
from PIL import Image
import pytesseract
import re
from datetime import datetime
import io
import base64
from receipt_parser import ReceiptParser
from excel_processor import ExcelProcessor

# Page configuration
st.set_page_config(
    page_title="Avant Expense Report",
    page_icon="📄",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        padding: 0.5rem;
        font-size: 1.1rem;
        border-radius: 8px;
    }
    .success-box {
        padding: 1rem;
        border-radius: 8px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("📄 Avant Expense Report Generator")
st.markdown("Upload a receipt photo and automatically generate your expense report!")

# Initialize session state
if 'receipt_data' not in st.session_state:
    st.session_state.receipt_data = None
if 'excel_file' not in st.session_state:
    st.session_state.excel_file = None

# Create two columns
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📸 Step 1: Upload Receipt")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a receipt image",
        type=['png', 'jpg', 'jpeg'],
        help="Upload a clear photo of your receipt"
    )
    
    if uploaded_file is not None:
        # Display the image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Receipt", use_column_width=True)
        
        # Process button
        if st.button("🔍 Extract Data from Receipt"):
            with st.spinner("Processing receipt with OCR..."):
                try:
                    # Perform OCR
                    text = pytesseract.image_to_string(image)
                    
                    # Parse receipt data
                    parser = ReceiptParser()
                    receipt_data = parser.parse(text)
                    
                    # Store in session state
                    st.session_state.receipt_data = receipt_data
                    
                    st.success("✅ Receipt processed successfully!")
                    
                except Exception as e:
                    st.error(f"Error processing receipt: {str(e)}")
                    st.error("Please try with a clearer image or check that Tesseract is installed.")

with col2:
    st.header("📊 Step 2: Review & Generate")
    
    if st.session_state.receipt_data:
        receipt_data = st.session_state.receipt_data
        
        # Display extracted data
        st.subheader("Extracted Information")
        
        # Editable fields
        merchant = st.text_input("Merchant", value=receipt_data.get('merchant', ''))
        date = st.text_input("Date", value=receipt_data.get('date', ''))
        total = st.number_input("Total Amount (€)", value=receipt_data.get('total', 0.0), format="%.2f")
        
        st.subheader("Line Items")
        items = receipt_data.get('items', [])
        
        if items:
            for i, item in enumerate(items):
                with st.expander(f"Item {i+1}: {item.get('description', 'Unknown')}"):
                    st.write(f"**Quantity:** {item.get('quantity', 1)}")
                    st.write(f"**Unit Price:** €{item.get('unit_price', 0):.2f}")
                    st.write(f"**Total:** €{item.get('amount', 0):.2f}")
        else:
            st.info("No line items detected. Single expense entry will be created.")
        
        # Generate Excel button
        if st.button("📋 Generate Expense Report"):
            with st.spinner("Creating Excel file..."):
                try:
                    processor = ExcelProcessor()
                    
                    # Update receipt data with edited values
                    receipt_data['merchant'] = merchant
                    receipt_data['date'] = date
                    receipt_data['total'] = total
                    
                    # Generate Excel file
                    excel_buffer = processor.create_expense_report(receipt_data)
                    
                    # Store in session state
                    st.session_state.excel_file = excel_buffer
                    
                    st.success("✅ Expense report generated!")
                    
                except Exception as e:
                    st.error(f"Error generating report: {str(e)}")
    
    else:
        st.info("👆 Upload and process a receipt to continue")

# Download section
if st.session_state.excel_file:
    st.markdown("---")
    st.header("📥 Step 3: Download Report")
    
    col_download1, col_download2 = st.columns(2)
    
    with col_download1:
        # Download Excel button
        st.download_button(
            label="⬇️ Download Expense Report (Excel)",
            data=st.session_state.excel_file,
            file_name=f"expense_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with col_download2:
        # Download receipt image button
        if uploaded_file:
            st.download_button(
                label="⬇️ Download Receipt Image",
                data=uploaded_file.getvalue(),
                file_name=f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
                mime="image/jpeg"
            )
    
    # Email instructions
    st.markdown("""
        <div class="success-box">
            <h4>📧 Next Steps:</h4>
            <ol>
                <li>Download both the expense report and receipt image</li>
                <li>Compose an email to finance@avant.org</li>
                <li>Attach both files</li>
                <li>Send!</li>
            </ol>
        </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>Avant Expense Report Generator v1.0 | Built with Streamlit</p>
        <p>Having issues? Make sure the receipt is clear and well-lit.</p>
    </div>
""", unsafe_allow_html=True)
