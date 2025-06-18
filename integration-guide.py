#!/usr/bin/env python3
"""
Enhanced RAG Integration Guide
Shows how to integrate the advanced features with your existing system
"""

# Step 1: Install additional dependencies
"""
pip install matplotlib pandas sqlite3
"""

# Step 2: Enhanced RAG with Analytics
from simple_rag_interface import VuetifyRAG
from enhanced_query_processor import EnhancedVuetifyRAG
from rag_analytics import RAGAnalytics, MonitoredRAG

class SuperchargedVuetifyRAG:
    """Complete RAG system with intelligence and monitoring"""
    
    def __init__(self, chroma_db_path: str = "./chromadb_data"):
        """Initialize the complete system"""
        print("🚀 Initializing Supercharged Vuetify RAG...")
        
        # Base RAG system
        self.base_rag = VuetifyRAG(chroma_db_path)
        
        # Enhanced query processing
        self.enhanced_rag = EnhancedVuetifyRAG(self.base_rag)
        
        # Analytics system
        self.analytics = RAGAnalytics("vuetify_rag_analytics.db")
        
        # Monitored version
        self.monitored_rag = MonitoredRAG(self.base_rag, self.analytics)
        
        print("✅ Supercharged RAG system ready!")
    
    def smart_query(self, user_query: str, use_intelligence: bool = True, 
                   monitor: bool = True) -> dict:
        """Execute smart query with optional intelligence and monitoring"""
        
        if use_intelligence:
            # Use enhanced query processing
            print("🧠 Using intelligent query processing...")
            result = self.enhanced_rag.smart_query(user_query)
            
            if monitor:
                # Log the query for analytics
                from datetime import datetime
                from rag_analytics import QueryLog
                
                query_log = QueryLog(
                    timestamp=datetime.now().isoformat(),
                    query=user_query,
                    query_type=result['analysis']['type'],
                    components=result['analysis']['components'],
                    response_time=1.0,  # Would be measured in real implementation
                    num_results=len(result['sources']),
                    similarity_scores=[0.8, 0.7, 0.6]  # Would extract from actual results
                )
                self.analytics.log_query(query_log)
            
        else:
            # Use basic query processing
            if monitor:
                result = self.monitored_rag.query_with_monitoring(user_query)
            else:
                result = self.base_rag.query(user_query)
        
        return result
    
    def get_performance_insights(self):
        """Get performance insights"""
        return self.analytics.get_performance_summary()
    
    def generate_analytics_report(self):
        """Generate analytics report"""
        return self.analytics.generate_report("vuetify_rag_report.html")

# Step 3: Usage Examples
def demo_supercharged_rag():
    """Demo the complete enhanced system"""
    
    # Initialize the supercharged system
    rag = SuperchargedVuetifyRAG()
    
    # Test queries with different complexity levels
    test_scenarios = [
        {
            "name": "🔧 API Reference Query",
            "query": "v-btn color and size props",
            "expected_type": "api_reference"
        },
        {
            "name": "💻 Code Example Query", 
            "query": "v-card with elevation example",
            "expected_type": "code_example"
        },
        {
            "name": "🎨 Styling Query",
            "query": "custom theme colors and variants",
            "expected_type": "styling"
        },
        {
            "name": "❓ Troubleshooting Query",
            "query": "v-data-table sorting not working",
            "expected_type": "troubleshooting"
        },
        {
            "name": "📖 Usage Guide Query",
            "query": "how to create responsive navigation",
            "expected_type": "component_usage"
        }
    ]
    
    print("🧪 Testing Enhanced RAG Features")
    print("=" * 60)
    
    for scenario in test_scenarios:
        print(f"\n{scenario['name']}")
        print(f"Query: {scenario['query']}")
        print("-" * 40)
        
        # Execute smart query
        result = rag.smart_query(scenario['query'])
        
        # Check if query type was detected correctly
        detected_type = result.get('analysis', {}).get('type', 'unknown')
        components = result.get('analysis', {}).get('components', [])
        
        print(f"✅ Detected Type: {detected_type}")
        print(f"🧩 Components: {components}")
        print(f"📚 Sources: {len(result.get('sources', []))} chunks")
        
        # Show response preview
        response = result.get('response', '')
        preview = response[:200] + "..." if len(response) > 200 else response
        print(f"🤖 Response Preview: {preview}")
        
        print()
    
    # Show analytics
    print("\n📊 Performance Analytics")
    print("=" * 60)
    
    insights = rag.get_performance_insights()
    print(f"Total Queries: {insights['total_queries']}")
    print(f"Avg Response Time: {insights['avg_response_time']}s")
    print(f"Avg Similarity: {insights['avg_similarity']:.3f}")
    
    if insights['top_components']:
        print(f"\nTop Components:")
        for comp in insights['top_components'][:5]:
            print(f"  {comp['component']}: {comp['queries']} queries")
    
    # Generate report
    report_file = rag.generate_analytics_report()
    print(f"\n📄 Analytics Report: {report_file}")

