# File: day2/ex3_dataset_analysis.py
"""
Exercise 2.3: Dataset Quality Analysis
Analyze datasets to find coverage gaps and quality issues
"""

import json
from collections import Counter

class DatasetAnalyzer:
    """
    Analyzes test datasets for quality issues
    """
    
    def __init__(self, dataset_path: str):
        """Load dataset from JSON file"""
        with open(dataset_path, 'r') as f:
            data = json.load(f)
        self.test_cases = data.get("goldens", [])
        
    def analyze_coverage(self):
        """
        Check if dataset covers diverse topics
        Returns gaps in coverage
        """
        print("\n" + "="*60)
        print("COVERAGE ANALYSIS")
        print("="*60)
        
        # Count by subcategory
        subcategories = [tc.get("metadata", {}).get("subcategory", "unknown") 
                        for tc in self.test_cases]
        subcat_counts = Counter(subcategories)
        
        print(f"\nTotal test cases: {len(self.test_cases)}")
        print(f"\nUnique topics covered: {len(subcat_counts)}")
        
        print("\nBreakdown by topic:")
        for topic, count in subcat_counts.most_common():
            percentage = (count / len(self.test_cases)) * 100
            bar = "█" * int(percentage / 2)  # Visual bar
            print(f"  {topic:.<30} {count:>3} ({percentage:>5.1f}%) {bar}")
        
        # Identify gaps (topics with < 5% coverage)
        gaps = [topic for topic, count in subcat_counts.items() 
                if (count / len(self.test_cases)) < 0.05]
        
        if gaps:
            print(f"\n⚠️  COVERAGE GAPS (< 5% of dataset):")
            for gap in gaps:
                print(f"  - {gap}")
        else:
            print("\n✓ Good coverage - no major gaps")
        
        return subcat_counts
    
    def analyze_difficulty_distribution(self):
        """
        Check if difficulty is balanced
        Target: 60% easy, 30% medium, 10% hard
        """
        print("\n" + "="*60)
        print("DIFFICULTY DISTRIBUTION")
        print("="*60)
        
        difficulties = [tc.get("metadata", {}).get("difficulty", "unknown") 
                       for tc in self.test_cases]
        diff_counts = Counter(difficulties)
        
        total = len(self.test_cases)
        
        print(f"\nActual distribution:")
        for diff in ["easy", "medium", "hard"]:
            count = diff_counts.get(diff, 0)
            percentage = (count / total) * 100
            bar = "█" * int(percentage / 2)
            print(f"  {diff:.<10} {count:>3} ({percentage:>5.1f}%) {bar}")
        
        # Compare to target
        targets = {"easy": 60, "medium": 30, "hard": 10}
        print(f"\nTarget distribution:")
        for diff, target in targets.items():
            print(f"  {diff:.<10} {target}%")
        
        # Check if distribution is acceptable
        easy_pct = (diff_counts.get("easy", 0) / total) * 100
        medium_pct = (diff_counts.get("medium", 0) / total) * 100
        hard_pct = (diff_counts.get("hard", 0) / total) * 100
        
        issues = []
        if easy_pct < 50:
            issues.append("⚠️  Too few easy cases (should be ~60%)")
        if easy_pct > 70:
            issues.append("⚠️  Too many easy cases (should be ~60%)")
        if medium_pct < 20:
            issues.append("⚠️  Too few medium cases (should be ~30%)")
        if hard_pct < 5:
            issues.append("⚠️  Too few hard cases (should be ~10%)")
        
        if issues:
            print("\n⚠️  DISTRIBUTION ISSUES:")
            for issue in issues:
                print(f"  {issue}")
        else:
            print("\n✓ Good difficulty balance")
        
        return diff_counts
    
    def analyze_output_quality(self):
        """
        Check for quality issues in expected outputs
        """
        print("\n" + "="*60)
        print("OUTPUT QUALITY CHECK")
        print("="*60)
        
        issues = []
        
        for i, tc in enumerate(self.test_cases):
            expected = tc.get("expected_output", "")
            
            # Check for vague outputs
            if len(expected) < 20:
                issues.append({
                    "case": i + 1,
                    "type": "Too vague",
                    "input": tc.get("input", "")[:50] + "...",
                    "output": expected
                })
            
            # Check for missing outputs
            if not expected or expected.strip() == "":
                issues.append({
                    "case": i + 1,
                    "type": "Missing output",
                    "input": tc.get("input", "")[:50] + "...",
                    "output": "(empty)"
                })
            
            # Check for overly long outputs (might be too specific)
            if len(expected) > 500:
                issues.append({
                    "case": i + 1,
                    "type": "Too verbose",
                    "input": tc.get("input", "")[:50] + "...",
                    "output": expected[:100] + "..."
                })
        
        print(f"\nChecked {len(self.test_cases)} test cases")
        print(f"Found {len(issues)} quality issues")
        
        if issues:
            print("\n⚠️  QUALITY ISSUES:")
            for issue in issues[:10]:  # Show first 10
                print(f"\n  Case #{issue['case']} - {issue['type']}")
                print(f"    Input: {issue['input']}")
                print(f"    Output: {issue['output']}")
            
            if len(issues) > 10:
                print(f"\n  ... and {len(issues) - 10} more issues")
        else:
            print("\n✓ No obvious quality issues found")
        
        return issues
    
    def check_duplicates(self):
        """
        Find duplicate or very similar test cases
        """
        print("\n" + "="*60)
        print("DUPLICATE CHECK")
        print("="*60)
        
        inputs = [tc.get("input", "").lower().strip() for tc in self.test_cases]
        input_counts = Counter(inputs)
        
        duplicates = [(inp, count) for inp, count in input_counts.items() if count > 1]
        
        if duplicates:
            print(f"\n⚠️  Found {len(duplicates)} duplicate inputs:")
            for inp, count in duplicates[:5]:  # Show first 5
                print(f"  '{inp[:60]}...' appears {count} times")
        else:
            print("\n✓ No exact duplicates found")
        
        return duplicates
    
    def generate_report(self):
        """
        Generate comprehensive quality report
        """
        print("\n" + "="*60)
        print("DATASET QUALITY REPORT")
        print("="*60)
        
        coverage = self.analyze_coverage()
        difficulty = self.analyze_difficulty_distribution()
        quality = self.analyze_output_quality()
        duplicates = self.check_duplicates()
        
        # Overall score
        print("\n" + "="*60)
        print("OVERALL ASSESSMENT")
        print("="*60)
        
        score = 100
        recommendations = []
        
        # Coverage scoring
        if len(coverage) < 3:
            score -= 20
            recommendations.append("Add more diverse topics")
        
        # Difficulty scoring
        total = len(self.test_cases)
        easy_pct = (difficulty.get("easy", 0) / total) * 100
        if easy_pct < 50 or easy_pct > 70:
            score -= 15
            recommendations.append("Rebalance difficulty distribution")
        
        # Quality scoring
        if len(quality) > len(self.test_cases) * 0.1:  # > 10% have issues
            score -= 25
            recommendations.append("Improve expected output quality")
        
        # Duplicate scoring
        if duplicates:
            score -= 10
            recommendations.append("Remove duplicate test cases")
        
        print(f"\n📊 Quality Score: {score}/100")
        
        if score >= 80:
            print("✓ Excellent dataset quality")
        elif score >= 60:
            print("⚠️  Good dataset, but room for improvement")
        else:
            print("❌ Dataset needs significant improvement")
        
        if recommendations:
            print("\n📋 Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        
        return score


# ========== ANALYZE YOUR DATASETS ==========

if __name__ == "__main__":
    print("DATASET QUALITY ANALYZER")
    print("="*60)
    
    # Analyze the synthetic dataset you created
    print("\n🔍 Analyzing: day2_synthetic_cases.json")
    analyzer = DatasetAnalyzer("day2_synthetic_cases.json")
    score = analyzer.generate_report()
    
    print("\n" + "="*60)
    print(f"Analysis complete! Dataset quality score: {score}/100")
    print("="*60)

print("\n\n🔍 Analyzing: day2_cases.json (your manual dataset)")
