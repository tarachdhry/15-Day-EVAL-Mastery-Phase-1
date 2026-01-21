# day5/cost_tracker.py
"""
Exercise 5.7:Track evaluation costs and stay within budget
"""

import json
from datetime import datetime
from dataclasses import dataclass
from typing import List
import statistics

@dataclass
class EvalCost:
    """Single evaluation run cost"""
    timestamp: str
    test_cases: int
    api_calls: int
    estimated_cost: float
    pass_rate: float
    notes: str

class CostTracker:
    """
    Track and manage evaluation costs
    
    WHAT THIS DOES:
    - Records cost of each eval run
    - Calculates monthly spend
    - Alerts if over budget
    - Shows cost trends
    """
    
    def __init__(self, monthly_budget: float = 500.0):
        self.monthly_budget = monthly_budget
        self.cost_history = []
        self.load_history()
    
    def load_history(self):
        """Load previous cost data"""
        try:
            with open('cost_history.json', 'r') as f:
                data = json.load(f)
                self.cost_history = [EvalCost(**item) for item in data]
        except FileNotFoundError:
            self.cost_history = []
    
    def save_history(self):
        """Save cost data"""
        data = [
            {
                'timestamp': c.timestamp,
                'test_cases': c.test_cases,
                'api_calls': c.api_calls,
                'estimated_cost': c.estimated_cost,
                'pass_rate': c.pass_rate,
                'notes': c.notes
            }
            for c in self.cost_history
        ]
        
        with open('cost_history.json', 'w') as f:
            json.dump(data, f, indent=2)
    
    def calculate_eval_cost(self, test_cases: int, metrics_per_case: int = 3) -> float:
        """
        Estimate cost of an evaluation run
        
        CALCULATION:
        - Each test case = 1 chatbot call + N metric calls
        - GPT-4: ~$0.03 per 1K tokens
        - Average eval: ~500 tokens = ~$0.015 per call
        
        Args:
            test_cases: Number of test cases
            metrics_per_case: Number of metrics (accuracy, empathy, safety = 3)
        
        Returns:
            Estimated cost in dollars
        """
        # API calls = chatbot response + metric evaluations
        api_calls = test_cases * (1 + metrics_per_case)
        
        # Cost per call (conservative estimate)
        cost_per_call = 0.015
        
        total_cost = api_calls * cost_per_call
        
        return total_cost
    
    def record_eval(self, test_cases: int, pass_rate: float, notes: str = ""):
        """
        Record an evaluation run
        
        WHAT THIS DOES:
        - Calculates cost
        - Saves to history
        - Checks if over budget
        """
        cost = self.calculate_eval_cost(test_cases)
        api_calls = test_cases * 4  # 1 chatbot + 3 metrics
        
        eval_cost = EvalCost(
            timestamp=datetime.now().isoformat(),
            test_cases=test_cases,
            api_calls=api_calls,
            estimated_cost=cost,
            pass_rate=pass_rate,
            notes=notes
        )
        
        self.cost_history.append(eval_cost)
        self.save_history()
        
        print(f"\n💰 Eval Cost Recorded:")
        print(f"   Test cases: {test_cases}")
        print(f"   API calls: {api_calls}")
        print(f"   Cost: ${cost:.2f}")
        print(f"   Pass rate: {pass_rate:.1%}")
        
        # Check budget
        monthly_spend = self.get_monthly_spend()
        remaining = self.monthly_budget - monthly_spend
        
        if remaining < 0:
            print(f"\n⚠️  OVER BUDGET! ${abs(remaining):.2f} over limit")
        elif remaining < 50:
            print(f"\n⚠️  LOW BUDGET! ${remaining:.2f} remaining")
        else:
            print(f"\n✓ Budget OK: ${remaining:.2f} remaining this month")
    
    def get_monthly_spend(self) -> float:
        """
        Calculate spending for current month
        
        WHAT THIS DOES:
        - Filters cost history to current month
        - Sums up costs
        """
        current_month = datetime.now().strftime("%Y-%m")
        
        monthly_costs = [
            c.estimated_cost for c in self.cost_history
            if c.timestamp.startswith(current_month)
        ]
        
        return sum(monthly_costs)
    
    def get_cost_report(self) -> dict:
        """
        Generate cost analysis report
        
        RETURNS:
        - Monthly spend
        - Cost per test case
        - Most expensive runs
        - Cost trend
        """
        if not self.cost_history:
            return {"error": "No cost data available"}
        
        monthly_spend = self.get_monthly_spend()
        
        # Average cost per test case
        avg_cost_per_case = statistics.mean(
            c.estimated_cost / c.test_cases for c in self.cost_history
        )
        
        # Most expensive runs
        expensive_runs = sorted(
            self.cost_history,
            key=lambda x: x.estimated_cost,
            reverse=True
        )[:5]
        
        # Cost trend (last 10 runs)
        recent_costs = [c.estimated_cost for c in self.cost_history[-10:]]
        
        return {
            'monthly_spend': monthly_spend,
            'monthly_budget': self.monthly_budget,
            'budget_remaining': self.monthly_budget - monthly_spend,
            'percent_used': (monthly_spend / self.monthly_budget) * 100,
            'total_runs': len(self.cost_history),
            'avg_cost_per_case': avg_cost_per_case,
            'expensive_runs': [
                {
                    'timestamp': r.timestamp,
                    'cost': r.estimated_cost,
                    'test_cases': r.test_cases
                }
                for r in expensive_runs
            ],
            'cost_trend': recent_costs
        }
    
    def print_cost_report(self):
        """Print formatted cost report"""
        report = self.get_cost_report()
        
        if 'error' in report:
            print(report['error'])
            return
        
        print("\n" + "=" * 80)
        print("COST ANALYSIS REPORT")
        print("=" * 80)
        
        print(f"\n💰 Monthly Budget: ${report['monthly_budget']:.2f}")
        print(f"   Spent: ${report['monthly_spend']:.2f} ({report['percent_used']:.1f}%)")
        print(f"   Remaining: ${report['budget_remaining']:.2f}")
        
        print(f"\n📊 Usage Statistics:")
        print(f"   Total eval runs: {report['total_runs']}")
        print(f"   Avg cost per test case: ${report['avg_cost_per_case']:.4f}")
        
        print(f"\n💸 Most Expensive Runs:")
        for i, run in enumerate(report['expensive_runs'], 1):
            print(f"   {i}. ${run['cost']:.2f} - {run['test_cases']} cases - {run['timestamp'][:10]}")
        
        print(f"\n📈 Cost Trend (last 10 runs):")
        for i, cost in enumerate(report['cost_trend'], 1):
            print(f"   Run {i}: ${cost:.2f}")

# Example usage
if __name__ == "__main__":
    tracker = CostTracker(monthly_budget=500.0)
    
    # Record your Day 5 evaluation
    tracker.record_eval(
        test_cases=40,
        pass_rate=0.90,
        notes="Day 5 - v3 balanced prompt"
    )
    
    # Show cost report
    tracker.print_cost_report()
