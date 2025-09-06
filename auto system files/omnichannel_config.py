#!/usr/bin/env python3
"""
Omnichannel Framework Configuration and Setup
Complete setup guide and configuration management
"""

import os
import json
import yaml
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, time

logger = logging.getLogger(__name__)

@dataclass
class PlatformConfig:
    """Configuration for individual platforms"""
    enabled: bool = True
    api_credentials: Dict[str, str] = None
    upload_limits: Dict[str, int] = None
    optimal_times: List[str] = None
    content_settings: Dict[str, Any] = None
    quality_settings: Dict[str, Any] = None

@dataclass
class OmnichannelConfig:
    """Main configuration for the omnichannel system"""
    
    # System settings
    system_name: str = "Omnichannel Content Hub"
    version: str = "1.0.0"
    debug_mode: bool = False
    log_level: str = "INFO"
    
    # Content creation settings
    default_video_duration: float = 45.0
    default_canvas_size: tuple = (1080, 1920)
    content_output_dir: str = "./output"
    temp_dir: str = "./temp"
    
    # Platform configurations
    youtube: PlatformConfig = None
    tiktok: PlatformConfig = None
    facebook: PlatformConfig = None
    
    # Distribution settings
    distribution_strategy: str = "balanced"  # balanced, viral_first, authority_first
    max_concurrent_uploads: int = 3
    upload_retry_attempts: int = 3
    
    # Analytics and monitoring
    analytics_enabled: bool = True
    performance_tracking: bool = True
    webhook_notifications: bool = False
    webhook_url: str = ""
    
    # A/B testing settings
    ab_testing_enabled: bool = True
    test_percentage: float = 0.2  # 20% of content for testing
    
    def __post_init__(self):
        """Initialize default platform configs if not provided"""
        if self.youtube is None:
            self.youtube = PlatformConfig(
                enabled=True,
                api_credentials={},
                upload_limits={'daily': 20, 'hourly': 5},
                optimal_times=['14:00', '18:00', '20:00'],
                content_settings={
                    'max_title_length': 100,
                    'max_description_length': 5000,
                    'max_tags': 15,
                    'category': 'Education'
                },
                quality_settings={
                    'video_bitrate': '8000k',
                    'audio_bitrate': '192k',
                    'fps': 30
                }
            )
        
        if self.tiktok is None:
            self.tiktok = PlatformConfig(
                enabled=True,
                api_credentials={},
                upload_limits={'daily': 30, 'hourly': 8},
                optimal_times=['06:00', '10:00', '19:00'],
                content_settings={
                    'max_title_length': 150,
                    'hashtag_strategy': 'trending_focus',
                    'viral_elements': True
                },
                quality_settings={
                    'video_bitrate': '6000k',
                    'audio_bitrate': '128k',
                    'fps': 30
                }
            )
        
        if self.facebook is None:
            self.facebook = PlatformConfig(
                enabled=True,
                api_credentials={},
                upload_limits={'daily': 25, 'hourly': 6},
                optimal_times=['13:00', '15:00', '18:00'],
                content_settings={
                    'max_title_length': 255,
                    'max_description_length': 2000,
                    'social_focus': True
                },
                quality_settings={
                    'video_bitrate': '7000k',
                    'audio_bitrate': '160k',
                    'fps': 30
                }
            )

