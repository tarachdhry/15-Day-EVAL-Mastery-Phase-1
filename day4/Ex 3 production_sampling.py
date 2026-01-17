"""
Exercise 4.3: Production Sampling & Data Flywheel
Learn from real production traffic to improve your evals
"""

import json
import random
from datetime import datetime
from collections import defaultdict

# ============================================================================
# PRODUCTION LOG SIMULATOR
# ============================================================================

class ProductionLogger:
    """
    Simulates logging production requests
    In real system, this would capture actual user interactions
    """
    
    def __init__(self, log_file="production_logs.json"):
        self.log_file = log_file
    
    def log_request(self, user_input, llm_response, metadata=None):
        """
        Log a production request-response pair
        
        In real system, this happens automatically on every user interaction
        """
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "llm_response": llm_response,
            "metadata": metadata or {}
        }
        
        # Append to log file
        try:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
        except FileNotFoundError:
            logs = []
        
        logs.append(log_entry)
        
        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=2)


class ProductionSampler:
    """
    Sample production requests for evaluation
    Can't evaluate everything (too expensive), so sample strategically
    """
    
    def __init__(self, log_file="production_logs.json"):
        self.log_file = log_file
    
    def load_logs(self):
        """Load production logs"""
        try:
            with open(self.log_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def random_sample(self, sample_rate=0.1):
        """
        Strategy 1: Random sampling
        Sample X% of all requests randomly
        
        Use when: You want unbiased view of overall quality
        """
        logs = self.load_logs()
        sample_size = int(len(logs) * sample_rate)
        
        sample = random.sample(logs, min(sample_size, len(logs)))
        
        print(f"📊 Random Sample: {len(sample)}/{len(logs)} requests ({sample_rate*100:.0f}%)")
        return sample
    
    def failure_biased_sample(self, budget=20):
        """
        Strategy 2: Failure-biased sampling
        Sample requests that likely failed (short responses, errors, etc.)
        
        Use when: You want to find problems quickly
        """
        logs = self.load_logs()
        
        # Score each log by "failure likelihood"
        scored_logs = []
        for log in logs:
            failure_score = 0
            
            response = log['llm_response']
            
            # Heuristics for potential failures:
            if len(response) < 50:
                failure_score += 3  # Very short response
            
            if "I don't know" in response or "I'm not sure" in response:
                failure_score += 2  # Uncertainty
            
            if "error" in response.lower() or "sorry" in response.lower():
                failure_score += 1  # Apologetic
            
            if len(response) > 500:
                failure_score += 1  # Too verbose
            
            scored_logs.append((failure_score, log))
        
        # Sort by failure score (highest first)
        scored_logs.sort(reverse=True, key=lambda x: x[0])
        
        # Take top N
        sample = [log for score, log in scored_logs[:budget]]
        
        print(f"🎯 Failure-Biased Sample: {len(sample)} highest-risk requests")
        return sample
    
    def edge_case_sample(self, budget=20):
        """
        Strategy 3: Edge case sampling
        Sample unusual/rare requests
        
        Use when: You want to test robustness
        """
        logs = self.load_logs()
        
        # Find edge cases by looking at input characteristics
        edge_cases = []
        
        for log in logs:
            user_input = log['user_input']
            
            # Edge case heuristics:
            is_edge = False
            
            if len(user_input) < 10:  # Very short
                is_edge = True
            
            if len(user_input) > 200:  # Very long
                is_edge = True
            
            if user_input.isupper():  # ALL CAPS (angry user)
                is_edge = True
            
            if "???" in user_input or "!!!" in user_input:  # Multiple punctuation
                is_edge = True
            
            if is_edge:
                edge_cases.append(log)
        
        # Random sample from edge cases
        sample = random.sample(edge_cases, min(budget, len(edge_cases)))
        
        print(f"🔍 Edge Case Sample: {len(sample)} unusual requests")
        return sample
    
    def diverse_sample(self, budget=20):
        """
        Strategy 4: Diversity sampling
        Sample requests covering different topics/categories
        
        Use when: You want broad coverage
        """
        logs = self.load_logs()
        
        # Group by topic (simplified - in real system, use embeddings)
        topics = defaultdict(list)
        
        keywords = {
            "shipping": ["package", "delivery", "tracking", "shipped"],
            "account": ["password", "login", "account", "sign in"],
            "billing": ["refund", "charge", "payment", "invoice"],
            "product": ["feature", "how to", "does it", "can I"],
            "complaint": ["frustrated", "angry", "disappointed", "terrible"]
        }
        
        for log in logs:
            text = (log['user_input'] + " " + log['llm_response']).lower()
            
            for topic, topic_keywords in keywords.items():
                if any(kw in text for kw in topic_keywords):
                    topics[topic].append(log)
                    break
            else:
                topics["other"].append(log)
        
        # Sample evenly from each topic
        sample = []
        per_topic = budget // len(topics)
        
        for topic, topic_logs in topics.items():
            sample.extend(random.sample(topic_logs, min(per_topic, len(topic_logs))))
        
        print(f"🌈 Diverse Sample: {len(sample)} requests across {len(topics)} topics")
        return sample


# ============================================================================
# DATA FLYWHEEL
# ============================================================================

class DataFlywheel:
    """
    Data Flywheel:
    Production → Sample → Evaluate → Find failures → Add to golden set → Deploy → Production
    """
    
    def __init__(self):
        self.sampler = ProductionSampler()
        self.new_test_cases = []
    
    def run_cycle(self):
        """Execute one flywheel cycle"""
        
        print("="*70)
        print("DATA FLYWHEEL CYCLE")
        print("="*70)
        
        # Step 1: Sample production
        print("\n[Step 1] Sampling production traffic...")
        sample = self.sampler.failure_biased_sample(budget=10)
        
        if not sample:
            print("No production data available")
            return
        
        # Step 2: Evaluate sample (simplified - just check for issues)
        print("\n[Step 2] Evaluating sampled requests...")
        failures = []
        
        for log in sample:
            # Simple failure detection
            response = log['llm_response']
            
            has_issue = (
                len(response) < 30 or
                "I don't know" in response or
                "error" in response.lower()
            )
            
            if has_issue:
                failures.append(log)
        
        print(f"   Found {len(failures)} potential failures")
        
        # Step 3: Convert failures to test cases
        print("\n[Step 3] Creating new test cases from failures...")
        
        for failure in failures[:5]:  # Top 5
            test_case = {
                "input": failure['user_input'],
                "actual_output": failure['llm_response'],
                "expected_output": "TODO: Define expected behavior",
                "source": "production",
                "timestamp": failure['timestamp']
            }
            
            self.new_test_cases.append(test_case)
            
            print(f"   ✓ New test case: '{failure['user_input'][:50]}...'")
        
        # Step 4: Add to golden dataset
        print("\n[Step 4] Adding to golden dataset...")
        self.save_to_golden_set()
        
        print(f"\n✓ Flywheel cycle complete!")
        print(f"  Added {len(self.new_test_cases)} new test cases")
        print("  Next: Review and define expected outputs, then re-run evals")
        print("="*70)
    
    def save_to_golden_set(self):
        """Save new test cases to golden dataset"""
        
        try:
            with open("golden_dataset_additions.json", 'r') as f:
                existing = json.load(f)
        except FileNotFoundError:
            existing = []
        
        existing.extend(self.new_test_cases)
        
        with open("golden_dataset_additions.json", 'w') as f:
            json.dump(existing, f, indent=2)


# ============================================================================
# DEMO
# ============================================================================

def generate_demo_production_data():
    """Create sample production logs for demonstration"""
    
    logger = ProductionLogger()
    
    # Simulate 50 production requests
    demo_requests = [
        # Good responses
        ("How do I track my order?", "I'd be happy to help you track your order! Please provide your order number and I'll look it up right away."),
        ("What's your return policy?", "We offer a 30-day money-back guarantee on all purchases. Returns are easy - just visit our returns portal and follow the steps."),
        
        # Problematic responses (will get sampled)
        ("My package is late!", "Check tracking."),  # Too short
        ("I'm very frustrated", "I don't know what to tell you."),  # Unhelpful
        ("Help!!!", "Error processing request."),  # Error
        ("REFUND MY MONEY NOW!!!", "Please calm down and contact support."),  # Poor handling of caps
        
        # Edge cases
        ("", "I didn't receive any input."),  # Empty input
        ("Can you help me with my order #12345 that I placed on October 1st but it still hasn't arrived and I'm getting worried because it was supposed to be a gift and now the event is tomorrow and I don't know what to do?", "Yes."),  # Long input, short response
        
        # More normal requests
        ("How do I reset my password?", "To reset your password, click 'Forgot Password' on the login page and follow the email instructions."),
        ("Do you ship internationally?", "Yes! We ship to over 100 countries. Shipping costs vary by location."),
    ]
    
    # Add more varied requests
    for i in range(40):
        demo_requests.append((
            f"Question {i} about product features",
            f"Here's a detailed answer about product features: {i}"
        ))
    
    for user_input, response in demo_requests:
        logger.log_request(user_input, response)
    
    print(f"✓ Generated {len(demo_requests)} production logs")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║              PRODUCTION SAMPLING & DATA FLYWHEEL                     ║
╚══════════════════════════════════════════════════════════════════════╝

Learn from real production traffic to continuously improve evals.

The Data Flywheel:
1. Sample production requests
2. Evaluate them
3. Find failures
4. Add to golden dataset
5. Improve system
6. Deploy
7. Repeat

This ensures your evals stay relevant as product evolves.
""")
    
    # Generate demo data
    print("\n" + "="*70)
    print("DEMO: Generating sample production data")
    print("="*70)
    generate_demo_production_data()
    
    # Show different sampling strategies
    print("\n" + "="*70)
    print("SAMPLING STRATEGIES")
    print("="*70)
    
    sampler = ProductionSampler()
    
    print("\nStrategy 1: Random Sample")
    print("-" * 70)
    random_sample = sampler.random_sample(sample_rate=0.2)
    print(f"Sample size: {len(random_sample)}")
    
    print("\nStrategy 2: Failure-Biased Sample")
    print("-" * 70)
    failure_sample = sampler.failure_biased_sample(budget=10)
    print(f"Sample size: {len(failure_sample)}")
    print("\nStrategy 2: Failure-Biased Sample")
print("-" * 70)
failure_sample = sampler.failure_biased_sample(budget=10)

# ADD THIS NEW SECTION:
print(f"\n📊 DETAILED FAILURE ANALYSIS:")
print("="*70)

logs = sampler.load_logs()
scored = []

for log in logs:
    response = log['llm_response']
    score = 0
    reasons = []
    
    if len(response) < 50:
        score += 3
        reasons.append("Very short response")
    if "I don't know" in response or "I'm not sure" in response:
        score += 2
        reasons.append("Shows uncertainty")
    if "error" in response.lower():
        score += 2
        reasons.append("Contains 'error'")
    if len(response) > 500:
        score += 1
        reasons.append("Too verbose")
    
    if score > 0:  # Only show flagged requests
        scored.append((score, log, reasons))

# Sort and show top 10
scored.sort(reverse=True, key=lambda x: x[0])

for i, (score, log, reasons) in enumerate(scored[:10], 1):
    print(f"\n#{i} - Failure Score: {score}")
    print(f"Input: {log['user_input'][:60]}")
    print(f"Response: {log['llm_response'][:60]}")
    print(f"Reasons: {', '.join(reasons)}")

    print("\n" + "="*70)
    print("\nTop 3 likely failures:")
    for i, log in enumerate(failure_sample[:3], 1):
        print(f"{i}. Input: '{log['user_input'][:50]}...'")
        print(f"   Response: '{log['llm_response'][:50]}...'")
    
    print("\nStrategy 3: Edge Case Sample")
    print("-" * 70)
    edge_sample = sampler.edge_case_sample(budget=10)
    print(f"Sample size: {len(edge_sample)}")
    
    print("\nStrategy 4: Diverse Sample")
    print("-" * 70)
    diverse_sample = sampler.diverse_sample(budget=20)
    print(f"Sample size: {len(diverse_sample)}")
    
    # Run data flywheel
    print("\n" + "="*70)
    print("DATA FLYWHEEL")
    print("="*70)
    
    flywheel = DataFlywheel()
    flywheel.run_cycle()
    
    print("\n" + "="*70)
    print("✓ Production sampling complete!")
    print("="*70)
    
    print("""
NEXT STEPS:
1. Review golden_dataset_additions.json
2. Define expected outputs for new test cases
3. Add to your test suite
4. Re-run CI/CD tests

This is how your evals evolve with your product!
""")
