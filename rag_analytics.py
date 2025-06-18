#!/usr/bin/env python3
"""
RAG Performance Analytics and Monitoring
Track query patterns, performance metrics, and system health
"""

import json
import time
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import pandas as pd

@dataclass
class QueryLog:
    """Log entry for a query"""
    timestamp: str
    query: str
    query_type: str
    components: List[str]
    response_time: float
    num_results: int
    similarity_scores: List[float]
    user_feedback: Optional[str] = None
    session_id: Optional[str] = None

class RAGAnalytics:
    """Analytics system for RAG performance monitoring"""
    
    def __init__(self, db_path: str = "rag_analytics.db"):
        """Initialize analytics database"""
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for analytics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS query_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                query TEXT NOT NULL,
                query_type TEXT,
                components TEXT,  -- JSON array
                response_time REAL,
                num_results INTEGER,
                avg_similarity REAL,
                user_feedback TEXT,
                session_id TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS component_stats (
                component TEXT PRIMARY KEY,
                query_count INTEGER DEFAULT 0,
                avg_response_time REAL DEFAULT 0,
                avg_similarity REAL DEFAULT 0,
                last_queried TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                date TEXT PRIMARY KEY,
                total_queries INTEGER DEFAULT 0,
                avg_response_time REAL DEFAULT 0,
                avg_similarity REAL DEFAULT 0,
                unique_components INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"📊 Analytics database initialized: {self.db_path}")
    
    def log_query(self, query_log: QueryLog):
        """Log a query with its performance metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate average similarity
        avg_similarity = sum(query_log.similarity_scores) / len(query_log.similarity_scores) if query_log.similarity_scores else 0
        
        # Insert query log
        cursor.execute('''
            INSERT INTO query_logs 
            (timestamp, query, query_type, components, response_time, num_results, avg_similarity, user_feedback, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            query_log.timestamp,
            query_log.query,
            query_log.query_type,
            json.dumps(query_log.components),
            query_log.response_time,
            query_log.num_results,
            avg_similarity,
            query_log.user_feedback,
            query_log.session_id
        ))
        
        # Update component stats
        for component in query_log.components:
            cursor.execute('''
                INSERT OR REPLACE INTO component_stats 
                (component, query_count, avg_response_time, avg_similarity, last_queried)
                VALUES (
                    ?, 
                    COALESCE((SELECT query_count FROM component_stats WHERE component = ?), 0) + 1,
                    (COALESCE((SELECT avg_response_time FROM component_stats WHERE component = ?) * 
                             (SELECT query_count FROM component_stats WHERE component = ?), 0) + ?) / 
                    (COALESCE((SELECT query_count FROM component_stats WHERE component = ?), 0) + 1),
                    (COALESCE((SELECT avg_similarity FROM component_stats WHERE component = ?) * 
                             (SELECT query_count FROM component_stats WHERE component = ?), 0) + ?) / 
                    (COALESCE((SELECT query_count FROM component_stats WHERE component = ?), 0) + 1),
                    ?
                )
            ''', (component, component, component, component, query_log.response_time, 
                  component, component, component, avg_similarity, component, query_log.timestamp))
        
        # Update daily stats
        date = query_log.timestamp[:10]  # Extract date (YYYY-MM-DD)
        cursor.execute('''
            INSERT OR REPLACE INTO daily_stats 
            (date, total_queries, avg_response_time, avg_similarity, unique_components)
            VALUES (
                ?,
                COALESCE((SELECT total_queries FROM daily_stats WHERE date = ?), 0) + 1,
                (COALESCE((SELECT avg_response_time FROM daily_stats WHERE date = ?) * 
                         (SELECT total_queries FROM daily_stats WHERE date = ?), 0) + ?) / 
                (COALESCE((SELECT total_queries FROM daily_stats WHERE date = ?), 0) + 1),
                (COALESCE((SELECT avg_similarity FROM daily_stats WHERE date = ?) * 
                         (SELECT total_queries FROM daily_stats WHERE date = ?), 0) + ?) / 
                (COALESCE((SELECT total_queries FROM daily_stats WHERE date = ?), 0) + 1),
                (SELECT COUNT(DISTINCT component) FROM (
                    SELECT json_each.value as component 
                    FROM query_logs, json_each(query_logs.components) 
                    WHERE date(timestamp) = ?
                ))
            )
        ''', (date, date, date, date, query_log.response_time, date, 
              date, date, avg_similarity, date, date))
        
        conn.commit()
        conn.close()
    
    def get_performance_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get performance summary for the last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Total queries
        cursor.execute('''
            SELECT COUNT(*) FROM query_logs 
            WHERE timestamp >= ?
        ''', (start_date.isoformat(),))
        total_queries = cursor.fetchone()[0]
        
        # Average response time
        cursor.execute('''
            SELECT AVG(response_time) FROM query_logs 
            WHERE timestamp >= ?
        ''', (start_date.isoformat(),))
        avg_response_time = cursor.fetchone()[0] or 0
        
        # Average similarity
        cursor.execute('''
            SELECT AVG(avg_similarity) FROM query_logs 
            WHERE timestamp >= ?
        ''', (start_date.isoformat(),))
        avg_similarity = cursor.fetchone()[0] or 0
        
        # Top components
        cursor.execute('''
            SELECT component, query_count, avg_response_time, avg_similarity 
            FROM component_stats 
            ORDER BY query_count DESC 
            LIMIT 10
        ''')
        top_components = [
            {
                'component': row[0],
                'queries': row[1],
                'avg_response_time': row[2],
                'avg_similarity': row[3]
            }
            for row in cursor.fetchall()
        ]
        
        # Query types distribution
        cursor.execute('''
            SELECT query_type, COUNT(*) 
            FROM query_logs 
            WHERE timestamp >= ?
            GROUP BY query_type 
            ORDER BY COUNT(*) DESC
        ''', (start_date.isoformat(),))
        query_types = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'period': f"Last {days} days",
            'total_queries': total_queries,
            'avg_response_time': round(avg_response_time, 3),
            'avg_similarity': round(avg_similarity, 3),
            'top_components': top_components,
            'query_types': query_types
        }
    
    def get_trending_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending/popular queries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT query, COUNT(*) as frequency,
                   AVG(response_time) as avg_response_time,
                   AVG(avg_similarity) as avg_similarity
            FROM query_logs 
            WHERE timestamp >= datetime('now', '-7 days')
            GROUP BY LOWER(query)
            ORDER BY frequency DESC, avg_similarity DESC
            LIMIT ?
        ''', (limit,))
        
        trending = [
            {
                'query': row[0],
                'frequency': row[1],
                'avg_response_time': round(row[2], 3),
                'avg_similarity': round(row[3], 3)
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        return trending
    
    def generate_report(self, output_file: str = "rag_analytics_report.html"):
        """Generate comprehensive analytics report"""
        
        # Get data
        summary = self.get_performance_summary(30)  # Last 30 days
        trending = self.get_trending_queries(15)
        
        # Generate HTML report
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Vuetify RAG Analytics Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #1976D2; color: white; padding: 20px; border-radius: 8px; }}
                .metric {{ background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .component {{ background: #e3f2fd; padding: 10px; margin: 5px 0; border-radius: 3px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .chart {{ margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎯 Vuetify RAG Analytics Report</h1>
                <p>Performance insights for your documentation RAG system</p>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <h2>📊 Performance Summary ({summary['period']})</h2>
            <div class="metric">
                <strong>Total Queries:</strong> {summary['total_queries']}
            </div>
            <div class="metric">
                <strong>Average Response Time:</strong> {summary['avg_response_time']}s
            </div>
            <div class="metric">
                <strong>Average Similarity Score:</strong> {summary['avg_similarity']:.3f}
            </div>
            
            <h2>🏆 Top Components</h2>
            <table>
                <tr>
                    <th>Component</th>
                    <th>Queries</th>
                    <th>Avg Response Time</th>
                    <th>Avg Similarity</th>
                </tr>
        """
        
        for comp in summary['top_components']:
            html_content += f"""
                <tr>
                    <td>{comp['component']}</td>
                    <td>{comp['queries']}</td>
                    <td>{comp['avg_response_time']:.3f}s</td>
                    <td>{comp['avg_similarity']:.3f}</td>
                </tr>
            """
        
        html_content += """
            </table>
            
            <h2>🔥 Trending Queries</h2>
            <table>
                <tr>
                    <th>Query</th>
                    <th>Frequency</th>
                    <th>Avg Response Time</th>
                    <th>Avg Similarity</th>
                </tr>
        """
        
        for query in trending:
            html_content += f"""
                <tr>
                    <td>{query['query']}</td>
                    <td>{query['frequency']}</td>
                    <td>{query['avg_response_time']}s</td>
                    <td>{query['avg_similarity']:.3f}</td>
                </tr>
            """
        
        html_content += """
            </table>
            
            <h2>📈 Query Type Distribution</h2>
            <table>
                <tr>
                    <th>Query Type</th>
                    <th>Count</th>
                    <th>Percentage</th>
                </tr>
        """
        
        total_typed_queries = sum(summary['query_types'].values())
        for query_type, count in summary['query_types'].items():
            percentage = (count / total_typed_queries * 100) if total_typed_queries > 0 else 0
            html_content += f"""
                <tr>
                    <td>{query_type}</td>
                    <td>{count}</td>
                    <td>{percentage:.1f}%</td>
                </tr>
            """
        
        html_content += """
            </table>
        </body>
        </html>
        """
        
        # Save report
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"📄 Analytics report generated: {output_file}")
        return output_file

