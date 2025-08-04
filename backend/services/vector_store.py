"""
Qdrant Vector Store Service for Oncall Lens
Handles vector storage, indexing, and retrieval for the RAG system.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import os

from qdrant_client import QdrantClient
from qdrant_client.models import (
    CollectionConfig,
    CreateCollection,
    Distance,
    PointStruct,
    VectorParams,
    FieldCondition,
    Filter
)
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

from config.settings import Settings

logger = logging.getLogger(__name__)


class QdrantVectorStore:
    """
    Qdrant vector store service for storing and retrieving postmortem documents.
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client: Optional[QdrantClient] = None
        self.embeddings: Optional[OpenAIEmbeddings] = None
        self.collection_name = settings.qdrant_collection_name
        
    async def initialize(self) -> None:
        """
        Initialize the Qdrant client and embeddings model.
        """
        logger.info("🔧 Initializing Qdrant vector store...")
        
        try:
            # Initialize Qdrant client
            self.client = QdrantClient(
                host=self.settings.qdrant_host,
                port=self.settings.qdrant_port,
                grpc_port=self.settings.qdrant_grpc_port,
                api_key=self.settings.qdrant_api_key,
                https=self.settings.qdrant_https,
            )
            
            # Initialize OpenAI embeddings
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=self.settings.openai_api_key,
                model=self.settings.openai_embedding_model
            )
            
            # Create collection if it doesn't exist
            await self._ensure_collection_exists()
            
            logger.info("✅ Qdrant vector store initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Qdrant vector store: {e}")
            raise
    
    async def _ensure_collection_exists(self) -> None:
        """
        Ensure the collection exists with proper configuration.
        """
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if self.collection_name not in collection_names:
                logger.info(f"Creating Qdrant collection: {self.collection_name}")
                
                # Create collection with vector configuration
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.settings.qdrant_vector_size,
                        distance=Distance.COSINE if self.settings.qdrant_distance_metric == "Cosine" else Distance.EUCLID
                    )
                )
                logger.info(f"✅ Created collection: {self.collection_name}")
            else:
                logger.info(f"✅ Collection already exists: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"❌ Failed to ensure collection exists: {e}")
            raise
    
    async def load_knowledge_base(self) -> None:
        """
        Load and index all postmortem documents from the knowledge base.
        """
        logger.info("📚 Loading knowledge base documents...")
        
        try:
            knowledge_base_path = Path(self.settings.knowledge_base_path)
            
            if not knowledge_base_path.exists():
                logger.warning(f"⚠️ Knowledge base path does not exist: {knowledge_base_path}")
                return
            
            # Load documents from the knowledge base directory
            loader = DirectoryLoader(
                str(knowledge_base_path),
                glob="*.md",
                loader_cls=TextLoader
            )
            documents = loader.load()
            
            if not documents:
                logger.warning("⚠️ No documents found in knowledge base")
                return
            
            logger.info(f"📄 Found {len(documents)} documents to process")
            
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.settings.chunk_size,
                chunk_overlap=self.settings.chunk_overlap,
                separators=["\n\n", "\n", "## ", "### ", "- ", ". ", " ", ""]
            )
            
            splits = text_splitter.split_documents(documents)
            logger.info(f"✂️ Split into {len(splits)} chunks")
            
            # Generate embeddings and store in Qdrant
            await self._store_documents(splits)
            
            logger.info("✅ Knowledge base loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to load knowledge base: {e}")
            raise
    
    async def _store_documents(self, documents: List[Document]) -> None:
        """
        Store documents with their embeddings in Qdrant.
        
        Args:
            documents: List of document chunks to store
        """
        logger.info(f"💾 Storing {len(documents)} document chunks...")
        
        try:
            points = []
            
            for i, doc in enumerate(documents):
                # Generate embedding for the document
                embedding = await self._get_embedding(doc.page_content)
                
                # Create point with metadata
                point = PointStruct(
                    id=i,
                    vector=embedding,
                    payload={
                        "content": doc.page_content,
                        "source": doc.metadata.get("source", "unknown"),
                        "chunk_index": i,
                        **doc.metadata
                    }
                )
                points.append(point)
                
                # Batch insert every 100 points
                if len(points) >= 100:
                    self.client.upsert(
                        collection_name=self.collection_name,
                        points=points
                    )
                    logger.info(f"💾 Stored batch of {len(points)} points")
                    points = []
            
            # Insert remaining points
            if points:
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )
                logger.info(f"💾 Stored final batch of {len(points)} points")
                
            logger.info("✅ All documents stored successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to store documents: {e}")
            raise
    
    async def _get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a text string.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            embedding = await self.embeddings.aembed_query(text)
            return embedding
        except Exception as e:
            logger.error(f"❌ Failed to generate embedding: {e}")
            raise
    
    async def similarity_search(
        self, 
        query: str, 
        top_k: int = None, 
        similarity_threshold: float = None
    ) -> List[Dict[str, Any]]:
        """
        Perform similarity search for relevant documents.
        
        Args:
            query: Search query
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of relevant documents with metadata
        """
        try:
            top_k = top_k or self.settings.top_k_retrieval
            similarity_threshold = similarity_threshold or self.settings.similarity_threshold
            
            logger.info(f"🔍 Searching for: '{query[:100]}...' (top_k={top_k})")
            
            # Generate query embedding
            query_embedding = await self._get_embedding(query)
            
            # Search in Qdrant
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                score_threshold=similarity_threshold
            )
            
            # Format results
            results = []
            for result in search_results:
                results.append({
                    "content": result.payload["content"],
                    "source": result.payload.get("source", "unknown"),
                    "similarity_score": result.score,
                    "metadata": {k: v for k, v in result.payload.items() if k not in ["content", "source"]}
                })
            
            logger.info(f"✅ Found {len(results)} relevant documents")
            return results
            
        except Exception as e:
            logger.error(f"❌ Similarity search failed: {e}")
            raise
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get collection statistics.
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            
            return {
                "collection_name": self.collection_name,
                "vector_count": collection_info.points_count,
                "vector_size": collection_info.config.params.vectors.size,
                "distance_metric": collection_info.config.params.vectors.distance.name,
                "status": collection_info.status.name
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get collection stats: {e}")
            return {
                "collection_name": self.collection_name,
                "vector_count": 0,
                "error": str(e)
            }
    
    async def cleanup(self) -> None:
        """
        Clean up resources.
        """
        logger.info("🧹 Cleaning up Qdrant vector store...")
        
        if self.client:
            # Qdrant client cleanup is handled automatically
            pass
            
        logger.info("✅ Qdrant vector store cleanup completed") 