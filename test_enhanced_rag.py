#!/usr/bin/env python3
"""
Test script for Enhanced Vuetify RAG system
Demonstrates intelligent query processing and multi-stage retrieval
"""

import sys
import json
from simple_rag_interface import VuetifyRAG

# Import from the enhanced query processor file
sys.path.append('.')
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("enhanced_query_processor", "enhanced-query-processor.py")
    enhanced_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(enhanced_module)
    
    EnhancedVuetifyRAG = enhanced_module.EnhancedVuetifyRAG
    VuetifyQueryProcessor = enhanced_module.VuetifyQueryProcessor
    QueryType = enhanced_module.QueryType
    
except Exception as e:
    print(f"❌ Failed to import enhanced query processor: {e}")
    sys.exit(1)

def test_query_analysis():
    """Test the query analysis capabilities"""
    print("🧪 Testing Query Analysis")
    print("=" * 50)
    
    processor = VuetifyQueryProcessor()
    
    test_queries = [
        "How to use v-btn component?",
        "v-card elevation props",
        "v-data-table sorting example",
        "custom theme colors",
        "v-text-field validation rules",
        "v-dialog vs v-menu comparison",
        "v-form not submitting",
        "v-app-bar accessibility best practices"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        analysis = processor.analyze_query(query)
        
        print(f"  Type: {analysis.query_type.value}")
        print(f"  Components: {analysis.components}")
        print(f"  Keywords: {analysis.keywords}")
        print(f"  Confidence: {analysis.intent_confidence:.2f}")
        print(f"  Enhanced: {analysis.enhanced_query[:100]}...")

def test_enhanced_queries():
    """Test enhanced query processing with actual RAG system"""
    print("\n🚀 Testing Enhanced RAG Queries")
    print("=" * 50)
    
    try:
        # Initialize systems
        base_rag = VuetifyRAG()
        enhanced_rag = EnhancedVuetifyRAG(base_rag)
        
        # Test queries with different intents
        test_cases = [
            {
                'query': 'v-btn color property',
                'description': 'API Reference Query'
            },
            {
                'query': 'create button with custom styling',
                'description': 'Usage Guide Query'
            },
            {
                'query': 'elevation shadow effects',
                'description': 'Styling Query'
            },
            {
                'query': 'form validation example',
                'description': 'Example Query'
            }
        ]
        
        for test_case in test_cases:
            print(f"\n🔍 {test_case['description']}")
            print(f"Query: '{test_case['query']}'")
            print("-" * 40)
            
            try:
                result = enhanced_rag.smart_query(test_case['query'], n_results=3)
                
                # Show analysis
                analysis = result['analysis']
                print(f"Detected Type: {analysis['type']}")
                print(f"Components: {analysis['components']}")
                print(f"Confidence: {analysis['confidence']:.2f}")
                
                # Show response summary
                response = result['response']
                if len(response) > 200:
                    print(f"Response: {response[:200]}...")
                else:
                    print(f"Response: {response}")
                
                # Show sources
                sources = result['sources']
                print(f"Sources: {len(sources)} chunks found")
                for i, source in enumerate(sources[:2], 1):
                    component = source['component'] or 'Unknown'
                    similarity = source['similarity']
                    print(f"  {i}. {component} (similarity: {similarity})")
                
            except Exception as e:
                print(f"❌ Error: {e}")
        
    except Exception as e:
        print(f"❌ Failed to initialize enhanced RAG: {e}")
        print("Make sure ChromaDB is set up correctly.")

def test_component_detection():
    """Test component detection accuracy"""
    print("\n🔧 Testing Component Detection")
    print("=" * 50)
    
    processor = VuetifyQueryProcessor()
    
    component_tests = [
        ("How to use v-btn?", ["v-btn"]),
        ("v-data-table with v-text-field", ["v-data-table", "v-text-field"]),
        ("VCard elevation property", ["v-card"]),
        ("AppBar navigation setup", ["v-app-bar"]),
        ("button styling", []),  # Should detect no specific components
        ("DataTable sorting", ["v-data-table"]),
    ]
    
    for query, expected in component_tests:
        analysis = processor.analyze_query(query)
        detected = analysis.components
        
        print(f"Query: '{query}'")
        print(f"  Expected: {expected}")
        print(f"  Detected: {detected}")
        
        # Simple accuracy check
        if set(expected).issubset(set(detected)) or (not expected and not detected):
            print("  ✅ Correct")
        else:
            print("  ❌ Mismatch")

def main():
    """Main test function"""
    print("🧪 Enhanced Vuetify RAG System Tests")
    print("=" * 60)
    
    # Test 1: Query Analysis
    test_query_analysis()
    
    # Test 2: Component Detection
    test_component_detection()
    
    # Test 3: Enhanced Queries
    test_enhanced_queries()
    
    print(f"\n🎉 Tests completed!")

if __name__ == "__main__":
    main() 