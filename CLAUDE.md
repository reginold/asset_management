# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based asset management and financial analysis tool with two main components:

1. **Web scraping module** (`run.py`) - Automated login and data extraction from SBI Securities website using Selenium
2. **Financial analysis module** (`card.py`) - CSV data processing, visualization, and AI-powered cost reduction suggestions

## Dependencies and Setup

Install dependencies:
```bash
pip install -r requirements.txt
```

Required environment variables:
- `SAMBANOVA_API_KEY` - API key for SambaNova's AI service (used for cost reduction suggestions)

## Architecture

### Web Scraping (`run.py`)
- Uses Selenium WebDriver with headless Chrome for automated browsing
- Configured for SBI Securities website login
- Requires manual configuration of `USER_ID` and `USER_PW` variables
- Sets up Chrome with specific options for headless operation

### Financial Analysis (`card.py`)
- **Data Processing**: Reads CSV files with financial transaction data
- **Visualization**: Creates pie charts showing expenditure by category using matplotlib
- **AI Integration**: Uses SambaNova's Llama model for generating cost reduction suggestions
- **Japanese Language Support**: Configured with Hiragino font for Japanese text rendering

### Data Format
The CSV files (like `202509.csv`) contain transaction data with columns including:
- Date
- Description/Merchant
- Category
- Amount
- Currency information

## Key Functions

### `card.py` Functions:
- `read_csv()` - Loads CSV data into pandas DataFrame
- `calculate_total_price()` - Sums total expenditure
- `generate_monthly_report()` - Groups transactions by month
- `create_pie_chart()` - Generates expenditure visualization
- `suggest_cost_reduction()` - AI-powered financial advice

### `run.py` Functions:
- `handler()` - Main entry point for web scraping
- `login_sbisec()` - Handles SBI Securities login process

## Running the Code

For financial analysis:
```bash
python card.py
```

For web scraping (requires configuration):
```bash
python run.py
```

## Important Notes

- The web scraping module requires valid SBI Securities credentials
- Chrome/Chromium browser and chromedriver must be available for Selenium
- Japanese font support is configured for visualization output
- AI suggestions require valid SambaNova API key
- CSV file path in `card.py` is hardcoded and may need adjustment