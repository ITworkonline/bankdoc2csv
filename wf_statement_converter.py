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
            if not text:
                continue
            lines = text.split('\n')
            for line in lines:
                if not line.strip() or 'Beginning balance' in line or 'Ending balance' in line:
                    continue
                # 只匹配行首日期
                date_pattern = r'^(\d{1,2}/\d{1,2})'
                date_match = re.match(date_pattern, line)
                if not date_match:
                    continue
                date_str = date_match.group(1)
                try:
                    current_year = datetime.now().year
                    date = datetime.strptime(f"{date_str}/{current_year}", "%m/%d/%Y")
                except ValueError:
                    continue
                # 去掉日期部分
                rest = line[len(date_str):].strip()
                # 提取所有金额
                amount_pattern = r'([\d,]+\.\d{2})'
                amounts = re.findall(amount_pattern, rest)
                if not amounts:
                    continue
                # 只保留前两个金额（一般第一个是收入/支出，第二个是余额）
                if len(amounts) >= 2:
                    amount_str = amounts[0]  # 只取第一个金额
                else:
                    amount_str = amounts[0]
                # 提取描述（去掉所有金额部分，只保留前面的内容）
                desc_split = re.split(amount_pattern, rest, maxsplit=1)
                description = desc_split[0].strip() if desc_split else rest
                # 判断正负
                try:
                    amount = float(amount_str.replace(',', ''))
                    is_deposit = any(keyword in description.lower() for keyword in ['deposit', 'credit', 'refund', 'transfer in'])
                    if not is_deposit:
                        amount = -amount
                except Exception:
                    continue
                transactions.append({
                    'Date': date,
                    'Description': description,
                    'Amount': amount
                })
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