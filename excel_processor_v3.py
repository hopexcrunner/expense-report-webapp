from openpyxl import load_workbook
from datetime import datetime
import io, os, requests

class ExcelProcessorV3:
    def __init__(self):
        self.template_path = "Avant_2026_Expense_Report_Form.xlsx"
        self.CATEGORY_ROWS = {
            'Travel': 42,
            'Advance': 37,
            'Ministry Entertainment': 61,
            'Other': 111,
            'Honorariums': 165
        }
    
    def get_exchange_rate(self, from_currency, to_currency, date_str):
        """Get exchange rate using RECEIPT DATE"""
        if from_currency == to_currency:
            return 1.0
        try:
            date_obj = None
            for fmt in ['%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d']:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    break
                except:
                    continue
            
            if not date_obj:
                date_obj = datetime.now()
            
            date_formatted = date_obj.strftime('%Y-%m-%d')
            url = f"https://api.exchangerate.host/{date_formatted}"
            params = {'base': from_currency, 'symbols': to_currency}
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if 'rates' in data and to_currency in data['rates']:
                    return float(data['rates'][to_currency])
        except Exception:
            pass
        
        fallback_rates = {
            ('EUR', 'USD'): 1.08, ('USD', 'EUR'): 0.93, ('GBP', 'USD'): 1.27,
            ('GBP', 'EUR'): 1.17, ('USD', 'GBP'): 0.79, ('EUR', 'GBP'): 0.85
        }
        return fallback_rates.get((from_currency, to_currency), 1.0)
    
    def create_expense_report(self, employee_info, receipts):
        if not os.path.exists(self.template_path):
            return self._create_simple_report(employee_info, receipts)
        
        wb = load_workbook(self.template_path)
        sheet = wb['Expense Report']
        
        # Employee info - check if cells are merged before writing
        self._set_cell_value_safe(sheet, 6, 3, employee_info.get('name', ''))
        self._set_cell_value_safe(sheet, 6, 7, employee_info.get('date_submitted', ''))
        
        if employee_info.get('account_project'):
            self._set_cell_value_safe(sheet, 9, 3, employee_info.get('account_project'))
        if employee_info.get('field'):
            self._set_cell_value_safe(sheet, 9, 7, employee_info.get('field'))
        
        # Signature in ROW 24
        self._set_cell_value_safe(sheet, 24, 3, employee_info.get('name', ''))
        self._set_cell_value_safe(sheet, 24, 7, employee_info.get('signature_date', ''))
        
        # Process receipts
        category_counters = {cat: 0 for cat in self.CATEGORY_ROWS.keys()}
        
        for receipt in receipts:
            category = receipt.get('category', 'Travel')
            start_row = self.CATEGORY_ROWS.get(category, 42)
            row = start_row + category_counters[category]
            category_counters[category] += 1
            
            if row > 200:
                continue
            
            currency = receipt.get('currency', 'EUR')
            receipt_date = receipt['data'].get('date', '')
            exchange_rate = self.get_exchange_rate(currency, 'USD', receipt_date)
            
            # Date in MM/DD/YYYY
            self._set_cell_value_safe(sheet, row, 2, receipt['data'].get('date', ''))
            
            if category == 'Travel':
                self._set_cell_value_safe(sheet, row, 3, receipt.get('from_location', ''))
                self._set_cell_value_safe(sheet, row, 4, receipt.get('to_location', ''))
            elif category == 'Ministry Entertainment':
                self._set_cell_value_safe(sheet, row, 3, receipt.get('who', ''))
                self._set_cell_value_safe(sheet, row, 4, receipt.get('where', ''))
            else:
                self._set_cell_value_safe(sheet, row, 3, receipt['data'].get('merchant', ''))
                # Skip address for merged cells - just use merchant
            
            self._set_cell_value_safe(sheet, row, 5, receipt.get('ministry_purpose', ''))
            self._set_cell_value_safe(sheet, row, 6, receipt['data'].get('total', 0.0))
            self._set_cell_value_safe(sheet, row, 7, exchange_rate)
        
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer
    
    def _set_cell_value_safe(self, sheet, row, col, value):
        """Set cell value, skipping merged cells"""
        try:
            cell = sheet.cell(row=row, column=col)
            
            # Check if this is a merged cell
            if hasattr(cell, 'coordinate'):
                coord = cell.coordinate
                # Check if cell is part of a merged range
                for merged_range in sheet.merged_cells.ranges:
                    if coord in merged_range:
                        # This is a merged cell, skip it
                        return
            
            # Safe to write
            if isinstance(value, (int, float)):
                cell.value = value
            elif isinstance(value, str):
                cell.value = value
            else:
                cell.value = str(value) if value else ''
        except Exception as e:
            # If any error occurs, just skip this cell
            print(f"Skipping cell ({row}, {col}): {e}")
            pass
    
    def _create_simple_report(self, employee_info, receipts):
        from openpyxl import Workbook
        wb = Workbook()
        sheet = wb.active
        sheet['A1'] = 'Avant Expense Report'
        sheet['A3'] = employee_info.get('name', '')
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer
