import pandas as pd
import matplotlib.pyplot as plt
import os
from openai import OpenAI
import numpy as np

client = OpenAI(
    base_url="https://api.sambanova.ai/v1", 
    api_key=os.environ.get("SAMBANOVA_API_KEY")
)

def read_csv(file_path):
    """Reads a CSV file with proper encoding and column names."""
    try:
        df = pd.read_csv(file_path, encoding='shift_jis', header=None)
        df.columns = ['Date', 'Description', 'Type', 'Payment_Method', 'Unknown1', 'Bill_Date', 'Amount', 'Amount_JPY', 'Unknown2', 'Foreign_Amount', 'Currency', 'Exchange_Rate', 'Settlement_Date']
        df['Date'] = pd.to_datetime(df['Date'], format='%Y/%m/%d')
        df['Amount_JPY'] = pd.to_numeric(df['Amount_JPY'], errors='coerce')
        df = df.dropna(subset=['Amount_JPY'])
        return df
    except UnicodeDecodeError:
        print("Trying alternative encoding...")
        df = pd.read_csv(file_path, encoding='utf-8', header=None)
        df.columns = ['Date', 'Description', 'Type', 'Payment_Method', 'Unknown1', 'Bill_Date', 'Amount', 'Amount_JPY', 'Unknown2', 'Foreign_Amount', 'Currency', 'Exchange_Rate', 'Settlement_Date']
        df['Date'] = pd.to_datetime(df['Date'], format='%Y/%m/%d')
        df['Amount_JPY'] = pd.to_numeric(df['Amount_JPY'], errors='coerce')
        df = df.dropna(subset=['Amount_JPY'])
        return df

def calculate_total_expenses(df):
    """Calculates the total expenses from the DataFrame."""
    total_expenses = df['Amount_JPY'].sum()
    print(f"Total Expenses: ¥{total_expenses:,.0f}")
    return total_expenses

def generate_monthly_summary(df):
    """Generates a monthly expense summary."""
    df['Month'] = df['Date'].dt.to_period('M')
    monthly_summary = df.groupby('Month').agg({
        'Amount_JPY': ['sum', 'count', 'mean'],
        'Description': lambda x: list(x)[:5]  # Top 5 descriptions per month
    }).round(2)
    
    print("Monthly Expense Summary:")
    print("=" * 50)
    for month in monthly_summary.index:
        total = monthly_summary.loc[month, ('Amount_JPY', 'sum')]
        count = monthly_summary.loc[month, ('Amount_JPY', 'count')]
        avg = monthly_summary.loc[month, ('Amount_JPY', 'mean')]
        print(f"\n{month}:")
        print(f"  Total Expenses: ¥{total:,.0f}")
        print(f"  Number of Transactions: {count}")
        print(f"  Average per Transaction: ¥{avg:,.0f}")
    
    return monthly_summary

import matplotlib.font_manager as fm

def create_expense_visualization(df):
    """Creates pie chart visualizations for expense analysis."""
    import matplotlib.font_manager as fm
    
    # Create merchant analysis (top spending by description)
    merchant_data = df.groupby('Description')['Amount_JPY'].sum().nlargest(8)
    other_amount = df['Amount_JPY'].sum() - merchant_data.sum()
    
    # Add "Others" category if there are more merchants
    if other_amount > 0:
        others_series = pd.Series([other_amount], index=['Others'])
        merchant_data = pd.concat([merchant_data, others_series])
    
    # Set font for Japanese characters
    font_path = '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc'
    try:
        prop = fm.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = prop.get_name()
    except:
        prop = None
        print("Japanese font not found, using default font")
    
    # Create subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Pie chart for top merchants
    colors = plt.cm.Set3(range(len(merchant_data)))
    wedges, texts, autotexts = ax1.pie(merchant_data.values, labels=merchant_data.index, 
                                       autopct='%1.1f%%', startangle=90, colors=colors)
    ax1.set_title('Spending by Merchant', fontsize=14, fontproperties=prop)
    
    # Adjust text properties for better readability
    for text in texts:
        text.set_fontsize(10)
        if prop:
            text.set_fontproperties(prop)
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(9)
    
    # Monthly spending pie chart
    df['Month'] = df['Date'].dt.to_period('M')
    monthly_data = df.groupby('Month')['Amount_JPY'].sum()
    
    # Create month labels with amounts
    month_labels = [f'{month}\n¥{amount:,.0f}' for month, amount in monthly_data.items()]
    
    wedges2, texts2, autotexts2 = ax2.pie(monthly_data.values, labels=month_labels, 
                                          autopct='%1.1f%%', startangle=90,
                                          colors=['#ff9999', '#66b3ff'])
    ax2.set_title('Monthly Spending Distribution', fontsize=14, fontproperties=prop)
    
    # Adjust text properties
    for text in texts2:
        text.set_fontsize(10)
    for autotext in autotexts2:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(9)
    
    plt.tight_layout()
    plt.savefig('expense_analysis.png', bbox_inches='tight', dpi=300)
    plt.close()
    
    return merchant_data

