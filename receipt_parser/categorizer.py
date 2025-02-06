import csv
import re
from pathlib import Path
import pandas as pd
import pkg_resources
import os

class ReceiptCategorizer:
    def __init__(self, categories_file=None):
        """Initialize with optional path to categories file."""
        self.categories_map = {}
        if categories_file:
            # If it's a relative path to the default categories file
            if categories_file == 'categories.csv':
                categories_file = pkg_resources.resource_filename('receipt_parser', 'data/categories.csv')
            # If it's an absolute path or custom relative path
            elif not os.path.isabs(categories_file):
                categories_file = os.path.join(os.getcwd(), categories_file)
                
            self.load_categories(categories_file)
    
    def load_categories(self, file_path):
        """Load category mappings from CSV file."""
        try:
            df = pd.read_csv(file_path)
            # Create a dictionary of items to their categories
            for _, row in df.iterrows():
                self.categories_map[row['item'].lower()] = {
                    'category': row['category'],
                    'sub-category': row['sub-category']
                }
        except FileNotFoundError:
            print(f"Error: Categories file not found at {file_path}")
            print("Available paths:")
            print(f"Current directory: {os.getcwd()}")
            print(f"Package data directory: {pkg_resources.resource_filename('receipt_parser', 'data')}")
            raise
    
    def categorize_item(self, item_name):
        """
        Categorize an item based on known mappings and rules.
        Returns tuple of (category, sub-category)
        """
        item_lower = item_name.lower()
        
        # Check exact matches first
        if item_lower in self.categories_map:
            cat_info = self.categories_map[item_lower]
            return cat_info['category'], cat_info['sub-category']
        
        # Default categories based on keywords
        keyword_categories = {
            'fresh': ('Grocery', 'Veggies'),
            'frozen': ('Grocery', 'Frozen'),
            'chicken': ('Grocery', 'Meat'),
            'beef': ('Grocery', 'Meat'),
            'toilet paper': ('Supplies', 'Personal Care'),
            'toothpaste': ('Supplies', 'Personal Care'),
            'wipes': ('Supplies', 'Cleaning'),
            'tax': ('Tax', 'Tax')
        }
        
        # Check keywords
        for keyword, (category, subcategory) in keyword_categories.items():
            if keyword in item_lower:
                return category, subcategory
        
        # Default category if no matches found
        return 'Uncategorized', 'Uncategorized'
    
    def categorize_receipt(self, input_csv, output_csv):
        """
        Read a receipt CSV, add categories, and save to new CSV.
        """
        # Read the input CSV
        df = pd.read_csv(input_csv)
        
        # Create new columns for categories if they don't exist
        if 'category' not in df.columns:
            df['category'] = ''
        if 'sub-category' not in df.columns:
            df['sub-category'] = ''
        
        # Categorize each item
        for idx, row in df.iterrows():
            category, subcategory = self.categorize_item(row['item'])
            df.at[idx, 'category'] = category
            df.at[idx, 'sub-category'] = subcategory
        
        # Make sure directory exists
        os.makedirs(os.path.dirname(output_csv) if os.path.dirname(output_csv) else '.', exist_ok=True)
        
        # Save to output CSV
        df.to_csv(output_csv, index=False)