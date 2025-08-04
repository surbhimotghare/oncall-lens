# RAGAS Evaluation System for Oncall Lens

A comprehensive scientific evaluation framework for the Oncall Lens RAG system using RAGAS (Retrieval-Augmented Generation Assessment) metrics.

## 🎯 Overview

This evaluation system implements **Task 5** from the Oncall Lens plan: creating a golden test dataset and running scientific evaluation. It provides:

- **Synthetic Dataset Generation**: Automatically creates realistic Q&A pairs from historical postmortems
- **RAGAS Evaluation**: Measures RAG system performance with industry-standard metrics
- **Interactive Analysis**: Jupyter notebook for exploring results and generating insights
- **CLI Tools**: Command-line interface for automated evaluation workflows

## 📊 RAGAS Metrics

The system evaluates your RAG pipeline on six key metrics:

| Metric | Description | Good Score |
|--------|-------------|------------|
| **Faithfulness** | How well answers are grounded in retrieved context | > 0.8 |
| **Answer Relevancy** | How relevant answers are to the questions | > 0.8 |
| **Context Precision** | How precise/relevant the retrieved context is | > 0.8 |
| **Context Recall** | How complete the retrieved context is | > 0.8 |
| **Answer Similarity** | Semantic similarity with ground truth answers | > 0.7 |
| **Answer Correctness** | Factual correctness compared to ground truth | > 0.7 |

## 🏗️ Architecture

```
backend/evaluation/
├── dataset_generator.py    # Synthetic Q&A generation
├── ragas_evaluator.py     # RAGAS evaluation pipeline
├── cli.py                 # Command-line interface
├── evaluation_notebook.ipynb  # Interactive analysis
├── data/                  # Generated datasets
├── results/               # Evaluation results
└── README.md             # This file
```

## 🚀 Quick Start

### 1. Setup

Ensure all dependencies are installed:
```bash
cd backend
pip install -r requirements.txt
```

### 2. Generate Synthetic Dataset

```bash
cd backend/evaluation
python cli.py generate-dataset --knowledge-base ../data/knowledge-base --output ./data/synthetic_dataset.json
```

### 3. Run Evaluation

```bash
python cli.py evaluate --dataset ./data/synthetic_dataset.json --output-dir ./results
```

### 4. Full Pipeline

Run everything in one command:
```bash
python cli.py full-pipeline --knowledge-base ../data/knowledge-base --output-dir ./results
```

## 🧪 Detailed Usage

### Dataset Generation

The synthetic dataset generator creates realistic Q&A pairs from your postmortem knowledge base:

```python
from evaluation.dataset_generator import DatasetGenerator
from config.settings import get_settings

generator = DatasetGenerator(get_settings())

dataset = await generator.generate_full_dataset(
    knowledge_base_path="../data/knowledge-base",
    output_path="./data/synthetic_dataset.json",
    num_questions_per_category=3  # Per category: root_cause, resolution, impact, prevention, detection
)
```

**Generated Questions Categories:**
- **Root Cause**: "What was the root cause of the database failure?"
- **Resolution**: "How was the API incident resolved?"
- **Impact**: "What was the business impact of the outage?"
- **Prevention**: "What preventive measures were recommended?"
- **Detection**: "How was the incident detected?"

### RAGAS Evaluation

Run comprehensive evaluation on your RAG system:

```python
from evaluation.ragas_evaluator import RAGASEvaluator

evaluator = RAGASEvaluator(get_settings())

results = await evaluator.run_full_evaluation(
    dataset_path="./data/synthetic_dataset.json",
    output_dir="./results",
    run_name="baseline_evaluation"
)

print(f"Faithfulness: {results['scores']['faithfulness']:.3f}")
print(f"Answer Relevancy: {results['scores']['answer_relevancy']:.3f}")
```

### Interactive Analysis

Use the Jupyter notebook for detailed analysis:

```bash
jupyter notebook evaluation_notebook.ipynb
```

The notebook provides:
- Interactive visualizations
- Detailed Q&A pair analysis
- Performance recommendations
- Comparison tools

## 📈 Understanding Results

### Expected Baseline Results

Based on the plan, initial baseline results should look like:

| Metric | Score | Interpretation |
|--------|-------|----------------|
| Faithfulness | 0.91 | Excellent - answers well grounded |
| Answer Relevancy | 0.88 | Good - answers relevant to questions |
| Context Precision | 0.75 | **Needs improvement** - retrieval issue |
| Context Recall | 0.72 | **Needs improvement** - missing context |

### Interpreting Scores

- **> 0.9**: Excellent performance
- **0.8 - 0.9**: Good performance  
- **< 0.8**: Needs improvement

### Common Issues & Solutions

| Low Score | Problem | Solution |
|-----------|---------|----------|
| Context Precision | Irrelevant contexts retrieved | Implement hybrid search (semantic + keyword) |
| Context Recall | Missing relevant context | Use parent document retriever |
| Faithfulness | Answers not grounded | Improve prompt engineering |
| Answer Relevancy | Off-topic answers | Enhance question routing |