def analyze_spending_patterns(df):
    """Analyzes spending patterns and provides insights."""
    # Calculate key metrics
    total_spending = df['Amount_JPY'].sum()
    avg_transaction = df['Amount_JPY'].mean()
    transaction_count = len(df)
    
    # Find top merchants
    top_merchants = df.groupby('Description')['Amount_JPY'].agg(['sum', 'count']).sort_values('sum', ascending=False).head(5)
    
    # Daily spending analysis
    df['Day'] = df['Date'].dt.date
    daily_spending = df.groupby('Day')['Amount_JPY'].sum()
    avg_daily_spending = daily_spending.mean()
    max_spending_day = daily_spending.idxmax()
    max_spending_amount = daily_spending.max()
    
    print("\nSpending Pattern Analysis:")
    print("=" * 50)
    print(f"Total Spending: ¥{total_spending:,.0f}")
    print(f"Average Transaction: ¥{avg_transaction:,.0f}")
    print(f"Total Transactions: {transaction_count}")
    print(f"Average Daily Spending: ¥{avg_daily_spending:,.0f}")
    print(f"Highest Spending Day: {max_spending_day} (¥{max_spending_amount:,.0f})")
    
    print("\nTop 5 Merchants by Total Spending:")
    for idx, (merchant, data) in enumerate(top_merchants.iterrows(), 1):
        print(f"{idx}. {merchant}: ¥{data['sum']:,.0f} ({data['count']} transactions)")
    
    return {
        'total_spending': total_spending,
        'avg_transaction': avg_transaction,
        'top_merchants': top_merchants,
        'daily_spending': daily_spending
    }

def suggest_cost_reduction(df, analysis_data):
    """Generates cost-reduction suggestions using AI and data analysis."""
    top_merchants_dict = analysis_data['top_merchants']['sum'].to_dict()
    total_spending = analysis_data['total_spending']
    
    # Create spending summary for AI
    spending_summary = f"""Total monthly spending: ¥{total_spending:,.0f}
Top spending categories:
"""
    for merchant, amount in list(top_merchants_dict.items())[:5]:
        percentage = (amount / total_spending) * 100
        spending_summary += f"- {merchant}: ¥{amount:,.0f} ({percentage:.1f}%)\n"
    
    try:
        prompt = [
            {
                "role": "system",
                "content": "You are a Japanese financial advisor. Analyze spending patterns and provide specific, actionable cost reduction suggestions. Focus on practical advice for Japanese consumers."
            },
            {
                "role": "user",
                "content": f"Based on this spending data:\n{spending_summary}\n\nProvide 5 specific cost reduction strategies with estimated savings amounts in Japanese Yen."
            }
        ]
        response = client.chat.completions.create(
            model="DeepSeek-R1-0528",
            messages=prompt,
            max_tokens=1024
        )
        ai_suggestions = response.choices[0].message.content
    except Exception as e:
        ai_suggestions = f"AI suggestions unavailable: {e}"
    
    print("\nCost Reduction Recommendations:")
    print("=" * 50)
    print(ai_suggestions)
    
    # Add data-driven suggestions
    print("\nData-Driven Insights:")
    print("-" * 30)
    
    # Find frequent small transactions that could be optimized
    small_frequent = df[df['Amount_JPY'] < 1000].groupby('Description')['Amount_JPY'].agg(['sum', 'count'])
    small_frequent = small_frequent[small_frequent['count'] >= 3].sort_values('sum', ascending=False)
    
    if not small_frequent.empty:
        print("Frequent small purchases to consider reducing:")
        for merchant, data in small_frequent.head(3).iterrows():
            print(f"- {merchant}: ¥{data['sum']:,.0f} across {data['count']} transactions")
    
    return ai_suggestions

# Main Script
if __name__ == "__main__":
    file_path = "202509.csv"
    
    print("Loading and analyzing expense data...")
    df = read_csv(file_path)
    
    print(f"\nLoaded {len(df)} transactions from {file_path}")
    print(f"Date range: {df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}")
    
    # Calculate total expenses
    total_expenses = calculate_total_expenses(df)
    
    # Generate monthly summary
    monthly_summary = generate_monthly_summary(df)
    
    # Analyze spending patterns
    analysis_data = analyze_spending_patterns(df)
    
    # Create visualizations
    print("\nCreating expense visualizations...")
    top_merchants = create_expense_visualization(df)
    
    # Generate cost reduction suggestions
    suggestions = suggest_cost_reduction(df, analysis_data)
    
    print("\nAnalysis complete! Check 'expense_analysis.png' for visualizations.")
