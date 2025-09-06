#!/usr/bin/env python3
"""
Real-time Monitoring & Analytics System
Complete monitoring, alerting, and analytics for omnichannel content
"""

import asyncio
import aiohttp
import json
import logging
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
import numpy as np
import sqlite3
from contextlib import asynccontextmanager
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import schedule
import threading
import os

logger = logging.getLogger(__name__)

@dataclass
class AlertRule:
    """Alert configuration rule"""
    rule_id: str
    name: str
    condition_type: str  # threshold, trend, anomaly
    metric: str
    platform: str
    threshold_value: float
    comparison: str  # greater_than, less_than, equals
    time_window_minutes: int
    severity: str  # low, medium, high, critical
    enabled: bool = True
    notification_methods: List[str] = None  # email, webhook, slack

@dataclass
class Alert:
    """Alert instance"""
    alert_id: str
    rule_id: str
    triggered_at: datetime
    metric_value: float
    message: str
    severity: str
    platform: str
    resolved: bool = False
    resolved_at: Optional[datetime] = None

@dataclass
class PerformanceSnapshot:
    """Performance snapshot for a specific time"""
    timestamp: datetime
    platform: str
    content_id: str
    views: int
    engagement_rate: float
    revenue: float
    reach: int
    shares: int
    comments: int
    likes: int

