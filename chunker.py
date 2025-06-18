#!/usr/bin/env python3
"""
Practical Vuetify Documentation Chunker
Chunks large Vuetify documentation into vector-database-ready pieces
"""

import re
import json
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import argparse
from tqdm import tqdm

@dataclass
class DocumentChunk:
    """Represents a chunk of documentation with metadata"""
    content: str
    metadata: Dict[str, Any]
    chunk_id: str
    content_length: int
    word_count: int

class VuetifyDocChunker:
    """Simplified chunker for Vuetify documentation"""
    
    def __init__(self, max_chunk_size: int = 1200, overlap: int = 150):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap
        self.chunk_counter = 0
        self.stats = {
            'total_chunks': 0,
            'components_found': 0,
            'code_examples': 0,
            'api_sections': 0,
            'processing_time': 0
        }
        
    def chunk_documentation(self, doc_content: str) -> List[DocumentChunk]:
        """Main method to chunk the entire documentation"""
        print("🔄 Starting documentation chunking...")
        start_time = time.time()
        
        chunks = []
        
        # Split into major sections
        sections = self._extract_component_sections(doc_content)
        print(f"📚 Found {len(sections)} component sections")
        
        # Process each section with progress bar
        for section in tqdm(sections, desc="Processing sections"):
            section_chunks = self._process_component_section(section)
            chunks.extend(section_chunks)
            
        self.stats['total_chunks'] = len(chunks)
        self.stats['components_found'] = len(sections)
        self.stats['processing_time'] = time.time() - start_time
        
        print(f"✅ Chunking complete! Created {len(chunks)} chunks in {self.stats['processing_time']:.2f}s")
        return chunks
    
    def _extract_component_sections(self, content: str) -> List[Dict[str, Any]]:
        """Extract major component sections from the documentation"""
        sections = []
        
        # Look for component headers like "## Button", "## Card", etc.
        # Also catch "---" followed by "## ComponentName"
        component_pattern = r'(?:^---\s*\n)?^#{1,2}\s+([A-Z][a-zA-Z\s\-]+?)(?:\s*\n|$)'
        
        parts = re.split(component_pattern, content, flags=re.MULTILINE)
        
        current_section = None
        for i, part in enumerate(parts):
            if i == 0:  # Skip content before first header
                continue
            elif i % 2 == 1:  # This is a header
                if current_section:
                    sections.append(current_section)
                
                # Clean up component name
                component_name = part.strip()
                # Convert to v-component format if not already
                if not component_name.lower().startswith('v-'):
                    component_name = f"v-{component_name.lower().replace(' ', '-')}"
                
                current_section = {
                    'component': component_name,
                    'title': part.strip(),
                    'content': '',
                    'raw_content': ''
                }
            else:  # This is content
                if current_section:
                    current_section['content'] = part
                    current_section['raw_content'] = part
                    
        if current_section:
            sections.append(current_section)
            
        return sections
    
    def _process_component_section(self, section: Dict[str, Any]) -> List[DocumentChunk]:
        """Process a single component section into chunks"""
        chunks = []
        component_name = section['component']
        content = section['content']
        
        # Split content into subsections
        subsections = self._extract_subsections(content)
        
        # Create overview chunk first
        overview = self._create_overview_chunk(section, subsections)
        if overview:
            chunks.append(overview)
        
        # Process each subsection
        for subsection in subsections:
            subsection_chunks = self._process_subsection(subsection, component_name)
            chunks.extend(subsection_chunks)
            
        return chunks
    
    def _extract_subsections(self, content: str) -> List[Dict[str, str]]:
        """Extract subsections like Usage, Props, Examples, etc."""
        subsections = []
        
        # Pattern for subsection headers (### or #### SubsectionName)
        subsection_pattern = r'^#{3,5}\s+([^\n]+?)(?:\s*\n|$)'
        parts = re.split(subsection_pattern, content, flags=re.MULTILINE)
        
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                title = parts[i].strip()
                content_part = parts[i + 1].strip()
                
                if content_part:  # Only add non-empty sections
                    subsections.append({
                        'title': title,
                        'content': content_part
                    })
        
        return subsections
    
    def _create_overview_chunk(self, section: Dict[str, Any], 
                             subsections: List[Dict[str, str]]) -> Optional[DocumentChunk]:
        """Create an overview chunk for the component"""
        component_name = section['component']
        content = section['content']
        
        # Extract description (first paragraph)
        lines = content.split('\n')
        description_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('<') and not line.startswith('```'):
                description_lines.append(line)
                if len(' '.join(description_lines)) > 400:
                    break
            elif description_lines:
                break
        
        if not description_lines:
            return None
            
        # Build overview content
        overview_content = f"# {component_name}\n\n"
        overview_content += ' '.join(description_lines)
        
        # Add available sections
        if subsections:
            section_names = [sub['title'] for sub in subsections]
            overview_content += f"\n\nAvailable sections: {', '.join(section_names)}"
        
        return self._create_chunk(
            content=overview_content,
            metadata={
                'component': component_name,
                'section_type': 'overview',
                'subsection': None,
                'content_type': 'component_overview'
            }
        )
    
    def _process_subsection(self, subsection: Dict[str, str], 
                          component_name: str) -> List[DocumentChunk]:
        """Process a subsection into chunks"""
        chunks = []
        title = subsection['title']
        content = subsection['content']
        
        # Classify content type
        content_type = self._classify_content_type(title, content)
        
        # Handle code examples specially
        if self._has_code_blocks(content):
            code_chunks = self._process_code_content(content, component_name, title)
            chunks.extend(code_chunks)
            if content_type == 'code_example':
                self.stats['code_examples'] += len(code_chunks)
        else:
            # Regular text content
            text_chunks = self._split_large_content(content)
            for i, chunk_content in enumerate(text_chunks):
                full_content = f"## {component_name} - {title}\n\n{chunk_content}"
                
                chunk = self._create_chunk(
                    content=full_content,
                    metadata={
                        'component': component_name,
                        'section_type': 'subsection',
                        'subsection': title,
                        'content_type': content_type,
                        'chunk_index': i
                    }
                )
                chunks.append(chunk)
                
                if content_type == 'api_reference':
                    self.stats['api_sections'] += 1
        
        return chunks
    
    def _classify_content_type(self, title: str, content: str) -> str:
        """Classify the type of content"""
        title_lower = title.lower()
        
        if 'api' in title_lower or 'prop' in title_lower:
            return 'api_reference'
        elif 'usage' in title_lower:
            return 'usage_guide'
        elif 'example' in title_lower or self._has_code_blocks(content):
            return 'code_example'
        elif 'slot' in title_lower:
            return 'slots_reference'
        elif 'event' in title_lower:
            return 'events_reference'
        else:
            return 'documentation'
    
    def _has_code_blocks(self, content: str) -> bool:
        """Check if content contains code blocks"""
        return bool(re.search(r'```\w*\n', content))
    
    def _process_code_content(self, content: str, component_name: str, 
                            title: str) -> List[DocumentChunk]:
        """Process content that contains code blocks"""
        chunks = []
        
        # Split by code blocks but keep context
        parts = re.split(r'(```[\w]*\n.*?\n```)', content, flags=re.DOTALL)
        
        current_text = ""
        for part in parts:
            if part.strip().startswith('```'):
                # This is a code block
                # Combine with preceding explanation
                full_content = f"## {component_name} - {title}\n\n"
                if current_text.strip():
                    full_content += f"{current_text.strip()}\n\n"
                full_content += part.strip()
                
                # Extract language
                lang_match = re.match(r'```(\w+)', part)
                language = lang_match.group(1) if lang_match else 'text'
                
                chunk = self._create_chunk(
                    content=full_content,
                    metadata={
                        'component': component_name,
                        'section_type': 'code_example',
                        'subsection': title,
                        'content_type': 'code_example',
                        'language': language,
                        'has_explanation': bool(current_text.strip())
                    }
                )
                chunks.append(chunk)
                current_text = ""
            else:
                current_text += part
        
        return chunks
    
    def _split_large_content(self, content: str) -> List[str]:
        """Split large content into smaller chunks"""
        if len(content) <= self.max_chunk_size:
            return [content]
        
        # Split by sentences
        sentences = re.split(r'(?<=[.!?])\s+', content)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.max_chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _create_chunk(self, content: str, metadata: Dict[str, Any]) -> DocumentChunk:
        """Create a DocumentChunk with unique ID"""
        self.chunk_counter += 1
        
        chunk_id = f"vuetify_chunk_{self.chunk_counter:06d}"
        word_count = len(content.split())
        
        return DocumentChunk(
            content=content,
            metadata={
                **metadata,
                'chunk_id': chunk_id,
                'source': 'vuetify_documentation'
            },
            chunk_id=chunk_id,
            content_length=len(content),
            word_count=word_count
        )

