#!/usr/bin/env python3
"""
Enhanced Human Review Workflow for Merchant Categorization
Advanced interface with learning capabilities and batch operations
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from categorization_engine import CategorizationEngine

class EnhancedReviewWorkflow:
    """Enhanced workflow for human review with smart suggestions and learning."""
    
    def __init__(self):
        self.engine = CategorizationEngine()
        self.session_file = "review_session.json"
        self.current_session = self._load_session()
        
    def _load_session(self) -> Dict:
        """Load current review session data."""
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "started_at": datetime.now().isoformat(),
            "merchants_reviewed": 0,
            "decisions_made": [],
            "patterns_learned": [],
            "session_stats": {}
        }
    
    def _save_session(self):
        """Save current session data."""
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(self.current_session, f, ensure_ascii=False, indent=2)
    
    def start_enhanced_review(self):
        """Start the enhanced review process with smart suggestions."""
        print("🧠 ENHANCED MERCHANT CATEGORIZATION REVIEW")
        print("=" * 60)
        print("Features: Smart suggestions, batch operations, pattern learning")
        
        # Get merchants needing review
        merchants_to_review = self._get_merchants_for_review()
        
        if not merchants_to_review:
            print("✅ No merchants requiring review!")
            return
        
        # Group similar merchants
        grouped_merchants = self._group_similar_merchants(merchants_to_review)
        
        print(f"\nFound {len(merchants_to_review)} merchants in {len(grouped_merchants)} groups")
        print("Groups help you categorize similar merchants efficiently.")
        
        # Review by groups
        for group_idx, (pattern, merchants) in enumerate(grouped_merchants.items(), 1):
            self._review_merchant_group(group_idx, pattern, merchants, len(grouped_merchants))
        
        # Session summary
        self._show_session_summary()
        self._save_session()
    
    def _get_merchants_for_review(self) -> List[Tuple[str, str, float, str, float, int]]:
        """Get merchants that need human review with their categorization and transaction info."""
        from agents.billing_agent import BillingAgent
        from billing_analyzer import BillingAnalyzer
        
        agent = BillingAgent()
        
        if not os.path.exists(agent.unknown_categories_file):
            return []
        
        # Load billing data to get transaction amounts
        analyzer = BillingAnalyzer()
        try:
            df = analyzer.read_billing_files()
            merchant_stats = df.groupby('Merchant')['Amount'].agg(['sum', 'count']).round(2)
        except:
            merchant_stats = {}
        
        with open(agent.unknown_categories_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        merchants_to_review = []
        
        for merchant, info in data.items():
            if not info.get("human_reviewed", False):
                # Get current categorization attempt
                category, confidence, method = self.engine.categorize_merchant(merchant)
                
                # Get transaction info
                if merchant in merchant_stats.index:
                    total_amount = float(merchant_stats.loc[merchant, 'sum'])
                    transaction_count = int(merchant_stats.loc[merchant, 'count'])
                else:
                    total_amount = 0.0
                    transaction_count = 0
                
                merchants_to_review.append((merchant, category, confidence, method, total_amount, transaction_count))
        
        # Sort by total amount (highest first - these have most financial impact)
        merchants_to_review.sort(key=lambda x: x[4], reverse=True)
        
        return merchants_to_review
    
    def _group_similar_merchants(self, merchants: List[Tuple[str, str, float, str, float, int]]) -> Dict[str, List[Tuple[str, str, float, str, float, int]]]:
        """Group similar merchants for batch processing."""
        groups = {}
        
        for merchant_data in merchants:
            merchant = merchant_data[0]
            
            # Extract pattern (simplified)
            pattern = self._extract_pattern(merchant)
            
            if pattern not in groups:
                groups[pattern] = []
            groups[pattern].append(merchant_data)
        
        # Sort groups by total financial impact (sum of amounts in group)
        def group_total_amount(group_items):
            return sum(item[4] for item in group_items[1])  # Sum of amounts
        
        return dict(sorted(groups.items(), key=group_total_amount, reverse=True))
    
    def _extract_pattern(self, merchant: str) -> str:
        """Extract pattern from merchant name for grouping."""
        import re
        
        # Remove numbers and special characters for pattern
        pattern = re.sub(r'[0-9\-\*・．]', '', merchant)
        pattern = re.sub(r'\s+', ' ', pattern).strip()
        
        # Take first meaningful part
        parts = pattern.split()
        if parts:
            return parts[0][:10]  # First 10 chars of first meaningful word
        
        return "misc"
    
    def _review_merchant_group(self, group_idx: int, pattern: str, merchants: List[Tuple], total_groups: int):
        """Review a group of similar merchants."""
        total_amount = sum(m[4] for m in merchants)
        total_transactions = sum(m[5] for m in merchants)
        
        print(f"\n{'='*60}")
        print(f"GROUP {group_idx}/{total_groups}: {pattern}")
        print(f"{'='*60}")
        print(f"Contains {len(merchants)} merchants")
        print(f"Total Amount: ¥{total_amount:,.0f} ({total_transactions} transactions)")
        
        if len(merchants) > 1:
            print("\nBatch operations available:")
            print("  'a' - Apply same category to all in group")
            print("  'i' - Review individually")
            print("  's' - Skip entire group")
            print("  'p' - Preview all merchants in group")
            
            choice = input(f"\nChoose action (a/i/s/p): ").strip().lower()
            
            if choice == 'p':
                self._preview_group(merchants)
                choice = input(f"\nChoose action (a/i/s): ").strip().lower()
            
            if choice == 'a':
                self._batch_categorize_group(pattern, merchants)
                return
            elif choice == 's':
                print("⏭️  Skipped entire group")
                return
        
        # Review individually
        for i, merchant_data in enumerate(merchants, 1):
            print(f"\n[{i}/{len(merchants)}] in group '{pattern}':")
            self._review_single_merchant(merchant_data)
    
    def _preview_group(self, merchants: List[Tuple]):
        """Show preview of all merchants in group."""
        print(f"\nGroup preview ({len(merchants)} merchants):")
        for i, (merchant, category, confidence, method, amount, count) in enumerate(merchants, 1):
            status = "✓" if confidence > 0.7 else "?"
            print(f"  {i:2}. {status} {merchant[:40]:40} -> {category:12} ¥{amount:>8,.0f} ({count}tx) [{confidence:.2f}]")
    
    def _batch_categorize_group(self, pattern: str, merchants: List[Tuple]):
        """Apply same category to all merchants in group."""
        categories = list(self.engine.categories.keys())
        total_amount = sum(m[4] for m in merchants)
        
        print(f"\nBatch categorization for group '{pattern}' (¥{total_amount:,.0f} total):")
        self._show_categories(categories)
        
        while True:
            try:
                choice = input(f"\nSelect category (1-{len(categories)}) or 's' to skip: ").strip()
                
                if choice.lower() == 's':
                    print("⏭️  Skipped group")
                    return
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(categories):
                    category = categories[choice_num - 1]
                    
                    print(f"\nApplying '{category}' to {len(merchants)} merchants:")
                    
                    for merchant, _, _, _, amount, count in merchants:
                        self._save_categorization_decision(merchant, category, "batch_human")
                        print(f"  ✅ {merchant[:40]:40} -> {category:12} ¥{amount:>8,.0f} ({count}tx)")
                    
                    # Learn pattern
                    self._learn_pattern(pattern, category, len(merchants))
                    
                    self.current_session["merchants_reviewed"] += len(merchants)
                    break
                else:
                    print(f"Please enter 1-{len(categories)} or 's'")
                    
            except ValueError:
                print("Invalid input. Please enter a number or 's'")
            except KeyboardInterrupt:
                print("\n⏹️  Review cancelled")
                return
    
    def _review_single_merchant(self, merchant_data: Tuple[str, str, float, str, float, int]):
        """Review a single merchant with enhanced suggestions."""
        merchant, current_category, confidence, method, amount, count = merchant_data
        
        print(f"Merchant: {merchant}")
        print(f"Amount: ¥{amount:,.0f} ({count} transactions)")
        print(f"Current suggestion: {current_category} (confidence: {confidence:.2f}, method: {method})")
        
        # Show context if available
        self._show_merchant_context(merchant)
        
        # Show categories
        categories = list(self.engine.categories.keys())
        self._show_categories(categories)
        
        while True:
            try:
                choice = input(f"\nSelect category (1-{len(categories)}), 'a' to accept suggestion, or 's' to skip: ").strip()
                
                if choice.lower() == 'a' and current_category != 'Unknown':
                    chosen_category = current_category
                    print(f"✅ Accepted: {chosen_category}")
                    break
                elif choice.lower() == 's':
                    print("⏭️  Skipped")
                    return
                else:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(categories):
                        chosen_category = categories[choice_num - 1]
                        print(f"✅ Categorized as: {chosen_category}")
                        break
                    else:
                        print(f"Please enter 1-{len(categories)}, 'a', or 's'")
                        
            except ValueError:
                print("Invalid input. Please enter a number, 'a', or 's'")
            except KeyboardInterrupt:
                print("\n⏹️  Review cancelled")
                return
        
        # Save decision
        self._save_categorization_decision(merchant, chosen_category, "individual_human")
        self.current_session["merchants_reviewed"] += 1
    
    def _show_categories(self, categories: List[str]):
        """Show available categories in a nice format."""
        print("\nAvailable categories:")
        for i, cat in enumerate(categories, 1):
            print(f"  {i:2}. {cat}")
    
    def _show_merchant_context(self, merchant: str):
        """Show context about the merchant if available."""
        # Could be enhanced to show:
        # - Previous transactions
        # - Similar merchants already categorized
        # - Web search results
        pass
    
    def _save_categorization_decision(self, merchant: str, category: str, source: str):
        """Save categorization decision and update systems."""
        from agents.billing_agent import BillingAgent
        
        agent = BillingAgent()
        
        # Update unknown categories file
        if os.path.exists(agent.unknown_categories_file):
            with open(agent.unknown_categories_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {}
        
        data[merchant] = {
            "suggested_category": category,
            "human_reviewed": True,
            "date_reviewed": datetime.now().isoformat(),
            "review_source": source
        }
        
        with open(agent.unknown_categories_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Learn from decision
        self.engine._learn_from_categorization(merchant, category, source)
        
        # Track in session
        self.current_session["decisions_made"].append({
            "merchant": merchant,
            "category": category,
            "source": source,
            "timestamp": datetime.now().isoformat()
        })
    
    def _learn_pattern(self, pattern: str, category: str, count: int):
        """Learn from batch categorization pattern."""
        self.current_session["patterns_learned"].append({
            "pattern": pattern,
            "category": category,
            "merchant_count": count,
            "timestamp": datetime.now().isoformat()
        })
    
    def _show_session_summary(self):
        """Show summary of review session."""
        print(f"\n{'='*60}")
        print("SESSION SUMMARY")
        print(f"{'='*60}")
        
        reviewed = self.current_session["merchants_reviewed"]
        decisions = len(self.current_session["decisions_made"])
        patterns = len(self.current_session["patterns_learned"])
        
        print(f"Merchants reviewed: {reviewed}")
        print(f"Decisions made: {decisions}")
        print(f"Patterns learned: {patterns}")
        
        if decisions > 0:
            # Category breakdown
            categories = {}
            for decision in self.current_session["decisions_made"]:
                cat = decision["category"]
                categories[cat] = categories.get(cat, 0) + 1
            
            print(f"\nCategories assigned:")
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                print(f"  {cat}: {count}")
        
        print(f"\n✅ Session completed successfully!")

def main():
    """Main CLI interface for enhanced review."""
    workflow = EnhancedReviewWorkflow()
    
    while True:
        print("\n🧠 ENHANCED MERCHANT REVIEW WORKFLOW")
        print("=" * 50)
        print("1. Start enhanced review")
        print("2. Show categorization statistics") 
        print("3. Export learned patterns")
        print("4. Reset session")
        print("5. Exit")
        
        try:
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == "1":
                workflow.start_enhanced_review()
            elif choice == "2":
                stats = workflow.engine.get_categorization_stats()
                print(f"\nCategorization Statistics:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
            elif choice == "3":
                # Export learned patterns
                with open("learned_patterns.json", 'w', encoding='utf-8') as f:
                    json.dump(workflow.current_session, f, ensure_ascii=False, indent=2)
                print("✅ Patterns exported to learned_patterns.json")
            elif choice == "4":
                # Reset session
                if os.path.exists(workflow.session_file):
                    os.remove(workflow.session_file)
                workflow.current_session = workflow._load_session()
                print("✅ Session reset")
            elif choice == "5":
                print("👋 Goodbye!")
                break
            else:
                print("Please select 1-5")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()