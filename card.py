import pandas as pd
import matplotlib.pyplot as plt
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://api.sambanova.ai/v1", 
    api_key=os.environ.get("SAMBANOVA_API_KEY")
)

def read_csv(file_path):
    """Reads a CSV file and returns a DataFrame."""
    return pd.read_csv(file_path, encoding='utf-8')

def calculate_total_price(df):
    """Calculates the total price from the DataFrame."""
    total_price = df['Amount'].sum()
    print(f"Total Price: {total_price}")
    return total_price

def generate_monthly_report(df):
    """Generates a monthly report summarizing financial data."""
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month'] = df['Date'].dt.to_period('M')
    monthly_report = df.groupby('Month')['Amount'].sum()
    print("Monthly Report:\n", monthly_report)
    return monthly_report

import matplotlib.font_manager as fm

def create_pie_chart(df):
    """Creates a pie chart for categories and saves it as an image."""
    # Convert negative amounts to positive
    df['Amount'] = df['Amount'].abs()
    
    # Group by category and sum the amounts
    category_data = df.groupby('Category')['Amount'].sum()
    
    # Sort categories by amount and get the top 5
    top_categories = category_data.nlargest(5)
    other_categories = category_data.drop(top_categories.index).sum()
    top_categories['Others'] = other_categories
    
    # Set the font properties for Japanese characters
    font_path = '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc'  # Update this path if necessary
    prop = fm.FontProperties(fname=font_path)
    
    # Create the pie chart
    plt.figure(figsize=(10, 8))
    top_categories.plot.pie(autopct='%1.1f%%', textprops={'fontproperties': prop})
    plt.title('Expenditure by Category', fontproperties=prop)
    plt.ylabel('')
    
    # Add a legend with all categories and their values
    all_labels = [f'{cat}: {amt:.2f}' for cat, amt in category_data.items()]
    plt.legend(all_labels, loc='upper right', bbox_to_anchor=(1.3, 1.0), prop=prop)
    
    # Save the pie chart as an image
    plt.savefig('expenditure_by_category.png', bbox_inches='tight')
    plt.close()

def suggest_cost_reduction(df):
    """Generates cost-reduction suggestions using the OpenAI API."""
    prompt = [
        {
            "role": "system",
            "content": "You are a financial assistant. Analyze the following categories and expenditures: \n"
                       f"{df.groupby('Category')['Amount'].sum().to_dict()} \n"
                       "and provide actionable suggestions to reduce costs."
        },
        {
            "role": "user",
            "content": "Generate cost-reduction suggestions."
        }
    ]
    response = client.chat.completions.create(
        model="Meta-Llama-3.1-405B-Instruct",
        messages=prompt,
        max_tokens=1024
    )
    suggestions = response.choices[0].message.content
    print("Suggestions to Lower Costs:\n", suggestions)
    return suggestions

# Main Script
if __name__ == "__main__":
    file_path = "/Users/bowenl/Downloads/test.csv"  # Replace with your file path
    df = read_csv(file_path)

    # Calculate total price
    total_price = calculate_total_price(df)

    # Generate monthly report
    monthly_report = generate_monthly_report(df)

    # Create a pie chart
    create_pie_chart(df)

    # Provide suggestions to lower costs
    suggestions = suggest_cost_reduction(df)
