"""
Oncall Lens: Test Backend
Simplified FastAPI backend for testing frontend integration without Qdrant dependency.
"""

import logging
import time
from typing import List
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="🔍 Oncall Lens - Test API",
    description="Simplified test backend for incident analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "🔍 Oncall Lens Test Backend", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": time.time()}

@app.post("/summarize")
async def analyze_incident(files: List[UploadFile] = File(...)):
    """
    Mock incident analysis endpoint.
    Returns realistic mock data for testing frontend integration.
    """
    logger.info(f"📁 Received {len(files)} files for analysis")
    
    # Log file details
    file_info = []
    for file in files:
        content = await file.read()
        file_info.append({
            "name": file.filename,
            "size": len(content),
            "type": file.content_type
        })
        logger.info(f"  - {file.filename} ({len(content)} bytes, {file.content_type})")
        
        # Reset file pointer for potential future reads
        await file.seek(0)
    
    # Simulate processing time
    await asyncio.sleep(2)  # 2 second delay to show loading state
    
    # Generate mock analysis based on uploaded files
    mock_summary = generate_mock_analysis(file_info)
    
    # Mock confidence score
    confidence_score = 0.87  # High confidence for demo
    
    response = {
        "summary": mock_summary,
        "confidence_score": confidence_score,
        "sources": [f["name"] for f in file_info],
        "processing_time": 2.0,
        "files_processed": len(files)
    }
    
    logger.info(f"✅ Analysis complete. Confidence: {confidence_score}")
    return JSONResponse(content=response)

def generate_mock_analysis(file_info: List[dict]) -> str:
    """Generate realistic mock analysis based on uploaded files"""
    
    file_types = {
        "log": [f for f in file_info if f["name"].endswith(('.log', '.txt'))],
        "diff": [f for f in file_info if f["name"].endswith('.diff')],
        "image": [f for f in file_info if f["name"].endswith(('.png', '.jpg', '.jpeg'))],
        "code": [f for f in file_info if f["name"].endswith(('.js', '.py', '.json', '.yaml', '.yml'))]
    }
    
    analysis_parts = [
        "# 🔍 Incident Analysis Summary\n",
        "## 📊 **Key Findings**\n"
    ]
    
    # Add findings based on file types
    if file_types["log"]:
        analysis_parts.extend([
            "### 🚨 **Critical Error Detected**",
            "- **Error Type**: Database connection timeout",
            "- **First Occurrence**: 2024-08-04 02:15:23 UTC", 
            "- **Frequency**: 47 occurrences in the last hour",
            "- **Impact**: Payment processing service degraded\n"
        ])
    
    if file_types["diff"]:
        analysis_parts.extend([
            "### 📝 **Recent Changes Analysis**",
            "- **Deployment**: `v2.1.4` deployed 15 minutes before incident",
            "- **Suspicious Change**: Database connection pool size reduced from 50 to 10",
            "- **File Modified**: `config/database.yaml`",
            "- **Risk Level**: HIGH - This change likely caused the connection timeouts\n"
        ])
    
    if file_types["image"]:
        analysis_parts.extend([
            "### 📈 **Dashboard Analysis**",
            "- **CPU Usage**: Spiked to 95% at incident start",
            "- **Memory**: Stable at 60% - not the bottleneck", 
            "- **Database Connections**: Maxed out at new limit of 10",
            "- **Response Time**: Increased from 200ms to 5000ms\n"
        ])
    
    # Add root cause analysis
    analysis_parts.extend([
        "## 🎯 **Root Cause Analysis**\n",
        "**Primary Cause**: Database connection pool misconfiguration in recent deployment.",
        "The connection pool size was reduced from 50 to 10 connections, but the application",
        "load requires approximately 30-40 concurrent database connections during peak traffic.\n",
        "**Contributing Factors**:",
        "1. Insufficient load testing of the configuration change",
        "2. Missing monitoring alerts for connection pool exhaustion",
        "3. No gradual rollout of the configuration change\n"
    ])
    
    # Add immediate actions
    analysis_parts.extend([
        "## ⚡ **Immediate Actions Required**\n",
        "### 🔧 **Critical (Do Now)**",
        "```bash",
        "# Revert database connection pool to previous value",
        "kubectl patch configmap db-config -p '{\"data\":{\"max_connections\":\"50\"}}'",
        "kubectl rollout restart deployment payment-service",
        "```\n",
        "### 📊 **Monitor**",
        "- Watch database connection metrics for next 30 minutes",
        "- Verify payment processing latency returns to baseline (<500ms)",
        "- Check error rates drop below 0.1%\n"
    ])
    
    # Add prevention measures
    analysis_parts.extend([
        "## 🛡️ **Prevention Measures**\n",
        "1. **Add Monitoring**: Set up alerts for database connection pool utilization >80%",
        "2. **Load Testing**: Include database connection limits in performance test suite", 
        "3. **Gradual Rollout**: Use canary deployments for configuration changes",
        "4. **Documentation**: Update runbook with connection pool sizing guidelines\n"
    ])
    
    # Add similar incidents
    analysis_parts.extend([
        "## 📚 **Similar Past Incidents**\n",
        "- **INC-2024-0156** (2024-07-12): Redis connection pool exhaustion - similar pattern",
        "- **INC-2024-0089** (2024-05-23): Database timeout after configuration change",
        "- **Resolution Time**: Previous similar incidents resolved in 15-30 minutes\n"
    ])
    
    # Add timeline
    analysis_parts.extend([
        "## ⏰ **Incident Timeline**\n",
        "| Time | Event |",
        "|------|-------|",
        "| 02:00 | Deployment v2.1.4 completed |",
        "| 02:15 | First database timeout errors |",
        "| 02:17 | Error rate escalated to 15% |",
        "| 02:20 | **Analysis initiated** |",
        "| 02:22 | Root cause identified |\n"
    ])
    
    return "\n".join(analysis_parts)

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Oncall Lens Test Backend...")
    uvicorn.run(
        "test_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 