"""
Exercise 4.2: Eval Monitoring Dashboard
Track eval performance over time to spot regressions
"""

import json
import os
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt

# ============================================================================
# LOGGING SYSTEM
# ============================================================================

class EvalLogger:
    """
    Logs eval results to track performance over time
    """
    
    def __init__(self, log_file="eval_history.json"):
        self.log_file = log_file
        
        # Create log file if doesn't exist
        if not os.path.exists(log_file):
            with open(log_file, 'w') as f:
                json.dump([], f)
    
    def log_run(self, run_data):
        """
        Log a test run
        
        run_data = {
            "timestamp": "2025-10-13 14:30:00",
            "commit_hash": "abc123",
            "total_tests": 11,
            "passed": 9,
            "failed": 2,
            "failures": [
                {"test": "empathy_test_data1", "score": 0.20, "reason": "..."},
                {"test": "empathy_test_data2", "score": 0.00, "reason": "..."}
            ],
            "metrics": {
                "accuracy": {"avg_score": 0.85, "pass_rate": 1.0},
                "empathy": {"avg_score": 0.58, "pass_rate": 0.6}
            }
        }
        """
        
        # Load existing logs
        with open(self.log_file, 'r') as f:
            logs = json.load(f)
        
        # Add new run
        logs.append(run_data)
        
        # Save back
        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=2)
        
        print(f"✓ Logged run to {self.log_file}")
    
    def get_history(self):
        """Get all historical runs"""
        with open(self.log_file, 'r') as f:
            return json.load(f)


# ============================================================================
# DASHBOARD
# ============================================================================

