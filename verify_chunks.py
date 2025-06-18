#!/usr/bin/env python3
"""
Verification script for chunked Vuetify documentation.
Analyzes the structure and content of the chunked JSON file.
"""

import json
import argparse
import sys
from collections import Counter
import re


def load_chunks(filename):
    """Load chunks from JSON file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{filename}': {e}")
        sys.exit(1)


def analyze_chunks(data):
    """Analyze the structure and content of chunks."""
    if isinstance(data, dict) and 'chunks' in data:
        chunks = data['chunks']
    elif isinstance(data, list):
        chunks = data
    else:
        print("Error: Unexpected data structure in JSON file.")
        sys.exit(1)
    
    print(f"📊 Chunk Analysis Report")
    print(f"=" * 50)
    print(f"Total chunks: {len(chunks)}")
    
    # Analyze chunk sizes
    chunk_sizes = [len(chunk.get('content', '')) for chunk in chunks]
    if chunk_sizes:
        print(f"Average chunk size: {sum(chunk_sizes) / len(chunk_sizes):.1f} characters")
        print(f"Smallest chunk: {min(chunk_sizes)} characters")
        print(f"Largest chunk: {max(chunk_sizes)} characters")
    
    # Analyze chunk types/sources
    sources = [chunk.get('source', 'unknown') for chunk in chunks]
    source_counts = Counter(sources)
    print(f"\n📁 Content Sources:")
    for source, count in source_counts.most_common():
        print(f"  {source}: {count} chunks")
    
    # Analyze section types
    sections = []
    for chunk in chunks:
        content = chunk.get('content', '')
        # Look for section markers
        if content.startswith('#'):
            # Extract the first line as section type
            first_line = content.split('\n')[0]
            sections.append(first_line.count('#'))
        else:
            sections.append(0)
    
    section_counts = Counter(sections)
    print(f"\n📑 Section Types (by header level):")
    for level, count in sorted(section_counts.items()):
        if level > 0:
            print(f"  Level {level} headers: {count} chunks")
        else:
            print(f"  No headers: {count} chunks")
    
    # Sample some chunks
    print(f"\n📋 Sample Chunks:")
    for i, chunk in enumerate(chunks[:3]):
        print(f"\n--- Chunk {i+1} ---")
        print(f"Source: {chunk.get('source', 'unknown')}")
        content = chunk.get('content', '')
        preview = content[:200] + "..." if len(content) > 200 else content
        print(f"Content preview: {preview}")
    
    return chunks


def search_chunks(chunks, search_term, case_sensitive=False):
    """Search for specific content in chunks."""
    search_term_display = search_term
    if not case_sensitive:
        search_term = search_term.lower()
    
    matching_chunks = []
    
    for i, chunk in enumerate(chunks):
        content = chunk.get('content', '')
        search_content = content if case_sensitive else content.lower()
        
        if search_term in search_content:
            # Find all matches with context
            if case_sensitive:
                matches = [(m.start(), m.end()) for m in re.finditer(re.escape(search_term), content)]
            else:
                matches = [(m.start(), m.end()) for m in re.finditer(re.escape(search_term), content, re.IGNORECASE)]
            
            matching_chunks.append({
                'chunk_index': i,
                'chunk': chunk,
                'matches': matches,
                'match_count': len(matches)
            })
    
    print(f"\n🔍 Search Results for '{search_term_display}'")
    print(f"=" * 50)
    print(f"Found {len(matching_chunks)} chunks containing '{search_term_display}'")
    
    total_matches = sum(result['match_count'] for result in matching_chunks)
    print(f"Total occurrences: {total_matches}")
    
    # Show details for each matching chunk
    for result in matching_chunks[:10]:  # Limit to first 10 results
        chunk = result['chunk']
        content = chunk.get('content', '')
        
        print(f"\n--- Chunk {result['chunk_index'] + 1} ---")
        print(f"Source: {chunk.get('source', 'unknown')}")
        print(f"Matches: {result['match_count']}")
        
        # Show context around first match
        if result['matches']:
            start, end = result['matches'][0]
            context_start = max(0, start - 100)
            context_end = min(len(content), end + 100)
            context = content[context_start:context_end]
            
            # Highlight the match
            highlight_start = start - context_start
            highlight_end = end - context_start
            highlighted = (
                context[:highlight_start] + 
                f"**{context[highlight_start:highlight_end]}**" + 
                context[highlight_end:]
            )
            
            print(f"Context: ...{highlighted}...")
    
    if len(matching_chunks) > 10:
        print(f"\n... and {len(matching_chunks) - 10} more results")
    
    return matching_chunks


def main():
    parser = argparse.ArgumentParser(description='Verify and search Vuetify documentation chunks')
    parser.add_argument('filename', help='JSON file containing chunks')
    parser.add_argument('--search', '-s', help='Search term to find in chunks')
    parser.add_argument('--case-sensitive', '-c', action='store_true', 
                       help='Make search case-sensitive')
    parser.add_argument('--max-results', '-m', type=int, default=10,
                       help='Maximum number of search results to show')
    
    args = parser.parse_args()
    
    # Load and analyze chunks
    data = load_chunks(args.filename)
    chunks = analyze_chunks(data)
    
    # Perform search if requested
    if args.search:
        search_chunks(chunks, args.search, args.case_sensitive)


if __name__ == '__main__':
    main()
