"""
Oncall Lens: Oncall Incident Summarizer
FastAPI Backend Application

This is the main entry point for the Oncall Lens backend API.
It provides endpoints for uploading incident files and generating AI-powered summaries.
"""

import logging
from contextlib import asynccontextmanager
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from models.api_models import (
    HealthResponse,
    IncidentSummaryRequest,
    IncidentSummaryResponse,
    ErrorResponse
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


@app.post("/summarize", response_model=IncidentSummaryResponse)
async def create_incident_summary(
    files: List[UploadFile] = File(..., description="Incident files (logs, diffs, screenshots, etc.)")
):
    """
    Main endpoint for incident analysis.
    
    Accepts multiple files related to an incident and returns an AI-generated summary
    with historical context and actionable recommendations.
    
    Args:
        files: List of uploaded files (logs, stack traces, diffs, screenshots, etc.)
        
    Returns:
        IncidentSummaryResponse with analysis results
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
    
    try:
        logger.info(f"📁 Processing {len(files)} files for incident analysis")
        
        # Process uploaded files
        processed_files = await file_processor.process_files(files)
        
        # Run agent analysis
        summary_result = await agent_service.analyze_incident(processed_files)
        
        logger.info("✅ Incident analysis completed successfully")
        
        return IncidentSummaryResponse(
            summary=summary_result.summary,
            confidence_score=summary_result.confidence_score,
            root_causes=summary_result.root_causes,
            similar_incidents=summary_result.similar_incidents,
            recommendations=summary_result.recommendations,
            processing_time_ms=summary_result.processing_time_ms,
            files_processed=len(files)
        )
        
    except ValueError as e:
        logger.error(f"❌ Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error during incident analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred during analysis"
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
