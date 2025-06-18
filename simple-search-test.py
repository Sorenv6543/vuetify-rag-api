#!/usr/bin/env python3
"""
Simple search test for chunked documentation
"""

import json
import re
from typing import List, Dict, Any

def simple_text_search(chunks: List[Dict[str, Any]], query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Simple text-based search through chunks"""
    query_lower = query.lower()
    results = []
    
    for chunk in chunks:
        content_lower = chunk['content'].lower()
        
        # Calculate relevance score (simple keyword matching)
        score = 0
        
        # Component name match (high weight)
        if query_lower in chunk['metadata'].get('component', '').lower():
            score += 10
        
        # Content matches
        matches = len(re.findall(re.escape(query_lower), content_lower))
        score += matches * 2
        
        # Subsection title match
        if query_lower in chunk['metadata'].get('subsection', '').lower():
            score += 5
        
        if score > 0:
            results.append({
                'chunk': chunk,
                'score': score,
                'matches': matches
            })
    
    # Sort by score and return top results
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:max_results]

def test_search_queries(chunks_file: str):
    """Test various search queries"""
    print("🔍 Testing Search Functionality")
    print("=" * 50)
    
    # Load chunks
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    print(f"📚 Loaded {len(chunks)} chunks")
    
    # Test queries
    test_queries = [
        "v-btn color",
        "button props",
        "data table sorting", 
        "form validation",
        "card elevation",
        "theme colors"
    ]
    
    for query in test_queries:
        print(f"\n🔎 Query: '{query}'")
        print("-" * 30)
        
        results = simple_text_search(chunks, query, max_results=3)
        
        if results:
            for i, result in enumerate(results, 1):
                chunk = result['chunk']
                metadata = chunk['metadata']
                
                print(f"{i}. {metadata.get('component', 'Unknown')} - {metadata.get('subsection', 'N/A')}")
                print(f"   Type: {metadata.get('content_type', 'Unknown')}")
                print(f"   Score: {result['score']}, Matches: {result['matches']}")
                
                # Show snippet
                content = chunk['content']
                if len(content) > 150:
                    snippet = content[:150] + "..."
                else:
                    snippet = content
                print(f"   Preview: {snippet}")
                print()
        else:
            print("   No results found")

def export_component_list(chunks_file: str):
    """Export list of all components found"""
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    components = set()
    for chunk in chunks:
        if component := chunk['metadata'].get('component'):
            components.add(component)
    
    components_list = sorted(list(components))
    
    print(f"\n📋 Found {len(components_list)} components:")
    for i, component in enumerate(components_list, 1):
        print(f"{i:2d}. {component}")
    
    # Save to file
    with open('vuetify_components_list.txt', 'w') as f:
        for component in components_list:
            f.write(f"{component}\n")
    
    print(f"\n💾 Component list saved to 'vuetify_components_list.txt'")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python simple_search_test.py vuetify_chunks.json")
        sys.exit(1)
    
    chunks_file = sys.argv[1]
    
    try:
        test_search_queries(chunks_file)
        export_component_list(chunks_file)
        
        print(f"\n✅ Search test complete!")
        print(f"Your chunks are ready for vector database integration!")
        
    except FileNotFoundError:
        print(f"❌ Error: File '{chunks_file}' not found!")
    except Exception as e:
        print(f"❌ Error: {e}")
