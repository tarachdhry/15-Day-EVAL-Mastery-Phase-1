# File: day3/ex1_multidimensional_metric.py
"""
Exercise 3.1: Multi-Dimensional Metric
Score responses across multiple quality dimensions
"""

import openai
import os
import json
import asyncio
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase
from deepeval import assert_test

client = openai.OpenAI(api_key="")


class MultiDimensionalQualityMetric(BaseMetric):
    """
    Evaluates response across 5 dimensions:
    1. Accuracy - Is information correct?
    2. Completeness - Does it answer fully?
    3. Clarity - Is it easy to understand?
    4. Empathy - Is tone appropriate and helpful?
    5. Conciseness - Is it brief without losing info?
    
    Returns individual scores + weighted overall score
    """
    
    def __init__(self, threshold: float = 0.7, weights: dict = None):
        self.threshold = threshold
        self.score = 0
        self.reason = ""
        
        # Dimension scores
        self.accuracy_score = 0
        self.completeness_score = 0
        self.clarity_score = 0
        self.empathy_score = 0
        self.conciseness_score = 0
        
        # Default weights (sum to 1.0)
        self.weights = weights or {
            "accuracy": 0.30,      # Most important
            "completeness": 0.25,
            "clarity": 0.20,
            "empathy": 0.15,
            "conciseness": 0.10    # Least important
        }
    
    def measure(self, test_case: LLMTestCase):
        """
        Evaluate across all dimensions
        """
        
        evaluation_prompt = f"""
You are evaluating a customer support response across 5 quality dimensions.

User Question:
{test_case.input}

Response to Evaluate:
{test_case.actual_output}

Expected/Ideal Response (for reference):
{test_case.expected_output}

Rate the response on each dimension from 0 to 10:

1. ACCURACY (0-10): Is the information factually correct?
   - 10 = Completely accurate
   - 5 = Partially correct
   - 0 = Incorrect information

2. COMPLETENESS (0-10): Does it fully answer the question?
   - 10 = Addresses all aspects
   - 5 = Partially answers
   - 0 = Doesn't answer question

3. CLARITY (0-10): Is it easy to understand?
   - 10 = Crystal clear
   - 5 = Somewhat clear
   - 0 = Confusing

4. EMPATHY (0-10): Is the tone helpful and appropriate?
   - 10 = Warm, understanding, supportive
   - 5 = Neutral, functional
   - 0 = Cold, robotic, or rude

5. CONCISENESS (0-10): Is it brief without losing important info?
   - 10 = Perfectly concise
   - 5 = Somewhat wordy
   - 0 = Extremely verbose or too terse

Respond in JSON format:
{{
  "accuracy": 0-10,
  "completeness": 0-10,
  "clarity": 0-10,
  "empathy": 0-10,
  "conciseness": 0-10,
  "reasoning": {{
    "accuracy": "why this score",
    "completeness": "why this score",
    "clarity": "why this score",
    "empathy": "why this score",
    "conciseness": "why this score"
  }}
}}
"""
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert evaluator of customer support responses."},
                {"role": "user", "content": evaluation_prompt}
            ],
            temperature=0
        )
        
        result = response.choices[0].message.content
        result = result.replace("```json", "").replace("```", "").strip()
        
        try:
            scores = json.loads(result)
            
            # Store individual dimension scores (normalize to 0-1)
            self.accuracy_score = scores["accuracy"] / 10
            self.completeness_score = scores["completeness"] / 10
            self.clarity_score = scores["clarity"] / 10
            self.empathy_score = scores["empathy"] / 10
            self.conciseness_score = scores["conciseness"] / 10
            
            # Calculate weighted overall score
            self.score = (
                self.accuracy_score * self.weights["accuracy"] +
                self.completeness_score * self.weights["completeness"] +
                self.clarity_score * self.weights["clarity"] +
                self.empathy_score * self.weights["empathy"] +
                self.conciseness_score * self.weights["conciseness"]
            )
            
            # Build detailed reason
            reasoning = scores.get("reasoning", {})
            self.reason = f"""
Overall Score: {self.score:.2f}

Dimension Breakdown:
- Accuracy: {self.accuracy_score:.2f} ({scores['accuracy']}/10) - {reasoning.get('accuracy', 'N/A')}
- Completeness: {self.completeness_score:.2f} ({scores['completeness']}/10) - {reasoning.get('completeness', 'N/A')}
- Clarity: {self.clarity_score:.2f} ({scores['clarity']}/10) - {reasoning.get('clarity', 'N/A')}
- Empathy: {self.empathy_score:.2f} ({scores['empathy']}/10) - {reasoning.get('empathy', 'N/A')}
- Conciseness: {self.conciseness_score:.2f} ({scores['conciseness']}/10) - {reasoning.get('conciseness', 'N/A')}
"""
            
        except Exception as e:
            print(f"Error parsing scores: {e}")
            self.score = 0.5
            self.reason = f"Evaluation error: {str(e)}"
        
        return self.score
    
    def is_successful(self):
        return self.score >= self.threshold
    
    def get_dimension_scores(self):
        """Return dict of all dimension scores"""
        return {
            "accuracy": self.accuracy_score,
            "completeness": self.completeness_score,
            "clarity": self.clarity_score,
            "empathy": self.empathy_score,
            "conciseness": self.conciseness_score,
            "overall": self.score
        }


