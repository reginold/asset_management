import pandas as pd
import requests
import os
import argparse
import json
from dotenv import load_dotenv
from fuzzywuzzy import fuzz

load_dotenv()

def web_search_categorize(item_name):
    """Use Tavily search API to help categorize unknown items"""
    try:
        # Use Tavily API for search
        tavily_url = "https://api.tavily.com/search"
        tavily_headers = {
            "Content-Type": "application/json"
        }
        tavily_data = {
            "api_key": os.environ.get('TAVILY_API_KEY'),
            "query": item_name,
            "max_results": 3
        }

        response = requests.post(tavily_url, headers=tavily_headers, json=tavily_data, timeout=10)

        if response.status_code != 200:
            return None

        search_results = response.json()

        if not search_results.get('results'):
            return None

        # Extract content from search results
        combined_info = ""
        for result in search_results['results'][:3]:
            combined_info += result.get('content', '') + " "

        if not combined_info.strip():
            return None

        # Use LLM to analyze search results and categorize
        url = "https://api.sambanova.ai/v1/chat/completions"
        api_headers = {
            "Authorization": f"Bearer {os.environ.get('SAMBANOVA_API_KEY')}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "Llama-3.3-Swallow-70B-Instruct-v0.4",
            "messages": [{
                "role": "user",
                "content": f"Categorize this expense item into ONE category only. Item: {item_name}\n\nCategories:\n- 食费/Food Expenses\n- 日用品/Daily Necessities\n- 衣服/Clothing\n- 美容/Beauty\n- 医疗费/Medical Expenses\n- 教育费/Education Expenses\n- 光热费/Utilities\n- 交通费/Transportation Expenses\n- 通信费/Communication Expenses\n- 住居费/Housing Expenses\n- パン/Bread\n- コーヒー/Coffee\n- 玩具/Toys\n- ガソリン/Gasoline\n- 遊ぼ/Leisure/Entertainment\n- 亚马逊/Amazon/Shopping\n- 税金/Taxes\n- Home Maintenance/家居维护\n- Insurance/保险\n- Hobbies/兴趣爱好\n- Vacation/度假\n- Home Improvement/家居改善\n\nReturn only the category in 'Category Name/English Translation' format (e.g., 食费/Food Expenses), please add new category based on your search result. Do NOT use 'Other' category.\n\nWeb search results for context: {combined_info[:8000]}"
            }],
            "max_tokens": 32000,
            "stream": False
        }

        llm_response = requests.post(url, headers=api_headers, json=data)
        llm_result = llm_response.json()

        if 'choices' in llm_result:
            return {
                'category': llm_result['choices'][0]['message']['content'].strip(),
                'info': combined_info[:200]
            }
    except Exception as e:
        print(f"Web search error: {e}")

    return None

CACHE_FILE = '/Users/bowenl/work/asset_management/category_cache.json'

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def find_fuzzy_match(item_name, cache, threshold=85):
    """Find similar items in cache using fuzzy matching"""
    best_match = None
    best_score = 0

    for cached_item, category in cache.items():
        score = fuzz.ratio(item_name, cached_item)
        if score > best_score and score >= threshold:
            best_score = score
            best_match = (cached_item, category, score)

    return best_match

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

        # Step 1: Exact cache match
        if item in cache:
            suggested_category = cache[item]
            print(f"\n✓ Exact match: {item}")
            print(f"Amount: {row['Amount']} JPY")
            print(f"Cached Category: {suggested_category}")
            confirm = input("Use cached? (y/n or enter new category): ").strip()

        else:
            # Step 2: Fuzzy match
            fuzzy_result = find_fuzzy_match(item, cache)

            if fuzzy_result:
                matched_item, category, score = fuzzy_result
                print(f"\n≈ Similar to: {matched_item} ({score}% match)")
                print(f"Item: {item}")
                print(f"Amount: {row['Amount']} JPY")
                print(f"Suggested Category: {category}")
                confirm = input("Use this? (y/n or enter custom category): ").strip()
                suggested_category = category

            else:
                # Step 3: LLM if no match
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
            print("\nSearching web for more information...")
            web_result = web_search_categorize(item)

            if web_result:
                print(f"Web info: {web_result['info']}")
                print(f"Web-based suggestion: {web_result['category']}")
                confirm2 = input("Use web suggestion? (y/n or enter custom): ").strip()

                if confirm2.lower() == 'y':
                    df.at[idx, 'Category'] = web_result['category']
                    cache[item] = web_result['category']
                elif confirm2.lower() == 'n':
                    custom = input("Enter category: ").strip()
                    df.at[idx, 'Category'] = custom
                    cache[item] = custom
                else:
                    df.at[idx, 'Category'] = confirm2
                    cache[item] = confirm2
            else:
                print("No web results found.")
                custom = input("Enter category: ").strip()
                df.at[idx, 'Category'] = custom
                cache[item] = custom
        else:
            df.at[idx, 'Category'] = confirm
            cache[item] = confirm  # Save to cache

save_cache(cache)
df.to_excel(file_path, index=False, header=False)
print(f"\nCategories saved to: {file_path}")
print(f"Cache updated: {len(cache)} merchants remembered")
