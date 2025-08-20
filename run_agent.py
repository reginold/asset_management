#!/usr/bin/env python3
"""
Simple Agent Runner - One Command to Rule Them All
Runs the complete billing analysis workflow using the billing agent
"""

import sys
import os
import json

def main():
    print("🚀 ASSET MANAGEMENT AGENT SYSTEM")
    print("=" * 60)
    print("Running complete monthly analysis workflow...")
    print()
    
    # Run billing agent directly
    try:
        from agents.billing_agent import BillingAgent
        
        print("🤖 Initializing Billing Agent...")
        agent = BillingAgent()
        
        print("📊 Processing monthly billing data...")
        result = agent.process_monthly_billing()
        
        if "error" in result and result["error"]:
            print(f"❌ Analysis failed: {result['error']}")
            sys.exit(1)
        
        print("🎉 Agent workflow completed successfully!")
        print()
        print("📊 Generated files:")
        print("  • billing_analysis.png - Comprehensive visualizations")
        print("  • billing_report_*.json - Detailed analysis report")
        if os.path.exists("unknown_categories.json"):
            print("  • unknown_categories.json - Merchants for human review")
        
        # Show quick summary
        if "summary" in result:
            summary = result["summary"]
            print(f"\n📈 Quick Summary:")
            print(f"  • Total transactions: {summary.get('total_transactions', 0):,}")
            print(f"  • Total amount: ¥{summary.get('total_amount', 0):,.0f}")
            print(f"  • Date range: {summary.get('date_range', 'Unknown')}")
        
        # Check for uncategorized merchants
        uncategorized_count = 0
        if os.path.exists("unknown_categories.json"):
            try:
                with open("unknown_categories.json", 'r', encoding='utf-8') as f:
                    data = json.load(f)
                uncategorized_count = sum(1 for info in data.values() if not info.get("human_reviewed", False))
            except:
                pass
        
        print()
        if uncategorized_count > 0:
            print("💡 Next steps:")
            print(f"  1. {uncategorized_count} merchants need categorization")
            print("  2. Run: python main.py --review")
            print("  3. After categorization, run: python update_analysis.py")
        else:
            print("✅ All merchants have been categorized!")
            print("💡 Check 'billing_analysis.png' for your complete financial analysis")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print()
        print("💡 Try running manual workflow instead:")
        print("  python main.py --mode billing")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error running agent workflow: {e}")
        print()
        print("💡 Try running manual workflow instead:")
        print("  python main.py --mode billing")
        sys.exit(1)

if __name__ == "__main__":
    main()