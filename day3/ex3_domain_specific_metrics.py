"""
Exercise 3.3: Domain-Specific Metrics
Build metrics for RAG and Agent architectures
"""

import openai
import json
from deepeval.test_case import LLMTestCase
from deepeval.metrics import BaseMetric

client = openai.OpenAI(api_key="")


# ============================================================================
# RAG-SPECIFIC METRICS
# ============================================================================

class GroundednessMetric(BaseMetric):
    """
    Checks if response claims are supported by retrieved context
    Critical for RAG: Prevents hallucination
    """
    
    def __init__(self, threshold: float = 0.8):
        self.threshold = threshold
        self.score = 0
        self.reason = ""
        self.unsupported_claims = []
    
    def measure(self, test_case: LLMTestCase):
        """Check if ALL claims in response are in context"""
        
        if not test_case.retrieval_context:
            self.score = 0
            self.reason = "No retrieval context provided"
            return self.score
        
        context = "\n".join(test_case.retrieval_context)
        response = test_case.actual_output
        
        prompt = f"""You are evaluating if a response is grounded in source documents.

RETRIEVED CONTEXT:
{context}

RESPONSE TO EVALUATE:
{response}

TASK:
1. Extract all factual claims from the response
2. For each claim, check if it's supported by the context
3. List any claims NOT found in context

Return JSON:
{{
  "total_claims": <number>,
  "supported_claims": <number>,
  "unsupported_claims": ["claim 1", "claim 2"],
  "groundedness_score": <0-10>
}}

CRITICAL: A claim is unsupported if the EXACT information isn't in context.
Don't assume or infer - only check what's explicitly stated."""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        
        result = response.choices[0].message.content.replace("```json", "").replace("```", "").strip()
        
        try:
            parsed = json.loads(result)
            self.score = parsed["groundedness_score"] / 10
            self.unsupported_claims = parsed["unsupported_claims"]
            
            total = parsed["total_claims"]
            supported = parsed["supported_claims"]
            
            self.reason = f"""Groundedness Analysis:
- Total claims: {total}
- Supported by context: {supported}
- Unsupported claims: {len(self.unsupported_claims)}

Unsupported: {', '.join(self.unsupported_claims) if self.unsupported_claims else 'None'}

Score: {self.score:.2f}"""
        except:
            self.score = 0.5
            self.reason = "Parsing error"
        
        return self.score
    
    def is_successful(self):
        return self.score >= self.threshold
    
    @property
    def __name__(self):
        return "Groundedness"


class CitationQualityMetric(BaseMetric):
    """
    Checks if response includes proper citations
    Critical for RAG: Users need to verify claims
    """
    
    def __init__(self, threshold: float = 0.7):
        self.threshold = threshold
        self.score = 0
        self.reason = ""
    
    def measure(self, test_case: LLMTestCase):
        """Check citation quality"""
        
        response = test_case.actual_output
        context = test_case.retrieval_context or []
        
        prompt = f"""Evaluate the CITATION QUALITY of this response.

RESPONSE:
{response}

CRITERIA:
1. Are there citations? (mentions of sources, doc names, page numbers)
2. Are they accurate? (match the context provided)
3. Are they sufficient? (important claims have citations)
4. Are they useful? (user can verify claims)

Rate 0-10:
10: All claims cited, accurate, verifiable
7-9: Most claims cited, mostly accurate
4-6: Some citations, but incomplete
0-3: No citations or wrong citations

Return JSON:
{{
  "has_citations": true/false,
  "citation_accuracy": <0-10>,
  "citation_coverage": <0-10>,
  "score": <0-10>,
  "reasoning": "explanation"
}}"""

        response_obj = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        
        result = response_obj.choices[0].message.content.replace("```json", "").replace("```", "").strip()
        
        try:
            parsed = json.loads(result)
            self.score = parsed["score"] / 10
            self.reason = parsed["reasoning"]
        except:
            self.score = 0.5
            self.reason = "Parsing error"
        
        return self.score
    
    def is_successful(self):
        return self.score >= self.threshold
    
    @property
    def __name__(self):
        return "Citation Quality"


# ============================================================================
# AGENT-SPECIFIC METRICS
# ============================================================================

