"""
RAGAS Evaluator for Oncall Lens
Scientific evaluation of RAG system performance using RAGAS metrics.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
    answer_similarity,
    answer_correctness
)

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from config.settings import Settings
from services.agent_service import AgentService
from services.vector_store import QdrantVectorStore

logger = logging.getLogger(__name__)


class RAGASEvaluator:
    """
    Scientific evaluation of RAG system using RAGAS metrics.
    
    This evaluator runs comprehensive performance assessment of the 
    Oncall Lens RAG system including:
    - Faithfulness: How grounded are the answers in the context
    - Answer Relevancy: How relevant are answers to questions
    - Context Precision: How precise is the retrieved context
    - Context Recall: How complete is the retrieved context
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            api_key=settings.openai_api_key
        )
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=settings.openai_api_key
        )
        
        # Initialize services
        self.agent_service: Optional[AgentService] = None
        self.vector_store: Optional[QdrantVectorStore] = None
        
        # RAGAS metrics to evaluate
        self.metrics = [
            faithfulness,
            answer_relevancy, 
            context_precision,
            context_recall,
            answer_similarity,
            answer_correctness
        ]
        
    async def initialize_services(self):
        """Initialize the RAG services for evaluation."""
        logger.info("🔧 Initializing RAG services for evaluation...")
        
        # Initialize vector store
        self.vector_store = QdrantVectorStore(self.settings)
        await self.vector_store.initialize()
        
        # Initialize agent service
        self.agent_service = AgentService(self.settings)
        await self.agent_service.initialize()
        
        logger.info("✅ RAG services initialized")
        
    def load_synthetic_dataset(self, dataset_path: str) -> Dict[str, Any]:
        """Load the synthetic evaluation dataset."""
        logger.info(f"Loading synthetic dataset from {dataset_path}")
        
        with open(dataset_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
            
        logger.info(f"Loaded dataset with {dataset['metadata']['total_questions']} questions")
        return dataset
        
    async def run_rag_pipeline(self, question: str) -> Dict[str, Any]:
        """Run the RAG pipeline on a single question."""
        try:
            # Use the agent service to get an answer
            # This simulates an incident analysis with just a text question
            mock_files = []  # No files, just the question as context
            
            result = await self.agent_service.analyze_incident(
                processed_files=mock_files
            )
            
            # Extract answer and contexts from result
            answer = result.summary if hasattr(result, 'summary') else str(result)
            
            # Get contexts from similar incidents found
            contexts = []
            if hasattr(result, 'similar_incidents'):
                for incident in result.similar_incidents[:3]:  # Top 3 contexts
                    if hasattr(incident, 'description'):
                        contexts.append(incident.description)
                    elif isinstance(incident, dict) and 'description' in incident:
                        contexts.append(incident['description'])
            
            # If no contexts from similar incidents, query vector store directly
            if not contexts:
                search_results = await self.vector_store.similarity_search(
                    query=question,
                    k=3
                )
                contexts = [doc.page_content for doc in search_results]
            
            return {
                "answer": answer,
                "contexts": contexts
            }
            
        except Exception as e:
            logger.error(f"Failed to run RAG pipeline for question: {question[:100]}... Error: {e}")
            return {
                "answer": f"Error processing question: {str(e)}",
                "contexts": ["No context available due to processing error"]
            }
    
    async def generate_rag_responses(self, dataset: Dict[str, Any]) -> Dict[str, List[Any]]:
        """Generate RAG responses for all questions in the dataset."""
        logger.info("🔄 Generating RAG responses for evaluation...")
        
        questions = dataset["questions"]
        generated_answers = []
        retrieved_contexts = []
        
        total = len(questions)
        
        for i, question in enumerate(questions):
            logger.info(f"Processing question {i+1}/{total}: {question[:80]}...")
            
            try:
                result = await self.run_rag_pipeline(question)
                generated_answers.append(result["answer"])
                retrieved_contexts.append(result["contexts"])
                
            except Exception as e:
                logger.error(f"Failed to process question {i+1}: {e}")
                generated_answers.append(f"Error: {str(e)}")
                retrieved_contexts.append(["Error retrieving context"])
                
        logger.info("✅ Generated all RAG responses")
        
        return {
            "questions": questions,
            "answers": generated_answers,
            "contexts": retrieved_contexts,
            "ground_truths": dataset["ground_truths"]
        }
    
    def run_ragas_evaluation(self, evaluation_data: Dict[str, List[Any]]) -> Dict[str, float]:
        """Run RAGAS evaluation on the generated responses."""
        logger.info("📊 Running RAGAS evaluation...")
        
        # Create RAGAS dataset
        dataset = Dataset.from_dict({
            "question": evaluation_data["questions"],
            "answer": evaluation_data["answers"],
            "contexts": evaluation_data["contexts"],
            "ground_truth": evaluation_data["ground_truths"]
        })
        
        # Run evaluation
        result = evaluate(
            dataset=dataset,
            metrics=self.metrics,
            llm=self.llm,
            embeddings=self.embeddings
        )
        
        # Extract scores
        scores = {}
        for metric_name, score in result.items():
            if isinstance(score, (int, float)):
                scores[metric_name] = round(float(score), 3)
            elif hasattr(score, 'mean'):
                scores[metric_name] = round(float(score.mean()), 3)
            elif hasattr(score, 'score'):
                scores[metric_name] = round(float(score.score), 3)
            else:
                # Handle EvaluationResult object
                try:
                    scores[metric_name] = round(float(score), 3)
                except (TypeError, ValueError):
                    # If we can't convert, try to get the score attribute
                    if hasattr(score, 'score'):
                        scores[metric_name] = round(float(score.score), 3)
                    else:
                        scores[metric_name] = 0.0
        
        logger.info("✅ RAGAS evaluation completed")
        return scores
    
    def save_evaluation_results(
        self, 
        scores: Dict[str, float],
        evaluation_data: Dict[str, List[Any]],
        output_dir: str,
        run_name: str = None
    ) -> str:
        """Save evaluation results to files."""
        
        if run_name is None:
            run_name = f"evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
        output_path = Path(output_dir) / run_name
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save scores summary
        scores_file = output_path / "scores.json"
        with open(scores_file, 'w') as f:
            json.dump({
                "metadata": {
                    "run_name": run_name,
                    "timestamp": datetime.now().isoformat(),
                    "total_questions": len(evaluation_data["questions"]),
                    "model": "gpt-4o",
                    "embedding_model": "text-embedding-3-small"
                },
                "scores": scores
            }, f, indent=2)
        
        # Save detailed results
        detailed_results = pd.DataFrame({
            "question": evaluation_data["questions"],
            "generated_answer": evaluation_data["answers"],
            "ground_truth": evaluation_data["ground_truths"],
            "contexts": [str(ctx) for ctx in evaluation_data["contexts"]]
        })
        
        detailed_file = output_path / "detailed_results.csv"
        detailed_results.to_csv(detailed_file, index=False)
        
        # Create summary report
        report_file = output_path / "evaluation_report.md"
        self.create_evaluation_report(scores, str(report_file), run_name)
        
        logger.info(f"📁 Evaluation results saved to {output_path}")
        return str(output_path)
    
    def create_evaluation_report(self, scores: Dict[str, float], report_path: str, run_name: str):
        """Create a markdown evaluation report."""
        
        report_content = f"""# RAGAS Evaluation Report: {run_name}

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

This report presents the RAGAS evaluation results for the Oncall Lens RAG system.

## Metrics Explanation

- **Faithfulness**: How well the generated answers are grounded in the retrieved context (higher is better)
- **Answer Relevancy**: How relevant the generated answers are to the questions (higher is better)  
- **Context Precision**: How precise/relevant the retrieved context is (higher is better)
- **Context Recall**: How complete the retrieved context is (higher is better)
- **Answer Similarity**: Semantic similarity between generated and ground truth answers (higher is better)
- **Answer Correctness**: Correctness of generated answers compared to ground truth (higher is better)

## Results

| Metric | Score | Interpretation |
|--------|-------|----------------|
"""
        
        # Add scores to table
        interpretations = {
            "faithfulness": "Excellent (>0.9)" if scores.get("faithfulness", 0) > 0.9 else 
                          "Good (>0.8)" if scores.get("faithfulness", 0) > 0.8 else "Needs Improvement",
            "answer_relevancy": "Excellent (>0.9)" if scores.get("answer_relevancy", 0) > 0.9 else 
                              "Good (>0.8)" if scores.get("answer_relevancy", 0) > 0.8 else "Needs Improvement",
            "context_precision": "Excellent (>0.9)" if scores.get("context_precision", 0) > 0.9 else 
                               "Good (>0.8)" if scores.get("context_precision", 0) > 0.8 else "Needs Improvement",
            "context_recall": "Excellent (>0.9)" if scores.get("context_recall", 0) > 0.9 else 
                            "Good (>0.8)" if scores.get("context_recall", 0) > 0.8 else "Needs Improvement"
        }
        
        for metric, score in scores.items():
            interpretation = interpretations.get(metric, "N/A")
            report_content += f"| {metric.replace('_', ' ').title()} | {score:.3f} | {interpretation} |\n"
        
        report_content += f"""

## Analysis

### Strengths
- Metrics scoring above 0.8 indicate strong performance in those areas
- High faithfulness suggests good grounding in source material
- High answer relevancy indicates good question understanding

### Areas for Improvement  
- Metrics below 0.8 suggest opportunities for enhancement
- Low context precision/recall may indicate retrieval issues
- Consider advanced retrieval techniques for improvement

## Recommendations

Based on these results:

1. **If Context Precision < 0.8**: Implement hybrid search (semantic + keyword)
2. **If Context Recall < 0.8**: Use parent document retriever for more complete context  
3. **If Faithfulness < 0.8**: Improve prompt engineering for better grounding
4. **If Answer Relevancy < 0.8**: Enhance question understanding and routing

## Next Steps

1. Implement recommended improvements
2. Re-run evaluation to measure impact
3. Compare results with baseline metrics
4. Consider A/B testing different retrieval strategies

---

*Generated by Oncall Lens RAGAS Evaluator v1.0*
"""

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
    
    async def run_full_evaluation(
        self, 
        dataset_path: str,
        output_dir: str,
        run_name: str = None
    ) -> Dict[str, Any]:
        """Run complete evaluation pipeline."""
        
        logger.info("🚀 Starting full RAGAS evaluation...")
        
        # Initialize services
        await self.initialize_services()
        
        # Load dataset
        dataset = self.load_synthetic_dataset(dataset_path)
        
        # Generate RAG responses
        evaluation_data = await self.generate_rag_responses(dataset)
        
        # Run RAGAS evaluation
        scores = self.run_ragas_evaluation(evaluation_data)
        
        # Save results
        results_path = self.save_evaluation_results(
            scores, evaluation_data, output_dir, run_name
        )
        
        logger.info("🎉 Full evaluation completed successfully!")
        
        return {
            "scores": scores,
            "results_path": results_path,
            "total_questions": len(evaluation_data["questions"])
        }


async def main():
    """Run RAGAS evaluation."""
    from config.settings import get_settings
    
    settings = get_settings()
    evaluator = RAGASEvaluator(settings)
    
    dataset_path = "backend/evaluation/data/synthetic_dataset.json"
    output_dir = "backend/evaluation/results"
    
    results = await evaluator.run_full_evaluation(
        dataset_path=dataset_path,
        output_dir=output_dir,
        run_name="baseline_evaluation"
    )
    
    print("\n🎉 Evaluation Results:")
    print("=" * 50)
    for metric, score in results["scores"].items():
        print(f"{metric.replace('_', ' ').title():.<30} {score:.3f}")
    print("=" * 50)
    print(f"📁 Detailed results: {results['results_path']}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 