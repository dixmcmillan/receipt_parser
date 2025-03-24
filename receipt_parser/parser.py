import re
from datetime import datetime
import csv
import PyPDF2
import argparse
import os
import glob
from pathlib import Path
from .categorizer import ReceiptCategorizer
import pandas as pd

def clean_price(price_str):
    # Remove any leading/trailing whitespace and ensure proper decimal format
    price_str = price_str.strip()
    if price_str.startswith('.'):
        price_str = '0' + price_str
    return price_str

def clean_item_name(item_name):
    # Clean up extra spaces and normalize item names
    return ' '.join(item_name.split())

def parse_walmart_receipt(pdf_path, output_csv, categories_file=None):
    """Parse Walmart receipt and optionally categorize items."""
    # Ensure PDF file exists
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
    # Read PDF file
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = pdf_reader.pages[0].extract_text()
    except Exception as e:
        raise RuntimeError(f"Error reading PDF {pdf_path}: {str(e)}")
    
    # Extract date
    date_match = re.search(r'([A-Z][a-z]{2}\s+\d{2},\s+\d{4})', text)
    if date_match:
        date_str = date_match.group(1)
        date_obj = datetime.strptime(date_str, '%b %d, %Y')
        date = date_obj.strftime('%Y-%m-%d')
    else:
        # Try alternative date format
        date_match = re.search(r'(\d{2}/\d{2}/\d{4})', text)
        if date_match:
            date_str = date_match.group(1)
            date_obj = datetime.strptime(date_str, '%m/%d/%Y')
            date = date_obj.strftime('%Y-%m-%d')
        else:
            # Use PDF filename as fallback for date
            filename = os.path.basename(pdf_path)
            date_match = re.search(r'(\d{8})', filename)
            if date_match:
                date_str = date_match.group(1)
                try:
                    date_obj = datetime.strptime(date_str, '%Y%m%d')
                    date = date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    date = "Unknown"
            else:
                date = "Unknown"
    
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
    
    # Write to temporary CSV first
    temp_csv = output_csv + '.temp'
    os.makedirs(os.path.dirname(output_csv) if os.path.dirname(output_csv) else '.', exist_ok=True)
    
    with open(temp_csv, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['date', 'store', 'item', 'qty_wgt', 'price'])
        writer.writeheader()
        writer.writerows(items)
    
    # If categories file is provided, categorize the items
    try:
        if categories_file:
            categorizer = ReceiptCategorizer(categories_file)
            categorizer.categorize_receipt(temp_csv, output_csv)
            os.remove(temp_csv)  # Clean up temporary file
        else:
            # If no categorization needed, just rename temp file
            os.rename(temp_csv, output_csv)
        return True
    except Exception as e:
        print(f"Error during categorization: {str(e)}")
        # Ensure we don't leave temporary files
        if os.path.exists(temp_csv):
            os.remove(temp_csv)
        raise

def batch_process(folder_path, output_folder, categories_file=None, combine=False):
    """
    Process all PDF files in a folder.
    
    Args:
        folder_path: Path to folder containing PDFs
        output_folder: Folder to save output CSVs
        categories_file: Optional path to categories CSV
        combine: If True, combine all results into a single CSV
    """
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Find all PDF files in the folder
    pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {folder_path}")
        return
    
    print(f"Found {len(pdf_files)} PDF files to process...")
    
    successful_files = []
    failed_files = []
    
    for pdf_file in pdf_files:
        filename = os.path.basename(pdf_file)
        base_name = os.path.splitext(filename)[0]
        output_path = os.path.join(output_folder, f"{base_name}.csv")
        
        print(f"Processing {filename}...")
        
        try:
            parse_walmart_receipt(pdf_file, output_path, categories_file)
            successful_files.append(output_path)
            print(f"  ✓ Saved to {output_path}")
        except Exception as e:
            print(f"  ✗ Failed: {str(e)}")
            failed_files.append(pdf_file)
    
    # Combine all CSVs if requested
    if combine:
        # Find all existing CSV files in the output folder
        existing_csvs = glob.glob(os.path.join(output_folder, "*.csv"))
        existing_csvs = [f for f in existing_csvs if not f.endswith("combined_receipts.csv")]
        
        if existing_csvs:
            combined_csv = os.path.join(output_folder, "combined_receipts.csv")
            combine_csv_files(existing_csvs, combined_csv)
            print(f"Combined results saved to {combined_csv}")
        else:
            print("No CSV files found to combine")
    
    # Print summary
    print("\nProcessing Summary:")
    print(f"  Successfully processed: {len(successful_files)} files")
    print(f"  Failed to process: {len(failed_files)} files")
    
    if failed_files:
        print("\nFailed files:")
        for file in failed_files:
            print(f"  - {os.path.basename(file)}")

def combine_csv_files(csv_files, output_file):
    """Combine multiple CSV files into a single file."""
    if not csv_files:
        return
        
    # Read the first file to get the header
    combined_df = pd.read_csv(csv_files[0])
    
    # Append all other files
    for file in csv_files[1:]:
        df = pd.read_csv(file)
        combined_df = pd.concat([combined_df, df], ignore_index=True)
    
    # Sort by date
    if 'date' in combined_df.columns:
        combined_df.sort_values(by='date', inplace=True)
    
    # Save combined file
    combined_df.to_csv(output_file, index=False)

def main():
    parser = argparse.ArgumentParser(description='Parse Walmart receipts to CSV format')
    parser.add_argument('input', help='Path to the Walmart receipt PDF or folder containing PDFs')
    parser.add_argument('--output', '-o', help='Output CSV file path or folder (optional)')
    parser.add_argument('--categories', '-c', help='Path to categories CSV file (optional)')
    parser.add_argument('--batch', '-b', action='store_true', help='Process all PDFs in the input folder')
    parser.add_argument('--combine', action='store_true', help='Combine all outputs into a single CSV (only with --batch)')
    
    args = parser.parse_args()
    
    try:
        # Batch processing mode
        if args.batch or os.path.isdir(args.input):
            folder_path = args.input
            output_folder = args.output if args.output else os.path.join(folder_path, "parsed")
            batch_process(folder_path, output_folder, args.categories, args.combine)
        
        # Single file mode
        else:
            pdf_path = args.input
            # If no output path specified, create one based on the PDF name
            if not args.output:
                base_name = os.path.splitext(os.path.basename(pdf_path))[0]
                args.output = f"{base_name}_parsed.csv"
            
            parse_walmart_receipt(pdf_path, args.output, args.categories)
            print(f"Parsed receipt saved to: {args.output}")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

if __name__ == '__main__':
    main()