class ToolSelectionMetric(BaseMetric):
    """
    Checks if agent selected appropriate tools
    Critical for Agents: Wrong tools = wrong results
    """
    
    def __init__(self, threshold: float = 0.8):
        self.threshold = threshold
        self.score = 0
        self.reason = ""
    
    def measure(self, test_case: LLMTestCase):
        """Evaluate tool selection appropriateness"""
        
        # Extract tool usage from context or metadata
        # For demo, we'll check the actual_output mentions tools
        
        user_query = test_case.input
        tools_used = test_case.actual_output  # Assume this contains tool trace
        expected_tools = test_case.expected_output or "N/A"
        
        prompt = f"""Evaluate if the agent selected appropriate tools.

USER QUERY:
{user_query}

TOOLS AGENT USED:
{tools_used}

EXPECTED TOOLS (reference):
{expected_tools}

EVALUATION CRITERIA:
1. Did agent use necessary tools? (not skip required tools)
2. Did agent avoid unnecessary tools? (not use irrelevant tools)
3. Was the tool sequence logical?

Rate 0-10:
10: Perfect tool selection
7-9: Good, minor issues
4-6: Missing key tools or used wrong ones
0-3: Completely wrong tools

Return JSON:
{{
  "necessary_tools_used": true/false,
  "unnecessary_tools_avoided": true/false,
  "sequence_logical": true/false,
  "score": <0-10>,
  "reasoning": "explanation"
}}"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        
        result = response.choices[0].message.content.replace("```json", "").replace("```", "").strip()
        
        try:
            parsed = json.loads(result)
            self.score = parsed["score"] / 10
            self.reason = parsed["reasoning"]
        except:
            self.score = 0.5
            self.reason = "Parsing error"
        
        return self.score
    
    def is_successful(self):
        return self.score >= self.threshold
    
    @property
    def __name__(self):
        return "Tool Selection"


# ============================================================================
# TESTS
# ============================================================================

def test_groundedness():
    """Test RAG groundedness metric"""
    
    print("="*70)
    print("TEST 1: Groundedness (RAG)")
    print("="*70)
    
    # Case 1: Fully grounded
    test_case_1 = LLMTestCase(
        input="What's the refund policy?",
        actual_output="We offer a 30-day money-back guarantee. Returns are processed within 5-7 business days.",
        retrieval_context=[
            "Our refund policy: 30-day money-back guarantee on all purchases.",
            "Refund processing time: 5-7 business days after receiving returned item."
        ]
    )
    
    metric = GroundednessMetric(threshold=0.8)
    score = metric.measure(test_case_1)
    
    print(f"\n✓ Case 1: Fully Grounded Response")
    print(f"Score: {score:.2f} {'✓ PASS' if metric.is_successful() else '✗ FAIL'}")
    print(metric.reason)
    
    # Case 2: Hallucination
    test_case_2 = LLMTestCase(
        input="What's the refund policy?",
        actual_output="We offer a 30-day money-back guarantee with free return shipping. You'll also get a 10% discount on your next order.",
        retrieval_context=[
            "Our refund policy: 30-day money-back guarantee on all purchases.",
            "Refund processing time: 5-7 business days."
        ]
    )
    
    score = metric.measure(test_case_2)
    
    print(f"\n✗ Case 2: Contains Hallucinations")
    print(f"Score: {score:.2f} {'✓ PASS' if metric.is_successful() else '✗ FAIL'}")
    print(metric.reason)


def test_citations():
    """Test citation quality"""
    
    print("\n\n" + "="*70)
    print("TEST 2: Citation Quality (RAG)")
    print("="*70)
    
    # Good citations
    test_case_1 = LLMTestCase(
        input="When was the product launched?",
        actual_output="According to the Q2 2024 Report, the product launched on March 15, 2024 (page 3). The initial rollout covered 5 regions (see Regional Strategy Doc, section 2.1).",
        retrieval_context=["Q2 2024 Report", "Regional Strategy Doc"]
    )
    
    metric = CitationQualityMetric(threshold=0.7)
    score = metric.measure(test_case_1)
    
    print(f"\n✓ Case 1: Good Citations")
    print(f"Score: {score:.2f} {'✓ PASS' if metric.is_successful() else '✗ FAIL'}")
    print(f"Reason: {metric.reason}")
    
    # No citations
    test_case_2 = LLMTestCase(
        input="When was the product launched?",
        actual_output="The product launched in March 2024 and rolled out to multiple regions.",
        retrieval_context=["Q2 2024 Report"]
    )
    
    score = metric.measure(test_case_2)
    
    print(f"\n✗ Case 2: Missing Citations")
    print(f"Score: {score:.2f} {'✓ PASS' if metric.is_successful() else '✗ FAIL'}")
    print(f"Reason: {metric.reason}")


def test_tool_selection():
    """Test agent tool selection"""
    
    print("\n\n" + "="*70)
    print("TEST 3: Tool Selection (Agents)")
    print("="*70)
    
    # Good tool selection
    test_case_1 = LLMTestCase(
        input="What's the weather in Paris and convert 20 EUR to USD?",
        actual_output="Tools used: weather_api(location='Paris'), currency_converter(from='EUR', to='USD', amount=20)",
        expected_output="Should use: weather_api, currency_converter"
    )
    
    metric = ToolSelectionMetric(threshold=0.8)
    score = metric.measure(test_case_1)
    
    print(f"\n✓ Case 1: Correct Tools")
    print(f"Score: {score:.2f} {'✓ PASS' if metric.is_successful() else '✗ FAIL'}")
    print(f"Reason: {metric.reason}")
    
    # Wrong tools
    test_case_2 = LLMTestCase(
        input="What's the weather in Paris?",
        actual_output="Tools used: calculator(2+2), web_search('Paris weather'), send_email()",
        expected_output="Should use: weather_api"
    )
    
    score = metric.measure(test_case_2)
    
    print(f"\n✗ Case 2: Wrong Tools")
    print(f"Score: {score:.2f} {'✓ PASS' if metric.is_successful() else '✗ FAIL'}")
    print(f"Reason: {metric.reason}")


if __name__ == "__main__":
    test_groundedness()
    test_citations()
    test_tool_selection()
    
    print("\n" + "="*70)
    print("✓ Domain-specific metrics complete!")
    print("="*70)
