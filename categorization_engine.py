"""
Advanced Merchant Categorization Engine
Sophisticated preprocessing and categorization with LLM assistance and learning
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from openai import OpenAI

@dataclass
class CategoryRule:
    """Represents a categorization rule."""
    pattern: str
    category: str
    confidence: float
    rule_type: str  # 'exact', 'contains', 'regex', 'llm'
    created_by: str  # 'system', 'human', 'llm'
    created_at: datetime
    usage_count: int = 0

class CategorizationEngine:
    """Advanced categorization engine with learning capabilities."""
    
    def __init__(self, api_key=None):
        self.client = OpenAI(
            base_url="https://api.sambanova.ai/v1", 
            api_key=api_key or os.environ.get("SAMBANOVA_API_KEY")
        ) if api_key or os.environ.get("SAMBANOVA_API_KEY") else None
        
        self.categories = {
            "Shopping": ["amazon", "楽天", "アマゾン", "ショッピング", "store", "shop"],
            "Utilities": ["ガス", "電気", "水道", "electric", "gas", "water", "utility"],
            "Transportation": ["タクシー", "go", "電車", "バス", "交通", "taxi", "train", "uber"],
            "Food & Dining": ["レストラン", "食事", "restaurant", "cafe", "food", "dining"],
            "Entertainment": ["netflix", "spotify", "映画", "entertainment", "movie", "music"],
            "Digital Services": ["apple", "google", "microsoft", "digital", "software", "app"],
            "Healthcare": ["病院", "薬", "hospital", "pharmacy", "medical", "health"],
            "Education": ["学校", "教育", "school", "education", "university", "course"],
            "Clothing": ["uniqlo", "ユニクロ", "服", "clothing", "fashion", "apparel"],
            "Financial": ["銀行", "金融", "bank", "finance", "credit", "loan"],
            "Other": []
        }
        
        self.rules_file = "categorization_rules.json"
        self.learning_data_file = "categorization_learning.json"
        self.rules = self._load_rules()
        
    def _load_rules(self) -> List[CategoryRule]:
        """Load categorization rules from file."""
        if not os.path.exists(self.rules_file):
            return self._initialize_default_rules()
        
        try:
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            rules = []
            for rule_data in data:
                rules.append(CategoryRule(
                    pattern=rule_data["pattern"],
                    category=rule_data["category"],
                    confidence=rule_data["confidence"],
                    rule_type=rule_data["rule_type"],
                    created_by=rule_data["created_by"],
                    created_at=datetime.fromisoformat(rule_data["created_at"]),
                    usage_count=rule_data.get("usage_count", 0)
                ))
            
            return rules
            
        except Exception as e:
            print(f"Error loading rules: {e}")
            return self._initialize_default_rules()
    
    def _initialize_default_rules(self) -> List[CategoryRule]:
        """Initialize default categorization rules."""
        rules = []
        now = datetime.now()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                rules.append(CategoryRule(
                    pattern=keyword.lower(),
                    category=category,
                    confidence=0.8,
                    rule_type="contains",
                    created_by="system",
                    created_at=now
                ))
        
        # Add specific high-confidence rules
        high_confidence_rules = [
            ("amazon", "Shopping", 0.95),
            ("アマゾン", "Shopping", 0.95),
            ("東京ガス", "Utilities", 0.99),
            ("go(タクシー", "Transportation", 0.95),
            ("apple com", "Digital Services", 0.90),
            ("ユニクロ", "Clothing", 0.95),
            ("netflix", "Entertainment", 0.95)
        ]
        
        for pattern, category, confidence in high_confidence_rules:
            rules.append(CategoryRule(
                pattern=pattern.lower(),
                category=category,
                confidence=confidence,
                rule_type="contains",
                created_by="system",
                created_at=now
            ))
        
        self._save_rules(rules)
        return rules
    
    def _save_rules(self, rules: List[CategoryRule]):
        """Save rules to file."""
        data = []
        for rule in rules:
            data.append({
                "pattern": rule.pattern,
                "category": rule.category,
                "confidence": rule.confidence,
                "rule_type": rule.rule_type,
                "created_by": rule.created_by,
                "created_at": rule.created_at.isoformat(),
                "usage_count": rule.usage_count
            })
        
        with open(self.rules_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def categorize_merchant(self, merchant: str) -> Tuple[str, float, str]:
        """
        Categorize a merchant using rules and return category, confidence, and method.
        
        Returns:
            Tuple of (category, confidence, method_used)
        """
        if not merchant or isinstance(merchant, float):
            return "Unknown", 0.0, "invalid_input"
        
        merchant_clean = self._clean_merchant_name(merchant)
        
        # Try rule-based categorization first
        best_match = self._apply_rules(merchant_clean)
        if best_match[1] > 0.7:  # High confidence threshold
            return best_match
        
        # If no high-confidence rule match, try LLM
        if self.client:
            llm_result = self._categorize_with_llm(merchant)
            if llm_result[1] > best_match[1]:
                # Learn from LLM result
                self._learn_from_categorization(merchant_clean, llm_result[0], "llm")
                return llm_result
        
        # Return best rule match or unknown
        return best_match if best_match[1] > 0 else ("Unknown", 0.0, "no_match")
    
    def _clean_merchant_name(self, merchant: str) -> str:
        """Clean and normalize merchant name."""
        # Remove common prefixes/suffixes
        cleaned = re.sub(r'^(株式会社|有限会社|合同会社)', '', merchant)
        cleaned = re.sub(r'(株式会社|有限会社|合同会社)$', '', cleaned)
        
        # Remove special characters and normalize
        cleaned = re.sub(r'[・＊※]', '', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def _apply_rules(self, merchant: str) -> Tuple[str, float, str]:
        """Apply categorization rules to merchant."""
        best_category = "Unknown"
        best_confidence = 0.0
        best_method = "no_match"
        
        merchant_lower = merchant.lower()
        
        for rule in self.rules:
            match = False
            
            if rule.rule_type == "exact":
                match = merchant_lower == rule.pattern.lower()
            elif rule.rule_type == "contains":
                match = rule.pattern.lower() in merchant_lower
            elif rule.rule_type == "regex":
                try:
                    match = bool(re.search(rule.pattern, merchant_lower, re.IGNORECASE))
                except re.error:
                    continue
            
            if match and rule.confidence > best_confidence:
                best_category = rule.category
                best_confidence = rule.confidence
                best_method = f"rule_{rule.rule_type}"
                rule.usage_count += 1
        
        return best_category, best_confidence, best_method
    
    def _categorize_with_llm(self, merchant: str) -> Tuple[str, float, str]:
        """Use LLM to categorize merchant."""
        try:
            categories_list = list(self.categories.keys())
            categories_str = ", ".join(categories_list)
            
            prompt = [
                {
                    "role": "system",
                    "content": f"""You are an expert at categorizing Japanese merchants and businesses. 
                    
