"""
Exercise 3.4: Composite Scoring Systems
Combine multiple metrics into actionable scorecards
"""

import openai
import json
from deepeval.test_case import LLMTestCase
from deepeval.metrics import BaseMetric

client = openai.OpenAI(api_key="")


# ============================================================================
# SIMPLE METRICS (for demo)
# ============================================================================

class SimpleAccuracyMetric(BaseMetric):
    def __init__(self, threshold=0.7):
        self.threshold = threshold
        self.score = 0
        self.reason = ""
    
    def measure(self, test_case: LLMTestCase):
        prompt = f"""Rate ACCURACY 0-10.
Input: {test_case.input}
Response: {test_case.actual_output}
Expected: {test_case.expected_output}

Return JSON: {{"score": <0-10>, "reason": "<brief>"}}"""
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        result = json.loads(response.choices[0].message.content.replace("```json", "").replace("```", "").strip())
        self.score = result["score"] / 10
        self.reason = result["reason"]
        return self.score
    
    def is_successful(self):
        return self.score >= self.threshold
    
    @property
    def __name__(self):
        return "Accuracy"


class SimpleEmpathyMetric(BaseMetric):
    def __init__(self, threshold=0.7):
        self.threshold = threshold
        self.score = 0
        self.reason = ""
    
    def measure(self, test_case: LLMTestCase):
        prompt = f"""Rate EMPATHY 0-10.
Input: {test_case.input}
Response: {test_case.actual_output}

Return JSON: {{"score": <0-10>, "reason": "<brief>"}}"""
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        result = json.loads(response.choices[0].message.content.replace("```json", "").replace("```", "").strip())
        self.score = result["score"] / 10
        self.reason = result["reason"]
        return self.score
    
    def is_successful(self):
        return self.score >= self.threshold
    
    @property
    def __name__(self):
        return "Empathy"


class SimpleClarityMetric(BaseMetric):
    def __init__(self, threshold=0.7):
        self.threshold = threshold
        self.score = 0
        self.reason = ""
    
    def measure(self, test_case: LLMTestCase):
        prompt = f"""Rate CLARITY 0-10.
Response: {test_case.actual_output}

Return JSON: {{"score": <0-10>, "reason": "<brief>"}}"""
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        result = json.loads(response.choices[0].message.content.replace("```json", "").replace("```", "").strip())
        self.score = result["score"] / 10
        self.reason = result["reason"]
        return self.score
    
    def is_successful(self):
        return self.score >= self.threshold
    
    @property
    def __name__(self):
        return "Clarity"


# ============================================================================
# COMPOSITE SCORING STRATEGIES
# ============================================================================

class WeightedCompositeScore:
    """
    Strategy 1: Weighted Average
    Combine metrics using importance weights
    """
    
    def __init__(self, metrics: dict):
        """
        metrics = {
            metric_instance: weight,
            accuracy_metric: 0.40,
            empathy_metric: 0.30,
            clarity_metric: 0.30
        }
        """
        self.metrics = metrics
        
        # Validate weights sum to 1.0
        total_weight = sum(metrics.values())
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total_weight}")
    
    def evaluate(self, test_case: LLMTestCase):
        """Run all metrics and compute weighted score"""
        
        results = {}
        weighted_score = 0
        
        for metric, weight in self.metrics.items():
            score = metric.measure(test_case)
            results[metric.__name__] = {
                "score": score,
                "weight": weight,
                "weighted": score * weight,
                "passed": metric.is_successful()
            }
            weighted_score += score * weight
        
        overall_pass = weighted_score >= 0.7  # Threshold
        
        return {
            "overall_score": weighted_score,
            "passed": overall_pass,
            "breakdown": results
        }


class ThresholdCompositeScore:
    """
    Strategy 2: All Must Pass Thresholds
    Every metric must exceed its threshold
    """
    
    def __init__(self, metrics: list):
        """
        metrics = [accuracy_metric, empathy_metric, clarity_metric]
        Each has its own threshold
        """
        self.metrics = metrics
    
    def evaluate(self, test_case: LLMTestCase):
        """Run all metrics and check if ALL pass"""
        
        results = {}
        all_passed = True
        
        for metric in self.metrics:
            score = metric.measure(test_case)
            passed = metric.is_successful()
            
            results[metric.__name__] = {
                "score": score,
                "threshold": metric.threshold,
                "passed": passed
            }
            
            if not passed:
                all_passed = False
        
        return {
            "all_passed": all_passed,
            "breakdown": results
        }