class MonitoredRAG:
    """RAG system with built-in analytics monitoring"""
    
    def __init__(self, base_rag_system, analytics: RAGAnalytics):
        """Initialize with base RAG and analytics"""
        self.base_rag = base_rag_system
        self.analytics = analytics
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def query_with_monitoring(self, user_query: str, **kwargs) -> Dict[str, Any]:
        """Execute query with full monitoring"""
        start_time = time.time()
        
        # Execute the query
        try:
            result = self.base_rag.query(user_query, **kwargs)
            
            # Extract components from query (simplified)
            components = []
            query_lower = user_query.lower()
            if 'v-' in query_lower:
                import re
                components = re.findall(r'v-[a-z-]+', query_lower)
            
            # Calculate metrics
            response_time = time.time() - start_time
            similarity_scores = []
            
            if 'sources' in result:
                for source in result['sources']:
                    if 'similarity' in source:
                        try:
                            score = float(source['similarity'])
                            similarity_scores.append(score)
                        except:
                            pass
            
            # Log the query
            query_log = QueryLog(
                timestamp=datetime.now().isoformat(),
                query=user_query,
                query_type='general',  # This would come from enhanced processor
                components=components,
                response_time=response_time,
                num_results=len(result.get('sources', [])),
                similarity_scores=similarity_scores,
                session_id=self.session_id
            )
            
            self.analytics.log_query(query_log)
            
            # Add monitoring info to result
            result['monitoring'] = {
                'response_time': response_time,
                'similarity_scores': similarity_scores,
                'session_id': self.session_id
            }
            
            return result
            
        except Exception as e:
            # Log failed queries too
            error_log = QueryLog(
                timestamp=datetime.now().isoformat(),
                query=user_query,
                query_type='error',
                components=[],
                response_time=time.time() - start_time,
                num_results=0,
                similarity_scores=[],
                session_id=self.session_id
            )
            
            self.analytics.log_query(error_log)
            raise e
    
    def add_feedback(self, query: str, feedback: str):
        """Add user feedback for a query"""
        # This would update the most recent query log with feedback
        # Implementation depends on how you want to handle feedback
        print(f"📝 Feedback logged: {feedback} for query: {query}")

