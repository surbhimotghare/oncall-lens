"""
Advanced Retrieval Service for Oncall Lens
Implements advanced retrieval techniques to improve RAG performance.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import asyncio

from langchain.retrievers import (
    ParentDocumentRetriever,
    EnsembleRetriever
)
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain.storage import InMemoryStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_cohere import CohereRerank
from langchain.schema import Document
from qdrant_client import QdrantClient, models
from langchain_qdrant import QdrantVectorStore

from config.settings import Settings

logger = logging.getLogger(__name__)


class AdvancedRetrievalService:
    """
    Advanced retrieval service implementing multiple retrieval strategies:
    - Parent Document Retriever (small-to-big)
    - Hybrid Search (BM25 + Semantic)
    - Multi-Query Retriever
    - Contextual Compression (Reranking)
    - Ensemble Retriever (combines multiple strategies)
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=settings.openai_api_key
        )
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            api_key=settings.openai_api_key
        )
        
        # Storage for different retrievers
        self.documents: List[Document] = []
        self.naive_retriever = None
        self.parent_document_retriever = None
        self.bm25_retriever = None
        self.multi_query_retriever = None
        self.compression_retriever = None
        self.hybrid_retriever = None
        self.ensemble_retriever = None
        
        # Qdrant clients for different collections
        self.parent_doc_client = None
        self.parent_doc_vectorstore = None
        
    async def initialize(self):
        """Initialize the advanced retrieval service."""
        logger.info("🔧 Initializing Advanced Retrieval Service...")
        
        # Load documents
        await self._load_documents()
        
        # Initialize all retrieval strategies
        await self._setup_naive_retriever()
        await self._setup_parent_document_retriever()
        await self._setup_bm25_retriever()
        await self._setup_multi_query_retriever()
        await self._setup_compression_retriever()
        await self._setup_hybrid_retriever()
        await self._setup_ensemble_retriever()
        
        logger.info("✅ Advanced Retrieval Service initialized")
        
    async def _load_documents(self):
        """Load documents from knowledge base."""
        logger.info("📚 Loading documents for advanced retrieval...")
        
        knowledge_base_path = Path(self.settings.knowledge_base_path)
        if not knowledge_base_path.exists():
            logger.warning(f"⚠️ Knowledge base path does not exist: {knowledge_base_path}")
            return
        
        # Load documents
        loader = DirectoryLoader(
            str(knowledge_base_path),
            glob="*.md",
            loader_cls=TextLoader
        )
        self.documents = loader.load()
        
        logger.info(f"📄 Loaded {len(self.documents)} documents")
        
    async def _setup_naive_retriever(self):
        """Setup naive semantic retriever as baseline."""
        logger.info("🔧 Setting up Naive Retriever...")
        
        from langchain_community.vectorstores import Qdrant
        
        vectorstore = Qdrant.from_documents(
            self.documents,
            self.embeddings,
            location=":memory:",
            collection_name="naive_retrieval"
        )
        
        self.naive_retriever = vectorstore.as_retriever(
            search_kwargs={"k": 10}
        )
        
        logger.info("✅ Naive Retriever ready")
        
    async def _setup_parent_document_retriever(self):
        """Setup Parent Document Retriever (small-to-big strategy)."""
        logger.info("🔧 Setting up Parent Document Retriever...")
        
        # Create child splitter for small chunks
        child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,  # Smaller chunks for precise matching
            chunk_overlap=50,
            separators=["\n\n", "\n", "## ", "### ", "- ", ". ", " ", ""]
        )
        
        # Setup Qdrant client for parent documents
        self.parent_doc_client = QdrantClient(location=":memory:")
        
        self.parent_doc_client.create_collection(
            collection_name="parent_documents",
            vectors_config=models.VectorParams(
                size=1536, 
                distance=models.Distance.COSINE
            )
        )
        
        self.parent_doc_vectorstore = QdrantVectorStore(
            collection_name="parent_documents",
            embedding=self.embeddings,
            client=self.parent_doc_client
        )
        
        # Create in-memory store for parent documents
        store = InMemoryStore()
        
        # Create parent document retriever
        self.parent_document_retriever = ParentDocumentRetriever(
            vectorstore=self.parent_doc_vectorstore,
            docstore=store,
            child_splitter=child_splitter,
            search_kwargs={"k": 5}
        )
        
        # Add documents
        self.parent_document_retriever.add_documents(self.documents)
        
        logger.info("✅ Parent Document Retriever ready")
        
    async def _setup_bm25_retriever(self):
        """Setup BM25 (keyword-based) retriever."""
        logger.info("🔧 Setting up BM25 Retriever...")
        
        self.bm25_retriever = BM25Retriever.from_documents(
            self.documents,
            k=10
        )
        
        logger.info("✅ BM25 Retriever ready")
        
    async def _setup_multi_query_retriever(self):
        """Setup Multi-Query Retriever."""
        logger.info("🔧 Setting up Multi-Query Retriever...")
        
        self.multi_query_retriever = MultiQueryRetriever.from_llm(
            retriever=self.naive_retriever,
            llm=self.llm
        )
        
        logger.info("✅ Multi-Query Retriever ready")
        
    async def _setup_compression_retriever(self):
        """Setup Contextual Compression Retriever with Cohere Rerank."""
        logger.info("🔧 Setting up Compression Retriever...")
        
        try:
            # Check if Cohere API key is available
            cohere_api_key = getattr(self.settings, 'cohere_api_key', None)
            if not cohere_api_key:
                logger.warning("⚠️ Cohere API key not found, skipping compression retriever")
                return
                
            # CohereRerank automatically picks up COHERE_API_KEY from environment
            compressor = CohereRerank(
                model="rerank-v3.5"
            )
            
            self.compression_retriever = ContextualCompressionRetriever(
                base_compressor=compressor,
                base_retriever=self.naive_retriever
            )
            
            logger.info("✅ Compression Retriever ready")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not setup compression retriever: {e}")
            self.compression_retriever = None
            
    async def _setup_hybrid_retriever(self):
        """Setup Hybrid Retriever (BM25 + Semantic)."""
        logger.info("🔧 Setting up Hybrid Retriever...")
        
        # Combine BM25 and semantic search
        retrievers = [self.bm25_retriever, self.naive_retriever]
        weights = [0.3, 0.7]  # Favor semantic search slightly
        
        self.hybrid_retriever = EnsembleRetriever(
            retrievers=retrievers,
            weights=weights
        )
        
        logger.info("✅ Hybrid Retriever ready")
        
    async def _setup_ensemble_retriever(self):
        """Setup Ensemble Retriever combining all strategies."""
        logger.info("🔧 Setting up Ensemble Retriever...")
        
        # Combine all available retrievers
        retrievers = [
            self.naive_retriever,
            self.parent_document_retriever,
            self.bm25_retriever,
            self.multi_query_retriever,
            self.hybrid_retriever
        ]
        
        # Add compression retriever if available
        if self.compression_retriever:
            retrievers.append(self.compression_retriever)
            
        # Equal weighting for all retrievers
        weights = [1/len(retrievers)] * len(retrievers)
        
        self.ensemble_retriever = EnsembleRetriever(
            retrievers=retrievers,
            weights=weights
        )
        
        logger.info("✅ Ensemble Retriever ready")
        
    def get_retriever(self, strategy: str = "ensemble"):
        """
        Get a specific retriever by strategy name.
        
        Available strategies:
        - naive: Basic semantic search
        - parent_document: Small-to-big retrieval
        - bm25: Keyword-based search
        - multi_query: Multiple query variations
        - compression: Reranked results (if available)
        - hybrid: BM25 + Semantic
        - ensemble: All strategies combined
        """
        retrievers = {
            "naive": self.naive_retriever,
            "parent_document": self.parent_document_retriever,
            "bm25": self.bm25_retriever,
            "multi_query": self.multi_query_retriever,
            "compression": self.compression_retriever,
            "hybrid": self.hybrid_retriever,
            "ensemble": self.ensemble_retriever
        }
        
        retriever = retrievers.get(strategy)
        if retriever is None:
            logger.warning(f"⚠️ Retriever '{strategy}' not available, using naive")
            return self.naive_retriever
            
        return retriever
        
    async def test_retrieval_strategies(self, query: str, top_k: int = 3):
        """Test all retrieval strategies with a sample query."""
        logger.info(f"🔍 Testing retrieval strategies with query: '{query[:50]}...'")
        
        strategies = ["naive", "parent_document", "bm25", "multi_query", "hybrid", "ensemble"]
        if self.compression_retriever:
            strategies.append("compression")
            
        results = {}
        
        for strategy in strategies:
            try:
                retriever = self.get_retriever(strategy)
                if retriever is None:
                    continue
                    
                docs = retriever.get_relevant_documents(query)[:top_k]
                results[strategy] = {
                    "num_docs": len(docs),
                    "docs": [
                        {
                            "content": doc.page_content[:200] + "...",
                            "source": doc.metadata.get("source", "unknown")
                        }
                        for doc in docs
                    ]
                }
                
                logger.info(f"  {strategy}: {len(docs)} documents retrieved")
                
            except Exception as e:
                logger.error(f"  {strategy}: Error - {e}")
                results[strategy] = {"error": str(e)}
                
        return results


async def main():
    """Test the advanced retrieval service."""
    from config.settings import get_settings
    
    settings = get_settings()
    service = AdvancedRetrievalService(settings)
    
    await service.initialize()
    
    # Test with a sample query
    test_query = "What was the root cause of the Shakespeare search outage?"
    results = await service.test_retrieval_strategies(test_query)
    
    print("\n🔍 Advanced Retrieval Test Results:")
    print("=" * 60)
    
    for strategy, result in results.items():
        if "error" in result:
            print(f"{strategy:.<20} ❌ {result['error']}")
        else:
            print(f"{strategy:.<20} ✅ {result['num_docs']} documents")
            
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main()) 