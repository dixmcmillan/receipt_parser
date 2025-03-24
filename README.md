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

3. As a Python module:
   ```python
   from receipt_parser import parse_walmart_receipt, batch_process
   
   # Process single receipt
   parse_walmart_receipt('receipt.pdf', 'output.csv')
   
   # Process multiple receipts
   batch_process('pdf_folder', 'output_folder', categories_file='categories.csv', combine=True)
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
