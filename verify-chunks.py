#!/usr/bin/env python3
"""
Verify and explore chunked Vuetify documentation
"""

import json
from collections import defaultdict
import argparse

def load_chunks(filename):
    """Load chunks from JSON file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def explore_chunks(chunks):
    """Explore and analyze the chunks"""
    print(f"📊 Chunk Exploration Report")
    print("=" * 50)
    
    total_chunks = len(chunks)
    print(f"Total chunks: {total_chunks}")
    
    # Analyze chunk sizes
    sizes = [chunk['content_length'] for chunk in chunks]
    avg_size = sum(sizes) / len(sizes)
    max_size = max(sizes)
    min_size = min(sizes)
    
    print(f"Chunk sizes: avg={avg_size:.0f}, min={min_size}, max={max_size}")
    
    # Component breakdown
    components = defaultdict(int)
    content_types = defaultdict(int)
    
    for chunk in chunks:
        metadata = chunk['metadata']
        components[metadata.get('component', 'Unknown')] += 1
        content_types[metadata.get('content_type', 'Unknown')] += 1
    
    print(f"\n🧩 Components (top 10):")
    for component, count in sorted(components.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {component}: {count} chunks")
    
    print(f"\n📝 Content Types:")
    for content_type, count in sorted(content_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {content_type}: {count} chunks")

def show_sample_chunks(chunks, num_samples=3):
    """Show sample chunks"""
    print(f"\n📖 Sample Chunks:")
    print("=" * 50)
    
    # Show different types of chunks
    content_types = ['component_overview', 'code_example', 'api_reference', 'documentation']
    
    for content_type in content_types:
        matching_chunks = [c for c in chunks if c['metadata'].get('content_type') == content_type]
        if matching_chunks:
            chunk = matching_chunks[0]
            print(f"\n📋 {content_type.replace('_', ' ').title()} Example:")
            print(f"Component: {chunk['metadata'].get('component', 'Unknown')}")
            print(f"Section: {chunk['metadata'].get('subsection', 'N/A')}")
            print(f"Length: {chunk['content_length']} chars")
            print("-" * 40)
            content_preview = chunk['content'][:300] + "..." if len(chunk['content']) > 300 else chunk['content']
            print(content_preview)
            print()

def search_chunks(chunks, query):
    """Search for chunks containing a query"""
    print(f"\n🔍 Searching for: '{query}'")
    print("=" * 50)
    
    matching_chunks = []
    query_lower = query.lower()
    
    for chunk in chunks:
        if query_lower in chunk['content'].lower():
            matching_chunks.append(chunk)
    
    print(f"Found {len(matching_chunks)} matching chunks")
    
    # Show first few matches
    for i, chunk in enumerate(matching_chunks[:5]):
        metadata = chunk['metadata']
        print(f"\n{i+1}. {metadata.get('component', 'Unknown')} - {metadata.get('subsection', 'N/A')}")
        print(f"   Type: {metadata.get('content_type', 'Unknown')}")
        
        # Find the query in content and show context
        content = chunk['content']
        content_lower = content.lower()
        start_idx = content_lower.find(query_lower)
        if start_idx != -1:
            # Show 100 chars before and after
            context_start = max(0, start_idx - 100)
            context_end = min(len(content), start_idx + len(query) + 100)
            context = content[context_start:context_end]
            print(f"   Context: ...{context}...")

def validate_chunks(chunks):
    """Validate chunk structure and content"""
    print(f"\n✅ Validation Report:")
    print("=" * 50)
    
    issues = []
    
    for i, chunk in enumerate(chunks):
        # Check required fields
        if 'chunk_id' not in chunk:
            issues.append(f"Chunk {i}: Missing chunk_id")
        
        if 'content' not in chunk or not chunk['content'].strip():
            issues.append(f"Chunk {i}: Empty content")
        
        if 'metadata' not in chunk:
            issues.append(f"Chunk {i}: Missing metadata")
        else:
            metadata = chunk['metadata']
            if 'component' not in metadata:
                issues.append(f"Chunk {i}: Missing component in metadata")
    
    if issues:
        print(f"❌ Found {len(issues)} issues:")
        for issue in issues[:10]:  # Show first 10 issues
            print(f"  - {issue}")
        if len(issues) > 10:
            print(f"  ... and {len(issues) - 10} more")
    else:
        print("✅ All chunks are valid!")
    
    return len(issues) == 0

def main():
    parser = argparse.ArgumentParser(description='Verify chunked Vuetify documentation')
    parser.add_argument('chunks_file', help='JSON file containing chunks')
    parser.add_argument('--search', '-s', help='Search for specific content')
    parser.add_argument('--samples', '-n', type=int, default=3, help='Number of sample chunks to show')
    
    args = parser.parse_args()
    
    try:
        chunks = load_chunks(args.chunks_file)
        print(f"📁 Loaded {len(chunks)} chunks from {args.chunks_file}")
        
        # Validate chunks
        is_valid = validate_chunks(chunks)
        
        if is_valid:
            # Explore chunks
            explore_chunks(chunks)
            
            # Show samples
            show_sample_chunks(chunks, args.samples)
            
            # Search if query provided
            if args.search:
                search_chunks(chunks, args.search)
        
    except FileNotFoundError:
        print(f"❌ Error: File '{args.chunks_file}' not found!")
    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON in '{args.chunks_file}'!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
