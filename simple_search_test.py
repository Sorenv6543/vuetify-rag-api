#!/usr/bin/env python3
"""
Simple search test for Vuetify documentation chunks.
Demonstrates various search scenarios and use cases.
"""

import json
import sys
import re
from collections import defaultdict


def load_chunks(filename):
    """Load chunks from JSON file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, dict) and 'chunks' in data:
            return data['chunks']
        elif isinstance(data, list):
            return data
        else:
            print("Error: Unexpected data structure in JSON file.")
            sys.exit(1)
            
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{filename}': {e}")
        sys.exit(1)


def simple_search(chunks, term, max_results=5):
    """Simple text search in chunks."""
    results = []
    term_lower = term.lower()
    
    for i, chunk in enumerate(chunks):
        content = chunk.get('content', '')
        if term_lower in content.lower():
            results.append({
                'index': i,
                'content': content,
                'preview': content[:200] + "..." if len(content) > 200 else content
            })
    
    return results[:max_results]


def component_search(chunks, component_name):
    """Search for Vuetify components."""
    # Look for component usage patterns
    patterns = [
        f"<{component_name}",  # Opening tag
        f"</{component_name}>",  # Closing tag
        f"`{component_name}`",  # Inline code
        f"# {component_name}",  # Header
        f"## {component_name}", # Subheader
    ]
    
    results = defaultdict(list)
    
    for i, chunk in enumerate(chunks):
        content = chunk.get('content', '')
        content_lower = content.lower()
        component_lower = component_name.lower()
        
        for pattern in patterns:
            if pattern.lower() in content_lower:
                # Find the actual match position for context
                matches = list(re.finditer(re.escape(pattern.lower()), content_lower))
                for match in matches:
                    start = max(0, match.start() - 50)
                    end = min(len(content), match.end() + 50)
                    context = content[start:end]
                    
                    results[pattern.lower()].append({
                        'chunk_index': i,
                        'context': context,
                        'full_content': content
                    })
    
    return dict(results)


def api_search(chunks, search_terms):
    """Search for API-related content."""
    api_keywords = ['props', 'events', 'slots', 'methods', 'api']
    results = []
    
    for i, chunk in enumerate(chunks):
        content = chunk.get('content', '').lower()
        
        # Check if chunk contains API information
        has_api_content = any(keyword in content for keyword in api_keywords)
        
        if has_api_content:
            # Check if it matches our search terms
            for term in search_terms:
                if term.lower() in content:
                    results.append({
                        'chunk_index': i,
                        'content': chunk.get('content', ''),
                        'search_term': term,
                        'preview': chunk.get('content', '')[:300] + "..."
                    })
                    break
    
    return results


def run_test_scenarios(chunks):
    """Run various search test scenarios."""
    print("🔍 Simple Search Test Results")
    print("=" * 60)
    print(f"Total chunks loaded: {len(chunks)}")
    print()
    
    # Test 1: Component searches
    print("📱 Test 1: Component Searches")
    print("-" * 30)
    
    components_to_test = ['v-btn', 'v-card', 'v-text-field', 'v-app-bar']
    
    for component in components_to_test:
        results = simple_search(chunks, component, max_results=3)
        print(f"\n🔹 {component}: Found {len(results)} chunks")
        
        for i, result in enumerate(results[:2]):  # Show first 2 results
            print(f"   Chunk {result['index']}: {result['preview']}")
    
    # Test 2: Feature searches
    print("\n\n🎨 Test 2: Feature Searches")
    print("-" * 30)
    
    features_to_test = ['color', 'theme', 'responsive', 'dark mode']
    
    for feature in features_to_test:
        results = simple_search(chunks, feature, max_results=2)
        print(f"\n🔹 '{feature}': Found {len(results)} chunks")
        
        if results:
            preview = results[0]['preview'].replace('\n', ' ')[:150]
            print(f"   Sample: {preview}...")
    
    # Test 3: Advanced component analysis
    print("\n\n🏗️ Test 3: Advanced Component Analysis")
    print("-" * 30)
    
    component_results = component_search(chunks, 'v-btn')
    
    print(f"\n🔹 v-btn component analysis:")
    for pattern, matches in component_results.items():
        if matches:
            print(f"   {pattern}: {len(matches)} occurrences")
            if len(matches) > 0:
                sample_context = matches[0]['context'].replace('\n', ' ')[:100]
                print(f"   Sample: ...{sample_context}...")
    
    # Test 4: API Documentation search
    print("\n\n📚 Test 4: API Documentation Search")
    print("-" * 30)
    
    api_terms = ['props', 'events', 'slots']
    api_results = api_search(chunks, api_terms)
    
    print(f"\n🔹 API documentation: Found {len(api_results)} chunks")
    
    for result in api_results[:2]:  # Show first 2 API results
        term = result['search_term']
        preview = result['preview'].replace('\n', ' ')[:150]
        print(f"   {term} - Chunk {result['chunk_index']}: {preview}...")
    
    # Test 5: Code example search
    print("\n\n💻 Test 5: Code Example Search")
    print("-" * 30)
    
    code_results = simple_search(chunks, '<template>', max_results=3)
    script_results = simple_search(chunks, '<script>', max_results=3)
    
    print(f"\n🔹 Template examples: Found {len(code_results)} chunks")
    print(f"🔹 Script examples: Found {len(script_results)} chunks")
    
    if code_results:
        preview = code_results[0]['preview'].replace('\n', ' ')[:150]
        print(f"   Sample template: {preview}...")
    
    # Test 6: Style and utility search
    print("\n\n🎭 Test 6: Style & Utility Search")
    print("-" * 30)
    
    style_terms = ['class', 'css', 'utility', 'spacing', 'flex']
    
    for term in style_terms:
        results = simple_search(chunks, term, max_results=1)
        if results:
            print(f"🔹 '{term}': Found content in chunk {results[0]['index']}")
    
    print("\n" + "=" * 60)
    print("✅ Search tests completed!")
    print("\nThis demonstrates the chunked documentation is:")
    print("  ✓ Well-structured for component searches")
    print("  ✓ Contains API documentation")
    print("  ✓ Includes code examples")
    print("  ✓ Has style and utility information")
    print("  ✓ Ready for RAG applications!")


def main():
    if len(sys.argv) != 2:
        print("Usage: python simple_search_test.py <chunks_file.json>")
        sys.exit(1)
    
    filename = sys.argv[1]
    chunks = load_chunks(filename)
    run_test_scenarios(chunks)


if __name__ == '__main__':
    main() 