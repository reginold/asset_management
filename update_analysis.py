#!/usr/bin/env python3
"""
Quick Update Analysis Script
Run this after completing human categorization review to get updated reports
"""

import os
from billing_analyzer import BillingAnalyzer
from agents.billing_agent import BillingAgent

def main():
    print("🔄 UPDATING BILLING ANALYSIS WITH NEW CATEGORIES")
    print("=" * 60)
    
    # Check if there are human-reviewed categories
    if os.path.exists("unknown_categories.json"):
        import json
        with open("unknown_categories.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        reviewed_count = sum(1 for info in data.values() if info.get("human_reviewed", False))
        total_count = len(data)
        
        print(f"📊 Categorization Status:")
        print(f"  • Total merchants: {total_count}")
        print(f"  • Human reviewed: {reviewed_count}")
        print(f"  • Pending review: {total_count - reviewed_count}")
        
        if reviewed_count == 0:
            print("\n⚠️  No merchants have been categorized yet.")
            print("💡 Run 'python main.py --review' first to categorize merchants")
            return
        
        print(f"\n✅ Found {reviewed_count} categorized merchants")
    
    print(f"\n🔄 Regenerating analysis with updated categories...")
    
    # Run billing analysis
    agent = BillingAgent()
    result = agent.process_monthly_billing()
    
    if "error" in result and result["error"]:
        print(f"❌ Analysis failed: {result['error']}")
        return
    
    print("\n✅ Analysis completed successfully!")
    print("\n📁 Generated files:")
    print("  📊 billing_analysis.png - Updated visualizations")
    print("  📄 billing_report_*.json - Updated detailed report")
    
    # Show quick summary
    if "summary" in result:
        summary = result["summary"]
        print(f"\n📈 Quick Summary:")
        print(f"  • Total transactions: {summary.get('total_transactions', 0):,}")
        print(f"  • Total amount: ¥{summary.get('total_amount', 0):,.0f}")
        print(f"  • Date range: {summary.get('date_range', 'Unknown')}")
    
    # Show category breakdown
    if "by_category" in result:
        print(f"\n💰 Updated Category Breakdown:")
        categories = result["by_category"]
        for category, data in sorted(categories.items(), key=lambda x: x[1]["sum"], reverse=True):
            amount = data["sum"]
            count = data["count"]
            print(f"  • {category}: ¥{amount:,.0f} ({count} transactions)")
    
    # Check remaining uncategorized
    remaining = 0
    if os.path.exists("unknown_categories.json"):
        with open("unknown_categories.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        remaining = sum(1 for info in data.values() if not info.get("human_reviewed", False))
    
    if remaining > 0:
        print(f"\n💡 Next Steps:")
        print(f"  • {remaining} merchants still need categorization")
        print(f"  • Run 'python main.py --review' to continue categorizing")
        print(f"  • Run 'python update_analysis.py' again after more categorization")
    else:
        print(f"\n🎉 All merchants have been categorized!")
        print(f"  • Your billing analysis is now complete")
        print(f"  • Check 'billing_analysis.png' for the final visualizations")

if __name__ == "__main__":
    main()