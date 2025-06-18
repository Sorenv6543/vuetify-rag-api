#!/usr/bin/env python3
"""
Local API Server for Cursor AI Assistant
Turns your Vuetify RAG into a coding assistant API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import json
from typing import List, Dict, Any, Optional
import time

# Import your existing RAG system
try:
    from simple_rag_interface import VuetifyRAG
except ImportError:
    print("❌ simple_rag_interface.py not found. Make sure it's in the same directory.")
    exit(1)

app = FastAPI(
    title="Vuetify Coding Assistant API",
    description="Local API for Cursor AI integration",
    version="1.0.0"
)

# Enable CORS for Cursor
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global RAG system
rag_system = None

class QueryRequest(BaseModel):
    query: str
    context: Optional[str] = None  # Code context from Cursor
    component: Optional[str] = None
    type: Optional[str] = "coding"  # coding, api, example, troubleshooting

class CodeAssistantResponse(BaseModel):
    answer: str
    code_examples: List[str]
    related_components: List[str]
    documentation_links: List[str]
    confidence: float

@app.on_event("startup")
async def startup_event():
    """Initialize the RAG system on startup"""
    global rag_system
    print("🚀 Initializing Vuetify RAG system...")
    try:
        rag_system = VuetifyRAG()
        print("✅ RAG system loaded successfully!")
    except Exception as e:
        print(f"❌ Failed to load RAG system: {e}")
        raise

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Vuetify Coding Assistant",
        "version": "1.0.0",
        "endpoints": {
            "ask": "/ask - Main coding assistant endpoint",
            "search": "/search - Search documentation", 
            "component": "/component/{name} - Get component info",
            "health": "/health - System health"
        }
    }

@app.get("/health")
async def health_check():
    """System health check"""
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    return {
        "status": "healthy",
        "rag_system": "online",
        "timestamp": time.time()
    }

@app.post("/ask", response_model=CodeAssistantResponse)
async def ask_coding_question(request: QueryRequest):
    """Main coding assistant endpoint - optimized for Cursor"""
    
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        # Enhance query for coding context
        enhanced_query = _enhance_query_for_coding(request)
        
        # Search the documentation
        result = rag_system.query(enhanced_query, n_results=3)
        
        # Extract code examples from results
        code_examples = _extract_code_examples(result.get('sources', []))
        
        # Format response for coding assistance
        response = _format_coding_response(result, request.context)
        
        return CodeAssistantResponse(
            answer=response['answer'],
            code_examples=code_examples,
            related_components=response['components'],
            documentation_links=response['links'],
            confidence=response['confidence']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/search")
async def search_documentation(q: str, limit: int = 5):
    """Search documentation - simple endpoint"""
    
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        result = rag_system.query(q, n_results=limit)
        
        return {
            "query": q,
            "results": [
                {
                    "content": source.get('content', '')[:500] + "...",
                    "component": source.get('component'),
                    "section": source.get('section'),
                    "similarity": source.get('similarity')
                }
                for source in result.get('sources', [])
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/component/{component_name}")
async def get_component_info(component_name: str):
    """Get specific component information"""
    
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        # Search for component-specific information
        result = rag_system.search(
            f"{component_name} props usage examples",
            component_filter=component_name
        )
        
        if not result:
            raise HTTPException(status_code=404, detail=f"Component {component_name} not found")
        
        # Extract component info
        props = []
        examples = []
        usage = ""
        
        for chunk in result:
            content = chunk.get('content', '')
            if 'props' in content.lower() or 'properties' in content.lower():
                props.append(content)
            elif 'example' in content.lower() or '<template>' in content:
                examples.append(content)
            elif 'usage' in content.lower():
                usage = content
        
        return {
            "component": component_name,
            "props": props[:2],  # Top 2 prop descriptions
            "examples": examples[:3],  # Top 3 examples
            "usage": usage,
            "found_chunks": len(result)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/autocomplete")
async def code_autocomplete(request: dict):
    """Provide code autocompletion suggestions"""
    
    code_context = request.get('context', '')
    cursor_position = request.get('position', 0)
    
    # Extract current component being typed
    current_component = _extract_current_component(code_context, cursor_position)
    
    if current_component:
        # Get component suggestions
        result = rag_system.search(f"{current_component} props", n_results=2)
        
        suggestions = []
        for chunk in result:
            content = chunk.get('content', '')
            # Extract prop names (simplified)
            props = _extract_props_from_content(content)
            suggestions.extend(props)
        
        return {
            "component": current_component,
            "suggestions": suggestions[:10],
            "type": "props"
        }
    
    return {"suggestions": []}

def _enhance_query_for_coding(request: QueryRequest) -> str:
    """Enhance query specifically for coding assistance"""
    
    base_query = request.query
    enhanced_parts = [base_query]
    
    # Add context if provided
    if request.context:
        # Extract components from code context
        components = _extract_components_from_code(request.context)
        if components:
            enhanced_parts.append(f"components: {' '.join(components)}")
    
    # Add type-specific keywords
    type_keywords = {
        "coding": "implementation code example usage",
        "api": "props methods events API",
        "example": "example template script code",
        "troubleshooting": "error fix debug solution"
    }
    
    if request.type in type_keywords:
        enhanced_parts.append(type_keywords[request.type])
    
    # Add Vuetify context
    enhanced_parts.append("Vuetify Vue.js")
    
    return " ".join(enhanced_parts)

def _extract_components_from_code(code: str) -> List[str]:
    """Extract Vuetify components from code context"""
    import re
    
    # Find v-component patterns
    components = re.findall(r'<v-([a-z-]+)', code)
    # Find v-component in attributes
    components.extend(re.findall(r'v-([a-z-]+)', code))
    
    return list(set([f"v-{comp}" for comp in components]))

def _extract_code_examples(sources: List[Dict]) -> List[str]:
    """Extract code examples from search results"""
    import re
    
    examples = []
    
    for source in sources:
        content = source.get('content', '')
        
        # Find Vue code blocks
        vue_blocks = re.findall(r'```vue\n(.*?)\n```', content, re.DOTALL)
        examples.extend(vue_blocks)
        
        # Find HTML/template blocks
        html_blocks = re.findall(r'```html\n(.*?)\n```', content, re.DOTALL)
        examples.extend(html_blocks)
        
        # Find template tags
        template_blocks = re.findall(r'<template>(.*?)</template>', content, re.DOTALL)
        examples.extend(template_blocks)
    
    # Clean and limit examples
    cleaned_examples = []
    for example in examples:
        if len(example.strip()) > 50:  # Skip very short examples
            cleaned_examples.append(example.strip())
            if len(cleaned_examples) >= 5:  # Limit to 5 examples
                break
    
    return cleaned_examples

def _format_coding_response(result: Dict, context: Optional[str] = None) -> Dict:
    """Format response specifically for coding assistance"""
    
    response = result.get('response', '')
    sources = result.get('sources', [])
    
    # Extract components mentioned
    components = []
    for source in sources:
        component = source.get('component')
        if component and component not in components:
            components.append(component)
    
    # Create documentation links (placeholder)
    links = [f"https://vuetifyjs.com/components/{comp}/" for comp in components[:3]]
    
    # Calculate confidence based on similarity scores
    confidences = []
    for source in sources:
        similarity = source.get('similarity', '0')
        try:
            score = float(similarity)
            confidences.append(score)
        except:
            pass
    
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5
    
    # Enhance response for coding
    if context:
        response = f"Based on your code context:\n\n{response}"
    
    return {
        'answer': response,
        'components': components,
        'links': links,
        'confidence': avg_confidence
    }

def _extract_current_component(code: str, position: int) -> Optional[str]:
    """Extract the component being typed at cursor position"""
    import re
    
    # Get text around cursor position
    start = max(0, position - 50)
    end = min(len(code), position + 10)
    context = code[start:end]
    
    # Look for v-component pattern
    match = re.search(r'<v-([a-z-]+)', context)
    if match:
        return f"v-{match.group(1)}"
    
    return None

def _extract_props_from_content(content: str) -> List[str]:
    """Extract prop names from documentation content"""
    import re
    
    props = []
    
    # Look for prop patterns like :prop-name or v-bind:prop
    prop_patterns = [
        r':([a-z-]+)=',
        r'v-bind:([a-z-]+)',
        r'<v-[a-z-]+[^>]*\s([a-z-]+)=',
    ]
    
    for pattern in prop_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        props.extend(matches)
    
    # Clean and deduplicate
    unique_props = list(set([prop.lower() for prop in props if len(prop) > 1]))
    
    return unique_props[:10]  # Return top 10

if __name__ == "__main__":
    print("🚀 Starting Vuetify Coding Assistant API...")
    print("📍 Will be available at: http://localhost:8000")
    print("📚 Endpoints:")
    print("   POST /ask - Main coding assistant")
    print("   GET  /search?q=query - Search docs")
    print("   GET  /component/v-btn - Component info")
    print("   GET  /health - Health check")
    print()
    
    uvicorn.run(
        app, 
        host="127.0.0.1", 
        port=8000,
        log_level="info"
    )
