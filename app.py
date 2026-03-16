import streamlit as st
from PIL import Image
import pytesseract
import io
from datetime import datetime
from receipt_parser import ReceiptParser
from excel_processor_v3 import ExcelProcessorV3
import zipfile

st.set_page_config(page_title="Avant Expense Report", page_icon="📄", layout="wide")

st.markdown("""
    <style>
    .main {padding: 2rem;}
    .stButton>button {width: 100%; background-color: #4CAF50; color: white; padding: 0.75rem; font-size: 1.1rem; border-radius: 8px;}
    </style>
""", unsafe_allow_html=True)

def compress_image(image, max_width=1920, quality=85):
    """Compress image for faster mobile upload and processing"""
    # Convert to RGB if needed (handles RGBA, P, etc.)
    if image.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', image.size, (255, 255, 255))
        if image.mode == 'P':
            image = image.convert('RGBA')
        background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
        image = background
    elif image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Resize if too large
    if image.width > max_width:
        ratio = max_width / image.width
        new_height = int(image.height * ratio)
        image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)
        print(f"📏 Resized image to {max_width}x{new_height}")
    
    # Compress to JPEG
    output = io.BytesIO()
    image.save(output, format='JPEG', quality=quality, optimize=True)
    output.seek(0)
    compressed_size = len(output.getvalue())
    print(f"📦 Compressed to {compressed_size / 1024:.1f} KB")
    
    return Image.open(output)

if 'receipts' not in st.session_state:
    st.session_state.receipts = []
if 'employee_info' not in st.session_state:
    st.session_state.employee_info = {
        'name': '', 'account_project': '', 'field': '',
        'date_submitted': datetime.now().strftime('%m/%d/%Y'),
        'signature_date': datetime.now().strftime('%m/%d/%Y')
    }

st.title("📄 Avant Expense Report Generator v3.0")
st.markdown("**Upload multiple receipts** and automatically generate your expense report!")

with st.sidebar:
    st.header("👤 Employee Information")
    st.markdown("*Fill this once for all receipts*")
    
    name = st.text_input("Name*", value=st.session_state.employee_info['name'], help="Required - your full name")
    
    col1, col2 = st.columns(2)
    with col1:
        date_submitted = st.date_input("Date Submitted", value=datetime.strptime(st.session_state.employee_info['date_submitted'], '%m/%d/%Y'))
    with col2:
        signature_date = st.date_input("Signature Date", value=datetime.strptime(st.session_state.employee_info['signature_date'], '%m/%d/%Y'))
    
    account_project = st.text_input("Account/Project Number", value=st.session_state.employee_info['account_project'])
    field = st.text_input("Field", value=st.session_state.employee_info['field'])
    
    st.session_state.employee_info = {
        'name': name, 'account_project': account_project, 'field': field,
        'date_submitted': date_submitted.strftime('%m/%d/%Y'),
        'signature_date': signature_date.strftime('%m/%d/%Y')
    }
    
    if name:
        st.success(f"✅ {name}")
    else:
        st.warning("⚠️ Name required")
    
    st.markdown("---")
    st.info("📱 **Mobile Tip:** Large photos are automatically compressed for faster upload!")

st.header("📸 Step 1: Upload Receipts")
st.markdown("Upload **one or multiple** receipt images or PDFs")

# Increase file size limit and add helpful message
uploaded_files = st.file_uploader(
    "Choose files", 
    type=['png', 'jpg', 'jpeg', 'pdf'], 
    accept_multiple_files=True, 
    help="📱 Mobile: Camera photos are automatically compressed. Max 200MB per file.",
    key="file_uploader"
)

