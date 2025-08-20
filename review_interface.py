#!/usr/bin/env python3
"""
Human Review Interface for Merchant Categorization
Interactive CLI for reviewing and categorizing unknown merchants
"""

import json
import os
from datetime import datetime
from agents.billing_agent import BillingAgent

class ReviewInterface:
    """Interactive interface for human review of merchant categories."""
    
    def __init__(self):
        self.agent = BillingAgent()
        self.categories = [
            "Shopping", "Utilities", "Transportation", "Food & Dining",
            "Entertainment", "Digital Services", "Healthcare", "Education",
            "Clothing", "Other"
        ]
    
    def start_review(self):
        """Start the interactive review process."""
        print("🔍 MERCHANT CATEGORY REVIEW")
        print("=" * 50)
        
        # Load unknown merchants
        if not os.path.exists(self.agent.unknown_categories_file):
            print("✅ No merchants requiring review found!")
            return
        
        # Load billing data to get transaction amounts
        from billing_analyzer import BillingAnalyzer
        analyzer = BillingAnalyzer()
        try:
            df = analyzer.read_billing_files()
            merchant_stats = df.groupby('Merchant')['Amount'].agg(['sum', 'count']).round(2)
        except:
            merchant_stats = {}
        
        with open(self.agent.unknown_categories_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Filter unreviewed merchants and add amount info
        unreviewed = {}
        for merchant, info in data.items():
            if not info.get("human_reviewed", False):
                # Get transaction info
                if merchant in merchant_stats.index:
                    total_amount = float(merchant_stats.loc[merchant, 'sum'])
                    transaction_count = int(merchant_stats.loc[merchant, 'count'])
                else:
                    total_amount = 0.0
                    transaction_count = 0
                
                unreviewed[merchant] = {
                    **info,
                    'total_amount': total_amount,
                    'transaction_count': transaction_count
                }
        
        if not unreviewed:
            print("✅ All merchants have been reviewed!")
            return
        
        # Sort by amount (highest first)
        unreviewed = dict(sorted(unreviewed.items(), key=lambda x: x[1]['total_amount'], reverse=True))
        
        print(f"Found {len(unreviewed)} merchants requiring categorization")
        print("(Sorted by transaction amount - highest first)\n")
        
        # Review each merchant
        for i, (merchant, info) in enumerate(unreviewed.items(), 1):
            self.review_merchant(merchant, info, i, len(unreviewed))
            
            # Update the data file
            data[merchant]["human_reviewed"] = True
            data[merchant]["date_reviewed"] = datetime.now().isoformat()
            
            with open(self.agent.unknown_categories_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
    
    def review_merchant(self, merchant, info, current, total):
        """Review a single merchant."""
        print(f"\n[{current}/{total}] Reviewing: {merchant}")
        print(f"Date added: {info.get('date_added', 'Unknown')[:19]}")
        
        # Show transaction amount information
        total_amount = info.get('total_amount', 0)
        transaction_count = info.get('transaction_count', 0)
        if total_amount > 0:
            print(f"💰 Total Amount: ¥{total_amount:,.0f} ({transaction_count} transactions)")
            avg_amount = total_amount / transaction_count if transaction_count > 0 else 0
            print(f"📊 Average per transaction: ¥{avg_amount:,.0f}")
        else:
            print("💰 Amount: No transaction data found")
        
        # Show available categories
        print("\nAvailable categories:")
        for i, cat in enumerate(self.categories, 1):
            print(f"  {i}. {cat}")
        
        while True:
            try:
                choice = input(f"\nSelect category (1-{len(self.categories)}) or 's' to skip: ").strip()
                
                if choice.lower() == 's':
                    print("⏭️  Skipped")
                    info["suggested_category"] = "Unknown"
                    break
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(self.categories):
                    category = self.categories[choice_num - 1]
                    info["suggested_category"] = category
                    print(f"✅ Categorized as: {category}")
                    break
                else:
                    print(f"Please enter 1-{len(self.categories)} or 's'")
                    
            except ValueError:
                print("Invalid input. Please enter a number or 's'")
            except KeyboardInterrupt:
                print("\n\n⏹️  Review cancelled")
                return
    
    def show_statistics(self):
        """Show categorization statistics."""
        if not os.path.exists(self.agent.unknown_categories_file):
            print("No categorization data found.")
            return
        
        with open(self.agent.unknown_categories_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        total = len(data)
        reviewed = sum(1 for info in data.values() if info.get("human_reviewed", False))
        pending = total - reviewed
        
        print(f"\n📊 CATEGORIZATION STATISTICS")
        print(f"{'='*40}")
        print(f"Total merchants: {total}")
        print(f"Reviewed: {reviewed}")
        print(f"Pending: {pending}")
        
        if reviewed > 0:
            print(f"\nCategory distribution:")
            categories = {}
            for info in data.values():
                if info.get("human_reviewed", False):
                    cat = info.get("suggested_category", "Unknown")
                    categories[cat] = categories.get(cat, 0) + 1
            
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                print(f"  {cat}: {count}")
    
    def export_categories(self, filename="merchant_categories.json"):
        """Export reviewed categories for use in billing analysis."""
        if not os.path.exists(self.agent.unknown_categories_file):
            print("No categorization data found.")
            return
        
        with open(self.agent.unknown_categories_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract only reviewed categories
        reviewed_categories = {
            merchant: info["suggested_category"]
            for merchant, info in data.items()
            if info.get("human_reviewed", False)
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(reviewed_categories, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Exported {len(reviewed_categories)} categories to {filename}")

def main():
    """Main CLI interface."""
    interface = ReviewInterface()
    
    while True:
        print("\n🏦 ASSET MANAGEMENT - MERCHANT REVIEW")
        print("=" * 50)
        print("1. Start merchant review")
        print("2. Show statistics") 
        print("3. Export categories")
        print("4. Exit")
        
        try:
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == "1":
                interface.start_review()
            elif choice == "2":
                interface.show_statistics()
            elif choice == "3":
                interface.export_categories()
            elif choice == "4":
                print("👋 Goodbye!")
                break
            else:
                print("Please select 1-4")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()