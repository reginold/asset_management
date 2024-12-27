import pandas as pd
import openai
import os
import matplotlib.pyplot as plt

openai.api_key = os.getenv("SAMBANOVA_API_KEY")
openai.api_base = "https://api.sambanova.ai/v1"  # Use a custom base URL if required


def read_csv(file_path):
    """Reads a CSV file and returns a DataFrame."""
    return pd.read_csv(file_path, encoding='cp932')

def categorize_item(item):
    """Categorizes an item using the OpenAI API."""
    response = openai.ChatCompletion.create(
        model="Meta-Llama-3.1-405B-Instruct",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": f"Categorize the item: {item}"}
        ],
        max_tokens=1024
    )
    return response.choices[0].text.strip()

def categorize_items(df, column_name):
    """Categorizes items in a specified column of a DataFrame."""
    df['Category'] = df[column_name].apply(categorize_item)
    return df

def plot_pie_chart(df, value_column, category_column):
    """Plots a pie chart of the summed values by category."""
    category_sum = df.groupby(category_column)[value_column].sum()
    plt.figure(figsize=(10, 7))
    category_sum.plot.pie(autopct='%1.1f%%')
    plt.title('Payment Distribution by Category')
    plt.ylabel('')
    plt.show()

def main(file_path):
    df = read_csv(file_path)
    print(df.head())
    df = categorize_items(df, 'Item')
    plot_pie_chart(df, 'Price', 'Category')

if __name__ == "__main__":
    file_path = '/Users/bowenl/Downloads/202501.csv'
    main(file_path)