# day5/production_sampler.py
"""
Production Sampling Strategies

PM DECISIONS:
- How much traffic to sample?
- What to prioritize?
- How to stay within budget?
"""

import random
from typing import List, Dict
from datetime import datetime

class ProductionSampler:
    """
    Smart sampling for production traffic
    
    GOAL: Get quality visibility without evaluating everything
    """
    
    def __init__(self, monthly_budget: float = 500.0):
        self.monthly_budget = monthly_budget
        self.cost_per_eval = 0.06  # $0.06 per evaluation
        
        # Calculate daily eval budget
        self.daily_budget = monthly_budget / 30
        self.daily_eval_limit = int(self.daily_budget / self.cost_per_eval)
        
        print(f"\n💰 Sampling Budget:")
        print(f"   Monthly: ${monthly_budget}")
        print(f"   Daily: ${self.daily_budget:.2f}")
        print(f"   Daily eval limit: {self.daily_eval_limit} evaluations")
    
    def strategy_1_random_sampling(self, daily_requests: int) -> dict:
        """
        STRATEGY 1: Random Sampling
        
        WHAT: Sample X% of all traffic randomly
        
        PROS:
        - Unbiased
        - Simple to implement
        
        CONS:
        - Might miss important cases
        - Treats all requests equally
        
        PM DECISION: What % to sample?
        """
        # Calculate sample rate to stay within budget
        if daily_requests <= self.daily_eval_limit:
            sample_rate = 1.0  # Evaluate everything
        else:
            sample_rate = self.daily_eval_limit / daily_requests
        
        sampled = int(daily_requests * sample_rate)
        cost = sampled * self.cost_per_eval
        
        return {
            'strategy': 'Random Sampling',
            'sample_rate': sample_rate,
            'daily_requests': daily_requests,
            'sampled': sampled,
            'skipped': daily_requests - sampled,
            'daily_cost': cost,
            'monthly_cost': cost * 30,
            'coverage': sample_rate * 100
        }
    
    def strategy_2_priority_sampling(self, requests: List[Dict]) -> dict:
        """
        STRATEGY 2: Priority-Based Sampling
        
        WHAT: Sample based on importance
        - 100% of high-priority categories (billing, escalation)
        - 50% of medium-priority
        - 10% of low-priority
        
        PROS:
        - Focus on what matters
        - Better ROI
        
        CONS:
        - Blind spots in low-priority areas
        - More complex
        
        PM DECISION: How to prioritize?
        """
        high_priority = ['billing', 'escalation', 'security']
        medium_priority = ['technical', 'account']
        # low_priority = everything else
        
        sampled = []
        
        for req in requests:
            category = req.get('category', 'unknown')
            
            if category in high_priority:
                # Always sample high-priority
                sampled.append(req)
            elif category in medium_priority:
                # Sample 50% of medium
                if random.random() < 0.5:
                    sampled.append(req)
            else:
                # Sample 10% of low-priority
                if random.random() < 0.1:
                    sampled.append(req)
        
        cost = len(sampled) * self.cost_per_eval
        
        return {
            'strategy': 'Priority-Based Sampling',
            'total_requests': len(requests),
            'sampled': len(sampled),
            'skipped': len(requests) - len(sampled),
            'daily_cost': cost,
            'monthly_cost': cost * 30,
            'coverage': (len(sampled) / len(requests)) * 100
        }
    
    def strategy_3_failure_focused(self, requests: List[Dict]) -> dict:
        """
        STRATEGY 3: Failure-Focused Sampling
        
        WHAT: Sample cases likely to fail
        - Angry customers (sentiment detection)
        - Complex questions (length > 100 chars)
        - New users (no history)
        - Edge of confidence threshold
        
        PROS:
        - Catches problems faster
        - Efficient use of budget
        
        CONS:
        - Misses "happy path" issues
        - Needs prediction logic
        
        PM DECISION: What signals indicate likely failure?
        """
        sampled = []
        
        for req in requests:
            # Check failure indicators
            should_sample = False
            
            # Angry customer signals
            if any(word in req.get('text', '').lower() for word in ['ridiculous', 'terrible', 'sue', 'complaint']):
                should_sample = True
            
            # Complex question
            if len(req.get('text', '')) > 100:
                should_sample = True
            
            # New user
            if req.get('user_history_count', 0) < 3:
                should_sample = True
            
            # Random sample of rest (10%)
            if not should_sample and random.random() < 0.1:
                should_sample = True
            
            if should_sample:
                sampled.append(req)
        
        cost = len(sampled) * self.cost_per_eval
        
        return {
            'strategy': 'Failure-Focused Sampling',
            'total_requests': len(requests),
            'sampled': len(sampled),
            'skipped': len(requests) - len(sampled),
            'daily_cost': cost,
            'monthly_cost': cost * 30,
            'coverage': (len(sampled) / len(requests)) * 100
        }
    
    def strategy_4_adaptive_sampling(self, requests: List[Dict], recent_pass_rate: float) -> dict:
        """
        STRATEGY 4: Adaptive Sampling
        
        WHAT: Adjust sample rate based on quality trends
        - Quality dropping? Sample more (investigate)
        - Quality stable? Sample less (save money)
        
        PROS:
        - Dynamic response to issues
        - Efficient in steady state
        
        CONS:
        - Complex logic
        - Lag in detection
        
        PM DECISION: How to balance reactivity vs cost?
        """
        # Adjust sample rate based on recent quality
        if recent_pass_rate >= 0.95:
            # Quality excellent: reduce sampling
            sample_rate = 0.05  # 5%
            reason = "Quality excellent (≥95%), reducing sampling"
        elif recent_pass_rate >= 0.85:
            # Quality good: normal sampling
            sample_rate = 0.10  # 10%
            reason = "Quality good (85-95%), normal sampling"
        elif recent_pass_rate >= 0.75:
            # Quality concerning: increase sampling
            sample_rate = 0.25  # 25%
            reason = "Quality concerning (75-85%), increasing sampling"
        else:
            # Quality poor: maximum sampling
            sample_rate = 0.50  # 50%
            reason = "Quality poor (<75%), maximum sampling for investigation"
        
        sampled = int(len(requests) * sample_rate)
        cost = sampled * self.cost_per_eval
        
        return {
            'strategy': 'Adaptive Sampling',
            'total_requests': len(requests),
            'sampled': sampled,
            'skipped': len(requests) - sampled,
            'sample_rate': sample_rate,
            'daily_cost': cost,
            'monthly_cost': cost * 30,
            'coverage': sample_rate * 100,
            'reason': reason,
            'recent_pass_rate': recent_pass_rate
        }
    
    def compare_strategies(self, daily_requests: int = 1000):
        """
        PM TOOL: Compare all strategies
        """
        print("\n" + "=" * 80)
        print("SAMPLING STRATEGY COMPARISON")
        print(f"Daily Requests: {daily_requests}")
        print(f"Budget Limit: ${self.daily_budget:.2f}/day")
        print("=" * 80)
        
        # Strategy 1: Random
        random_result = self.strategy_1_random_sampling(daily_requests)
        print(f"\n📊 {random_result['strategy']}")
        print(f"   Sample rate: {random_result['sample_rate']*100:.1f}%")
        print(f"   Evaluations: {random_result['sampled']}/{daily_requests}")
        print(f"   Cost: ${random_result['daily_cost']:.2f}/day (${random_result['monthly_cost']:.2f}/month)")
        
        # Strategy 2: Priority
        # Simulate requests with categories
        sim_requests = [
            {'category': random.choice(['billing', 'technical', 'how-to', 'escalation'])}
            for _ in range(daily_requests)
        ]
        priority_result = self.strategy_2_priority_sampling(sim_requests)
        print(f"\n📊 {priority_result['strategy']}")
        print(f"   Evaluations: {priority_result['sampled']}/{daily_requests}")
        print(f"   Cost: ${priority_result['daily_cost']:.2f}/day (${priority_result['monthly_cost']:.2f}/month)")
        
        # Strategy 4: Adaptive (assuming good quality)
        adaptive_result = self.strategy_4_adaptive_sampling(sim_requests, recent_pass_rate=0.90)
        print(f"\n📊 {adaptive_result['strategy']}")
        print(f"   Sample rate: {adaptive_result['sample_rate']*100:.1f}%")
        print(f"   Evaluations: {adaptive_result['sampled']}/{daily_requests}")
        print(f"   Cost: ${adaptive_result['daily_cost']:.2f}/day (${adaptive_result['monthly_cost']:.2f}/month)")
        print(f"   Reason: {adaptive_result['reason']}")
        
        print("\n" + "=" * 80)
        print("💡 PM RECOMMENDATION:")
        print("   Start with: Priority-Based (focus on revenue/risk)")
        print("   Evolve to: Adaptive (dynamic based on quality)")
        print("=" * 80)

# Run comparison
if __name__ == "__main__":
    sampler = ProductionSampler(monthly_budget=500.0)
    sampler.compare_strategies(daily_requests=1000)
