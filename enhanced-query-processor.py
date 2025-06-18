#!/usr/bin/env python3
"""
Enhanced Query Processor for Vuetify RAG
Adds intelligent query understanding and multi-stage retrieval
"""

import re
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class QueryType(Enum):
    """Types of queries the system can handle"""
    COMPONENT_USAGE = "component_usage"          # "How to use v-btn?"
    API_REFERENCE = "api_reference"              # "v-btn props"
    CODE_EXAMPLE = "code_example"                # "v-btn example"
    STYLING = "styling"                          # "v-btn colors"
    COMPARISON = "comparison"                    # "v-btn vs v-icon-btn"
    TROUBLESHOOTING = "troubleshooting"          # "v-btn not working"
    BEST_PRACTICES = "best_practices"            # "v-btn accessibility"
    INTEGRATION = "integration"                  # "v-btn with router"

@dataclass
class QueryAnalysis:
    """Results of query analysis"""
    original_query: str
    query_type: QueryType
    components: List[str]
    keywords: List[str]
    intent_confidence: float
    suggested_filters: Dict[str, str]
    enhanced_query: str

class VuetifyQueryProcessor:
    """Advanced query processor for Vuetify documentation"""
    
    def __init__(self):
        # Component patterns
        self.component_patterns = [
            r'\bv-[a-z-]+\b',  # v-btn, v-card, etc.
            r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b'  # DataTable, AppBar, etc.
        ]
        
        # Intent keywords
        self.intent_keywords = {
            QueryType.API_REFERENCE: [
                'props', 'properties', 'attributes', 'api', 'options', 
                'parameters', 'configuration', 'methods', 'events'
            ],
            QueryType.CODE_EXAMPLE: [
                'example', 'sample', 'demo', 'code', 'implementation',
                'tutorial', 'walkthrough', 'snippet'
            ],
            QueryType.STYLING: [
                'style', 'css', 'color', 'theme', 'appearance', 'design',
                'layout', 'spacing', 'margin', 'padding', 'elevation',
                'rounded', 'variant', 'size'
            ],
            QueryType.COMPONENT_USAGE: [
                'how to', 'use', 'create', 'make', 'build', 'setup',
                'configure', 'implement', 'add'
            ],
            QueryType.COMPARISON: [
                'vs', 'versus', 'difference', 'compare', 'comparison',
                'between', 'alternative', 'instead'
            ],
            QueryType.TROUBLESHOOTING: [
                'not working', 'broken', 'error', 'issue', 'problem',
                'fix', 'debug', 'troubleshoot', 'help'
            ],
            QueryType.BEST_PRACTICES: [
                'best practice', 'recommended', 'accessibility', 'a11y',
                'performance', 'optimization', 'should', 'guidelines'
            ],
            QueryType.INTEGRATION: [
                'router', 'vuex', 'pinia', 'typescript', 'nuxt',
                'integration', 'with', 'using'
            ]
        }
        
        # Vuetify-specific keywords
        self.vuetify_keywords = {
            'colors': ['primary', 'secondary', 'accent', 'error', 'info', 
                      'success', 'warning', 'surface'],
            'variants': ['elevated', 'flat', 'tonal', 'outlined', 'text', 'plain'],
            'sizes': ['x-small', 'small', 'default', 'large', 'x-large'],
            'density': ['default', 'comfortable', 'compact'],
            'themes': ['light', 'dark', 'theme'],
            'layout': ['container', 'row', 'col', 'spacer', 'flex'],
            'navigation': ['drawer', 'tabs', 'breadcrumbs', 'stepper'],
            'input': ['validation', 'rules', 'required', 'email'],
            'data': ['table', 'list', 'iterator', 'pagination', 'sorting']
        }
    
    def analyze_query(self, query: str) -> QueryAnalysis:
        """Analyze query to understand intent and extract components"""
        
        # Extract components
        components = self._extract_components(query)
        
        # Determine query type
        query_type, confidence = self._classify_query_type(query)
        
        # Extract keywords
        keywords = self._extract_keywords(query)
        
        # Generate filters
        filters = self._generate_filters(query, components, query_type)
        
        # Enhance query
        enhanced_query = self._enhance_query(query, components, keywords, query_type)
        
        return QueryAnalysis(
            original_query=query,
            query_type=query_type,
            components=components,
            keywords=keywords,
            intent_confidence=confidence,
            suggested_filters=filters,
            enhanced_query=enhanced_query
        )
    
    def _extract_components(self, query: str) -> List[str]:
        """Extract Vuetify component names from query"""
        components = []
        
        for pattern in self.component_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                # Normalize to v-component format
                if not match.lower().startswith('v-'):
                    # Convert CamelCase to kebab-case
                    kebab = re.sub(r'([A-Z])', r'-\1', match).lower().strip('-')
                    match = f"v-{kebab}"
                components.append(match.lower())
        
        return list(set(components))  # Remove duplicates
    
    def _classify_query_type(self, query: str) -> Tuple[QueryType, float]:
        """Classify the type of query"""
        query_lower = query.lower()
        
        # Score each query type
        type_scores = {}
        
        for query_type, keywords in self.intent_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in query_lower:
                    score += 1
            
            # Normalize score
            if keywords:
                type_scores[query_type] = score / len(keywords)
        
        # Find best match
        if type_scores:
            best_type = max(type_scores, key=type_scores.get)
            confidence = type_scores[best_type]
            
            # Minimum confidence threshold
            if confidence > 0.1:
                return best_type, confidence
        
        # Default to component usage
        return QueryType.COMPONENT_USAGE, 0.5
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract relevant Vuetify keywords"""
        query_lower = query.lower()
        found_keywords = []
        
        for category, keywords in self.vuetify_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    found_keywords.append(keyword)
        
        return found_keywords
    
    def _generate_filters(self, query: str, components: List[str], 
                         query_type: QueryType) -> Dict[str, str]:
        """Generate suggested filters for database query"""
        filters = {}
        
        # Component filter
        if components:
            filters['component'] = components[0]  # Use first component
        
        # Content type filter based on query type
        content_type_mapping = {
            QueryType.API_REFERENCE: 'api_reference',
            QueryType.CODE_EXAMPLE: 'code_example',
            QueryType.COMPONENT_USAGE: 'usage_guide',
            QueryType.STYLING: 'documentation'
        }
        
        if query_type in content_type_mapping:
            filters['content_type'] = content_type_mapping[query_type]
        
        return filters
    
    def _enhance_query(self, original_query: str, components: List[str], 
                      keywords: List[str], query_type: QueryType) -> str:
        """Enhance query with additional context"""
        
        # Start with original query
        enhanced_parts = [original_query]
        
        # Add Vuetify context
        enhanced_parts.append("Vuetify Vue.js component library")
        
        # Add component context
        if components:
            enhanced_parts.append(f"components: {' '.join(components)}")
        
        # Add keyword context
        if keywords:
            enhanced_parts.append(f"related: {' '.join(keywords)}")
        
        # Add type-specific context
        type_context = {
            QueryType.API_REFERENCE: "props methods events API documentation",
            QueryType.CODE_EXAMPLE: "code examples implementation tutorial",
            QueryType.STYLING: "CSS styling themes colors appearance",
            QueryType.COMPONENT_USAGE: "usage guide how-to tutorial",
            QueryType.TROUBLESHOOTING: "troubleshooting debugging solutions",
            QueryType.BEST_PRACTICES: "best practices recommendations guidelines"
        }
        
        if query_type in type_context:
            enhanced_parts.append(type_context[query_type])
        
        return " ".join(enhanced_parts)

class EnhancedVuetifyRAG:
    """Enhanced RAG system with query intelligence"""
    
    def __init__(self, base_rag_system):
        """Initialize with existing RAG system"""
        self.base_rag = base_rag_system
        self.query_processor = VuetifyQueryProcessor()
    
    def smart_query(self, user_query: str, n_results: int = 5) -> Dict[str, Any]:
        """Process query with intelligence and multi-stage retrieval"""
        
        # Analyze the query
        analysis = self.query_processor.analyze_query(user_query)
        
        print(f"🧠 Query Analysis:")
        print(f"   Type: {analysis.query_type.value}")
        print(f"   Components: {analysis.components}")
        print(f"   Keywords: {analysis.keywords}")
        print(f"   Confidence: {analysis.intent_confidence:.2f}")
        
        # Multi-stage retrieval
        all_results = []
        
        # Stage 1: Enhanced query search
        print(f"🔍 Stage 1: Enhanced semantic search...")
        enhanced_results = self.base_rag.search(
            analysis.enhanced_query, 
            n_results=n_results,
            component_filter=analysis.suggested_filters.get('component')
        )
        all_results.extend(enhanced_results)
        
        # Stage 2: Component-specific search (if components detected)
        if analysis.components and len(enhanced_results) < n_results:
            print(f"🔍 Stage 2: Component-specific search...")
            for component in analysis.components:
                component_results = self.base_rag.search(
                    user_query,
                    n_results=3,
                    component_filter=component
                )
                all_results.extend(component_results)
        
        # Stage 3: Content-type specific search
        content_type = analysis.suggested_filters.get('content_type')
        if content_type and len(all_results) < n_results:
            print(f"🔍 Stage 3: Content-type search ({content_type})...")
            # This would require extending the base RAG to filter by content_type
            # For now, we'll use the enhanced query
        
        # Remove duplicates and re-rank
        unique_results = self._deduplicate_results(all_results)
        final_results = unique_results[:n_results]
        
        # Generate enhanced response
        response = self._generate_contextual_response(
            user_query, final_results, analysis
        )
        
        return {
            'query': user_query,
            'analysis': {
                'type': analysis.query_type.value,
                'components': analysis.components,
                'keywords': analysis.keywords,
                'confidence': analysis.intent_confidence
            },
            'response': response,
            'sources': [
                {
                    'component': result['metadata'].get('component'),
                    'section': result['metadata'].get('subsection'),
                    'type': result['metadata'].get('content_type'),
                    'similarity': f"{result['similarity_score']:.3f}"
                }
                for result in final_results
            ],
            'search_strategy': 'multi_stage_intelligent'
        }
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate results based on chunk ID"""
        seen_ids = set()
        unique_results = []
        
        # Sort by similarity score first
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        for result in results:
            chunk_id = result['metadata'].get('chunk_id')
            if chunk_id and chunk_id not in seen_ids:
                seen_ids.add(chunk_id)
                unique_results.append(result)
        
        return unique_results
    
    def _generate_contextual_response(self, query: str, results: List[Dict[str, Any]], 
                                    analysis: QueryAnalysis) -> str:
        """Generate response with query-type specific formatting"""
        
        if not self.base_rag.openai_client:
            return self.base_rag._format_simple_response(results)
        
        # Prepare context
        context_parts = []
        for i, result in enumerate(results):
            metadata = result['metadata']
            component = metadata.get('component', 'Unknown')
            section = metadata.get('subsection', 'General')
            content = result['content']
            
            context_parts.append(f"[Source {i+1}: {component} - {section}]\n{content}")
        
        context = "\n\n".join(context_parts)
        
        # Type-specific system prompts
        system_prompts = {
            QueryType.API_REFERENCE: """You are a Vuetify API reference assistant. Focus on:
- Listing available props, methods, and events
- Explaining parameter types and default values
- Providing prop usage examples
- Mentioning related API methods""",
            
            QueryType.CODE_EXAMPLE: """You are a Vuetify code example assistant. Focus on:
- Providing complete, working code examples
- Explaining each part of the code
- Showing both template and script sections
- Including relevant imports and setup""",
            
            QueryType.STYLING: """You are a Vuetify styling assistant. Focus on:
- Explaining CSS classes and utility properties
- Showing color, size, and variant options
- Demonstrating theme customization
- Providing visual styling examples""",
            
            QueryType.TROUBLESHOOTING: """You are a Vuetify troubleshooting assistant. Focus on:
- Identifying common issues and solutions
- Providing step-by-step fixes
- Explaining what might be causing problems
- Offering alternative approaches"""
        }
        
        system_prompt = system_prompts.get(
            analysis.query_type, 
            "You are a helpful Vuetify expert assistant."
        )
        
        # Enhanced user prompt
        user_prompt = f"""Query Type: {analysis.query_type.value}
Components: {', '.join(analysis.components) if analysis.components else 'General'}
Keywords: {', '.join(analysis.keywords) if analysis.keywords else 'None'}

Context from Vuetify Documentation:
{context}

User Question: {query}

Please provide a comprehensive answer based on the query type and documentation context."""
        
        try:
            response = self.base_rag.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"⚠️  OpenAI error: {e}")
            return self.base_rag._format_simple_response(results)

# Usage example
def demo_enhanced_rag():
    """Demo the enhanced RAG system"""
    
    # This assumes you have the base RAG system set up
    from simple_rag_interface import VuetifyRAG
    
    base_rag = VuetifyRAG()
    enhanced_rag = EnhancedVuetifyRAG(base_rag)
    
    # Test queries
    test_queries = [
        "v-btn color props",                    # API Reference
        "v-card elevation example",             # Code Example  
        "v-data-table sorting tutorial",        # Usage Guide
        "custom theme colors styling",          # Styling
        "v-form validation not working",        # Troubleshooting
        "v-text-field accessibility best practices"  # Best Practices
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"🔍 Query: {query}")
        print('='*60)
        
        result = enhanced_rag.smart_query(query)
        
        print(f"\n🤖 Response:")
        print(result['response'])
        
        print(f"\n📊 Analysis:")
        analysis = result['analysis']
        print(f"Type: {analysis['type']}")
        print(f"Components: {analysis['components']}")
        print(f"Confidence: {analysis['confidence']:.2f}")

if __name__ == "__main__":
    demo_enhanced_rag()
