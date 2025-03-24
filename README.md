A Python tool to parse Walmart receipts from PDF format into CSV.

## Installation

```bash
pip install -e .
```

For development, install with test dependencies:
```bash
pip install -e ".[dev]"
```

## Usage

You can use this tool in several ways:

1. As a command-line tool for single files:
   ```bash
   parse-receipt receipt.pdf -o output.csv
   ```

2. For batch processing multiple PDFs:
   ```bash
   parse-receipt /path/to/pdf/folder -b -o /path/to/output/folder
   ```
   
   Options for batch processing:
   - `-b` or `--batch`: Enable batch processing mode
   - `-c` or `--categories`: Specify a categories CSV file
   - `--combine`: Combine all outputs into a single CSV file

3. With categorization (interactive mode):
   ```bash
   parse-receipt receipt.pdf -o output.csv -c master_categories.csv
   ```
   
   When using the `-c` option, the parser will:
   - Read categories from the specified CSV file
   - Automatically categorize items based on the master categories
   - Prompt for categories of unrecognized items
   - Add new categorizations to the master categories file
   
   The categories file should be a CSV with columns:
   ```csv
   Item,Category,Sub-Category
   Bananas,Grocery,Produce
   Milk,Grocery,Dairy
   ```

   During interactive mode:
   - For each uncategorized item, you'll be prompted to enter a category
   - Press Enter to skip categorizing an item (it will remain "Uncategorized")
   - Categories are saved automatically to the master file
   - Use Ctrl+C to exit interactive mode at any time

4. As a Python module:
   ```python
   from receipt_parser import parse_walmart_receipt, batch_process
   
   # Process single receipt
   parse_walmart_receipt('receipt.pdf', 'output.csv')
   
   # Process multiple receipts with categories
   batch_process('pdf_folder', 'output_folder', 
                categories_file='categories.csv', 
                combine=True)
   ```

## Output Format

The parser generates CSV files with the following columns:
- Date: Transaction date
- Item: Product name
- Price: Item price
- Category: Item category (if using categories)
- Sub-Category: Item sub-category (if using categories)
- Receipt: Source receipt filename

When using `--combine` in batch mode, all receipts are combined into a single CSV file named `combined_receipts.csv`.

## Categories File Format

The master categories file (`master_categories.csv`) should be a CSV file with three columns:
- Item: Exact product name as it appears on the receipt
- Category: Main category (e.g., Grocery, Household, Other)
- Sub-Category: More specific category (e.g., Produce, Dairy, Paper Products)

Example:
```csv
Item,Category,Sub-Category
Bananas,Grocery,Produce
Paper Towels,Household,Paper Products
Tax,Other,Tax
```

## Development

### Setting up development environment

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

### Running Tests

Run tests with pytest:
```bash
pytest receipt_parser/tests/
```

Run tests with coverage:
```bash
pytest --cov=receipt_parser receipt_parser/tests/
```

### Code Quality

Format code with black:
```bash
black receipt_parser/
```

Run linting:
```bash
flake8 receipt_parser/
```
