# File: day2/ex1_dataset_sprint.py
"""
Exercise 2.1: Dataset Sprint 
Build test cases across different domains
"""

from deepeval.dataset import EvaluationDataset, Golden

# Initialize dataset
dataset = EvaluationDataset()

# ========== CUSTOMER SUPPORT ==========

# Easy cases (7)
dataset.add_golden(Golden(
    input="How do I reset my password?",
    expected_output="Click 'Forgot Password', enter email, check inbox for reset link",
    additional_metadata={
        "difficulty": "easy",
        "category": "customer_support",
        "subcategory": "account_management"
    }
))

dataset.add_golden(Golden(
    input="What are your business hours?",
    expected_output="Monday-Friday 9 AM to 5 PM EST",
    additional_metadata={
        "difficulty": "easy",
        "category": "customer_support",
        "subcategory": "general_info"
    }
))


dataset.add_golden(Golden(
    input="I'm facing issues with login credentials",
    expected_output="Please go through our guide to login page for a step by step process",
    additional_metadata={
        "difficulty": "easy",
        "category": "customer_support",
        "subcategory": "general_info"
    }
))


dataset.add_golden(Golden(
    input="What is the customer support contact no.",
    expected_output="you can reach out to our team at +22222222",
    additional_metadata={
        "difficulty": "easy",
        "category": "customer_support",
        "subcategory": "general_info"
    }
))


dataset.add_golden(Golden(
    input="When can I expect to have my membership activated",
    expected_output="It usually take 24 hrs for you memebership to get activated post paymet processing",
    additional_metadata={
        "difficulty": "easy",
        "category": "customer_support",
        "subcategory": "general_info"
    }
))


dataset.add_golden(Golden(
    input="Is there any discount avaialbel for product SKU No. 14526",
    expected_output="Yes, you can avail the discount using coupn code DIS56",
    additional_metadata={
        "difficulty": "easy",
        "category": "customer_support",
        "subcategory": "general_info"
    }
))


dataset.add_golden(Golden(
    input="Can I cancel my order for which the payment is already made",
    expected_output="You can cancel your order within 24 hrs subject to zero additional charges",
    additional_metadata={
        "difficulty": "easy",
        "category": "customer_support",
        "subcategory": "general_info"
    }
))

# ADD 7 MORE EASY CUSTOMER SUPPORT CASES


dataset.add_golden(Golden(
    input="What are the steps to cancel my order",
    expected_output="You can find cancellation process details in our cancellation policy guide",
    additional_metadata={
        "difficulty": "easy",
        "category": "customer_support",
        "subcategory": "general_info"
    }
))


dataset.add_golden(Golden(
    input="How do I raise a refund request",
    expected_output="You can find details for refund in our refund policy doc on help page",
    additional_metadata={
        "difficulty": "easy",
        "category": "customer_support",
        "subcategory": "general_info"
    }
))


dataset.add_golden(Golden(
    input="I want to deactivate my notifications",
    expected_output="You can deactivate your notification by going to setting->notification->app->deactivate",
    additional_metadata={
        "difficulty": "easy",
        "category": "customer_support",
        "subcategory": "general_info"
    }
))


dataset.add_golden(Golden(
    input="How long does it take to ship the product",
    expected_output="The produt will be shipped within 2-7 days of processing payment ",
    additional_metadata={
        "difficulty": "easy",
        "category": "customer_support",
        "subcategory": "general_info"
    }
))


dataset.add_golden(Golden(
    input="What is your return policy",
    expected_output="You can return any product within 30 days. For any otehr information please read our return policy guide",
    additional_metadata={
        "difficulty": "easy",
        "category": "customer_support",
        "subcategory": "general_info"
    }
))


dataset.add_golden(Golden(
    input="How can I get access to your product list",
    expected_output="You can share your email here and we will mail you the product list",
    additional_metadata={
        "difficulty": "easy",
        "category": "customer_support",
        "subcategory": "general_info"
    }
))


