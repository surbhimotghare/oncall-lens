#!/usr/bin/env python3
"""
RAGAS Evaluation System Demo
Demonstrates the complete workflow from dataset generation to evaluation.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.append('..')

from config.settings import get_settings
from evaluation.dataset_generator import DatasetGenerator
from evaluation.ragas_evaluator import RAGASEvaluator


async def demo_complete_workflow():
    """Demonstrate the complete RAGAS evaluation workflow."""
    
    print("🚀 RAGAS Evaluation System Demo")
    print("=" * 60)
    print("This demo shows the complete workflow:")
    print("1. Generate synthetic dataset from postmortems")
    print("2. Run RAGAS evaluation")
    print("3. Generate evaluation report")
    print("=" * 60)
    
    # Configuration
    settings = get_settings()
    
    # Paths
    knowledge_base_path = "../data/knowledge-base"
    dataset_path = "./demo_data/demo_dataset.json"
    results_dir = "./demo_results"
    
    # Create directories
    Path(dataset_path).parent.mkdir(parents=True, exist_ok=True)
    Path(results_dir).mkdir(parents=True, exist_ok=True)
    
    try:
        # Step 1: Generate synthetic dataset
        print("\n📊 Step 1: Generating Synthetic Dataset")
        print("-" * 40)
        
        generator = DatasetGenerator(settings)
        
        print(f"Loading postmortems from: {knowledge_base_path}")
        dataset = await generator.generate_full_dataset(
            knowledge_base_path=knowledge_base_path,
            output_path=dataset_path,
            num_questions_per_category=2  # Small demo dataset
        )
        
        print(f"✅ Generated {dataset['metadata']['total_questions']} Q&A pairs")
        print(f"📁 Saved to: {dataset_path}")
        
        # Show sample questions
        print("\n🔍 Sample Generated Questions:")
        for i, question in enumerate(dataset['questions'][:3]):
            print(f"{i+1}. {question}")
        
        # Step 2: Run RAGAS evaluation
        print(f"\n🔬 Step 2: Running RAGAS Evaluation")
        print("-" * 40)
        
        evaluator = RAGASEvaluator(settings)
        
        print("Starting evaluation (this may take a few minutes)...")
        results = await evaluator.run_full_evaluation(
            dataset_path=dataset_path,
            output_dir=results_dir,
            run_name="demo_evaluation"
        )
        
        # Step 3: Display results
        print(f"\n🎉 Step 3: Evaluation Results")
        print("-" * 40)
        
        print(f"Total Questions Evaluated: {results['total_questions']}")
        print("\nRAGAS Scores:")
        
        for metric, score in results['scores'].items():
            # Color code based on performance
            if score > 0.9:
                status = "🟢 Excellent"
            elif score > 0.8:
                status = "🟡 Good"
            else:
                status = "🔴 Needs Improvement"
            
            print(f"  {metric.replace('_', ' ').title():.<25} {score:.3f} {status}")
        
        # Analysis and recommendations
        print(f"\n📈 Analysis:")
        
        scores = results['scores']
        excellent = [k for k, v in scores.items() if v > 0.9]
        good = [k for k, v in scores.items() if 0.8 < v <= 0.9]
        needs_improvement = [k for k, v in scores.items() if v <= 0.8]
        
        if excellent:
            print(f"✅ Excellent Performance: {', '.join(excellent)}")
        if good:
            print(f"👍 Good Performance: {', '.join(good)}")
        if needs_improvement:
            print(f"⚠️  Needs Improvement: {', '.join(needs_improvement)}")
        
        print(f"\n📁 Detailed results saved to: {results['results_path']}")
        
        # Show what was created
        print(f"\n📋 Generated Files:")
        results_path = Path(results['results_path'])
        for file in results_path.glob("*"):
            print(f"  - {file.name}")
        
        # Next steps
        print(f"\n🚀 Next Steps:")
        print("1. Review the detailed evaluation report")
        print("2. Implement recommended improvements")
        print("3. Re-run evaluation to measure progress")
        print("4. Set up automated evaluation pipeline")
        
        print(f"\n✅ Demo completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def quick_test():
    """Quick test to verify system is working."""
    print("🧪 Quick System Test")
    print("-" * 20)
    
    try:
        # Test imports
        from ragas.metrics import faithfulness
        print("✅ RAGAS imports working")
        
        # Test settings
        settings = get_settings()
        if not settings.openai_api_key or settings.openai_api_key == "your-openai-api-key":
            print("❌ OpenAI API key not configured")
            print("💡 Set OPENAI_API_KEY environment variable")
            return False
        print("✅ Configuration looks good")
        
        # Test knowledge base
        kb_path = Path("../data/knowledge-base")
        postmortems = list(kb_path.glob("*.md"))
        non_templates = [p for p in postmortems if not p.name.startswith("postmortem-template")]
        
        if len(non_templates) == 0:
            print("❌ No postmortem files found")
            return False
        print(f"✅ Found {len(non_templates)} postmortem files")
        
        print("✅ Quick test passed! System ready for demo.")
        return True
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return False


async def main():
    """Main demo entry point."""
    
    print("Welcome to the RAGAS Evaluation System Demo!")
    print("This demo will show you how to evaluate your RAG system scientifically.\n")
    
    # Quick test first
    if not await quick_test():
        print("\n❌ System not ready. Please fix the issues above.")
        return
    
    print("\n" + "="*60)
    print("Starting full demo...")
    print("="*60)
    
    success = await demo_complete_workflow()
    
    if success:
        print("\n🎉 Demo completed successfully!")
        print("\nYou now have a working RAGAS evaluation system!")
        print("\nTo run evaluations on your own:")
        print("  python cli.py full-pipeline --knowledge-base ../data/knowledge-base --output-dir ./results")
    else:
        print("\n❌ Demo encountered issues. Please check the error messages above.")


if __name__ == "__main__":
    asyncio.run(main()) 