# File: run_evaluation.py
"""
Orchestrates full evaluation and generates comprehensive reports
Runs all tests from golden dataset and saves detailed results
"""

import json
import os
from datetime import datetime
from rag_system import StripeRAG # Your RAG system
from stripe_rag_evaluator import StripeRAGEvaluator

def run_evaluation():
    """
    Main evaluation runner
    
    PROCESS:
    1. Initialize RAG system
    2. Initialize evaluator with golden dataset
    3. Run all evaluations
    4. Calculate aggregate metrics
    5. Save detailed results
    6. Print summary
    """
    
    print("="*70)
    print("STRIPE RAG EVALUATION")
    print("="*70)
    
    # 1. Initialize RAG system
    print("\n📦 Initializing RAG system...")
    # Note: You'll need to load Stripe docs instead of QuickCart
    # For now, using existing RAG system as-is
    rag = StripeRAG()  # TODO: Create StripeRAG class or load Stripe docs
    
    # 2. Initialize evaluator
    print("\n📋 Loading golden dataset...")
    evaluator = StripeRAGEvaluator(
        rag_system=rag,
        golden_dataset_path="stripe_golden_final.json"
    )
    
    # 3. Run full evaluation
    print("\n🔬 Running evaluation...")
    results = evaluator.run_full_evaluation()
    
    # 4. Calculate aggregate metrics
    print("\n📊 Calculating aggregate metrics...")
    aggregates = calculate_aggregate_metrics(results)
    
    # 5. Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"evaluation_results_{timestamp}.json"
    
    output = {
        "results": results,
        "aggregates": aggregates,
        "timestamp": timestamp
    }
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    # 6. Print summary
    print_summary(aggregates)
    
    return output

def calculate_aggregate_metrics(results):
    """
    Calculate aggregate statistics across all tests
    
    METRICS:
    - Overall pass rate
    - Pass rate by difficulty
    - Pass rate by category
    - Pass rate by failure mode
    - Average retrieval metrics
    - Average answer quality
    """
    
    single_turn = results["single_turn_results"]
    multiturn = results["multiturn_results"]
    
    # Overall pass rates
    single_turn_pass = sum(1 for r in single_turn if r["overall_pass"])
    single_turn_total = len(single_turn)
    single_turn_pass_rate = single_turn_pass / single_turn_total if single_turn_total > 0 else 0
    
    multiturn_pass = sum(1 for r in multiturn if r["overall_pass"])
    multiturn_total = len(multiturn)
    multiturn_pass_rate = multiturn_pass / multiturn_total if multiturn_total > 0 else 0
    
    # Pass rate by difficulty
    by_difficulty = {}
    for diff in ["easy", "medium", "hard"]:
        tests = [r for r in single_turn if r["difficulty"] == diff]
        passed = sum(1 for r in tests if r["overall_pass"])
        by_difficulty[diff] = {
            "total": len(tests),
            "passed": passed,
            "pass_rate": passed / len(tests) if tests else 0
        }
    
    # Pass rate by category
    by_category = {}
    all_tests = single_turn + [{"category": m["category"], "overall_pass": m["overall_pass"]} 
                                for m in multiturn]
    
    for test in all_tests:
        cat = test["category"]
        if cat not in by_category:
            by_category[cat] = {"total": 0, "passed": 0}
        by_category[cat]["total"] += 1
        if test["overall_pass"]:
            by_category[cat]["passed"] += 1
    
    for cat in by_category:
        total = by_category[cat]["total"]
        passed = by_category[cat]["passed"]
        by_category[cat]["pass_rate"] = passed / total if total > 0 else 0
    
    # Pass rate by failure mode
    by_failure_mode = {}
    for test in single_turn:
        mode = test["failure_mode"]
        if mode not in by_failure_mode:
            by_failure_mode[mode] = {"total": 0, "passed": 0}
        by_failure_mode[mode]["total"] += 1
        if test["overall_pass"]:
            by_failure_mode[mode]["passed"] += 1
    
    for mode in by_failure_mode:
        total = by_failure_mode[mode]["total"]
        passed = by_failure_mode[mode]["passed"]
        by_failure_mode[mode]["pass_rate"] = passed / total if total > 0 else 0
    
    # Average retrieval metrics (single-turn only)
    avg_precision = sum(r["retrieval_metrics"]["precision_at_k"] for r in single_turn) / len(single_turn)
    avg_recall = sum(r["retrieval_metrics"]["recall_at_k"] for r in single_turn) / len(single_turn)
    avg_mrr = sum(r["retrieval_metrics"]["mrr"] for r in single_turn) / len(single_turn)
    avg_similarity = sum(r["retrieval_metrics"]["top_similarity"] for r in single_turn) / len(single_turn)
    
    # Average answer quality
    avg_semantic_sim = sum(r["answer_metrics"]["semantic_similarity"] for r in single_turn) / len(single_turn)
    avg_answer_length = sum(r["answer_metrics"]["length"] for r in single_turn) / len(single_turn)
    
    # Failure analysis
    retrieval_failures = [r for r in single_turn if not r["retrieval_pass"]]
    answer_failures = [r for r in single_turn if not r["answer_pass"]]
    
    return {
        "overall": {
            "single_turn_pass_rate": single_turn_pass_rate,
            "single_turn_passed": single_turn_pass,
            "single_turn_total": single_turn_total,
            "multiturn_pass_rate": multiturn_pass_rate,
            "multiturn_passed": multiturn_pass,
            "multiturn_total": multiturn_total
        },
        "by_difficulty": by_difficulty,
        "by_category": by_category,
        "by_failure_mode": by_failure_mode,
        "retrieval_metrics": {
            "avg_precision": avg_precision,
            "avg_recall": avg_recall,
            "avg_mrr": avg_mrr,
            "avg_top_similarity": avg_similarity
        },
        "answer_metrics": {
            "avg_semantic_similarity": avg_semantic_sim,
            "avg_answer_length": avg_answer_length
        },
        "failure_analysis": {
            "retrieval_failures_count": len(retrieval_failures),
            "answer_failures_count": len(answer_failures),
            "retrieval_failure_ids": [r["test_id"] for r in retrieval_failures],
            "answer_failure_ids": [r["test_id"] for r in answer_failures]
        }
    }