# ========== TEST THE METRIC ==========

def test_good_response():
    """Should score high across all dimensions"""
    test_case = LLMTestCase(
        input="How do I reset my password?",
        actual_output="I'd be happy to help you reset your password! Simply click 'Forgot Password' on the login page, enter your registered email, and you'll receive a reset link within 5 minutes. Let me know if you need any other assistance!",
        expected_output="Instructions for password reset via email"
    )
    
    metric = MultiDimensionalQualityMetric(threshold=0.7)
    
    print("\n" + "="*60)
    print("TEST 1: Good Response")
    print("="*60)
    
    metric.measure(test_case)
    print(f"{'✓ PASSED' if metric.is_successful() else '✗ FAILED'}")
    
    scores = metric.get_dimension_scores()
    print("\nDimension Scores:")
    for dim, score in scores.items():
        print(f"  {dim:.<20} {score:.2f}")
    
    print(f"\nDetailed Reasoning:")
    print(metric.reason)


def test_accurate_but_cold():
    """High accuracy, low empathy"""
    test_case = LLMTestCase(
        input="How do I reset my password?",
        actual_output="Click forgot password.",
        expected_output="Instructions for password reset"
    )
    
    metric = MultiDimensionalQualityMetric(threshold=0.7)
    
    print("\n" + "="*60)
    print("TEST 2: Accurate but Cold")
    print("="*60)
    
    try:
        metric.measure(test_case)
        print(f"{'✓ PASSED' if metric.is_successful() else '✗ FAILED'}")
        print("✓ PASSED")
    except AssertionError:
        print("✗ FAILED (as expected - lacks empathy)")
    
    scores = metric.get_dimension_scores()
    print("\nDimension Scores:")
    for dim, score in scores.items():
        print(f"  {dim:.<20} {score:.2f}")
    
    print("\nInsight: High accuracy (0.90) but low empathy (0.40) → Overall: {:.2f}".format(metric.score))


def test_empathetic_but_vague():
    """High empathy, low completeness"""
    test_case = LLMTestCase(
        input="How do I reset my password?",
        actual_output="I'm so sorry you're having trouble with your password!",
        expected_output="Instructions for password reset"
    )
    
    metric = MultiDimensionalQualityMetric(threshold=0.7)
    
    print("\n" + "="*60)
    print("TEST 3: Empathetic but Vague")
    print("="*60)
    
    try:
        metric.measure(test_case)
        print(f"{'✓ PASSED' if metric.is_successful() else '✗ FAILED'}")
        print("✓ PASSED")
    except AssertionError:
        print("✗ FAILED (as expected - doesn't actually answer)")
    
    scores = metric.get_dimension_scores()
    print("\nDimension Scores:")
    for dim, score in scores.items():
        print(f"  {dim:.<20} {score:.2f}")
    
    print("\nInsight: High empathy but doesn't answer question → Fails completeness")

