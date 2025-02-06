
A Python tool to parse Walmart receipts from PDF format into CSV.

## Installation

```bash
pip install -e .
```

## Usage

You can use this tool in two ways:

1. As a command-line tool:
   ```bash
   parse-receipt receipt.pdf -o output.csv
   ```

2. As a Python module:
   ```python
   from receipt_parser import parse_walmart_receipt
   parse_walmart_receipt('receipt.pdf', 'output.csv')
   ```
