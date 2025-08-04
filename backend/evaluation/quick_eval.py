#!/usr/bin/env python3
"""
Quick RAGAS Evaluation Demo
Demonstrates RAGAS evaluation with a simple mock RAG system.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.append('..')

from config.settings import get_settings
from evaluation.ragas_evaluator import RAGASEvaluator


class MockRAGSystem:
    """Simple mock RAG system for demonstration."""
    
    def __init__(self):
        self.mock_responses = {
            "What was the root cause": "The root cause was a database connection pool exhaustion due to a memory leak in the connection cleanup code.",
            "How was the incident resolved": "The incident was resolved by restarting the database service and deploying a hotfix for the memory leak.",
            "What was the impact": "The impact was 45 minutes of service downtime affecting approximately 50,000 users.",
            "What preventive measures": "Preventive measures included implementing connection pool monitoring and adding automated cleanup procedures.",
            "How was the incident detected": "The incident was detected through monitoring alerts that fired when the error rate exceeded 85%."
        }
    
    async def get_answer(self, question: str) -> str:
        """Get a mock answer for the question."""
        # Simple keyword matching for demo
        for key, response in self.mock_responses.items():
            if key.lower() in question.lower():
                return response
        return "The incident was caused by a system failure that required immediate intervention to restore service."


class QuickEvaluator(RAGASEvaluator):
    """Quick evaluator that uses a mock RAG system."""
    
    def __init__(self, settings):
        super().__init__(settings)
        self.mock_rag = MockRAGSystem()
    
    async def run_rag_pipeline(self, question: str) -> dict:
        """Run the mock RAG pipeline on a single question."""
        try:
            # Get mock answer
            answer = await self.mock_rag.get_answer(question)
            
            # Mock contexts based on question type
            if "root cause" in question.lower():
                contexts = ["Database connection pool reached maximum capacity. Memory leak detected in connection cleanup code."]
            elif "resolved" in question.lower() or "resolution" in question.lower():
                contexts = ["Service was restarted at 14:30 UTC. Hotfix deployed at 15:00 UTC containing memory leak fix."]
            elif "impact" in question.lower():
                contexts = ["Service downtime lasted 45 minutes. Approximately 50,000 users were affected."]
            elif "preventive" in question.lower() or "prevention" in question.lower():
                contexts = ["Monitoring alerts were implemented. Automated cleanup procedures were added."]
            elif "detected" in question.lower() or "detection" in question.lower():
                contexts = ["Monitoring system detected high error rates. Alerts fired when error rate exceeded 85%."]
            else:
                contexts = ["System failure occurred during peak traffic hours. Immediate intervention was required."]
            
            return {
                "answer": answer,
                "contexts": contexts
            }
            
        except Exception as e:
            return {
                "answer": f"Error processing question: {str(e)}",
                "contexts": ["Error retrieving context"]
            }


async def main():
    """Run quick evaluation demo."""
    print("🚀 Quick RAGAS Evaluation Demo")
    print("=" * 50)
    print("This demo shows RAGAS evaluation with a mock RAG system")
    print("=" * 50)
    
    # Load the generated dataset
    dataset_path = "./data/synthetic_dataset.json"
    
    if not Path(dataset_path).exists():
        print(f"❌ Dataset not found at {dataset_path}")
        print("💡 Run: python cli.py generate-dataset first")
        return
    
    # Initialize evaluator
    settings = get_settings()
    evaluator = QuickEvaluator(settings)
    
    # Load dataset
    print(f"\n📊 Loading dataset from {dataset_path}")
    dataset = evaluator.load_synthetic_dataset(dataset_path)
    print(f"✅ Loaded {dataset['metadata']['total_questions']} questions")
    
    # Use only first 5 questions to avoid rate limits
    small_dataset = {
        "metadata": dataset["metadata"],
        "questions": dataset["questions"][:5],
        "answers": dataset["answers"][:5],
        "ground_truths": dataset["ground_truths"][:5],
        "contexts": dataset["contexts"][:5]
    }
    print(f"📝 Using first 5 questions for demo (to avoid rate limits)")
    
    # Generate mock RAG responses
    print(f"\n🤖 Generating mock RAG responses...")
    evaluation_data = await evaluator.generate_rag_responses(small_dataset)
    print(f"✅ Generated responses for {len(evaluation_data['questions'])} questions")
    
    # Run RAGAS evaluation
    print(f"\n🔬 Running RAGAS evaluation...")
    scores = evaluator.run_ragas_evaluation(evaluation_data)
    
    # Display results
    print(f"\n🎉 Evaluation Results:")
    print("=" * 50)
    
    if not scores:
        print("⚠️  No scores returned from evaluation")
        return
    
    for metric, score in scores.items():
        if score > 0.9:
            status = "🟢 Excellent"
        elif score > 0.8:
            status = "🟡 Good"
        else:
            status = "🔴 Needs Improvement"
        
        print(f"{metric.replace('_', ' ').title():.<30} {score:.3f} {status}")
    
    print("=" * 50)
    
    # Analysis
    print(f"\n📈 Analysis:")
    excellent = [k for k, v in scores.items() if v > 0.9]
    good = [k for k, v in scores.items() if 0.8 < v <= 0.9]
    needs_improvement = [k for k, v in scores.items() if v <= 0.8]
    
    if excellent:
        print(f"✅ Excellent Performance: {', '.join(excellent)}")
    if good:
        print(f"👍 Good Performance: {', '.join(good)}")
    if needs_improvement:
        print(f"⚠️  Needs Improvement: {', '.join(needs_improvement)}")
    
    print(f"\n🎯 This demonstrates the RAGAS evaluation system working!")
    print(f"📚 Next: Run with your actual RAG system for real metrics")


if __name__ == "__main__":
    asyncio.run(main()) 