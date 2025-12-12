"""
Exercise 3.2: Metric Calibration
Align LLM judge scores with human judgment
"""

import openai
import json
from deepeval.test_case import LLMTestCase
from deepeval.metrics import BaseMetric
import statistics

client = openai.OpenAI(api_key="")


class CalibratedEmpathyMetric(BaseMetric):
    """
    Empathy metric calibrated against human ratings
    """
    
    def __init__(self, threshold: float = 0.7, version: int = 1):
        self.threshold = threshold
        self.version = version  # Prompt version for A/B testing
        self.score = 0
        self.reason = ""
    
    def measure(self, test_case: LLMTestCase):
        """Evaluate empathy with calibrated prompt"""
        
        if self.version == 1:
            # V1: Basic prompt (uncalibrated)
            prompt = f"""Rate the EMPATHY of this response on 0-10 scale.

User: {test_case.input}
Response: {test_case.actual_output}

Score 0-10 and explain briefly.
Return JSON: {{"score": <0-10>, "reason": "<explanation>"}}"""
        
        elif self.version == 2:
            # V2: Calibrated prompt (with clear criteria)
            prompt = f"""Rate the EMPATHY of this response on 0-10 scale.

User: {test_case.input}
Response: {test_case.actual_output}

EMPATHY CRITERIA (use these exactly):
10: Acknowledges emotion + validates feelings + offers support + warm tone
8-9: Acknowledges emotion + warm tone + helpful
6-7: Polite and friendly but doesn't acknowledge emotion
4-5: Neutral/functional tone, no emotional connection
2-3: Cold or dismissive
0-1: Rude or harmful

Return JSON: {{"score": <0-10>, "reason": "<explanation>"}}"""
        
        else:
            # V3: Most calibrated (with examples)
            prompt = f"""Rate the EMPATHY of this response on 0-10 scale.

User: {test_case.input}
Response: {test_case.actual_output}

EXAMPLES:
- Score 10: "I completely understand how frustrating that must be. Let me help you right away."
- Score 5: "I can help with that. Here's what to do."
- Score 2: "Do this: [instructions]"

Return JSON: {{"score": <0-10>, "reason": "<explanation>"}}"""
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        
        result = response.choices[0].message.content
        result = result.replace("```json", "").replace("```", "").strip()
        
        try:
            parsed = json.loads(result)
            self.score = parsed["score"] / 10  # Normalize to 0-1
            self.reason = parsed["reason"]
        except:
            self.score = 0.5
            self.reason = "Parsing error"
        
        return self.score
    
    def is_successful(self):
        return self.score >= self.threshold
    
    @property
    def __name__(self):
        return f"Calibrated Empathy v{self.version}"


def calculate_correlation(llm_scores, human_scores):
    """Calculate Pearson correlation between LLM and human ratings"""
    n = len(llm_scores)
    
    # Mean
    llm_mean = sum(llm_scores) / n
    human_mean = sum(human_scores) / n
    
    # Correlation
    numerator = sum((llm_scores[i] - llm_mean) * (human_scores[i] - human_mean) for i in range(n))
    llm_variance = sum((x - llm_mean) ** 2 for x in llm_scores)
    human_variance = sum((x - human_mean) ** 2 for x in human_scores)
    
    denominator = (llm_variance * human_variance) ** 0.5
    
    if denominator == 0:
        return 0
    
    return numerator / denominator


