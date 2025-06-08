#!/usr/bin/env python3

import os
import argparse
import pdfplumber
import pandas as pd
from datetime import datetime
import re

def extract_transactions_from_pdf(pdf_path):
    """
    Extract transactions from a Wells Fargo PDF statement.
    Returns a list of dictionaries containing transaction details.
    """
    transactions = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            
            # Split the text into lines
            lines = text.split('\n')
            
            # Process each line
            for line in lines:
                # Skip empty lines and headers
                if not line.strip() or 'Beginning balance' in line or 'Ending balance' in line:
                    continue
                
                # Try to match transaction patterns
                # Looking for date at the start of the line
                date_pattern = r'^(\d{1,2}/\d{1,2})'
                date_match = re.search(date_pattern, line)
                
                if date_match:
                    # Extract date
                    date_str = date_match.group(1)
                    try:
                        # Add current year (this might need adjustment for statements spanning year-end)
                        current_year = datetime.now().year
                        date = datetime.strptime(f"{date_str}/{current_year}", "%m/%d/%Y")
                        
                        # Extract amount - look for numbers with optional decimals and commas
                        amount_pattern = r'([\d,]+\.\d{2})'
                        amounts = re.findall(amount_pattern, line)
                        
                        if amounts:
                            amount = float(amounts[-1].replace(',', ''))
                            
                            # Determine if it's a deposit or withdrawal based on context
                            is_deposit = any(keyword in line.lower() for keyword in 
                                          ['deposit', 'credit', 'refund', 'transfer in'])
                            
                            # If not explicitly a deposit, treat as withdrawal
                            if not is_deposit:
                                amount = -amount
                            
                            # Get description - everything between date and amount
                            description = line.replace(date_str, '', 1)
                            description = re.sub(r'[\d,]+\.\d{2}', '', description).strip()
                            description = re.sub(r'\s+', ' ', description)
                            
                            transactions.append({
                                'Date': date,
                                'Description': description,
                                'Amount': amount
                            })
                    except ValueError:
                        continue
    
    return transactions

def process_pdf_folder(input_folder, output_file):
    """
    Process all PDF files in the input folder and create a combined CSV file.
    """
    all_transactions = []
    
    # Process each PDF file in the folder
    for filename in os.listdir(input_folder):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(input_folder, filename)
            try:
                transactions = extract_transactions_from_pdf(pdf_path)
                all_transactions.extend(transactions)
                print(f"Successfully processed {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
    
    if all_transactions:
        # Convert to DataFrame and sort by date
        df = pd.DataFrame(all_transactions)
        df = df.sort_values('Date')
        
        # Format the date column
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
        
        # Save to CSV
        df.to_csv(output_file, index=False)
        print(f"\nSuccessfully created CSV file: {output_file}")
        print(f"Total transactions processed: {len(df)}")
    else:
        print("No transactions were found in the PDF files.")

def main():
    parser = argparse.ArgumentParser(description='Convert Wells Fargo PDF statements to CSV')
    parser.add_argument('--input_folder', required=True, help='Folder containing PDF statements')
    parser.add_argument('--output_file', required=True, help='Output CSV file path')
    
    args = parser.parse_args()
    
    # Verify input folder exists
    if not os.path.isdir(args.input_folder):
        print(f"Error: Input folder '{args.input_folder}' does not exist.")
        return
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    process_pdf_folder(args.input_folder, args.output_file)

if __name__ == '__main__':
    main() 