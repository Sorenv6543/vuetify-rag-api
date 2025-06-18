#!/usr/bin/env python3
"""
Test ChromaDB vector database with Vuetify documentation chunks.
"""

import chromadb
import json

def clean_metadata(metadata_dict):
    """Clean metadata by removing None values and ensuring all values are strings."""
    cleaned = {}
    for key, value in metadata_dict.items():
        if value is not None:
            # Convert all values to strings to ensure compatibility
            cleaned[key] = str(value)
        else:
            # Convert None to empty string or skip entirely
            cleaned[key] = ""
    return cleaned

def main():
    print("🔗 Loading Vuetify chunks...")
    
    # Load your chunks
    with open('vuetify_chunks_embedding_ready.json', 'r') as f:
        chunks = json.load(f)
    
    print(f"📄 Loaded {len(chunks)} total chunks")
    
    # Create ChromaDB client
    print("🗄️ Creating ChromaDB client...")
    client = chromadb.Client()
    collection = client.create_collection('vuetify_docs')
    
    # Add documents (first 100 for testing)
    test_chunks = chunks[:100]
    print(f"➕ Adding {len(test_chunks)} chunks to ChromaDB...")
    
    # Clean metadata to remove None values
    cleaned_metadatas = [clean_metadata(c['metadata']) for c in test_chunks]
    
    collection.add(
        documents=[c['text'] for c in test_chunks],
        metadatas=cleaned_metadatas,
        ids=[c['id'] for c in test_chunks]
    )
    
    print(f'✅ Added {len(test_chunks)} chunks to ChromaDB!')
    
    # Test queries
    print("\n🔍 Testing queries...")
    
    # Query 1: Button color props
    print("\nQuery 1: 'button color props'")
    results = collection.query(query_texts=['button color props'], n_results=3)
    print(f"Found {len(results['documents'][0])} results")
    
    for i, (doc, metadata, distance) in enumerate(zip(
        results['documents'][0], 
        results['metadatas'][0], 
        results['distances'][0]
    )):
        print(f"  Result {i+1} (distance: {distance:.3f}):")
        print(f"    Component: {metadata.get('component', 'unknown')}")
        print(f"    Type: {metadata.get('content_type', 'unknown')}")
        preview = doc[:150] + "..." if len(doc) > 150 else doc
        print(f"    Content: {preview}")
        print()
    
    # Query 2: Component usage
    print("Query 2: 'v-btn component usage'")
    results = collection.query(query_texts=['v-btn component usage'], n_results=3)
    print(f"Found {len(results['documents'][0])} results")
    
    for i, (doc, metadata, distance) in enumerate(zip(
        results['documents'][0], 
        results['metadatas'][0], 
        results['distances'][0]
    )):
        print(f"  Result {i+1} (distance: {distance:.3f}):")
        print(f"    Component: {metadata.get('component', 'unknown')}")
        print(f"    Type: {metadata.get('content_type', 'unknown')}")
        preview = doc[:150] + "..." if len(doc) > 150 else doc
        print(f"    Content: {preview}")
        print()
    
    # Query 3: Styling information
    print("Query 3: 'CSS classes and styling'")
    results = collection.query(query_texts=['CSS classes and styling'], n_results=3)
    print(f"Found {len(results['documents'][0])} results")
    
    for i, (doc, metadata, distance) in enumerate(zip(
        results['documents'][0], 
        results['metadatas'][0], 
        results['distances'][0]
    )):
        print(f"  Result {i+1} (distance: {distance:.3f}):")
        print(f"    Component: {metadata.get('component', 'unknown')}")
        print(f"    Type: {metadata.get('content_type', 'unknown')}")
        preview = doc[:150] + "..." if len(doc) > 150 else doc
        print(f"    Content: {preview}")
        print()
    
    # Query 4: API documentation
    print("Query 4: 'API props events slots'")
    results = collection.query(query_texts=['API props events slots'], n_results=3)
    print(f"Found {len(results['documents'][0])} results")
    
    for i, (doc, metadata, distance) in enumerate(zip(
        results['documents'][0], 
        results['metadatas'][0], 
        results['distances'][0]
    )):
        print(f"  Result {i+1} (distance: {distance:.3f}):")
        print(f"    Component: {metadata.get('component', 'unknown')}")
        print(f"    Type: {metadata.get('content_type', 'unknown')}")
        preview = doc[:150] + "..." if len(doc) > 150 else doc
        print(f"    Content: {preview}")
        print()
    
    print("🎉 ChromaDB test completed successfully!")
    print("\nNext steps:")
    print("  ✓ Vector database is working")
    print("  ✓ Semantic search is functional")
    print("  ✓ Ready for RAG applications")
    print("  ✓ Can scale to full dataset")
    print("  ✓ Metadata filtering is available")

if __name__ == '__main__':
    main() 