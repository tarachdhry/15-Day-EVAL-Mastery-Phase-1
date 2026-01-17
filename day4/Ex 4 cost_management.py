"""
Exercise 4.4: Cost Management & ROI
Track eval costs and optimize spending
"""

import json
import time
from datetime import datetime
from collections import defaultdict

# ============================================================================
# COST TRACKER
# ============================================================================

class CostTracker:
    """
    Track API costs for eval runs
    """
    
    # Pricing (per 1K tokens) - Update with current pricing
    PRICING = {
        "gpt-4": {
            "input": 0.03,   # $0.03 per 1K input tokens
            "output": 0.06   # $0.06 per 1K output tokens
        },
        "gpt-3.5-turbo": {
            "input": 0.001,
            "output": 0.002
        }
    }
    
    def __init__(self, log_file="cost_tracking.json"):
        self.log_file = log_file
        self.current_run_costs = []
    
    def log_api_call(self, model, input_tokens, output_tokens, metric_name):
        """
        Log a single API call cost
        """
        
        pricing = self.PRICING.get(model, self.PRICING["gpt-4"])
        
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        total_cost = input_cost + output_cost
        
        call_data = {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "metric": metric_name,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": total_cost
        }
        
        self.current_run_costs.append(call_data)
        
        return total_cost
    
    def save_run(self, run_metadata):
        """
        Save completed run with all costs
        """
        
        total_cost = sum(call["cost"] for call in self.current_run_costs)
        total_calls = len(self.current_run_costs)
        
        run_summary = {
            "timestamp": datetime.now().isoformat(),
            "metadata": run_metadata,
            "total_calls": total_calls,
            "total_cost": total_cost,
            "avg_cost_per_call": total_cost / total_calls if total_calls > 0 else 0,
            "calls": self.current_run_costs
        }
        
        # Load existing
        try:
            with open(self.log_file, 'r') as f:
                history = json.load(f)
        except FileNotFoundError:
            history = []
        
        history.append(run_summary)
        
        with open(self.log_file, 'w') as f:
            json.dump(history, f, indent=2)
        
        # Reset for next run
        self.current_run_costs = []
        
        return run_summary
    
    def get_history(self):
        """Load cost history"""
        try:
            with open(self.log_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []


# ============================================================================
# COST OPTIMIZER
# ============================================================================

class CostOptimizer:
    """
    Strategies to reduce eval costs
    """
    
    def __init__(self, tracker: CostTracker):
        self.tracker = tracker
    
    def analyze_by_metric(self):
        """
        Find which metrics are most expensive
        """
        
        history = self.tracker.get_history()
        
        if not history:
            print("No cost data available")
            return
        
        # Aggregate by metric
        metric_costs = defaultdict(lambda: {"total_cost": 0, "call_count": 0})
        
        for run in history:
            for call in run["calls"]:
                metric = call["metric"]
                metric_costs[metric]["total_cost"] += call["cost"]
                metric_costs[metric]["call_count"] += 1
        
        print("="*70)
        print("COST ANALYSIS BY METRIC")
        print("="*70)
        
        # Sort by total cost
        sorted_metrics = sorted(
            metric_costs.items(),
            key=lambda x: x[1]["total_cost"],
            reverse=True
        )
        
        for metric, data in sorted_metrics:
            avg_cost = data["total_cost"] / data["call_count"]
            print(f"\n{metric}:")
            print(f"  Total cost: ${data['total_cost']:.4f}")
            print(f"  Calls: {data['call_count']}")
            print(f"  Avg per call: ${avg_cost:.4f}")
        
        print("\n" + "="*70)
    
    def recommend_optimizations(self):
        """
        Suggest cost reduction strategies
        """
        
        history = self.tracker.get_history()
        
        if not history:
            return
        
        print("\n" + "="*70)
        print("OPTIMIZATION RECOMMENDATIONS")
        print("="*70)
        
        # Calculate metrics
        total_cost = sum(run["total_cost"] for run in history)
        total_calls = sum(run["total_calls"] for run in history)
        avg_per_run = total_cost / len(history) if history else 0
        
        print(f"\n📊 Current Stats:")
        print(f"  Total spent: ${total_cost:.2f}")
        print(f"  Total API calls: {total_calls:,}")
        print(f"  Avg cost per run: ${avg_per_run:.2f}")
        
        # Recommendations
        print(f"\n💡 Optimization Strategies:\n")
        
        # 1. Model routing
        potential_savings_routing = total_cost * 0.60  # 60% savings possible
        print(f"1. MODEL ROUTING (Potential: ${potential_savings_routing:.2f} saved)")
        print(f"   • Use GPT-3.5-turbo for simple metrics (empathy, clarity)")
        print(f"   • Reserve GPT-4 for complex metrics (accuracy, hallucination)")
        print(f"   • Estimated savings: 60%")
        
        # 2. Caching
        potential_savings_cache = total_cost * 0.30  # 30% cache hit rate
        print(f"\n2. CACHING (Potential: ${potential_savings_cache:.2f} saved)")
        print(f"   • Cache identical test cases")
        print(f"   • Cache embedding-similar queries")
        print(f"   • Estimated savings: 30% with typical cache hit rate")
        
        # 3. Batch processing
        potential_savings_batch = total_cost * 0.15  # 15% from batching
        print(f"\n3. BATCH PROCESSING (Potential: ${potential_savings_batch:.2f} saved)")
        print(f"   • Combine multiple evals in one prompt")
        print(f"   • Reduce overhead tokens")
        print(f"   • Estimated savings: 15%")
        
        # 4. Sampling
        if total_calls > 100:
            potential_savings_sample = total_cost * 0.50  # Run half as many
            print(f"\n4. SMART SAMPLING (Potential: ${potential_savings_sample:.2f} saved)")
            print(f"   • Don't eval every test case every time")
            print(f"   • Rotate through golden set")
            print(f"   • Focus on recently changed areas")
            print(f"   • Estimated savings: 50%")
        
        # Total potential
        total_potential = sum([
            potential_savings_routing,
            potential_savings_cache,
            potential_savings_batch,
            potential_savings_sample if total_calls > 100 else 0
        ])
        
        print(f"\n{'─'*70}")
        print(f"TOTAL POTENTIAL SAVINGS: ${total_potential:.2f} ({total_potential/total_cost*100:.0f}%)")
        print(f"Optimized monthly cost: ${(total_cost - total_potential)*30:.2f}")
        print('─'*70)


# ============================================================================
# ROI CALCULATOR
# ============================================================================

class ROICalculator:
    """
    Calculate return on investment for eval system
    """
    
    def calculate_roi(
        self,
        monthly_eval_cost: float,
        bugs_prevented_per_month: int,
        cost_per_bug: float
    ):
        """
        Calculate ROI of eval system
        
        Args:
            monthly_eval_cost: What you spend on evals
            bugs_prevented_per_month: Bugs caught before production
            cost_per_bug: Cost of a bug reaching customers
        """
        
        print("="*70)
        print("ROI ANALYSIS")
        print("="*70)
        
        # Calculate value
        monthly_value = bugs_prevented_per_month * cost_per_bug
        monthly_profit = monthly_value - monthly_eval_cost
        roi_percentage = (monthly_profit / monthly_eval_cost) * 100 if monthly_eval_cost > 0 else 0
        
        print(f"\n💰 COSTS:")
        print(f"  Eval system cost: ${monthly_eval_cost:,.2f}/month")
        
        print(f"\n✅ VALUE CREATED:")
        print(f"  Bugs prevented: {bugs_prevented_per_month}/month")
        print(f"  Cost per bug: ${cost_per_bug:,.2f}")
        print(f"  Total value: ${monthly_value:,.2f}/month")
        
        print(f"\n📈 ROI:")
        print(f"  Net profit: ${monthly_profit:,.2f}/month")
        print(f"  ROI: {roi_percentage:,.0f}%")
        
        # Interpretation
        print(f"\n💡 INTERPRETATION:")
        if roi_percentage > 500:
            print(f"  🟢 EXCELLENT - Every $1 spent returns ${roi_percentage/100:.0f}")
            print(f"     Invest more in evals!")
        elif roi_percentage > 200:
            print(f"  🟢 GOOD - Strong positive return")
            print(f"     Current spend is justified")
        elif roi_percentage > 0:
            print(f"  🟡 POSITIVE - Breaking even or slight profit")
            print(f"     Consider optimizing costs")
        else:
            print(f"  🔴 NEGATIVE - Costing more than value")
            print(f"     Need to reduce costs or improve bug detection")
        
        print("="*70)
        
        return {
            "monthly_cost": monthly_eval_cost,
            "monthly_value": monthly_value,
            "monthly_profit": monthly_profit,
            "roi_percentage": roi_percentage
        }


# ============================================================================
# DEMO
# ============================================================================

def simulate_eval_runs():
    """
    Simulate eval runs with cost tracking
    """
    
    tracker = CostTracker()
    
    print("="*70)
    print("SIMULATING EVAL RUNS WITH COST TRACKING")
    print("="*70)
    
    # Simulate 5 eval runs
    for run_num in range(1, 6):
        print(f"\n🔄 Run #{run_num}")
        
        # Simulate different metrics with different costs
        metrics = [
            ("Accuracy", 500, 200),      # Heavy metric
            ("Empathy", 300, 150),       # Medium metric
            ("Clarity", 200, 100),       # Light metric
            ("Hallucination", 600, 250), # Heaviest metric
            ("Citation", 400, 180)       # Medium-heavy
        ]
        
        # Simulate 10 test cases
        for test_num in range(10):
            for metric_name, avg_input, avg_output in metrics:
                # Add some randomness
                import random
                input_tokens = int(avg_input * random.uniform(0.8, 1.2))
                output_tokens = int(avg_output * random.uniform(0.8, 1.2))
                
                cost = tracker.log_api_call(
                    model="gpt-4",
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    metric_name=metric_name
                )
        
        # Save run
        summary = tracker.save_run({
            "run_number": run_num,
            "test_cases": 10,
            "metrics": 5
        })
        
        print(f"  Cost: ${summary['total_cost']:.2f} ({summary['total_calls']} API calls)")
    
    print(f"\n✓ Completed 5 eval runs")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                    COST MANAGEMENT & ROI                             ║
╚══════════════════════════════════════════════════════════════════════╝

Track, optimize, and justify eval costs.

Key insights:
- Which metrics cost the most?
- How to reduce costs by 60%+?
- What's the ROI of your eval system?
""")
    
    # Simulate runs
    simulate_eval_runs()
    
    # Cost analysis
    tracker = CostTracker()
    optimizer = CostOptimizer(tracker)
    
    print("\n")
    optimizer.analyze_by_metric()
    optimizer.recommend_optimizations()
    
    # ROI calculation
    print("\n")
    roi_calc = ROICalculator()
    
    # Example: You spend $150/month on evals, catch 10 bugs, each bug costs $2000
    roi_calc.calculate_roi(
        monthly_eval_cost=150,
        bugs_prevented_per_month=10,
        cost_per_bug=2000
    )
    
    print("\n" + "="*70)
    print("✓ Cost management complete!")
    print("="*70)
    
    print("""
KEY TAKEAWAYS:
1. Track costs per metric to find optimization targets
2. Use model routing (GPT-3.5 for simple, GPT-4 for complex)
3. Implement caching for repeated test cases
4. Calculate ROI to justify eval investment to leadership

🎉 DAY 4 COMPLETE!
""")
