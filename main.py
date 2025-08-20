#!/usr/bin/env python3
"""
Main entry point for Asset Management System
Integrated billing analysis with agent-to-agent automation
"""

import os
import sys
import argparse
from pathlib import Path

# Add agents directory to path
sys.path.append(str(Path(__file__).parent / "agents"))

from billing_analyzer import BillingAnalyzer
from agents.billing_agent import BillingAgent

def run_billing_analysis():
    """Run complete billing analysis workflow."""
    print("🚀 Starting Asset Management Analysis")
    print("=" * 50)
    
    # Initialize billing agent
    agent = BillingAgent()
    
    # Process monthly billing
    result = agent.process_monthly_billing()
    
    if "error" in result:
        print(f"❌ Analysis failed: {result['error']}")
        return False
    
    print("\n✅ Analysis completed successfully!")
    
    # Check for unknown categories
    if os.path.exists(agent.unknown_categories_file):
        import json
        with open(agent.unknown_categories_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        unreviewed = sum(1 for info in data.values() if not info.get("human_reviewed", False))
        if unreviewed > 0:
            print(f"\n⚠️  {unreviewed} merchants need categorization")
            print("Run 'python review_interface.py' to categorize them")
    
    return True

def run_legacy_analysis():
    """Run legacy card.py analysis for comparison."""
    print("🔄 Running legacy analysis...")
    
    try:
        # Import and run legacy analysis
        import card
        print("Legacy analysis completed")
        return True
    except Exception as e:
        print(f"Legacy analysis failed: {e}")
        return False

def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="Asset Management System")
    parser.add_argument("--mode", choices=["billing", "legacy", "both"], 
                       default="billing", help="Analysis mode")
    parser.add_argument("--review", action="store_true", 
                       help="Start merchant review interface")
    
    args = parser.parse_args()
    
    if args.review:
        from review_interface import ReviewInterface
        interface = ReviewInterface()
        interface.start_review()
        return
    
    success = True
    
    if args.mode in ["billing", "both"]:
        success &= run_billing_analysis()
    
    if args.mode in ["legacy", "both"]:
        success &= run_legacy_analysis()
    
    if success:
        print("\n🎉 All analyses completed successfully!")
        print("\nGenerated files:")
        print("  📊 billing_analysis.png - Comprehensive visualizations")
        print("  📄 billing_report_*.json - Detailed analysis report")
        if os.path.exists("expense_analysis.png"):
            print("  📊 expense_analysis.png - Legacy analysis")
    else:
        print("\n❌ Some analyses failed. Check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()