Categories available: {categories_str}

Rules:
1. Return only the category name (exact match from the list)
2. If uncertain, use "Other"
3. Consider Japanese and English business names
4. Focus on the primary business type"""
                },
                {
                    "role": "user", 
                    "content": f"Categorize this merchant: {merchant}"
                }
            ]
            
            response = self.client.chat.completions.create(
                model="DeepSeek-R1-0528",
                messages=prompt,
                max_tokens=50,
                temperature=0.1
            )
            
            suggested_category = response.choices[0].message.content.strip()
            
            # Validate category
            if suggested_category in self.categories:
                confidence = 0.75  # Default LLM confidence
                return suggested_category, confidence, "llm"
            else:
                # Try to find closest match
                for category in self.categories:
                    if category.lower() in suggested_category.lower():
                        return category, 0.7, "llm_fuzzy"
                
                return "Other", 0.6, "llm_fallback"
            
        except Exception as e:
            print(f"LLM categorization failed for '{merchant}': {e}")
            return "Unknown", 0.0, "llm_error"
    
    def _learn_from_categorization(self, merchant: str, category: str, source: str):
        """Learn from successful categorizations to improve future results."""
        # Create a new rule from successful categorization
        if category != "Unknown" and category != "Other":
            # Extract keywords from merchant name
            keywords = self._extract_keywords(merchant)
            
            for keyword in keywords:
                if len(keyword) >= 3:  # Only meaningful keywords
                    new_rule = CategoryRule(
                        pattern=keyword.lower(),
                        category=category,
                        confidence=0.6,  # Start with moderate confidence
                        rule_type="contains",
                        created_by=source,
                        created_at=datetime.now()
                    )
                    
                    # Add if not already exists
                    existing = any(
                        r.pattern == new_rule.pattern and r.category == new_rule.category
                        for r in self.rules
                    )
                    
                    if not existing:
                        self.rules.append(new_rule)
        
        self._save_learning_data(merchant, category, source)
    
    def _extract_keywords(self, merchant: str) -> List[str]:
        """Extract meaningful keywords from merchant name."""
        # Remove common words and extract keywords
        common_words = {'app', 'com', 'co', 'ltd', 'inc', 'corp', 'the', 'and', 'or'}
        
        # Split by various delimiters
        words = re.split(r'[・\s\-_\(\)（）\*＊]+', merchant)
        
        keywords = []
        for word in words:
            word = word.strip()
            if len(word) >= 3 and word.lower() not in common_words:
                keywords.append(word)
        
        return keywords
    
    def _save_learning_data(self, merchant: str, category: str, source: str):
        """Save learning data for analysis and improvement."""
        learning_entry = {
            "merchant": merchant,
            "category": category,
            "source": source,
            "timestamp": datetime.now().isoformat()
        }
        
        # Load existing learning data
        learning_data = []
        if os.path.exists(self.learning_data_file):
            try:
                with open(self.learning_data_file, 'r', encoding='utf-8') as f:
                    learning_data = json.load(f)
            except:
                learning_data = []
        
        learning_data.append(learning_entry)
        
        # Save updated learning data
        with open(self.learning_data_file, 'w', encoding='utf-8') as f:
            json.dump(learning_data, f, ensure_ascii=False, indent=2)
    
    def categorize_batch(self, merchants: List[str]) -> Dict[str, Tuple[str, float, str]]:
        """Categorize a batch of merchants efficiently."""
        results = {}
        
        # Group by similarity to optimize LLM calls
        for merchant in merchants:
            if merchant not in results:
                result = self.categorize_merchant(merchant)
                results[merchant] = result
        
        # Save updated rules after batch processing
        self._save_rules(self.rules)
        
        return results
    
    def get_categorization_stats(self) -> Dict[str, any]:
        """Get statistics about categorization performance."""
        total_rules = len(self.rules)
        by_source = {}
        by_category = {}
        usage_stats = {}
        
        for rule in self.rules:
            by_source[rule.created_by] = by_source.get(rule.created_by, 0) + 1
            by_category[rule.category] = by_category.get(rule.category, 0) + 1
            if rule.usage_count > 0:
                usage_stats[rule.pattern] = rule.usage_count
        
        return {
            "total_rules": total_rules,
            "rules_by_source": by_source,
            "rules_by_category": by_category,
            "most_used_rules": sorted(usage_stats.items(), key=lambda x: x[1], reverse=True)[:10],
            "learning_data_exists": os.path.exists(self.learning_data_file)
        }

if __name__ == "__main__":
    # Test the categorization engine
    engine = CategorizationEngine()
    
    test_merchants = [
        "ＡＭＡＺＯＮ．ＣＯ．ＪＰ",
        "ＧＯ（タクシーアプリ）＊アプリ配車",
        "東京ガス",
        "ユニクロ・ＧＵ・ＰＬＳＴオンライン",
        "ＡＰＰＬＥ　ＣＯＭ　ＢＩＬＬ",
        "Unknown Merchant 123"
    ]
    
    print("Testing categorization engine:")
    results = engine.categorize_batch(test_merchants)
    
    for merchant, (category, confidence, method) in results.items():
        print(f"  {merchant[:30]:30} -> {category:15} ({confidence:.2f}, {method})")
    
    print(f"\nStats: {engine.get_categorization_stats()}")