def print_summary(aggregates):
    """Print human-readable summary"""
    
    print("\n" + "="*70)
    print("EVALUATION SUMMARY")
    print("="*70)
    
    overall = aggregates["overall"]
    
    # Overall results
    print(f"\n📊 OVERALL RESULTS:")
    print(f"  Single-turn: {overall['single_turn_passed']}/{overall['single_turn_total']} "
          f"({overall['single_turn_pass_rate']*100:.1f}%)")
    print(f"  Multi-turn:  {overall['multiturn_passed']}/{overall['multiturn_total']} "
          f"({overall['multiturn_pass_rate']*100:.1f}%)")
    
    # By difficulty
    print(f"\n📈 BY DIFFICULTY:")
    for diff in ["easy", "medium", "hard"]:
        stats = aggregates["by_difficulty"][diff]
        print(f"  {diff.capitalize():8} {stats['passed']}/{stats['total']} "
              f"({stats['pass_rate']*100:.1f}%)")
    
    # By category (top 5)
    print(f"\n📁 BY CATEGORY (Top 5):")
    by_cat = sorted(aggregates["by_category"].items(), 
                    key=lambda x: x[1]["pass_rate"])
    for cat, stats in by_cat[:5]:
        print(f"  {cat:20} {stats['passed']}/{stats['total']} "
              f"({stats['pass_rate']*100:.1f}%)")
    
    # Retrieval metrics
    ret = aggregates["retrieval_metrics"]
    print(f"\n🔍 RETRIEVAL QUALITY:")
    print(f"  Precision@K:    {ret['avg_precision']:.3f}")
    print(f"  Recall@K:       {ret['avg_recall']:.3f}")
    print(f"  MRR:            {ret['avg_mrr']:.3f}")
    print(f"  Avg Similarity: {ret['avg_top_similarity']:.3f}")
    
    # Answer metrics
    ans = aggregates["answer_metrics"]
    print(f"\n💬 ANSWER QUALITY:")
    print(f"  Semantic Similarity: {ans['avg_semantic_similarity']:.3f}")
    print(f"  Avg Length:          {ans['avg_answer_length']:.0f} chars")
    
    # Failures
    fail = aggregates["failure_analysis"]
    print(f"\n❌ FAILURES:")
    print(f"  Retrieval failures: {fail['retrieval_failures_count']}")
    print(f"  Answer failures:    {fail['answer_failures_count']}")
    
    if fail["retrieval_failures_count"] > 0:
        print(f"\n  Failed retrieval tests:")
        for test_id in fail["retrieval_failure_ids"][:5]:
            print(f"    - {test_id}")
        if fail["retrieval_failures_count"] > 5:
            print(f"    ... and {fail['retrieval_failures_count'] - 5} more")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if overall["single_turn_pass_rate"] < 0.80:
        print(f"  ⚠️  Pass rate below 80% - investigate failures before production")
    
    if ret["avg_precision"] < 0.70:
        print(f"  ⚠️  Low precision - retrieving too many irrelevant docs")
    
    if ret["avg_recall"] < 0.70:
        print(f"  ⚠️  Low recall - missing relevant docs, consider increasing top_k")
    
    if ans["avg_semantic_similarity"] < 0.70:
        print(f"  ⚠️  Low answer quality - review generation prompts")
    
    # By failure mode (show worst 3)
    print(f"\n🔍 WORST PERFORMING FAILURE MODES:")
    by_mode = sorted(aggregates["by_failure_mode"].items(),
                     key=lambda x: x[1]["pass_rate"])
    for mode, stats in by_mode[:3]:
        print(f"  {mode:25} {stats['passed']}/{stats['total']} "
              f"({stats['pass_rate']*100:.1f}%)")

if __name__ == "__main__":
    results = run_evaluation()
    
    print("\n" + "="*70)
    print("✅ EVALUATION COMPLETE")
    print("="*70)
    print("\nNext steps:")
    print("1. Review failed tests in detail")
    print("2. Categorize failures (retrieval vs answer)")
    print("3. Implement fixes for top failure modes")
    print("4. Re-run evaluation to measure improvement")
