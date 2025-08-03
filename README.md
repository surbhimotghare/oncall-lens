# Oncall Lens: Oncall Incident Summarizer

An intelligent web application that acts as an expert assistant for on-call engineers during incident response. Upload incident artifacts (logs, stack traces, diffs, screenshots) and get AI-powered summaries with historical context.

## 🏗️ Project Structure

```
oncall-lens/
├── backend/                    # FastAPI backend
│   ├── main.py                # Main FastAPI application
│   ├── requirements.txt       # Python dependencies
│   ├── agents/               # LangGraph agent implementations
│   ├── services/             # Business logic services
│   ├── models/              # Data models and schemas
│   └── data/
│       ├── knowledge-base/   # Historical postmortem files (.md)
│       └── sample-incident-1/ # Test incident files
├── frontend/                 # Next.js frontend (coming soon)
└── README.md
```

## 🚀 Quick Start

### 1. Download Starter Kit Files

You need to manually download these files to test the system:

#### Historical Knowledge Base (for RAG)
**Location**: `backend/data/knowledge-base/`

1. **GitHub Postmortems Repository**: https://github.com/dastergon/postmortems
   - Download 3-5 `.md` files from different companies (GitLab, Google, etc.)
   - Save them in `backend/data/knowledge-base/`

#### Sample Incident Files  
**Location**: `backend/data/sample-incident-1/`

1. **Log File**: 
   - URL: https://raw.githubusercontent.com/logpai/loghub/master/HDFS/HDFS_1k.log
   - Save as: `HDFS_1k.log`

2. **Diff File**:
   - URL: https://github.com/psf/requests/commit/c0c4b7062e57c83344655a13c32791485a73dd70.diff
   - Save as: `bugfix.diff`

3. **Stack Trace**:
   - URL: https://gist.github.com/gregmalcolm/5565391
   - Copy the text content and save as: `stack_trace.txt`

4. **Metric Graph**:
   - URL: https://grafana.com/static/assets/img/blog/mixed-data-source-cpu-usage.png
   - Save as: `cpu_spike.png`

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the backend directory:

```bash
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here  # Optional for external search
```

### 4. Run the Backend

```bash
uvicorn main:app --reload --port 8000
```

### 5. Test the System

Upload the sample incident files to `/summarize` endpoint and get an AI-powered incident summary!

## 🧠 How It Works

1. **Data Triage Agent**: Processes different file types (logs, diffs, images, text)
2. **Historical Analyst Agent**: Uses RAG to search through postmortem knowledge base
3. **External Researcher Agent**: Searches public documentation for unknown errors
4. **Manager Agent**: Orchestrates the entire workflow
5. **Synthesizer Agent**: Generates final incident summary

## 🛠️ Technology Stack

- **Backend**: FastAPI, LangChain, LangGraph
- **LLM**: OpenAI GPT-4o (multi-modal)
- **Vector DB**: ChromaDB
- **Embeddings**: OpenAI text-embedding-3-small
- **Evaluation**: RAGAS
- **Frontend**: Next.js (coming soon)

## 📊 Expected Output

When you upload the starter kit files, expect a summary like:

> *"The KeyError in stack_trace.txt suggests a missing dictionary key during request processing. The CPU spike in cpu_spike.png indicates resource exhaustion around the same timeframe. The changes in bugfix.diff show recent modifications to error handling in the requests library. Based on historical analysis, similar incidents occurred in the GitLab postmortem from July 15th, involving KeyError exceptions during high load periods. Recommended next steps: Check request payload validation and increase resource limits."*

## 🎯 Development Phases

- [x] **Phase 1**: Project setup and starter kit
- [ ] **Phase 2**: Basic FastAPI backend with file upload
- [ ] **Phase 3**: Multi-modal agent pipeline with LangGraph
- [ ] **Phase 4**: RAG integration with ChromaDB
- [ ] **Phase 5**: Advanced retrieval techniques
- [ ] **Phase 6**: RAGAS evaluation pipeline
- [ ] **Phase 7**: Next.js frontend
- [ ] **Phase 8**: Production deployment

## 📝 License

MIT License - See LICENSE file for details