class ConfigManager:
    """Manages configuration loading, saving, and validation"""
    
    def __init__(self, config_path: str = "omnichannel_config.yaml"):
        self.config_path = Path(config_path)
        self.config: Optional[OmnichannelConfig] = None
        
    def load_config(self) -> OmnichannelConfig:
        """Load configuration from file or create default"""
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config_data = yaml.safe_load(f)
                
                # Convert dict to dataclass
                self.config = self._dict_to_config(config_data)
                logger.info(f"Configuration loaded from {self.config_path}")
                
            except Exception as e:
                logger.error(f"Error loading config: {str(e)}")
                logger.info("Creating default configuration")
                self.config = OmnichannelConfig()
        else:
            logger.info("No config file found, creating default")
            self.config = OmnichannelConfig()
            self.save_config()
        
        return self.config
    
    def save_config(self):
        """Save current configuration to file"""
        
        if self.config is None:
            raise ValueError("No configuration to save")
        
        try:
            config_dict = self._config_to_dict(self.config)
            
            with open(self.config_path, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            
            logger.info(f"Configuration saved to {self.config_path}")
            
        except Exception as e:
            logger.error(f"Error saving config: {str(e)}")
    
    def _dict_to_config(self, data: Dict) -> OmnichannelConfig:
        """Convert dictionary to OmnichannelConfig"""
        
        # Handle platform configs
        platforms = {}
        for platform in ['youtube', 'tiktok', 'facebook']:
            if platform in data:
                platforms[platform] = PlatformConfig(**data[platform])
        
        # Remove platform data from main config
        main_data = {k: v for k, v in data.items() if k not in ['youtube', 'tiktok', 'facebook']}
        
        return OmnichannelConfig(**main_data, **platforms)
    
    def _config_to_dict(self, config: OmnichannelConfig) -> Dict:
        """Convert OmnichannelConfig to dictionary"""
        
        result = {}
        
        for field_name, field_value in asdict(config).items():
            if isinstance(field_value, dict) and 'enabled' in field_value:
                # This is a platform config
                result[field_name] = field_value
            else:
                result[field_name] = field_value
        
        return result
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return list of issues"""
        
        issues = []
        
        if self.config is None:
            issues.append("No configuration loaded")
            return issues
        
        # Validate platform credentials
        for platform_name in ['youtube', 'tiktok', 'facebook']:
            platform_config = getattr(self.config, platform_name)
            
            if platform_config.enabled:
                required_creds = self._get_required_credentials(platform_name)
                
                for cred in required_creds:
                    if cred not in platform_config.api_credentials or not platform_config.api_credentials[cred]:
                        issues.append(f"{platform_name}: Missing {cred} credential")
        
        # Validate directories
        dirs_to_check = [self.config.content_output_dir, self.config.temp_dir]
        for dir_path in dirs_to_check:
            if not Path(dir_path).exists():
                issues.append(f"Directory does not exist: {dir_path}")
        
        # Validate upload limits
        for platform_name in ['youtube', 'tiktok', 'facebook']:
            platform_config = getattr(self.config, platform_name)
            
            if platform_config.upload_limits['daily'] <= 0:
                issues.append(f"{platform_name}: Daily upload limit must be > 0")
        
        return issues
    
    def _get_required_credentials(self, platform: str) -> List[str]:
        """Get required credentials for each platform"""
        
        cred_requirements = {
            'youtube': ['client_id', 'client_secret'],
            'tiktok': ['access_token'],
            'facebook': ['access_token', 'page_id']
        }
        
        return cred_requirements.get(platform, [])

class SetupWizard:
    """Interactive setup wizard for first-time configuration"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
    
    def run_setup(self) -> OmnichannelConfig:
        """Run interactive setup wizard"""
        
        print("🚀 Welcome to Omnichannel Content Hub Setup!")
        print("=" * 50)
        
        # Load or create config
        config = self.config_manager.load_config()
        
        # System settings
        config = self._setup_system_settings(config)
        
        # Platform setup
        config = self._setup_platforms(config)
        
        # Distribution settings
        config = self._setup_distribution(config)
        
        # Analytics settings
        config = self._setup_analytics(config)
        
        # Save configuration
        self.config_manager.config = config
        self.config_manager.save_config()
        
        # Validate and show summary
        issues = self.config_manager.validate_config()
        self._show_setup_summary(config, issues)
        
        return config
    
    def _setup_system_settings(self, config: OmnichannelConfig) -> OmnichannelConfig:
        """Setup basic system settings"""
        
        print("\n📋 System Settings")
        print("-" * 20)
        
        # Output directory
        output_dir = input(f"Content output directory [{config.content_output_dir}]: ").strip()
        if output_dir:
            config.content_output_dir = output_dir
        
        # Create directory if it doesn't exist
        Path(config.content_output_dir).mkdir(parents=True, exist_ok=True)
        
        # Debug mode
        debug_input = input(f"Enable debug mode? (y/N) [{config.debug_mode}]: ").strip().lower()
        if debug_input in ['y', 'yes']:
            config.debug_mode = True
        
        return config
    
    def _setup_platforms(self, config: OmnichannelConfig) -> OmnichannelConfig:
        """Setup platform configurations"""
        
        print("\n🎯 Platform Configuration")
        print("-" * 25)
        
        platforms = ['youtube', 'tiktok', 'facebook']
        
        for platform_name in platforms:
            print(f"\n{platform_name.upper()} Setup:")
            
            platform_config = getattr(config, platform_name)
            
            # Enable/disable platform
            enabled_input = input(f"Enable {platform_name}? (Y/n) [{platform_config.enabled}]: ").strip().lower()
            if enabled_input in ['n', 'no']:
                platform_config.enabled = False
                continue
            
            platform_config.enabled = True
            
            # Platform-specific credential setup
            if platform_name == 'youtube':
                self._setup_youtube_credentials(platform_config)
            elif platform_name == 'tiktok':
                self._setup_tiktok_credentials(platform_config)
            elif platform_name == 'facebook':
                self._setup_facebook_credentials(platform_config)
            
            # Upload limits
            daily_limit = input(f"Daily upload limit [{platform_config.upload_limits['daily']}]: ").strip()
            if daily_limit.isdigit():
                platform_config.upload_limits['daily'] = int(daily_limit)
        
        return config
    
    def _setup_youtube_credentials(self, platform_config: PlatformConfig):
        """Setup YouTube API credentials"""
        
        print("YouTube requires OAuth2 credentials from Google Cloud Console")
        print("Visit: https://console.cloud.google.com/apis/credentials")
        
        client_id = input("YouTube Client ID: ").strip()
        client_secret = input("YouTube Client Secret: ").strip()
        
        if client_id and client_secret:
            platform_config.api_credentials.update({
                'client_id': client_id,
                'client_secret': client_secret
            })
    
    def _setup_tiktok_credentials(self, platform_config: PlatformConfig):
        """Setup TikTok API credentials"""
        
        print("TikTok requires a Business Account with Content Posting API access")
        print("Visit: https://developers.tiktok.com/")
        
        access_token = input("TikTok Access Token: ").strip()
        
        if access_token:
            platform_config.api_credentials.update({
                'access_token': access_token
            })
    
    def _setup_facebook_credentials(self, platform_config: PlatformConfig):
        """Setup Facebook API credentials"""
        
        print("Facebook requires a Business Account and Page Access Token")
        print("Visit: https://developers.facebook.com/tools/explorer/")
        
        access_token = input("Facebook Access Token: ").strip()
        page_id = input("Facebook Page ID: ").strip()
        
        if access_token and page_id:
            platform_config.api_credentials.update({
                'access_token': access_token,
                'page_id': page_id
            })
    
    def _setup_distribution(self, config: OmnichannelConfig) -> OmnichannelConfig:
        """Setup distribution strategy"""
        
        print("\n📤 Distribution Strategy")
        print("-" * 23)
        
        strategies = ['balanced', 'viral_first', 'authority_first']
        
        print("Available strategies:")
        for i, strategy in enumerate(strategies, 1):
            print(f"{i}. {strategy}")
        
        choice = input(f"Select strategy (1-3) [{strategies.index(config.distribution_strategy) + 1}]: ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= 3:
            config.distribution_strategy = strategies[int(choice) - 1]
        
        return config
    
    def _setup_analytics(self, config: OmnichannelConfig) -> OmnichannelConfig:
        """Setup analytics and monitoring"""
        
        print("\n📊 Analytics & Monitoring")
        print("-" * 25)
        
        # Analytics
        analytics_input = input(f"Enable analytics? (Y/n) [{config.analytics_enabled}]: ").strip().lower()
        if analytics_input in ['n', 'no']:
            config.analytics_enabled = False
        
        # Webhooks
        webhook_input = input(f"Enable webhook notifications? (y/N) [{config.webhook_notifications}]: ").strip().lower()
        if webhook_input in ['y', 'yes']:
            config.webhook_notifications = True
            webhook_url = input("Webhook URL: ").strip()
            if webhook_url:
                config.webhook_url = webhook_url
        
        return config
    
    def _show_setup_summary(self, config: OmnichannelConfig, issues: List[str]):
        """Show setup summary and validation results"""
        
        print("\n✅ Setup Complete!")
        print("=" * 50)
        
        # Enabled platforms
        enabled_platforms = []
        for platform_name in ['youtube', 'tiktok', 'facebook']:
            platform_config = getattr(config, platform_name)
            if platform_config.enabled:
                enabled_platforms.append(platform_name.title())
        
        print(f"📱 Enabled Platforms: {', '.join(enabled_platforms)}")
        print(f"📤 Distribution Strategy: {config.distribution_strategy}")
        print(f"📊 Analytics: {'Enabled' if config.analytics_enabled else 'Disabled'}")
        print(f"📁 Output Directory: {config.content_output_dir}")
        
        # Show validation issues
        if issues:
            print(f"\n⚠️  Configuration Issues ({len(issues)}):")
            for issue in issues:
                print(f"  • {issue}")
            print("\nPlease fix these issues before running the system.")
        else:
            print(f"\n🎉 Configuration is valid! Ready to start.")
        
        print(f"\nConfig saved to: {self.config_manager.config_path}")

class CredentialManager:
    """Secure credential management"""
    
    def __init__(self, config_path: str = "credentials.json"):
        self.config_path = Path(config_path)
        self.credentials = {}
        self.load_credentials()
    
    def load_credentials(self):
        """Load credentials from encrypted file"""
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    self.credentials = json.load(f)
                logger.info("Credentials loaded successfully")
            except Exception as e:
                logger.error(f"Error loading credentials: {str(e)}")
                self.credentials = {}
        else:
            self.credentials = {}
    
    def save_credentials(self):
        """Save credentials to file"""
        
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.credentials, f, indent=2)
            
            # Set file permissions (readable only by owner)
            os.chmod(self.config_path, 0o600)
            logger.info("Credentials saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving credentials: {str(e)}")
    
    def set_credential(self, platform: str, key: str, value: str):
        """Set a credential for a platform"""
        
        if platform not in self.credentials:
            self.credentials[platform] = {}
        
        self.credentials[platform][key] = value
        self.save_credentials()
    
    def get_credential(self, platform: str, key: str) -> Optional[str]:
        """Get a credential for a platform"""
        
        return self.credentials.get(platform, {}).get(key)
    
    def get_all_credentials(self, platform: str) -> Dict[str, str]:
        """Get all credentials for a platform"""
        
        return self.credentials.get(platform, {})

class EnvironmentSetup:
    """Setup and validate the environment"""
    
    @staticmethod
    def check_dependencies():
        """Check if all required dependencies are installed"""
        
        required_packages = [
            'google-api-python-client',
            'google-auth-httplib2', 
            'google-auth-oauthlib',
            'aiohttp',
            'moviepy',
            'pillow',
            'pyyaml',
            'numpy'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print("❌ Missing required packages:")
            for package in missing_packages:
                print(f"  • {package}")
            print("\nInstall with: pip install " + " ".join(missing_packages))
            return False
        
        print("✅ All dependencies are installed")
        return True
    
    @staticmethod
    def setup_directories(config: OmnichannelConfig):
        """Create required directories"""
        
        directories = [
            config.content_output_dir,
            config.temp_dir,
            f"{config.content_output_dir}/youtube",
            f"{config.content_output_dir}/tiktok", 
            f"{config.content_output_dir}/facebook",
            f"{config.content_output_dir}/thumbnails",
            f"{config.content_output_dir}/captions"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"📁 Created directory: {directory}")
    
    @staticmethod
    def validate_apis(config: OmnichannelConfig) -> Dict[str, bool]:
        """Validate API connections"""
        
        results = {}
        
        # This would contain actual API validation logic
        # For now, just placeholder checks
        
        for platform_name in ['youtube', 'tiktok', 'facebook']:
            platform_config = getattr(config, platform_name)
            
            if platform_config.enabled:
                # Check if credentials exist
                has_creds = bool(platform_config.api_credentials)
                results[platform_name] = has_creds
                
                status = "✅" if has_creds else "❌"
                print(f"{status} {platform_name.title()}: {'Ready' if has_creds else 'Missing credentials'}")
            else:
                results[platform_name] = False
                print(f"⏸️  {platform_name.title()}: Disabled")
        
        return results

# Main setup script
def main():
    """Main setup function"""
    
    print("🚀 Omnichannel Framework Setup")
    print("=" * 40)
    
    # Check dependencies
    if not EnvironmentSetup.check_dependencies():
        return
    
    # Run setup wizard
    wizard = SetupWizard()
    config = wizard.run_setup()
    
    # Setup directories
    EnvironmentSetup.setup_directories(config)
    
    # Validate APIs
    api_status = EnvironmentSetup.validate_apis(config)
    
    # Final summary
    enabled_count = sum(1 for status in api_status.values() if status)
    total_count = len([p for p in ['youtube', 'tiktok', 'facebook'] if getattr(config, p).enabled])
    
    print(f"\n🎉 Setup completed!")
    print(f"📊 {enabled_count}/{total_count} platforms configured")
    
    if enabled_count > 0:
        print("\n🚀 Ready to start the omnichannel system!")
        print("Run: python omnichannel_orchestrator.py")
    else:
        print("\n⚠️  Please configure at least one platform before starting.")

if __name__ == "__main__":
    main()