class HybridCompositeScore:
    """
    Strategy 3: Critical + Weighted
    Some metrics are critical (must pass), others are weighted
    """
    
    def __init__(self, critical_metrics: list, weighted_metrics: dict):
        """
        critical_metrics = [accuracy_metric]  ← MUST pass
        weighted_metrics = {empathy_metric: 0.6, clarity_metric: 0.4}  ← Weighted
        """
        self.critical_metrics = critical_metrics
        self.weighted_metrics = weighted_metrics
    
    def evaluate(self, test_case: LLMTestCase):
        """Check critical first, then weighted"""
        
        # Check critical metrics
        critical_results = {}
        critical_passed = True
        
        for metric in self.critical_metrics:
            score = metric.measure(test_case)
            passed = metric.is_successful()
            
            critical_results[metric.__name__] = {
                "score": score,
                "threshold": metric.threshold,
                "passed": passed,
                "critical": True
            }
            
            if not passed:
                critical_passed = False
        
        # If critical fails, immediately fail
        if not critical_passed:
            return {
                "passed": False,
                "reason": "Critical metric(s) failed",
                "critical": critical_results,
                "weighted": None
            }
        
        # Check weighted metrics
        weighted_results = {}
        weighted_score = 0
        
        for metric, weight in self.weighted_metrics.items():
            score = metric.measure(test_case)
            weighted_results[metric.__name__] = {
                "score": score,
                "weight": weight,
                "weighted": score * weight
            }
            weighted_score += score * weight
        
        return {
            "passed": weighted_score >= 0.7,
            "overall_score": weighted_score,
            "critical": critical_results,
            "weighted": weighted_results
        }


# ============================================================================
# TESTS
# ============================================================================

def test_weighted_strategy():
    """Test weighted average approach"""
    
    print("="*70)
    print("STRATEGY 1: Weighted Composite Score")
    print("="*70)
    
    # Setup metrics
    accuracy = SimpleAccuracyMetric(threshold=0.7)
    empathy = SimpleEmpathyMetric(threshold=0.7)
    clarity = SimpleClarityMetric(threshold=0.7)
    
    # Create weighted scorer (accuracy matters most)
    scorer = WeightedCompositeScore({
        accuracy: 0.50,  # 50% weight
        empathy: 0.30,   # 30% weight
        clarity: 0.20    # 20% weight
    })
    
    # Test case: High accuracy, low empathy
    test_case = LLMTestCase(
        input="My order is late!",
        actual_output="Order #12345 shipped on 10/5. Tracking: XYZ123. Arrives 10/12.",
        expected_output="Provide order status and tracking"
    )
    
    result = scorer.evaluate(test_case)
    
    print(f"\nTest: High Accuracy, Low Empathy")
    print(f"Overall Score: {result['overall_score']:.2f}")
    print(f"Passed: {'✓ YES' if result['passed'] else '✗ NO'}")
    print(f"\nBreakdown:")
    for metric_name, data in result['breakdown'].items():
        print(f"  {metric_name}: {data['score']:.2f} (weight: {data['weight']:.2f}) → {data['weighted']:.2f}")
    
    print(f"\n💡 Insight: Weighted average allows trade-offs between metrics")


def test_threshold_strategy():
    """Test all-must-pass approach"""
    
    print("\n\n" + "="*70)
    print("STRATEGY 2: Threshold-Based (All Must Pass)")
    print("="*70)
    
    # Setup metrics with different thresholds
    accuracy = SimpleAccuracyMetric(threshold=0.8)   # Strict
    empathy = SimpleEmpathyMetric(threshold=0.6)     # Lenient
    clarity = SimpleClarityMetric(threshold=0.7)     # Medium
    
    scorer = ThresholdCompositeScore([accuracy, empathy, clarity])
    
    # Test case
    test_case = LLMTestCase(
        input="How do I reset my password?",
        actual_output="Click 'Forgot Password' on the login page. You'll receive a reset email within 5 minutes.",
        expected_output="Password reset instructions"
    )
    
    result = scorer.evaluate(test_case)
    
    print(f"\nTest: Balanced Response")
    print(f"All Passed: {'✓ YES' if result['all_passed'] else '✗ NO'}")
    print(f"\nBreakdown:")
    for metric_name, data in result['breakdown'].items():
        status = '✓' if data['passed'] else '✗'
        print(f"  {status} {metric_name}: {data['score']:.2f} (threshold: {data['threshold']:.2f})")
    
    print(f"\n💡 Insight: Stricter - one failure means overall failure")


