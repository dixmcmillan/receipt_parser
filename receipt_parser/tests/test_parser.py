import os
import pytest
import tempfile
import shutil
from pathlib import Path
from receipt_parser.parser import parse_walmart_receipt, batch_process

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

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
    """Test batch processing with categories file."""
    output_dir = os.path.join(temp_dir, "output")
    categories_file = os.path.join(temp_dir, "categories.csv")
    
    # Create a simple categories file
    with open(categories_file, 'w') as f:
        f.write("item,category\nBananas,Produce\n")
    
    batch_process(sample_pdf_dir, output_dir, categories_file=categories_file)
    assert os.path.exists(output_dir) 