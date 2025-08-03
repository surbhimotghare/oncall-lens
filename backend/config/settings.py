"""
Configuration settings for Oncall Lens backend.
Uses Pydantic Settings to manage environment variables and configuration.
"""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    
    # Application settings
    app_name: str = Field(default="Oncall Lens", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    
    # API settings
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    
    # OpenAI settings
    openai_api_key: str = Field(..., description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o", description="OpenAI model to use")
    openai_embedding_model: str = Field(default="text-embedding-3-small", description="OpenAI embedding model")
    openai_max_tokens: int = Field(default=4000, description="Max tokens for OpenAI responses")
    openai_temperature: float = Field(default=0.1, description="Temperature for OpenAI responses")
    
    # LangSmith settings (optional)
    langsmith_api_key: Optional[str] = Field(default=None, description="LangSmith API key for tracing")
    langsmith_project: str = Field(default="oncall-lens", description="LangSmith project name")
    
    # ChromaDB settings
    chromadb_persist_directory: str = Field(
        default="./chroma_db", 
        description="Directory to persist ChromaDB data"
    )
    chromadb_collection_name: str = Field(
        default="oncall_postmortems", 
        description="ChromaDB collection name"
    )
    
    # Data paths
    knowledge_base_path: str = Field(
        default="./data/knowledge-base",
        description="Path to knowledge base files (postmortems)"
    )
    sample_data_path: str = Field(
        default="./data/sample-incident-1",
        description="Path to sample incident data"
    )
    
    # File processing settings
    max_file_size_mb: int = Field(default=50, description="Maximum file size in MB")
    supported_file_types: List[str] = Field(
        default=[".txt", ".log", ".md", ".diff", ".patch", ".json", ".csv", ".png", ".jpg", ".jpeg"],
        description="Supported file extensions"
    )
    
    # Agent settings
    max_processing_time_seconds: int = Field(
        default=300, 
        description="Maximum processing time for incident analysis"
    )
    similarity_threshold: float = Field(
        default=0.7, 
        description="Similarity threshold for finding related incidents"
    )
    max_similar_incidents: int = Field(
        default=5, 
        description="Maximum number of similar incidents to return"
    )
    
    # RAG settings
    chunk_size: int = Field(default=1000, description="Text chunk size for embeddings")
    chunk_overlap: int = Field(default=200, description="Overlap between text chunks")
    top_k_retrieval: int = Field(default=5, description="Number of chunks to retrieve")
    
    # RAGAS evaluation settings
    ragas_metrics: List[str] = Field(
        default=["answer_relevancy", "faithfulness", "context_recall", "context_precision"],
        description="RAGAS metrics to use for evaluation"
    )
    
    # Security settings
    cors_origins: List[str] = Field(
        default=["http://localhost:3000"], 
        description="Allowed CORS origins"
    )
    
    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    
    class Config:
        env_file = ".env"
        env_prefix = "ONCALL_"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.
    This function is cached so settings are only loaded once.
    """
    return Settings()


def create_env_template():
    """
    Create a template .env file with all required environment variables.
    Useful for setup and documentation.
    """
    template = """# Oncall Lens Environment Variables
# Copy this file to .env and fill in your values

# OpenAI API Configuration (Required)
ONCALL_OPENAI_API_KEY=your_openai_api_key_here
ONCALL_OPENAI_MODEL=gpt-4o
ONCALL_OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# LangSmith Configuration (Optional)
# ONCALL_LANGSMITH_API_KEY=your_langsmith_api_key_here
# ONCALL_LANGSMITH_PROJECT=oncall-lens

# Application Configuration
ONCALL_DEBUG=false
ONCALL_API_HOST=0.0.0.0
ONCALL_API_PORT=8000

# Database Configuration
ONCALL_CHROMADB_PERSIST_DIRECTORY=./chroma_db
ONCALL_CHROMADB_COLLECTION_NAME=oncall_postmortems

# File Processing Configuration
ONCALL_MAX_FILE_SIZE_MB=50

# Agent Configuration
ONCALL_MAX_PROCESSING_TIME_SECONDS=300
ONCALL_SIMILARITY_THRESHOLD=0.7
ONCALL_MAX_SIMILAR_INCIDENTS=5

# RAG Configuration
ONCALL_CHUNK_SIZE=1000
ONCALL_CHUNK_OVERLAP=200
ONCALL_TOP_K_RETRIEVAL=5

# Logging
ONCALL_LOG_LEVEL=INFO
"""
    
    env_path = ".env.template"
    with open(env_path, "w") as f:
        f.write(template)
    
    print(f"✅ Created environment template at {env_path}")
    print("Copy this file to .env and fill in your values")


if __name__ == "__main__":
    # Create environment template when run directly
    create_env_template() 