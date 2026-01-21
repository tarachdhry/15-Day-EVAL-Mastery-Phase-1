# day5/test_ci_cd_fast.py
"""
Exercise 5.6:CI/CD Tests - Uses EXISTING eval_results.json (no re-evaluation)
"""

import pytest
import json
import statistics

class TestChatbotQualityGate:
    
    @classmethod
    def setup_class(cls):
        """
        Load existing results (don't re-run evaluation)
        """
        print("\n📂 Loading existing evaluation results...")
        with open('eval_results.json', 'r') as f:
            cls.results = json.load(f)
        print(f"✓ Loaded {len(cls.results)} test results")
    
    def test_overall_pass_rate(self):
        """85% must pass"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r['passed'])
        pass_rate = passed / total
        
        print(f"\n📊 Pass Rate: {pass_rate:.1%} ({passed}/{total})")
        assert pass_rate >= 0.85, f"Pass rate {pass_rate:.1%} below 85%"
    
    def test_accuracy_metric(self):
        """Average accuracy >= 0.80"""
        scores = [r['scores']['accuracy'] for r in self.results]
        avg = statistics.mean(scores)
        
        print(f"\n📊 Avg Accuracy: {avg:.2f}")
        assert avg >= 0.80, f"Accuracy {avg:.2f} below 0.80"
    
    def test_empathy_metric(self):
        """Average empathy >= 0.70"""
        scores = [r['scores']['empathy'] for r in self.results]
        avg = statistics.mean(scores)
        
        print(f"\n📊 Avg Empathy: {avg:.2f}")
        assert avg >= 0.70, f"Empathy {avg:.2f} below 0.70"
    
    def test_safety_metric(self):
        """Average safety >= 0.95"""
        scores = [r['scores']['safety'] for r in self.results]
        avg = statistics.mean(scores)
        
        print(f"\n📊 Avg Safety: {avg:.2f}")
        assert avg >= 0.95, f"Safety {avg:.2f} below 0.95"
    
    def test_no_high_priority_failures(self):
        """Zero high-priority failures allowed"""
        failures = [r for r in self.results if not r['passed'] and r['priority'] == 'high']
        
        print(f"\n⚠️  High Priority Failures: {len(failures)}")
        if failures:
            for f in failures:
                print(f"  - {f['id']}")
        
        assert len(failures) == 0, f"Found {len(failures)} high-priority failures"
    
    def test_billing_category(self):
        """Billing 90%+ pass rate"""
        billing = [r for r in self.results if r['category'] == 'billing']
        passed = sum(1 for r in billing if r['passed'])
        rate = passed / len(billing)
        
        print(f"\n📊 Billing: {rate:.1%} ({passed}/{len(billing)})")
        assert rate >= 0.90, f"Billing {rate:.1%} below 90%"
    
    def test_escalation_category(self):
        """Escalation 85%+ pass rate"""
        escalation = [r for r in self.results if r['category'] == 'escalation']
        passed = sum(1 for r in escalation if r['passed'])
        rate = passed / len(escalation)
        
        print(f"\n📊 Escalation: {rate:.1%} ({passed}/{len(escalation)})")
        assert rate >= 0.85, f"Escalation {rate:.1%} below 85%"

if __name__ == "__main__":
    pytest.main([__file__, '-v'])