def test_verbose_but_accurate():
    """Test case: Verbose but accurate"""
    test_case = LLMTestCase(
        input="How do I cancel my subscription?",
        actual_output="Thank you so much for reaching out to us today! I completely understand that you're looking to cancel your subscription, and I want to make sure I provide you with the most comprehensive information possible to help you through this process. To cancel your subscription, you'll need to first log into your account dashboard, which you can access by clicking the 'Login' button in the top right corner of our website. Once you're logged in, navigate to the 'Settings' menu, then click on 'Subscription Management.' From there, you'll see a list of all your active subscriptions, and you can select the one you wish to cancel. Click the 'Cancel Subscription' button, and you'll be prompted to confirm your cancellation. After confirming, you'll receive an email confirmation within 24 hours. Please note that your subscription will remain active until the end of your current billing period.",
        expected_output="Instructions to cancel subscription"
    )
    
    metric = MultiDimensionalQualityMetric(threshold=0.7)
    
    print("\n" + "="*60)
    print("TEST 5: Verbose but Accurate")
    print("="*60)
    
    metric.measure(test_case)
    print(f"{'✓ PASSED' if metric.is_successful() else '✗ FAILED'}")
    
    scores = metric.get_dimension_scores()
    print("\nDimension Scores:")
    for dim, score in scores.items():
        print(f"  {dim:.<20} {score:.2f}")
    
    print(f"\n💡 Insight: Accuracy high ({scores['accuracy']:.2f}) but conciseness low ({scores['conciseness']:.2f})")


def test_confusing_but_empathetic():
    """Test case: Confusing but empathetic"""
    test_case = LLMTestCase(
        input="How do I update my billing address?",
        actual_output="I'm so sorry you're having trouble with this! It can definitely be frustrating when you need to update important information. We really appreciate your patience! To help you out, you'll want to go to the place where you manage things, and from there, look for the area that handles your information. You know, the section that has all your details? Once you find that, you should see something about addresses. Click on that and you should be all set! Let me know if you need any more help - we're here for you!",
        expected_output="Instructions to update billing address"
    )
    
    metric = MultiDimensionalQualityMetric(threshold=0.7)
    
    print("\n" + "="*60)
    print("TEST 6: Confusing but Empathetic")
    print("="*60)
    
    metric.measure(test_case)
    print(f"{'✓ PASSED' if metric.is_successful() else '✗ FAILED'}")
    
    scores = metric.get_dimension_scores()
    print("\nDimension Scores:")
    for dim, score in scores.items():
        print(f"  {dim:.<20} {score:.2f}")
    
    print(f"\n💡 Insight: Empathy high ({scores['empathy']:.2f}) but clarity low ({scores['clarity']:.2f})")


def test_perfect_response():
    """Test case: Perfect across all dimensions"""
    test_case = LLMTestCase(
        input="What's your shipping policy?",
        actual_output="Great question! We offer free standard shipping on all orders over $50, which typically arrives in 5-7 business days. For orders under $50, standard shipping is $5.99. If you need your order faster, we also offer express shipping (2-3 business days) for $14.99. All orders ship within 24 hours on business days. You'll receive tracking information via email once your order ships!",
        expected_output="Shipping policy details"
    )
    
    metric = MultiDimensionalQualityMetric(threshold=0.7)
    
    print("\n" + "="*60)
    print("TEST 7: Perfect Response")
    print("="*60)
    
    metric.measure(test_case)
    print(f"{'✓ PASSED' if metric.is_successful() else '✗ FAILED'}")
    
    scores = metric.get_dimension_scores()
    print("\nDimension Scores:")
    for dim, score in scores.items():
        print(f"  {dim:.<20} {score:.2f}")
    
    print(f"\n💡 Insight: All dimensions > 0.85? This is your gold standard!")


