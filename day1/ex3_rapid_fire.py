# File: day1/ex3_rapid_fire.py
"""
Exercise 1.3: Rapid Fire Testing
Build 15 diverse test cases quickly
"""

from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualPrecisionMetric,
    HallucinationMetric
)

# ========== CUSTOMER SUPPORT (5 tests) ==========

def test_cs_password_reset():
    test_case = LLMTestCase(
        input="I forgot my password, what do I do?",
        actual_output="Click 'Forgot Password' on the login page. Enter your email and we'll send you a reset link.",
        expected_output="Instructions for password reset via email"
    )
    assert_test(test_case, [AnswerRelevancyMetric(threshold=0.7)])

def test_cs_refund_request():
    test_case = LLMTestCase(
        input="What's the window to return the product i bought",
        actual_output="You can return the product within 30 days of buying for full refund",
        expected_output="30 day return policy"
    )
    assert_test(test_case, [ContextualPrecisionMetric(threshold=0.7)])

def test_cs_shipping_status():
    test_case = LLMTestCase(
        input="How long does it take to ship teh product",
        actual_output="The product is shipped within 2-7 days after payment is made",
        expected_output="Standard shipping takes 2-7 days"
    )
    assert_test(test_case, [ContextualPrecisionMetric(threshold=0.7)])

def test_cs_account_deletion():
    test_case = LLMTestCase(
        input="What is the procedure to delete my account",
        actual_output="Once a request is made, an OTP will be sent to your email to confirm the deletion",
        expected_output="OTP is generated and sent to registered email ID"
    )
    assert_test(test_case, [FaithfulnessMetric(threshold=0.7)])

def test_cs_billing_issue():
    test_case = LLMTestCase(
        input="My payment is not going through",
        actual_output="Please contact our customer care for assistnace",
        expected_output="Share customer care details"
    )
    assert_test(test_case, [ContextualPrecisionMetric(threshold=0.7)])

# ========== TECHNICAL DOCUMENTATION (5 tests) ==========

def test_tech_api_authentication():
    test_case = LLMTestCase(
        input="How do I authenticate the API",
        actual_output="Visit our API authetication page *link shared* for step by step process",
        expected_output="Share API authentication page link"
    )
    assert_test(test_case, [AnswerRelevancyMetric(threshold=0.7)])

def test_tech_error_handling():
    test_case = LLMTestCase(
        input="How do I authenticate the API",
        actual_output="Visit our API authetication page *link shared* for step by step process",
        expected_output="Share API authentication page link"
    )
    assert_test(test_case, [AnswerRelevancyMetric(threshold=0.7)])

def test_tech_installation_steps():
    test_case = LLMTestCase(
        input="How do I install teh app version",
        actual_output="Sharing step by step guide to installation on your email ID",
        expected_output="Send installation guide on registered email"
    )
    assert_test(test_case, [AnswerRelevancyMetric(threshold=0.7)])

def test_tech_configuration():
    test_case = LLMTestCase(
        input="How do I the configure my app",
        actual_output="Sharing step by step guide to installation on your email ID",
        expected_output="Send installation guide on registered email"
    )
    assert_test(test_case, [AnswerRelevancyMetric(threshold=0.7)])

def test_tech_troubleshooting():
    test_case = LLMTestCase(
        input="How do I troubloeshhot the errors",
        actual_output="Sharing step by step guide to installation on your email ID",
        expected_output="Send installation guide on registered email"
    )
    assert_test(test_case, [AnswerRelevancyMetric(threshold=0.7)])

# ========== DATA ANALYSIS (5 tests) ==========

def test_data_trend_analysis():
    test_case = LLMTestCase(
        input="Could you share data trends over past 5 years",
        actual_output="Sure, what parameters would you want to see trend analysis",
        expected_output="Share trend analsyis for shared parameters or features"
    )
    assert_test(test_case, [AnswerRelevancyMetric(threshold=0.7)])

def test_data_statistical_summary():
    test_case = LLMTestCase(
        input="I want a data statistical summary of my Y-O-Y performance",
        actual_output="Sure, please share what features you want to generate the summary for",
        expected_output="Generate Statistical summary"
    )
    assert_test(test_case, [AnswerRelevancyMetric(threshold=0.7)])

def test_data_comparison():
    test_case = LLMTestCase(
        input="How do I this year's data with previous year",
        actual_output="You can compare yearly data in our comparison tab by changing teh years",
        expected_output="Guide through the comaprison functionality"
    )
    assert_test(test_case, [AnswerRelevancyMetric(threshold=0.7)])

def test_data_insight_extraction():
    test_case = LLMTestCase(
        input="How do I extract data insights",
        actual_output="You can feed reqiured data points in out inghts tab and it shall generate teh report for you ",
        expected_output="Extract data insights and generate report"
    )
    assert_test(test_case, [AnswerRelevancyMetric(threshold=0.7)])

def test_data_recommendation():
    test_case = LLMTestCase(
        input="Do you have any data recommendation to suggest",
        actual_output="Sure, you can share your requiremenst and we can generate recommendation for you",
        expected_output="Share recommendation on data analysis"
    )
    assert_test(test_case, [AnswerRelevancyMetric(threshold=0.7)])
