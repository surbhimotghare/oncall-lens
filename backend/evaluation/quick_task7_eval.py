"""
Quick Task 7: Advanced Retrieval Performance Assessment
Fast evaluation of key advanced retrieval strategies.
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


class QuickAdvancedRetrievalEvaluator:
    """
    Quick evaluation of advanced retrieval techniques using RAGAS metrics.
    Tests only the most important strategies with minimal questions.
    """
    
    def __init__(self):
        self.settings = get_settings_no_cache()
        self.evaluator = RAGASEvaluator(self.settings)
        
        # Baseline scores from Task 5
        self.baseline_scores = {
            "faithfulness": 0.267,
            "answer_relevancy": 0.518,
            "context_precision": 0.75,
            "context_recall": 0.833,
            "semantic_similarity": 0.437,
            "answer_correctness": 0.163
        }
        
        # Test only the most important strategies
        self.strategies = [
            "naive",           # Baseline for comparison
            "hybrid",          # BM25 + Semantic (most promising)
            "ensemble"         # All strategies combined
        ]
        
    async def initialize(self):
        """Initialize the advanced retrieval service."""
        logger.info("🔧 Initializing Advanced Retrieval Service...")
        self.advanced_service = AdvancedRetrievalService(self.settings)
        await self.advanced_service.initialize()
        logger.info("✅ Advanced Retrieval Service ready")
        
    def create_mini_dataset(self) -> Dict[str, Any]:
        """Create a minimal evaluation dataset with just 2 questions."""
        logger.info("📊 Creating minimal evaluation dataset...")
        
        # Use just 2 focused questions for quick evaluation
        mini_dataset = {
            "metadata": {"total_questions": 2},
            "questions": [
                "What was the root cause of the Hosted Graphite outage on March 12th, 2014?",
                "How was the service outage resolved and what steps were taken?"
            ],
            "contexts": [
                ["# Hosted Graphite Postmortem Report\n\n## Outage\n**Period:** March 12th 2014 18:50 UTC to 19:20 (30 minutes)\n**Impact:** Complete loss of new incoming data from all customers\n\n## Root Cause\nA user deleted their account while still sending data. All 13 aggregation services attempted to remove data for this user from a queue, but a lookup on the user's ID failed. Queue processing stopped, and it started building up in memory. No new metric data was written out.\n\n## Resolution\nAfter investigating, the team decided to discard a large amount of data in memory to get the service back up quickly. The discarded data was copied in logs that could be replayed. The service was restored by 19:20 UTC."],
                ["# Hosted Graphite Postmortem Report\n\n## Resolution Steps\n1. On-call engineer began investigating at 18:56 UTC\n2. First outage notification tweet sent at 19:00 UTC\n3. Decision made to discard data in memory to restore service quickly\n4. Service operating normally by 19:20 UTC\n5. Engineer began replaying logs to restore missing data\n6. All restores completed by 22:00 UTC\n\n## Actions Taken\n- Added better error handling to aggregation services\n- Implemented improved logging for data replay\n- Enhanced monitoring for similar failure modes"]
            ],
            "ground_truths": [
                "The root cause was a user account deletion while data was still being sent, causing aggregation services to fail when looking up the deleted user ID, which stopped queue processing and prevented new metric data from being written.",
                "The outage was resolved by discarding data in memory to quickly restore service, then replaying logs to restore missing data. The team added better error handling to prevent future occurrences."
            ],
            "answers": [
                "The root cause was a user account deletion while data was still being sent, causing aggregation services to fail when looking up the deleted user ID, which stopped queue processing and prevented new metric data from being written.",
                "The outage was resolved by discarding data in memory to quickly restore service, then replaying logs to restore missing data. The team added better error handling to prevent future occurrences."
            ]
        }
        
        logger.info(f"✅ Created mini dataset with {len(mini_dataset['questions'])} questions")
        return mini_dataset
        
    async def evaluate_strategy(self, strategy: str, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single retrieval strategy."""
        logger.info(f"🔍 Evaluating strategy: {strategy}")
        
        try:
            # Get the retriever for this strategy
            retriever = self.advanced_service.get_retriever(strategy)
            if not retriever:
                logger.warning(f"⚠️ Strategy {strategy} not available")
                return {"error": f"Strategy {strategy} not available"}
            
            # Create a simple RAG pipeline
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_openai import ChatOpenAI
            
            prompt = ChatPromptTemplate.from_template("""
            Answer the question based on the context provided.
            
            Question: {question}
            Context: {context}
            
            Answer:""")
            
            llm = ChatOpenAI(
                model=self.settings.openai_model,
                temperature=0,
                api_key=self.settings.openai_api_key
            )
            
            # Generate responses
            questions = dataset['questions']
            responses = []
            contexts = []
            
            for i, question in enumerate(questions):
                try:
                    # Get relevant documents
                    docs = await retriever.aget_relevant_documents(question)
                    
                    # Combine context
                    context = "\n\n".join([doc.page_content for doc in docs])
                    contexts.append([context] if context else [])
                    
                    # Generate response
                    chain = prompt | llm
                    response = await chain.ainvoke({
                        "question": question,
                        "context": context
                    })
                    
                    responses.append(response.content)
                    logger.info(f"✅ Generated response {i+1}/{len(questions)} for {strategy}")
                    
                except Exception as e:
                    logger.error(f"❌ Error processing question {i+1}: {e}")
                    responses.append("Error generating response")
                    contexts.append([])
            
            # Create evaluation data
            evaluation_data = {
                "questions": questions,
                "responses": responses,
                "contexts": contexts,
                "ground_truths": dataset['ground_truths'],
                "answers": dataset['answers']
            }
            
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
        
    async def run_quick_evaluation(self):
        """Run quick evaluation of key strategies."""
        logger.info("🚀 Starting Quick Task 7: Advanced Retrieval Performance Assessment")
        print("=" * 80)
        
        # Initialize services
        await self.initialize()
        
        # Create mini dataset
        dataset = self.create_mini_dataset()
        
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
                
        # Generate quick report
        await self.generate_quick_report(strategy_results)
        
    async def generate_quick_report(self, strategy_results: Dict[str, Any]):
        """Generate a quick comparison report."""
        logger.info("📊 Generating quick comparison report...")
        
        # Create results directory
        results_dir = Path("evaluation/results/quick_task7")
        results_dir.mkdir(parents=True, exist_ok=True)
        
        # Calculate improvements
        improvements = {}
        for strategy, results in strategy_results.items():
            if "error" not in results and "scores" in results:
                scores = results["scores"]
                strategy_improvements = {}
                
                for metric, baseline_score in self.baseline_scores.items():
                    if metric in scores:
                        current_score = scores[metric]
                        improvement = current_score - baseline_score
                        improvement_pct = (improvement / baseline_score) * 100 if baseline_score > 0 else 0
                        
                        strategy_improvements[metric] = {
                            "baseline": baseline_score,
                            "current": current_score,
                            "improvement": improvement,
                            "improvement_pct": improvement_pct
                        }
                        
                improvements[strategy] = strategy_improvements
        
        # Generate markdown report
        report_content = f"""# Quick Task 7: Advanced Retrieval Performance Assessment

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

Quick evaluation of advanced retrieval techniques against baseline results from Task 5.

## Baseline Performance (Task 5)

| Metric | Score | Status |
|--------|-------|--------|
| Faithfulness | {self.baseline_scores['faithfulness']:.3f} | {'✅ Good' if self.baseline_scores['faithfulness'] >= 0.8 else '🔴 Needs Improvement'} |
| Answer Relevancy | {self.baseline_scores['answer_relevancy']:.3f} | {'✅ Good' if self.baseline_scores['answer_relevancy'] >= 0.8 else '🔴 Needs Improvement'} |
| Context Precision | {self.baseline_scores['context_precision']:.3f} | {'✅ Good' if self.baseline_scores['context_precision'] >= 0.8 else '🔴 Needs Improvement'} |
| Context Recall | {self.baseline_scores['context_recall']:.3f} | {'✅ Good' if self.baseline_scores['context_recall'] >= 0.8 else '🔴 Needs Improvement'} |

## Quick Results

"""
        
        # Add results for each strategy
        for strategy, results in strategy_results.items():
            if "error" in results:
                report_content += f"""
### {strategy.replace('_', ' ').title()}

❌ **Error**: {results['error']}

"""
            elif "scores" in results:
                scores = results["scores"]
                strategy_improvements = improvements.get(strategy, {})
                
                report_content += f"""
### {strategy.replace('_', ' ').title()}

| Metric | Score | Improvement | Status |
|--------|-------|-------------|--------|
"""
                
                for metric, baseline_score in self.baseline_scores.items():
                    if metric in scores:
                        current_score = scores[metric]
                        improvement = strategy_improvements.get(metric, {})
                        
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
## Quick Summary

