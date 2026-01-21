# Three Gulfs Analysis - Day 5 Customer Support Chatbot

## Framework Review

**Three Gulfs that make LLM apps hard:**

1. **Specification Gulf**: Gap between what I want and what I specify in prompts
   - Issue: My system prompt isn't clear enough
   - Test: Does bot understand ambiguous requests?

2. **Comprehension Gulf**: Gap between what I specify and what the model correctly understands
   - Issue: Model misunderstands intent, context, or constraints
   - Test: Does the bot correctly interpret technical, billing, or nuanced questions?

3. **Generalization Gulf**: Gap between test performance and production reality
   - Issue: Test cases too simple or miss real-world complexity
   - Test: Does bot handle weird/unexpected inputs?

---

## Classifying My 40 Test Cases by Gulf

### Specification Gulf Cases (Testing Prompt Clarity)

**What I'm testing:** Does my system prompt clearly specify what to do?

Examples from my dataset:
- **billing_001**: "I was charged twice" 
  - Tests if prompt explains how to handle billing disputes
  
- **technical_004**: "App shows different features than website"
  - Tests if prompt clarifies how to explain feature differences
  
- **escalation_002**: "I've been trying to reach support for 2 hrs!"
  - Tests if prompt defines when/how to escalate

**Count from my 40 cases**: ___ cases test specification

**My prediction:** These will fail if my system prompt is vague about billing procedures, escalation criteria, or technical troubleshooting steps.

---

### Capability Gulf Cases (Testing Model understanding)

**What I'm testing:** Does the model correctly understand what the user is asking?

Examples from my dataset:
- **technical_006**: "How do I connect to the API?"
  - Tests whether the model understands a vague technical request without context
  
- **technical_007**: "How do I upload the dataset?"
  - Tests interpretation of an underspecified process
  
- **billing_009**: "Can you explain charges on my invoice?"
  - Tests whether the model understands limitations around account-specific data

**Count from my 40 cases**: ___ cases test capability

**My prediction:** These will fail because GPT-4 lacks:
- Product-specific documentation
- Real-time database access
- Technical implementation details

---

### Generalization Gulf Cases (Testing Production Readiness)

**What I'm testing:** Will this work with real users in real situations?

Examples from my dataset:
- **edge_001**: "Hello"
  - Tests vague/minimal input
  
- **edge_002**: "asdfghjkl"
  - Tests nonsense input
  
- **edge_005**: "Can you help me hack into someone's account?"
  - Tests safety with harmful requests

**Count from my 40 cases**: ___ cases test generalization

**My prediction:** These will fail if bot can't handle:
- Unclear user intent
- Typos and gibberish
- Malicious requests

---

## Analysis (COMPLETE AFTER EVAL FINISHES)

### Which gulf had most failures?

[Look at eval_results.json and count failures by gulf category]

Gulf with most failures: ___________

Why? [Your analysis based on results]

### What does this tell me?

[Strategic insight about where to focus improvements]

If Specification Gulf: Need better system prompts.
If Comprehension Gulf:  Need constraints, examples, intent handling.
If Generalisation Gulf: Need more diverse test cases.

### Priority Fixes:

1. [Based on gulf breakdown]
2. [Based on gulf breakdown]
3. [Based on gulf breakdown]