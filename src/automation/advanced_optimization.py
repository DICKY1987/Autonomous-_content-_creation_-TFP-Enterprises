#!/usr/bin/env python3
"""
Advanced Optimization & A/B Testing System
Intelligent content optimization and performance learning
"""

import asyncio
import json
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import logging
import hashlib
from enum import Enum
import random
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import pickle

logger = logging.getLogger(__name__)

class OptimizationStrategy(Enum):
    ENGAGEMENT_FOCUSED = "engagement_focused"
    REACH_FOCUSED = "reach_focused"
    REVENUE_FOCUSED = "revenue_focused"
    VIRAL_FOCUSED = "viral_focused"

@dataclass
class ContentVariation:
    """A variation of content for A/B testing"""
    variation_id: str
    content_id: str
    platform: str
    variation_type: str  # title, thumbnail, timing, hashtags, description
    original_value: Any
    test_value: Any
    test_percentage: float
    created_at: datetime
    performance_data: Dict = None

@dataclass
class PerformanceMetrics:
    """Standardized performance metrics across platforms"""
    views: int = 0
    engagement_rate: float = 0.0
    shares: int = 0
    comments: int = 0
    likes: int = 0
    saves: int = 0
    click_through_rate: float = 0.0
    watch_time_seconds: float = 0.0
    completion_rate: float = 0.0
    revenue: float = 0.0
    reach: int = 0
    impressions: int = 0
    timestamp: datetime = None

@dataclass
class OptimizationInsight:
    """Actionable optimization insight"""
    insight_type: str
    platform: str
    description: str
    confidence_score: float
    impact_estimate: float
    action_required: str
    data_source: str
    created_at: datetime

class ContentVariationGenerator:
    """Generates content variations for A/B testing"""
    
    def __init__(self):
        self.title_variations = {
            'question_hook': [
                "Did you know {fact}?",
                "Have you ever wondered {fact}?", 
                "What if I told you {fact}?",
                "Can you believe {fact}?"
            ],
            'number_hook': [
                "5 Amazing Facts About {topic}",
                "3 Shocking Truths About {topic}",
                "7 Mind-Blowing {topic} Facts"
            ],
            'emotional_hook': [
                "This {topic} fact will blow your mind!",
                "You won't believe this {topic} discovery!",
                "Prepare to be amazed by {topic}!"
            ]
        }
        
        self.thumbnail_strategies = {
            'text_overlay': {
                'position': ['top', 'center', 'bottom'],
                'color': ['red', 'yellow', 'white'],
                'size': ['large', 'medium', 'small']
            },
            'emotion_face': {
                'expression': ['shocked', 'excited', 'curious', 'amazed'],
                'position': ['left', 'right', 'center']
            },
            'visual_elements': {
                'arrows': True,
                'circles': True,
                'zoom_effect': True,
                'contrast_boost': True
            }
        }
    
    def generate_title_variations(self, original_title: str, topic: str, fact: str) -> List[str]:
        """Generate title variations for A/B testing"""
        
        variations = []
        
        # Generate variations from templates
        for category, templates in self.title_variations.items():
            for template in templates:
                variation = template.format(topic=topic, fact=fact)
                if variation != original_title and len(variation) <= 100:
                    variations.append(variation)
        
        # Add emoji variations
        emoji_sets = [
            " 🤯", " 😱", " 🔥", " ⚡", " 🚀", " 💎", " 🎯", " 💡"
        ]
        
        for emoji in emoji_sets:
            emoji_variation = (original_title + emoji)[:100]
            if emoji_variation not in variations:
                variations.append(emoji_variation)
        
        return variations[:5]  # Return top 5 variations
    
    def generate_hashtag_variations(self, original_hashtags: List[str], platform: str) -> List[List[str]]:
        """Generate hashtag variations based on platform trends"""
        
        platform_trending = {
            'tiktok': [
                '#fyp', '#viral', '#trending', '#foryou', '#xyzbca',
                '#learnontiktok', '#mindblown', '#facts', '#educational',
                '#science', '#technology', '#amazing', '#wow'
            ],
            'youtube': [
                '#Shorts', '#Education', '#Facts', '#Science', '#Technology',
                '#Learning', '#Amazing', '#Incredible', '#MindBlowing', '#Viral'
            ],
            'facebook': [
                '#Amazing', '#Facts', '#Science', '#Technology', '#Educational',
                '#MindBlowing', '#Incredible', '#Learning', '#Knowledge', '#Viral'
            ]
        }
        
        trending_tags = platform_trending.get(platform, [])
        variations = []
        
        # Variation 1: Original + trending
        var1 = original_hashtags[:] + random.sample(trending_tags, min(3, len(trending_tags)))
        variations.append(var1)
        
        # Variation 2: Replace some original with trending
        var2 = original_hashtags[:-2] + random.sample(trending_tags, 4)
        variations.append(var2)
        
        # Variation 3: Trending-heavy
        var3 = original_hashtags[:2] + random.sample(trending_tags, 6)
        variations.append(var3)
        
        return variations
    
    def generate_timing_variations(self, original_time: datetime, platform: str) -> List[datetime]:
        """Generate timing variations for posting"""
        
        platform_optimal_hours = {
            'youtube': [14, 18, 20],
            'tiktok': [6, 10, 19, 21],
            'facebook': [13, 15, 18]
        }
        
        optimal_hours = platform_optimal_hours.get(platform, [14, 18, 20])
        variations = []
        
        for hour in optimal_hours:
            new_time = original_time.replace(hour=hour, minute=0, second=0)
            if new_time != original_time:
                variations.append(new_time)
        
        return variations

