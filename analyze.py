import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import argparse
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

parser = argparse.ArgumentParser()
parser.add_argument('--file_name', type=str, required=True, help='Billing Excel file name (e.g., 202507.xlsx)')
args = parser.parse_args()

file_path = f'/Users/bowenl/work/asset_management/data/billing/{args.file_name}'
month_code = args.file_name.replace('.xlsx', '')

df = pd.read_excel(file_path, header=None)
df.columns = ['Date', 'Item', 'Amount', 'Note', 'Category']

print("="*60)
print(f"MONTHLY EXPENSE SUMMARY - {month_code}")
print("="*60)

print(f"\nTotal Expenses: ¥{df['Amount'].sum():,.0f}")
print(f"Number of Transactions: {len(df)}")
print(f"Average Transaction: ¥{df['Amount'].mean():,.0f}")

print("\n" + "="*60)
print("BREAKDOWN BY CATEGORY")
print("="*60)

category_summary = df.groupby('Category')['Amount'].agg(['sum', 'count', 'mean']).sort_values('sum', ascending=False)
category_summary.columns = ['Total', 'Count', 'Average']

for idx, row in category_summary.iterrows():
    percentage = (row['Total'] / df['Amount'].sum()) * 100
    print(f"\n{idx}")
    print(f"  Total: ¥{row['Total']:,.0f} ({percentage:.1f}%)")
    print(f"  Transactions: {int(row['Count'])}")
    print(f"  Average: ¥{row['Average']:,.0f}")

fig, axes = plt.subplots(2, 2, figsize=(15, 12))

category_summary['Total'].plot(kind='bar', ax=axes[0, 0], color='steelblue')
axes[0, 0].set_title('Total Spending by Category', fontsize=14, fontweight='bold')
axes[0, 0].set_xlabel('Category')
axes[0, 0].set_ylabel('Amount (¥)')
axes[0, 0].tick_params(axis='x', rotation=45)

top_6_indices = category_summary.head(6).index
labels = [cat if cat in top_6_indices else '' for cat in category_summary.index]
autopct_func = lambda pct: f'{pct:.1f}%' if pct > (category_summary.head(6)['Total'].min() / category_summary['Total'].sum() * 100) else ''
axes[0, 1].pie(category_summary['Total'], labels=labels, autopct=autopct_func, startangle=90)
axes[0, 1].set_title('Expense Distribution', fontsize=14, fontweight='bold')

df['Date'] = pd.to_datetime(df['Date'])
daily_spending = df.groupby(df['Date'].dt.date)['Amount'].sum()
daily_spending.plot(kind='line', ax=axes[1, 0], marker='o', color='green')
axes[1, 0].set_title('Daily Spending Trend', fontsize=14, fontweight='bold')
axes[1, 0].set_xlabel('Date')
axes[1, 0].set_ylabel('Amount (¥)')
axes[1, 0].tick_params(axis='x', rotation=45)

category_summary['Count'].plot(kind='bar', ax=axes[1, 1], color='coral')
axes[1, 1].set_title('Transaction Count by Category', fontsize=14, fontweight='bold')
axes[1, 1].set_xlabel('Category')
axes[1, 1].set_ylabel('Number of Transactions')
axes[1, 1].tick_params(axis='x', rotation=45)

plt.tight_layout()
output_chart = f'/Users/bowenl/work/asset_management/expense_analysis_{month_code}.png'
plt.savefig(output_chart, dpi=300, bbox_inches='tight')
print("\n" + "="*60)
print(f"Chart saved: {output_chart}")
print("="*60)
