"""
Billing Analysis Agent for MCP integration
Handles automated billing data processing and report generation
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from billing_analyzer import BillingAnalyzer

class BillingAgent:
    """Agent for automated billing analysis and reporting."""
    
    def __init__(self):
        self.analyzer = BillingAnalyzer()
        self.unknown_categories_file = "unknown_categories.json"
        
    def process_monthly_billing(self):
        """Main workflow for monthly billing processing."""
        try:
            print("🤖 Billing Agent: Starting monthly analysis...")
            
            # Run complete analysis
            df, unknown_merchants = self.analyzer.analyze_all()
            
            # Save unknown merchants for human review
            if len(unknown_merchants) > 0:
                self.save_unknown_categories(unknown_merchants)
                
            # Generate summary report
            report = self.generate_summary_report(df)
            
            print("✅ Billing Agent: Analysis complete!")
            return report
            
        except Exception as e:
            print(f"❌ Billing Agent Error: {e}")
            return {"error": str(e)}
    
    def save_unknown_categories(self, unknown_merchants):
        """Save unknown merchants to file for human review."""
        existing_data = {}
        
        # Load existing unknown categories
        if os.path.exists(self.unknown_categories_file):
            try:
                with open(self.unknown_categories_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except:
                existing_data = {}
        
        # Add new unknown merchants
        for merchant in unknown_merchants:
            if merchant not in existing_data:
                existing_data[merchant] = {
                    "suggested_category": "Unknown",
                    "human_reviewed": False,
                    "date_added": datetime.now().isoformat()
                }
        
        # Save updated data
        with open(self.unknown_categories_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Saved {len(unknown_merchants)} merchants for human review")
    
    def load_human_categories(self):
        """Load human-reviewed categories."""
        if not os.path.exists(self.unknown_categories_file):
            return {}
            
        try:
            with open(self.unknown_categories_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Return only human-reviewed categories
            return {
                merchant: info["suggested_category"] 
                for merchant, info in data.items() 
                if info.get("human_reviewed", False)
            }
        except:
            return {}
    
    def generate_summary_report(self, df):
        """Generate summary report for the analysis."""
        total_transactions = len(df)
        total_amount = df['Amount'].sum()
        date_range = f"{df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}"
        
        # Category breakdown
        category_summary = df.groupby('Category')['Amount'].agg(['sum', 'count']).round(2)
        
        # Monthly breakdown
        df['Month'] = df['Date'].dt.to_period('M')
        monthly_summary = df.groupby('Month')['Amount'].sum().round(2)
        
        # Convert to JSON-serializable format
        category_dict = {}
        for category in category_summary.index:
            category_dict[category] = {
                "sum": float(category_summary.loc[category, 'sum']),
                "count": int(category_summary.loc[category, 'count'])
            }
        
        monthly_dict = {str(month): float(amount) for month, amount in monthly_summary.items()}
        
        report = {
            "analysis_date": datetime.now().isoformat(),
            "summary": {
                "total_transactions": total_transactions,
                "total_amount": float(total_amount),
                "date_range": date_range
            },
            "by_category": category_dict,
            "by_month": monthly_dict,
            "files_processed": df['Source_File'].nunique()
        }
        
        # Save report
        report_file = f"billing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"📊 Report saved as {report_file}")
        return report

# MCP Tool definitions
def get_tools():
    """Return MCP tool definitions for this agent."""
    return [
        {
            "name": "process_billing",
            "description": "Process all billing files and generate monthly report",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "review_unknown_categories", 
            "description": "Get list of merchants needing categorization",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "update_category",
            "description": "Update category for a merchant",
            "inputSchema": {
                "type": "object", 
                "properties": {
                    "merchant": {"type": "string"},
                    "category": {"type": "string"}
                },
                "required": ["merchant", "category"]
            }
        }
    ]

def handle_tool_call(name, arguments):
    """Handle MCP tool calls."""
    agent = BillingAgent()
    
    if name == "process_billing":
        return agent.process_monthly_billing()
        
    elif name == "review_unknown_categories":
        if os.path.exists(agent.unknown_categories_file):
            with open(agent.unknown_categories_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            unreviewed = {
                merchant: info for merchant, info in data.items()
                if not info.get("human_reviewed", False)
            }
            return {"unreviewed_merchants": unreviewed}
        return {"unreviewed_merchants": {}}
        
    elif name == "update_category":
        merchant = arguments.get("merchant")
        category = arguments.get("category")
        
        if not merchant or not category:
            return {"error": "Missing merchant or category"}
            
        # Update the unknown categories file
        if os.path.exists(agent.unknown_categories_file):
            with open(agent.unknown_categories_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {}
            
        data[merchant] = {
            "suggested_category": category,
            "human_reviewed": True,
            "date_reviewed": datetime.now().isoformat()
        }
        
        with open(agent.unknown_categories_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        return {"success": True, "message": f"Updated {merchant} -> {category}"}
    
    return {"error": f"Unknown tool: {name}"}

if __name__ == "__main__":
    # Test the agent
    agent = BillingAgent()
    result = agent.process_monthly_billing()
    print(json.dumps(result, indent=2, default=str))