dataset.add_golden(Golden(
    input="Can I return a product bought online to any of your stores",
    expected_output="Yes, you can return to any store nearby",
    additional_metadata={
        "difficulty": "easy",
        "category": "customer_support",
        "subcategory": "general_info"
    }
))

# Medium cases (8)
dataset.add_golden(Golden(
    input="I was charged twice for the same order, how do I get a refund?",
    expected_output="Contact billing support with order number, they'll investigate duplicate charge and process refund within 5-7 business days",
    additional_metadata={
        "difficulty": "medium",
        "category": "customer_support",
        "subcategory": "billing"
    }
))

dataset.add_golden(Golden(
    input="My payment is not being accepted",
    expected_output="Apologies for the trouble. It could possibly be a server issue. Kindly use teh follwing link to make the payment",
    additional_metadata={
        "difficulty": "Medium",
        "category": "customer_support",
        "subcategory": "Billing"
    }
))

dataset.add_golden(Golden(
    input="I did not recieve order notification post payment",
    expected_output="It usually take 2-6 hrs for us to process payments. Please contact +22334252 if you've already passed that window",
    additional_metadata={
        "difficulty": "Medium",
        "category": "customer_support",
        "subcategory": "General_info"
    }
))

dataset.add_golden(Golden(
    input="My discount coupon not working",
    expected_output="It is possible taht your valididty is expired. Kidnly share the coupon code here for us to procese the issue ",
    additional_metadata={
        "difficulty": "Medium",
        "category": "customer_support",
        "subcategory": "Discounts"
    }
))

dataset.add_golden(Golden(
    input="Havent recieved the refund yet",
    expected_output="It usually take about 7-13 days for teh refund to reflect in your bank account. Please contact +3417538261 if you've already passed that window",
    additional_metadata={
        "difficulty": "Medium",
        "category": "customer_support",
        "subcategory": "Refund"
    }
))

dataset.add_golden(Golden(
    input="I recieved a wrong product",
    expected_output="Sincere apologies. We request you to kindly conact +45362728 in order to address your concern and deliver the ordered product",
    additional_metadata={
        "difficulty": "Medium",
        "category": "customer_support",
        "subcategory": "Delivery"
    }
))

dataset.add_golden(Golden(
    input="It's been 14 days and my product is not delivered yet",
    expected_output="Sincere apologies for the delay. This could possibly due to shipping issues. Kindly contact our team at +36737217 so we can escalate your request",
    additional_metadata={
        "difficulty": "Medium",
        "category": "customer_support",
        "subcategory": "Delivery"
    }
))

dataset.add_golden(Golden(
    input="My OTP has expired for subscription.",
    expected_output="No issues if your subscription is still active you can request a new OTP using our generate OTP tab on login page",
    additional_metadata={
        "difficulty": "Medium",
        "category": "customer_support",
        "subcategory": "Login"
    }
))



# Hard cases (6)
dataset.add_golden(Golden(
    input="I need to export my data under GDPR, cancel my subscription, delete my account, but keep my order history for tax purposes - what's the process?",
    expected_output="Step-by-step process: 1) Request data export via settings, 2) Cancel subscription (keeps order history), 3) Submit GDPR deletion request specifying to retain order records for legal compliance",
    additional_metadata={
        "difficulty": "hard",
        "category": "customer_support",
        "subcategory": "compliance"
    }
))

dataset.add_golden(Golden(
    input="I want return the product due to defect, it has crossed 30 day return window",
    expected_output="Unfortunately we do not accept return post 30 day window. For further assitance kindly contact our support team at +362769487",
    additional_metadata={
        "difficulty": "hard",
        "category": "customer_support",
        "subcategory": "Return"
    }
))

dataset.add_golden(Golden(
    input="I want to change my address for pickup",
    expected_output="Sure. Please provide your updated address in the link here. You can also reach out to our support team at +37626489 to make the changes",
    additional_metadata={
        "difficulty": "hard",
        "category": "customer_support",
        "subcategory": "Shipping"
    }
))


