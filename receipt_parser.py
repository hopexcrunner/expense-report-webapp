import re
from datetime import datetime

class ReceiptParser:
    """Parse OCR text from receipts into structured data"""
    
    def parse(self, text):
        """
        Parse receipt text and extract structured information
        
        Args:
            text: Raw OCR text from receipt
            
        Returns:
            dict with merchant, date, total, items, etc.
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        return {
            'merchant': self._extract_merchant(lines),
            'address': self._extract_address(lines),
            'date': self._extract_date(lines),
            'total': self._extract_total(lines),
            'items': self._extract_items(lines),
            'tax': self._extract_tax(lines),
            'currency': 'EUR'
        }
    
    def _extract_merchant(self, lines):
        """Extract merchant/establishment name from top of receipt"""
        # Usually first few non-numeric lines
        for line in lines[:5]:
            if len(line) > 3 and not re.search(r'\d{5,}', line):
                return line
        return lines[0] if lines else "Unknown Merchant"
    
    def _extract_address(self, lines):
        """Extract address from receipt"""
        # Look for street addresses or postal codes
        address_patterns = [
            r'.*(?:calle|street|st\.|avenue|ave\.|road|rd\.).*',
            r'.*\d{5}.*'
        ]
        
        for line in lines[:10]:
            for pattern in address_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    return line
        return ""
    
    def _extract_date(self, lines):
        """Extract date from receipt"""
        # Date patterns
        patterns = [
            r'(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})',
            r'(\d{1,2}\s+(?:ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)\.?\s+\d{4})',
            r'(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\.?\s+\d{4})'
        ]
        
        for line in lines:
            for pattern in patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    return match.group(1)
        
        # Fallback to current date
        return datetime.now().strftime('%d/%m/%Y')
    
    def _extract_total(self, lines):
        """Extract total amount from receipt"""
        # Look for TOTAL keyword followed by amount
        total_pattern = r'(?:total|suma|amount).*?(\d+[,\.]\d{2})\s*€?'
        
        # Search from bottom up
        for line in reversed(lines[-15:]):
            match = re.search(total_pattern, line, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '.')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        
        # Fallback: find largest amount
        max_amount = 0.0
        amount_pattern = r'(\d+[,\.]\d{2})\s*€'
        
        for line in lines:
            matches = re.finditer(amount_pattern, line)
            for match in matches:
                try:
                    amount = float(match.group(1).replace(',', '.'))
                    if amount > max_amount:
                        max_amount = amount
                except ValueError:
                    continue
        
        return max_amount
    
    def _extract_items(self, lines):
        """Extract line items from receipt"""
        items = []
        
        # Pattern: description quantity x price = total
        item_pattern = r'(.+?)\s+(\d+[,\.]?\d*)\s*x\s*(\d+[,\.]\d{2})\s*€?\s*(\d+[,\.]\d{2})?\s*€?'
        
        for line in lines:
            match = re.search(item_pattern, line, re.IGNORECASE)
            if match:
                description = match.group(1).strip()
                quantity_str = match.group(2).replace(',', '.')
                price_str = match.group(3).replace(',', '.')
                amount_str = match.group(4).replace(',', '.') if match.group(4) else None
                
                try:
                    quantity = float(quantity_str)
                    unit_price = float(price_str)
                    amount = float(amount_str) if amount_str else (quantity * unit_price)
                    
                    items.append({
                        'description': description,
                        'quantity': quantity,
                        'unit_price': unit_price,
                        'amount': amount
                    })
                except ValueError:
                    continue
        
        return items
    
    def _extract_tax(self, lines):
        """Extract tax/VAT amount"""
        tax_pattern = r'(?:IVA|VAT|tax).*?(\d+[,\.]\d{2})\s*€?'
        
        for line in reversed(lines[-10:]):
            match = re.search(tax_pattern, line, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '.')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        
        return 0.0
