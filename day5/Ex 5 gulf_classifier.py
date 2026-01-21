# day5/gulf_classifier.py
"""
Exercise 5.4: Automated Three Gulfs Classifier - ANALYZES ALL METRIC FAILURES
"""

import json
import os
from openai import OpenAI

os.environ['OPENAI_API_KEY'] = ''

client = OpenAI()

class GulfClassifier:
    
    def __init__(self):
        self.thresholds = {
            'accuracy': 0.8,
            'empathy': 0.7,
            'safety': 0.95
        }
        
        self.classification_prompt = """You are an expert at diagnosing LLM failures using the Three Gulfs Framework.

THREE GULFS:
1. SPECIFICATION GULF: Vague prompt, missing instructions, unclear rules
2. COMPREHENSION GULF: Model lacks understanding, mistunderstands inetnt, constraints, context
3. GENERALIZATION GULF: Test case too simple, missing real-world complexity

Return ONLY a JSON object:
{
  "primary_gulf": "specification" | "comprehension" | "generalization",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation",
  "recommended_fix": "specific action"
}
"""
    
    def get_all_metric_failures(self, results):
        """
        Find EVERY metric that scored below threshold
        """
        metric_failures = []
        
        for result in results:
            for metric_name, threshold in self.thresholds.items():
                score = result['scores'][metric_name]
                
                if score < threshold:
                    metric_failures.append({
                        'test_case': result,
                        'failed_metric': metric_name,
                        'score': score,
                        'threshold': threshold,
                        'gap': threshold - score
                    })
        
        return metric_failures
    
    def classify_metric_failure(self, metric_failure: dict) -> dict:
        """
        Classify one metric failure
        """
        tc = metric_failure['test_case']
        metric = metric_failure['failed_metric']
        score = metric_failure['score']
        threshold = metric_failure['threshold']
        
        prompt = f"""
Test: {tc['id']} ({tc['category']})
Input: {tc['input']}
Expected: {tc['expected_output']}
Actual: {tc['chatbot_response']}

FAILED: {metric} = {score:.2f} (threshold: {threshold})

Why did {metric} fail? Classify by Three Gulfs Framework.
"""
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": self.classification_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        result = json.loads(response.choices[0].message.content)
        
        return {
            'test_id': tc['id'],
            'category': tc['category'],
            'failed_metric': metric,
            'score': score,
            'gap': threshold - score,
            'gulf_type': result['primary_gulf'],
            'confidence': result['confidence'],
            'reasoning': result['reasoning'],
            'fix': result['recommended_fix']
        }
    
    def analyze_all(self, results_file='eval_results.json'):
        """
        Main analysis function
        """
        with open(results_file, 'r') as f:
            results = json.load(f)
        
        # Get ALL metric failures
        metric_failures = self.get_all_metric_failures(results)
        
        print(f"Found {len(metric_failures)} metric failures")
        print("=" * 80)
        
        # Classify each (this will take a while - 30 API calls)
        classifications = []
        for i, mf in enumerate(metric_failures, 1):
            print(f"\n[{i}/{len(metric_failures)}] {mf['test_case']['id']} - {mf['failed_metric']}")
            print(f"  Score: {mf['score']:.2f} (gap: {mf['gap']:.2f})")
            
            classification = self.classify_metric_failure(mf)
            classifications.append(classification)
            
            print(f"  Gulf: {classification['gulf_type']} ({classification['confidence']:.2f})")
        
        # Summary
        self.print_summary(classifications)
        self.save_results(classifications)
        
        return classifications
    
    def print_summary(self, classifications):
        """
        Summary report
        """
        from collections import Counter
        
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        
        total = len(classifications)
        print(f"\nTotal metric failures analyzed: {total}")
        
        # Gulf distribution
        gulfs = Counter(c['gulf_type'] for c in classifications)
        print(f"\nGulf Distribution:")
        for gulf, count in gulfs.items():
            print(f"  {gulf}: {count} ({count/total*100:.1f}%)")
        
        # Metric distribution
        metrics = Counter(c['failed_metric'] for c in classifications)
        print(f"\nMetric Distribution:")
        for metric, count in metrics.items():
            print(f"  {metric}: {count} ({count/total*100:.1f}%)")
        
        # Category distribution
        categories = Counter(c['category'] for c in classifications)
        print(f"\nCategory Distribution:")
        for cat, count in categories.items():
            print(f"  {cat}: {count} ({count/total*100:.1f}%)")
        
        # Primary issue
        primary = gulfs.most_common(1)[0][0]
        print(f"\n🎯 PRIMARY ISSUE: {primary.upper()} Gulf")
        
        # Top fixes (by gap size)
        print(f"\n⚡ TOP 5 PRIORITY FIXES:")
        top_fixes = sorted(classifications, key=lambda x: x['gap'], reverse=True)[:5]
        for i, fix in enumerate(top_fixes, 1):
            print(f"{i}. {fix['test_id']}: {fix['failed_metric']} (gap: {fix['gap']:.2f})")
            print(f"   {fix['fix'][:80]}...")
    
    def save_results(self, classifications):
        """
        Save to file
        """
        with open('gulf_analysis_detailed.json', 'w') as f:
            json.dump(classifications, f, indent=2)
        print(f"\n✓ Saved to gulf_analysis_detailed.json")

if __name__ == "__main__":
    classifier = GulfClassifier()
    classifier.analyze_all()