def demo_analytics():
    """Demo the analytics system"""
    
    # Initialize analytics
    analytics = RAGAnalytics("demo_analytics.db")
    
    # Simulate some query logs
    import random
    
    components = ['v-btn', 'v-card', 'v-text-field', 'v-data-table', 'v-form']
    query_types = ['api_reference', 'code_example', 'styling', 'component_usage']
    
    print("📊 Simulating query logs...")
    
    for i in range(50):
        # Simulate random query
        component = random.choice(components)
        query_type = random.choice(query_types)
        
        query_log = QueryLog(
            timestamp=(datetime.now() - timedelta(days=random.randint(0, 7))).isoformat(),
            query=f"How to use {component} with custom styling?",
            query_type=query_type,
            components=[component],
            response_time=random.uniform(0.2, 2.0),
            num_results=random.randint(3, 8),
            similarity_scores=[random.uniform(0.6, 0.95) for _ in range(3)]
        )
        
        analytics.log_query(query_log)
    
    # Generate reports
    print("\n📊 Performance Summary:")
    summary = analytics.get_performance_summary()
    
    print(f"Total Queries: {summary['total_queries']}")
    print(f"Avg Response Time: {summary['avg_response_time']}s")
    print(f"Avg Similarity: {summary['avg_similarity']:.3f}")
    
    print(f"\nTop Components:")
    for comp in summary['top_components'][:5]:
        print(f"  {comp['component']}: {comp['queries']} queries")
    
    # Generate HTML report
    report_file = analytics.generate_report("demo_analytics_report.html")
    print(f"\n📄 Full report: {report_file}")

if __name__ == "__main__":
    demo_analytics()
