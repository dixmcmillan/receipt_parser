from setuptools import setup, find_packages

setup(
    name="receipt_parser",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PyPDF2>=3.0.0",
        "pandas>=1.0.0",
    ],
    package_data={
        'receipt_parser': ['data/*.csv'],
    },
    entry_points={
        'console_scripts': [
            'parse-receipt=receipt_parser.parser:main',
        ],
    },
    author="Dixon McMillan",
    author_email="example@example.com",
    description="A tool to parse Walmart receipts into CSV format",
)