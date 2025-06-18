#!/usr/bin/env python3
"""
Test script for the Cursor API Server
Demonstrates various ways to query the Vuetify RAG system
"""

import json
import requests
import time

def test_api_server():
    """Test the API server endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Vuetify RAG API Server")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Health Check")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Server healthy - {health['total_documents']} documents")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Make sure the server is running: python cursor_api_server.py")
        return
    
    # Test 2: Basic query
    print("\n2. Basic Vuetify Query")
    query_data = {
        "query": "How to use v-btn component?",
        "use_enhanced": False  # Use basic search that we know works
    }
    
    response = requests.post(f"{base_url}/ask", json=query_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Query successful ({result['response_time']:.2f}s)")
        print(f"Response: {result['response'][:200]}...")
        print(f"Sources: {len(result['sources'])} chunks")
    else:
        print(f"❌ Query failed: {response.status_code}")
    
    # Test 3: Query with context (as requested)
    print("\n3. Query with Context")
    query_data = {
        "query": "How to change button colors?",
        "context": "I'm building a Vue.js application with Vuetify and need to customize button colors",
        "use_enhanced": False
    }
    
    response = requests.post(f"{base_url}/ask", json=query_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Context query successful ({result['response_time']:.2f}s)")
        print(f"Context used: {result['context_used']}")
        print(f"Response: {result['response'][:200]}...")
    else:
        print(f"❌ Context query failed: {response.status_code}")
    
    # Test 4: Search only
    print("\n4. Search Only (No AI Response)")
    query_data = {
        "query": "v-card elevation examples",
        "n_results": 3
    }
    
    response = requests.post(f"{base_url}/search", json=query_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Search successful ({result['response_time']:.2f}s)")
        print(f"Found {result['num_results']} results")
        for i, res in enumerate(result['results'][:2], 1):
            component = res['metadata']['component']
            similarity = res['similarity_score']
            print(f"  {i}. {component} (similarity: {similarity:.3f})")
    else:
        print(f"❌ Search failed: {response.status_code}")
    
    # Test 5: Component filter
    print("\n5. Component-Filtered Query")
    query_data = {
        "query": "styling and customization",
        "component_filter": "v-buttons",
        "use_enhanced": False
    }
    
    response = requests.post(f"{base_url}/ask", json=query_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Filtered query successful ({result['response_time']:.2f}s)")
        print(f"Sources: {len(result['sources'])} chunks from v-buttons")
    else:
        print(f"❌ Filtered query failed: {response.status_code}")
    
    # Test 6: List components
    print("\n6. Available Components")
    response = requests.get(f"{base_url}/components")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Found {result['total_count']} components")
        print(f"Examples: {', '.join(result['components'][:10])}...")
    else:
        print(f"❌ Components list failed: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("🎉 API Server tests completed!")
    print("\nUsage in Cursor:")
    print("POST http://localhost:8000/ask")
    print('{"query": "How to use v-btn?", "context": "your code here"}')

def curl_examples():
    """Print curl examples for easy testing"""
    print("\n📋 Curl Examples for Testing:")
    print("-" * 30)
    
    examples = [
        {
            "name": "Basic Query",
            "curl": '''curl -X POST "http://localhost:8000/ask" \\
  -H "Content-Type: application/json" \\
  -d '{"query": "How to use v-btn?", "use_enhanced": false}' '''
        },
        {
            "name": "Query with Context",
            "curl": '''curl -X POST "http://localhost:8000/ask" \\
  -H "Content-Type: application/json" \\
  -d '{"query": "How to change colors?", "context": "Vue.js project", "use_enhanced": false}' '''
        },
        {
            "name": "Search Only",
            "curl": '''curl -X POST "http://localhost:8000/search" \\
  -H "Content-Type: application/json" \\
  -d '{"query": "v-card examples", "n_results": 3}' '''
        },
        {
            "name": "Health Check",
            "curl": '''curl http://localhost:8000/health'''
        }
    ]
    
    for example in examples:
        print(f"\n{example['name']}:")
        print(example['curl'])

if __name__ == "__main__":
    test_api_server()
    curl_examples() 