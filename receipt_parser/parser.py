import re
from datetime import datetime
import csv
import PyPDF2
import argparse
import os

def clean_price(price_str):
    price_str = price_str.strip()
    if price_str.startswith('.'):
        price_str = '0' + price_str
    return price_str

def clean_item_name(item_name):
    return ' '.join(item_name.split())

def parse_walmart_receipt(pdf_path, output_csv):
    # Read PDF file
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = pdf_reader.pages[0].extract_text()
    
    # Extract date
    date_match = re.search(r'([A-Z][a-z]{2}\s+\d{2},\s+\d{4})', text)
    if date_match:
        date_str = date_match.group(1)
        date_obj = datetime.strptime(date_str, '%b %d, %Y')
        date = date_obj.strftime('%Y-%m-%d')
    
    # Split text into lines and process each line
    lines = text.split('\n')
    items = []
    
    for i, line in enumerate(lines):
        # Skip empty lines
        if not line.strip():
            continue
            
        # Match item lines (containing "Shopped")
        if 'Shopped' in line:
            # Split the line at "Shopped"
            parts = line.split('Shopped')
            item_name = clean_item_name(parts[0].strip())
            
            # Extract quantity or weight
            qty_wgt = ''
            qty_match = re.search(r'Shopped Qty (\d+)', line)
            wgt_match = re.search(r'Shopped Wt (\d+\.\d+)', line)
            
            if qty_match:
                qty_wgt = qty_match.group(1)
            elif wgt_match:
                qty_wgt = f"{wgt_match.group(1)} lb"
            
            # Extract price (last number in the line)
            price_match = re.search(r'\$(\d+\.\d{2})', line)
            if price_match:
                price = clean_price(price_match.group(1))
                items.append({
                    'date': date,
                    'store': 'Walmart',
                    'item': item_name,
                    'qty_wgt': qty_wgt,
                    'price': price
                })
        
        # Match fresh produce (like bananas)
        elif 'Fresh' in line and 'lb' in line:
            # Extract item name, weight, and price using more precise regex
            item_match = re.search(r'Fresh ([^,]+)', line)
            wgt_match = re.search(r'(\d+\.\d+)\s*lb', line)
            price_match = re.search(r'\$(\d*\.?\d{2})', line)
            
            if item_match and wgt_match and price_match:
                items.append({
                    'date': date,
                    'store': 'Walmart',
                    'item': clean_item_name(f"Fresh {item_match.group(1)}"),
                    'qty_wgt': f"{wgt_match.group(1)} lb",
                    'price': clean_price(price_match.group(1))
                })
        
        # Match tax line
        elif 'Tax' in line and not 'Subtotal' in line:
            tax_match = re.search(r'\$(\d+\.\d{2})', line)
            if tax_match:
                tax = clean_price(tax_match.group(1))
                items.append({
                    'date': date,
                    'store': 'Walmart',
                    'item': 'Tax',
                    'qty_wgt': '',
                    'price': tax
                })
    
    # Write to CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['date', 'store', 'item', 'qty_wgt', 'price'])
        writer.writeheader()
        writer.writerows(items)
    pass

def main():
    parser = argparse.ArgumentParser(description='Parse Walmart receipts to CSV format')
    parser.add_argument('pdf_path', help='Path to the Walmart receipt PDF')
    parser.add_argument('--output', '-o', help='Output CSV file path (optional)')
    
    args = parser.parse_args()
    
    # If no output path specified, create one based on the PDF name
    if not args.output:
        base_name = os.path.splitext(os.path.basename(args.pdf_path))[0]
        args.output = f"{base_name}_parsed.csv"
    
    parse_walmart_receipt(args.pdf_path, args.output)
    print(f"Parsed receipt saved to: {args.output}")

if __name__ == '__main__':
    main()
