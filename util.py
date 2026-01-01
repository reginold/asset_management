import os
import json
import requests
from fuzzywuzzy import fuzz
from dotenv import load_dotenv

load_dotenv()

CACHE_FILE = '/Users/bowenl/work/asset_management/category_cache.json'

def load_cache():
    """Load category cache from JSON file"""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    """Save category cache to JSON file"""
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
