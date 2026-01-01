# 💰 Monthly Billing Optimizer

AI-powered family billing management system with automatic categorization, expense analysis, and budget recommendations.

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up API key
echo 'SAMBANOVA_API_KEY="your-key-here"' > .env

# 3. Run analysis
python categorize.py --file_name 202507.xlsx
python analyze.py --file_name 202507.xlsx
python recommend.py --file_name 202507.xlsx
```

## 📁 Project Structure

```
asset_management/
├── .env                          # API keys
├── requirements.txt              # Python dependencies
├── README.md                     # This file
│
├── data/
│   └── billing/                  # Excel billing files
│       ├── 202507.xlsx
│       └── 202508.xlsx
│
├── categorize.py                 # AI-powered expense categorization
├── analyze.py                    # Generate summary & visualizations
├── recommend.py                  # AI financial recommendations
└── read_billing.py               # View billing data
```

## 🎯 Features

### 1. **AI Categorization** (`categorize.py`)
- Uses SambaNova AI (Llama-3.3-Swallow-70B) for intelligent categorization
- Supports 12 expense categories (Food, Transportation, Travel, etc.)
- Interactive confirmation for each item
- Bilingual category names (English/中文)

### 2. **Visual Analysis** (`analyze.py`)
- **Summary Statistics**: Total, count, average spending
- **4-Panel Visualization**:
  - Total spending by category (bar chart)
  - Expense distribution (pie chart - top 6)
  - Daily spending trend (line chart)
  - Transaction count by category (bar chart)

### 3. **AI Recommendations** (`recommend.py`)
- Powered by Qwen3-235B reasoning model
- Provides spending pattern analysis
- Suggests budget optimizations
- Compares with historical data
- Outputs markdown report

## 📊 Supported Categories

| English | 中文 |
|---------|------|
| Food | 餐饮 |
| Transportation | 交通 |
| Utilities | 公用事业 |
| Shopping | 购物 |
| Clothes | 服装 |
| Subscription | 订阅 |
| Travel | 旅行 |
| Entertainment | 娱乐 |
| Healthcare | 医疗 |
| Convenience Store | 便利店 |
| Vending Machine | 自动售货机 |
| Movie | 电影 |

## 🔧 Usage

### Step 1: Read Billing Data
```bash
python read_billing.py --file_name 202507.xlsx
```

### Step 2: Categorize Expenses
```bash
python categorize.py --file_name 202507.xlsx
```

Interactive process:
```
Item: 東京ガス
Amount: 9232 JPY
Suggested Category: Utilities/公用事业

Confirm? (y/n or enter custom category): y
```

### Step 3: Generate Analysis
```bash
python analyze.py --file_name 202507.xlsx
```

Output:
- Console summary with category breakdown
- `expense_analysis_202507.png` - 4-panel chart

### Step 4: Get AI Recommendations
```bash
python recommend.py --file_name 202507.xlsx
```

You'll be prompted to provide context:
```
EXPENSE PERIOD: 2025-05-14 to 2025-06-12

Please provide context for this month's expenses:
(e.g., business trip from May 27-30, girlfriend's birthday on June 9, etc.)

Enter your activities (press Enter twice when done):
> Business trip to Osaka from May 28-30
> Girlfriend's birthday on June 9
>
```

Output:
- Console: AI recommendations
- `recommendation_202507.md` - Detailed markdown report

## ⚙️ Configuration

### Environment Variables (`.env`)
```bash
SAMBANOVA_API_KEY="your-sambanova-api-key"
```

Get your free API key at: https://sambanova.ai

### Excel File Format
Place your billing Excel files in `data/billing/` with format:

| Date | Item | Amount | Note |
|------|------|--------|------|
| 2025-05-14 | 東京ガス | 9232 | ・１６０２—０８５—１０８１ |

## 📈 Output Examples

### Analysis Summary
```
==========================================================
MONTHLY EXPENSE SUMMARY - 202507
==========================================================

Total Expenses: ¥878,273
Number of Transactions: 106
Average Transaction: ¥8,285

==========================================================
BREAKDOWN BY CATEGORY
==========================================================

Travel/旅行
  Total: ¥233,697 (26.6%)
  Transactions: 3
  Average: ¥77,899
```

### Recommendation Report (Markdown)
```markdown
# AI财务建议报告 - 202507

## 用户背景
Business trip to Osaka from May 28-30
Girlfriend's birthday on June 9

## 分析与建议
...
```

## 🛠️ Dependencies

Key packages (see `requirements.txt`):
- `pandas` - Data processing
- `openpyxl` - Excel file handling
- `matplotlib` - Visualizations
- `requests` - API calls
- `python-dotenv` - Environment variables

Install all:
```bash
pip install -r requirements.txt
```

## 🌐 API Models

This system uses SambaNova Cloud API:

1. **Categorization**: `Llama-3.3-Swallow-70B-Instruct-v0.4`
   - Fast, accurate categorization
   - Japanese language support

2. **Recommendations**: `Qwen3-235B`
   - Advanced reasoning
   - Chinese language output
   - Financial analysis expertise

## 📝 Notes

- All category names use bilingual format: `English/中文`
- Charts automatically adjust for Chinese/Japanese text display
- Pie chart shows top 6 categories to avoid label overlap
- Recommendations are saved as `.md` files for easy viewing

## 🐛 Troubleshooting

**Issue**: `ModuleNotFoundError: No module named 'pandas'`
```bash
pip install -r requirements.txt
```

**Issue**: API error
- Check your `.env` file has correct API key
- Verify API key is valid at https://sambanova.ai

**Issue**: Excel file not found
```bash
# Ensure file is in correct location
ls data/billing/202507.xlsx
```

## 📄 License

MIT License - feel free to use and modify

---

**Built with Claude Code** 🤖 - Simple, functional billing optimization
