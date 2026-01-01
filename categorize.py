import pandas as pd
import requests
import os
import argparse
from dotenv import load_dotenv

load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument('--file_name', type=str, required=True, help='Billing Excel file name (e.g., 202507.xlsx)')
args = parser.parse_args()

file_path = f'/Users/bowenl/work/asset_management/data/billing/{args.file_name}'
df = pd.read_excel(file_path, header=None)
df.columns = ['Date', 'Item', 'Amount', 'Note']

if 'Category' not in df.columns:
    df['Category'] = ''

def categorize_item(item_name):
    url = "https://api.sambanova.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.environ.get('SAMBANOVA_API_KEY')}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "Llama-3.3-Swallow-70B-Instruct-v0.4",
        "messages": [{
            "role": "user",
            "content": f"Categorize this expense item into ONE category only. Item: {item_name}\n\nCategories:\n- Food/餐饮\n- Transportation/交通\n- Utilities/公用事业\n- Shopping/购物\n- Clothes/服装\n- Subscription/订阅\n- Travel/旅行\n- Entertainment/娱乐\n- Healthcare/医疗\n- Convenience Store/便利店\n- Vending Machine/自动售货机\n- Movie/电影\n\nReturn only the category in 'English/Chinese' format (e.g., Food/餐饮), nothing else. Do NOT use 'Other' category."
        }],
        "max_tokens": 32000,
        "stream": False
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    if 'choices' in result:
        return result['choices'][0]['message']['content'].strip()
    else:
        print(f"API Error: {result}")
        return "Other"

for idx, row in df.iterrows():
    if pd.isna(row['Category']) or row['Category'] == '':
        item = row['Item']
        suggested_category = categorize_item(item)

        print(f"\nItem: {item}")
        print(f"Amount: {row['Amount']} JPY")
        print(f"Suggested Category: {suggested_category}")

        confirm = input("Confirm? (y/n or enter custom category): ").strip()

        if confirm.lower() == 'y':
            df.at[idx, 'Category'] = suggested_category
        elif confirm.lower() == 'n':
            custom = input("Enter category: ").strip()
            df.at[idx, 'Category'] = custom
        else:
            df.at[idx, 'Category'] = confirm

df.to_excel(file_path, index=False, header=False)
print(f"\nCategories saved to: {file_path}")
