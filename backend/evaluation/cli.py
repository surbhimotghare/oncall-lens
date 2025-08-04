"""
CLI for RAGAS Evaluation System
Provides command-line interface for running evaluations with various options.
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import get_settings
from evaluation.dataset_generator import DatasetGenerator
from evaluation.ragas_evaluator import RAGASEvaluator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EvaluationCLI:
    """Command-line interface for RAGAS evaluation system."""
    
    def __init__(self):
        self.settings = get_settings()
        
    async def generate_dataset(self, args):
        """Generate synthetic evaluation dataset."""
        print("🔧 Generating synthetic evaluation dataset...")
        
        generator = DatasetGenerator(self.settings)
        
        dataset = await generator.generate_full_dataset(
            knowledge_base_path=args.knowledge_base,
            output_path=args.output,
            num_questions_per_category=args.questions_per_category
        )
        
        print(f"✅ Generated dataset with {dataset['metadata']['total_questions']} questions")
        print(f"📁 Saved to: {args.output}")
        
    async def run_evaluation(self, args):
        """Run RAGAS evaluation."""
        print("🚀 Running RAGAS evaluation...")
        
        evaluator = RAGASEvaluator(self.settings)
        
        results = await evaluator.run_full_evaluation(
            dataset_path=args.dataset,
            output_dir=args.output_dir,
            run_name=args.run_name
        )
        
        print("\n🎉 Evaluation Results:")
        print("=" * 50)
        for metric, score in results["scores"].items():
            print(f"{metric.replace('_', ' ').title():.<30} {score:.3f}")
        print("=" * 50)
        print(f"📁 Detailed results: {results['results_path']}")
        
    async def run_full_pipeline(self, args):
        """Run complete pipeline: generate dataset + evaluate."""
        print("🔄 Running full evaluation pipeline...")
        
        # Step 1: Generate dataset
        print("\n📊 Step 1: Generating synthetic dataset...")
        generator = DatasetGenerator(self.settings)
        
        dataset_path = args.output_dir + "/synthetic_dataset.json"
        dataset = await generator.generate_full_dataset(
            knowledge_base_path=args.knowledge_base,
            output_path=dataset_path,
            num_questions_per_category=args.questions_per_category
        )
        
        print(f"✅ Generated dataset with {dataset['metadata']['total_questions']} questions")
        
        # Step 2: Run evaluation
        print("\n🔬 Step 2: Running RAGAS evaluation...")
        evaluator = RAGASEvaluator(self.settings)
        
        results = await evaluator.run_full_evaluation(
            dataset_path=dataset_path,
            output_dir=args.output_dir,
            run_name=args.run_name
        )
        
        print("\n🎉 Full Pipeline Results:")
        print("=" * 60)
        print(f"Dataset Questions: {results['total_questions']}")
        print("-" * 60)
        for metric, score in results["scores"].items():
            print(f"{metric.replace('_', ' ').title():.<30} {score:.3f}")
        print("=" * 60)
        print(f"📁 Results saved to: {results['results_path']}")
        
    def create_parser(self):
        """Create argument parser."""
        parser = argparse.ArgumentParser(
            description="RAGAS Evaluation CLI for Oncall Lens",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Generate synthetic dataset
  python cli.py generate-dataset --knowledge-base ../data/knowledge-base --output ./data/dataset.json

  # Run evaluation on existing dataset
  python cli.py evaluate --dataset ./data/dataset.json --output-dir ./results

  # Run full pipeline (generate + evaluate)
  python cli.py full-pipeline --knowledge-base ../data/knowledge-base --output-dir ./results
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Generate dataset command
        gen_parser = subparsers.add_parser(
            'generate-dataset', 
            help='Generate synthetic evaluation dataset'
        )
        gen_parser.add_argument(
            '--knowledge-base', '-kb',
            type=str,
            default='../data/knowledge-base',
            help='Path to knowledge base directory (default: ../data/knowledge-base)'
        )
        gen_parser.add_argument(
            '--output', '-o',
            type=str,
            default='./data/synthetic_dataset.json',
            help='Output path for generated dataset (default: ./data/synthetic_dataset.json)'
        )
        gen_parser.add_argument(
            '--questions-per-category', '-q',
            type=int,
            default=3,
            help='Number of questions per category (default: 3)'
        )
        
        # Evaluate command
        eval_parser = subparsers.add_parser(
            'evaluate',
            help='Run RAGAS evaluation on existing dataset'
        )
        eval_parser.add_argument(
            '--dataset', '-d',
            type=str,
            default='./data/synthetic_dataset.json',
            help='Path to evaluation dataset (default: ./data/synthetic_dataset.json)'
        )
        eval_parser.add_argument(
            '--output-dir', '-o',
            type=str,
            default='./results',
            help='Output directory for results (default: ./results)'
        )
        eval_parser.add_argument(
            '--run-name', '-n',
            type=str,
            help='Name for this evaluation run (default: auto-generated)'
        )
        
        # Full pipeline command
        full_parser = subparsers.add_parser(
            'full-pipeline',
            help='Run complete pipeline: generate dataset + evaluate'
        )
        full_parser.add_argument(
            '--knowledge-base', '-kb',
            type=str,
            default='../data/knowledge-base',
            help='Path to knowledge base directory (default: ../data/knowledge-base)'
        )
        full_parser.add_argument(
            '--output-dir', '-o',
            type=str,
            default='./results',
            help='Output directory for all results (default: ./results)'
        )
        full_parser.add_argument(
            '--questions-per-category', '-q',
            type=int,
            default=3,
            help='Number of questions per category (default: 3)'
        )
        full_parser.add_argument(
            '--run-name', '-n',
            type=str,
            help='Name for this evaluation run (default: auto-generated)'
        )
        
        return parser
    
    async def run(self):
        """Main CLI entry point."""
        parser = self.create_parser()
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            return
            
        try:
            if args.command == 'generate-dataset':
                await self.generate_dataset(args)
            elif args.command == 'evaluate':
                await self.run_evaluation(args)
            elif args.command == 'full-pipeline':
                await self.run_full_pipeline(args)
            else:
                parser.print_help()
                
        except KeyboardInterrupt:
            print("\n❌ Evaluation interrupted by user")
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            print(f"\n❌ Evaluation failed: {e}")
            sys.exit(1)


async def main():
    """Main entry point."""
    cli = EvaluationCLI()
    await cli.run()


if __name__ == "__main__":
    asyncio.run(main()) 