"""
Oncall Lens: Oncall Incident Summarizer
FastAPI Backend Application

This is the main entry point for the Oncall Lens backend API.
It provides endpoints for uploading incident files and generating AI-powered summaries.
"""

import logging
from contextlib import asynccontextmanager
from typing import List, Optional
import asyncio
import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile, status, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.background import BackgroundTasks
import json

from models.api_models import (
    HealthResponse,
    IncidentSummaryRequest,
    IncidentSummaryResponse,
    ErrorResponse,
    ProcessedFile
)
from services.agent_service import AgentService
from services.file_processor import FileProcessor
from config.settings import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global services
agent_service: Optional[AgentService] = None
file_processor: Optional[FileProcessor] = None

# Progress tracking
progress_tasks: dict = {}

async def progress_stream(task_id: str):
    """Stream progress updates for a specific task."""
    while True:
        if task_id in progress_tasks:
            progress = progress_tasks[task_id]
            yield f"data: {json.dumps(progress)}\n\n"
            
            if progress.get("completed", False):
                del progress_tasks[task_id]
                break
        await asyncio.sleep(0.1)  # Check more frequently for real-time updates

def update_progress(task_id: str, stage: str, message: str, percentage: int = 0, completed: bool = False):
    """Update progress for a specific task."""
    progress_tasks[task_id] = {
        "task_id": task_id,
        "stage": stage,
        "message": message,
        "percentage": percentage,
        "completed": completed,
        "timestamp": asyncio.get_event_loop().time()
    }

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    Initializes services during startup and cleans up during shutdown.
    """
    global agent_service, file_processor
    
    logger.info("🚀 Starting Oncall Lens Backend...")
    
    try:
        # Initialize services
        settings = get_settings()
        file_processor = FileProcessor()
        agent_service = AgentService(settings)
        
        # Initialize RAG system and agents
        await agent_service.initialize()
        
        logger.info("✅ All services initialized successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        raise
    
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down Oncall Lens Backend...")
    if agent_service:
        await agent_service.cleanup()


# Create FastAPI app
app = FastAPI(
    title="Oncall Lens API",
    description="AI-powered incident analysis and summarization for on-call engineers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return HealthResponse(
        status="healthy",
        message="Oncall Lens backend is running",
        services={
            "agent_service": agent_service is not None and agent_service.is_healthy(),
            "file_processor": file_processor is not None
        }
    )


@app.get("/progress/{task_id}")
async def get_progress(task_id: str):
    """
    Server-Sent Events endpoint for real-time progress updates.
    """
    return StreamingResponse(
        progress_stream(task_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )

@app.post("/summarize")
async def create_incident_summary(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(..., description="Incident files (logs, diffs, screenshots, etc.)"),
    openai_api_key: Optional[str] = Form(None, description="OpenAI API key from frontend"),
    cohere_api_key: Optional[str] = Form(None, description="Cohere API key from frontend")
):
    """
    Main endpoint for incident analysis.
    
    Supports hybrid API key configuration:
    - API keys can be provided via frontend (openai_api_key, cohere_api_key parameters)
    - Falls back to server environment variables if not provided
    
    Returns immediately with a task_id, then runs analysis in background.
    Use the /progress/{task_id} endpoint to track progress.
    
    Args:
        files: List of uploaded files (logs, stack traces, diffs, screenshots, etc.)
        openai_api_key: Optional OpenAI API key from frontend
        cohere_api_key: Optional Cohere API key from frontend
        
    Returns:
        Task ID for tracking progress
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided. Please upload at least one incident file."
        )
    
    if not agent_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent service not available. Please try again later."
        )
    
    # Validate API keys - check both frontend and backend sources
    settings = get_settings()
    final_openai_key = openai_api_key or settings.openai_api_key
    
    if not final_openai_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OpenAI API key is required. Please provide it via the frontend settings or configure it on the server."
        )
    
    # Process files immediately before background task (to avoid file handle closure)
    logger.info(f"📁 Processing {len(files)} files before background analysis")
    try:
        processed_files = await file_processor.process_files(files)
        logger.info(f"✅ Successfully processed {len(processed_files)} files")
    except Exception as e:
        logger.error(f"❌ Failed to process files: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process uploaded files: {str(e)}"
        )
    
    # Generate task ID for progress tracking
    import uuid
    task_id = str(uuid.uuid4())
    
    logger.info(f"📁 Starting background analysis for {len(processed_files)} processed files, task_id: {task_id}")
    logger.info(f"🔑 Using API key source: {'frontend' if openai_api_key else 'server environment'}")
    
    # Initialize progress
    update_progress(task_id, "start", "Analysis request received...", 0)
    
    # Start background analysis with processed files and API keys
    background_tasks.add_task(run_analysis_background, task_id, processed_files, final_openai_key, cohere_api_key or settings.cohere_api_key)
    
    # Return immediately with task_id
    return {"task_id": task_id, "status": "started"}

async def run_analysis_background(task_id: str, processed_files: List[ProcessedFile], openai_api_key: Optional[str] = None, cohere_api_key: Optional[str] = None):
    """Run the analysis in the background with progress updates."""
    try:
        update_progress(task_id, "start", "Starting incident analysis...", 5)
        
        # Files are already processed, so skip file processing step
        update_progress(task_id, "processing", f"Using {len(processed_files)} processed files", 25)
        
        # Run agent analysis with progress updates and dynamic API keys
        update_progress(task_id, "analysis", "Initializing AI analysis...", 30)
        
        # Create progress callback for agent service
        def progress_callback(stage: str, message: str, percentage: int):
            update_progress(task_id, stage, message, percentage)
        
        summary_result = await agent_service.analyze_incident_with_progress(
            processed_files, progress_callback, openai_api_key, cohere_api_key
        )
        
        # Store the final result in progress_tasks for retrieval
        progress_tasks[task_id + "_result"] = {
            "summary": summary_result.summary,
            "confidence_score": summary_result.confidence_score,
            "root_causes": [rc.dict() for rc in summary_result.root_causes],
            "similar_incidents": [si.dict() for si in summary_result.similar_incidents],
            "recommendations": [r.dict() for r in summary_result.recommendations],
            "processing_time_ms": summary_result.processing_time_ms,
            "files_processed": len(processed_files)
        }
        
        update_progress(task_id, "complete", "Analysis completed successfully!", 100, completed=True)
        logger.info("✅ Background incident analysis completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Background analysis failed: {e}")
        update_progress(task_id, "error", f"Analysis failed: {str(e)}", 0, completed=True)


@app.get("/results/{task_id}")
async def get_analysis_results(task_id: str):
    """
    Get the final analysis results for a completed task.
    """
    result_key = task_id + "_result"
    
    if result_key in progress_tasks:
        result = progress_tasks[result_key]
        del progress_tasks[result_key]  # Clean up after retrieval
        return result
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Results not found. Task may not be completed yet."
        )

@app.get("/knowledge-base/stats")
async def get_knowledge_base_stats():
    """
    Get statistics about the knowledge base (postmortems, incidents, etc.)
    """
    if not agent_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent service not available"
        )
    
    try:
        stats = await agent_service.get_knowledge_base_stats()
        return stats
    except Exception as e:
        logger.error(f"❌ Error retrieving knowledge base stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve knowledge base statistics"
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """
    Global HTTP exception handler for consistent error responses.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            status_code=exc.status_code
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """
    Global exception handler for unexpected errors.
    """
    logger.error(f"❌ Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error occurred",
            status_code=500
        ).dict()
    )


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
