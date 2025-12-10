# File: day2/ex4_dataset_evolution.py
"""
Exercise 2.4: Dataset Evolution Strategy
Plan how datasets stay relevant over time
"""

import json
from datetime import datetime
from collections import Counter

class DatasetEvolutionPlanner:
    """
    Plans and tracks dataset evolution over time
    """
    
    def __init__(self, dataset_path: str):
        with open(dataset_path, 'r') as f:
            data = json.load(f)
        self.test_cases = data.get("goldens", [])
        self.evolution_log = []
    
    def analyze_production_failures(self, production_logs: list):
        """
        Analyze production failures to identify new test cases needed
        
        In real production, you'd pull from:
        - User complaint tickets
        - Low satisfaction ratings
        - Error logs
        - Support escalations
        """
        print("\n" + "="*60)
        print("PRODUCTION FAILURE ANALYSIS")
        print("="*60)
        
        failure_patterns = Counter()
        new_test_cases = []
        
        for log in production_logs:
            user_input = log.get("input", "")
            failure_reason = log.get("failure_reason", "unknown")
            
            failure_patterns[failure_reason] += 1
            
            # Check if this scenario is already in test dataset
            already_tested = any(
                tc.get("input", "").lower() == user_input.lower() 
                for tc in self.test_cases
            )
            
            if not already_tested:
                new_test_cases.append({
                    "input": user_input,
                    "expected_output": log.get("expected_behavior", ""),
                    "metadata": {
                        "source": "production_failure",
                        "failure_reason": failure_reason,
                        "date_added": datetime.now().isoformat()
                    }
                })
        
        print(f"\nAnalyzed {len(production_logs)} production failures")
        print(f"Found {len(new_test_cases)} new scenarios to add to tests")
        
        print("\nTop failure patterns:")
        for pattern, count in failure_patterns.most_common(5):
            print(f"  {pattern}: {count} occurrences")
        
        return new_test_cases
    
    def identify_coverage_gaps(self, product_features: list):
        """
        Compare test coverage against actual product features
        """
        print("\n" + "="*60)
        print("COVERAGE GAP ANALYSIS")
        print("="*60)
        
        # Get what we're currently testing
        tested_categories = set()
        for tc in self.test_cases:
            cat = tc.get("metadata", {}).get("category", "unknown")
            tested_categories.add(cat)
        
        # Compare to what we should be testing
        missing_coverage = []
        for feature in product_features:
            if feature not in tested_categories:
                missing_coverage.append(feature)
        
        print(f"\nProduct features: {len(product_features)}")
        print(f"Features with test coverage: {len(tested_categories)}")
        print(f"Features WITHOUT coverage: {len(missing_coverage)}")
        
        if missing_coverage:
            print("\n⚠️  MISSING COVERAGE:")
            for feature in missing_coverage:
                print(f"  - {feature}")
        else:
            print("\n✓ All features have test coverage")
        
        return missing_coverage
    
    def recommend_retirement(self, days_since_last_failure: int = 180):
        """
        Identify old test cases that might be obsolete
        
        Tests that haven't caught issues in 6+ months might be:
        - Testing deprecated features
        - Redundant with other tests
        - No longer relevant
        """
        print("\n" + "="*60)
        print("TEST RETIREMENT CANDIDATES")
        print("="*60)
        
        # In real system, you'd track last_failure_date for each test
        # Here we'll simulate
        
        retirement_candidates = []
        
        for i, tc in enumerate(self.test_cases):
            metadata = tc.get("metadata", {})
            category = metadata.get("category", "unknown")
            
            # Simulate: if category is very specific/niche, consider retiring
            if category in ["legacy_features", "deprecated", "old_api"]:
                retirement_candidates.append({
                    "test_case": tc.get("input", "")[:60],
                    "reason": "Tests deprecated feature",
                    "category": category
                })
        
        print(f"\nFound {len(retirement_candidates)} candidates for retirement")
        
        if retirement_candidates:
            print("\nCandidates (sample):")
            for candidate in retirement_candidates[:5]:
                print(f"  - {candidate['test_case']}")
                print(f"    Reason: {candidate['reason']}")
        
        return retirement_candidates
    
    def calculate_dataset_staleness(self):
        """
        Measure how stale the dataset is
        """
        print("\n" + "="*60)
        print("DATASET STALENESS CHECK")
        print("="*60)
        
        # Check when cases were last updated
        dates = []
        for tc in self.test_cases:
            date_added = tc.get("metadata", {}).get("date_added")
            if date_added:
                dates.append(date_added)
        
        if not dates:
            print("\n⚠️  No date metadata - cannot calculate staleness")
            print("Recommendation: Add 'date_added' to all test cases")
            return None
        
        # In real system, calculate days since last update
        print(f"\nDataset age indicators:")
        print(f"  Total test cases: {len(self.test_cases)}")
        print(f"  Cases with date metadata: {len(dates)}")
        
        # Simulate staleness score
        staleness_score = 75  # Arbitrary for demonstration
        
        print(f"\n📊 Staleness Score: {staleness_score}/100")
        
        if staleness_score < 50:
            print("✓ Dataset is fresh and up-to-date")
        elif staleness_score < 75:
            print("⚠️  Dataset showing age - consider review")
        else:
            print("❌ Dataset is stale - needs significant update")
        
        return staleness_score
    
    def create_evolution_plan(self, 
                            new_cases: list, 
                            missing_coverage: list, 
                            retirement_candidates: list):
        """
        Generate actionable evolution plan
        """
        print("\n" + "="*60)
        print("DATASET EVOLUTION PLAN")
        print("="*60)
        
        plan = {
            "add": len(new_cases),
            "retire": len(retirement_candidates),
            "expand_coverage": len(missing_coverage),
            "actions": []
        }
        
        # Action 1: Add production failures
        if new_cases:
            plan["actions"].append({
                "action": "Add production failure cases",
                "count": len(new_cases),
                "priority": "HIGH",
                "timeline": "This sprint"
            })
        
        # Action 2: Expand coverage
        if missing_coverage:
            plan["actions"].append({
                "action": f"Create tests for: {', '.join(missing_coverage[:3])}",
                "count": len(missing_coverage),
                "priority": "MEDIUM",
                "timeline": "Next 2 sprints"
            })
        
        # Action 3: Retire obsolete
        if retirement_candidates:
            plan["actions"].append({
                "action": "Archive deprecated feature tests",
                "count": len(retirement_candidates),
                "priority": "LOW",
                "timeline": "Next quarter"
            })
        
        # Action 4: Regular maintenance
        plan["actions"].append({
            "action": "Quarterly dataset review",
            "priority": "ONGOING",
            "timeline": "Every 3 months"
        })
        
        print("\n📋 ACTION PLAN:")
        for i, action in enumerate(plan["actions"], 1):
            print(f"\n{i}. {action['action']}")
            if "count" in action:
                print(f"   Items: {action['count']}")
            print(f"   Priority: {action['priority']}")
            print(f"   Timeline: {action['timeline']}")
        
        return plan


