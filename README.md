# Avant Expense Report Generator v3.0

## 🎉 What's New in v3.0

### ALL 7 CRITICAL FIXES APPLIED:

1. ✅ **Date Format Standardized** - All dates in MM/DD/YYYY format
2. ✅ **Signature Location Fixed** - Now in row 24 (was incorrectly in row 11)
3. ✅ **Ministry Entertainment Row** - Corrected to row 61 (was 64)
4. ✅ **Other Category Row** - Corrected to row 111 (was 75)
5. ✅ **Ministry Entertainment "Who" Field** - Required field for person entertained
6. ✅ **Ministry Entertainment "Where" Field** - Auto-filled city, user confirmable
7. ✅ **Exchange Rates from Receipt Date** - Uses purchase date, not today

### BONUS FEATURES:

8. ✅ **Currency Selector** - EUR, USD, GBP first, then all major currencies
9. ✅ **City Auto-Detection** - Extracts city from receipt for Ministry Entertainment
10. ✅ **Spanish Month Names** - Handles "31 ene 2026" format

## 📋 Category-Specific Requirements

### Travel
- ✅ From location (required)
- ✅ To location (required)
- ✅ Ministry Purpose (required)

### Ministry Entertainment
- ✅ Who - Person being entertained (required)
- ✅ Where - City location (required, auto-filled)
- ✅ Ministry Purpose (required)

### All Other Categories
- ✅ Ministry Purpose (required)

## 🚀 Deployment

1. Delete all files in your GitHub `expense-report-webapp` repository
2. Upload ALL files from this folder
3. Commit changes
4. Streamlit auto-redeploys in ~30 seconds

## 📁 Files Included

- `app.py` - Main application with all fixes
- `excel_processor_v3.py` - Fixed row mapping and date handling
- `receipt_parser.py` - Date conversion and city extraction
- `requirements.txt` - Python dependencies
- `packages.txt` - System dependencies
- `Avant_2026_Expense_Report_Form.xlsx` - Template
- `README.md` - This file

## ✅ Testing Checklist

After deployment, verify:

- [ ] Dates display as MM/DD/YYYY everywhere
- [ ] Signature appears in Excel row 24
- [ ] Ministry Entertainment receipts go to row 61
- [ ] Other receipts go to row 111
- [ ] Ministry Entertainment shows Who/Where fields
- [ ] Currency dropdown shows EUR/USD/GBP first
- [ ] Exchange rate matches receipt date
- [ ] Spanish dates convert correctly ("31 ene 2026" → "01/31/2026")

## 📧 Support

Questions? it@avant.org

---

**v3.0** - March 2026 - All critical fixes applied
