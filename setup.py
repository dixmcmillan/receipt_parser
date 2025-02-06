from setuptools import setup, find_packages

setup(
    name="receipt_parser",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PyPDF2>=3.0.0",
    ],
    entry_points={
        'console_scripts': [
            'parse-receipt=receipt_parser.parser:main',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool to parse Walmart receipts into CSV format",
)
