#!/usr/bin/env python3
"""
Simple demonstration of Enhanced Vuetify RAG system
"""

from simple_rag_interface import VuetifyRAG
import importlib.util

# Import enhanced module
spec = importlib.util.spec_from_file_location('enhanced_query_processor', 'enhanced-query-processor.py')
enhanced_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(enhanced_module)

def main():
    print("🚀 Enhanced Vuetify RAG Demonstration")
    print("=" * 50)
    
    # Initialize enhanced RAG
    base_rag = VuetifyRAG()
    enhanced_rag = enhanced_module.EnhancedVuetifyRAG(base_rag)
    
    # Test queries
    queries = [
        "button colors",
        "v-btn styling",
        "card elevation",
        "theme customization"
    ]
    
    for query in queries:
        print(f"\n🔍 Testing: '{query}'")
        print("-" * 30)
        
        result = enhanced_rag.smart_query(query, n_results=2)
        
        # Show analysis
        analysis = result['analysis']
        print(f"Type: {analysis['type']}")
        print(f"Components: {analysis['components'][:3]}...")  # Show first 3
        print(f"Confidence: {analysis['confidence']:.2f}")
        
        # Show brief response
        response = result['response']
        if "No relevant" in response:
            print("Response: No relevant documentation found")
        else:
            lines = response.split('\n')[:3]  # First 3 lines
            print(f"Response: {' '.join(lines)[:150]}...")
        
        # Show sources
        sources = result['sources']
        print(f"Sources: {len(sources)} chunks")

if __name__ == "__main__":
    main() 