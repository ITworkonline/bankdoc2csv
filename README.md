# Wells Fargo Statement PDF to CSV Converter

This script converts Wells Fargo bank statement PDFs into a structured CSV format.

## Features
- Processes multiple PDF statements in a folder
- Extracts transaction dates, descriptions, and amounts
- Distinguishes between deposits (positive) and withdrawals (negative)
- Exports data to a clean CSV format

## Installation

1. Clone this repository
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Place your Wells Fargo PDF statements in a folder
2. Run the script:
```bash
python wf_statement_converter.py --input_folder /path/to/pdf/folder --output_file output.csv
```

## Output Format
The generated CSV will contain the following columns:
- Date: Transaction date
- Description: Transaction description
- Amount: Transaction amount (positive for deposits, negative for withdrawals) 