def test_calibration():
    """Test different prompt versions against human ground truth"""
    
    print("="*70)
    print("METRIC CALIBRATION: Aligning LLM Judge with Human Ratings")
    print("="*70)
    
    # Test cases with HUMAN ratings (simulated ground truth)
    test_cases = [
        {
            "case": LLMTestCase(
                input="My package never arrived!",
                actual_output="I'm so sorry to hear your package didn't arrive. That must be incredibly frustrating, especially if you were counting on it. Let me investigate this right away and make it right for you.",
            ),
            "human_score": 0.95  # Very empathetic
        },
        {
            "case": LLMTestCase(
                input="How do I change my password?",
                actual_output="I'd be happy to help you change your password! It's a quick process. Just go to Settings > Security > Change Password. Let me know if you need any other assistance!",
            ),
            "human_score": 0.80  # Friendly and warm
        },
        {
            "case": LLMTestCase(
                input="My order is late",
                actual_output="I can help with that. Check your order status in your account dashboard.",
            ),
            "human_score": 0.40  # Functional but cold
        },
        {
            "case": LLMTestCase(
                input="I'm having trouble logging in",
                actual_output="Click 'Forgot Password'.",
            ),
            "human_score": 0.15  # Very cold
        },
        {
            "case": LLMTestCase(
                input="What's your return policy?",
                actual_output="You have 30 days to return items. No questions asked, full refund. We want you to be completely satisfied!",
            ),
            "human_score": 0.75  # Warm but not addressing emotion
        },
        {
            "case": LLMTestCase(
                input="I HATE YOUR COMPANY!",
                actual_output="I sincerely apologize for your experience. That's completely unacceptable, and I take full responsibility. Let me personally make this right.",
            ),
            "human_score": 0.98  # Warm but not addressing emotion
        },

        ]
    
    # Test 3 versions
    versions = [1, 2, 3]
    results = {}
    
    for version in versions:
        print(f"\n{'='*70}")
        print(f"Testing Prompt Version {version}")
        print('='*70)
        
        metric = CalibratedEmpathyMetric(version=version)
        llm_scores = []
        human_scores = []
        
        for i, item in enumerate(test_cases):
            score = metric.measure(item["case"])
            llm_scores.append(score)
            human_scores.append(item["human_score"])
            
            diff = abs(score - item["human_score"])
            print(f"\nCase {i+1}:")
            print(f"  Input: {item['case'].input[:50]}...")
            print(f"  Human score:  {item['human_score']:.2f}")
            print(f"  LLM score:    {score:.2f}")
            print(f"  Difference:   {diff:.2f} {'✓' if diff < 0.15 else '✗'}")
        
        # Calculate correlation
        correlation = calculate_correlation(llm_scores, human_scores)
        avg_diff = sum(abs(llm_scores[i] - human_scores[i]) for i in range(len(llm_scores))) / len(llm_scores)
        
        results[version] = {
            "correlation": correlation,
            "avg_difference": avg_diff
        }
        
        print(f"\n{'─'*70}")
        print(f"Version {version} Results:")
        print(f"  Correlation:      {correlation:.3f} {'✓ Good' if correlation > 0.85 else '✗ Needs improvement'}")
        print(f"  Avg Difference:   {avg_diff:.3f} {'✓ Good' if avg_diff < 0.15 else '✗ Too high'}")
        print('─'*70)
    
    # Compare versions
    print(f"\n{'='*70}")
    print("CALIBRATION SUMMARY")
    print('='*70)
    
    for version, metrics in results.items():
        print(f"\nVersion {version}:")
        print(f"  Correlation:    {metrics['correlation']:.3f}")
        print(f"  Avg Difference: {metrics['avg_difference']:.3f}")
    
    best_version = max(results, key=lambda v: results[v]["correlation"])
    print(f"\n🏆 Best Version: {best_version} (correlation: {results[best_version]['correlation']:.3f})")
    print("\n💡 Insight: Clear criteria + examples = better calibration")


def test_variance():
    """Test how stable scores are across multiple runs"""
    
    print("\n\n" + "="*70)
    print("SCORE VARIANCE TEST")
    print("="*70)
    
    test_case = LLMTestCase(
        input="I'm upset about my order",
        actual_output="Let me help you with that."
    )
    
    # Run same case 5 times with best version
    metric = CalibratedEmpathyMetric(version=3)
    scores = []
    
    print("\nRunning same test case 5 times...")
    for i in range(5):
        score = metric.measure(test_case)
        scores.append(score)
        print(f"  Run {i+1}: {score:.3f}")
    
    # Calculate variance
    mean_score = statistics.mean(scores)
    std_dev = statistics.stdev(scores) if len(scores) > 1 else 0
    
    print(f"\n{'─'*70}")
    print(f"Mean:     {mean_score:.3f}")
    print(f"Std Dev:  {std_dev:.3f}")
    print(f"Range:    {min(scores):.3f} - {max(scores):.3f}")
    print(f"Variance: {std_dev/mean_score*100:.1f}% {'✓ Acceptable' if std_dev < 0.05 else '⚠️  High variance'}")
    print('─'*70)
    
    print("\n💡 Insight: temperature=0 reduces but doesn't eliminate variance")


if __name__ == "__main__":
    test_calibration()
    test_variance()
    
    print("\n" + "="*70)
    print("✓ Calibration exercise complete!")
    print("="*70)
