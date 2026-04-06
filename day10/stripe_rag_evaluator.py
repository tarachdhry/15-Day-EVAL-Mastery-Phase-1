# File: stripe_rag_evaluator.py (FIXED VERSION)
"""
Comprehensive RAG Evaluation System
NOW INCLUDES: Precision@K, Recall@K, MRR in aggregate results
"""

import json
import numpy as np
from openai import OpenAI
from typing import Dict, List
import os
from dotenv import load_dotenv

load_dotenv()

class StripeRAGEvaluator:
    
    def __init__(self, rag_system, golden_dataset_path: str):
        self.rag = rag_system
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        with open(golden_dataset_path, 'r') as f:
            data = json.load(f)
            self.dataset_info = data["dataset_info"]
            self.single_turn_tests = data["single_turn_tests"]
            self.multiturn_conversations = data["multi_turn_conversations"]
        
        print(f"✅ Loaded: {self.dataset_info['single_turn_tests']} single + {self.dataset_info['multi_turn_conversations']} multi-turn")
    
    def evaluate_retrieval(self, test_case: Dict, retrieved_docs: List[Dict]) -> Dict:
        """
        Calculate Precision@K, Recall@K, MRR
        """
        relevant_doc_ids = test_case.get("relevant_docs", [])
        requirements = test_case.get("retrieval_requirements", {})
        
        retrieved_ids = [doc["doc_id"] for doc in retrieved_docs]
        
        # 1. PRECISION@K
        relevant_retrieved = [doc_id for doc_id in retrieved_ids if doc_id in relevant_doc_ids]
        precision = len(relevant_retrieved) / len(retrieved_ids) if retrieved_ids else 0.0
        
        # 2. RECALL@K
        recall = len(relevant_retrieved) / len(relevant_doc_ids) if relevant_doc_ids else 1.0
        
        # 3. MRR (Mean Reciprocal Rank)
        mrr = 0.0
        for idx, doc_id in enumerate(retrieved_ids, 1):
            if doc_id in relevant_doc_ids:
                mrr = 1.0 / idx
                break
        
        # 4. TOP DOC SIMILARITY
        top_similarity = retrieved_docs[0]["similarity"] if retrieved_docs else 0.0
        min_similarity = requirements.get("min_similarity", 0.0)
        meets_threshold = top_similarity >= min_similarity
        
        # 5. TRICK QUESTIONS (should NOT retrieve)
        expected_behavior = requirements.get("expected_behavior", "")
        if expected_behavior == "should_not_retrieve":
            max_allowed = requirements.get("max_similarity", 0.60)
            should_not_retrieve_pass = top_similarity <= max_allowed
        else:
            should_not_retrieve_pass = None
        
        # 6. REQUIRED DOC IN TOP K?
        required_in_top_k = requirements.get("required_doc_must_be_in_top_k", None)
        if required_in_top_k and relevant_doc_ids:
            top_k_ids = retrieved_ids[:required_in_top_k]
            required_doc_found = any(doc_id in top_k_ids for doc_id in relevant_doc_ids)
        else:
            required_doc_found = None
        
        return {
            "precision_at_k": precision,
            "recall_at_k": recall,
            "mrr": mrr,
            "top_similarity": top_similarity,
            "meets_threshold": meets_threshold,
            "should_not_retrieve_pass": should_not_retrieve_pass,
            "required_doc_found": required_doc_found,
            "relevant_retrieved": relevant_retrieved,
            "retrieved_ids": retrieved_ids
        }
    
    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Semantic similarity using embeddings"""
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=[text1, text2]
        )
        
        emb1 = np.array(response.data[0].embedding)
        emb2 = np.array(response.data[1].embedding)
        
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        return float(similarity)
    
    def evaluate_answer_quality(self, test_case: Dict, rag_answer: str) -> Dict:
        """Answer quality metrics"""
        expected_answer = test_case["expected_answer"]
        
        # 1. SEMANTIC SIMILARITY
        similarity = self.calculate_semantic_similarity(expected_answer, rag_answer)
        
        # 2. LENGTH CHECK
        min_length = 50
        length_ok = len(rag_answer) >= min_length
        
        # 3. HALLUCINATION CHECK
        failure_mode = test_case.get("failure_mode", "")
        if failure_mode == "info_not_in_docs":
            knows_limitation = any(phrase in rag_answer.lower() for phrase in [
                "don't have", "don't know", "not in", "cannot find",
                "not available", "outside", "documentation focuses on"
            ])
        else:
            knows_limitation = None
        
        # 4. QUALITY RATING
        if similarity >= 0.75:
            quality = "good"
        elif similarity >= 0.60:
            quality = "acceptable"
        else:
            quality = "poor"
        
        return {
            "semantic_similarity": similarity,
            "length": len(rag_answer),
            "length_ok": length_ok,
            "knows_limitation": knows_limitation,
            "quality": quality
        }
    
    def evaluate_single_turn(self, test_case: Dict) -> Dict:
        """Evaluate single test"""
        question = test_case["question"]
        test_id = test_case["id"]
        
        # Run RAG
        result = self.rag.query(question, top_k=3)
        
        # Evaluate
        retrieval_metrics = self.evaluate_retrieval(test_case, result["sources"])
        answer_metrics = self.evaluate_answer_quality(test_case, result["answer"])
        
        # PASS/FAIL
        retrieval_pass = True
        retrieval_failures = []
        
        if not retrieval_metrics["meets_threshold"]:
            retrieval_pass = False
            retrieval_failures.append(f"Similarity {retrieval_metrics['top_similarity']:.3f} below threshold")
        
        if retrieval_metrics["should_not_retrieve_pass"] is False:
            retrieval_pass = False
            retrieval_failures.append("Should not retrieve but found high similarity")
        
        if retrieval_metrics["required_doc_found"] is False:
            retrieval_pass = False
            retrieval_failures.append("Required doc not in top K")
        
        answer_pass = True
        answer_failures = []
        
        if answer_metrics["quality"] == "poor":
            answer_pass = False
            answer_failures.append(f"Low semantic similarity ({answer_metrics['semantic_similarity']:.3f})")
        
        if not answer_metrics["length_ok"]:
            answer_pass = False
            answer_failures.append(f"Answer too short ({answer_metrics['length']} chars)")
        
        if answer_metrics["knows_limitation"] is False:
            answer_pass = False
            answer_failures.append("Should say 'I don't know' but attempted to answer")
        
        overall_pass = retrieval_pass and answer_pass
        
        return {
            "test_id": test_id,
            "question": question,
            "rag_answer": result["answer"],
            "expected_answer": test_case["expected_answer"],
            "retrieval_metrics": retrieval_metrics,
            "answer_metrics": answer_metrics,
            "retrieval_pass": retrieval_pass,
            "answer_pass": answer_pass,
            "overall_pass": overall_pass,
            "retrieval_failures": retrieval_failures,
            "answer_failures": answer_failures,
            "category": test_case["category"],
            "difficulty": test_case["difficulty"],
            "failure_mode": test_case["failure_mode"]
        }
    
    def evaluate_multiturn_conversation(self, conversation: Dict) -> Dict:
        """Multi-turn evaluation (stateless RAG will struggle)"""
        conv_id = conversation["id"]
        turns = conversation["turns"]
        
        turn_results = []
        
        for turn_data in turns:
            question = turn_data["user"]
            
            result = self.rag.query(question, top_k=3)
            
            temp_test = {
                "id": f"{conv_id}_turn{turn_data['turn']}",
                "question": question,
                "expected_answer": turn_data["expected_answer"],
                "relevant_docs": turn_data["relevant_docs"],
                "retrieval_requirements": conversation.get("retrieval_requirements", {}),
                "failure_mode": conversation["failure_mode"]
            }
            
            retrieval_metrics = self.evaluate_retrieval(temp_test, result["sources"])
            answer_metrics = self.evaluate_answer_quality(temp_test, result["answer"])
            
            turn_results.append({
                "turn": turn_data["turn"],
                "question": question,
                "rag_answer": result["answer"],
                "expected_answer": turn_data["expected_answer"],
                "retrieval_metrics": retrieval_metrics,
                "answer_metrics": answer_metrics,
                "context_needed": turn_data.get("context_needed", []),
                "must_remember": turn_data.get("must_remember", "")
            })
        
        all_turns_pass = all(
            turn["retrieval_metrics"]["meets_threshold"] and 
            turn["answer_metrics"]["quality"] in ["good", "acceptable"]
            for turn in turn_results
        )
        
        return {
            "conversation_id": conv_id,
            "conversation_name": conversation["conversation_name"],
            "turns": turn_results,
            "overall_pass": all_turns_pass,
            "category": conversation["category"],
            "difficulty": conversation["difficulty"]
        }
    
    def run_full_evaluation(self) -> Dict:
        """Run complete evaluation"""
        print("\n" + "="*70)
        print("STARTING FULL EVALUATION")
        print("="*70)
        
        # Single-turn
        print(f"\n📝 Evaluating {len(self.single_turn_tests)} single-turn tests...")
        single_turn_results = []
        
        for i, test in enumerate(self.single_turn_tests, 1):
            print(f"   [{i}/{len(self.single_turn_tests)}] {test['id']}")
            result = self.evaluate_single_turn(test)
            single_turn_results.append(result)
        
        # Multi-turn
        print(f"\n💬 Evaluating {len(self.multiturn_conversations)} multi-turn conversations...")
        multiturn_results = []
        
        for i, conv in enumerate(self.multiturn_conversations, 1):
            print(f"   [{i}/{len(self.multiturn_conversations)}] {conv['id']}")
            result = self.evaluate_multiturn_conversation(conv)
            multiturn_results.append(result)
        
        print("\n✅ Evaluation complete!")
        
        return {
            "dataset_info": self.dataset_info,
            "single_turn_results": single_turn_results,
            "multiturn_results": multiturn_results,
            "timestamp": str(np.datetime64('now'))
        }