## 📁 Output Files

Each evaluation run creates:

```
results/
└── baseline_evaluation/
    ├── scores.json              # RAGAS metrics summary
    ├── detailed_results.csv     # Individual Q&A results
    └── evaluation_report.md     # Human-readable report
```

### Example `scores.json`:
```json
{
  "metadata": {
    "run_name": "baseline_evaluation", 
    "timestamp": "2024-01-15T10:30:00",
    "total_questions": 45,
    "model": "gpt-4o"
  },
  "scores": {
    "faithfulness": 0.875,
    "answer_relevancy": 0.823,
    "context_precision": 0.756,
    "context_recall": 0.701
  }
}
```

## 🔧 CLI Reference

### Generate Dataset
```bash
python cli.py generate-dataset [OPTIONS]

Options:
  --knowledge-base, -kb  Path to knowledge base directory
  --output, -o          Output path for dataset
  --questions-per-category, -q  Questions per category (default: 3)
```

### Run Evaluation
```bash
python cli.py evaluate [OPTIONS]

Options:
  --dataset, -d         Path to evaluation dataset
  --output-dir, -o      Output directory for results
  --run-name, -n        Name for this evaluation run
```

### Full Pipeline
```bash
python cli.py full-pipeline [OPTIONS]

Options:
  --knowledge-base, -kb  Path to knowledge base directory
  --output-dir, -o      Output directory for all results
  --questions-per-category, -q  Questions per category
  --run-name, -n        Name for this evaluation run
```

## 🎯 Advanced Usage

### Custom Evaluation Metrics

Add custom metrics to the evaluator:

```python
from ragas.metrics import answer_correctness
from evaluation.ragas_evaluator import RAGASEvaluator

class CustomEvaluator(RAGASEvaluator):
    def __init__(self, settings):
        super().__init__(settings)
        self.metrics.append(answer_correctness)  # Add custom metric
```

### Batch Evaluation

Run multiple evaluation configurations:

```python
configurations = [
    {"run_name": "baseline", "questions_per_category": 3},
    {"run_name": "extended", "questions_per_category": 5},
    {"run_name": "comprehensive", "questions_per_category": 10}
]

for config in configurations:
    results = await evaluator.run_full_evaluation(
        dataset_path=dataset_path,
        output_dir="./results",
        **config
    )
```

### A/B Testing Different RAG Configurations

```python
# Test different retrieval strategies
configs = {
    "semantic_only": {"retrieval_type": "semantic"},
    "hybrid_search": {"retrieval_type": "hybrid"},
    "parent_document": {"retrieval_type": "parent_doc"}
}

for name, config in configs.items():
    # Update RAG configuration
    # Run evaluation
    results = await evaluator.run_full_evaluation(...)
```

## 🚦 CI/CD Integration

### GitHub Actions Example

```yaml
name: RAG Evaluation
on: [push, pull_request]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r backend/requirements.txt
      - name: Run RAGAS evaluation
        run: |
          cd backend/evaluation
          python cli.py full-pipeline --output-dir ./ci-results
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: evaluation-results
          path: backend/evaluation/ci-results/
```

## 🐛 Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   ```bash
   export OPENAI_API_KEY="your-key-here"
   ```

2. **Qdrant Connection Error**
   - Ensure Qdrant is running
   - Check connection settings in `config/settings.py`

3. **Memory Issues with Large Datasets**
   - Reduce `num_questions_per_category`
   - Process in smaller batches

4. **RAGAS Import Errors**
   ```bash
   pip install --upgrade ragas datasets
   ```

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔄 Continuous Improvement

### Regular Evaluation Schedule

Set up automated evaluations:

1. **Weekly**: Run baseline evaluation
2. **Before Releases**: Full comprehensive evaluation  
3. **After Changes**: Targeted evaluation of affected components

### Metrics Tracking

Track metrics over time:

```python
# Store results in database
results_history = []
results_history.append({
    "timestamp": datetime.now(),
    "scores": eval_results["scores"],
    "version": "v1.2.0"
})
```

### Performance Monitoring

Monitor key thresholds:

- **Alert if Faithfulness < 0.8**
- **Alert if Context Recall < 0.7**
- **Weekly trend analysis**

## 📚 Next Steps

After establishing baseline evaluation:

1. **Implement Advanced Retrieval** (Task 6)
   - Hybrid search
   - Parent document retriever
   - Multi-query retrieval

2. **Re-evaluate Improvements**
   - Compare with baseline
   - Measure impact of changes
   - Document improvements

3. **Production Monitoring**
   - Real-time evaluation
   - User feedback integration
   - A/B testing framework

## 🤝 Contributing

To contribute to the evaluation system:

1. Add new synthetic question categories
2. Implement custom RAGAS metrics
3. Create evaluation visualizations
4. Improve documentation

---

## 📞 Support

For questions about the evaluation system:

1. Check the troubleshooting section
2. Review the example notebook
3. Examine the CLI help: `python cli.py --help`

**Happy Evaluating! 🚀** 