# 📄 Avant Expense Report - Streamlit Web App

A web application that uses OCR to automatically extract data from receipt photos and generate Excel expense reports.

## ✨ Features

- 📸 Upload receipt photos from phone or computer
- 🔍 Automatic OCR text extraction
- 📊 Smart parsing of merchant, date, amounts, and line items
- 📋 Auto-fill Excel expense report template
- ⬇️ Download completed report and original receipt
- 🌐 Works on any device with a web browser

## 🚀 Quick Start - Deploy to Streamlit Cloud (FREE!)

### Step 1: Push to GitHub

1. Create a new GitHub repository called `expense-report-app`
2. Upload all files from this project
3. Make sure to include:
   - `app.py`
   - `receipt_parser.py`
   - `excel_processor.py`
   - `requirements.txt`
   - `packages.txt`
   - `Avant_2026_Expense_Report_Form.xlsx`

### Step 2: Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io
2. Sign in with your GitHub account
3. Click "New app"
4. Select:
   - Repository: `your-username/expense-report-app`
   - Branch: `main`
   - Main file path: `app.py`
5. Click "Deploy"
6. Wait 2-3 minutes for deployment
7. Your app is live! 🎉

You'll get a URL like: `https://your-username-expense-report-app.streamlit.app`

## 💻 Run Locally

### Prerequisites
- Python 3.8 or higher
- Tesseract OCR installed

### Install Tesseract

**Windows:**
```bash
# Download installer from:
https://github.com/UB-Mannheim/tesseract/wiki
# Run installer and add to PATH
```

**Mac:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

### Run the App

```bash
# Clone the repository
git clone https://github.com/your-username/expense-report-app.git
cd expense-report-app

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📱 Using the App

### From Computer:
1. Open the app URL in your browser
2. Click "Browse files" to upload a receipt photo
3. Click "Extract Data from Receipt"
4. Review the extracted information
5. Click "Generate Expense Report"
6. Download the Excel file and receipt image

### From Phone:
1. Open the app URL in your mobile browser
2. Tap "Browse files"
3. Choose "Camera" to take a photo OR "Photo Library" to upload
4. Follow the same steps as above
5. Download files directly to your phone

## 🏗️ Project Structure

```
expense-report-app/
├── app.py                              # Main Streamlit application
├── receipt_parser.py                   # OCR text parsing logic
├── excel_processor.py                  # Excel file generation
├── requirements.txt                    # Python dependencies
├── packages.txt                        # System dependencies (for Streamlit Cloud)
├── Avant_2026_Expense_Report_Form.xlsx # Excel template
└── README.md                           # This file
```

## 🔧 How It Works

1. **Upload**: User uploads a receipt image
2. **OCR**: Tesseract extracts text from the image
3. **Parse**: Regex patterns identify:
   - Merchant name
   - Date
   - Total amount
   - Line items (quantity × price)
   - Tax/VAT
4. **Excel**: Data populates the Avant expense report template
5. **Download**: User gets Excel report + original receipt

## 📊 Data Extracted

- ✅ Merchant/establishment name
- ✅ Address
- ✅ Date and time
- ✅ Individual line items
- ✅ Quantities and prices
- ✅ Subtotals and total
- ✅ Tax information (VAT/IVA)

## 🎨 Customization

### Change Expense Category
Edit `excel_processor.py` line 64:
```python
self._set_cell_value(sheet, row, 13, "8420 - Travel")  # Change category code
```

### Add More Parsing Patterns
Edit `receipt_parser.py` to add support for different receipt formats.

### Customize UI
Edit `app.py` CSS section to change colors, fonts, layout.

## 🐛 Troubleshooting

### OCR not working?
- Make sure receipt image is clear and well-lit
- Check that Tesseract is installed: `tesseract --version`
- Try with a different receipt photo

### Excel template not found?
- Ensure `Avant_2026_Expense_Report_Form.xlsx` is in the project directory
- App will create a simple report if template is missing

### App won't deploy to Streamlit Cloud?
- Check that all files are committed to GitHub
- Verify `requirements.txt` and `packages.txt` are present
- Check Streamlit Cloud deployment logs for errors

## 📝 Next Steps

After downloading your files:

1. ✅ Review the extracted data for accuracy
2. ✅ Edit the Excel file if needed (add employee name, etc.)
3. ✅ Email both files to finance@avant.org
4. ✅ Keep copies for your records

## 🆓 Deployment Costs

- **Streamlit Cloud**: FREE forever
- **GitHub**: FREE
- **Domain**: Optional (FREE subdomain provided)
- **Total Cost**: $0

## 🔒 Privacy & Security

- 📄 Files are processed in your browser session only
- 🗑️ No data is stored permanently
- 🔐 HTTPS encryption on Streamlit Cloud
- 👁️ Only you can see your uploaded receipts

## 📖 Tech Stack

- **Frontend**: Streamlit
- **OCR**: Tesseract + Pytesseract
- **Excel**: OpenPyXL
- **Image Processing**: Pillow (PIL)
- **Hosting**: Streamlit Cloud (free)

## 🤝 Contributing

Found a bug or want to add a feature? 
1. Fork the repository
2. Make your changes
3. Submit a pull request

## 📄 License

Proprietary - Avant Ministries Internal Use

## 🆘 Support

Issues? Contact: it@avant.org

---

**Built with ❤️ for Avant Ministries**

Version 1.0.0 | Last updated: February 2026