dataset.add_golden(Golden(
    input="I want to you to match the price qouted on th website with what I paid offline",
    expected_output="We have separate pricing for our online and offline SKU mentioned in our company guide. Rest assured that your paid the fair price for teh product",
    additional_metadata={
        "difficulty": "hard",
        "category": "customer_support",
        "subcategory": "Pricing policy"
    }
))

dataset.add_golden(Golden(
    input="I am not able to change location on my app",
    expected_output="This is an app store issue.On your app stor go to settings-> profile->chaneg location.",
    additional_metadata={
        "difficulty": "hard",
        "category": "customer_support",
        "subcategory": "Application"
    }
))

dataset.add_golden(Golden(
    input="I want to report issue with my product that has passed warranty",
    expected_output="Apologies for the inconvenience. Kindly contact our team at +5527648 and we'll guide your through our service policy",
    additional_metadata={
        "difficulty": "hard",
        "category": "customer_support",
        "subcategory": "Service policy"
    }
))


# ========== TECHNICAL DOCUMENTATION ==========

# Easy (1)
dataset.add_golden(Golden(
    input="How do I install the Python package?",
    expected_output="Run: pip install package-name",
    additional_metadata={
        "difficulty": "easy",
        "category": "technical_docs",
        "subcategory": "installation"
    }
))


# Medium (1)
dataset.add_golden(Golden(
    input="How do I authenticate API requests?",
    expected_output="Include API key in Authorization header: 'Authorization: Bearer YOUR_API_KEY'. Get key from dashboard settings.",
    additional_metadata={
        "difficulty": "medium",
        "category": "technical_docs",
        "subcategory": "api"
    }
))


# Hard (1)
dataset.add_golden(Golden(
    input="How do I implement custom authentication with OAuth2, handle token refresh, and manage multiple user sessions with rate limiting?",
    expected_output="Multi-step implementation guide covering OAuth2 flow, refresh token storage, session management with Redis, and rate limiting per user with token bucket algorithm",
    additional_metadata={
        "difficulty": "hard",
        "category": "technical_docs",
        "subcategory": "advanced_auth"
    }
))



# ========== PRODUCT RECOMMENDATIONS ==========

# Easy (1)
dataset.add_golden(Golden(
    input="I need wireless headphones under $100",
    expected_output="Recommended options: Sony WH-CH520 ($58), Anker Soundcore Q30 ($79), JBL Tune 510BT ($49)",
    additional_metadata={
        "difficulty": "easy",
        "category": "product_recommendations",
        "subcategory": "electronics"
    }
))



# ========== SAVE DATASET ==========

print(f"Dataset created with {len(dataset.goldens)} test cases")

print("\nBreakdown by difficulty:")
easy = len([g for g in dataset.goldens if g.additional_metadata.get("difficulty") == "easy"])
medium = len([g for g in dataset.goldens if g.additional_metadata.get("difficulty") == "medium"])
hard = len([g for g in dataset.goldens if g.additional_metadata.get("difficulty") == "hard"])
print(f"Easy: {easy}")
print(f"Medium: {medium}")
print(f"Hard: {hard}")

print("\nBreakdown by category:")
categories = {}
for g in dataset.goldens:
    cat = g.additional_metadata.get("category", "unknown")
    categories[cat] = categories.get(cat, 0) + 1
for cat, count in categories.items():
    print(f"{cat}: {count}")

import json

# Save your manual dataset
dataset_dict = {
    "goldens": [
        {
            "input": g.input,
            "expected_output": g.expected_output,
            "metadata": g.additional_metadata
        }
        for g in dataset.goldens
    ]
}

with open("day2_manual_cases.json", "w") as f:
    json.dump(dataset_dict, f, indent=2)

print(f"✓ Saved manual dataset")
