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
        
        # Detect currency from symbols and location
        currency = self._detect_currency(lines)
        
        return {
            'merchant': self._extract_merchant(lines),
            'address': self._extract_address(lines),
            'date': self._extract_date(lines),
            'total': self._extract_total(lines),
            'items': self._extract_items(lines),
            'tax': self._extract_tax(lines),
            'currency': currency
        }
    
    def _detect_currency(self, lines):
        """Detect currency from receipt"""
        text = ' '.join(lines).upper()
        
        # Check for currency symbols and keywords
        if '€' in text or 'EUR' in text or 'EURO' in text:
            return 'EUR'
        elif '$' in text or 'USD' in text or 'DOLLAR' in text:
            return 'USD'
        elif '£' in text or 'GBP' in text or 'POUND' in text:
            return 'GBP'
        
        # Check for country/city indicators
        euro_indicators = ['SPAIN', 'ESPAÑA', 'FRANCE', 'GERMANY', 'ITALY', 
                          'PORTUGAL', 'BELGIUM', 'NETHERLANDS', 'AUSTRIA',
                          'MADRID', 'BARCELONA', 'VALENCIA', 'ALICANTE', 
                          'SEVILLA', 'PARIS', 'BERLIN', 'ROME', 'LISBON']
        
        for indicator in euro_indicators:
            if indicator in text:
                return 'EUR'
        
        return 'EUR'  # Default to EUR
    
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
        # Multiple patterns to try
        patterns = [
            r'(?:total|suma|amount|importe)\s*[:\s]*(\d+[,\.]\d{2})',  # TOTAL: 10,95
            r'(\d+[,\.]\d{2})\s*€?\s*(?:total|suma)',  # 10,95 € TOTAL
            r'total\s*[:\s]*€?\s*(\d+[,\.]\d{2})',  # Total: €10,95
        ]
        
        # Search from bottom up (last 20 lines where totals usually are)
        for line in reversed(lines[-20:]):
            for pattern in patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    amount_str = match.group(1).replace(',', '.')
                    try:
                        amount = float(amount_str)
                        # Sanity check: total should be reasonable (0.01 to 100000)
                        if 0.01 <= amount <= 100000:
                            return amount
                    except ValueError:
                        continue
        
        # Fallback: find largest reasonable amount
        max_amount = 0.0
        amount_pattern = r'(\d+[,\.]\d{2})\s*€?'
        
        for line in lines:
            matches = re.finditer(amount_pattern, line)
            for match in matches:
                try:
                    amount = float(match.group(1).replace(',', '.'))
                    # Skip very small amounts (tips, tax) and very large (could be phone numbers)
                    if 1.0 <= amount <= 10000 and amount > max_amount:
                        max_amount = amount
                except ValueError:
                    continue
        
        return max_amount if max_amount > 0 else 0.0
    
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
