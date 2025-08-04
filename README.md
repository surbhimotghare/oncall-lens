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
└── README.md                # This file
```

## 🚀 Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Next.js (React/TypeScript) 
- **AI Orchestration**: LangChain + LangGraph
- **LLM**: OpenAI GPT-4o
- **Embeddings**: OpenAI text-embedding-3-small
- **Vector DB**: Qdrant
- **Evaluation**: RAGAS
- **Monitoring**: LangSmith

## 🎯 Features

- **Multi-Modal File Processing**: Handles logs, stack traces, code diffs, and screenshots
- **Intelligent Agent System**: 4-agent workflow for comprehensive incident analysis
- **Historical Context**: RAG-powered search through past incident postmortems
- **Root Cause Analysis**: AI-powered identification of likely failure causes
- **Actionable Recommendations**: Prioritized next steps for incident resolution

## 🔧 Development Setup

### Prerequisites
- Python 3.13+
- Node.js 18+ (for frontend)
- Qdrant server (Docker recommended)
- OpenAI API key

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Configuration
```bash
cp .env.template .env
# Edit .env with your API keys:
# ONCALL_OPENAI_API_KEY=your_openai_api_key_here
```

### Start Qdrant (Docker)
```bash
docker run -p 6333:6333 qdrant/qdrant
```

### Start Backend Server
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Visit `http://localhost:8000/docs` for interactive API documentation.

## 📊 Current Implementation Status

### ✅ Completed
- [x] **Phase 1**: Backend foundation with FastAPI
- [x] **Phase 2**: Multi-agent system with LangGraph  
- [x] **Phase 3**: File processing pipeline
- [x] **Phase 4**: RAG integration with Qdrant
- [x] **Phase 5**: OpenAI integration (GPT-4o + embeddings)

### 🔄 In Progress  
- [ ] **Phase 6**: RAGAS evaluation pipeline
- [ ] **Phase 7**: Frontend Next.js application
- [ ] **Phase 8**: Advanced retrieval techniques
- [ ] **Phase 9**: Production deployment

## 🎮 Usage

### API Endpoints

#### Health Check
```bash
GET /health
```

#### Analyze Incident Files
```bash
POST /summarize
Content-Type: multipart/form-data
Files: logs, stack traces, diffs, etc.
```

#### Knowledge Base Stats
```bash
GET /knowledge-base/stats
```

## 🧪 Sample Data

The project includes realistic sample incident files for testing:

- **Postmortems**: Historical incident reports from major tech companies
- **Log Files**: Java application logs with database connection errors
- **Stack Traces**: HikariCP connection pool timeout exceptions
- **Code Diffs**: Bug fixes showing resource leak corrections
- **Metrics**: CPU/memory/database connection metrics during incidents

## 🤖 Agent Architecture

The system uses a 4-agent workflow powered by LangGraph:

1. **Data Triage Agent**: Extracts key information from uploaded files
2. **Historical Analyst Agent**: Searches for similar past incidents using RAG
3. **Root Cause Analyzer**: Identifies likely failure causes with confidence scores
4. **Synthesizer Agent**: Generates actionable recommendations and final summary

## 📈 Performance & Evaluation

- **RAGAS Metrics**: Faithfulness, Answer Relevancy, Context Recall, Context Precision
- **Processing Time**: < 30 seconds for typical incident analysis
- **Similarity Threshold**: 0.7 (configurable)
- **Vector Dimensions**: 1536 (OpenAI text-embedding-3-small)

## 🛠️ Development Notes

### Project Architecture
- **Async-first**: All I/O operations are asynchronous for performance
- **Type Safety**: Full Pydantic model validation throughout
- **Error Handling**: Comprehensive logging and graceful failure recovery
- **Configuration**: Environment-based settings with .env support

### Vector Database
- **Engine**: Qdrant with cosine similarity
- **Batch Processing**: 100 documents per batch for efficient indexing
- **Collection Management**: Automatic creation with proper vector configuration

### LLM Integration
- **Model**: GPT-4o with 4000 token limit
- **Temperature**: 0.1 for consistent, focused responses
- **Prompts**: Role-specific system prompts for each agent

## 🚀 Getting Started

1. **Clone and setup**:
   ```bash
   git clone <repo-url>
   cd oncall-lens/backend
   python -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.template .env
   # Add your OpenAI API key to .env
   ```

3. **Start Qdrant**:
   ```bash
   docker run -p 6333:6333 qdrant/qdrant
   ```

4. **Run the backend**:
   ```bash
   uvicorn main:app --reload
   ```

5. **Test with sample data**:
   - Visit `http://localhost:8000/docs`
   - Upload files from `data/sample-incident-1/`
   - Get AI-powered incident analysis!

## 📝 License

This project is part of the AI Engineering certification challenge.

---

**Built with ❤️ for on-call engineers everywhere** 🚀
