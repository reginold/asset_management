import pandas as pd
import requests
import os
import argparse
from dotenv import load_dotenv

load_dotenv()

def load_expense_data(file_path):
    df = pd.read_excel(file_path, header=None)
    df.columns = ['Date', 'Item', 'Amount', 'Note', 'Category']
    return df

def get_expense_summary(df):
    category_summary = df.groupby('Category')['Amount'].agg(['sum', 'count'])
    total_amount = df['Amount'].sum()
    date_range = f"{df['Date'].min()} to {df['Date'].max()}"

    summary = f"""
Month: 202507
Date Range: {date_range}
Total Spending: ¥{total_amount:,.0f}
Number of Transactions: {len(df)}

Category Breakdown:
{df.groupby('Category')['Amount'].sum().to_string()}

Top 10 Expenses:
{df.nlargest(10, 'Amount')[['Date', 'Item', 'Amount', 'Category']].to_string()}
"""
    return summary

def get_ai_recommendation(expense_summary, user_context):
    url = "https://api.sambanova.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.environ.get('SAMBANOVA_API_KEY')}",
        "Content-Type": "application/json"
    }

    prompt = f"""You are a financial advisor analyzing monthly expenses. Based on the expense data and user's activities, provide:

1. Spending Pattern Analysis - What stands out about this month?
2. Comparison Recommendations - Should compare with last 1 month or last 3 months? Why?
3. Optimization Suggestions - How to optimize future spending?
4. Budget Recommendations - Suggested budget allocations for next month

Expense Data:
{expense_summary}

User Context:
{user_context}

Provide detailed, actionable recommendations in a clear format in Chinese only."""

    data = {
        "model": "Qwen3-235B",
        "messages": [{
            "role": "user",
            "content": prompt
        }],
        "max_tokens": 32000,
        "stream": False
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    if 'choices' in result:
        recommendation = result['choices'][0]['message']['content']

        if '<think>' in recommendation:
            parts = recommendation.split('</think>')
            if len(parts) > 1:
                recommendation = parts[-1].strip()

        return recommendation
    else:
        return f"API Error: {result}"

def save_recommendation(recommendation, context, output_path, month_code):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# AI财务建议报告 - {month_code}\n\n")
        f.write("---\n\n")
        f.write(f"## 用户背景\n\n{context}\n\n")
        f.write("---\n\n")
        f.write("## 分析与建议\n\n")
        f.write(recommendation)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file_name', type=str, required=True, help='Billing Excel file name (e.g., 202507.xlsx)')
    args = parser.parse_args()

    file_path = f'/Users/bowenl/work/asset_management/data/billing/{args.file_name}'
    month_code = args.file_name.replace('.xlsx', '')

    df = load_expense_data(file_path)

    start_date = df['Date'].min().strftime('%Y-%m-%d')
    end_date = df['Date'].max().strftime('%Y-%m-%d')

    print("="*80)
    print(f"EXPENSE PERIOD: {start_date} to {end_date}")
    print("="*80)
    print("\nPlease provide context for this month's expenses:")
    print("(e.g., business trip from May 27-30, girlfriend's birthday on June 9, etc.)")
    print("\nEnter your activities (press Enter twice when done):")

    activities = []
    while True:
        line = input()
        if line == "":
            break
        activities.append(line)

    context = "\n".join(activities)
    summary = get_expense_summary(df)

    print("\nAnalyzing with AI...")

    recommendation = get_ai_recommendation(summary, context)

    print("\n" + "="*80)
    print("AI FINANCIAL RECOMMENDATIONS")
    print("="*80)
    print(recommendation)
    print("="*80)

    output_file = f'/Users/bowenl/work/asset_management/recommendation_{month_code}.md'
    save_recommendation(recommendation, context, output_file, month_code)
    print(f"\nRecommendation saved to: {output_file}")