if uploaded_files:
    # Show file info
    total_size = sum(f.size for f in uploaded_files) / (1024 * 1024)
    st.success(f"✅ **{len(uploaded_files)} file(s)** uploaded ({total_size:.1f} MB total)")
    
    if st.button("🔍 Extract Data from All Receipts", type="primary"):
        st.session_state.receipts = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"Processing {idx+1}/{len(uploaded_files)}: {uploaded_file.name}...")
            
            try:
                # Check file size
                file_size_mb = uploaded_file.size / (1024 * 1024)
                if file_size_mb > 15:
                    st.warning(f"⚠️ {uploaded_file.name} is {file_size_mb:.1f}MB - compressing for faster processing...")
                
                if uploaded_file.type == 'application/pdf':
                    try:
                        import pdf2image
                        images = pdf2image.convert_from_bytes(uploaded_file.read())
                        image = images[0]
                        if file_size_mb > 5:
                            image = compress_image(image)
                    except Exception:
                        st.error(f"PDF processing failed for {uploaded_file.name}")
                        continue
                else:
                    image = Image.open(uploaded_file)
                    
                    # Compress large images automatically
                    if file_size_mb > 3 or image.width > 2000:
                        st.info(f"📦 Compressing {uploaded_file.name} for faster processing...")
                        image = compress_image(image)
                
                # Perform OCR
                text = pytesseract.image_to_string(image)
                parser = ReceiptParser()
                receipt_data = parser.parse(text)
                
                # Convert image to bytes for storage
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='JPEG', quality=85)
                img_byte_arr = img_byte_arr.getvalue()
                
                st.session_state.receipts.append({
                    'filename': uploaded_file.name,
                    'data': receipt_data,
                    'image': img_byte_arr,
                    'category': 'Travel',
                    'currency': receipt_data.get('currency', 'EUR'),
                    'from_location': '', 'to_location': '',
                    'who': '', 'where': '',
                    'ministry_purpose': ''
                })
                
            except Exception as e:
                st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
            
            progress_bar.progress((idx + 1) / len(uploaded_files))
        
        status_text.empty()
        progress_bar.empty()
        st.success("✅ All receipts processed!")
        st.rerun()

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
                
                merchant = st.text_input("Merchant/Vendor", value=receipt['data'].get('merchant', ''), key=f"merchant_{idx}")
                receipt_date = st.text_input("Receipt Date (MM/DD/YYYY)", value=receipt['data'].get('date', ''), key=f"date_{idx}", help="Format: MM/DD/YYYY")
                
                # Currency selector with top 3 first
                currencies = [
                    ('EUR', '€ Euro'), ('USD', '$ US Dollar'), ('GBP', '£ British Pound'), None,
                    ('JPY', '¥ Japanese Yen'), ('CHF', 'CHF Swiss Franc'), ('CAD', 'C$ Canadian Dollar'),
                    ('AUD', 'A$ Australian Dollar'), ('CNY', '¥ Chinese Yuan'), ('INR', '₹ Indian Rupee'),
                    ('MXN', '$ Mexican Peso'), ('BRL', 'R$ Brazilian Real'),
                ]
                
                currency_display = []
                currency_map = {}
                for curr in currencies:
                    if curr is None:
                        currency_display.append('---')
                    else:
                        label = f"{curr[0]} - {curr[1]}"
                        currency_display.append(label)
                        currency_map[label] = curr[0]
                
                current_currency = receipt.get('currency', 'EUR')
                try:
                    current_idx = [c[0] for c in currencies if c].index(current_currency)
                except:
                    current_idx = 0
                
                selected_currency_str = st.selectbox("Currency", currency_display, index=current_idx, key=f"currency_{idx}")
                if selected_currency_str != '---':
                    receipt['currency'] = currency_map[selected_currency_str]
                
                amount = st.number_input(f"Amount ({receipt['currency']})", value=float(receipt['data'].get('total', 0.0)), format="%.2f", min_value=0.0, key=f"amount_{idx}")
                
                receipt['data']['merchant'] = merchant
                receipt['data']['date'] = receipt_date
                receipt['data']['total'] = amount
                
                st.markdown("---")
                st.subheader("Categorization")
                
                categories = ["Travel", "Advance", "Ministry Entertainment", "Other", "Honorariums"]
                selected_category = st.selectbox("Expense Category*", categories, index=categories.index(receipt.get('category', 'Travel')), key=f"category_{idx}")
                receipt['category'] = selected_category
                
                if selected_category == 'Travel':
                    st.markdown("**Travel Details** *(required)*")
                    from_loc = st.text_input("From (Starting Location)*", value=receipt.get('from_location', ''), key=f"from_{idx}", placeholder="e.g., Madrid")
                    to_loc = st.text_input("To (Destination)*", value=receipt.get('to_location', ''), key=f"to_{idx}", placeholder="e.g., Barcelona")
                    receipt['from_location'] = from_loc
                    receipt['to_location'] = to_loc
                
                elif selected_category == 'Ministry Entertainment':
                    st.markdown("**Ministry Entertainment Details** *(required)*")
                    who = st.text_input("Who (Person Being Entertained)*", value=receipt.get('who', ''), key=f"who_{idx}", placeholder="e.g., Pastor John", help="Who was entertained?")
                    detected_city = receipt['data'].get('city', receipt['data'].get('address', '').split(',')[0] if ',' in receipt['data'].get('address', '') else '')
                    where = st.text_input("Where (City)*", value=receipt.get('where', detected_city), key=f"where_{idx}", placeholder="e.g., Madrid", help="City where entertainment took place")
                    receipt['who'] = who
                    receipt['where'] = where
                
                purpose = st.text_area("Ministry Purpose*", value=receipt.get('ministry_purpose', ''), key=f"purpose_{idx}", height=100, placeholder="Describe the ministry purpose...", help="Required for all categories")
                receipt['ministry_purpose'] = purpose

    st.markdown("---")
    st.header("📋 Step 3: Generate Expense Report")
    
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
        
        elif receipt['category'] == 'Ministry Entertainment':
            if not receipt.get('who', '').strip():
                validation_errors.append(f"❌ Receipt {receipt_num}: **Who** is required for Ministry Entertainment")
                can_generate = False
            if not receipt.get('where', '').strip():
                validation_errors.append(f"❌ Receipt {receipt_num}: **Where** is required for Ministry Entertainment")
                can_generate = False
    
    if validation_errors:
        st.warning("**Please fix the following issues:**")
        for error in validation_errors:
            st.markdown(error)
    else:
        st.success("✅ All required fields completed!")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📋 Generate Expense Report", type="primary", disabled=not can_generate, use_container_width=True):
            with st.spinner("Creating your expense report..."):
                try:
                    processor = ExcelProcessorV3()
                    excel_buffer = processor.create_expense_report(st.session_state.employee_info, st.session_state.receipts)
                    
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                        for idx, receipt in enumerate(st.session_state.receipts):
                            filename = f"receipt_{idx+1:02d}_{receipt['filename']}"
                            zip_file.writestr(filename, receipt['image'])
                    zip_buffer.seek(0)
                    
                    st.balloons()
                    st.markdown(f"""
                        <div style='padding: 1rem; border-radius: 8px; background-color: #d4edda; border: 1px solid #c3e6cb; color: #155724; margin: 1rem 0;'>
                            <h3>✅ Success!</h3>
                            <p>Your expense report has been generated with <strong>{len(st.session_state.receipts)}</strong> receipt(s).</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.download_button("📥 Download Expense Report (Excel)", data=excel_buffer, file_name=f"Avant_Expense_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
                    with col_b:
                        st.download_button("📥 Download All Receipts (ZIP)", data=zip_buffer, file_name=f"Receipts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip", mime="application/zip", use_container_width=True)
                    
                    st.markdown(f"""
                        ### 📧 Next Steps:
                        1. ✅ Download both files above
                        2. 📧 Email to: **finance@avant.org**
                        3. 📝 Subject: "Expense Report - {name}"
                        4. 📎 Attach both the Excel file and ZIP of receipts
                    """)
                    
                except Exception as e:
                    st.error(f"❌ Error generating report: {str(e)}")
                    with st.expander("Error Details"):
                        st.exception(e)

st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p><strong>Avant Expense Report Generator v3.1</strong></p>
        <p>✨ Mobile optimized | 📦 Auto-compression | 📱 Works on any device</p>
        <p style='font-size: 0.9em;'>Built with Streamlit | For assistance: it@avant.org</p>
    </div>
""", unsafe_allow_html=True)
