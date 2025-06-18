#!/usr/bin/env python3
"""
ChromaDB Setup Script for Vuetify Documentation
Initializes vector database with full dataset and provides configuration options.
"""

import chromadb
import json
import os
import sys
from typing import List, Dict, Any, Optional
import argparse
from tqdm import tqdm
import time

class VuetifyChromaDBSetup:
    """Setup and configure ChromaDB for Vuetify documentation."""
    
    def __init__(self, 
                 persist_directory: str = "./chromadb_data",
                 collection_name: str = "vuetify_docs"):
        """
        Initialize ChromaDB setup.
        
        Args:
            persist_directory: Directory to persist ChromaDB data
            collection_name: Name of the collection to create
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        
    def clean_metadata(self, metadata_dict: Dict[str, Any]) -> Dict[str, str]:
        """Clean metadata by removing None values and ensuring all values are strings."""
        cleaned = {}
        for key, value in metadata_dict.items():
            if value is not None:
                # Convert all values to strings to ensure compatibility
                cleaned[key] = str(value)
            else:
                # Convert None to empty string
                cleaned[key] = ""
        return cleaned
    
    def initialize_client(self, use_persistent: bool = True) -> chromadb.Client:
        """
        Initialize ChromaDB client.
        
        Args:
            use_persistent: Whether to use persistent storage
            
        Returns:
            ChromaDB client instance
        """
        print("🔧 Initializing ChromaDB client...")
        
        if use_persistent:
            # Create persist directory if it doesn't exist
            os.makedirs(self.persist_directory, exist_ok=True)
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            print(f"   ✓ Using persistent storage: {self.persist_directory}")
        else:
            self.client = chromadb.Client()
            print("   ✓ Using in-memory storage")
            
        return self.client
    
    def create_collection(self, reset_if_exists: bool = False) -> chromadb.Collection:
        """
        Create or get collection.
        
        Args:
            reset_if_exists: Whether to reset collection if it already exists
            
        Returns:
            ChromaDB collection instance
        """
        if not self.client:
            raise ValueError("Client not initialized. Call initialize_client() first.")
            
        print(f"📁 Setting up collection: {self.collection_name}")
        
        # Check if collection exists
        try:
            existing_collections = [col.name for col in self.client.list_collections()]
            
            if self.collection_name in existing_collections:
                if reset_if_exists:
                    print("   ⚠️  Collection exists. Deleting and recreating...")
                    self.client.delete_collection(self.collection_name)
                    self.collection = self.client.create_collection(self.collection_name)
                    print("   ✓ Collection recreated")
                else:
                    print("   ✓ Using existing collection")
                    self.collection = self.client.get_collection(self.collection_name)
            else:
                self.collection = self.client.create_collection(self.collection_name)
                print("   ✓ Collection created")
                
        except Exception as e:
            print(f"   ❌ Error creating collection: {e}")
            raise
            
        return self.collection
    
    def load_chunks(self, filename: str) -> List[Dict[str, Any]]:
        """
        Load chunks from JSON file.
        
        Args:
            filename: Path to JSON file containing chunks
            
        Returns:
            List of chunk dictionaries
        """
        print(f"📄 Loading chunks from: {filename}")
        
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Chunks file not found: {filename}")
            
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                chunks = json.load(f)
            print(f"   ✓ Loaded {len(chunks)} chunks")
            return chunks
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {filename}: {e}")
        except Exception as e:
            raise ValueError(f"Error loading {filename}: {e}")
    
    def add_chunks_to_collection(self, 
                                chunks: List[Dict[str, Any]], 
                                batch_size: int = 100,
                                max_chunks: Optional[int] = None) -> int:
        """
        Add chunks to ChromaDB collection in batches.
        
        Args:
            chunks: List of chunk dictionaries
            batch_size: Number of chunks to process in each batch
            max_chunks: Maximum number of chunks to process (None for all)
            
        Returns:
            Number of chunks successfully added
        """
        if not self.collection:
            raise ValueError("Collection not initialized. Call create_collection() first.")
            
        # Limit chunks if specified
        if max_chunks:
            chunks = chunks[:max_chunks]
            
        total_chunks = len(chunks)
        print(f"📥 Adding {total_chunks} chunks to collection (batch size: {batch_size})")
        
        added_count = 0
        failed_count = 0
        
        # Process in batches with progress bar
        with tqdm(total=total_chunks, desc="Adding chunks") as pbar:
            for i in range(0, total_chunks, batch_size):
                batch = chunks[i:i + batch_size]
                
                try:
                    # Prepare batch data
                    documents = [chunk['text'] for chunk in batch]
                    metadatas = [self.clean_metadata(chunk['metadata']) for chunk in batch]
                    ids = [chunk['id'] for chunk in batch]
                    
                    # Add batch to collection
                    self.collection.add(
                        documents=documents,
                        metadatas=metadatas,
                        ids=ids
                    )
                    
                    added_count += len(batch)
                    pbar.update(len(batch))
                    
                except Exception as e:
                    failed_count += len(batch)
                    print(f"\n   ❌ Error adding batch {i//batch_size + 1}: {e}")
                    pbar.update(len(batch))
                    
                # Small delay to prevent overwhelming the system
                time.sleep(0.01)
        
        print(f"   ✅ Successfully added: {added_count} chunks")
        if failed_count > 0:
            print(f"   ❌ Failed to add: {failed_count} chunks")
            
        return added_count
    
    def verify_setup(self, sample_queries: Optional[List[str]] = None) -> bool:
        """
        Verify that the ChromaDB setup is working correctly.
        
        Args:
            sample_queries: List of test queries to run
            
        Returns:
            True if verification passes, False otherwise
        """
        if not self.collection:
            print("❌ Collection not available for verification")
            return False
            
        print("🔍 Verifying ChromaDB setup...")
        
        try:
            # Check collection count
            count = self.collection.count()
            print(f"   ✓ Collection contains {count} documents")
            
            if count == 0:
                print("   ⚠️  Collection is empty")
                return False
            
            # Test sample queries
            if not sample_queries:
                sample_queries = [
                    "v-btn component usage",
                    "color props",
                    "API documentation"
                ]
            
            print("   🔍 Testing sample queries...")
            for query in sample_queries:
                try:
                    results = self.collection.query(
                        query_texts=[query],
                        n_results=3
                    )
                    
                    if results and results['documents'] and results['documents'][0]:
                        print(f"      ✓ '{query}': Found {len(results['documents'][0])} results")
                    else:
                        print(f"      ⚠️  '{query}': No results found")
                        
                except Exception as e:
                    print(f"      ❌ '{query}': Query failed - {e}")
                    return False
            
            print("   ✅ Verification completed successfully!")
            return True
            
        except Exception as e:
            print(f"   ❌ Verification failed: {e}")
            return False
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the current collection."""
        if not self.collection:
            return {"error": "Collection not initialized"}
            
        try:
            count = self.collection.count()
            
            # Get a sample document to show structure
            sample_result = self.collection.query(
                query_texts=["sample"],
                n_results=1
            )
            
            info = {
                "collection_name": self.collection_name,
                "document_count": count,
                "persist_directory": self.persist_directory,
                "sample_available": bool(sample_result and sample_result['documents'])
            }
            
            if info["sample_available"]:
                sample_metadata = sample_result['metadatas'][0][0] if sample_result['metadatas'][0] else {}
                info["sample_metadata_keys"] = list(sample_metadata.keys())
                
            return info
            
        except Exception as e:
            return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(description='Setup ChromaDB for Vuetify documentation')
    parser.add_argument('--chunks-file', '-f', 
                       default='vuetify_chunks_embedding_ready.json',
                       help='Path to chunks JSON file')
    parser.add_argument('--collection-name', '-c',
                       default='vuetify_docs',
                       help='Name of ChromaDB collection')
    parser.add_argument('--persist-dir', '-p',
                       default='./chromadb_data',
                       help='Directory for persistent storage')
    parser.add_argument('--batch-size', '-b',
                       type=int, default=100,
                       help='Batch size for adding documents')
    parser.add_argument('--max-chunks', '-m',
                       type=int, default=None,
                       help='Maximum number of chunks to process (for testing)')
    parser.add_argument('--reset', '-r',
                       action='store_true',
                       help='Reset collection if it exists')
    parser.add_argument('--memory-only',
                       action='store_true',
                       help='Use in-memory storage instead of persistent')
    
    args = parser.parse_args()
    
    # Initialize setup
    setup = VuetifyChromaDBSetup(
        persist_directory=args.persist_dir,
        collection_name=args.collection_name
    )
    
    try:
        print("🚀 Starting ChromaDB setup for Vuetify documentation")
        print("=" * 60)
        
        # Initialize client
        setup.initialize_client(use_persistent=not args.memory_only)
        
        # Create collection
        setup.create_collection(reset_if_exists=args.reset)
        
        # Load chunks
        chunks = setup.load_chunks(args.chunks_file)
        
        # Add chunks to collection
        added_count = setup.add_chunks_to_collection(
            chunks=chunks,
            batch_size=args.batch_size,
            max_chunks=args.max_chunks
        )
        
        # Verify setup
        if setup.verify_setup():
            print("\n🎉 ChromaDB setup completed successfully!")
            
            # Show collection info
            info = setup.get_collection_info()
            print("\n📊 Collection Information:")
            for key, value in info.items():
                if key != "error":
                    print(f"   {key}: {value}")
                    
        else:
            print("\n❌ Setup verification failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 