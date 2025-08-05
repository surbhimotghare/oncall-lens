"""
Task 7: Advanced Retrieval Performance Assessment with RAGAS

This script evaluates the performance of our advanced retrieval techniques
against the baseline results from Task 5.
"""

import os
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the project root to Python path
import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import get_settings_no_cache
from services.advanced_retrieval import AdvancedRetrievalService
from evaluation.ragas_evaluator import RAGASEvaluator
from evaluation.dataset_generator import DatasetGenerator


class AdvancedRetrievalEvaluator:
    """
    Evaluates advanced retrieval techniques using RAGAS metrics.
    Compares performance against baseline from Task 5.
    """
    
    def __init__(self):
        self.settings = get_settings_no_cache()
        self.evaluator = RAGASEvaluator(self.settings)
        self.dataset_generator = DatasetGenerator(self.settings)
        
        # Baseline scores from Task 5
        self.baseline_scores = {
            "faithfulness": 0.267,
            "answer_relevancy": 0.518,
            "context_precision": 0.75,
            "context_recall": 0.833,
            "semantic_similarity": 0.437,
            "answer_correctness": 0.163
        }
        
        # Advanced retrieval strategies to test
        self.strategies = [
            "naive",           # Baseline for comparison
            "parent_document", # Small-to-big strategy
            "hybrid",          # BM25 + Semantic
            "multi_query",     # Multiple query variations
            "compression",     # Cohere reranking
            "ensemble"         # All strategies combined
        ]
        
    async def initialize(self):
        """Initialize the advanced retrieval service."""
        logger.info("🔧 Initializing Advanced Retrieval Service...")
        self.advanced_service = AdvancedRetrievalService(self.settings)
        await self.advanced_service.initialize()
        logger.info("✅ Advanced Retrieval Service ready")
        
    async def generate_evaluation_dataset(self) -> Dict[str, Any]:
        """Load existing evaluation dataset."""
        logger.info("📊 Loading existing evaluation dataset...")
        
        # Load the existing synthetic dataset
        dataset_path = Path("evaluation/data/synthetic_dataset.json")
        
        if not dataset_path.exists():
            logger.warning("⚠️ Synthetic dataset not found, generating new one...")
            # Fallback to generating a new dataset
            dataset = await self.dataset_generator.generate_full_dataset(
                knowledge_base_path=self.settings.knowledge_base_path,
                output_path="evaluation/data/synthetic_dataset.json",
                num_questions_per_category=2
            )
            return dataset
        
        with open(dataset_path, 'r') as f:
            dataset_data = json.load(f)
            
        logger.info(f"✅ Loaded {len(dataset_data['questions'])} evaluation questions")
        return dataset_data
        
    async def evaluate_strategy(self, strategy: str, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single retrieval strategy."""
        logger.info(f"🔍 Evaluating strategy: {strategy}")
        
        try:
            # Get the retriever for this strategy
            retriever = self.advanced_service.get_retriever(strategy)
            if not retriever:
                logger.warning(f"⚠️ Strategy {strategy} not available")
                return {"error": f"Strategy {strategy} not available"}
            
            # Create a custom RAG pipeline for this strategy
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_openai import ChatOpenAI
            
            prompt = ChatPromptTemplate.from_template("""
            You are a helpful assistant. Use the context provided below to answer the question.
            
            Question: {question}
            
            Context: {context}
            
            Answer the question based on the context provided. If you cannot answer based on the context, say so.
            """)
            
            llm = ChatOpenAI(
                model=self.settings.openai_model,
                temperature=0,
                api_key=self.settings.openai_api_key
            )
            
            # Generate RAG responses using our custom retriever
            evaluation_data = await self._generate_rag_responses_with_retriever(
                retriever, llm, prompt, dataset
            )
            
            # Run RAGAS evaluation
            scores = self.evaluator.run_ragas_evaluation(evaluation_data)
            
            return {
                "scores": scores,
                "evaluation_data": evaluation_data,
                "strategy": strategy
            }
            
        except Exception as e:
            logger.error(f"❌ Error evaluating {strategy}: {e}")
            return {"error": str(e)}
    
    async def _generate_rag_responses_with_retriever(
        self, 
        retriever, 
        llm, 
        prompt, 
        dataset: Dict[str, Any]
    ) -> Dict[str, List[Any]]:
        """Generate RAG responses using a custom retriever."""
        logger.info(f"🤖 Generating responses with custom retriever...")
        
        questions = dataset['questions']
        responses = []
        contexts = []
        
        # Use only first 5 questions for faster evaluation
        num_questions = min(5, len(questions))
        questions = questions[:num_questions]
        
        for i, question in enumerate(questions):
            try:
                # Get relevant documents using our custom retriever
                docs = await retriever.aget_relevant_documents(question)
                
                # Combine context from retrieved documents
                context = "\n\n".join([doc.page_content for doc in docs])
                contexts.append([context] if context else [])
                
                # Generate response using LLM
                chain = prompt | llm
                response = await chain.ainvoke({
                    "question": question,
                    "context": context
                })
                
                responses.append(response.content)
                
                logger.info(f"✅ Generated response {i+1}/{len(questions)}")
                
            except Exception as e:
                logger.error(f"❌ Error processing question {i+1}: {e}")
                responses.append("Error generating response")
                contexts.append([])
        
        return {
            "questions": questions,
            "responses": responses,
            "contexts": contexts,
            "ground_truths": dataset.get('ground_truths', [])[:num_questions],
            "answers": dataset.get('answers', [])[:num_questions]
        }
        
    async def run_comprehensive_evaluation(self):
        """Run comprehensive evaluation of all advanced retrieval strategies."""
        logger.info("🚀 Starting Task 7: Advanced Retrieval Performance Assessment")
        print("=" * 80)
        
        # Initialize services
        await self.initialize()
        
        # Generate evaluation dataset
        dataset = await self.generate_evaluation_dataset()
        
        # Evaluate each strategy
        strategy_results = {}
        
        for strategy in self.strategies:
            try:
                results = await self.evaluate_strategy(strategy, dataset)
                strategy_results[strategy] = results
                logger.info(f"✅ Completed evaluation for {strategy}")
            except Exception as e:
                logger.error(f"❌ Error evaluating {strategy}: {e}")
                strategy_results[strategy] = {"error": str(e)}
                
        # Generate comparison report
        await self.generate_comparison_report(strategy_results)
        
    async def generate_comparison_report(self, strategy_results: Dict[str, Any]):
        """Generate a comprehensive comparison report."""
        logger.info("📊 Generating comparison report...")
        
        # Create results directory
        results_dir = Path("evaluation/results/advanced_retrieval_task7")
        results_dir.mkdir(parents=True, exist_ok=True)
        
        # Prepare report data
        report_data = {
            "metadata": {
                "run_name": "advanced_retrieval_task7",
                "timestamp": datetime.now().isoformat(),
                "strategies_tested": list(strategy_results.keys()),
                "baseline_comparison": True
            },
            "baseline_scores": self.baseline_scores,
            "strategy_results": strategy_results,
            "improvements": {}
        }
        
        # Calculate improvements
        for strategy, results in strategy_results.items():
            if "error" not in results and "scores" in results:
                scores = results["scores"]
                improvements = {}
                
                for metric, baseline_score in self.baseline_scores.items():
                    if metric in scores:
                        current_score = scores[metric]
                        improvement = current_score - baseline_score
                        improvement_pct = (improvement / baseline_score) * 100 if baseline_score > 0 else 0
                        
                        improvements[metric] = {
                            "baseline": baseline_score,
                            "current": current_score,
                            "improvement": improvement,
                            "improvement_pct": improvement_pct
                        }
                        
                report_data["improvements"][strategy] = improvements
        
        # Save detailed results
        with open(results_dir / "detailed_results.json", "w") as f:
            json.dump(report_data, f, indent=2)
            
        # Generate markdown report
        await self.generate_markdown_report(report_data, results_dir)
        
        logger.info(f"✅ Results saved to {results_dir}")
        
    async def generate_markdown_report(self, report_data: Dict[str, Any], results_dir: Path):
        """Generate a markdown comparison report."""
        
        report_content = f"""# Task 7: Advanced Retrieval Performance Assessment

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

This report compares the performance of advanced retrieval techniques against the baseline results from Task 5.

## Baseline Performance (Task 5)

| Metric | Score | Status |
|--------|-------|--------|
| Faithfulness | {self.baseline_scores['faithfulness']:.3f} | {'✅ Good' if self.baseline_scores['faithfulness'] >= 0.8 else '🔴 Needs Improvement'} |
| Answer Relevancy | {self.baseline_scores['answer_relevancy']:.3f} | {'✅ Good' if self.baseline_scores['answer_relevancy'] >= 0.8 else '🔴 Needs Improvement'} |
| Context Precision | {self.baseline_scores['context_precision']:.3f} | {'✅ Good' if self.baseline_scores['context_precision'] >= 0.8 else '🔴 Needs Improvement'} |
| Context Recall | {self.baseline_scores['context_recall']:.3f} | {'✅ Good' if self.baseline_scores['context_recall'] >= 0.8 else '🔴 Needs Improvement'} |
| Semantic Similarity | {self.baseline_scores['semantic_similarity']:.3f} | {'✅ Good' if self.baseline_scores['semantic_similarity'] >= 0.8 else '🔴 Needs Improvement'} |
| Answer Correctness | {self.baseline_scores['answer_correctness']:.3f} | {'✅ Good' if self.baseline_scores['answer_correctness'] >= 0.8 else '🔴 Needs Improvement'} |

## Advanced Retrieval Results

"""
        
        # Add results for each strategy
        for strategy, results in report_data["strategy_results"].items():
            if "error" in results:
                report_content += f"""
### {strategy.replace('_', ' ').title()}

❌ **Error**: {results['error']}

"""
            elif "scores" in results:
                scores = results["scores"]
                improvements = report_data["improvements"].get(strategy, {})
                
                report_content += f"""
### {strategy.replace('_', ' ').title()}

| Metric | Score | Improvement | Status |
|--------|-------|-------------|--------|
"""
                
                for metric, baseline_score in self.baseline_scores.items():
                    if metric in scores:
                        current_score = scores[metric]
                        improvement = improvements.get(metric, {})
                        
                        improvement_text = ""
                        if improvement:
                            imp_pct = improvement.get("improvement_pct", 0)
                            if imp_pct > 0:
                                improvement_text = f"+{imp_pct:.1f}%"
                            elif imp_pct < 0:
                                improvement_text = f"{imp_pct:.1f}%"
                        
                        status = "✅ Good" if current_score >= 0.8 else "🔴 Needs Improvement"
                        
                        report_content += f"| {metric.replace('_', ' ').title()} | {current_score:.3f} | {improvement_text} | {status} |\n"
                
                report_content += "\n"
        
        # Add summary
        report_content += """
## Summary

### Key Findings

1. **Best Performing Strategy**: [To be determined from results]
2. **Biggest Improvements**: [To be determined from results]
3. **Areas Still Needing Work**: [To be determined from results]

### Recommendations

Based on the results:

1. **For Production Use**: [Recommendation based on best strategy]
2. **For Further Improvement**: [Recommendations for next steps]
3. **For A/B Testing**: [Recommendations for live testing]

---

*Generated by Oncall Lens Advanced Retrieval Evaluator v1.0*
"""
        
        with open(results_dir / "evaluation_report.md", "w") as f:
            f.write(report_content)
            
        print("📊 Generated comprehensive evaluation report!")
        print(f"📁 Results saved to: {results_dir}")
        
        # Print quick summary
        print("\n🎯 Quick Summary:")
        print("=" * 50)
        for strategy, results in report_data["strategy_results"].items():
            if "scores" in results:
                scores = results["scores"]
                print(f"  {strategy:.<20} Context Precision: {scores.get('context_precision', 0):.3f}")
            else:
                print(f"  {strategy:.<20} ❌ Error")


async def main():
    """Main evaluation function."""
    evaluator = AdvancedRetrievalEvaluator()
    
    try:
        await evaluator.run_comprehensive_evaluation()
    except KeyboardInterrupt:
        print("\n⏹️ Evaluation interrupted by user")
    except Exception as e:
        print(f"\n❌ Evaluation failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 