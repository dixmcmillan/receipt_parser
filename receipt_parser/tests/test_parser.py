import os
import pytest
import tempfile
import shutil
from pathlib import Path
from receipt_parser.parser import parse_walmart_receipt, batch_process
import pandas as pd

@pytest.fixture
def temp_dir(tmp_path):
    return str(tmp_path)

@pytest.fixture
def sample_pdf_dir(temp_dir):
    """Create a directory with sample PDF files for testing."""
    pdf_dir = os.path.join(temp_dir, "pdfs")
    os.makedirs(pdf_dir)
    
    # Create dummy PDF files (for testing file handling)
    for i in range(3):
        pdf_path = os.path.join(pdf_dir, f"receipt_{i+1}.pdf")
        with open(pdf_path, 'wb') as f:
            f.write(b"%PDF-1.4\n")  # Minimal PDF header
    
    return pdf_dir

def test_batch_process_creates_output_directory(temp_dir, sample_pdf_dir):
    """Test that batch_process creates the output directory if it doesn't exist."""
    output_dir = os.path.join(temp_dir, "output")
    batch_process(sample_pdf_dir, output_dir)
    assert os.path.exists(output_dir)

def test_batch_process_handles_empty_directory(temp_dir):
    """Test that batch_process handles an empty directory gracefully."""
    empty_dir = os.path.join(temp_dir, "empty")
    output_dir = os.path.join(temp_dir, "output")
    os.makedirs(empty_dir)
    
    batch_process(empty_dir, output_dir)
    assert os.path.exists(output_dir)

def test_batch_process_combines_files(temp_dir, sample_pdf_dir):
    """Test that batch_process handles combining files even when processing fails."""
    output_dir = os.path.join(temp_dir, "output")
    
    # Create a dummy successful output file to test combination
    os.makedirs(output_dir, exist_ok=True)
    dummy_csv = os.path.join(output_dir, "receipt_1.csv")
    with open(dummy_csv, 'w') as f:
        f.write("date,store,item,qty_wgt,price\n")
        f.write("2024-03-24,Walmart,Test Item,1,$9.99\n")
    
    batch_process(sample_pdf_dir, output_dir, combine=True)
    
    # The combined file should be created even if some files fail
    combined_file = os.path.join(output_dir, "combined_receipts.csv")
    assert os.path.exists(combined_file)

def test_batch_process_with_categories(temp_dir, sample_pdf_dir):
    """Test batch processing with master categories file."""
    output_dir = os.path.join(temp_dir, "output")
    categories_file = os.path.join(temp_dir, "master_categories.csv")
    
    # Create a test categories file
    with open(categories_file, 'w') as f:
        f.write("Item,Category,Sub-Category\n")
        f.write("Test Item,Grocery,Test\n")
    
    # Create a test receipt CSV
    receipt_dir = os.path.join(temp_dir, "receipts")
    os.makedirs(receipt_dir)
    test_csv = os.path.join(receipt_dir, "test_receipt.csv")
    
    with open(test_csv, 'w') as f:
        f.write("date,store,item,qty_wgt,price\n")
        f.write("2024-01-01,Walmart,Test Item,1,$10.00\n")
        f.write("2024-01-01,Walmart,Unknown Item,1,$5.00\n")
    
    # Process with categories
    output_csv = os.path.join(output_dir, "categorized_receipt.csv")
    os.makedirs(output_dir, exist_ok=True)
    
    # Mock user input for unknown item
    import builtins
    original_input = builtins.input
    input_responses = iter(['Grocery', 'New'])
    builtins.input = lambda _: next(input_responses)
    
    try:
        from receipt_parser.categorizer import ReceiptCategorizer
        categorizer = ReceiptCategorizer(categories_file)
        categorizer.categorize_receipt(test_csv, output_csv)
        
        # Verify the results
        df = pd.read_csv(output_csv)
        assert len(df) == 2
        assert df.iloc[0]['category'] == 'Grocery'
        assert df.iloc[0]['sub-category'] == 'Test'
        
        # Verify the unknown item was added to master categories
        master_df = pd.read_csv(categories_file)
        assert 'Unknown Item' in master_df['Item'].values
        assert 'Grocery' in master_df['Category'].values
        assert 'New' in master_df['Sub-Category'].values
        
    finally:
        builtins.input = original_input

def test_categorizer_skips_unknown_items(temp_dir):
    """Test that categorizer can skip unknown items when requested."""
    categories_file = os.path.join(temp_dir, "master_categories.csv")
    
    # Create a test categories file
    with open(categories_file, 'w') as f:
        f.write("Item,Category,Sub-Category\n")
        f.write("Known Item,Grocery,Test\n")
    
    # Create a test receipt CSV
    test_csv = os.path.join(temp_dir, "test_receipt.csv")
    with open(test_csv, 'w') as f:
        f.write("date,store,item,qty_wgt,price\n")
        f.write("2024-01-01,Walmart,Known Item,1,$10.00\n")
        f.write("2024-01-01,Walmart,Unknown Item,1,$5.00\n")
    
    # Process with categories
    output_csv = os.path.join(temp_dir, "categorized_receipt.csv")
    
    # Mock user input to skip unknown item
    import builtins
    original_input = builtins.input
    builtins.input = lambda _: ''  # Return empty string to skip
    
    try:
        from receipt_parser.categorizer import ReceiptCategorizer
        categorizer = ReceiptCategorizer(categories_file)
        categorizer.categorize_receipt(test_csv, output_csv)
        
        # Verify the results
        df = pd.read_csv(output_csv)
        assert len(df) == 2
        assert df[df['item'] == 'Known Item']['category'].iloc[0] == 'Grocery'
        assert df[df['item'] == 'Unknown Item']['category'].iloc[0] == 'Uncategorized'
        
        # Verify the master categories file wasn't modified
        master_df = pd.read_csv(categories_file)
        assert 'Unknown Item' not in master_df['Item'].values
        
    finally:
        builtins.input = original_input 