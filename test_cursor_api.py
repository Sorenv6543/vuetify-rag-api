#!/usr/bin/env python3
"""
Test script for Cursor API Server
Demonstrates coding assistant features for Vuetify development
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_health():
    """Test server health"""
    print("🏥 Testing Server Health")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Server Status: {health['status']}")
            print(f"✅ RAG System: {health['rag_system']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("💡 Make sure server is running: python cursor-api-server.py")
        return False
    
    return True

def test_coding_assistant():
    """Test the main coding assistant endpoint"""
    print("\n🤖 Testing Coding Assistant")
    print("-" * 30)
    
    test_cases = [
        {
            "name": "Button with Context",
            "query": "How to make a responsive button with custom colors?",
            "context": "<template>\n  <v-btn>\n    Click me\n  </v-btn>\n</template>",
            "type": "coding"
        },
        {
            "name": "Card Component",
            "query": "Show me card examples with elevation",
            "context": "<v-card></v-card>",
            "type": "example"
        },
        {
            "name": "API Reference",
            "query": "What are the props for v-text-field?",
            "type": "api"
        },
        {
            "name": "Troubleshooting",
            "query": "v-data-table not showing data",
            "context": "<v-data-table :items=\"items\"></v-data-table>",
            "type": "troubleshooting"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        
        payload = {
            "query": test_case["query"],
            "type": test_case["type"]
        }
        
        if "context" in test_case:
            payload["context"] = test_case["context"]
        
        try:
            response = requests.post(f"{BASE_URL}/ask", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Query successful")
                print(f"   📝 Answer: {result['answer'][:100]}...")
                print(f"   🔧 Code Examples: {len(result['code_examples'])} found")
                print(f"   📦 Components: {', '.join(result['related_components'][:3])}")
                print(f"   🎯 Confidence: {result['confidence']:.2f}")
                
                if result['code_examples']:
                    print(f"   💻 First Example: {result['code_examples'][0][:80]}...")
                
            else:
                print(f"   ❌ Failed: {response.status_code}")
                print(f"   📄 Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_component_info():
    """Test component-specific information"""
    print("\n📦 Testing Component Information")
    print("-" * 30)
    
    components = ['v-buttons', 'v-cards', 'v-text-fields', 'v-data-tables']
    
    for component in components:
        print(f"\n🔍 Testing {component}")
        
        try:
            response = requests.get(f"{BASE_URL}/component/{component}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Component found")
                print(f"   📄 Props: {len(result['props'])} sections")
                print(f"   💻 Examples: {len(result['examples'])} found")
                print(f"   📊 Total chunks: {result['found_chunks']}")
                
                if result['usage']:
                    print(f"   📖 Usage: {result['usage'][:60]}...")
                    
            elif response.status_code == 404:
                print(f"   ⚠️  Component not found")
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_search():
    """Test search functionality"""
    print("\n🔍 Testing Search Functionality")
    print("-" * 30)
    
    searches = [
        "v-btn color props",
        "card elevation examples",
        "form validation rules",
        "responsive grid layout",
        "theme customization"
    ]
    
    for i, query in enumerate(searches, 1):
        print(f"\n{i}. Searching: '{query}'")
        
        try:
            response = requests.get(f"{BASE_URL}/search", params={"q": query, "limit": 3})
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Found {len(result['results'])} results")
                
                for j, res in enumerate(result['results'][:2], 1):
                    component = res['component']
                    similarity = res['similarity']
                    content_preview = res['content'][:80].replace('\n', ' ')
                    print(f"   {j}. {component} (sim: {similarity}) - {content_preview}...")
                    
            else:
                print(f"   ❌ Search failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_autocomplete():
    """Test autocomplete functionality"""
    print("\n⚡ Testing Autocomplete")
    print("-" * 30)
    
    test_contexts = [
        {
            "context": "<v-btn ",
            "position": 7,
            "description": "Button props"
        },
        {
            "context": "<template>\n  <v-card \n",
            "position": 19,
            "description": "Card props"
        }
    ]
    
    for i, test in enumerate(test_contexts, 1):
        print(f"\n{i}. {test['description']}")
        print(f"   Context: {test['context']}")
        
        try:
            payload = {
                "context": test["context"],
                "position": test["position"]
            }
            
            response = requests.post(f"{BASE_URL}/autocomplete", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('suggestions'):
                    print(f"   ✅ Found suggestions for {result.get('component', 'unknown')}")
                    suggestions = result['suggestions'][:5]
                    print(f"   💡 Suggestions: {', '.join(suggestions)}")
                else:
                    print(f"   ⚠️  No suggestions found")
            else:
                print(f"   ❌ Autocomplete failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_endpoints_overview():
    """Test the root endpoint"""
    print("\n📋 Testing Endpoints Overview")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Service: {result['service']}")
            print(f"✅ Version: {result['version']}")
            print(f"✅ Status: {result['status']}")
            
            print("\n📡 Available Endpoints:")
            for endpoint, desc in result['endpoints'].items():
                print(f"   {endpoint}: {desc}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run all tests"""
    print("🧪 Cursor API Server Test Suite")
    print("=" * 50)
    
    # Test health first
    if not test_health():
        return
    
    # Run all tests
    test_endpoints_overview()
    test_coding_assistant()
    test_component_info()
    test_search()
    test_autocomplete()
    
    print("\n" + "=" * 50)
    print("🎉 Test Suite Completed!")
    print("\n💡 Integration Tips for Cursor:")
    print("   • Use POST /ask with your code context")
    print("   • Try different 'type' values: coding, api, example, troubleshooting")
    print("   • Use GET /component/{name} for specific component docs")
    print("   • Use POST /autocomplete for prop suggestions")
    print("\n📖 Example API Usage:")
    print('   curl -X POST "http://localhost:8000/ask" \\')
    print('     -H "Content-Type: application/json" \\')
    print('     -d \'{"query": "How to use v-btn?", "context": "<v-btn></v-btn>", "type": "coding"}\'')

if __name__ == "__main__":
    main() 