class DatabaseManager:
    """SQLite database manager for analytics data"""
    
    def __init__(self, db_path: str = "omnichannel_analytics.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Performance data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    platform TEXT,
                    content_id TEXT,
                    metric_name TEXT,
                    metric_value REAL,
                    INDEX(timestamp),
                    INDEX(platform),
                    INDEX(content_id)
                )
            ''')
            
            # Alert history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alert_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id TEXT UNIQUE,
                    rule_id TEXT,
                    triggered_at DATETIME,
                    resolved_at DATETIME,
                    metric_value REAL,
                    message TEXT,
                    severity TEXT,
                    platform TEXT,
                    resolved BOOLEAN DEFAULT 0
                )
            ''')
            
            # Content metadata table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS content_metadata (
                    content_id TEXT PRIMARY KEY,
                    title TEXT,
                    created_at DATETIME,
                    topic TEXT,
                    platforms TEXT,  -- JSON array
                    ab_test_variant TEXT,
                    optimization_score REAL
                )
            ''')
            
            conn.commit()
    
    def store_performance_data(self, snapshot: PerformanceSnapshot):
        """Store performance snapshot in database"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Store each metric as a separate row for easier querying
            metrics = {
                'views': snapshot.views,
                'engagement_rate': snapshot.engagement_rate,
                'revenue': snapshot.revenue,
                'reach': snapshot.reach,
                'shares': snapshot.shares,
                'comments': snapshot.comments,
                'likes': snapshot.likes
            }
            
            for metric_name, metric_value in metrics.items():
                cursor.execute('''
                    INSERT INTO performance_data 
                    (timestamp, platform, content_id, metric_name, metric_value)
                    VALUES (?, ?, ?, ?, ?)
                ''', (snapshot.timestamp, snapshot.platform, snapshot.content_id, 
                     metric_name, metric_value))
            
            conn.commit()
    
    def get_performance_trend(self, platform: str, metric: str, hours: int = 24) -> List[Tuple]:
        """Get performance trend for a metric"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            since = datetime.now() - timedelta(hours=hours)
            
            cursor.execute('''
                SELECT timestamp, AVG(metric_value) as avg_value
                FROM performance_data
                WHERE platform = ? AND metric_name = ? AND timestamp > ?
                GROUP BY DATE(timestamp), HOUR(timestamp)
                ORDER BY timestamp
            ''', (platform, metric, since))
            
            return cursor.fetchall()
    
    def get_platform_summary(self, platform: str, hours: int = 24) -> Dict:
        """Get platform performance summary"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            since = datetime.now() - timedelta(hours=hours)
            
            cursor.execute('''
                SELECT 
                    metric_name,
                    SUM(metric_value) as total_value,
                    AVG(metric_value) as avg_value,
                    COUNT(*) as data_points
                FROM performance_data
                WHERE platform = ? AND timestamp > ?
                GROUP BY metric_name
            ''', (platform, since))
            
            results = {}
            for row in cursor.fetchall():
                metric_name, total_value, avg_value, data_points = row
                results[metric_name] = {
                    'total': total_value,
                    'average': avg_value,
                    'data_points': data_points
                }
            
            return results

class AlertManager:
    """Manages alerts and notifications"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.db_manager = DatabaseManager()
        self.notification_handlers = {
            'email': self._send_email_notification,
            'webhook': self._send_webhook_notification,
            'slack': self._send_slack_notification
        }
    
    def add_alert_rule(self, rule: AlertRule):
        """Add an alert rule"""
        self.alert_rules[rule.rule_id] = rule
        logger.info(f"Added alert rule: {rule.name}")
    
    def check_alerts(self, performance_data: Dict[str, Any]):
        """Check all alert rules against current performance data"""
        
        for rule in self.alert_rules.values():
            if not rule.enabled:
                continue
            
            platform_data = performance_data.get(rule.platform, {})
            metric_value = platform_data.get(rule.metric, 0)
            
            if self._evaluate_condition(rule, metric_value):
                self._trigger_alert(rule, metric_value)
    
    def _evaluate_condition(self, rule: AlertRule, current_value: float) -> bool:
        """Evaluate if alert condition is met"""
        
        if rule.comparison == 'greater_than':
            return current_value > rule.threshold_value
        elif rule.comparison == 'less_than':
            return current_value < rule.threshold_value
        elif rule.comparison == 'equals':
            return abs(current_value - rule.threshold_value) < 0.01
        
        return False
    
    def _trigger_alert(self, rule: AlertRule, metric_value: float):
        """Trigger an alert"""
        
        alert_id = f"{rule.rule_id}_{int(time.time())}"
        
        # Check if we already have an active alert for this rule
        existing_alert = next((alert for alert in self.active_alerts.values() 
                             if alert.rule_id == rule.rule_id and not alert.resolved), None)
        
        if existing_alert:
            return  # Don't spam alerts
        
        alert = Alert(
            alert_id=alert_id,
            rule_id=rule.rule_id,
            triggered_at=datetime.now(),
            metric_value=metric_value,
            message=f"{rule.name}: {rule.metric} is {metric_value:.2f} (threshold: {rule.threshold_value})",
            severity=rule.severity,
            platform=rule.platform
        )
        
        self.active_alerts[alert_id] = alert
        
        # Store in database
        with sqlite3.connect(self.db_manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO alert_history 
                (alert_id, rule_id, triggered_at, metric_value, message, severity, platform)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (alert.alert_id, alert.rule_id, alert.triggered_at, 
                 alert.metric_value, alert.message, alert.severity, alert.platform))
            conn.commit()
        
        # Send notifications
        self._send_notifications(alert, rule)
        
        logger.warning(f"ALERT TRIGGERED: {alert.message}")
    
    def _send_notifications(self, alert: Alert, rule: AlertRule):
        """Send notifications for an alert"""
        
        if not rule.notification_methods:
            return
        
        for method in rule.notification_methods:
            if method in self.notification_handlers:
                try:
                    self.notification_handlers[method](alert, rule)
                except Exception as e:
                    logger.error(f"Failed to send {method} notification: {str(e)}")
    
    def _send_email_notification(self, alert: Alert, rule: AlertRule):
        """Send email notification"""
        
        email_config = self.config.get('email', {})
        if not email_config.get('enabled'):
            return
        
        smtp_server = email_config.get('smtp_server')
        smtp_port = email_config.get('smtp_port', 587)
        username = email_config.get('username')
        password = email_config.get('password')
        to_emails = email_config.get('alert_recipients', [])
        
        if not all([smtp_server, username, password, to_emails]):
            logger.error("Email configuration incomplete")
            return
        
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = ', '.join(to_emails)
        msg['Subject'] = f"🚨 Omnichannel Alert: {alert.severity.upper()}"
        
        body = f"""
        Alert Details:
        - Platform: {alert.platform}
        - Severity: {alert.severity}
        - Message: {alert.message}
        - Triggered: {alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S')}
        
        Please check the dashboard for more details.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
    
    def _send_webhook_notification(self, alert: Alert, rule: AlertRule):
        """Send webhook notification"""
        
        webhook_config = self.config.get('webhook', {})
        if not webhook_config.get('enabled'):
            return
        
        webhook_url = webhook_config.get('url')
        if not webhook_url:
            return
        
        payload = {
            'alert_id': alert.alert_id,
            'rule_name': rule.name,
            'platform': alert.platform,
            'severity': alert.severity,
            'message': alert.message,
            'metric_value': alert.metric_value,
            'triggered_at': alert.triggered_at.isoformat()
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
    
    def _send_slack_notification(self, alert: Alert, rule: AlertRule):
        """Send Slack notification"""
        
        slack_config = self.config.get('slack', {})
        if not slack_config.get('enabled'):
            return
        
        webhook_url = slack_config.get('webhook_url')
        if not webhook_url:
            return
        
        severity_colors = {
            'low': '#36a64f',
            'medium': '#ff9500',
            'high': '#ff0000',
            'critical': '#8b0000'
        }
        
        payload = {
            'attachments': [{
                'color': severity_colors.get(alert.severity, '#36a64f'),
                'title': f"🚨 {alert.severity.upper()} Alert",
                'text': alert.message,
                'fields': [
                    {
                        'title': 'Platform',
                        'value': alert.platform,
                        'short': True
                    },
                    {
                        'title': 'Metric Value',
                        'value': f"{alert.metric_value:.2f}",
                        'short': True
                    },
                    {
                        'title': 'Time',
                        'value': alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S'),
                        'short': False
                    }
                ]
            }]
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()

class PerformanceCollector:
    """Collects performance data from all platforms"""
    
    def __init__(self, api_clients: Dict):
        self.api_clients = api_clients
        self.db_manager = DatabaseManager()
        self.collection_intervals = {
            'real_time': 300,  # 5 minutes
            'hourly': 3600,    # 1 hour
            'daily': 86400     # 24 hours
        }
    
    async def collect_all_platforms(self) -> Dict[str, Dict]:
        """Collect performance data from all platforms"""
        
        all_data = {}
        
        for platform, client in self.api_clients.items():
            try:
                platform_data = await self._collect_platform_data(platform, client)
                all_data[platform] = platform_data
                logger.info(f"Collected data from {platform}: {len(platform_data)} content items")
            except Exception as e:
                logger.error(f"Failed to collect data from {platform}: {str(e)}")
                all_data[platform] = {}
        
        return all_data
    
    async def _collect_platform_data(self, platform: str, client) -> Dict:
        """Collect data from a specific platform"""
        
        platform_data = {}
        
        if platform == 'youtube':
            platform_data = await self._collect_youtube_data(client)
        elif platform == 'tiktok':
            platform_data = await self._collect_tiktok_data(client)
        elif platform == 'facebook':
            platform_data = await self._collect_facebook_data(client)
        
        return platform_data
    
    async def _collect_youtube_data(self, client) -> Dict:
        """Collect YouTube analytics data"""
        
        try:
            # Get channel analytics
            analytics_response = client.service.reports().query(
                ids='channel==MINE',
                startDate='2024-01-01',
                endDate=datetime.now().strftime('%Y-%m-%d'),
                metrics='views,estimatedMinutesWatched,subscribersGained,likes,comments',
                dimensions='day'
            ).execute()
            
            # Process and aggregate data
            data = {
                'total_views': 0,
                'total_watch_time': 0,
                'total_subscribers': 0,
                'total_engagement': 0,
                'content_performance': []
            }
            
            for row in analytics_response.get('rows', []):
                data['total_views'] += int(row[1])
                data['total_watch_time'] += int(row[2])
                data['total_subscribers'] += int(row[3])
                data['total_engagement'] += int(row[4]) + int(row[5])
            
            return data
            
        except Exception as e:
            logger.error(f"YouTube data collection error: {str(e)}")
            return {}
    
    async def _collect_tiktok_data(self, client) -> Dict:
        """Collect TikTok analytics data"""
        
        try:
            # This would use TikTok's Analytics API
            # For now, return simulated data
            data = {
                'total_views': 0,
                'total_likes': 0,
                'total_shares': 0,
                'total_comments': 0,
                'content_performance': []
            }
            
            return data
            
        except Exception as e:
            logger.error(f"TikTok data collection error: {str(e)}")
            return {}
    
    async def _collect_facebook_data(self, client) -> Dict:
        """Collect Facebook analytics data"""
        
        try:
            # This would use Facebook Graph API for insights
            # For now, return simulated data
            data = {
                'total_reach': 0,
                'total_impressions': 0,
                'total_engagement': 0,
                'total_video_views': 0,
                'content_performance': []
            }
            
            return data
            
        except Exception as e:
            logger.error(f"Facebook data collection error: {str(e)}")
            return {}

class RealTimeMonitor:
    """Real-time monitoring system"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.db_manager = DatabaseManager()
        self.alert_manager = AlertManager(config)
        self.performance_collector = PerformanceCollector({})
        self.is_running = False
        self.monitoring_tasks = []
        
        # Setup default alert rules
        self._setup_default_alerts()
    
    def _setup_default_alerts(self):
        """Setup default alert rules"""
        
        default_rules = [
            AlertRule(
                rule_id="low_engagement_youtube",
                name="Low Engagement Rate - YouTube",
                condition_type="threshold",
                metric="engagement_rate",
                platform="youtube",
                threshold_value=2.0,
                comparison="less_than",
                time_window_minutes=60,
                severity="medium",
                notification_methods=["email"]
            ),
            AlertRule(
                rule_id="viral_content_tiktok",
                name="Viral Content Alert - TikTok",
                condition_type="threshold",
                metric="views",
                platform="tiktok",
                threshold_value=100000,
                comparison="greater_than",
                time_window_minutes=30,
                severity="high",
                notification_methods=["slack", "email"]
            ),
            AlertRule(
                rule_id="low_reach_facebook",
                name="Low Reach - Facebook",
                condition_type="threshold",
                metric="reach",
                platform="facebook",
                threshold_value=1000,
                comparison="less_than",
                time_window_minutes=120,
                severity="low",
                notification_methods=["email"]
            )
        ]
        
        for rule in default_rules:
            self.alert_manager.add_alert_rule(rule)
    
    async def start_monitoring(self):
        """Start real-time monitoring"""
        
        if self.is_running:
            logger.warning("Monitoring is already running")
            return
        
        self.is_running = True
        logger.info("🚀 Starting real-time monitoring system")
        
        # Start monitoring tasks
        self.monitoring_tasks = [
            asyncio.create_task(self._performance_monitoring_loop()),
            asyncio.create_task(self._alert_checking_loop()),
            asyncio.create_task(self._health_check_loop())
        ]
        
        # Wait for all tasks
        await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
    
    async def stop_monitoring(self):
        """Stop monitoring"""
        
        self.is_running = False
        
        for task in self.monitoring_tasks:
            task.cancel()
        
        logger.info("🛑 Monitoring system stopped")
    
    async def _performance_monitoring_loop(self):
        """Main performance monitoring loop"""
        
        while self.is_running:
            try:
                # Collect performance data
                performance_data = await self.performance_collector.collect_all_platforms()
                
                # Store data and check alerts
                for platform, data in performance_data.items():
                    if data:
                        # Store performance snapshots
                        for content_id, metrics in data.get('content_performance', {}).items():
                            snapshot = PerformanceSnapshot(
                                timestamp=datetime.now(),
                                platform=platform,
                                content_id=content_id,
                                views=metrics.get('views', 0),
                                engagement_rate=metrics.get('engagement_rate', 0),
                                revenue=metrics.get('revenue', 0),
                                reach=metrics.get('reach', 0),
                                shares=metrics.get('shares', 0),
                                comments=metrics.get('comments', 0),
                                likes=metrics.get('likes', 0)
                            )
                            self.db_manager.store_performance_data(snapshot)
                
                # Wait before next collection
                await asyncio.sleep(self.performance_collector.collection_intervals['real_time'])
                
            except Exception as e:
                logger.error(f"Performance monitoring error: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _alert_checking_loop(self):
        """Alert checking loop"""
        
        while self.is_running:
            try:
                # Get latest performance data
                current_performance = {}
                
                for platform in ['youtube', 'tiktok', 'facebook']:
                    platform_summary = self.db_manager.get_platform_summary(platform, hours=1)
                    current_performance[platform] = {
                        metric: data.get('average', 0) 
                        for metric, data in platform_summary.items()
                    }
                
                # Check alerts
                self.alert_manager.check_alerts(current_performance)
                
                # Wait before next check
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Alert checking error: {str(e)}")
                await asyncio.sleep(60)
    
    async def _health_check_loop(self):
        """System health monitoring loop"""
        
        while self.is_running:
            try:
                # Check system health metrics
                health_status = {
                    'database_connection': self._check_database_health(),
                    'api_connections': await self._check_api_health(),
                    'disk_space': self._check_disk_space(),
                    'memory_usage': self._check_memory_usage()
                }
                
                # Log health status
                unhealthy_components = [k for k, v in health_status.items() if not v]
                
                if unhealthy_components:
                    logger.warning(f"Health check failed for: {', '.join(unhealthy_components)}")
                else:
                    logger.info("✅ All systems healthy")
                
                # Wait before next health check
                await asyncio.sleep(1800)  # Check every 30 minutes
                
            except Exception as e:
                logger.error(f"Health check error: {str(e)}")
                await asyncio.sleep(300)
    
    def _check_database_health(self) -> bool:
        """Check database connectivity"""
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                return True
        except:
            return False
    
    async def _check_api_health(self) -> bool:
        """Check API connectivity"""
        # This would check actual API endpoints
        # For now, return True
        return True
    
    def _check_disk_space(self) -> bool:
        """Check available disk space"""
        import shutil
        
        try:
            total, used, free = shutil.disk_usage('.')
            free_percentage = (free / total) * 100
            return free_percentage > 10  # Alert if less than 10% free
        except:
            return True
    
    def _check_memory_usage(self) -> bool:
        """Check memory usage"""
        import psutil
        
        try:
            memory = psutil.virtual_memory()
            return memory.percent < 90  # Alert if more than 90% used
        except:
            return True

class ReportGenerator:
    """Generates performance reports"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def generate_daily_report(self, date: datetime = None) -> Dict:
        """Generate daily performance report"""
        
        if date is None:
            date = datetime.now().date()
        
        start_time = datetime.combine(date, datetime.min.time())
        end_time = datetime.combine(date, datetime.max.time())
        
        report = {
            'date': date.isoformat(),
            'platforms': {},
            'summary': {}
        }
        
        total_metrics = {
            'total_views': 0,
            'total_engagement': 0,
            'total_revenue': 0,
            'total_reach': 0
        }
        
        for platform in ['youtube', 'tiktok', 'facebook']:
            platform_data = self._get_platform_daily_data(platform, start_time, end_time)
            report['platforms'][platform] = platform_data
            
            # Add to totals
            total_metrics['total_views'] += platform_data.get('views', 0)
            total_metrics['total_engagement'] += platform_data.get('engagement_rate', 0)
            total_metrics['total_revenue'] += platform_data.get('revenue', 0)
            total_metrics['total_reach'] += platform_data.get('reach', 0)
        
        report['summary'] = total_metrics
        
        return report
    
    def _get_platform_daily_data(self, platform: str, start_time: datetime, end_time: datetime) -> Dict:
        """Get daily data for a platform"""
        
        with sqlite3.connect(self.db_manager.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    metric_name,
                    SUM(metric_value) as total_value,
                    AVG(metric_value) as avg_value,
                    COUNT(DISTINCT content_id) as content_count
                FROM performance_data
                WHERE platform = ? AND timestamp BETWEEN ? AND ?
                GROUP BY metric_name
            ''', (platform, start_time, end_time))
            
            data = {}
            for row in cursor.fetchall():
                metric_name, total_value, avg_value, content_count = row
                data[metric_name] = total_value
                data[f'avg_{metric_name}'] = avg_value
            
            data['content_count'] = content_count if 'content_count' in locals() else 0
            
            return data

# Example monitoring configuration

def _parse_env_list(var_name: str) -> List[str]:
    """Return a list parsed from a comma-separated env var."""
    return [item.strip() for item in os.getenv(var_name, "").split(",") if item.strip()]

MONITORING_CONFIG = {
    'email': {
        'enabled': True,
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'username': os.getenv('SMTP_USERNAME', ''),
        'password': os.getenv('SMTP_PASSWORD', ''),
        'alert_recipients': _parse_env_list('ALERT_RECIPIENTS'),
    },
    'slack': {
        'enabled': True,
        'webhook_url': os.getenv('SLACK_WEBHOOK_URL', ''),
    },
    'webhook': {
        'enabled': False,
        'url': os.getenv('ALERT_WEBHOOK_URL', ''),
    },
}

# Main monitoring system
async def main():
    """Example of running the monitoring system"""
    
    print("🚀 Starting Omnichannel Monitoring System")
    print("=" * 45)
    
    # Initialize monitoring system
    monitor = RealTimeMonitor(MONITORING_CONFIG)
    
    # Start monitoring
    try:
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down monitoring system...")
        await monitor.stop_monitoring()
    
    print("✅ Monitoring system stopped gracefully")

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    asyncio.run(main())
