# File: evaluation_report.py
"""
Generate comprehensive HTML evaluation report with visualizations
Shows pass/fail breakdown, metrics, and detailed failure analysis
"""

import json
import sys
from datetime import datetime

def load_results(results_file):
    """Load evaluation results from JSON"""
    with open(results_file, 'r') as f:
        return json.load(f)

def generate_html_report(data, output_file="evaluation_report.html"):
    """
    Generate beautiful HTML report with:
    - Executive summary
    - Pass/fail breakdown by difficulty, category, failure mode
    - Retrieval metrics visualization
    - Answer quality metrics
    - Detailed failure analysis
    - Recommendations
    """
    
    results = data['results']
    aggregates = data['aggregates']
    timestamp = data['timestamp']
    
    # Extract metrics
    overall = aggregates['overall']
    by_diff = aggregates['by_difficulty']
    by_cat = aggregates['by_category']
    by_mode = aggregates['by_failure_mode']
    retrieval = aggregates['retrieval_metrics']
    answer = aggregates['answer_metrics']
    failures = aggregates['failure_analysis']
    
    # HTML template
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Stripe RAG Evaluation Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .summary {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .summary h2 {{
            margin-top: 0;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .metric-card h3 {{
            margin: 0 0 10px 0;
            font-size: 0.9em;
            color: #666;
            text-transform: uppercase;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        .metric-subtitle {{
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }}
        .pass {{ color: #22c55e; }}
        .fail {{ color: #ef4444; }}
        .warning {{ color: #f59e0b; }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }}
        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #666;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 30px;
            background: #e5e7eb;
            border-radius: 15px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #22c55e 0%, #16a34a 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            transition: width 0.3s ease;
        }}
        .progress-fill.low {{
            background: linear-gradient(90deg, #ef4444 0%, #dc2626 100%);
        }}
        .progress-fill.medium {{
            background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%);
        }}
        
        .recommendation {{
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }}
        .recommendation.critical {{
            background: #fee2e2;
            border-left-color: #ef4444;
        }}
        
        .failure-section {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .failure-item {{
            background: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid #ef4444;
        }}
        .failure-item h4 {{
            margin: 0 0 10px 0;
            color: #ef4444;
        }}
        .failure-detail {{
            font-size: 0.9em;
            color: #666;
            margin: 5px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔬 Stripe RAG Evaluation Report</h1>
        <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p>Dataset: {results['dataset_info']['name']} v{results['dataset_info']['version']}</p>
    </div>
    
    <!-- EXECUTIVE SUMMARY -->
    <div class="summary">
        <h2>📊 Executive Summary</h2>
        
        <div class="metric-grid">
            <div class="metric-card">
                <h3>Single-Turn Pass Rate</h3>
                <div class="metric-value {'pass' if overall['single_turn_pass_rate'] >= 0.8 else 'fail'}">
                    {overall['single_turn_pass_rate']*100:.1f}%
                </div>
                <div class="metric-subtitle">{overall['single_turn_passed']}/{overall['single_turn_total']} tests passed</div>
            </div>
            
            <div class="metric-card">
                <h3>Multi-Turn Pass Rate</h3>
                <div class="metric-value {'pass' if overall['multiturn_pass_rate'] >= 0.8 else 'fail'}">
                    {overall['multiturn_pass_rate']*100:.1f}%
                </div>
                <div class="metric-subtitle">{overall['multiturn_passed']}/{overall['multiturn_total']} conversations passed</div>
            </div>
            
            <div class="metric-card">
                <h3>Avg Precision@K</h3>
                <div class="metric-value {'pass' if retrieval['avg_precision'] >= 0.7 else 'fail'}">
                    {retrieval['avg_precision']:.3f}
                </div>
                <div class="metric-subtitle">Retrieval accuracy</div>
            </div>
            
            <div class="metric-card">
                <h3>Avg Semantic Similarity</h3>
                <div class="metric-value {'pass' if answer['avg_semantic_similarity'] >= 0.7 else 'fail'}">
                    {answer['avg_semantic_similarity']:.3f}
                </div>
                <div class="metric-subtitle">Answer quality</div>
            </div>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill {'low' if overall['single_turn_pass_rate'] < 0.5 else 'medium' if overall['single_turn_pass_rate'] < 0.8 else ''}" 
                 style="width: {overall['single_turn_pass_rate']*100}%">
                Overall: {overall['single_turn_pass_rate']*100:.1f}%
            </div>
        </div>
    </div>
    
    <!-- BY DIFFICULTY -->
    <div class="summary">
        <h2>📈 Performance by Difficulty</h2>
        <table>
            <tr>
                <th>Difficulty</th>
                <th>Passed</th>
                <th>Total</th>
                <th>Pass Rate</th>
                <th>Progress</th>
            </tr>
"""
    
    for diff in ['easy', 'medium', 'hard']:
        stats = by_diff[diff]
        pass_rate = stats['pass_rate'] * 100
        html += f"""
            <tr>
                <td><strong>{diff.capitalize()}</strong></td>
                <td>{stats['passed']}</td>
                <td>{stats['total']}</td>
                <td class="{'pass' if stats['pass_rate'] >= 0.8 else 'fail'}">{pass_rate:.1f}%</td>
                <td>
                    <div class="progress-bar" style="height: 20px;">
                        <div class="progress-fill {'low' if stats['pass_rate'] < 0.5 else 'medium' if stats['pass_rate'] < 0.8 else ''}" 
                             style="width: {pass_rate}%; font-size: 0.8em;">
                            {pass_rate:.0f}%
                        </div>
                    </div>
                </td>
            </tr>
"""
    
    html += """
        </table>
    </div>
    
    <!-- BY CATEGORY -->
    <div class="summary">
        <h2>📁 Performance by Category</h2>
        <table>
            <tr>
                <th>Category</th>
                <th>Passed</th>
                <th>Total</th>
                <th>Pass Rate</th>
            </tr>
"""
    
    # Sort categories by pass rate
    sorted_cats = sorted(by_cat.items(), key=lambda x: x[1]['pass_rate'])
    
    for cat, stats in sorted_cats:
        pass_rate = stats['pass_rate'] * 100
        html += f"""
            <tr>
                <td>{cat}</td>
                <td>{stats['passed']}</td>
                <td>{stats['total']}</td>
                <td class="{'pass' if stats['pass_rate'] >= 0.8 else 'warning' if stats['pass_rate'] >= 0.5 else 'fail'}">
                    {pass_rate:.1f}%
                </td>
            </tr>
"""
    
    html += """
        </table>
    </div>
    
    <!-- RETRIEVAL METRICS -->
    <div class="summary">
        <h2>🔍 Retrieval Quality Metrics</h2>
        <div class="metric-grid">
            <div class="metric-card">
                <h3>Precision@K</h3>
                <div class="metric-value">{:.3f}</div>
                <div class="metric-subtitle">Relevant docs / Retrieved docs</div>
            </div>
            <div class="metric-card">
                <h3>Recall@K</h3>
                <div class="metric-value">{:.3f}</div>
                <div class="metric-subtitle">Retrieved relevant / Total relevant</div>
            </div>
            <div class="metric-card">
                <h3>MRR</h3>
                <div class="metric-value">{:.3f}</div>
                <div class="metric-subtitle">Mean Reciprocal Rank</div>
            </div>
            <div class="metric-card">
                <h3>Avg Top Similarity</h3>
                <div class="metric-value">{:.3f}</div>
                <div class="metric-subtitle">Confidence score</div>
            </div>
        </div>
    </div>
    
    <!-- FAILURE ANALYSIS -->
    <div class="failure-section">
        <h2>❌ Failure Analysis</h2>
        
        <div class="metric-grid">
            <div class="metric-card">
                <h3>Retrieval Failures</h3>
                <div class="metric-value fail">{}</div>
                <div class="metric-subtitle">Tests with retrieval issues</div>
            </div>
            <div class="metric-card">
                <h3>Answer Failures</h3>
                <div class="metric-value fail">{}</div>
                <div class="metric-subtitle">Tests with answer quality issues</div>
            </div>
        </div>
        
        <h3>Failed Tests (Top 10):</h3>
""".format(
        retrieval['avg_precision'],
        retrieval['avg_recall'],
        retrieval['avg_mrr'],
        retrieval['avg_top_similarity'],
        failures['retrieval_failures_count'],
        failures['answer_failures_count']
    )
    
    # Show top 10 failed tests
    single_turn_results = results['single_turn_results']
    failed_tests = [r for r in single_turn_results if not r['overall_pass']][:10]
    
    for test in failed_tests:
        html += f"""
        <div class="failure-item">
            <h4>{test['test_id']} - {test['category']} ({test['difficulty']})</h4>
            <div class="failure-detail"><strong>Question:</strong> {test['question']}</div>
            <div class="failure-detail"><strong>Retrieval issues:</strong> {', '.join(test['retrieval_failures']) if test['retrieval_failures'] else 'None'}</div>
            <div class="failure-detail"><strong>Answer issues:</strong> {', '.join(test['answer_failures']) if test['answer_failures'] else 'None'}</div>
            <div class="failure-detail"><strong>Top similarity:</strong> {test['retrieval_metrics']['top_similarity']:.3f}</div>
        </div>
"""
    
    # Recommendations
    html += """
    </div>
    
    <!-- RECOMMENDATIONS -->
    <div class="summary">
        <h2>💡 Recommendations</h2>
"""
    
    # Generate recommendations based on metrics
    if overall['single_turn_pass_rate'] < 0.8:
        html += f"""
        <div class="recommendation critical">
            <strong>🚨 Critical:</strong> Pass rate ({overall['single_turn_pass_rate']*100:.1f}%) is below 80% threshold. 
            System is not production-ready. Investigate and fix failures before deployment.
        </div>
"""
    
    if retrieval['avg_precision'] < 0.7:
        html += f"""
        <div class="recommendation">
            <strong>⚠️ Low Precision ({retrieval['avg_precision']:.3f}):</strong> System is retrieving too many irrelevant documents. 
            Consider: improving embedding model, adding re-ranking, or increasing similarity threshold.
        </div>
"""
    
    if retrieval['avg_recall'] < 0.7:
        html += f"""
        <div class="recommendation">
            <strong>⚠️ Low Recall ({retrieval['avg_recall']:.3f}):</strong> System is missing relevant documents. 
            Consider: increasing top_k, using hybrid search (vector + keyword), or query expansion.
        </div>
"""
    
    if answer['avg_semantic_similarity'] < 0.7:
        html += f"""
        <div class="recommendation">
            <strong>⚠️ Low Answer Quality ({answer['avg_semantic_similarity']:.3f}):</strong> Generated answers don't match expected responses. 
            Consider: improving generation prompt, using better LLM model, or providing more context to generator.
        </div>
"""
    
    if retrieval['avg_top_similarity'] < 0.65:
        html += f"""
        <div class="recommendation critical">
            <strong>🚨 Low Confidence ({retrieval['avg_top_similarity']:.3f}):</strong> Top retrieved documents have low similarity scores. 
            This suggests embedding model isn't capturing semantic meaning well. Consider switching to a better embedding model.
        </div>
"""
    
    # Worst performing failure modes
    html += """
        <h3>Focus Areas (Worst Performing Failure Modes):</h3>
        <ul>
"""
    
    sorted_modes = sorted(by_mode.items(), key=lambda x: x[1]['pass_rate'])[:3]
    for mode, stats in sorted_modes:
        html += f"""
            <li><strong>{mode}</strong>: {stats['passed']}/{stats['total']} ({stats['pass_rate']*100:.1f}%) - 
            Prioritize fixing this failure type</li>
"""
    
    html += """
        </ul>
    </div>
    
    <div class="summary">
        <h2>🎯 Next Steps</h2>
        <ol>
            <li><strong>Detailed Failure Analysis:</strong> Run analyze_failures.py to see specific examples of what's breaking</li>
            <li><strong>Fix Retrieval:</strong> Focus on precision (too many irrelevant docs retrieved)</li>
            <li><strong>Improve Embeddings:</strong> Low similarity scores suggest embedding quality issues</li>
            <li><strong>Re-test:</strong> After fixes, re-run evaluation to measure improvement</li>
            <li><strong>Iterate:</strong> Continue until pass rate ≥ 80%</li>
        </ol>
    </div>
    
    <div style="text-align: center; color: #666; margin-top: 40px; padding: 20px;">
        <p>Generated by Stripe RAG Evaluation System</p>
        <p>Report timestamp: {}</p>
    </div>
    
</body>
</html>
""".format(timestamp)
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ HTML report saved to: {output_file}")
    return output_file

if __name__ == "__main__":
    # Load most recent results
    if len(sys.argv) > 1:
        results_file = sys.argv[1]
    else:
        # Find most recent results file
        import glob
        results_files = glob.glob("evaluation_results_*.json")
        if not results_files:
            print("❌ No evaluation results found. Run run_evaluation.py first.")
            sys.exit(1)
        results_file = sorted(results_files)[-1]
    
    print(f"📊 Loading results from: {results_file}")
    data = load_results(results_file)
    
    print("🎨 Generating HTML report...")
    output_file = generate_html_report(data)
    
    print("\n" + "="*70)
    print("✅ REPORT GENERATED")
    print("="*70)
    print(f"\nOpen in browser: {output_file}")
    print("\nThe report includes:")
    print("  ✅ Executive summary with key metrics")
    print("  ✅ Pass/fail breakdown by difficulty, category")
    print("  ✅ Retrieval quality metrics (Precision, Recall, MRR)")
    print("  ✅ Answer quality metrics")
    print("  ✅ Detailed failure analysis")
    print("  ✅ Actionable recommendations")