def test_hybrid_strategy():
    """Test critical + weighted approach"""
    
    print("\n\n" + "="*70)
    print("STRATEGY 3: Hybrid (Critical + Weighted)")
    print("="*70)
    
    # Critical: Accuracy must pass
    accuracy = SimpleAccuracyMetric(threshold=0.8)
    
    # Weighted: Empathy and clarity
    empathy = SimpleEmpathyMetric(threshold=0.6)
    clarity = SimpleClarityMetric(threshold=0.6)
    
    scorer = HybridCompositeScore(
        critical_metrics=[accuracy],
        weighted_metrics={empathy: 0.6, clarity: 0.4}
    )
    
    # Test 1: Passes critical
    test_case_1 = LLMTestCase(
        input="What's 2+2?",
        actual_output="The answer is 4.",
        expected_output="4"
    )
    
    result = scorer.evaluate(test_case_1)
    
    print(f"\n✓ Test 1: Passes Critical")
    print(f"Passed: {'✓ YES' if result['passed'] else '✗ NO'}")
    if result.get('overall_score'):
        print(f"Overall Score: {result['overall_score']:.2f}")
    print(f"\nCritical Metrics:")
    for name, data in result['critical'].items():
        print(f"  {'✓' if data['passed'] else '✗'} {name}: {data['score']:.2f}")
    if result['weighted']:
        print(f"\nWeighted Metrics:")
        for name, data in result['weighted'].items():
            print(f"  {name}: {data['score']:.2f} (weight: {data['weight']:.2f})")
    
    # Test 2: Fails critical
    test_case_2 = LLMTestCase(
        input="What's 2+2?",
        actual_output="I'm here to help! Let me think about that for you! The answer might be around 5 or so!",
        expected_output="4"
    )
    
    result = scorer.evaluate(test_case_2)
    
    print(f"\n✗ Test 2: Fails Critical")
    print(f"Passed: {'✓ YES' if result['passed'] else '✗ NO'}")
    print(f"Reason: {result['reason']}")
    print(f"\nCritical Metrics:")
    for name, data in result['critical'].items():
        print(f"  {'✓' if data['passed'] else '✗'} {name}: {data['score']:.2f}")
    
    print(f"\n💡 Insight: Critical failures immediately reject, regardless of other scores")


def compare_strategies():
    """Compare all 3 strategies on same test case"""
    
    print("\n\n" + "="*70)
    print("STRATEGY COMPARISON")
    print("="*70)
    
    # Same test case
    test_case = LLMTestCase(
        input="My package is damaged!",
        actual_output="Submit a damage claim with photos to claims@company.com. Reference order #12345.",
        expected_output="Damage claim process"
    )
    
    # Strategy 1: Weighted
    acc1 = SimpleAccuracyMetric(threshold=0.7)
    emp1 = SimpleEmpathyMetric(threshold=0.7)
    clar1 = SimpleClarityMetric(threshold=0.7)
    weighted = WeightedCompositeScore({acc1: 0.5, emp1: 0.3, clar1: 0.2})
    result1 = weighted.evaluate(test_case)
    
    # Strategy 2: Threshold
    acc2 = SimpleAccuracyMetric(threshold=0.7)
    emp2 = SimpleEmpathyMetric(threshold=0.7)
    clar2 = SimpleClarityMetric(threshold=0.7)
    threshold = ThresholdCompositeScore([acc2, emp2, clar2])
    result2 = threshold.evaluate(test_case)
    
    # Strategy 3: Hybrid
    acc3 = SimpleAccuracyMetric(threshold=0.8)
    emp3 = SimpleEmpathyMetric(threshold=0.6)
    clar3 = SimpleClarityMetric(threshold=0.6)
    hybrid = HybridCompositeScore(
        critical_metrics=[acc3],
        weighted_metrics={emp3: 0.6, clar3: 0.4}
    )
    result3 = hybrid.evaluate(test_case)
    
    print(f"\nSame response evaluated 3 ways:")
    print(f"\n1. Weighted: {'✓ PASS' if result1['passed'] else '✗ FAIL'} (score: {result1['overall_score']:.2f})")
    print(f"2. Threshold: {'✓ PASS' if result2['all_passed'] else '✗ FAIL'}")
    print(f"3. Hybrid: {'✓ PASS' if result3['passed'] else '✗ FAIL'}")
    
    print(f"\n💡 Different strategies = different decisions on same response!")


if __name__ == "__main__":
    test_weighted_strategy()
    test_threshold_strategy()
    test_hybrid_strategy()
    compare_strategies()
    
    print("\n" + "="*70)
    print("✓ Composite scoring complete!")
    print("="*70)
    
    print("\n" + "="*70)
    print("🎉 DAY 3 COMPLETE!")
    print("="*70)
    print("\nYou learned:")
    print("  ✓ Multi-dimensional scoring")
    print("  ✓ Metric calibration with humans")
    print("  ✓ Domain-specific metrics (RAG, Agents)")
    print("  ✓ Composite scoring strategies")
    print("\nReady for Day 4: Production Systems!")
    print("="*70)
