import streamlit as st
from PIL import Image
import pytesseract
import io
from datetime import datetime
from receipt_parser import ReceiptParser
from excel_processor_v2 import ExcelProcessorV2
import zipfile

# Page configuration
st.set_page_config(
    page_title="Avant Expense Report",
    page_icon="📄",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {padding: 2rem;}
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        padding: 0.75rem;
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

# Initialize session state
if 'receipts' not in st.session_state:
    st.session_state.receipts = []
if 'employee_info' not in st.session_state:
    st.session_state.employee_info = {
        'name': '',
        'account_project': '',
        'field': '',
        'date_submitted': datetime.now().strftime('%m/%d/%Y'),
        'signature_date': datetime.now().strftime('%m/%d/%Y')
    }

# Title
st.title("📄 Avant Expense Report Generator v2.0")
st.markdown("**Upload multiple receipts** and automatically generate your expense report!")

# Sidebar - Employee Information
with st.sidebar:
    st.header("👤 Employee Information")
    st.markdown("*Fill this once for all receipts*")
    
    name = st.text_input(
        "Name*",
        value=st.session_state.employee_info['name'],
        help="Required - your full name"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        date_submitted = st.date_input(
            "Date Submitted",
            value=datetime.strptime(st.session_state.employee_info['date_submitted'], '%m/%d/%Y')
        )
    with col2:
        signature_date = st.date_input(
            "Signature Date",
            value=datetime.strptime(st.session_state.employee_info['signature_date'], '%m/%d/%Y')
        )
    
    account_project = st.text_input(
        "Account/Project Number",
        value=st.session_state.employee_info['account_project']
    )
    
    field = st.text_input(
        "Field",
        value=st.session_state.employee_info['field']
    )
    
    # Update session state
    st.session_state.employee_info = {
        'name': name,
        'account_project': account_project,
        'field': field,
        'date_submitted': date_submitted.strftime('%m/%d/%Y'),
        'signature_date': signature_date.strftime('%m/%d/%Y')
    }
    
    if name:
        st.success(f"✅ {name}")
    else:
        st.warning("⚠️ Name required")
    
    st.markdown("---")
    st.markdown("### 📱 Mobile Support")
    st.info("This app works on mobile! Use your phone camera to capture receipts directly.")

# Main content
st.header("📸 Step 1: Upload Receipts")
st.markdown("Upload **one or multiple** receipt images or PDFs")

# File uploader - supports multiple files and PDFs
uploaded_files = st.file_uploader(
    "Choose files",
    type=['png', 'jpg', 'jpeg', 'pdf'],
    accept_multiple_files=True,
    help="📱 On mobile: Tap to use camera or choose from gallery. PDFs supported!"
)

if uploaded_files:
    st.success(f"✅ **{len(uploaded_files)} file(s)** uploaded")
    
    if st.button("🔍 Extract Data from All Receipts", type="primary"):
        st.session_state.receipts = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"Processing {idx+1}/{len(uploaded_files)}: {uploaded_file.name}...")
            
            try:
                # Handle PDF
                if uploaded_file.type == 'application/pdf':
                    try:
                        import pdf2image
                        images = pdf2image.convert_from_bytes(uploaded_file.read())
                        image = images[0]  # Use first page
                    except Exception as pdf_error:
                        st.error(f"PDF processing failed for {uploaded_file.name}. Please ensure poppler is installed.")
                        continue
                else:
                    image = Image.open(uploaded_file)
                
                # Perform OCR
                text = pytesseract.image_to_string(image)
                
                # Parse receipt
                parser = ReceiptParser()
                receipt_data = parser.parse(text)
                
                # Convert image to bytes for storage
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='JPEG')
                img_byte_arr = img_byte_arr.getvalue()
                
                # Store receipt
                st.session_state.receipts.append({
                    'filename': uploaded_file.name,
                    'data': receipt_data,
                    'image': img_byte_arr,
                    'category': 'Travel',
                    'from_location': '',
                    'to_location': '',
                    'ministry_purpose': ''
                })
                
            except Exception as e:
                st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
            
            progress_bar.progress((idx + 1) / len(uploaded_files))
        
        status_text.empty()
        progress_bar.empty()
        st.success("✅ All receipts processed! Review below.")
        st.rerun()

