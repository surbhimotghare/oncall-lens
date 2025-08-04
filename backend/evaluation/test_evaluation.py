#!/usr/bin/env python3
"""
Test script for RAGAS Evaluation System
Runs quick tests to verify the evaluation system is working correctly.
"""

import asyncio
import sys
import os
import json
import logging
from pathlib import Path

# Add backend to path for imports
sys.path.append('..')

from config.settings import get_settings
from evaluation.dataset_generator import DatasetGenerator
from evaluation.ragas_evaluator import RAGASEvaluator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_dataset_generation():
    """Test synthetic dataset generation."""
    print("🧪 Testing Dataset Generation...")
    
    try:
        settings = get_settings()
        generator = DatasetGenerator(settings)
        
        # Test with minimal dataset
        test_output = "./test_data/test_dataset.json"
        Path(test_output).parent.mkdir(parents=True, exist_ok=True)
        
        dataset = await generator.generate_full_dataset(
            knowledge_base_path="../data/knowledge-base",
            output_path=test_output,
            num_questions_per_category=1  # Small test
        )
        
        # Verify dataset structure
        assert 'metadata' in dataset
        assert 'questions' in dataset
        assert 'answers' in dataset
        assert 'ground_truths' in dataset
        assert 'contexts' in dataset
        
        assert len(dataset['questions']) > 0
        assert len(dataset['questions']) == len(dataset['answers'])
        assert len(dataset['questions']) == len(dataset['ground_truths'])
        assert len(dataset['questions']) == len(dataset['contexts'])
        
        print(f"✅ Dataset generation test passed! Generated {len(dataset['questions'])} Q&A pairs")
        return True
        
    except Exception as e:
        print(f"❌ Dataset generation test failed: {e}")
        return False


async def test_ragas_evaluation():
    """Test RAGAS evaluation with minimal dataset."""
    print("🧪 Testing RAGAS Evaluation...")
    
    try:
        # Create minimal test dataset
        test_dataset = {
            "metadata": {
                "total_questions": 2,
                "generated_at": "2024-01-01T00:00:00",
                "test": True
            },
            "questions": [
                "What was the root cause of the database outage?",
                "How was the incident resolved?"
            ],
            "answers": [
                "The root cause was connection pool exhaustion due to a memory leak.",
                "The incident was resolved by restarting the database service and applying a hotfix."
            ],
            "ground_truths": [
                "Connection pool exhaustion caused by memory leak in the database driver.",
                "Resolution involved service restart and deployment of memory leak fix."
            ],
            "contexts": [
                ["Database connection pool reached maximum capacity of 100 connections. Memory leak detected in connection cleanup code."],
                ["Service was restarted at 14:30 UTC. Hotfix deployed at 15:00 UTC containing memory leak fix."]
            ]
        }
        
        # Save test dataset
        test_dataset_path = "./test_data/minimal_test_dataset.json"
        Path(test_dataset_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(test_dataset_path, 'w') as f:
            json.dump(test_dataset, f, indent=2)
        
        # Test evaluation (without initializing full RAG system)
        settings = get_settings()
        evaluator = RAGASEvaluator(settings)
        
        # Load dataset
        dataset = evaluator.load_synthetic_dataset(test_dataset_path)
        assert dataset is not None
        assert len(dataset['questions']) == 2
        
        print("✅ RAGAS evaluation setup test passed!")
        print("⚠️  Note: Full evaluation test requires running RAG system")
        return True
        
    except Exception as e:
        print(f"❌ RAGAS evaluation test failed: {e}")
        return False


def test_imports():
    """Test that all required imports work."""
    print("🧪 Testing Imports...")
    
    try:
        # Test core imports
        from evaluation.dataset_generator import DatasetGenerator
        from evaluation.ragas_evaluator import RAGASEvaluator
        from config.settings import get_settings
        
        # Test RAGAS imports
        from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
        from datasets import Dataset
        import pandas as pd
        
        # Test LangChain imports
        from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        from langchain_core.prompts import ChatPromptTemplate
        
        print("✅ All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        print("💡 Try: pip install -r requirements.txt")
        return False


def test_configuration():
    """Test configuration and environment setup."""
    print("🧪 Testing Configuration...")
    
    try:
        settings = get_settings()
        
        # Check required settings
        required_attrs = ['openai_api_key', 'qdrant_collection_name']
        for attr in required_attrs:
            if not hasattr(settings, attr):
                raise ValueError(f"Missing required setting: {attr}")
        
        # Check OpenAI API key
        if not settings.openai_api_key or settings.openai_api_key == "your-openai-api-key":
            print("⚠️  OpenAI API key not configured")
            print("💡 Set OPENAI_API_KEY environment variable")
            return False
        
        # Check knowledge base exists
        kb_path = Path("../data/knowledge-base")
        if not kb_path.exists():
            print(f"⚠️  Knowledge base not found at {kb_path}")
            return False
        
        # Count postmortem files
        postmortem_files = list(kb_path.glob("*.md"))
        non_template_files = [f for f in postmortem_files if not f.name.startswith("postmortem-template")]
        
        if len(non_template_files) == 0:
            print("⚠️  No postmortem files found in knowledge base")
            return False
        
        print(f"✅ Configuration test passed! Found {len(non_template_files)} postmortem files")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


async def run_all_tests():
    """Run all tests in sequence."""
    print("🚀 Running RAGAS Evaluation System Tests\n")
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_configuration),
        ("Dataset Generation", test_dataset_generation),
        ("RAGAS Evaluation", test_ragas_evaluation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running {test_name} Test")
        print('='*60)
        
        if asyncio.iscoroutinefunction(test_func):
            result = await test_func()
        else:
            result = test_func()
            
        results.append((test_name, result))
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\n🎉 All tests passed! The evaluation system is ready to use.")
        print("\n📚 Next steps:")
        print("1. Run: python cli.py full-pipeline --knowledge-base ../data/knowledge-base --output-dir ./results")
        print("2. Or use the demo: python demo.py")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues before running evaluations.")
        return False
    
    # Cleanup test files
    import shutil
    test_data_path = Path("./test_data")
    if test_data_path.exists():
        shutil.rmtree(test_data_path)
        print("\n🧹 Test files cleaned up")
    
    return passed == len(tests)


if __name__ == "__main__":
    asyncio.run(run_all_tests()) 