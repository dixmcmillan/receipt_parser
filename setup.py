from setuptools import setup, find_packages

setup(
    name="receipt_parser",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PyPDF2>=3.0.0",
        "pandas>=1.0.0",
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=22.0.0',  # for code formatting
            'flake8>=6.0.0',  # for linting
        ],
    },
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
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)