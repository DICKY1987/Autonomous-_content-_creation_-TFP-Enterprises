import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, LineChart, Line, PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { Play, Pause, Settings, TrendingUp, Users, Eye, ThumbsUp, Share, MessageCircle } from 'lucide-react';

const OmnichannelDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [isRunning, setIsRunning] = useState(false);
  const [platforms, setPlatforms] = useState({
    youtube: { enabled: true, status: 'active', dailyQuota: 20, used: 5 },
    tiktok: { enabled: true, status: 'active', dailyQuota: 30, used: 12 },
    facebook: { enabled: true, status: 'active', dailyQuota: 25, used: 8 }
  });

  // Sample performance data
  const performanceData = [
    { platform: 'YouTube', views: 15420, engagement: 8.5, revenue: 45.20 },
    { platform: 'TikTok', views: 89750, engagement: 12.3, revenue: 23.80 },
    { platform: 'Facebook', views: 32100, engagement: 6.8, revenue: 18.50 }
  ];

  const dailyMetrics = [
    { day: 'Mon', youtube: 2400, tiktok: 8900, facebook: 1800 },
    { day: 'Tue', youtube: 1398, tiktok: 7200, facebook: 2200 },
    { day: 'Wed', youtube: 3200, tiktok: 9800, facebook: 2800 },
    { day: 'Thu', youtube: 2780, tiktok: 6500, facebook: 2400 },
    { day: 'Fri', youtube: 1890, tiktok: 12000, facebook: 3200 },
    { day: 'Sat', youtube: 2390, tiktok: 15600, facebook: 4100 },
    { day: 'Sun', youtube: 3490, tiktok: 18200, facebook: 3800 }
  ];

  const contentQueue = [
    { id: 1, topic: 'AI Revolution 2025', status: 'processing', platforms: ['youtube', 'tiktok', 'facebook'], eta: '5 min' },
    { id: 2, topic: 'Climate Solutions', status: 'optimizing', platforms: ['youtube', 'facebook'], eta: '12 min' },
    { id: 3, topic: 'Space Technology', status: 'scheduled', platforms: ['tiktok'], eta: '2 hours' },
    { id: 4, topic: 'Renewable Energy', status: 'ready', platforms: ['youtube', 'tiktok', 'facebook'], eta: 'Ready' }
  ];

  const platformColors = {
    youtube: '#FF0000',
    tiktok: '#000000', 
    facebook: '#1877F2'
  };

  const COLORS = ['#FF0000', '#000000', '#1877F2'];

  const OverviewTab = () => (
    <div className="space-y-6">
      {/* System Status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">System Status</p>
              <p className="text-2xl font-bold text-green-600">
                {isRunning ? 'Running' : 'Stopped'}
              </p>
            </div>
            <div className="p-3 bg-green-100 rounded-full">
              {isRunning ? <Play className="h-6 w-6 text-green-600" /> : <Pause className="h-6 w-6 text-gray-600" />}
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Daily Videos</p>
              <p className="text-2xl font-bold text-blue-600">25</p>
              <p className="text-xs text-gray-500">Target: 30</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-full">
              <TrendingUp className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Revenue</p>
              <p className="text-2xl font-bold text-green-600">$87.50</p>
              <p className="text-xs text-green-500">+12% today</p>
            </div>
            <div className="p-3 bg-green-100 rounded-full">
              <Users className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Platform Performance Chart */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Platform Performance</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={performanceData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="platform" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="views" fill="#8884d8" name="Views" />
            <Bar dataKey="engagement" fill="#82ca9d" name="Engagement Rate (%)" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Daily Metrics Trend */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Weekly Trends</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={dailyMetrics}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="day" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="youtube" stroke="#FF0000" strokeWidth={2} name="YouTube" />
            <Line type="monotone" dataKey="tiktok" stroke="#000000" strokeWidth={2} name="TikTok" />
            <Line type="monotone" dataKey="facebook" stroke="#1877F2" strokeWidth={2} name="Facebook" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );

  const PlatformsTab = () => (
    <div className="space-y-6">
      {/* Platform Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {Object.entries(platforms).map(([platform, config]) => (
          <div key={platform} className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className={`w-3 h-3 rounded-full ${config.status === 'active' ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <h3 className="text-lg font-semibold capitalize">{platform}</h3>
              </div>
              <button
                onClick={() => setPlatforms(prev => ({
                  ...prev,
                  [platform]: { ...prev[platform], enabled: !prev[platform].enabled }
                }))}
                className={`px-3 py-1 rounded text-sm font-medium ${
                  config.enabled ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                }`}
              >
                {config.enabled ? 'Enabled' : 'Disabled'}
              </button>
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Daily Quota:</span>
                <span className="text-sm font-medium">{config.used}/{config.dailyQuota}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${platform === 'youtube' ? 'bg-red-500' : platform === 'tiktok' ? 'bg-black' : 'bg-blue-500'}`}
                  style={{ width: `${(config.used / config.dailyQuota) * 100}%` }}
                ></div>
              </div>
              <div className="flex justify-between text-xs text-gray-500">
                <span>{Math.round((config.used / config.dailyQuota) * 100)}% used</span>
                <span>{config.dailyQuota - config.used} remaining</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Platform Settings */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Platform Configuration</h3>
        
        <div className="space-y-4">
          {Object.entries(platforms).map(([platform, config]) => (
            <div key={platform} className="border rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-medium capitalize">{platform} Settings</h4>
                <Settings className="h-4 w-4 text-gray-500" />
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <label className="block text-gray-600">Daily Limit:</label>
                  <input 
                    type="number" 
                    value={config.dailyQuota}
                    className="mt-1 w-full px-2 py-1 border rounded"
                    onChange={(e) => setPlatforms(prev => ({
                      ...prev,
                      [platform]: { ...prev[platform], dailyQuota: parseInt(e.target.value) }
                    }))}
                  />
                </div>
                <div>
                  <label className="block text-gray-600">Priority:</label>
                  <select className="mt-1 w-full px-2 py-1 border rounded">
                    <option>High</option>
                    <option>Medium</option>
                    <option>Low</option>
                  </select>
                </div>
                <div>
                  <label className="block text-gray-600">Schedule:</label>
                  <select className="mt-1 w-full px-2 py-1 border rounded">
                    <option>Auto</option>
                    <option>Peak Hours</option>
                    <option>Custom</option>
                  </select>
                </div>
                <div>
                  <label className="block text-gray-600">Quality:</label>
                  <select className="mt-1 w-full px-2 py-1 border rounded">
                    <option>High</option>
                    <option>Medium</option>
                    <option>Fast</option>
                  </select>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const ContentTab = () => (
    <div className="space-y-6">
      {/* Content Queue */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Content Queue</h3>
        
        <div className="space-y-3">
          {contentQueue.map((item) => (
            <div key={item.id} className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center space-x-4">
                <div className={`w-3 h-3 rounded-full ${
                  item.status === 'processing' ? 'bg-yellow-500' : 
                  item.status === 'optimizing' ? 'bg-blue-500' :
                  item.status === 'scheduled' ? 'bg-purple-500' : 'bg-green-500'
                }`}></div>
                
                <div>
                  <h4 className="font-medium">{item.topic}</h4>
                  <p className="text-sm text-gray-600 capitalize">{item.status}</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-4">
                <div className="flex space-x-1">
                  {item.platforms.map(platform => (
                    <div 
                      key={platform}
                      className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white`}
                      style={{ backgroundColor: platformColors[platform] }}
                    >
                      {platform.charAt(0).toUpperCase()}
                    </div>
                  ))}
                </div>
                
                <span className="text-sm text-gray-500">{item.eta}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Content Performance */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Recent Content Performance</h3>
        
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2">Content</th>
                <th className="text-left py-2">Platform</th>
                <th className="text-center py-2">Views</th>
                <th className="text-center py-2">Engagement</th>
                <th className="text-center py-2">Revenue</th>
                <th className="text-center py-2">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b">
                <td className="py-2">AI Breakthroughs 2025</td>
                <td className="py-2">
                  <span className="inline-block w-3 h-3 bg-red-500 rounded-full mr-2"></span>
                  YouTube
                </td>
                <td className="text-center py-2">15.4K</td>
                <td className="text-center py-2">8.5%</td>
                <td className="text-center py-2">$45.20</td>
                <td className="text-center py-2">
                  <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">Live</span>
                </td>
              </tr>
              <tr className="border-b">
                <td className="py-2">Climate Solutions</td>
                <td className="py-2">
                  <span className="inline-block w-3 h-3 bg-black rounded-full mr-2"></span>
                  TikTok
                </td>
                <td className="text-center py-2">89.7K</td>
                <td className="text-center py-2">12.3%</td>
                <td className="text-center py-2">$23.80</td>
                <td className="text-center py-2">
                  <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">Live</span>
                </td>
              </tr>
              <tr className="border-b">
                <td className="py-2">Space Technology</td>
                <td className="py-2">
                  <span className="inline-block w-3 h-3 bg-blue-500 rounded-full mr-2"></span>
                  Facebook
                </td>
                <td className="text-center py-2">32.1K</td>
                <td className="text-center py-2">6.8%</td>
                <td className="text-center py-2">$18.50</td>
                <td className="text-center py-2">
                  <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded text-xs">Processing</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const AnalyticsTab = () => (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-lg p-4 text-center">
          <Eye className="h-8 w-8 text-blue-500 mx-auto mb-2" />
          <p className="text-2xl font-bold">137.3K</p>
          <p className="text-sm text-gray-600">Total Views</p>
          <p className="text-xs text-green-500">+15% this week</p>
        </div>
        
        <div className="bg-white rounded-lg shadow-lg p-4 text-center">
          <ThumbsUp className="h-8 w-8 text-green-500 mx-auto mb-2" />
          <p className="text-2xl font-bold">9.2%</p>
          <p className="text-sm text-gray-600">Avg Engagement</p>
          <p className="text-xs text-green-500">+2.1% this week</p>
        </div>
        
        <div className="bg-white rounded-lg shadow-lg p-4 text-center">
          <Share className="h-8 w-8 text-purple-500 mx-auto mb-2" />
          <p className="text-2xl font-bold">2.8K</p>
          <p className="text-sm text-gray-600">Total Shares</p>
          <p className="text-xs text-green-500">+8% this week</p>
        </div>
        
        <div className="bg-white rounded-lg shadow-lg p-4 text-center">
          <MessageCircle className="h-8 w-8 text-orange-500 mx-auto mb-2" />
          <p className="text-2xl font-bold">1.2K</p>
          <p className="text-sm text-gray-600">Comments</p>
          <p className="text-xs text-green-500">+12% this week</p>
        </div>
      </div>

      {/* Platform Distribution */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Views by Platform</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={performanceData}
                cx="50%"
                cy="50%"
                outerRadius={80}
                fill="#8884d8"
                dataKey="views"
                label={({name, percent}) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {performanceData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Revenue by Platform</h3>
          <div className="space-y-4">
            {performanceData.map((platform, index) => (
              <div key={platform.platform} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div 
                    className="w-4 h-4 rounded-full"
                    style={{ backgroundColor: COLORS[index] }}
                  ></div>
                  <span className="font-medium">{platform.platform}</span>
                </div>
                <div className="text-right">
                  <p className="font-bold">${platform.revenue}</p>
                  <p className="text-sm text-gray-600">{platform.engagement}% eng.</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Optimization Recommendations */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold mb-4">AI Optimization Recommendations</h3>
        
        <div className="space-y-3">
          <div className="p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500">
            <h4 className="font-medium text-blue-900">TikTok Optimization</h4>
            <p className="text-sm text-blue-700">Consider posting at 7-9 PM EST for 23% higher engagement based on audience analysis.</p>
          </div>
          
          <div className="p-4 bg-green-50 rounded-lg border-l-4 border-green-500">
            <h4 className="font-medium text-green-900">Content Strategy</h4>
            <p className="text-sm text-green-700">AI-focused content performs 34% better across all platforms. Increase AI topic frequency.</p>
          </div>
          
          <div className="p-4 bg-yellow-50 rounded-lg border-l-4 border-yellow-500">
            <h4 className="font-medium text-yellow-900">YouTube Shorts</h4>
            <p className="text-sm text-yellow-700">45-second videos have optimal retention. Consider extending current 30-second format.</p>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Omnichannel Content Hub</h1>
              <p className="text-sm text-gray-600">YouTube • TikTok • Facebook Distribution</p>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setIsRunning(!isRunning)}
                className={`px-4 py-2 rounded-lg font-medium ${
                  isRunning 
                    ? 'bg-red-100 text-red-700 hover:bg-red-200' 
                    : 'bg-green-100 text-green-700 hover:bg-green-200'
                }`}
              >
                {isRunning ? '⏸️ Pause System' : '▶️ Start System'}
              </button>
              
              <div className="text-right">
                <p className="text-sm font-medium">Daily Revenue</p>
                <p className="text-lg font-bold text-green-600">$87.50</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'overview', name: 'Overview' },
              { id: 'platforms', name: 'Platforms' },
              { id: 'content', name: 'Content' },
              { id: 'analytics', name: 'Analytics' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.name}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && <OverviewTab />}
        {activeTab === 'platforms' && <PlatformsTab />}
        {activeTab === 'content' && <ContentTab />}
        {activeTab === 'analytics' && <AnalyticsTab />}
      </div>
    </div>
  );
};

export default OmnichannelDashboard;