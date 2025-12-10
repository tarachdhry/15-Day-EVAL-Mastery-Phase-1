from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams

def test_basic_greeting():
    test_case = LLMTestCase(
        input="Hello, how are you?",
        actual_output="Hi! I'm doing great, thank you for asking! How can I help you today?",
        expected_output="A warm, friendly greeting that offers help"
    )
    
    friendliness_metric = GEval(
        name="Friendliness",
        criteria="The response should be warm, welcoming, and offer assistance",
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
        evaluation_steps=[
            "Check if the response is warm and friendly",
            "Check if the response offers help"
        ],
        threshold=0.7
    )
    
    assert_test(test_case, [friendliness_metric])

if __name__ == "__main__":
    test_basic_greeting()
    print("✅ Test passed!")