def test_custom_weights():
    """Test with different importance weights"""
    test_case = LLMTestCase(
        input="What's the refund policy?",
        actual_output="We offer 30-day returns.",
        expected_output="30-day money-back guarantee"
    )
    
    print("\n" + "="*60)
    print("TEST 4: Custom Weights Comparison")
    print("="*60)
    
    # Default weights (accuracy most important)
    metric1 = MultiDimensionalQualityMetric(
        threshold=0.7,
        weights={"accuracy": 0.30, "completeness": 0.25, "clarity": 0.20, "empathy": 0.15, "conciseness": 0.10}
    )
    metric1.measure(test_case)  # ADD asyncio.run()
    
    # Empathy-focused weights (customer-centric brand)
    metric2 = MultiDimensionalQualityMetric(
        threshold=0.7,
        weights={"accuracy": 0.20, "completeness": 0.20, "clarity": 0.15, "empathy": 0.35, "conciseness": 0.10}
    )
    metric1.measure(test_case)  # ADD asyncio.run()

    # Completeness focussed weights (customer-centric brand)
    metric2 = MultiDimensionalQualityMetric(
        threshold=0.7,
        weights={"accuracy": 0.20, "completeness": 0.30, "clarity": 0.15, "empathy": 0.25, "conciseness": 0.10}
    )
    metric1.measure(test_case) 


    print("\nSame response, different weights:")
    print(f"\nDefault weights (accuracy-focused):")
    print(f"  Overall Score: {metric1.score:.2f}")
    
    print(f"\nEmpathy-focused weights:")
    print(f"  Overall Score: {metric2.score:.2f}")
    
    print("\nInsight: Weighting changes what 'good' means for your brand")


def test_weight_experiments():
    """Compare same response with 3 different weight profiles"""
    test_case = LLMTestCase(
        input="How do I file a complaint?",
        actual_output="File a complaint by emailing complaints@company.com with your account number, date of incident, and detailed description. We respond within 2 business days.",
        expected_output="Complaint filing process"
    )
    
    print("\n" + "="*60)
    print("TEST 8: Weight Profile Comparison")
    print("="*60)
    
    # Profile 1: Legal/Compliance
    legal_weights = {
        "accuracy": 0.50,
        "completeness": 0.30,
        "clarity": 0.10,
        "empathy": 0.05,
        "conciseness": 0.05
    }
    
    # Profile 2: Customer Delight
    delight_weights = {
        "accuracy": 0.20,
        "completeness": 0.20,
        "clarity": 0.20,
        "empathy": 0.30,
        "conciseness": 0.10
    }
    
    # Profile 3: Technical Docs
    tech_weights = {
        "accuracy": 0.40,
        "completeness": 0.25,
        "clarity": 0.25,
        "empathy": 0.05,
        "conciseness": 0.05
    }
    
    profiles = {
        "Legal/Compliance": legal_weights,
        "Customer Delight": delight_weights,
        "Technical Docs": tech_weights
    }
    
    print("\nSame response evaluated with 3 different priorities:\n")
    
    for profile_name, weights in profiles.items():
        metric = MultiDimensionalQualityMetric(threshold=0.7, weights=weights)
        metric.measure(test_case)
        
        print(f"{profile_name}:")
        print(f"  Overall Score: {metric.score:.2f} {'✓' if metric.is_successful() else '✗'}")
        print(f"  Top weight: {max(weights, key=weights.get)} ({weights[max(weights, key=weights.get)]:.2f})")
        print()

if __name__ == "__main__":
    print("MULTI-DIMENSIONAL QUALITY METRIC")
    print("="*60)
    
    # Run all tests
    test_good_response()
    test_accurate_but_cold()
    test_empathetic_but_vague()
    test_custom_weights()
    test_verbose_but_accurate()       # NEW
    test_confusing_but_empathetic()   # NEW
    test_perfect_response()            # NEW
    test_weight_experiments()
    
    print("\n" + "="*60)
    print("✓ Multi-dimensional evaluation complete!")
    print("="*60)
