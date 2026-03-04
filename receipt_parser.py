import re
from datetime import datetime

class ReceiptParser:
    """Parse OCR text from receipts into structured data"""
    
    def parse(self, text):
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        currency = self._detect_currency(lines)
        
        return {
            'merchant': self._extract_merchant(lines),
            'address': self._extract_address(lines),
            'city': self._extract_city(lines),
            'date': self._extract_date(lines),
            'total': self._extract_total(lines),
            'items': self._extract_items(lines),
            'tax': self._extract_tax(lines),
            'currency': currency
        }
    
    def _detect_currency(self, lines):
        text = ' '.join(lines).upper()
        if '€' in text or 'EUR' in text or 'EURO' in text:
            return 'EUR'
        elif '$' in text or 'USD' in text or 'DOLLAR' in text:
            return 'USD'
        elif '£' in text or 'GBP' in text or 'POUND' in text:
            return 'GBP'
        
        euro_indicators = ['SPAIN', 'ESPAÑA', 'FRANCE', 'GERMANY', 'ITALY', 'PORTUGAL', 'BELGIUM', 'NETHERLANDS', 'AUSTRIA', 'MADRID', 'BARCELONA', 'VALENCIA', 'ALICANTE', 'SEVILLA', 'PARIS', 'BERLIN', 'ROME', 'LISBON']
        for indicator in euro_indicators:
            if indicator in text:
                return 'EUR'
        return 'EUR'
    
    def _extract_merchant(self, lines):
        for line in lines[:5]:
            if len(line) > 3 and not re.search(r'\d{5,}', line):
                return line
        return lines[0] if lines else "Unknown Merchant"
    
    def _extract_address(self, lines):
        address_patterns = [r'.*(?:calle|street|st\.|avenue|ave\.|road|rd\.).*', r'.*\d{5}.*']
        for line in lines[:10]:
            for pattern in address_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    return line
        return ""
    
    def _extract_city(self, lines):
        """Extract city from address or receipt"""
        for line in lines[:15]:
            # Look for city patterns
            if re.search(r'\b(madrid|barcelona|valencia|alicante|sevilla|burgos|bilbao)\b', line, re.IGNORECASE):
                match = re.search(r'\b(madrid|barcelona|valencia|alicante|sevilla|burgos|bilbao)\b', line, re.IGNORECASE)
                return match.group(1).title()
        
        # Extract from address if comma-separated
        address = self._extract_address(lines)
        if ',' in address:
            parts = address.split(',')
            if len(parts) >= 2:
                return parts[-2].strip()
        
        return ""
    
    def _extract_date(self, lines):
        """Extract date and convert to MM/DD/YYYY"""
        patterns = [
            r'(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})',
            r'(\d{1,2}\s+(?:ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)\.?\s+\d{4})',
            r'(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\.?\s+\d{4})'
        ]
        
        for line in lines:
            for pattern in patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    date_str = match.group(1)
                    return self._convert_to_mm_dd_yyyy(date_str)
        
        return datetime.now().strftime('%m/%d/%Y')
    
    def _convert_to_mm_dd_yyyy(self, date_str):
        """Convert any date format to MM/DD/YYYY"""
        # Try multiple input formats
        for fmt_in in ['%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d', '%d-%m-%Y', '%Y/%m/%d']:
            try:
                date_obj = datetime.strptime(date_str, fmt_in)
                return date_obj.strftime('%m/%d/%Y')
            except:
                continue
        
        # Handle Spanish month names
        spanish_months = {'ene': '01', 'feb': '02', 'mar': '03', 'abr': '04', 'may': '05', 'jun': '06', 'jul': '07', 'ago': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dic': '12'}
        for esp, num in spanish_months.items():
            if esp in date_str.lower():
                match = re.search(r'(\d{1,2})\s+' + esp + r'\.?\s+(\d{4})', date_str, re.IGNORECASE)
                if match:
                    day = match.group(1).zfill(2)
                    year = match.group(2)
                    return f"{num}/{day}/{year}"
        
        return date_str
    
    def _extract_total(self, lines):
        patterns = [
            r'(?:total|suma|amount|importe)\s*[:\s]*(\d+[,\.]\d{2})',
            r'(\d+[,\.]\d{2})\s*€?\s*(?:total|suma)',
            r'total\s*[:\s]*€?\s*(\d+[,\.]\d{2})',
        ]
        
        for line in reversed(lines[-20:]):
            for pattern in patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    amount_str = match.group(1).replace(',', '.')
                    try:
                        amount = float(amount_str)
                        if 0.01 <= amount <= 100000:
                            return amount
                    except ValueError:
                        continue
        
        max_amount = 0.0
        amount_pattern = r'(\d+[,\.]\d{2})\s*€?'
        for line in lines:
            matches = re.finditer(amount_pattern, line)
            for match in matches:
                try:
                    amount = float(match.group(1).replace(',', '.'))
                    if 1.0 <= amount <= 10000 and amount > max_amount:
                        max_amount = amount
                except ValueError:
                    continue
        
        return max_amount if max_amount > 0 else 0.0
    
    def _extract_items(self, lines):
        items = []
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
