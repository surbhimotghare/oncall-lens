"""
API Models for Oncall Lens
Pydantic models defining request/response schemas for the FastAPI endpoints.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Service health status")
    message: str = Field(..., description="Human-readable status message")
    services: Dict[str, bool] = Field(..., description="Status of individual services")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ProcessedFile(BaseModel):
    """Model representing a processed incident file."""
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="Type of file (log, diff, stack_trace, etc.)")
    content: str = Field(..., description="Processed file content")
    size_bytes: int = Field(..., description="File size in bytes")
    processing_notes: Optional[str] = Field(None, description="Notes from file processing")


class SimilarIncident(BaseModel):
    """Model representing a similar historical incident."""
    title: str = Field(..., description="Incident title")
    similarity_score: float = Field(..., description="Similarity score (0-1)")
    date: Optional[str] = Field(None, description="Incident date")
    root_cause: Optional[str] = Field(None, description="Root cause summary")
    resolution: Optional[str] = Field(None, description="How it was resolved")
    source_file: Optional[str] = Field(None, description="Source postmortem file")


class RootCause(BaseModel):
    """Model representing an identified root cause."""
    category: str = Field(..., description="Category of root cause (e.g., 'Configuration', 'Code Bug')")
    description: str = Field(..., description="Detailed description of the root cause")
    confidence: float = Field(..., description="Confidence score (0-1)")
    evidence: List[str] = Field(default_factory=list, description="Evidence supporting this root cause")


class Recommendation(BaseModel):
    """Model representing an actionable recommendation."""
    priority: str = Field(..., description="Priority level (P0, P1, P2)")
    category: str = Field(..., description="Category (immediate, short-term, long-term)")
    action: str = Field(..., description="Recommended action")
    rationale: str = Field(..., description="Why this action is recommended")


class IncidentSummaryRequest(BaseModel):
    """Request model for incident summarization (if needed for additional metadata)."""
    description: Optional[str] = Field(None, description="Optional incident description")
    urgency: Optional[str] = Field("medium", description="Incident urgency level")
    tags: List[str] = Field(default_factory=list, description="Optional tags for categorization")


class IncidentAnalysisResult(BaseModel):
    """Internal model for agent analysis results."""
    summary: str
    confidence_score: float
    root_causes: List[RootCause]
    similar_incidents: List[SimilarIncident]
    recommendations: List[Recommendation]
    processing_time_ms: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IncidentSummaryResponse(BaseModel):
    """Response model for incident analysis endpoint."""
    summary: str = Field(..., description="AI-generated incident summary")
    confidence_score: float = Field(..., description="Overall confidence in the analysis (0-1)")
    root_causes: List[RootCause] = Field(..., description="Identified root causes")
    similar_incidents: List[SimilarIncident] = Field(..., description="Similar historical incidents")
    recommendations: List[Recommendation] = Field(..., description="Actionable recommendations")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    files_processed: int = Field(..., description="Number of files processed")
    task_id: Optional[str] = Field(None, description="Task ID for progress tracking")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class KnowledgeBaseStats(BaseModel):
    """Response model for knowledge base statistics."""
    total_postmortems: int = Field(..., description="Total number of postmortems in knowledge base")
    total_incidents: int = Field(..., description="Total number of incidents indexed")
    last_updated: datetime = Field(..., description="When the knowledge base was last updated")
    vector_store_size: int = Field(..., description="Number of vectors in the store")
    categories: Dict[str, int] = Field(..., description="Breakdown by incident categories")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Agent-specific models

class AgentMessage(BaseModel):
    """Model for inter-agent communication."""
    agent_id: str = Field(..., description="ID of the sending agent")
    message_type: str = Field(..., description="Type of message")
    content: Dict[str, Any] = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentState(BaseModel):
    """Model representing the current state of the agent system."""
    current_step: str = Field(..., description="Current processing step")
    processed_files: List[ProcessedFile] = Field(default_factory=list)
    analysis_results: Dict[str, Any] = Field(default_factory=dict)
    messages: List[AgentMessage] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict) 