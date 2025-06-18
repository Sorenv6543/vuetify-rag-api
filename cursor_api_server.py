#!/usr/bin/env python3
"""
Cursor API Server for Vuetify RAG
FastAPI server providing HTTP endpoints for the Enhanced Vuetify RAG system
"""

import os
import sys
import json
import time
from typing import Optional, Dict, Any, List
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Import our RAG components
try:
    from simple_rag_interface import VuetifyRAG
    import importlib.util
    
    # Import enhanced query processor
    spec = importlib.util.spec_from_file_location(
        "enhanced_query_processor", 
        "enhanced_query_processor.py"
    )
    enhanced_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(enhanced_module)
    
    EnhancedVuetifyRAG = enhanced_module.EnhancedVuetifyRAG
    
except ImportError as e:
    print(f"❌ Failed to import RAG components: {e}")
    print("Make sure enhanced_query_processor.py and simple_rag_interface.py are available")
    sys.exit(1)

# Pydantic models for API
class QueryRequest(BaseModel):
    query: str
    context: Optional[str] = None
    component_filter: Optional[str] = None
    n_results: Optional[int] = 5
    use_enhanced: Optional[bool] = True

class QueryResponse(BaseModel):
    query: str
    response: str
    sources: List[Dict[str, Any]]
    response_time: float
    timestamp: str
    analysis: Optional[Dict[str, Any]] = None
    context_used: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    database_status: str
    total_documents: int
    server_uptime: float

# Initialize FastAPI app
app = FastAPI(
    title="Vuetify RAG API",
    description="Enhanced RAG system for Vuetify documentation queries",
    version="1.0.0"
)

# Add CORS middleware for browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global RAG system instance
rag_system = None
server_start_time = time.time()

@app.on_event("startup")
async def startup_event():
    """Initialize RAG system on startup"""
    global rag_system
    
    print("🚀 Starting Vuetify RAG API Server...")
    
    try:
        # Initialize base RAG
        print("📚 Loading Vuetify documentation database...")
        base_rag = VuetifyRAG()
        
        # Initialize enhanced RAG
        print("🧠 Setting up enhanced query processing...")
        rag_system = EnhancedVuetifyRAG(base_rag)
        
        print("✅ RAG system initialized successfully!")
        
    except Exception as e:
        print(f"❌ Failed to initialize RAG system: {e}")
        raise e

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with basic info"""
    return {
        "message": "Vuetify RAG API Server",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    global rag_system, server_start_time
    
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        # Check database status
        doc_count = rag_system.base_rag.collection.count()
        db_status = "healthy"
    except Exception as e:
        doc_count = 0
        db_status = f"unhealthy: {str(e)}"
    
    return HealthResponse(
        status="healthy" if rag_system else "unhealthy",
        timestamp=datetime.now().isoformat(),
        database_status=db_status,
        total_documents=doc_count,
        server_uptime=time.time() - server_start_time
    )

@app.post("/ask", response_model=QueryResponse)
async def ask_vuetify(request: QueryRequest):
    """Main query endpoint for Vuetify questions"""
    global rag_system
    
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    start_time = time.time()
    
    try:
        # Prepare query with context if provided
        query = request.query
        if request.context:
            # Enhance query with context
            context_summary = request.context[:200] + "..." if len(request.context) > 200 else request.context
            query = f"Given this context: {context_summary}\n\nQuestion: {request.query}"
        
        # Execute query
        if request.use_enhanced:
            result = rag_system.smart_query(
                query, 
                n_results=request.n_results
            )
            analysis = result.get('analysis')
        else:
            result = rag_system.base_rag.query(
                query,
                n_results=request.n_results,
                component_filter=request.component_filter
            )
            analysis = None
        
        response_time = time.time() - start_time
        
        return QueryResponse(
            query=request.query,
            response=result['response'],
            sources=result['sources'],
            response_time=response_time,
            timestamp=datetime.now().isoformat(),
            analysis=analysis,
            context_used=request.context[:100] + "..." if request.context and len(request.context) > 100 else request.context
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@app.post("/search", response_model=Dict[str, Any])
async def search_docs(request: QueryRequest):
    """Search-only endpoint (no AI response generation)"""
    global rag_system
    
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    start_time = time.time()
    
    try:
        # Perform search
        search_results = rag_system.base_rag.search(
            request.query,
            n_results=request.n_results,
            component_filter=request.component_filter
        )
        
        response_time = time.time() - start_time
        
        return {
            "query": request.query,
            "results": search_results,
            "num_results": len(search_results),
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/components")
async def list_components():
    """List available Vuetify components in the database"""
    global rag_system
    
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        # Get all unique components from the database
        results = rag_system.base_rag.collection.get()
        components = set()
        
        for metadata in results['metadatas']:
            if 'component' in metadata:
                components.add(metadata['component'])
        
        return {
            "components": sorted(list(components)),
            "total_count": len(components),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list components: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Get database statistics"""
    global rag_system
    
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        # Get all documents
        results = rag_system.base_rag.collection.get()
        
        # Count by component
        component_counts = {}
        content_type_counts = {}
        
        for metadata in results['metadatas']:
            component = metadata.get('component', 'unknown')
            content_type = metadata.get('content_type', 'unknown')
            
            component_counts[component] = component_counts.get(component, 0) + 1
            content_type_counts[content_type] = content_type_counts.get(content_type, 0) + 1
        
        return {
            "total_documents": len(results['documents']),
            "total_components": len(component_counts),
            "component_distribution": dict(sorted(component_counts.items(), key=lambda x: x[1], reverse=True)[:20]),
            "content_type_distribution": content_type_counts,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found", "available_endpoints": ["/", "/ask", "/search", "/health", "/components", "/stats"]}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "message": str(exc)}
    )

def main():
    """Run the server"""
    print("🔧 Vuetify RAG API Server")
    print("=" * 40)
    print("Endpoints:")
    print("  POST /ask          - Ask Vuetify questions")
    print("  POST /search       - Search documentation")
    print("  GET  /health       - Health check")
    print("  GET  /components   - List components")
    print("  GET  /stats        - Database statistics")
    print("  GET  /docs         - API documentation")
    print()
    
    # Run with uvicorn
    uvicorn.run(
        "cursor_api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main() 