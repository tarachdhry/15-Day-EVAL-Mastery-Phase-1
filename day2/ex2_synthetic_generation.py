# File: day2/ex2_synthetic_generation.py
"""
Exercise 2.2: Synthetic Data Generation
Use GPT-4 to automatically generate test cases
"""

import openai
import os
import json
from deepeval.dataset import EvaluationDataset, Golden

client = openai.OpenAI(api_key="")

# ========== SAMPLE DOCUMENTATION ==========
# This is the "knowledge base" GPT-4 will use to generate test cases

DOCUMENTATION = """
Customer Support Knowledge Base:

PASSWORD RESET:
Users can reset passwords by clicking "Forgot Password" on login page.
A reset link is sent to their registered email within 5 minutes.
Links expire after 24 hours.

REFUND POLICY:
30-day money-back guarantee on all purchases.
Refunds processed within 5-7 business days.
Original payment method is credited.
Shipping costs are non-refundable.

SHIPPING:
Standard shipping: 3-5 business days (free over $50)
Express shipping: 1-2 business days ($15)
International: 7-14 business days ($25)

ACCOUNT DELETION:
Users can delete accounts from Settings > Privacy > Delete Account.
Requires email confirmation.
Data is permanently deleted within 30 days.
Order history retained for legal compliance.

BUSINESS HOURS:
Monday-Friday: 9 AM - 6 PM EST
Saturday: 10 AM - 4 PM EST
Sunday: Closed
"""

# ========== GENERATION FUNCTION ==========

def generate_test_cases(documentation: str, num_cases: int = 20, category: str = "customer_support"):
    """
    Use GPT-4 to generate test cases from documentation
    """
    
    prompt = f"""
You are creating test cases for an LLM evaluation dataset.

Given this documentation:
{documentation}

Generate {num_cases} diverse test cases in the following JSON format:

[
  {{
    "input": "user question or request",
    "expected_output": "ideal response based on documentation",
    "difficulty": "easy|medium|hard",
    "subcategory": "specific topic"
  }}
]

Requirements:
- Mix of easy (60%), medium (30%), hard (10%) questions
- Easy: Simple factual questions with clear answers in docs
- Medium: Multi-step questions requiring combining info
- Hard: Complex scenarios with edge cases or multiple requirements
- Expected outputs should be specific and actionable
- Cover all topics in the documentation

Return ONLY the JSON array, no other text.
"""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a test case generation expert."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7  # Some creativity for diversity
    )
    
    result = response.choices[0].message.content
    
    # Parse JSON (remove markdown code blocks if present)
    result = result.replace("```json", "").replace("```", "").strip()
    test_cases = json.loads(result)
    
    # Convert to Golden objects
    dataset = EvaluationDataset()
    for case in test_cases:
        dataset.add_golden(Golden(
            input=case["input"],
            expected_output=case["expected_output"],
            additional_metadata={
                "difficulty": case.get("difficulty", "medium"),
                "category": category,
                "subcategory": case.get("subcategory", "general")
            }
        ))
    
    return dataset

# ========== GENERATE CASES ==========

print("Generating test cases using GPT-4...")
print("This will take about 20-30 seconds...\n")

generated_dataset = generate_test_cases(DOCUMENTATION, num_cases=20)

print(f"✓ Generated {len(generated_dataset.goldens)} test cases")

# ========== PRINT SAMPLE CASES ==========

print("\n" + "="*60)
print("SAMPLE GENERATED TEST CASES:")
print("="*60)

for i, golden in enumerate(generated_dataset.goldens[:5]):  # Show first 5
    print(f"\nTest Case {i+1}:")
    print(f"Input: {golden.input}")
    print(f"Expected: {golden.expected_output}")
    print(f"Difficulty: {golden.additional_metadata['difficulty']}")
    print(f"Subcategory: {golden.additional_metadata['subcategory']}")

# ========== ANALYZE DATASET ==========

print("\n" + "="*60)
print("DATASET ANALYSIS:")
print("="*60)

difficulties = {}
subcategories = {}

for g in generated_dataset.goldens:
    diff = g.additional_metadata.get("difficulty", "unknown")
    subcat = g.additional_metadata.get("subcategory", "unknown")
    
    difficulties[diff] = difficulties.get(diff, 0) + 1
    subcategories[subcat] = subcategories.get(subcat, 0) + 1

print("\nBy Difficulty:")
for diff, count in difficulties.items():
    percentage = (count / len(generated_dataset.goldens)) * 100
    print(f"  {diff}: {count} ({percentage:.0f}%)")

print("\nBy Subcategory:")
for subcat, count in sorted(subcategories.items()):
    print(f"  {subcat}: {count}")

# ========== SAVE DATASET ==========

dataset_dict = {
    "goldens": [
        {
            "input": g.input,
            "expected_output": g.expected_output,
            "metadata": g.additional_metadata
        }
        for g in generated_dataset.goldens
    ]
}

with open("day2_synthetic_cases.json", "w") as f:
    json.dump(dataset_dict, f, indent=2)

print(f"\n✓ Saved to day2_synthetic_cases.json")

# ========== EXPERIMENT: API DOCS ==========

print("\n" + "="*60)
print("EXPERIMENT: Generating from API Documentation")
print("="*60)

API_DOCS = """
Authentication API:

POST /auth/login
- Requires: email, password
- Returns: JWT token (expires in 24h)
- Rate limit: 5 attempts per minute

POST /auth/refresh
- Requires: refresh_token
- Returns: new JWT token
- Refresh tokens expire in 30 days

GET /auth/user
- Requires: Authorization header with JWT
- Returns: user profile data
"""

api_dataset = generate_test_cases(API_DOCS, num_cases=15, category="api_docs")

print(f"\n✓ Generated {len(api_dataset.goldens)} API test cases")

# Show sample API test cases
print("\nSample API Test Cases:")
for i, golden in enumerate(api_dataset.goldens[:3]):
    print(f"\n{i+1}. {golden.input}")
    print(f"   Expected: {golden.expected_output}")
    print(f"   Difficulty: {golden.additional_metadata['difficulty']}")


# Save API dataset
api_dataset_dict = {
    "goldens": [
        {
            "input": g.input,
            "expected_output": g.expected_output,
            "metadata": g.additional_metadata
        }
        for g in api_dataset.goldens
    ]
}

with open("day2_api_cases.json", "w") as f:
    json.dump(api_dataset_dict, f, indent=2)

print(f"\n✓ Saved API cases to day2_api_cases.json")

    
