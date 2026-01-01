import pandas as pd
import argparse

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

parser = argparse.ArgumentParser()
parser.add_argument('--file_name', type=str, required=True, help='Billing Excel file name (e.g., 202507.xlsx)')
args = parser.parse_args()

file_path = f'/Users/bowenl/work/asset_management/data/billing/{args.file_name}'
df = pd.read_excel(file_path, header=None)
df.columns = ['Date', 'Item', 'Amount', 'Note']

print("=== Billing Data ===")
print(df)
print(f"\nTotal Amount: {df['Amount'].sum():,} JPY")
print(f"Number of items: {len(df)}")
