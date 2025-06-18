# Vuetify RAG API Server

FastAPI server providing HTTP endpoints for querying Vuetify documentation with context awareness.

## Quick Start

### 1. Install Dependencies
```bash
pip install fastapi uvicorn
```

### 2. Start the Server
```bash
python cursor_api_server.py
```

Server will be available at: `http://localhost:8000`

### 3. API Documentation
Interactive docs available at: `http://localhost:8000/docs`

## API Endpoints

### POST `/ask` - Main Query Endpoint
Ask questions about Vuetify with optional context.

**Request:**
```json
{
  "query": "How to use v-btn?",
  "context": "I'm building a Vue.js app",
  "component_filter": "v-buttons",
  "n_results": 5,
  "use_enhanced": false
}
```

**Response:**
```json
{
  "query": "How to use v-btn?",
  "response": "The v-btn component replaces...",
  "sources": [...],
  "response_time": 0.85,
  "timestamp": "2025-06-17T20:38:29.731576",
  "analysis": {...},
  "context_used": "I'm building a Vue.js app"
}
```

### POST `/search` - Search Only
Search documentation without AI response generation.

**Request:**
```json
{
  "query": "v-card elevation",
  "n_results": 3
}
```

### GET `/health` - Health Check
Check server and database status.

### GET `/components` - List Components
Get all available Vuetify components in the database.

### GET `/stats` - Database Statistics
Get detailed statistics about the documentation database.

## Usage Examples

### Basic Curl Commands

```bash
# Basic query
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "How to use v-btn?", "use_enhanced": false}'

# Query with context
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "button colors", "context": "Vue.js project", "use_enhanced": false}'

# Search only
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "v-card examples"}'

# Health check
curl http://localhost:8000/health
```

### Python Requests

```python
import requests

# Basic query
response = requests.post("http://localhost:8000/ask", json={
    "query": "How to customize v-btn colors?",
    "context": "I'm working on a dark theme",
    "use_enhanced": False
})

result = response.json()
print(result["response"])
```

### JavaScript/TypeScript

```javascript
// Using fetch
const response = await fetch('http://localhost:8000/ask', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        query: 'How to use v-btn?',
        context: 'Building a Vue.js app',
        use_enhanced: false
    })
});

const result = await response.json();
console.log(result.response);
```

## Integration with Cursor

### Using HTTP Client
1. Install REST Client extension in Cursor
2. Create a `.http` file:

```http
### Ask Vuetify Question
POST http://localhost:8000/ask
Content-Type: application/json

{
  "query": "How to use v-btn?",
  "context": "{{your_code_context}}",
  "use_enhanced": false
}
```

### Using Terminal in Cursor
```bash
# Quick test
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "How to create responsive buttons?", "use_enhanced": false}'
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | required | Your Vuetify question |
| `context` | string | null | Code context to enhance query |
| `component_filter` | string | null | Filter to specific component |
| `n_results` | integer | 5 | Number of results to return |
| `use_enhanced` | boolean | true | Use enhanced query processing* |

*Note: Enhanced processing is currently experiencing issues. Recommend using `"use_enhanced": false` for reliable results.

## Response Format

All successful queries return:
- `query`: Original query text
- `response`: AI-generated answer or formatted results
- `sources`: Array of relevant documentation chunks
- `response_time`: Query processing time in seconds
- `timestamp`: When the query was processed
- `analysis`: Query analysis (if enhanced mode used)
- `context_used`: Truncated context that was applied

## Testing

Run the test suite:
```bash
python test_api_server.py
```

## Troubleshooting

### Server Won't Start
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check if ChromaDB database exists: `ls chromadb_data/`
- Run database setup if needed: `python setup_chromadb.py`

### No Results Found
- Try `"use_enhanced": false` in your request
- Check available components: `curl http://localhost:8000/components`
- Verify database health: `curl http://localhost:8000/health`

### Port Already in Use
Change the port in `cursor_api_server.py`:
```python
uvicorn.run("cursor_api_server:app", host="0.0.0.0", port=8001)
```

## Database Info

- **Total Documents**: 1,990 Vuetify documentation chunks
- **Components**: 224 Vuetify components covered
- **Content Types**: API reference, examples, styling guides, troubleshooting
- **Search Method**: Semantic search using sentence transformers

## Performance

- Average response time: 0.3-1.0 seconds
- Database size: ~50MB
- Memory usage: ~200MB
- Concurrent requests: Supported

The server provides fast, accurate responses about Vuetify components, styling, props, and usage patterns. 