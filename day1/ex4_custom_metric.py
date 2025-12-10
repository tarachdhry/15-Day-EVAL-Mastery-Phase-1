# File: day1/ex4_custom_metric.py
"""
Exercise 1.4: Build a Custom Metric from Scratch
Create a metric that evaluates brand voice alignment
"""

from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase
from deepeval import assert_test
import openai
import os


class BrandVoiceMetric(BaseMetric):
    """
    Evaluates if a response matches company brand voice:
    - Professional but friendly
    - Avoids jargon
    - Clear and concise
    - Helpful and empathetic
    """
    
    def __init__(self, threshold: float = 0.7):
        self.threshold = threshold
        self.score = 0
        self.reason = ""
    
    async def a_measure(self, test_case: LLMTestCase):
        """
        This method gets called by DeepEval to score the test case.
        1. Analyze test_case.actual_output
        2. Score it 0-1 based on brand criteria
        3. Set self.score
        4. Set self.reason (explanation)
        5. Return self.score
        """
        
        # Use OpenAI API to evaluate the brand voice
        
        client = openai.OpenAI(api_key=os.getenv(""))
        
        # Build a prompt that asks GPT-4 to evaluate brand voice
        evaluation_prompt = f"""
        Evaluate if this response matches our brand voice criteria:
        
        Brand Criteria:
        - Professional but friendly (not stiff or robotic)
        - Avoids jargon and technical terms
        - Clear and concise (no rambling)
        - Helpful and empathetic tone
        
        Response to evaluate:
        "{test_case.actual_output}"
        
        Score from 0 to 1 where:
        - 1.0 = Perfect brand voice alignment
        - 0.7-0.9 = Good, minor improvements needed
        - 0.4-0.6 = Mediocre, several issues
        - 0.0-0.3 = Poor, major misalignment
        
        Provide:
        1. A score (just the number)
        2. Brief explanation of what's good/bad
        
        Format your response as:
        Score: [number]
        Reason: [explanation]
        """
        
        # Call GPT-4
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a brand voice evaluator."},
                {"role": "user", "content": evaluation_prompt}
            ],
            temperature=0
        )
        
        result = response.choices[0].message.content
        
        # Parse the response to extract score and reason
        # Extract score and reason from result string
        lines = result.strip().split('\n')
        score_line = [l for l in lines if l.startswith('Score:')][0]
        reason_line = [l for l in lines if l.startswith('Reason:')][0]
        
        self.score = float(score_line.split(':')[1].strip())
        self.reason = reason_line.split(':')[1].strip()
        
        return self.score
    
    def is_successful(self):
        """Returns True if score meets threshold"""
        return self.score >= self.threshold


# TEST YOUR METRIC

def test_good_brand_voice():
    """Should PASS - good brand voice"""
    test_case = LLMTestCase(
        input="How do I reset my password?",
        actual_output="I'd be happy to help you reset your password! Simply click 'Forgot Password' on the login page, enter your email, and we'll send you a reset link right away."
    )
    
    metric = BrandVoiceMetric(threshold=0.7)
    assert_test(test_case, [metric])


def test_bad_brand_voice_robotic():
    """Should FAIL - too robotic/technical"""
    test_case = LLMTestCase(
        input="How do I reset my password?",
        actual_output="Execute password reset protocol via authentication portal. Input registered email address into designated field to initiate automated credential regeneration sequence."
    )
    
    metric = BrandVoiceMetric(threshold=0.7)
    try:
        assert_test(test_case, [metric])
        print("ERROR: This should have failed but passed")
    except AssertionError:
        print("CORRECT: Failed as expected (robotic tone)")


def test_bad_brand_voice_rude():
    """Should FAIL - not empathetic"""
    test_case = LLMTestCase(
        input="How do I reset my password?",
        actual_output="Just click forgot password. It's obvious."
    )
    
    metric = BrandVoiceMetric(threshold=0.7)
    try:
        assert_test(test_case, [metric])
        print("ERROR: This should have failed but passed")
    except AssertionError:
        print("CORRECT: Failed as expected (rude tone)")


if __name__ == "__main__":
    print("Testing Brand Voice Metric")
    print("=" * 50)
    
    print("\nTest 1: Good brand voice (should pass)")
    test_good_brand_voice()
    
    print("\nTest 2: Robotic voice (should fail)")
    test_bad_brand_voice_robotic()
    
    print("\nTest 3: Rude tone (should fail)")
    test_bad_brand_voice_rude()
    
    print("\n" + "=" * 50)
    print("Custom metric testing complete!")
