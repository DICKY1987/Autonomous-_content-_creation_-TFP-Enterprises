#!/usr/bin/env python3
"""
Advanced Performance Analytics & Optimization Dashboard
Real-time analytics with AI-powered insights and predictive optimization

Features:
- Multi-platform performance tracking
- Predictive analytics and trend forecasting
- Automated optimization recommendations
- ROI and revenue attribution analysis
- Competitive benchmarking
- Real-time alerting system
"""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
from dataclasses import dataclass
import json
import sqlite3
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

@dataclass
class PerformanceMetrics:
    """Core performance metrics structure"""
    timestamp: datetime
    platform: str
    content_id: str
    views: int
    engagement_rate: float
    ctr: float
    revenue: float
    cost: float
    roi: float
    audience_retention: float
    sentiment_score: float

class AdvancedAnalyticsDashboard:
    """
    Comprehensive analytics dashboard for automated content business
    Real-time tracking with predictive insights and optimization recommendations
    """
    
    def __init__(self, db_path: str = "content_analytics.db"):
        self.db_path = db_path
        self.ml_models = {}
        self.performance_thresholds = self._set_performance_thresholds()
        self.competitive_benchmarks = {}
        self._initialize_database()
        
    def _initialize_database(self):
        """Initialize SQLite database for analytics storage"""
        conn = sqlite3.connect(self.db_path)
        
        # Create tables for different data types
        tables = {
            'content_performance': '''
                CREATE TABLE IF NOT EXISTS content_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    platform TEXT,
                    content_id TEXT,
                    content_type TEXT,
                    title TEXT,
                    views INTEGER,
                    likes INTEGER,
                    comments INTEGER,
                    shares INTEGER,
                    engagement_rate REAL,
                    ctr REAL,
                    watch_time REAL,
                    retention_rate REAL,
                    revenue REAL,
                    cost REAL,
                    roi REAL
                )
            ''',
            'audience_analytics': '''
                CREATE TABLE IF NOT EXISTS audience_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    platform TEXT,
                    total_followers INTEGER,
                    new_followers INTEGER,
                    unfollows INTEGER,
                    demographics_data TEXT,
                    engagement_metrics TEXT,
                    top_content_preferences TEXT
                )
            ''',
            'revenue_tracking': '''
                CREATE TABLE IF NOT EXISTS revenue_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    revenue_stream TEXT,
                    amount REAL,
                    source_content_id TEXT,
                    attribution_model TEXT,
                    customer_segment TEXT,
                    conversion_funnel_stage TEXT
                )
            ''',
            'competitive_analysis': '''
                CREATE TABLE IF NOT EXISTS competitive_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    competitor_name TEXT,
                    platform TEXT,
                    followers INTEGER,
                    avg_engagement_rate REAL,
                    content_frequency INTEGER,
                    estimated_revenue REAL,
                    content_themes TEXT
                )
            '''
        }
        
        for table_name, table_sql in tables.items():
            conn.execute(table_sql)
        
        conn.commit()
        conn.close()
    
    def _set_performance_thresholds(self) -> Dict:
        """Set performance thresholds for alerting"""
        return {
            'youtube': {
                'views_24h_min': 1000,
                'ctr_min': 0.08,
                'retention_min': 0.60,
                'engagement_min': 0.05,
                'rpm_min': 2.0
            },
            'tiktok': {
                'views_24h_min': 5000,
                'completion_rate_min': 0.70,
                'engagement_min': 0.08,
                'shares_min': 50
            },
            'instagram': {
                'reach_min': 2000,
                'engagement_min': 0.06,
                'saves_min': 100,
                'profile_visits_min': 200
            }
        }
    
    async def collect_platform_data(self, platforms: List[str]) -> Dict:
        """Collect performance data from all platforms"""
        
        platform_data = {}
        
        for platform in platforms:
            if platform == 'youtube':
                data = await self._collect_youtube_analytics()
            elif platform == 'tiktok':
                data = await self._collect_tiktok_analytics()
            elif platform == 'instagram':
                data = await self._collect_instagram_analytics()
            else:
                continue
                
            platform_data[platform] = data
            
            # Store in database
            await self._store_performance_data(platform, data)
        
        return platform_data
    
    async def _collect_youtube_analytics(self) -> Dict:
        """Collect YouTube analytics data"""
        
        # This would integrate with YouTube Analytics API
        # Simulated data for demonstration
        return {
            'channel_metrics': {
                'subscribers': 125000,
                'total_views': 15500000,
                'watch_time_hours': 95000,
                'estimated_revenue': 8500.00
            },
            'recent_videos': [
                {
                    'video_id': 'abc123',
                    'title': 'AI Secrets That Will Change Your Life',
                    'published': '2024-12-10',
                    'views': 45000,
                    'likes': 3200,
                    'comments': 450,
                    'watch_time': 285000,  # seconds
                    'ctr': 0.12,
                    'retention_rate': 0.68,
                    'revenue': 180.00
                },
                {
                    'video_id': 'def456',
                    'title': 'Why Everyone is Wrong About Money',
                    'published': '2024-12-09',
                    'views': 32000,
                    'likes': 2800,
                    'comments': 380,
                    'watch_time': 195000,
                    'ctr': 0.09,
                    'retention_rate': 0.72,
                    'revenue': 125.00
                }
            ],
            'audience_demographics': {
                'age_groups': {'18-24': 0.25, '25-34': 0.35, '35-44': 0.25, '45+': 0.15},
                'gender': {'male': 0.65, 'female': 0.35},
                'top_countries': ['US', 'UK', 'Canada', 'Australia', 'Germany']
            }
        }
    
    def generate_performance_dashboard(self, timeframe: str = "30_days") -> Dict:
        """Generate comprehensive performance dashboard"""
        
        # Calculate date range
        end_date = datetime.now()
        if timeframe == "7_days":
            start_date = end_date - timedelta(days=7)
        elif timeframe == "30_days":
            start_date = end_date - timedelta(days=30)
        elif timeframe == "90_days":
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=30)
        
        # Fetch performance data
        performance_data = self._fetch_performance_data(start_date, end_date)
        
        # Generate visualizations
        charts = self._create_performance_charts(performance_data)
        
        # Calculate KPIs
        kpis = self._calculate_kpis(performance_data)
        
        # Generate insights
        insights = self._generate_ai_insights(performance_data, kpis)
        
        # Performance alerts
        alerts = self._check_performance_alerts(performance_data)
        
        return {
            'timeframe': timeframe,
            'kpis': kpis,
            'charts': charts,
            'insights': insights,
            'alerts': alerts,
            'recommendations': self._generate_optimization_recommendations(insights, alerts),
            'competitive_analysis': self._generate_competitive_analysis(),
            'forecast': self._generate_performance_forecast(performance_data)
        }
    
    def _calculate_kpis(self, performance_data: Dict) -> Dict:
        """Calculate key performance indicators"""
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(performance_data.get('content_metrics', []))
        
        if df.empty:
            return self._get_default_kpis()
        
        # Calculate primary KPIs
        kpis = {
            'total_views': int(df['views'].sum()),
            'total_revenue': float(df['revenue'].sum()),
            'total_cost': float(df['cost'].sum()),
            'overall_roi': float((df['revenue'].sum() - df['cost'].sum()) / df['cost'].sum() * 100) if df['cost'].sum() > 0 else 0,
            'avg_engagement_rate': float(df['engagement_rate'].mean()),
            'avg_ctr': float(df['ctr'].mean()),
            'avg_retention': float(df['retention_rate'].mean()),
            'content_count': len(df),
            'revenue_per_view': float(df['revenue'].sum() / df['views'].sum()) if df['views'].sum() > 0 else 0,
            'cost_per_view': float(df['cost'].sum() / df['views'].sum()) if df['views'].sum() > 0 else 0
        }
        
        # Calculate growth rates
        if len(df) > 1:
            df['date'] = pd.to_datetime(df['timestamp'])
            df_sorted = df.sort_values('date')
            
            # Split into two halves for growth calculation
            mid_point = len(df_sorted) // 2
            first_half = df_sorted.iloc[:mid_point]
            second_half = df_sorted.iloc[mid_point:]
            
            first_period_views = first_half['views'].sum()
            second_period_views = second_half['views'].sum()
            
            if first_period_views > 0:
                view_growth_rate = ((second_period_views - first_period_views) / first_period_views) * 100
                kpis['view_growth_rate'] = float(view_growth_rate)
            else:
                kpis['view_growth_rate'] = 0.0
            
            # Revenue growth
            first_period_revenue = first_half['revenue'].sum()
            second_period_revenue = second_half['revenue'].sum()
            
            if first_period_revenue > 0:
                revenue_growth_rate = ((second_period_revenue - first_period_revenue) / first_period_revenue) * 100
                kpis['revenue_growth_rate'] = float(revenue_growth_rate)
            else:
                kpis['revenue_growth_rate'] = 0.0
        
        return kpis
    
    def _create_performance_charts(self, performance_data: Dict) -> Dict:
        """Create performance visualization charts"""
        
        charts = {}
        
        # Convert data to DataFrame
        df = pd.DataFrame(performance_data.get('content_metrics', []))
        
        if df.empty:
            return {'error': 'No data available for charts'}
        
        df['date'] = pd.to_datetime(df['timestamp'])
        
        # 1. Views Over Time Chart
        daily_views = df.groupby(df['date'].dt.date)['views'].sum().reset_index()
        
        fig_views = go.Figure()
        fig_views.add_trace(go.Scatter(
            x=daily_views['date'],
            y=daily_views['views'],
            mode='lines+markers',
            name='Daily Views',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8)
        ))
        
        fig_views.update_layout(
            title='Views Over Time',
            xaxis_title='Date',
            yaxis_title='Views',
            hovermode='x unified',
            height=400
        )
        
        charts['views_timeline'] = fig_views.to_html(full_html=False, include_plotlyjs='cdn')
        
        # 2. Revenue vs Cost Analysis
        daily_financials = df.groupby(df['date'].dt.date).agg({
            'revenue': 'sum',
            'cost': 'sum'
        }).reset_index()
        
        fig_financials = go.Figure()
        fig_financials.add_trace(go.Bar(
            x=daily_financials['date'],
            y=daily_financials['revenue'],
            name='Revenue',
            marker_color='green',
            opacity=0.7
        ))
        fig_financials.add_trace(go.Bar(
            x=daily_financials['date'],
            y=daily_financials['cost'],
            name='Cost',
            marker_color='red',
            opacity=0.7
        ))
        
        fig_financials.update_layout(
            title='Revenue vs Cost Analysis',
            xaxis_title='Date',
            yaxis_title='Amount ($)',
            barmode='group',
            height=400
        )
        
        charts['revenue_cost_analysis'] = fig_financials.to_html(full_html=False, include_plotlyjs='cdn')
        
        # 3. Engagement Rate Distribution
        fig_engagement = px.histogram(
            df, 
            x='engagement_rate',
            nbins=20,
            title='Engagement Rate Distribution',
            labels={'engagement_rate': 'Engagement Rate', 'count': 'Number of Videos'}
        )
        fig_engagement.update_layout(height=400)
        
        charts['engagement_distribution'] = fig_engagement.to_html(full_html=False, include_plotlyjs='cdn')
        
        # 4. Platform Performance Comparison
        if 'platform' in df.columns:
            platform_metrics = df.groupby('platform').agg({
                'views': 'sum',
                'revenue': 'sum',
                'engagement_rate': 'mean'
            }).reset_index()
            
            fig_platform = make_subplots(
                rows=1, cols=3,
                subplot_titles=('Total Views', 'Total Revenue', 'Avg Engagement Rate'),
                specs=[[{"type": "bar"}, {"type": "bar"}, {"type": "bar"}]]
            )
            
            fig_platform.add_trace(
                go.Bar(x=platform_metrics['platform'], y=platform_metrics['views'], name='Views'),
                row=1, col=1
            )
            fig_platform.add_trace(
                go.Bar(x=platform_metrics['platform'], y=platform_metrics['revenue'], name='Revenue'),
                row=1, col=2
            )
            fig_platform.add_trace(
                go.Bar(x=platform_metrics['platform'], y=platform_metrics['engagement_rate'], name='Engagement'),
                row=1, col=3
            )
            
            fig_platform.update_layout(
                title_text="Platform Performance Comparison",
                height=400,
                showlegend=False
            )
            
            charts['platform_comparison'] = fig_platform.to_html(full_html=False, include_plotlyjs='cdn')
        
        return charts
    
    def _generate_ai_insights(self, performance_data: Dict, kpis: Dict) -> Dict:
        """Generate AI-powered insights from performance data"""
        
        insights = {
            'performance_summary': self._analyze_overall_performance(kpis),
            'content_insights': self._analyze_content_performance(performance_data),
            'audience_insights': self._analyze_audience_behavior(performance_data),
            'monetization_insights': self._analyze_monetization_performance(performance_data),
            'trend_analysis': self._analyze_trends(performance_data),
            'optimization_opportunities': self._identify_optimization_opportunities(performance_data, kpis)
        }
        
        return insights
    
    def _analyze_overall_performance(self, kpis: Dict) -> Dict:
        """Analyze overall performance trends"""
        
        analysis = {
            'performance_grade': 'B+',  # A, B+, B, C+, C, D
            'key_strengths': [],
            'areas_for_improvement': [],
            'performance_trajectory': 'positive'  # positive, neutral, negative
        }
        
        # Analyze engagement rate
        avg_engagement = kpis.get('avg_engagement_rate', 0)
        if avg_engagement > 0.08:
            analysis['key_strengths'].append('Excellent audience engagement (>8%)')
            analysis['performance_grade'] = 'A'
        elif avg_engagement > 0.06:
            analysis['key_strengths'].append('Good audience engagement (6-8%)')
        elif avg_engagement > 0.04:
            analysis['areas_for_improvement'].append('Engagement rate below optimal (4-6%)')
            analysis['performance_grade'] = 'C+'
        else:
            analysis['areas_for_improvement'].append('Low engagement rate (<4%) - urgent optimization needed')
            analysis['performance_grade'] = 'D'
        
        # Analyze ROI
        roi = kpis.get('overall_roi', 0)
        if roi > 300:
            analysis['key_strengths'].append(f'Outstanding ROI ({roi:.1f}%)')
        elif roi > 200:
            analysis['key_strengths'].append(f'Strong ROI ({roi:.1f}%)')
        elif roi > 100:
            analysis['key_strengths'].append(f'Positive ROI ({roi:.1f}%)')
        elif roi > 0:
            analysis['areas_for_improvement'].append(f'Low ROI ({roi:.1f}%) - optimize costs or revenue')
        else:
            analysis['areas_for_improvement'].append('Negative ROI - immediate action required')
            analysis['performance_grade'] = 'D'
        
        # Growth trajectory
        view_growth = kpis.get('view_growth_rate', 0)
        revenue_growth = kpis.get('revenue_growth_rate', 0)
        
        if view_growth > 20 and revenue_growth > 20:
            analysis['performance_trajectory'] = 'accelerating'
            analysis['key_strengths'].append('Strong growth momentum')
        elif view_growth > 0 and revenue_growth > 0:
            analysis['performance_trajectory'] = 'positive'
        elif view_growth < -10 or revenue_growth < -10:
            analysis['performance_trajectory'] = 'declining'
            analysis['areas_for_improvement'].append('Declining growth trend - strategy review needed')
        
        return analysis
    
    def _analyze_content_performance(self, performance_data: Dict) -> Dict:
        """Analyze content performance patterns"""
        
        df = pd.DataFrame(performance_data.get('content_metrics', []))
        
        if df.empty:
            return {'error': 'No content data available'}
        
        # Find top performing content
        top_content = df.nlargest(5, 'views')[['title', 'views', 'engagement_rate', 'revenue']].to_dict('records')
        
        # Find content patterns
        content_insights = {
            'top_performing_content': top_content,
            'best_performing_topics': self._identify_best_topics(df),
            'optimal_content_length': self._analyze_optimal_length(df),
            'best_posting_times': self._analyze_posting_times(df),
            'content_recommendations': self._generate_content_recommendations(df)
        }
        
        return content_insights
    
    def _identify_optimization_opportunities(self, performance_data: Dict, kpis: Dict) -> List[Dict]:
        """Identify specific optimization opportunities"""
        
        opportunities = []
        
        # Low engagement opportunity
        if kpis.get('avg_engagement_rate', 0) < 0.06:
            opportunities.append({
                'type': 'engagement_optimization',
                'priority': 'high',
                'description': 'Engagement rate below industry average',
                'impact_potential': 'high',
                'recommended_actions': [
                    'Improve video hooks (first 3 seconds)',
                    'Add more interactive elements (polls, questions)',
                    'Optimize thumbnail design for higher CTR',
                    'Create more controversial/discussion-worthy content'
                ],
                'expected_improvement': '30-50% engagement increase'
            })
        
        # Revenue optimization opportunity
        revenue_per_view = kpis.get('revenue_per_view', 0)
        if revenue_per_view < 0.002:  # $2 per 1000 views
            opportunities.append({
                'type': 'monetization_optimization',
                'priority': 'high',
                'description': 'Revenue per view below optimal',
                'impact_potential': 'very_high',
                'recommended_actions': [
                    'Diversify revenue streams (add sponsorships, affiliates)',
                    'Focus on higher CPM niches',
                    'Improve audience quality and retention',
                    'Implement premium content offerings'
                ],
                'expected_improvement': '50-100% revenue increase'
            })
        
        # Content consistency opportunity
        df = pd.DataFrame(performance_data.get('content_metrics', []))
        if not df.empty and len(df) < 20:  # Less than 20 videos in timeframe
            opportunities.append({
                'type': 'content_volume_optimization',
                'priority': 'medium',
                'description': 'Content volume below optimal for algorithm favor',
                'impact_potential': 'medium',
                'recommended_actions': [
                    'Increase posting frequency to 1 video per day minimum',
                    'Implement content batching and automation',
                    'Create evergreen content that can be repurposed',
                    'Develop content templates for faster production'
                ],
                'expected_improvement': '25-40% reach increase'
            })
        
        return opportunities
    
    def generate_competitive_analysis_report(self, competitors: List[str]) -> Dict:
        """Generate comprehensive competitive analysis"""
        
        competitive_analysis = {
            'market_position': self._analyze_market_position(competitors),
            'content_gap_analysis': self._analyze_content_gaps(competitors),
            'performance_benchmarking': self._benchmark_performance(competitors),
            'opportunity_identification': self._identify_competitive_opportunities(competitors),
            'strategic_recommendations': self._generate_competitive_strategy(competitors)
        }
        
        return competitive_analysis
    
    def _analyze_market_position(self, competitors: List[str]) -> Dict:
        """Analyze current market position vs competitors"""
        
        # This would integrate with competitor tracking APIs
        # Simulated analysis for demonstration
        return {
            'market_share_estimate': '2.3%',
            'ranking_in_niche': 15,
            'total_competitors_tracked': 50,
            'growth_rate_vs_market': '+15% above average',
            'unique_value_proposition': [
                'AI-powered content automation',
                'Higher video production quality',
                'More consistent posting schedule'
            ],
            'competitive_advantages': [
                'Advanced automation capabilities',
                'Superior content quality',
                'Better audience engagement rates'
            ],
            'areas_where_competitors_lead': [
                'Total subscriber count',
                'Brand recognition',
                'Sponsorship deals'
            ]
        }
    
    async def generate_automated_report(self, report_type: str = "weekly") -> Dict:
        """Generate automated performance report"""
        
        if report_type == "daily":
            timeframe = "1_day"
        elif report_type == "weekly":
            timeframe = "7_days"
        elif report_type == "monthly":
            timeframe = "30_days"
        else:
            timeframe = "7_days"
        
        # Collect latest data
        platform_data = await self.collect_platform_data(['youtube', 'tiktok', 'instagram'])
        
        # Generate dashboard
        dashboard_data = self.generate_performance_dashboard(timeframe)
        
        # Create executive summary
        executive_summary = self._create_executive_summary(dashboard_data)
        
        # Generate action items
        action_items = self._generate_action_items(dashboard_data)
        
        report = {
            'report_type': report_type,
            'generation_timestamp': datetime.now().isoformat(),
            'executive_summary': executive_summary,
            'key_metrics': dashboard_data['kpis'],
            'performance_insights': dashboard_data['insights'],
            'alerts_and_warnings': dashboard_data['alerts'],
            'optimization_recommendations': dashboard_data['recommendations'],
            'action_items': action_items,
            'next_review_date': (datetime.now() + timedelta(days=7 if report_type == "weekly" else 1)).isoformat()
        }
        
        # Save report
        await self._save_report(report)
        
        return report
    
    def _create_executive_summary(self, dashboard_data: Dict) -> str:
        """Create executive summary of performance"""
        
        kpis = dashboard_data.get('kpis', {})
        insights = dashboard_data.get('insights', {})
        
        # Extract key numbers
        total_views = kpis.get('total_views', 0)
        total_revenue = kpis.get('total_revenue', 0)
        roi = kpis.get('overall_roi', 0)
        view_growth = kpis.get('view_growth_rate', 0)
        
        performance_grade = insights.get('performance_summary', {}).get('performance_grade', 'B')
        
        summary = f"""
        **Performance Summary**
        
        Overall Performance Grade: {performance_grade}
        
        **Key Metrics:**
        • Total Views: {total_views:,}
        • Total Revenue: ${total_revenue:,.2f}
        • ROI: {roi:.1f}%
        • View Growth Rate: {view_growth:+.1f}%
        
        **Key Insights:**
        • {insights.get('performance_summary', {}).get('key_strengths', ['Performance analysis in progress'])[0] if insights.get('performance_summary', {}).get('key_strengths') else 'Performance analysis in progress'}
        • Content engagement remains {('strong' if kpis.get('avg_engagement_rate', 0) > 0.06 else 'moderate' if kpis.get('avg_engagement_rate', 0) > 0.04 else 'below target')}
        • Revenue trajectory is {('positive' if kpis.get('revenue_growth_rate', 0) > 0 else 'negative')}
        
        **Priority Actions:**
        • {dashboard_data.get('recommendations', [{'action': 'Continue current strategy'}])[0].get('action', 'Continue monitoring performance')}
        • Focus on {('scaling successful content patterns' if roi > 200 else 'optimizing underperforming areas')}
        """
        
        return summary.strip()