# Step 4: Command Line Interface
import argparse

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description='Supercharged Vuetify RAG System')
    parser.add_argument('command', choices=['query', 'analytics', 'demo'], 
                       help='Command to execute')
    parser.add_argument('--query', '-q', help='Query text for query command')
    parser.add_argument('--intelligence', action='store_true', 
                       help='Use enhanced intelligence')
    parser.add_argument('--monitor', action='store_true', 
                       help='Enable monitoring')
    
    args = parser.parse_args()
    
    if args.command == 'demo':
        demo_supercharged_rag()
        
    elif args.command == 'query':
        if not args.query:
            print("❌ Query text required with --query")
            return
        
        rag = SuperchargedVuetifyRAG()
        result = rag.smart_query(
            args.query, 
            use_intelligence=args.intelligence,
            monitor=args.monitor
        )
        
        print(f"Query: {args.query}")
        print(f"Response: {result['response']}")
        if 'analysis' in result:
            print(f"Analysis: {result['analysis']}")
        
    elif args.command == 'analytics':
        rag = SuperchargedVuetifyRAG()
        
        # Show insights
        insights = rag.get_performance_insights()
        print("📊 Performance Insights:")
        print(f"Total Queries: {insights['total_queries']}")
        print(f"Avg Response Time: {insights['avg_response_time']}s")
        
        # Generate report
        report = rag.generate_analytics_report()
        print(f"📄 Report Generated: {report}")

# Step 5: Interactive Mode Enhancement
def interactive_enhanced_mode():
    """Enhanced interactive mode with all features"""
    
    rag = SuperchargedVuetifyRAG()
    
    print("\n🎯 Enhanced Vuetify Documentation Assistant")
    print("=" * 50)
    print("🧠 Intelligence: ON")
    print("📊 Monitoring: ON") 
    print("💡 Type 'help' for commands, 'quit' to exit")
    print()
    
    while True:
        try:
            user_input = input("💬 Your question: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                # Show session summary
                insights = rag.get_performance_insights()
                print(f"\n📊 Session Summary:")
                print(f"Queries processed: {insights['total_queries']}")
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'help':
                print("\n📖 Enhanced Commands:")
                print("- Ask any Vuetify question")
                print("- 'analytics' - Show performance stats")
                print("- 'report' - Generate analytics report")
                print("- 'trending' - Show popular queries")
                print("- 'components' - List top components")
                print()
                continue
            
            if user_input.lower() == 'analytics':
                insights = rag.get_performance_insights()
                print(f"\n📊 Analytics:")
                print(f"Total Queries: {insights['total_queries']}")
                print(f"Avg Response Time: {insights['avg_response_time']}s")
                print(f"Avg Similarity: {insights['avg_similarity']:.3f}")
                continue
            
            if user_input.lower() == 'report':
                report = rag.generate_analytics_report()
                print(f"📄 Analytics report generated: {report}")
                continue
            
            if user_input.lower() == 'trending':
                trending = rag.analytics.get_trending_queries(5)
                print(f"\n🔥 Trending Queries:")
                for i, query in enumerate(trending, 1):
                    print(f"{i}. {query['query']} ({query['frequency']} times)")
                continue
            
            if user_input.lower() == 'components':
                insights = rag.get_performance_insights()
                print(f"\n🧩 Top Components:")
                for comp in insights['top_components'][:10]:
                    print(f"  {comp['component']}: {comp['queries']} queries")
                continue
            
            if not user_input:
                continue
            
            # Process the query
            result = rag.smart_query(user_input)
            
            # Display enhanced results
            print(f"\n🤖 Response:")
            print("-" * 40)
            print(result['response'])
            
            if 'analysis' in result:
                analysis = result['analysis']
                print(f"\n🧠 Query Analysis:")
                print(f"Type: {analysis['type']}")
                if analysis['components']:
                    print(f"Components: {', '.join(analysis['components'])}")
                print(f"Confidence: {analysis['confidence']:.2f}")
            
            print(f"\n📚 Sources ({len(result['sources'])}):")
            for i, source in enumerate(result['sources'][:3], 1):
                print(f"  {i}. {source['component']} - {source['section']} "
                      f"({source['similarity']})")
            
            print("\n" + "="*50)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Choose mode based on arguments
    import sys
    
    if len(sys.argv) > 1:
        main()  # CLI mode
    else:
        interactive_enhanced_mode()  # Interactive mode
