from openpyxl import load_workbook
from datetime import datetime
import io
import os

class ExcelProcessor:
    """Process Excel expense report templates"""
    
    def __init__(self):
        self.template_path = "Avant_2026_Expense_Report_Form.xlsx"
    
    def create_expense_report(self, receipt_data):
        """
        Create expense report from receipt data
        
        Args:
            receipt_data: Dictionary with merchant, date, total, items, etc.
            
        Returns:
            BytesIO buffer with Excel file
        """
        # Load template
        if os.path.exists(self.template_path):
            wb = load_workbook(self.template_path)
        else:
            # Create simple workbook if template doesn't exist
            return self._create_simple_report(receipt_data)
        
        sheet = wb['Expense Report']
        
        # Fill header information
        # Date submitted (G7)
        current_date = datetime.now().strftime('%m/%d/%Y')
        self._set_cell_value(sheet, 7, 7, current_date)  # Row 7, Column G
        
        # Add expense line items starting at row 42
        start_row = 42
        items = receipt_data.get('items', [])
        
        if items:
            # Add each line item
            for i, item in enumerate(items):
                row = start_row + i
                if row < 129:  # Stay within expense area
                    # Date (Column B)
                    self._set_cell_value(sheet, row, 2, receipt_data.get('date', ''))
                    
                    # Merchant (Column C - From)
                    self._set_cell_value(sheet, row, 3, receipt_data.get('merchant', ''))
                    
                    # Address (Column D - To)
                    self._set_cell_value(sheet, row, 4, receipt_data.get('address', ''))
                    
                    # Description (Column E - Purpose)
                    self._set_cell_value(sheet, row, 5, item.get('description', ''))
                    
                    # Amount (Column F - Local Currency)
                    self._set_cell_value(sheet, row, 6, item.get('amount', 0.0))
                    
                    # Exchange Rate (Column G)
                    self._set_cell_value(sheet, row, 7, 1.0)
                    
                    # Account Code (Column M)
                    self._set_cell_value(sheet, row, 13, "8464 - Meals & Entertainment")
        else:
            # Single entry for total amount
            row = start_row
            self._set_cell_value(sheet, row, 2, receipt_data.get('date', ''))
            self._set_cell_value(sheet, row, 3, receipt_data.get('merchant', ''))
            self._set_cell_value(sheet, row, 4, receipt_data.get('address', ''))
            self._set_cell_value(sheet, row, 5, "Expense")
            self._set_cell_value(sheet, row, 6, receipt_data.get('total', 0.0))
            self._set_cell_value(sheet, row, 7, 1.0)
            self._set_cell_value(sheet, row, 13, "8464 - Meals & Entertainment")
        
        # Save to BytesIO buffer
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        
        return buffer
    
    def _set_cell_value(self, sheet, row, col, value):
        """Set cell value handling different types"""
        cell = sheet.cell(row=row, column=col)
        
        if isinstance(value, (int, float)):
            cell.value = value
        elif isinstance(value, str):
            cell.value = value
        else:
            cell.value = str(value)
    
    def _create_simple_report(self, receipt_data):
        """Create a simple Excel report if template is not available"""
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment
        
        wb = Workbook()
        sheet = wb.active
        sheet.title = "Expense Report"
        
        # Header
        sheet['A1'] = 'Avant Expense Report'
        sheet['A1'].font = Font(size=16, bold=True)
        
        # Date
        sheet['A3'] = 'Date Submitted:'
        sheet['B3'] = datetime.now().strftime('%m/%d/%Y')
        
        # Receipt info
        sheet['A5'] = 'Merchant:'
        sheet['B5'] = receipt_data.get('merchant', '')
        
        sheet['A6'] = 'Date:'
        sheet['B6'] = receipt_data.get('date', '')
        
        sheet['A7'] = 'Total Amount:'
        sheet['B7'] = receipt_data.get('total', 0.0)
        sheet['B7'].number_format = '€#,##0.00'
        
        # Line items header
        sheet['A9'] = 'Description'
        sheet['B9'] = 'Quantity'
        sheet['C9'] = 'Unit Price'
        sheet['D9'] = 'Amount'
        
        # Style header
        for cell in ['A9', 'B9', 'C9', 'D9']:
            sheet[cell].font = Font(bold=True)
            sheet[cell].fill = PatternFill(start_color='CCCCCC', end_color='CCCCCC', fill_type='solid')
        
        # Add items
        items = receipt_data.get('items', [])
        row = 10
        
        if items:
            for item in items:
                sheet[f'A{row}'] = item.get('description', '')
                sheet[f'B{row}'] = item.get('quantity', 1)
                sheet[f'C{row}'] = item.get('unit_price', 0.0)
                sheet[f'D{row}'] = item.get('amount', 0.0)
                
                # Format currency
                sheet[f'C{row}'].number_format = '€#,##0.00'
                sheet[f'D{row}'].number_format = '€#,##0.00'
                
                row += 1
        else:
            sheet[f'A{row}'] = 'Single Expense'
            sheet[f'B{row}'] = 1
            sheet[f'C{row}'] = receipt_data.get('total', 0.0)
            sheet[f'D{row}'] = receipt_data.get('total', 0.0)
            
            sheet[f'C{row}'].number_format = '€#,##0.00'
            sheet[f'D{row}'].number_format = '€#,##0.00'
        
        # Adjust column widths
        sheet.column_dimensions['A'].width = 30
        sheet.column_dimensions['B'].width = 12
        sheet.column_dimensions['C'].width = 15
        sheet.column_dimensions['D'].width = 15
        
        # Save to buffer
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        
        return buffer