# Predictive Analytics Engine
class PredictiveAnalyticsEngine:
    """Advanced predictive analytics for content performance"""
    
    def __init__(self):
        self.models = {}
        self.feature_importance = {}
        
    def train_performance_prediction_model(self, historical_data: pd.DataFrame) -> Dict:
        """Train ML model to predict content performance"""
        
        # Feature engineering
        features = self._engineer_features(historical_data)
        
        # Prepare target variables
        targets = {
            'views_24h': historical_data['views_24h'],
            'engagement_rate': historical_data['engagement_rate'],
            'revenue': historical_data['revenue']
        }
        
        # Train models for each target
        model_results = {}
        
        for target_name, target_values in targets.items():
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                features, target_values, test_size=0.2, random_state=42
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train Random Forest model
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            train_score = model.score(X_train_scaled, y_train)
            test_score = model.score(X_test_scaled, y_test)
            
            # Store model and scaler
            self.models[target_name] = {
                'model': model,
                'scaler': scaler,
                'features': list(features.columns)
            }
            
            # Feature importance
            importance = dict(zip(features.columns, model.feature_importances_))
            self.feature_importance[target_name] = importance
            
            model_results[target_name] = {
                'train_r2': train_score,
                'test_r2': test_score,
                'feature_importance': importance
            }
        
        return model_results
    
    def _engineer_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Engineer features for ML models"""
        
        features = pd.DataFrame()
        
        # Title features
        features['title_length'] = data['title'].str.len()
        features['title_word_count'] = data['title'].str.split().str.len()
        features['title_has_number'] = data['title'].str.contains(r'\d').astype(int)
        features['title_has_question'] = data['title'].str.contains(r'\?').astype(int)
        features['title_emotional_words'] = data['title'].str.contains(
            r'amazing|incredible|shocking|secret|hidden|ultimate', case=False
        ).astype(int)
        
        # Temporal features
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        features['hour_of_day'] = data['timestamp'].dt.hour
        features['day_of_week'] = data['timestamp'].dt.dayofweek
        features['month'] = data['timestamp'].dt.month
        features['is_weekend'] = (data['timestamp'].dt.dayofweek >= 5).astype(int)
        
        # Content features
        features['video_duration'] = data.get('duration', 0)
        features['thumbnail_brightness'] = data.get('thumbnail_brightness', 0.5)
        features['has_custom_thumbnail'] = data.get('has_custom_thumbnail', True).astype(int)
        
        # Channel features
        features['subscriber_count'] = data.get('channel_subscribers', 0)
        features['channel_age_days'] = data.get('channel_age_days', 365)
        features['previous_video_performance'] = data.get('avg_recent_views', 0)
        
        return features
    
    def predict_content_performance(self, content_features: Dict) -> Dict:
        """Predict performance for new content"""
        
        predictions = {}
        
        # Convert features to DataFrame
        feature_df = pd.DataFrame([content_features])
        
        for target_name, model_data in self.models.items():
            model = model_data['model']
            scaler = model_data['scaler']
            required_features = model_data['features']
            
            # Ensure all required features are present
            for feature in required_features:
                if feature not in feature_df.columns:
                    feature_df[feature] = 0  # Default value
            
            # Select and scale features
            X = feature_df[required_features]
            X_scaled = scaler.transform(X)
            
            # Make prediction
            prediction = model.predict(X_scaled)[0]
            
            # Calculate confidence interval
            predictions_from_trees = [tree.predict(X_scaled)[0] for tree in model.estimators_]
            std_dev = np.std(predictions_from_trees)
            
            predictions[target_name] = {
                'predicted_value': float(prediction),
                'confidence_interval': {
                    'lower': float(prediction - 1.96 * std_dev),
                    'upper': float(prediction + 1.96 * std_dev)
                },
                'confidence_score': float(min(1.0, 1.0 - (std_dev / abs(prediction)) if prediction != 0 else 0.5))
            }
        
        return predictions

# Real-time Monitoring and Alerting
class RealTimeMonitor:
    """Real-time performance monitoring and alerting system"""
    
    def __init__(self):
        self.alert_rules = {}
        self.notification_channels = {}
        self.monitoring_active = False
        
    def setup_alert_rules(self, rules: Dict) -> None:
        """Setup custom alert rules"""
        self.alert_rules.update(rules)
    
    async def start_monitoring(self, check_interval: int = 300) -> None:
        """Start real-time monitoring with specified interval (seconds)"""
        
        self.monitoring_active = True
        
        while self.monitoring_active:
            try:
                # Check all alert rules
                alerts = await self._check_all_alerts()
                
                # Send notifications for triggered alerts
                if alerts:
                    await self._send_alert_notifications(alerts)
                
                # Wait for next check
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _check_all_alerts(self) -> List[Dict]:
        """Check all configured alert rules"""
        
        triggered_alerts = []
        
        for rule_name, rule_config in self.alert_rules.items():
            try:
                alert_result = await self._evaluate_alert_rule(rule_name, rule_config)
                if alert_result['triggered']:
                    triggered_alerts.append(alert_result)
            except Exception as e:
                print(f"Error checking alert rule {rule_name}: {e}")
        
        return triggered_alerts
    
    async def _evaluate_alert_rule(self, rule_name: str, rule_config: Dict) -> Dict:
        """Evaluate individual alert rule"""
        
        # Get current metrics based on rule type
        if rule_config['type'] == 'performance':
            current_value = await self._get_performance_metric(rule_config['metric'])
        elif rule_config['type'] == 'revenue':
            current_value = await self._get_revenue_metric(rule_config['metric'])
        elif rule_config['type'] == 'engagement':
            current_value = await self._get_engagement_metric(rule_config['metric'])
        else:
            return {'triggered': False}
        
        # Evaluate condition
        threshold = rule_config['threshold']
        condition = rule_config['condition']  # 'above', 'below', 'equals'
        
        triggered = False
        if condition == 'below' and current_value < threshold:
            triggered = True
        elif condition == 'above' and current_value > threshold:
            triggered = True
        elif condition == 'equals' and abs(current_value - threshold) < 0.01:
            triggered = True
        
        return {
            'triggered': triggered,
            'rule_name': rule_name,
            'current_value': current_value,
            'threshold': threshold,
            'condition': condition,
            'severity': rule_config.get('severity', 'medium'),
            'message': rule_config.get('message', f'{rule_name} alert triggered'),
            'timestamp': datetime.now().isoformat()
        }

# Usage Example
async def main():
    """Example usage of the analytics dashboard"""
    
    # Initialize dashboard
    dashboard = AdvancedAnalyticsDashboard()
    
    # Collect data from platforms
    platform_data = await dashboard.collect_platform_data(['youtube', 'tiktok', 'instagram'])
    
    # Generate comprehensive dashboard
    dashboard_report = dashboard.generate_performance_dashboard("30_days")
    
    print("=== PERFORMANCE DASHBOARD ===")
    print(f"Overall ROI: {dashboard_report['kpis']['overall_roi']:.1f}%")
    print(f"Total Views: {dashboard_report['kpis']['total_views']:,}")
    print(f"Total Revenue: ${dashboard_report['kpis']['total_revenue']:,.2f}")
    print(f"Engagement Rate: {dashboard_report['kpis']['avg_engagement_rate']:.2%}")
    
    print("\n=== KEY INSIGHTS ===")
    performance_summary = dashboard_report['insights']['performance_summary']
    print(f"Performance Grade: {performance_summary['performance_grade']}")
    
    if performance_summary['key_strengths']:
        print("\nStrengths:")
        for strength in performance_summary['key_strengths']:
            print(f"• {strength}")
    
    if performance_summary['areas_for_improvement']:
        print("\nAreas for Improvement:")
        for improvement in performance_summary['areas_for_improvement']:
            print(f"• {improvement}")
    
    print("\n=== OPTIMIZATION OPPORTUNITIES ===")
    for opportunity in dashboard_report['insights']['optimization_opportunities']:
        print(f"\n{opportunity['type'].upper()} ({opportunity['priority']} priority)")
        print(f"Description: {opportunity['description']}")
        print(f"Expected Impact: {opportunity['expected_improvement']}")
        print("Recommended Actions:")
        for action in opportunity['recommended_actions']:
            print(f"• {action}")
    
    # Generate automated report
    automated_report = await dashboard.generate_automated_report("weekly")
    print(f"\n=== AUTOMATED WEEKLY REPORT ===")
    print(automated_report['executive_summary'])
    
    # Initialize predictive analytics
    predictor = PredictiveAnalyticsEngine()
    
    # Example prediction for new content
    new_content_features = {
        'title_length': 45,
        'title_word_count': 8,
        'title_has_number': 1,
        'title_has_question': 0,
        'title_emotional_words': 1,
        'hour_of_day': 14,
        'day_of_week': 1,
        'is_weekend': 0,
        'video_duration': 180,
        'subscriber_count': 125000,
        'previous_video_performance': 35000
    }
    
    # Note: In real implementation, you would train the model first with historical data
    print(f"\n=== PREDICTIVE ANALYTICS ===")
    print("Prediction system initialized and ready for training with historical data")

if __name__ == "__main__":
    asyncio.run(main())