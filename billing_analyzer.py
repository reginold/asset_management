import pandas as pd
import os
import glob
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from openai import OpenAI

class BillingAnalyzer:
    """Analyzes billing data from Excel files in the billing folder."""
    
    def __init__(self, billing_folder="billing", api_key=None):
        self.billing_folder = billing_folder
        self.client = OpenAI(
            base_url="https://api.sambanova.ai/v1", 
            api_key=api_key or os.environ.get("SAMBANOVA_API_KEY")
        ) if api_key or os.environ.get("SAMBANOVA_API_KEY") else None
        
    def read_billing_files(self):
        """Read all Excel files from billing folder and combine into single DataFrame."""
        xlsx_files = glob.glob(os.path.join(self.billing_folder, "*.xlsx"))
        
        if not xlsx_files:
            raise FileNotFoundError(f"No Excel files found in {self.billing_folder} folder")
        
        all_data = []
        
        for file_path in xlsx_files:
            try:
                df = pd.read_excel(file_path)
                
                # Standardize column names based on expected structure
                if len(df.columns) >= 3:
                    df = df.iloc[:, :4]  # Take first 4 columns
                    df.columns = ['Date', 'Merchant', 'Amount', 'Reference']
                    
                    # Clean and standardize data
                    df['Date'] = pd.to_datetime(df['Date'])
                    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
                    df = df.dropna(subset=['Amount'])
                    df['Source_File'] = os.path.basename(file_path)
                    
                    all_data.append(df)
                    print(f"Loaded {len(df)} transactions from {file_path}")
                    
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue
        
        if not all_data:
            raise ValueError("No valid billing data found")
            
        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df = combined_df.sort_values('Date')
        
        print(f"\nTotal: {len(combined_df)} transactions loaded")
        print(f"Date range: {combined_df['Date'].min().strftime('%Y-%m-%d')} to {combined_df['Date'].max().strftime('%Y-%m-%d')}")
        
        return combined_df
    
    def categorize_merchants(self, df):
        """Categorize merchants using human-reviewed categories and advanced categorization engine."""
        import json
        import os
        from categorization_engine import CategorizationEngine
        
        # Load human-reviewed categories first
        human_categories = {}
        if os.path.exists("unknown_categories.json"):
            try:
                with open("unknown_categories.json", 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for merchant, info in data.items():
                    if info.get("human_reviewed", False):
                        category = info.get("suggested_category", "Unknown")
                        if category != "Unknown":
                            human_categories[merchant] = category
                
                print(f"Loaded {len(human_categories)} human-reviewed categories")
            except Exception as e:
                print(f"Error loading human categories: {e}")
        
        # Initialize categorization engine for remaining merchants
        engine = CategorizationEngine(api_key=self.client.api_key if self.client else None)
        
        # Get unique merchants for processing
        unique_merchants = df['Merchant'].dropna().unique().tolist()
        
        print(f"Categorizing {len(unique_merchants)} unique merchants...")
        
        # Apply categorization with priority: human > engine > unknown
        def get_category(merchant):
            if pd.isna(merchant):
                return 'Unknown'
            
            # First check human-reviewed categories
            if merchant in human_categories:
                return human_categories[merchant]
            
            # Fall back to engine categorization
            category, confidence, method = engine.categorize_merchant(merchant)
            return category
        
        df['Category'] = df['Merchant'].apply(get_category)
        
        # Track statistics
        category_counts = df['Category'].value_counts().to_dict()
        human_count = len(human_categories)
        engine_count = len(unique_merchants) - human_count
        unknown_count = category_counts.get('Unknown', 0)
        
        print(f"\nCategorization Results:")
        print(f"  Total merchants: {len(unique_merchants)}")
        print(f"  Human-reviewed: {human_count}")
        print(f"  Engine-categorized: {engine_count}")
        print(f"  Unknown/Uncategorized: {unknown_count}")
        
        print(f"\nCategory Distribution:")
        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = count / len(unique_merchants) * 100
            print(f"  {category}: {count} merchants ({percentage:.1f}%)")
        
        # Find merchants still needing review (should be very few now)
        remaining_unknown = df[df['Category'] == 'Unknown']['Merchant'].unique().tolist()
        
        if remaining_unknown:
            print(f"\nMerchants still needing categorization:")
            for merchant in remaining_unknown[:5]:
                print(f"  - {merchant}")
            if len(remaining_unknown) > 5:
                print(f"  ... and {len(remaining_unknown) - 5} more")
        else:
            print(f"\n✅ All merchants have been categorized!")
        
        return df, remaining_unknown
    
    def categorize_with_llm(self, unknown_merchants):
        """Use LLM to suggest categories for unknown merchants."""
        if not self.client or len(unknown_merchants) == 0:
            return {}
        
        try:
            merchants_text = "\n".join([f"- {merchant}" for merchant in unknown_merchants[:20]])
            
            prompt = [
                {
                    "role": "system", 
                    "content": "You are a financial categorization expert for Japanese consumers. Categorize merchants into these categories: Shopping, Utilities, Transportation, Food & Dining, Entertainment, Digital Services, Healthcare, Education, Clothing, Other. Respond with merchant:category pairs, one per line."
                },
                {
                    "role": "user",
                    "content": f"Categorize these merchants:\n{merchants_text}"
                }
            ]
            
            response = self.client.chat.completions.create(
                model="DeepSeek-R1-0528",
                messages=prompt,
                max_tokens=1024
            )
            
            # Parse response
            suggestions = {}
            for line in response.choices[0].message.content.split('\n'):
                if ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        merchant = parts[0].strip('- ')
                        category = parts[1].strip()
                        suggestions[merchant] = category
            
            return suggestions
            
        except Exception as e:
            print(f"LLM categorization failed: {e}")
            return {}
    
    def generate_monthly_report(self, df):
        """Generate comprehensive monthly billing report."""
        # Add month column
        df['Month'] = df['Date'].dt.to_period('M')
        
        # Monthly summary by category
        monthly_category = df.groupby(['Month', 'Category'])['Amount'].sum().unstack(fill_value=0)
        monthly_total = df.groupby('Month')['Amount'].sum()
        
        print("\n" + "="*60)
        print("MONTHLY BILLING REPORT")
        print("="*60)
        
        for month in monthly_total.index:
            print(f"\n{month}:")
            print(f"  Total: ¥{monthly_total[month]:,.0f}")
            
            if month in monthly_category.index:
                categories = monthly_category.loc[month].sort_values(ascending=False)
                categories = categories[categories > 0]
                
                print("  By Category:")
                for category, amount in categories.items():
                    percentage = (amount / monthly_total[month]) * 100
                    print(f"    {category}: ¥{amount:,.0f} ({percentage:.1f}%)")
        
        return monthly_category, monthly_total
    
    def create_monthly_visualization(self, df):
        """Create visualization for monthly billing data."""
        # Set up Japanese font
        font_path = '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc'
        try:
            prop = fm.FontProperties(fname=font_path)
            plt.rcParams['font.family'] = prop.get_name()
        except:
            prop = None
            print("Japanese font not found, using default font")
        
        df['Month'] = df['Date'].dt.to_period('M')
        
        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Monthly spending trend
        monthly_total = df.groupby('Month')['Amount'].sum()
        ax1.plot(range(len(monthly_total)), monthly_total.values, marker='o', linewidth=2)
        ax1.set_title('Monthly Spending Trend', fontproperties=prop)
        ax1.set_xlabel('Month', fontproperties=prop)
        ax1.set_ylabel('Amount (¥)', fontproperties=prop)
        ax1.tick_params(axis='x', rotation=45)
        ax1.set_xticks(range(len(monthly_total)))
        ax1.set_xticklabels([str(m) for m in monthly_total.index])
        
        # 2. Category distribution (overall)
        category_total = df.groupby('Category')['Amount'].sum().sort_values(ascending=False)
        colors = plt.cm.Set3(range(len(category_total)))
        ax2.pie(category_total.values, labels=category_total.index, autopct='%1.1f%%', colors=colors)
        ax2.set_title('Spending by Category', fontproperties=prop)
        
        # 3. Top 10 merchants with amounts (filter out NaN merchants)
        df_clean = df.dropna(subset=['Merchant'])
        top_merchants = df_clean.groupby('Merchant')['Amount'].sum().nlargest(10)
        bars = ax3.barh(range(len(top_merchants)), top_merchants.values, color='skyblue')
        ax3.set_yticks(range(len(top_merchants)))
        
        # Clean merchant names for display
        merchant_labels = []
        for merchant in top_merchants.index:
            if pd.isna(merchant):
                merchant_labels.append("Unknown")
            elif len(str(merchant)) > 25:
                merchant_labels.append(f"{str(merchant)[:25]}...")
            else:
                merchant_labels.append(str(merchant))
        
        ax3.set_yticklabels(merchant_labels, fontproperties=prop)
        ax3.set_title('Top 10 Merchants by Spending', fontproperties=prop)
        ax3.set_xlabel('Amount (¥)', fontproperties=prop)
        
        # Add amount labels on the bars
        for bar, amount in zip(bars, top_merchants.values):
            ax3.text(bar.get_width() + max(top_merchants.values) * 0.01, bar.get_y() + bar.get_height()/2, 
                    f'¥{amount:,.0f}', ha='left', va='center', fontsize=9, fontweight='bold')
        
        # 4. Top 10 highest individual transactions (filter out NaN merchants)
        top_transactions = df_clean.nlargest(10, 'Amount')[['Merchant', 'Amount', 'Date']]
        y_pos = range(len(top_transactions))
        
        bars4 = ax4.barh(y_pos, top_transactions['Amount'].values, color='lightcoral')
        ax4.set_yticks(y_pos)
        
        # Clean transaction labels for display
        transaction_labels = []
        for _, row in top_transactions.iterrows():
            merchant = str(row['Merchant']) if not pd.isna(row['Merchant']) else "Unknown"
            if len(merchant) > 20:
                transaction_labels.append(f"{merchant[:20]}...")
            else:
                transaction_labels.append(merchant)
        
        ax4.set_yticklabels(transaction_labels, fontproperties=prop)
        ax4.set_title('Top 10 Individual Transactions', fontproperties=prop)
        ax4.set_xlabel('Amount (¥)', fontproperties=prop)
        
        # Add amount labels on the transaction bars
        for bar, amount in zip(bars4, top_transactions['Amount'].values):
            ax4.text(bar.get_width() + max(top_transactions['Amount'].values) * 0.01, 
                    bar.get_y() + bar.get_height()/2, 
                    f'¥{amount:,.0f}', ha='left', va='center', fontsize=9, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('billing_analysis.png', bbox_inches='tight', dpi=300)
        plt.close()
        
        print("\nVisualization saved as 'billing_analysis.png'")
    
    def analyze_all(self):
        """Complete analysis workflow."""
        print("Starting billing analysis...")
        
        # Load data
        df = self.read_billing_files()
        
        # Categorize merchants
        df, unknown_merchants = self.categorize_merchants(df)
        
        # Try LLM categorization for unknowns
        if len(unknown_merchants) > 0:
            llm_suggestions = self.categorize_with_llm(unknown_merchants)
            print(f"\nLLM provided {len(llm_suggestions)} categorization suggestions")
        
        # Generate reports
        monthly_category, monthly_total = self.generate_monthly_report(df)
        
        # Create visualizations
        self.create_monthly_visualization(df)
        
        return df, unknown_merchants

if __name__ == "__main__":
    analyzer = BillingAnalyzer()
    df, unknown_merchants = analyzer.analyze_all()