# Display and edit receipts
if st.session_state.receipts:
    st.markdown("---")
    st.header("📊 Step 2: Review & Categorize Receipts")
    st.markdown(f"**{len(st.session_state.receipts)} receipt(s)** ready to review")
    
    for idx, receipt in enumerate(st.session_state.receipts):
        with st.expander(f"📄 Receipt {idx + 1}: {receipt['filename']}", expanded=(idx==0)):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.image(receipt['image'], caption=receipt['filename'], use_column_width=True)
            
            with col2:
                st.subheader("Receipt Information")
                
                # Extracted data (editable)
                merchant = st.text_input(
                    "Merchant/Vendor",
                    value=receipt['data'].get('merchant', ''),
                    key=f"merchant_{idx}"
                )
                
                receipt_date = st.text_input(
                    "Receipt Date",
                    value=receipt['data'].get('date', ''),
                    key=f"date_{idx}",
                    help="Format: DD/MM/YYYY"
                )
                
                amount = st.number_input(
                    f"Amount ({receipt['data'].get('currency', 'EUR')})",
                    value=float(receipt['data'].get('total', 0.0)),
                    format="%.2f",
                    min_value=0.0,
                    key=f"amount_{idx}"
                )
                
                # Update receipt data
                receipt['data']['merchant'] = merchant
                receipt['data']['date'] = receipt_date
                receipt['data']['total'] = amount
                
                st.markdown("---")
                st.subheader("Categorization")
                
                # Category dropdown
                categories = [
                    "Travel",
                    "Advance",
                    "Ministry Entertainment",
                    "Other",
                    "Honorariums"
                ]
                
                selected_category = st.selectbox(
                    "Expense Category*",
                    categories,
                    index=categories.index(receipt.get('category', 'Travel')),
                    key=f"category_{idx}",
                    help="Select the type of expense"
                )
                receipt['category'] = selected_category
                
                # Category-specific fields
                if selected_category == 'Travel':
                    st.markdown("**Travel Details** *(required for Travel)*")
                    from_loc = st.text_input(
                        "From (Starting Location)*",
                        value=receipt.get('from_location', ''),
                        key=f"from_{idx}",
                        placeholder="e.g., Madrid"
                    )
                    to_loc = st.text_input(
                        "To (Destination)*",
                        value=receipt.get('to_location', ''),
                        key=f"to_{idx}",
                        placeholder="e.g., Barcelona"
                    )
                    receipt['from_location'] = from_loc
                    receipt['to_location'] = to_loc
                
                # Ministry purpose (required for all)
                purpose = st.text_area(
                    "Ministry Purpose*",
                    value=receipt.get('ministry_purpose', ''),
                    key=f"purpose_{idx}",
                    height=100,
                    placeholder="Describe the ministry purpose of this expense...",
                    help="Required for all expense categories"
                )
                receipt['ministry_purpose'] = purpose

    # Generate Report Section
    st.markdown("---")
    st.header("📋 Step 3: Generate Expense Report")
    
    # Validation
    validation_errors = []
    can_generate = True
    
    if not name:
        validation_errors.append("❌ **Employee name** is required (see sidebar)")
        can_generate = False
    
    for idx, receipt in enumerate(st.session_state.receipts):
        receipt_num = idx + 1
        
        if not receipt.get('ministry_purpose', '').strip():
            validation_errors.append(f"❌ Receipt {receipt_num}: **Ministry Purpose** is required")
            can_generate = False
        
        if receipt['category'] == 'Travel':
            if not receipt.get('from_location', '').strip():
                validation_errors.append(f"❌ Receipt {receipt_num}: **From location** required for Travel")
                can_generate = False
            if not receipt.get('to_location', '').strip():
                validation_errors.append(f"❌ Receipt {receipt_num}: **To location** required for Travel")
                can_generate = False
    
    # Display validation errors
    if validation_errors:
        st.warning("**Please fix the following issues:**")
        for error in validation_errors:
            st.markdown(error)
    else:
        st.success("✅ All required fields completed!")
    
    # Generate button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            "📋 Generate Expense Report",
            type="primary",
            disabled=not can_generate,
            use_container_width=True
        ):
            with st.spinner("Creating your expense report..."):
                try:
                    processor = ExcelProcessorV2()
                    
                    excel_buffer = processor.create_expense_report(
                        st.session_state.employee_info,
                        st.session_state.receipts
                    )
                    
                    # Create ZIP of all receipts
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                        for idx, receipt in enumerate(st.session_state.receipts):
                            filename = f"receipt_{idx+1:02d}_{receipt['filename']}"
                            zip_file.writestr(filename, receipt['image'])
                    zip_buffer.seek(0)
                    
                    # Success message
                    st.balloons()
                    st.markdown("""
                        <div class="success-box">
                            <h3>✅ Success!</h3>
                            <p>Your expense report has been generated with <strong>{}</strong> receipt(s).</p>
                        </div>
                    """.format(len(st.session_state.receipts)), unsafe_allow_html=True)
                    
                    # Download buttons
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.download_button(
                            label="📥 Download Expense Report (Excel)",
                            data=excel_buffer,
                            file_name=f"Avant_Expense_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    
                    with col_b:
                        st.download_button(
                            label="📥 Download All Receipts (ZIP)",
                            data=zip_buffer,
                            file_name=f"Receipts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                            mime="application/zip",
                            use_container_width=True
                        )
                    
                    # Next steps
                    st.markdown("""
                        ### 📧 Next Steps:
                        1. ✅ Download both files above
                        2. 📧 Email to: **finance@avant.org**
                        3. 📝 Subject: "Expense Report - {}"
                        4. 📎 Attach both the Excel file and ZIP of receipts
                    """.format(name))
                    
                except Exception as e:
                    st.error(f"❌ Error generating report: {str(e)}")
                    with st.expander("Error Details"):
                        st.exception(e)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p><strong>Avant Expense Report Generator v2.0</strong></p>
        <p>✨ New: Batch upload | 📱 Mobile camera support | 📄 PDF support | 🏷️ Category selection</p>
        <p style='font-size: 0.9em;'>Built with Streamlit | For assistance: it@avant.org</p>
    </div>
""", unsafe_allow_html=True)
