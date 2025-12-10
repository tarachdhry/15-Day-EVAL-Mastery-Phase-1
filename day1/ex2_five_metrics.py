# File: day1/ex2_five_metrics.py
"""
Five Basic Metrics
Testing different metric types to understand their use cases
"""

from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import (
    GEval,
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualPrecisionMetric,
    HallucinationMetric
)


def test_correctness():
    """
    GEval: Custom criteria-based evaluation
    Use when: You need to evaluate against specific business rules or custom criteria
    """
    test_case = LLMTestCase(
        input="What is the capital of France?",
        actual_output="The capital of France is Paris, a major European city known for the Eiffel Tower.",
        expected_output="Paris"
    )
    
    metric = GEval(
        name="Correctness",
        criteria="The response must provide the correct factual answer to the question",)    
    assert_test(test_case, [metric])


def test_relevancy():
    """
    AnswerRelevancyMetric: Measures if the answer actually addresses the question
    Use when: You want to ensure responses stay on-topic and don't go off on tangents
    """
    test_case = LLMTestCase(
        input="How do I reset my password?",
        actual_output="To reset your password, click the 'Forgot Password' link on the login page, enter your email, and follow the instructions sent to your inbox.",
        expected_output="Instructions for password reset"
    )
    
    metric = AnswerRelevancyMetric(threshold=0.7)
    
    assert_test(test_case, [metric])


def test_faithfulness():
    """
    FaithfulnessMetric: Checks if the answer is grounded in the provided context
    Use when: You have RAG systems and need to ensure the LLM isn't making things up
    Requires: retrieval_context parameter
    """
    test_case = LLMTestCase(
        input="What are our business hours?",
        actual_output="We are open Monday through Friday, 9 AM to 5 PM EST.",
        expected_output="Business hours information",
        retrieval_context=[
            "Company Policy Document: Business hours are 9:00 AM to 5:00 PM Eastern Standard Time, Monday through Friday. We are closed on weekends and federal holidays."
        ]
    )
    
    metric = FaithfulnessMetric(threshold=0.7)
    
    assert_test(test_case, [metric])


def test_precision():
    """
    ContextualPrecisionMetric: Evaluates if relevant context is ranked higher
    Use when: Testing retrieval systems - are the most relevant docs appearing first?
    Requires: retrieval_context (list of docs in ranked order) and expected_output
    """
    test_case = LLMTestCase(
        input="What is our return policy?",
        actual_output="You can return items within 30 days for a full refund.",
        expected_output="30-day return policy with full refund",
        retrieval_context=[
            "Return Policy: We offer a 30-day return window for all items. Full refunds are provided for items in original condition.",  # Most relevant - should be first
            "Shipping Policy: Standard shipping takes 3-5 business days.",  # Less relevant
            "Privacy Policy: We protect your personal information."  # Not relevant
        ]
    )
    
    metric = ContextualPrecisionMetric(threshold=0.7)
    
    assert_test(test_case, [metric])


def test_hallucination():
    """
    HallucinationMetric: Detects when the model makes up information not in context
    Use when: You absolutely need to prevent false information
    Requires: context parameter
    """
    test_case = LLMTestCase(
        input="What features does our Pro plan include?",
        actual_output="The Pro plan includes unlimited users, 50GB storage, and priority support.",
        context=[
            "Pro Plan Features: Unlimited users, 50GB cloud storage, priority email support, advanced analytics dashboard."
        ]
    )
    
    metric = HallucinationMetric(threshold=0.7)
    
    assert_test(test_case, [metric])


if __name__ == "__main__":
    print("Running Exercise 1.2: Five Basic Metrics")
    print("=" * 50)
    print("\nTest 1: Correctness (GEval)")
    test_correctness()
    print("✓ Passed\n")
    
    print("Test 2: Answer Relevancy")
    test_relevancy()
    print("✓ Passed\n")
    
    print("Test 3: Faithfulness")
    test_faithfulness()
    print("✓ Passed\n")
    
    print("Test 4: Contextual Precision")
    test_precision()
    print("✓ Passed\n")
    
    print("Test 5: Hallucination Detection")
    test_hallucination()
    print("✓ Passed\n")
    
    print("=" * 50)
    print("All 5 metrics tested successfully!")

