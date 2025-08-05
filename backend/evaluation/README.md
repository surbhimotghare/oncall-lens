# RAGAS Evaluation System for Oncall Lens

Scientific evaluation of RAG system performance using RAGAS metrics.

## Overview

This evaluation system provides comprehensive assessment of the Oncall Lens RAG pipeline using the RAGAS framework. It includes synthetic data generation, RAGAS evaluation, and detailed reporting.

## Quick Start

### 1. Setup Environment
```bash
source setup_env.sh
```

### 2. Generate Synthetic Dataset
```bash
python3 cli.py generate-dataset \
  --knowledge-base ../data/knowledge-base \
  --output ./data/synthetic_dataset.json \
  --questions-per-category 3
```

### 3. Run Baseline Evaluation
```bash
python3 baseline_eval.py
```

## Core Components

### `baseline_eval.py` - Main Evaluation Script
The primary evaluation script that runs RAGAS assessment with optimized settings:
- Uses similarity threshold of 0.5 (optimized from default 0.7)
- Evaluates 6 questions for comprehensive metrics
- Provides detailed comparison with expected baseline results
- Saves results to `./results/improved_threshold_baseline/`

### `ragas_evaluator.py` - Core Evaluation Logic
Contains the `RAGASEvaluator` class with methods for:
- Loading synthetic datasets
- Running RAG pipeline evaluations
- Computing RAGAS metrics
- Generating detailed reports

### `dataset_generator.py` - Synthetic Data Generation
Creates realistic Q&A pairs from postmortem documents:
- 5 categories: root_cause, resolution, impact, prevention, detection
- Uses GPT-4o for high-quality generation
- Structured output for RAGAS evaluation

### `cli.py` - Command Line Interface
Provides commands for:
- `generate-dataset`: Create synthetic evaluation data
- `evaluate`: Run RAGAS evaluation
- `full-pipeline`: Complete workflow

## Baseline Results

Our optimized baseline evaluation achieved:

| Metric | Score | Status |
|--------|-------|--------|
| Context Precision | 0.750 | 🟢 **Meets Expectations** |
| Context Recall | 0.833 | 🟢 **Exceeded Expectations** |
| Faithfulness | 0.267 | 🔴 Needs Improvement |
| Answer Relevancy | 0.518 | 🔴 Needs Improvement |

## Key Findings

1. **Retrieval System Excellence**: Context Precision (0.750) and Recall (0.833) exceed targets
2. **Similarity Threshold Optimization**: Lowering from 0.7 to 0.5 unlocked full potential
3. **Generation Pipeline Focus**: Faithfulness and Answer Relevancy need improvement
4. **Knowledge Base Quality**: 26+ document chunks provide excellent coverage

## Usage Examples

### Generate Dataset
```bash
python3 cli.py generate-dataset \
  --knowledge-base ../data/knowledge-base \
  --output ./data/synthetic_dataset.json \
  --questions-per-category 4
```

### Run Evaluation
```bash
python3 baseline_eval.py
```

### Check Results
```bash
ls -la results/improved_threshold_baseline/
cat results/improved_threshold_baseline/scores.json
```

## Output Files

Evaluation results are saved to `./results/` with:
- `scores.json`: RAGAS metrics summary
- `detailed_results.csv`: Question-by-question breakdown
- `evaluation_report.md`: Comprehensive analysis

## LangSmith Integration

All evaluations are tracked in LangSmith:
- Project: `oncall-lens`
- Traces: RAGAS evaluation runs
- Metrics: Detailed performance analysis

## Next Steps

Based on baseline results, focus on:
1. **Prompt Engineering**: Improve RAG prompts for better context utilization
2. **Answer Generation**: Enhance LLM response quality
3. **Advanced Retrieval**: Implement hybrid search and parent document retriever 