class ABTestManager:
    """Manages A/B testing experiments"""
    
    def __init__(self, test_data_path: str = "ab_test_data.json"):
        self.test_data_path = Path(test_data_path)
        self.active_tests: Dict[str, ContentVariation] = {}
        self.completed_tests: List[ContentVariation] = []
        self.variation_generator = ContentVariationGenerator()
        self.load_test_data()
    
    def load_test_data(self):
        """Load existing test data"""
        
        if self.test_data_path.exists():
            try:
                with open(self.test_data_path, 'r') as f:
                    data = json.load(f)
                
                # Load active tests
                for test_data in data.get('active_tests', []):
                    test_data['created_at'] = datetime.fromisoformat(test_data['created_at'])
                    variation = ContentVariation(**test_data)
                    self.active_tests[variation.variation_id] = variation
                
                # Load completed tests
                for test_data in data.get('completed_tests', []):
                    test_data['created_at'] = datetime.fromisoformat(test_data['created_at'])
                    variation = ContentVariation(**test_data)
                    self.completed_tests.append(variation)
                
                logger.info(f"Loaded {len(self.active_tests)} active tests and {len(self.completed_tests)} completed tests")
                
            except Exception as e:
                logger.error(f"Error loading test data: {str(e)}")
    
    def save_test_data(self):
        """Save test data to file"""
        
        data = {
            'active_tests': [],
            'completed_tests': []
        }
        
        # Save active tests
        for variation in self.active_tests.values():
            test_dict = asdict(variation)
            test_dict['created_at'] = variation.created_at.isoformat()
            data['active_tests'].append(test_dict)
        
        # Save completed tests
        for variation in self.completed_tests:
            test_dict = asdict(variation)
            test_dict['created_at'] = variation.created_at.isoformat()
            data['completed_tests'].append(test_dict)
        
        try:
            with open(self.test_data_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving test data: {str(e)}")
    
    def create_test_variations(self, content_data: Dict, platform: str, test_percentage: float = 0.2) -> List[ContentVariation]:
        """Create A/B test variations for content"""
        
        variations = []
        content_id = content_data.get('content_id', 'unknown')
        
        # Title variations
        if 'title' in content_data:
            title_variations = self.variation_generator.generate_title_variations(
                content_data['title'],
                content_data.get('topic', ''),
                content_data.get('core_message', '')
            )
            
            for i, title_var in enumerate(title_variations[:2]):  # Test top 2 variations
                variation = ContentVariation(
                    variation_id=f"{content_id}_{platform}_title_{i}",
                    content_id=content_id,
                    platform=platform,
                    variation_type='title',
                    original_value=content_data['title'],
                    test_value=title_var,
                    test_percentage=test_percentage,
                    created_at=datetime.now()
                )
                variations.append(variation)
        
        # Hashtag variations
        if 'hashtags' in content_data:
            hashtag_variations = self.variation_generator.generate_hashtag_variations(
                content_data['hashtags'], platform
            )
            
            for i, hashtag_var in enumerate(hashtag_variations[:2]):
                variation = ContentVariation(
                    variation_id=f"{content_id}_{platform}_hashtags_{i}",
                    content_id=content_id,
                    platform=platform,
                    variation_type='hashtags',
                    original_value=content_data['hashtags'],
                    test_value=hashtag_var,
                    test_percentage=test_percentage,
                    created_at=datetime.now()
                )
                variations.append(variation)
        
        # Timing variations
        if 'upload_time' in content_data:
            timing_variations = self.variation_generator.generate_timing_variations(
                content_data['upload_time'], platform
            )
            
            for i, timing_var in enumerate(timing_variations[:1]):  # Test 1 timing variation
                variation = ContentVariation(
                    variation_id=f"{content_id}_{platform}_timing_{i}",
                    content_id=content_id,
                    platform=platform,
                    variation_type='timing',
                    original_value=content_data['upload_time'],
                    test_value=timing_var,
                    test_percentage=test_percentage,
                    created_at=datetime.now()
                )
                variations.append(variation)
        
        # Store active tests
        for variation in variations:
            self.active_tests[variation.variation_id] = variation
        
        self.save_test_data()
        return variations
    
    def should_use_variation(self, variation_id: str) -> bool:
        """Determine if a variation should be used based on test percentage"""
        
        if variation_id not in self.active_tests:
            return False
        
        variation = self.active_tests[variation_id]
        return random.random() < variation.test_percentage
    
    def record_performance(self, variation_id: str, metrics: PerformanceMetrics):
        """Record performance data for a variation"""
        
        if variation_id in self.active_tests:
            variation = self.active_tests[variation_id]
            variation.performance_data = asdict(metrics)
            self.save_test_data()
    
    def analyze_test_results(self, min_sample_size: int = 100) -> List[Dict]:
        """Analyze A/B test results and determine winners"""
        
        results = []
        
        # Group variations by content and type
        test_groups = {}
        for variation in self.active_tests.values():
            key = f"{variation.content_id}_{variation.platform}_{variation.variation_type}"
            if key not in test_groups:
                test_groups[key] = []
            test_groups[key].append(variation)
        
        for group_key, variations in test_groups.items():
            if len(variations) < 2:
                continue  # Need at least 2 variations to compare
            
            # Calculate performance for each variation
            performance_scores = []
            for variation in variations:
                if variation.performance_data:
                    # Calculate composite score based on multiple metrics
                    score = self._calculate_performance_score(variation.performance_data, variation.platform)
                    performance_scores.append((variation, score))
            
            if len(performance_scores) >= 2:
                # Find winner
                winner = max(performance_scores, key=lambda x: x[1])
                
                result = {
                    'group': group_key,
                    'winner': winner[0].variation_id,
                    'winner_score': winner[1],
                    'improvement': self._calculate_improvement(performance_scores),
                    'confidence': self._calculate_confidence(performance_scores),
                    'recommendation': self._generate_recommendation(winner[0])
                }
                results.append(result)
        
        return results
    
    def _calculate_performance_score(self, metrics: Dict, platform: str) -> float:
        """Calculate composite performance score"""
        
        # Platform-specific weights
        weights = {
            'youtube': {
                'engagement_rate': 0.3,
                'watch_time_seconds': 0.25,
                'completion_rate': 0.2,
                'views': 0.15,
                'revenue': 0.1
            },
            'tiktok': {
                'completion_rate': 0.3,
                'shares': 0.25,
                'engagement_rate': 0.2,
                'views': 0.15,
                'comments': 0.1
            },
            'facebook': {
                'shares': 0.3,
                'engagement_rate': 0.25,
                'comments': 0.2,
                'reach': 0.15,
                'saves': 0.1
            }
        }
        
        platform_weights = weights.get(platform, weights['youtube'])
        score = 0.0
        
        for metric, weight in platform_weights.items():
            value = metrics.get(metric, 0)
            # Normalize metrics to 0-1 scale (simplified)
            normalized_value = min(value / 1000, 1.0) if metric in ['views', 'reach'] else value
            score += normalized_value * weight
        
        return score
    
    def _calculate_improvement(self, performance_scores: List[Tuple]) -> float:
        """Calculate percentage improvement of winner over baseline"""
        
        if len(performance_scores) < 2:
            return 0.0
        
        sorted_scores = sorted(performance_scores, key=lambda x: x[1], reverse=True)
        winner_score = sorted_scores[0][1]
        baseline_score = sorted_scores[-1][1]
        
        if baseline_score > 0:
            return ((winner_score - baseline_score) / baseline_score) * 100
        return 0.0
    
    def _calculate_confidence(self, performance_scores: List[Tuple]) -> float:
        """Calculate confidence level in the test result"""
        
        # Simplified confidence calculation
        # In practice, you'd use proper statistical tests
        
        if len(performance_scores) < 2:
            return 0.0
        
        scores = [score for _, score in performance_scores]
        mean_score = np.mean(scores)
        std_score = np.std(scores)
        
        if std_score > 0:
            confidence = min(abs(max(scores) - mean_score) / std_score, 1.0)
        else:
            confidence = 1.0
        
        return confidence * 100  # Return as percentage

class PredictiveOptimizer:
    """ML-based predictive optimization system"""
    
    def __init__(self, model_path: str = "optimization_models"):
        self.model_path = Path(model_path)
        self.model_path.mkdir(exist_ok=True)
        
        self.models = {}
        self.scalers = {}
        self.feature_columns = [
            'hour_of_day', 'day_of_week', 'title_length', 'hashtag_count',
            'description_length', 'has_question', 'has_numbers', 'has_emojis'
        ]
        
        self.load_models()
    
    def load_models(self):
        """Load trained models for each platform"""
        
        for platform in ['youtube', 'tiktok', 'facebook']:
            model_file = self.model_path / f"{platform}_model.pkl"
            scaler_file = self.model_path / f"{platform}_scaler.pkl"
            
            if model_file.exists() and scaler_file.exists():
                try:
                    with open(model_file, 'rb') as f:
                        self.models[platform] = pickle.load(f)
                    
                    with open(scaler_file, 'rb') as f:
                        self.scalers[platform] = pickle.load(f)
                    
                    logger.info(f"Loaded model for {platform}")
                except Exception as e:
                    logger.error(f"Error loading model for {platform}: {str(e)}")
    
    def extract_features(self, content_data: Dict, upload_time: datetime) -> np.array:
        """Extract features from content for prediction"""
        
        features = []
        
        # Time features
        features.append(upload_time.hour)
        features.append(upload_time.weekday())
        
        # Content features
        title = content_data.get('title', '')
        description = content_data.get('description', '')
        hashtags = content_data.get('hashtags', [])
        
        features.append(len(title))
        features.append(len(hashtags))
        features.append(len(description))
        features.append(1 if '?' in title else 0)  # Has question
        features.append(1 if any(c.isdigit() for c in title) else 0)  # Has numbers
        features.append(1 if any(c in '😀😃😄😁🤯😱🔥⚡🚀💎🎯💡' for c in title) else 0)  # Has emojis
        
        return np.array(features).reshape(1, -1)
    
    def predict_performance(self, content_data: Dict, platform: str, upload_time: datetime) -> Dict[str, float]:
        """Predict content performance"""
        
        if platform not in self.models:
            return {'error': f'No model available for {platform}'}
        
        try:
            features = self.extract_features(content_data, upload_time)
            scaled_features = self.scalers[platform].transform(features)
            
            # Predict multiple metrics (in practice, you'd have separate models)
            prediction = self.models[platform].predict(scaled_features)[0]
            
            return {
                'predicted_views': max(int(prediction * 1000), 0),
                'predicted_engagement_rate': max(min(prediction * 10, 100), 0),
                'confidence_score': 0.75  # Placeholder confidence
            }
            
        except Exception as e:
            logger.error(f"Prediction error for {platform}: {str(e)}")
            return {'error': str(e)}
    
    def optimize_content(self, content_data: Dict, platform: str) -> Dict[str, Any]:
        """Generate optimized content recommendations"""
        
        optimization_suggestions = {
            'title_optimization': [],
            'timing_optimization': [],
            'hashtag_optimization': [],
            'description_optimization': []
        }
        
        # Title optimization
        title = content_data.get('title', '')
        if len(title) < 50:
            optimization_suggestions['title_optimization'].append(
                "Consider adding more descriptive words to reach 50-80 characters for better SEO"
            )
        
        if '?' not in title and platform == 'tiktok':
            optimization_suggestions['title_optimization'].append(
                "Add a question to increase engagement on TikTok"
            )
        
        # Timing optimization
        current_time = datetime.now()
        optimal_times = self._get_optimal_times(platform)
        
        best_time = min(optimal_times, key=lambda t: abs(current_time.hour - t))
        if abs(current_time.hour - best_time) > 2:
            optimization_suggestions['timing_optimization'].append(
                f"Consider posting at {best_time}:00 for better reach on {platform}"
            )
        
        # Hashtag optimization
        hashtags = content_data.get('hashtags', [])
        optimal_count = {'youtube': 10, 'tiktok': 15, 'facebook': 8}
        
        if len(hashtags) < optimal_count[platform]:
            optimization_suggestions['hashtag_optimization'].append(
                f"Add {optimal_count[platform] - len(hashtags)} more hashtags for better discoverability"
            )
        
        return optimization_suggestions
    
    def _get_optimal_times(self, platform: str) -> List[int]:
        """Get optimal posting times for platform"""
        
        optimal_times = {
            'youtube': [14, 18, 20],
            'tiktok': [6, 10, 19, 21],
            'facebook': [13, 15, 18]
        }
        
        return optimal_times.get(platform, [14, 18, 20])

class InsightGenerator:
    """Generates actionable insights from performance data"""
    
    def __init__(self):
        self.insight_history = []
    
    def generate_insights(self, performance_history: List[Dict], platform: str) -> List[OptimizationInsight]:
        """Generate insights from performance history"""
        
        insights = []
        
        if len(performance_history) < 5:
            return insights  # Need minimum data
        
        # Analyze timing patterns
        timing_insights = self._analyze_timing_patterns(performance_history, platform)
        insights.extend(timing_insights)
        
        # Analyze content patterns
        content_insights = self._analyze_content_patterns(performance_history, platform)
        insights.extend(content_insights)
        
        # Analyze engagement patterns
        engagement_insights = self._analyze_engagement_patterns(performance_history, platform)
        insights.extend(engagement_insights)
        
        return insights
    
    def _analyze_timing_patterns(self, data: List[Dict], platform: str) -> List[OptimizationInsight]:
        """Analyze timing patterns for insights"""
        
        insights = []
        
        # Group by hour
        hour_performance = {}
        for item in data:
            upload_time = datetime.fromisoformat(item.get('upload_time', datetime.now().isoformat()))
            hour = upload_time.hour
            
            if hour not in hour_performance:
                hour_performance[hour] = []
            hour_performance[hour].append(item.get('engagement_rate', 0))
        
        # Find best performing hours
        hour_averages = {hour: np.mean(rates) for hour, rates in hour_performance.items() if len(rates) >= 2}
        
        if hour_averages:
            best_hour = max(hour_averages.keys(), key=lambda h: hour_averages[h])
            best_performance = hour_averages[best_hour]
            
            # Check if significantly better than average
            overall_average = np.mean(list(hour_averages.values()))
            
            if best_performance > overall_average * 1.2:  # 20% better
                insight = OptimizationInsight(
                    insight_type="timing_optimization",
                    platform=platform,
                    description=f"Content posted at {best_hour}:00 performs {((best_performance/overall_average - 1) * 100):.1f}% better than average",
                    confidence_score=0.8,
                    impact_estimate=best_performance - overall_average,
                    action_required=f"Schedule more content at {best_hour}:00",
                    data_source="timing_analysis",
                    created_at=datetime.now()
                )
                insights.append(insight)
        
        return insights
    
    def _analyze_content_patterns(self, data: List[Dict], platform: str) -> List[OptimizationInsight]:
        """Analyze content patterns for insights"""
        
        insights = []
        
        # Analyze title patterns
        question_titles = [item for item in data if '?' in item.get('title', '')]
        non_question_titles = [item for item in data if '?' not in item.get('title', '')]
        
        if len(question_titles) >= 3 and len(non_question_titles) >= 3:
            question_avg = np.mean([item.get('engagement_rate', 0) for item in question_titles])
            non_question_avg = np.mean([item.get('engagement_rate', 0) for item in non_question_titles])
            
            if question_avg > non_question_avg * 1.15:  # 15% better
                insight = OptimizationInsight(
                    insight_type="content_optimization",
                    platform=platform,
                    description=f"Titles with questions perform {((question_avg/non_question_avg - 1) * 100):.1f}% better",
                    confidence_score=0.7,
                    impact_estimate=question_avg - non_question_avg,
                    action_required="Use more question-based titles",
                    data_source="content_analysis",
                    created_at=datetime.now()
                )
                insights.append(insight)
        
        return insights
    
    def _analyze_engagement_patterns(self, data: List[Dict], platform: str) -> List[OptimizationInsight]:
        """Analyze engagement patterns for insights"""
        
        insights = []
        
        # Find trending content patterns
        recent_data = sorted(data, key=lambda x: x.get('upload_time', ''), reverse=True)[:10]
        older_data = sorted(data, key=lambda x: x.get('upload_time', ''), reverse=True)[10:20]
        
        if len(recent_data) >= 5 and len(older_data) >= 5:
            recent_avg = np.mean([item.get('engagement_rate', 0) for item in recent_data])
            older_avg = np.mean([item.get('engagement_rate', 0) for item in older_data])
            
            if recent_avg > older_avg * 1.1:  # 10% improvement
                insight = OptimizationInsight(
                    insight_type="trend_analysis",
                    platform=platform,
                    description=f"Recent content engagement improved by {((recent_avg/older_avg - 1) * 100):.1f}%",
                    confidence_score=0.6,
                    impact_estimate=recent_avg - older_avg,
                    action_required="Continue current content strategy",
                    data_source="engagement_trend_analysis",
                    created_at=datetime.now()
                )
                insights.append(insight)
        
        return insights

# Example usage
async def main():
    """Example of advanced optimization system"""
    
    # Initialize systems
    ab_test_manager = ABTestManager()
    optimizer = PredictiveOptimizer()
    insight_generator = InsightGenerator()
    
    # Example content data
    content_data = {
        'content_id': 'test_001',
        'title': 'Amazing AI Facts',
        'description': 'Learn about incredible AI developments',
        'hashtags': ['#AI', '#Technology', '#Facts'],
        'topic': 'Artificial Intelligence',
        'core_message': 'AI is advancing rapidly',
        'upload_time': datetime.now()
    }
    
    print("🧪 Advanced Optimization System Demo")
    print("=" * 40)
    
    # Create A/B test variations
    print("\n1. Creating A/B Test Variations:")
    variations = ab_test_manager.create_test_variations(content_data, 'tiktok', 0.3)
    
    for var in variations:
        print(f"   Test: {var.variation_type}")
        print(f"   Original: {var.original_value}")
        print(f"   Variation: {var.test_value}")
        print()
    
    # Performance predictions
    print("2. Performance Predictions:")
    for platform in ['youtube', 'tiktok', 'facebook']:
        prediction = optimizer.predict_performance(content_data, platform, datetime.now())
        if 'error' not in prediction:
            print(f"   {platform.title()}:")
            print(f"     Predicted Views: {prediction.get('predicted_views', 0):,}")
            print(f"     Predicted Engagement: {prediction.get('predicted_engagement_rate', 0):.1f}%")
        else:
            print(f"   {platform.title()}: {prediction['error']}")
    
    # Optimization suggestions
    print("\n3. Optimization Suggestions:")
    for platform in ['youtube', 'tiktok', 'facebook']:
        suggestions = optimizer.optimize_content(content_data, platform)
        
        print(f"\n   {platform.title()}:")
        for category, suggestions_list in suggestions.items():
            if suggestions_list:
                print(f"     {category.replace('_', ' ').title()}:")
                for suggestion in suggestions_list:
                    print(f"       • {suggestion}")
    
    # Simulate some performance data for insight generation
    print("\n4. Performance Insights:")
    
    sample_performance = [
        {
            'upload_time': (datetime.now() - timedelta(days=i)).isoformat(),
            'engagement_rate': random.uniform(5, 15),
            'title': f"Test Title {i}" + ("?" if i % 3 == 0 else ""),
            'views': random.randint(1000, 50000)
        }
        for i in range(20)
    ]
    
    insights = insight_generator.generate_insights(sample_performance, 'tiktok')
    
    for insight in insights:
        print(f"   📊 {insight.insight_type.replace('_', ' ').title()}")
        print(f"      {insight.description}")
        print(f"      Action: {insight.action_required}")
        print(f"      Confidence: {insight.confidence_score:.1%}")
        print()
    
    print("🎯 Optimization analysis complete!")

if __name__ == "__main__":
    asyncio.run(main())