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
        self.master_categories_file = None
        self.unknown_items = []
        
        if categories_file:
            # If it's a relative path to the master categories file
            if categories_file == 'master_categories.csv':
                self.master_categories_file = categories_file
            # If it's an absolute path or custom relative path
            elif not os.path.isabs(categories_file):
                categories_file = os.path.join(os.getcwd(), categories_file)
            
            self.master_categories_file = categories_file
            self.load_categories(categories_file)
    
    def load_categories(self, file_path):
        """Load category mappings from CSV file."""
        try:
            df = pd.read_csv(file_path)
            print(f"Loading categories from: {file_path}")
            # Create a dictionary of items to their categories
            for _, row in df.iterrows():
                # Normalize the item name: lowercase and remove extra whitespace
                item_name = ' '.join(row['Item'].lower().split())
                self.categories_map[item_name] = {
                    'category': row['Category'],
                    'sub-category': row['Sub-Category']
                }
            print(f"Loaded {len(self.categories_map)} categories")
        except FileNotFoundError:
            print(f"Error: Categories file not found at {file_path}")
            print("Available paths:")
            print(f"Current directory: {os.getcwd()}")
            print(f"Package data directory: {pkg_resources.resource_filename('receipt_parser', 'data')}")
            raise
    
    def add_new_category(self, item, category, subcategory):
        """Add a new item and its categories to the master categories file."""
        if not self.master_categories_file:
            raise ValueError("Master categories file not specified")
            
        # Add to in-memory map
        self.categories_map[item.lower()] = {
            'category': category,
            'sub-category': subcategory
        }
        
        # Read existing categories
        df = pd.read_csv(self.master_categories_file)
        
        # Add new row
        new_row = pd.DataFrame({
            'Item': [item],
            'Category': [category],
            'Sub-Category': [subcategory]
        })
        
        # Append to existing DataFrame
        df = pd.concat([df, new_row], ignore_index=True)
        
        # Save back to file
        df.to_csv(self.master_categories_file, index=False)
    
    def categorize_item(self, item_name):
        """
        Categorize an item based on known mappings and rules.
        Returns tuple of (category, sub-category)
        """
        # Normalize the item name: lowercase and remove extra whitespace
        item_lower = ' '.join(item_name.lower().split())
        
        # Debug print
        print(f"Attempting to categorize: {item_name}")
        print(f"Normalized form: {item_lower}")
        print(f"Known items: {list(self.categories_map.keys())[:5]}...")  # Show first 5 items
        
        # Check exact matches first
        if item_lower in self.categories_map:
            cat_info = self.categories_map[item_lower]
            print(f"Found match! Category: {cat_info['category']}, Sub-category: {cat_info['sub-category']}")
            return cat_info['category'], cat_info['sub-category']
        
        # If no match found and we're using master categories, add to unknown items
        if self.master_categories_file and item_name not in self.unknown_items:
            print(f"No match found for: {item_name}")
            self.unknown_items.append(item_name)
        
        # Default category if no matches found
        return 'Uncategorized', 'Uncategorized'
    
    def categorize_receipt(self, input_csv, output_csv, interactive=True):
        """
        Read a receipt CSV, add categories, and save to new CSV.
        If interactive=True, prompt for categorization of unknown items.
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
        
        # Handle unknown items if in interactive mode
        if interactive and self.unknown_items and self.master_categories_file:
            print("\nFound uncategorized items. Please provide categories for them:")
            for item in self.unknown_items:
                print(f"\nItem: {item}")
                category = input("Enter category (or press enter to skip): ").strip()
                if category:
                    subcategory = input("Enter sub-category: ").strip()
                    self.add_new_category(item, category, subcategory)
                    # Update the categorization in the current DataFrame
                    mask = df['item'].str.lower() == item.lower()
                    df.loc[mask, 'category'] = category
                    df.loc[mask, 'sub-category'] = subcategory
        
        # Make sure directory exists
        os.makedirs(os.path.dirname(output_csv) if os.path.dirname(output_csv) else '.', exist_ok=True)
        
        # Save to output CSV
        df.to_csv(output_csv, index=False)