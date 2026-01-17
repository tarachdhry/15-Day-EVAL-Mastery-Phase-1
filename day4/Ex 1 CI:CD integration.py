"""
Exercise 4.1: CI/CD Integration with Pytest
Run evals automatically in your deployment pipeline
"""

import pytest
import openai
import json
from deepeval.test_case import LLMTestCase
from deepeval.metrics import BaseMetric

client = openai.OpenAI(api_key="")


# ============================================================================
# SYSTEM UNDER TEST
# ============================================================================

CURRENT_SYSTEM_PROMPT = """You are a helpful customer support agent.
Be professional and assist users with their questions."""

def generate_response(user_input: str) -> str:
    """The LLM system we're evaluating (this would be your actual product)"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": CURRENT_SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content


# ============================================================================
# METRICS
# ============================================================================

class AccuracyMetric(BaseMetric):
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


class EmpathyMetric(BaseMetric):
    def __init__(self, threshold=0.6):
        self.threshold = threshold
        self.score = 0
        self.reason = ""
    
    def measure(self, test_case: LLMTestCase):
        prompt = f"""Rate EMPATHY 0-10.

Input: {test_case.input}
Response: {test_case.actual_output}

Criteria: Acknowledges emotion + warm tone

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


# ============================================================================
# GOLDEN DATASET (from Day 2)
# ============================================================================

GOLDEN_TEST_CASES = [
    {
        "input": "My package never arrived!",
        "expected_output": "Acknowledge frustration, investigate order, offer solution",
        "metadata": {"category": "shipping", "priority": "high"}
    },
    {
        "input": "How do I reset my password?",
        "expected_output": "Step-by-step password reset instructions",
        "metadata": {"category": "account", "priority": "medium"}
    },
    {
        "input": "What's your return policy?",
        "expected_output": "30-day return policy details",
        "metadata": {"category": "policy", "priority": "low"}
    },
    {
        "input": "I'm very frustrated with your service",
        "expected_output": "Acknowledge emotion, apologize, offer to help",
        "metadata": {"category": "complaint", "priority": "high"}
    },
    {
        "input": "Can you help me track my order?",
        "expected_output": "Ask for order number, provide tracking info",
        "metadata": {"category": "shipping", "priority": "medium"}
    },
]


# ============================================================================
# PYTEST TEST SUITE
# ============================================================================

class TestCustomerSupportSystem:
    """
    Pytest test suite for CI/CD pipeline
    
    Run with: pytest test_evals.py -v
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup runs before each test"""
        self.accuracy_metric = AccuracyMetric(threshold=0.7)
        self.empathy_metric = EmpathyMetric(threshold=0.6)
    
    @pytest.mark.parametrize("test_data", GOLDEN_TEST_CASES)
    def test_accuracy_on_golden_set(self, test_data):
        """Test: All responses must be accurate"""
        
        # Generate response from your system
        response = generate_response(test_data["input"])
        
        # Create test case
        test_case = LLMTestCase(
            input=test_data["input"],
            actual_output=response,
            expected_output=test_data["expected_output"]
        )
        
        # Evaluate
        score = self.accuracy_metric.measure(test_case)
        
        # Assert (this will FAIL the CI/CD if score too low)
        assert self.accuracy_metric.is_successful(), \
            f"Accuracy failed: {score:.2f} < {self.accuracy_metric.threshold}\n" \
            f"Input: {test_data['input']}\n" \
            f"Response: {response}\n" \
            f"Reason: {self.accuracy_metric.reason}"
    
    @pytest.mark.parametrize("test_data", GOLDEN_TEST_CASES)
    def test_empathy_on_golden_set(self, test_data):
        """Test: All responses must be empathetic"""
        
        response = generate_response(test_data["input"])
        
        test_case = LLMTestCase(
            input=test_data["input"],
            actual_output=response,
            expected_output=test_data["expected_output"]
        )
        
        score = self.empathy_metric.measure(test_case)
        
        assert self.empathy_metric.is_successful(), \
            f"Empathy failed: {score:.2f} < {self.empathy_metric.threshold}\n" \
            f"Input: {test_data['input']}\n" \
            f"Response: {response}\n" \
            f"Reason: {self.empathy_metric.reason}"
    
    @pytest.mark.critical
    def test_no_hallucination_on_policy_questions(self):
        """Critical test: Must not hallucinate company policies"""
        
        test_cases = [
            {
                "input": "What's your refund policy?",
                "forbidden_phrases": ["90 days", "100% money back", "instant refund"],
                "required_info": "30 days"
            },
        ]
        
        for test in test_cases:
            response = generate_response(test["input"])
            
            # Check no forbidden phrases
            for phrase in test["forbidden_phrases"]:
                assert phrase.lower() not in response.lower(), \
                    f"HALLUCINATION DETECTED: Response contains '{phrase}'\n" \
                    f"Input: {test['input']}\n" \
                    f"Response: {response}"
            
            # Check required info present
            assert test["required_info"].lower() in response.lower(), \
                f"MISSING INFO: Response should mention '{test['required_info']}'\n" \
                f"Input: {test['input']}\n" \
                f"Response: {response}"


# ============================================================================
# RUN INSTRUCTIONS
# ============================================================================

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                    CI/CD EVAL INTEGRATION                            ║
╚══════════════════════════════════════════════════════════════════════╝

This test suite runs in your CI/CD pipeline to block bad deployments.

USAGE:
  pytest test_evals.py -v

This ensures every code change is evaluated before deployment.
""")
