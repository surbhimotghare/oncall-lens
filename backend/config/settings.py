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
    
    # Cohere settings (optional, for advanced retrieval)
    cohere_api_key: Optional[str] = Field(default=None, description="Cohere API key for reranking")
    
    # LangSmith settings (optional)
    langsmith_api_key: Optional[str] = Field(default=None, description="LangSmith API key for tracing")
    langsmith_project: str = Field(default="oncall-lens", description="LangSmith project name")
    
    # Qdrant settings (replacing ChromaDB)
    qdrant_host: str = Field(default="localhost", description="Qdrant server host")
    qdrant_port: int = Field(default=6333, description="Qdrant server port")
    qdrant_grpc_port: int = Field(default=6334, description="Qdrant gRPC port")
    qdrant_api_key: Optional[str] = Field(default=None, description="Qdrant API key (for cloud)")
    qdrant_https: bool = Field(default=False, description="Use HTTPS for Qdrant connection")
    qdrant_collection_name: str = Field(
        default="oncall_postmortems", 
        description="Qdrant collection name for postmortems"
    )
    qdrant_vector_size: int = Field(default=1536, description="Vector size for embeddings")
    qdrant_distance_metric: str = Field(default="Cosine", description="Distance metric for vector similarity")
    
    # Data paths
    knowledge_base_path: str = Field(
        default="./data/knowledge-base",
        description="Path to the knowledge base directory"
    )
    upload_path: str = Field(
        default="./data/uploads",
        description="Path to store uploaded files"
    )
    
    # RAG settings
    chunk_size: int = Field(default=1500, description="Chunk size for document splitting")
    chunk_overlap: int = Field(default=200, description="Overlap between chunks")
    similarity_threshold: float = Field(default=0.5, description="Similarity threshold for retrieval")
    max_docs_per_query: int = Field(default=5, description="Maximum documents to retrieve per query")
    
    # Agent settings
    max_agent_iterations: int = Field(default=10, description="Maximum iterations for agent")
    agent_timeout: int = Field(default=300, description="Agent timeout in seconds")
    
    # Evaluation settings
    evaluation_dataset_size: int = Field(default=30, description="Size of evaluation dataset")
    evaluation_batch_size: int = Field(default=5, description="Batch size for evaluation")
    
    # External API settings
    tavily_api_key: Optional[str] = Field(default=None, description="Tavily Search API key")
    
    # Security settings
    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        description="Secret key for JWT tokens"
    )
    access_token_expire_minutes: int = Field(
        default=30,
        description="Access token expiration in minutes"
    )
    
    # CORS settings
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="Allowed CORS origins"
    )
    
    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Optional[str] = Field(default=None, description="Log file path")
    
    # File upload settings
    max_file_size: int = Field(default=10 * 1024 * 1024, description="Max file size in bytes (10MB)")
    allowed_file_types: List[str] = Field(
        default=[".txt", ".log", ".diff", ".png", ".jpg", ".jpeg", ".pdf"],
        description="Allowed file extensions"
    )
    
    # Rate limiting
    rate_limit_requests: int = Field(default=100, description="Rate limit requests per minute")
    rate_limit_window: int = Field(default=60, description="Rate limit window in seconds")

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


def get_settings_no_cache() -> Settings:
    """
    Get application settings without caching.
    Useful for testing when environment variables change dynamically.
    """
    return Settings()


def create_env_template():
    """Create a template .env file with all available settings."""
    template_content = """# Oncall Lens Environment Configuration

# OpenAI Configuration (Required)
ONCALL_OPENAI_API_KEY=your_openai_api_key_here

# Cohere Configuration (For Advanced Retrieval)
ONCALL_COHERE_API_KEY=your_cohere_api_key_here

# LangSmith Configuration (Optional)
ONCALL_LANGSMITH_API_KEY=your_langsmith_api_key_here
ONCALL_LANGSMITH_PROJECT=oncall-lens

# Qdrant Configuration
ONCALL_QDRANT_HOST=localhost
ONCALL_QDRANT_PORT=6333
ONCALL_QDRANT_GRPC_PORT=6334

# Application Configuration
ONCALL_APP_NAME=Oncall Lens
ONCALL_DEBUG=false
ONCALL_API_HOST=0.0.0.0
ONCALL_API_PORT=8000

# Data Paths
ONCALL_KNOWLEDGE_BASE_PATH=./data/knowledge-base
ONCALL_UPLOAD_PATH=./data/uploads

# RAG Settings
ONCALL_CHUNK_SIZE=1500
ONCALL_CHUNK_OVERLAP=200
ONCALL_SIMILARITY_THRESHOLD=0.5
ONCALL_MAX_DOCS_PER_QUERY=5

# Security
ONCALL_SECRET_KEY=change-me-in-production
ONCALL_ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Upload
ONCALL_MAX_FILE_SIZE=10485760
ONCALL_ALLOWED_FILE_TYPES=[".txt",".log",".diff",".png",".jpg",".jpeg",".pdf"]

# Rate Limiting
ONCALL_RATE_LIMIT_REQUESTS=100
ONCALL_RATE_LIMIT_WINDOW=60
"""
    
    with open(".env.template", "w") as f:
        f.write(template_content)
    
    print("✅ Created .env.template file")
    print("📝 Copy it to .env and fill in your API keys")


if __name__ == "__main__":
    create_env_template() 