def save_chunks_json(chunks: List[DocumentChunk], output_file: str):
    """Save chunks to JSON file"""
    print(f"💾 Saving {len(chunks)} chunks to {output_file}...")
    
    chunk_data = []
    for chunk in chunks:
        chunk_data.append({
            'chunk_id': chunk.chunk_id,
            'content': chunk.content,
            'metadata': chunk.metadata,
            'content_length': chunk.content_length,
            'word_count': chunk.word_count
        })
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(chunk_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Chunks saved to {output_file}")

def save_embedding_ready_format(chunks: List[DocumentChunk], output_file: str):
    """Save chunks in format ready for embedding"""
    print(f"🔮 Preparing embedding-ready format...")
    
    embedding_data = []
    for chunk in chunks:
        # Create context-rich text for embedding
        context_parts = []
        
        if chunk.metadata.get('component'):
            context_parts.append(f"Component: {chunk.metadata['component']}")
        
        if chunk.metadata.get('subsection'):
            context_parts.append(f"Section: {chunk.metadata['subsection']}")
        
        content_type = chunk.metadata.get('content_type', 'documentation')
        context_parts.append(f"Type: {content_type}")
        
        # Create embedding text
        embedding_text = "\n".join(context_parts) + "\n\n" + chunk.content
        
        embedding_data.append({
            'id': chunk.chunk_id,
            'text': embedding_text,
            'display_content': chunk.content,
            'metadata': chunk.metadata
        })
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(embedding_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Embedding-ready data saved to {output_file}")

def analyze_chunks(chunks: List[DocumentChunk]):
    """Analyze the chunks and print statistics"""
    print("\n📊 Chunk Analysis:")
    print("=" * 50)
    
    # Basic stats
    total_chunks = len(chunks)
    total_content_length = sum(chunk.content_length for chunk in chunks)
    avg_chunk_size = total_content_length / total_chunks if total_chunks > 0 else 0
    
    print(f"Total chunks: {total_chunks}")
    print(f"Average chunk size: {avg_chunk_size:.0f} characters")
    
    # Component breakdown
    components = {}
    content_types = {}
    languages = {}
    
    for chunk in chunks:
        # Count by component
        component = chunk.metadata.get('component', 'Unknown')
        components[component] = components.get(component, 0) + 1
        
        # Count by content type
        content_type = chunk.metadata.get('content_type', 'Unknown')
        content_types[content_type] = content_types.get(content_type, 0) + 1
        
        # Count by language (for code examples)
        if 'language' in chunk.metadata:
            lang = chunk.metadata['language']
            languages[lang] = languages.get(lang, 0) + 1
    
    print(f"\nTop 10 Components:")
    for component, count in sorted(components.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {component}: {count} chunks")
    
    print(f"\nContent Types:")
    for content_type, count in sorted(content_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {content_type}: {count} chunks")
    
    if languages:
        print(f"\nCode Languages:")
        for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
            print(f"  {lang}: {count} examples")

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Chunk Vuetify documentation for RAG')
    parser.add_argument('input_file', help='Input markdown file')
    parser.add_argument('--output', '-o', default='vuetify_chunks', 
                       help='Output file prefix (default: vuetify_chunks)')
    parser.add_argument('--chunk-size', type=int, default=1200,
                       help='Maximum chunk size (default: 1200)')
    parser.add_argument('--overlap', type=int, default=150,
                       help='Overlap between chunks (default: 150)')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not Path(args.input_file).exists():
        print(f"❌ Error: Input file '{args.input_file}' not found!")
        return
    
    print(f"🚀 Starting Vuetify Documentation Chunker")
    print(f"📖 Input file: {args.input_file}")
    print(f"📏 Chunk size: {args.chunk_size}")
    print(f"🔄 Overlap: {args.overlap}")
    print()
    
    # Read the documentation
    print("📖 Reading documentation file...")
    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            doc_content = f.read()
        print(f"✅ Read {len(doc_content):,} characters from {args.input_file}")
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return
    
    # Create chunker and process
    chunker = VuetifyDocChunker(
        max_chunk_size=args.chunk_size,
        overlap=args.overlap
    )
    
    chunks = chunker.chunk_documentation(doc_content)
    
    if not chunks:
        print("❌ No chunks created!")
        return
    
    # Save outputs
    json_output = f"{args.output}.json"
    embedding_output = f"{args.output}_embedding_ready.json"
    
    save_chunks_json(chunks, json_output)
    save_embedding_ready_format(chunks, embedding_output)
    
    # Analyze results
    analyze_chunks(chunks)
    
    # Print statistics
    print(f"\n🎯 Processing Statistics:")
    print(f"Components found: {chunker.stats['components_found']}")
    print(f"Code examples: {chunker.stats['code_examples']}")
    print(f"API sections: {chunker.stats['api_sections']}")
    print(f"Processing time: {chunker.stats['processing_time']:.2f}s")
    
    print(f"\n✨ Chunking complete!")
    print(f"📁 Files created:")
    print(f"  - {json_output} (raw chunks)")
    print(f"  - {embedding_output} (embedding ready)")

if __name__ == "__main__":
    main()