# ========== EXAMPLE USAGE ==========

if __name__ == "__main__":
    print("DATASET EVOLUTION PLANNER")
    print("="*60)
    
    # Initialize with your dataset
    planner = DatasetEvolutionPlanner("day2_synthetic_cases.json")
    
    # Simulate production failures
    production_failures = [
        {
            "input": "Can I get refund if package was stolen?",
            "failure_reason": "edge_case_not_covered",
            "expected_behavior": "Explain filing claim process with carrier"
        },
        {
            "input": "Refund for international orders?",
            "failure_reason": "international_policy_unclear",
            "expected_behavior": "Different policy for international - 45 days"
        },
        {
            "input": "Can I exchange instead of refund?",
            "failure_reason": "exchange_not_documented",
            "expected_behavior": "Yes, exchanges available within 30 days"
        }
    ]
    
    new_cases = planner.analyze_production_failures(production_failures)
    
    # Check coverage vs actual features
    product_features = [
        "customer_support",
        "technical_docs",
        "product_recommendations",
        "billing_issues",  # Not covered!
        "subscription_management"  # Not covered!
    ]
    
    missing = planner.identify_coverage_gaps(product_features)
    
    # Identify retirement candidates
    retirement = planner.recommend_retirement()

    
    # Check staleness
    staleness = planner.calculate_dataset_staleness()
    
    # Generate evolution plan
    plan = planner.create_evolution_plan(new_cases, missing, retirement)
    
    print("\n" + "="*60)
    print("✓ Evolution planning complete!")
    print("="*60)
