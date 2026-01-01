import pandas as pd
import requests
import os
import argparse
import json
from dotenv import load_dotenv
from fuzzywuzzy import fuzz

load_dotenv()

CACHE_FILE = '/Users/bowenl/work/asset_management/category_cache.json'

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

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
            "content": f"Categorize this expense item into ONE category only. Item: {item_name}\n\nCategories:\n- 食费/Food Expenses\n- 日用品/Daily Necessities\n- 衣服/Clothing\n- 美容/Beauty\n- 医疗费/Medical Expenses\n- 教育费/Education Expenses\n- 光热费/Utilities\n- 交通费/Transportation Expenses\n- 通信费/Communication Expenses\n- 住居费/Housing Expenses\n- パン/Bread\n- コーヒー/Coffee\n- 玩具/Toys\n- ガソリン/Gasoline\n- 遊ぼ/Leisure/Entertainment\n- 亚马逊/Amazon/Shopping\n- 税金/Taxes\n- Home Maintenance/家居维护\n- Insurance/保险\n- Hobbies/兴趣爱好\n- Vacation/度假\n- Home Improvement/家居改善\n\nReturn only the category in 'Category Name/English Translation' format (e.g., 食费/Food Expenses), nothing else. Do NOT use 'Other' category."}],
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

cache = load_cache()

for idx, row in df.iterrows():
    if pd.isna(row['Category']) or row['Category'] == '':
        item = row['Item']

        # Step 1: Check cache first
        if item in cache:
            suggested_category = cache[item]
            print(f"\n✓ Found in cache: {item}")
            print(f"Amount: {row['Amount']} JPY")
            print(f"Cached Category: {suggested_category}")
            confirm = input("Use cached? (y/n or enter new category): ").strip()
        else:
            # Step 2: Use LLM if not in cache
            suggested_category = categorize_item(item)
            print(f"\n[NEW] Item: {item}")
            print(f"Amount: {row['Amount']} JPY")
            print(f"AI Suggested: {suggested_category}")
            print(f"Date: {row['Date'].strftime('%Y-%m-%d')}")
            confirm = input("Confirm? (y/n or enter custom category): ").strip()

        if confirm.lower() == 'y':
            df.at[idx, 'Category'] = suggested_category
            cache[item] = suggested_category  # Save to cache
        elif confirm.lower() == 'n':
            custom = input("Enter category: ").strip()
            df.at[idx, 'Category'] = custom
            cache[item] = custom  # Save to cache
        else:
            df.at[idx, 'Category'] = confirm
            cache[item] = confirm  # Save to cache

save_cache(cache)
df.to_excel(file_path, index=False, header=False)
print(f"\nCategories saved to: {file_path}")
print(f"Cache updated: {len(cache)} merchants remembered")