### Key Findings

1. **Best Performing Strategy**: [To be determined from results]
2. **Biggest Improvements**: [To be determined from results]
3. **Areas Still Needing Work**: [To be determined from results]

### Next Steps

1. **For Production**: Use the best performing strategy
2. **For Further Testing**: Run full evaluation with more questions
3. **For Optimization**: Focus on strategies showing improvement

---

*Generated by Oncall Lens Quick Evaluator v1.0*
"""
        
        with open(results_dir / "quick_evaluation_report.md", "w") as f:
            f.write(report_content)
            
        # Save detailed results
        report_data = {
            "metadata": {
                "run_name": "quick_task7",
                "timestamp": datetime.now().isoformat(),
                "strategies_tested": list(strategy_results.keys()),
                "baseline_comparison": True
            },
            "baseline_scores": self.baseline_scores,
            "strategy_results": strategy_results,
            "improvements": improvements
        }
        
        with open(results_dir / "quick_results.json", "w") as f:
            json.dump(report_data, f, indent=2)
            
        print("📊 Generated quick evaluation report!")
        print(f"📁 Results saved to: {results_dir}")
        
        # Print quick summary
        print("\n🎯 Quick Summary:")
        print("=" * 50)
        for strategy, results in strategy_results.items():
            if "scores" in results:
                scores = results["scores"]
                print(f"  {strategy:.<20} Context Precision: {scores.get('context_precision', 0):.3f}")
            else:
                print(f"  {strategy:.<20} ❌ Error")


async def main():
    """Main evaluation function."""
    evaluator = QuickAdvancedRetrievalEvaluator()
    
    try:
        await evaluator.run_quick_evaluation()
    except KeyboardInterrupt:
        print("\n⏹️ Evaluation interrupted by user")
    except Exception as e:
        print(f"\n❌ Evaluation failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 