class EvalDashboard:
    """
    Visualize eval performance over time
    """
    
    def __init__(self, log_file="eval_history.json"):
        self.logger = EvalLogger(log_file)
        self.history = self.logger.get_history()
    
    def show_summary(self):
        """Show current status and recent trends"""
        
        if not self.history:
            print("No eval history yet. Run tests to generate data.")
            return
        
        latest = self.history[-1]
        
        print("="*70)
        print("EVAL MONITORING DASHBOARD")
        print("="*70)
        
        # Current status
        print(f"\n📊 LATEST RUN ({latest['timestamp']})")
        print(f"   Tests: {latest['passed']}/{latest['total_tests']} passed ({latest['passed']/latest['total_tests']*100:.1f}%)")
        
        if latest['failed'] > 0:
            print(f"\n   ❌ {latest['failed']} tests failed:")
            for failure in latest['failures'][:3]:  # Show top 3
                print(f"      • {failure['test']}: {failure['score']:.2f}")
        else:
            print("   ✓ All tests passed!")
        
        # Metric breakdown
        print(f"\n📈 METRIC SCORES:")
        for metric, data in latest['metrics'].items():
            status = "✓" if data['pass_rate'] >= 0.8 else "⚠️" if data['pass_rate'] >= 0.6 else "❌"
            print(f"   {status} {metric.capitalize()}: {data['avg_score']:.2f} (pass rate: {data['pass_rate']*100:.0f}%)")
        
        # Trend analysis
        if len(self.history) >= 2:
            print(f"\n📉 TREND (last 7 runs):")
            recent = self.history[-7:]
            
            for metric in latest['metrics'].keys():
                scores = [run['metrics'][metric]['avg_score'] for run in recent if metric in run['metrics']]
                if len(scores) >= 2:
                    trend = scores[-1] - scores[0]
                    arrow = "📈" if trend > 0.05 else "📉" if trend < -0.05 else "➡️"
                    print(f"   {arrow} {metric.capitalize()}: {trend:+.2f}")
        
        print("="*70)
    
    def plot_trends(self):
        """Generate charts showing performance over time"""
        
        if len(self.history) < 2:
            print("Need at least 2 runs to plot trends")
            return
        
        # Extract data
        timestamps = [run['timestamp'] for run in self.history]
        pass_rates = [run['passed'] / run['total_tests'] for run in self.history]
        
        # Metric scores over time
        metrics = {}
        for run in self.history:
            for metric, data in run['metrics'].items():
                if metric not in metrics:
                    metrics[metric] = []
                metrics[metric].append(data['avg_score'])
        
        # Create plots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Plot 1: Overall pass rate
        ax1.plot(range(len(timestamps)), pass_rates, marker='o', linewidth=2)
        ax1.axhline(y=0.8, color='r', linestyle='--', label='Target (80%)')
        ax1.set_title('Overall Test Pass Rate Over Time', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Run Number')
        ax1.set_ylabel('Pass Rate')
        ax1.set_ylim([0, 1.05])
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Plot 2: Metric scores
        for metric, scores in metrics.items():
            ax2.plot(range(len(scores)), scores, marker='o', label=metric.capitalize(), linewidth=2)
        
        ax2.axhline(y=0.7, color='r', linestyle='--', alpha=0.5, label='Threshold')
        ax2.set_title('Metric Scores Over Time', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Run Number')
        ax2.set_ylabel('Score')
        ax2.set_ylim([0, 1.05])
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        plt.tight_layout()
        plt.savefig('eval_trends.png', dpi=150, bbox_inches='tight')
        print("✓ Saved trends chart to eval_trends.png")
        plt.show()
    
    def identify_regressions(self):
        """Find when performance dropped significantly"""
        
        if len(self.history) < 2:
            print("Need at least 2 runs to detect regressions")
            return
        
        print("\n🔍 REGRESSION ANALYSIS")
        print("="*70)
        
        regressions = []
        
        for i in range(1, len(self.history)):
            prev = self.history[i-1]
            curr = self.history[i]
            
            # Check overall pass rate
            prev_rate = prev['passed'] / prev['total_tests']
            curr_rate = curr['passed'] / curr['total_tests']
            
            if curr_rate < prev_rate - 0.2:  # 20% drop
                regressions.append({
                    "run": i,
                    "timestamp": curr['timestamp'],
                    "type": "Overall",
                    "drop": f"{(prev_rate - curr_rate)*100:.1f}%",
                    "from": prev_rate,
                    "to": curr_rate
                })
            
            # Check individual metrics
            for metric in curr['metrics']:
                if metric in prev['metrics']:
                    prev_score = prev['metrics'][metric]['avg_score']
                    curr_score = curr['metrics'][metric]['avg_score']
                    
                    if curr_score < prev_score - 0.15:  # 0.15 drop
                        regressions.append({
                            "run": i,
                            "timestamp": curr['timestamp'],
                            "type": f"{metric.capitalize()}",
                            "drop": f"{(prev_score - curr_score):.2f}",
                            "from": prev_score,
                            "to": curr_score
                        })
        
        if regressions:
            print(f"Found {len(regressions)} regressions:\n")
            for reg in regressions:
                print(f"❌ Run #{reg['run']} ({reg['timestamp']})")
                print(f"   {reg['type']} dropped by {reg['drop']}: {reg['from']:.2f} → {reg['to']:.2f}\n")
        else:
            print("✓ No significant regressions detected")
        
        print("="*70)


# ============================================================================
# SIMULATE HISTORICAL DATA (for demo)
# ============================================================================

def generate_demo_data():
    """Create sample historical data for demonstration"""
    
    logger = EvalLogger()
    
    # Simulate 10 test runs over time
    base_date = datetime(2025, 10, 1)
    
    runs = [
        # Week 1: Good performance
        {"day": 1, "accuracy": 0.85, "empathy": 0.75, "passed": 10, "total": 11},
        {"day": 2, "accuracy": 0.87, "empathy": 0.78, "passed": 11, "total": 11},
        {"day": 3, "accuracy": 0.86, "empathy": 0.76, "passed": 10, "total": 11},
        
        # Week 2: Empathy drops (regression!)
        {"day": 8, "accuracy": 0.88, "empathy": 0.55, "passed": 7, "total": 11},
        {"day": 9, "accuracy": 0.85, "empathy": 0.52, "passed": 7, "total": 11},
        
        # Week 3: Fixed empathy
        {"day": 15, "accuracy": 0.87, "empathy": 0.80, "passed": 11, "total": 11},
        {"day": 16, "accuracy": 0.89, "empathy": 0.82, "passed": 11, "total": 11},
        
        # Latest: Current performance (from your actual run)
        {"day": 20, "accuracy": 0.90, "empathy": 0.60, "passed": 9, "total": 11},
    ]
    
    for run in runs:
        timestamp = (base_date.replace(day=run['day'])).strftime("%Y-%m-%d %H:%M:%S")
        
        run_data = {
            "timestamp": timestamp,
            "commit_hash": f"abc{run['day']}",
            "total_tests": run['total'],
            "passed": run['passed'],
            "failed": run['total'] - run['passed'],
            "failures": [],
            "metrics": {
                "accuracy": {
                    "avg_score": run['accuracy'],
                    "pass_rate": 1.0 if run['accuracy'] >= 0.7 else 0.8
                },
                "empathy": {
                    "avg_score": run['empathy'],
                    "pass_rate": run['passed'] / run['total']
                }
            }
        }
        
        logger.log_run(run_data)
    
    print("✓ Generated demo historical data")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                    EVAL MONITORING DASHBOARD                         ║
╚══════════════════════════════════════════════════════════════════════╝

This dashboard tracks eval performance over time.

DEMO MODE: Generating sample data to show functionality.
In production, this would use real test results from CI/CD.
""")
    
    # Generate demo data
    generate_demo_data()
    
    # Show dashboard
    dashboard = EvalDashboard()
    dashboard.show_summary()
    dashboard.identify_regressions()
    dashboard.plot_trends()
    
    print("\n" + "="*70)
    print("✓ Monitoring dashboard complete!")
    print("="*70)
