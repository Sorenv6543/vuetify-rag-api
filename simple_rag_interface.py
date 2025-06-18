#!/usr/bin/env python3
"""
Simple RAG Query Interface for Vuetify Documentation
Combines ChromaDB search with OpenAI for intelligent responses
"""

import os
import json
import chromadb
from typing import List, Dict, Any, Optional
import argparse

# Optional: OpenAI integration
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("💡 Install OpenAI for enhanced responses: pip install openai")

class VuetifyRAG:
    """Simple RAG system for Vuetify documentation"""
    
    def __init__(self, chroma_db_path: str = "./chromadb_data"):
        """Initialize the RAG system"""
        self.chroma_db_path = chroma_db_path
        self.client = None
        self.collection = None
        self.openai_client = None
        
        self._setup_chromadb()
        self._setup_openai()
    
    def _setup_chromadb(self):
        """Setup ChromaDB connection"""
        try:
            # Use PersistentClient to match our setup
            self.client = chromadb.PersistentClient(path=self.chroma_db_path)
            
            # Get the collection we created earlier
            self.collection = self.client.get_collection("vuetify_docs")
            count = self.collection.count()
            print(f"✅ Connected to ChromaDB ({count} documents)")
            
        except Exception as e:
            print(f"❌ ChromaDB connection failed: {e}")
            print("💡 Run setup_chromadb.py first to create the database!")
            exit(1)
    
    def _setup_openai(self):
        """Setup OpenAI client if available"""
        if not OPENAI_AVAILABLE:
            return
        
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            self.openai_client = openai.OpenAI(api_key=api_key)
            print("✅ OpenAI client initialized")
        else:
            print("💡 Set OPENAI_API_KEY for AI-powered responses")
    
    def search(self, query: str, n_results: int = 5, 
               component_filter: str = None) -> List[Dict[str, Any]]:
        """Search the documentation"""
        
        # Build filters
        where_clause = None
        if component_filter:
            where_clause = {"component": component_filter}
        
        try:
            # Search ChromaDB
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_clause
            )
            
            # Format results
            formatted_results = []
            documents = results['documents'][0]
            metadatas = results['metadatas'][0]
            distances = results['distances'][0]
            
            for doc, metadata, distance in zip(documents, metadatas, distances):
                formatted_results.append({
                    'content': doc,
                    'metadata': metadata,
                    'similarity_score': 1 - distance,
                    'distance': distance
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    def generate_response(self, query: str, search_results: List[Dict[str, Any]]) -> str:
        """Generate AI response using search results"""
        
        if not self.openai_client:
            return self._format_simple_response(search_results)
        
        # Prepare context from search results
        context_parts = []
        for i, result in enumerate(search_results):
            metadata = result['metadata']
            component = metadata.get('component', 'Unknown')
            section = metadata.get('subsection', 'General')
            content = result['content']
            
            context_parts.append(f"[Source {i+1}: {component} - {section}]\n{content}")
        
        context = "\n\n".join(context_parts)
        
        # Create system prompt
        system_prompt = """You are a helpful Vuetify expert assistant. Use the provided documentation to answer questions about Vuetify components, their usage, props, and examples.

Guidelines:
- Always base your answers on the provided context
- Include specific component names and props when relevant
- Provide code examples when available in the context
- If the context doesn't contain enough information, say so clearly
- Focus on practical, actionable advice
- Keep responses concise but complete"""
        
        # Create user prompt
        user_prompt = f"""Context from Vuetify Documentation:
{context}

User Question: {query}

Please provide a helpful answer based on the documentation context above."""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"⚠️  OpenAI error: {e}")
            return self._format_simple_response(search_results)
    
    def _format_simple_response(self, search_results: List[Dict[str, Any]]) -> str:
        """Format a simple response without AI"""
        if not search_results:
            return "No relevant documentation found for your query."
        
        response_parts = ["Based on the Vuetify documentation:\n"]
        
        for i, result in enumerate(search_results, 1):
            metadata = result['metadata']
            component = metadata.get('component', 'Unknown')
            section = metadata.get('subsection', 'General')
            content_type = metadata.get('content_type', 'documentation')
            score = result['similarity_score']
            
            content = result['content']
            # Take first 300 chars as summary
            summary = content[:300] + "..." if len(content) > 300 else content
            
            response_parts.append(f"{i}. {component} - {section} ({content_type}) [relevance: {score:.2f}]:")
            response_parts.append(f"   {summary}")
            response_parts.append("")
        
        return "\n".join(response_parts)
    
    def query(self, user_query: str, n_results: int = 5, 
              component_filter: str = None) -> Dict[str, Any]:
        """Complete query pipeline"""
        
        print(f"🔍 Searching for: '{user_query}'")
        if component_filter:
            print(f"📌 Filtered to component: {component_filter}")
        
        # Search for relevant chunks
        search_results = self.search(user_query, n_results, component_filter)
        
        if not search_results:
            return {
                'query': user_query,
                'response': "No relevant documentation found.",
                'sources': []
            }
        
        print(f"📚 Found {len(search_results)} relevant chunks")
        
        # Generate response
        response = self.generate_response(user_query, search_results)
        
        return {
            'query': user_query,
            'response': response,
            'sources': [
                {
                    'component': result['metadata'].get('component'),
                    'section': result['metadata'].get('subsection'),
                    'type': result['metadata'].get('content_type'),
                    'similarity': f"{result['similarity_score']:.3f}"
                }
                for result in search_results
            ]
        }

def interactive_mode(rag: VuetifyRAG):
    """Interactive query mode"""
    print("\n🎯 Interactive Vuetify Documentation Assistant")
    print("=" * 50)
    print("Ask questions about Vuetify components!")
    print("Type 'quit' to exit, 'help' for help")
    print()
    
    while True:
        try:
            # Get user input
            query = input("💬 Your question: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if query.lower() == 'help':
                print("\n📖 Help:")
                print("- Ask questions like: 'How to use v-btn with custom colors?'")
                print("- Filter by component: 'v-card elevation' will focus on v-card")
                print("- Ask about props: 'v-text-field validation rules'")
                print("- Request examples: 'v-data-table sorting example'")
                print()
                continue
            
            if not query:
                continue
            
            # Detect component filter
            component_filter = None
            query_lower = query.lower()
            if query_lower.startswith('v-'):
                # Extract component name
                words = query_lower.split()
                for word in words:
                    if word.startswith('v-') and len(word) > 2:
                        component_filter = word
                        break
            
            # Process query
            result = rag.query(query, component_filter=component_filter)
            
            # Display results
            print(f"\n🤖 Response:")
            print("-" * 40)
            print(result['response'])
            
            print(f"\n📚 Sources:")
            for i, source in enumerate(result['sources'], 1):
                component = source['component'] or 'Unknown'
                section = source['section'] or 'General'
                content_type = source['type'] or 'documentation'
                similarity = source['similarity']
                print(f"  {i}. {component} - {section} "
                      f"({content_type}, similarity: {similarity})")
            
            print("\n" + "="*50)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def batch_test_mode(rag: VuetifyRAG):
    """Test with predefined queries"""
    print("\n🧪 Running Batch Tests")
    print("=" * 50)
    
    test_queries = [
        "How do I create a button with custom colors?",
        "v-data-table sorting and pagination",
        "v-form validation with rules",
        "v-card elevation and styling",
        "responsive navigation drawer",
        "v-text-field input validation",
        "theme customization",
        "v-dialog modal examples"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: {query}")
        print("-" * 40)
        
        result = rag.query(query, n_results=3)
        
        # Show summary
        response = result['response']
        summary = response[:200] + "..." if len(response) > 200 else response
        print(f"Response: {summary}")
        
        print(f"Sources: {len(result['sources'])} chunks")
        for source in result['sources'][:2]:  # Show top 2 sources
            component = source['component'] or 'Unknown'
            similarity = source['similarity']
            print(f"  - {component} ({similarity})")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Vuetify Documentation RAG System')
    parser.add_argument('--mode', choices=['interactive', 'test'], 
                       default='interactive', help='Run mode')
    parser.add_argument('--query', '-q', help='Single query to run')
    parser.add_argument('--component', '-c', help='Filter by component')
    parser.add_argument('--db-path', default='./chromadb_data', 
                       help='Path to ChromaDB data directory')
    
    args = parser.parse_args()
    
    print("🚀 Initializing Vuetify RAG System...")
    
    # Initialize RAG system
    try:
        rag = VuetifyRAG(chroma_db_path=args.db_path)
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return
    
    # Run based on mode
    if args.query:
        # Single query mode
        result = rag.query(args.query, component_filter=args.component)
        
        print(f"\nQuery: {result['query']}")
        print(f"\nResponse:")
        print("-" * 40)
        print(result['response'])
        print(f"\nSources: {len(result['sources'])} chunks")
        for i, source in enumerate(result['sources'], 1):
            component = source['component'] or 'Unknown'
            section = source['section'] or 'General'
            similarity = source['similarity']
            print(f"  {i}. {component} - {section} ({similarity})")
        
    elif args.mode == 'test':
        batch_test_mode(rag)
    else:
        interactive_mode(rag)

if __name__ == "__main__":
    main() 