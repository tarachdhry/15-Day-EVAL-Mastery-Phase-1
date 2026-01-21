# day5/metrics_definition.py
"""
Exercise 5.1:STRATEGIC METRICS DEFINITION
As a PM, you need to balance multiple success criteria:
- Accuracy (correct information)
- Empathy (appropriate tone for upset customers)
- Routing (escalate complex issues)
- Safety (no harmful/inappropriate responses)
- Efficiency (answer quickly without unnecessary verbosity)
"""

from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase
from deepeval import evaluate
import os

# Set your API key
os.environ['OPENAI_API_KEY'] = ''

class CustomerSupportMetrics:
    """
    PM PERSPECTIVE: Each metric represents a stakeholder concern
    - Accuracy: Engineering/Product quality bar
    - Empathy: Customer Success team requirement
    - Routing: Operations efficiency
    - Safety: Legal/Compliance requirement
    - Efficiency: Cost/UX balance
    """
    
    def __init__(self):
        # KEY PM DECISION: What are the minimum acceptable scores?
        # These thresholds come from stakeholder discussions
        self.thresholds = {
            'accuracy': 0.8,      # 80% factually correct
            'empathy': 0.7,       # 70% empathetic (lower bar, harder to measure)
            'routing': 0.85,      # 85% correct escalation decisions
            'safety': 0.95,       # 95% safe (very high bar for legal)
            'efficiency': 0.6     # 60% concise (allowing for thorough explanations)
        }
        
        # PM INSIGHT: Weights reflect business priorities
        # If your company prioritizes trust over speed, increase safety/accuracy weights
        self.weights = {
            'accuracy': 0.3,    # Most important
            'empathy': 0.2,     # Important for customer satisfaction
            'routing': 0.2,     # Important for operational efficiency
            'safety': 0.25,     # Critical for risk management
            'efficiency': 0.05  # Nice to have
        }
    
    def calculate_composite_score(self, scores):
        """
        PM DECISION: How do you combine multiple dimensions?
        
        Options:
        1. Weighted average (used here - balances all factors)
        2. Minimum threshold (all must pass - very strict)
        3. Critical + average (safety must pass, others averaged)
        
        We're using weighted average with safety override
        """
        # Safety override: If safety fails, entire evaluation fails
        if scores.get('safety', 1.0) < self.thresholds['safety']:
            return 0.0  # Automatic failure
        
        # Calculate weighted average for other metrics
        weighted_sum = sum(
            scores.get(metric, 0) * weight 
            for metric, weight in self.weights.items()
        )
        
        return weighted_sum
    
    def get_pass_fail_decision(self, scores):
        """
        PM PERSPECTIVE: What's the ship/no-ship decision?
        
        This is what gates your deployment in CI/CD
        """
        composite = self.calculate_composite_score(scores)
        
        # Check if individual critical metrics pass
        critical_pass = (
            scores.get('safety', 0) >= self.thresholds['safety'] and
            scores.get('accuracy', 0) >= self.thresholds['accuracy']
        )
        
        # Overall score must also be reasonable
        overall_pass = composite >= 0.75
        
        return {
            'decision': 'PASS' if (critical_pass and overall_pass) else 'FAIL',
            'composite_score': composite,
            'individual_scores': scores,
            'failing_metrics': [
                metric for metric, threshold in self.thresholds.items()
                if scores.get(metric, 0) < threshold
            ]
        }

# Example usage showing PM decision-making
if __name__ == "__main__":
    metrics = CustomerSupportMetrics()
    
    # Scenario 1: High accuracy but low empathy (engineering bias)
    scores_1 = {
        'accuracy': 0.95,
        'empathy': 0.5,   # Too robotic
        'routing': 0.9,
        'safety': 0.98,
        'efficiency': 0.7
    }
    
    result_1 = metrics.get_pass_fail_decision(scores_1)
    print("Scenario 1 - Technically correct but unfriendly:")
    print(f"  Decision: {result_1['decision']}")
    print(f"  Composite Score: {result_1['composite_score']:.2f}")
    print(f"  Failing Metrics: {result_1['failing_metrics']}")
    print()
    
    # Scenario 2: Good balance
    scores_2 = {
        'accuracy': 0.85,
        'empathy': 0.75,
        'routing': 0.88,
        'safety': 0.96,
        'efficiency': 0.65
    }
    
    result_2 = metrics.get_pass_fail_decision(scores_2)
    print("Scenario 2 - Balanced performance:")
    print(f"  Decision: {result_2['decision']}")
    print(f"  Composite Score: {result_2['composite_score']:.2f}")
    print(f"  Failing Metrics: {result_2['failing_metrics']}")
    print()
    
    # Scenario 3: Safety failure (automatic fail)
    scores_3 = {
        'accuracy': 0.95,
        'empathy': 0.85,
        'routing': 0.92,
        'safety': 0.89,  # Below 0.95 threshold
        'efficiency': 0.75
    }
    
    result_3 = metrics.get_pass_fail_decision(scores_3)
    print("Scenario 3 - Safety failure overrides everything:")
    print(f"  Decision: {result_3['decision']}")
    print(f"  Composite Score: {result_3['composite_score']:.2f}")
    print(f"  Failing Metrics: {result_3['failing_metrics']}")
