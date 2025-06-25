import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Label } from '../ui/label';
import { 
  Users, 
  Plus, 
  Edit, 
  Shield, 
  Database, 
  Globe, 
  Brain, 
  Sparkles,
  Target,
  Zap,
  AlertCircle,
  TrendingUp,
  Activity,
  Settings,
  Search,
  Crown,
  User
} from 'lucide-react';
import { Alert, AlertDescription } from '../ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Progress } from '../ui/progress';
import { SophiaUniversalChatInterface } from '../shared/SophiaUniversalChatInterface';

interface UserProfile {
  user_id: string;
  name: string;
  email: string;
  access_level: string;
  department: string;
  accessible_schemas: string[];
  search_permissions: string[];
  preferred_personality: string;
  api_quota_daily: number;
  api_usage_today: number;
  usage_percentage: number;
  created_at: string;
  last_active: string;
  custom_context: Record<string, any>;
}

interface UserAnalytics {
  total_users: number;
  total_api_usage_today: number;
  user_breakdown_by_level: Record<string, number>;
  active_users_today: number;
}

interface CreateUserFormData {
  user_id: string;
  name: string;
  email: string;
  access_level: string;
  department: string;
  search_permissions: string[];
  preferred_personality: string;
  api_quota_daily: number;
}

const ACCESS_LEVELS = [
  { value: 'employee', label: 'Employee', icon: User, color: 'bg-gray-500' },
  { value: 'manager', label: 'Manager', icon: Users, color: 'bg-blue-500' },
  { value: 'executive', label: 'Executive', icon: Shield, color: 'bg-purple-500' },
  { value: 'ceo', label: 'CEO', icon: Crown, color: 'bg-gold-500' }
];

const PERSONALITIES = [
  { value: 'executive_advisor', label: 'Executive Advisor', icon: Target },
  { value: 'friendly_assistant', label: 'Friendly Assistant', icon: Sparkles },
  { value: 'technical_expert', label: 'Technical Expert', icon: Brain },
  { value: 'creative_collaborator', label: 'Creative Collaborator', icon: Zap },
  { value: 'professional_consultant', label: 'Professional Consultant', icon: Shield }
];

const SEARCH_PERMISSIONS = [
  { value: 'internal_only', label: 'Internal Only', icon: Database, description: 'Access to internal company data only' },
  { value: 'internet_only', label: 'Internet Only', icon: Globe, description: 'Access to internet sources only' },
  { value: 'blended_intelligence', label: 'Blended Intelligence', icon: Brain, description: 'Combine internal and internet intelligence' },
  { value: 'ceo_deep_research', label: 'CEO Deep Research', icon: Search, description: 'Advanced research with scraping (CEO only)' }
];

export const CEOUserManagementDashboard: React.FC = () => {
  const [users, setUsers] = useState<UserProfile[]>([]);
  const [analytics, setAnalytics] = useState<UserAnalytics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedUser, setSelectedUser] = useState<UserProfile | null>(null);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState('overview');

  // Form state for creating/editing users
  const [formData, setFormData] = useState<CreateUserFormData>({
    user_id: '',
    name: '',
    email: '',
    access_level: 'employee',
    department: '',
    search_permissions: ['internal_only'],
    preferred_personality: 'friendly_assistant',
    api_quota_daily: 1000
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load users and analytics in parallel
      const [usersResponse, analyticsResponse] = await Promise.all([
        fetch('/api/v1/sophia/users'),
        fetch('/api/v1/sophia/analytics/users')
      ]);

      if (usersResponse.ok) {
        const usersData = await usersResponse.json();
        setUsers(usersData.users || []);
      }

      if (analyticsResponse.ok) {
        const analyticsData = await analyticsResponse.json();
        setAnalytics(analyticsData.analytics);
      }

    } catch (err) {
      console.error('Failed to load data:', err);
      setError('Failed to load user management data');
    } finally {
      setLoading(false);
    }
  };

  const createUser = async () => {
    try {
      setError(null);

      const response = await fetch('/api/v1/sophia/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        throw new Error('Failed to create user');
      }

      const result = await response.json();
      
      if (result.success) {
        await loadData();
        setShowCreateDialog(false);
        resetForm();
      } else {
        throw new Error(result.message || 'Failed to create user');
      }

    } catch (err) {
      console.error('Failed to create user:', err);
      setError(err instanceof Error ? err.message : 'Failed to create user');
    }
  };

  const updateUserPermissions = async (userId: string, updates: Partial<CreateUserFormData>) => {
    try {
      setError(null);

      const response = await fetch(`/api/v1/sophia/users/${userId}/permissions`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      });

      if (!response.ok) {
        throw new Error('Failed to update user permissions');
      }

      const result = await response.json();
      
      if (result.success) {
        await loadData();
        setShowEditDialog(false);
        setSelectedUser(null);
      } else {
        throw new Error(result.message || 'Failed to update user');
      }

    } catch (err) {
      console.error('Failed to update user:', err);
      setError(err instanceof Error ? err.message : 'Failed to update user');
    }
  };

  const resetForm = () => {
    setFormData({
      user_id: '',
      name: '',
      email: '',
      access_level: 'employee',
      department: '',
      search_permissions: ['internal_only'],
      preferred_personality: 'friendly_assistant',
      api_quota_daily: 1000
    });
  };

  const filteredUsers = users.filter(user =>
    user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.department.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getAccessLevelConfig = (level: string) => {
    return ACCESS_LEVELS.find(l => l.value === level) || ACCESS_LEVELS[0];
  };

  const getPersonalityConfig = (personality: string) => {
    return PERSONALITIES.find(p => p.value === personality) || PERSONALITIES[0];
  };

  const getUsageColor = (percentage: number) => {
    if (percentage >= 90) return 'text-red-600';
    if (percentage >= 75) return 'text-yellow-600';
    return 'text-green-600';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">User Management</h1>
          <p className="text-gray-600">Manage Sophia AI user access and permissions</p>
        </div>
        <Button onClick={() => setShowCreateDialog(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Add User
        </Button>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Analytics Overview */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-2">
                <Users className="h-5 w-5 text-blue-500" />
                <div>
                  <p className="text-sm text-gray-600">Total Users</p>
                  <p className="text-2xl font-bold">{analytics.total_users}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-2">
                <Activity className="h-5 w-5 text-green-500" />
                <div>
                  <p className="text-sm text-gray-600">Active Today</p>
                  <p className="text-2xl font-bold">{analytics.active_users_today}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-purple-500" />
                <div>
                  <p className="text-sm text-gray-600">API Usage Today</p>
                  <p className="text-2xl font-bold">{analytics.total_api_usage_today}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-2">
                <Crown className="h-5 w-5 text-yellow-500" />
                <div>
                  <p className="text-sm text-gray-600">Executives</p>
                  <p className="text-2xl font-bold">
                    {(analytics.user_breakdown_by_level.executive || 0) + (analytics.user_breakdown_by_level.ceo || 0)}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="overview">User Overview</TabsTrigger>
          <TabsTrigger value="permissions">Permissions Matrix</TabsTrigger>
          <TabsTrigger value="analytics">Usage Analytics</TabsTrigger>
          <TabsTrigger value="sophia-chat">Sophia Console</TabsTrigger>
        </TabsList>

        {/* User Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          {/* Search Bar */}
          <div className="flex items-center gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search users by name, email, or department..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button variant="outline" onClick={loadData} disabled={loading}>
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            </Button>
          </div>

          {/* Users Table */}
          <Card>
            <CardHeader>
              <CardTitle>All Users ({filteredUsers.length})</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {filteredUsers.map((user) => {
                  const accessConfig = getAccessLevelConfig(user.access_level);
                  const personalityConfig = getPersonalityConfig(user.preferred_personality);
                  const AccessIcon = accessConfig.icon;
                  const PersonalityIcon = personalityConfig.icon;

                  return (
                    <div key={user.user_id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                      <div className="flex items-center gap-4">
                        <div className={`p-2 rounded-full ${accessConfig.color} text-white`}>
                          <AccessIcon className="h-4 w-4" />
                        </div>
                        
                        <div>
                          <div className="flex items-center gap-2">
                            <h3 className="font-medium">{user.name}</h3>
                            <Badge variant="outline">{accessConfig.label}</Badge>
                          </div>
                          <p className="text-sm text-gray-600">{user.email}</p>
                          <p className="text-xs text-gray-500">{user.department}</p>
                        </div>
                      </div>

                      <div className="text-right space-y-1">
                        <div className="flex items-center gap-2">
                          <PersonalityIcon className="h-3 w-3" />
                          <span className="text-sm">{personalityConfig.label}</span>
                        </div>
                        
                        <div className="flex items-center gap-2">
                          <span className={`text-sm font-medium ${getUsageColor(user.usage_percentage)}`}>
                            {user.api_usage_today}/{user.api_quota_daily}
                          </span>
                          <span className="text-xs text-gray-500">
                            ({Math.round(user.usage_percentage)}%)
                          </span>
                        </div>
                        
                        <Progress value={user.usage_percentage} className="w-20 h-2" />
                      </div>

                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setSelectedUser(user);
                            setFormData({
                              user_id: user.user_id,
                              name: user.name,
                              email: user.email,
                              access_level: user.access_level,
                              department: user.department,
                              search_permissions: user.search_permissions,
                              preferred_personality: user.preferred_personality,
                              api_quota_daily: user.api_quota_daily
                            });
                            setShowEditDialog(true);
                          }}
                        >
                          <Edit className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  );
                })}

                {filteredUsers.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    No users found matching your search.
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Permissions Matrix Tab */}
        <TabsContent value="permissions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Access Level Permissions Matrix</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {ACCESS_LEVELS.map((level) => {
                  const Icon = level.icon;
                  const levelUsers = users.filter(u => u.access_level === level.value);
                  
                  return (
                    <div key={level.value} className="space-y-3">
                      <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-full ${level.color} text-white`}>
                          <Icon className="h-4 w-4" />
                        </div>
                        <h3 className="font-medium">{level.label}</h3>
                        <Badge variant="secondary">{levelUsers.length} users</Badge>
                      </div>
                      
                      <div className="ml-11 space-y-2">
                        <div>
                          <p className="text-sm font-medium">Accessible Schemas:</p>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {levelUsers[0]?.accessible_schemas.map(schema => (
                              <Badge key={schema} variant="outline" className="text-xs">
                                {schema}
                              </Badge>
                            )) || <span className="text-xs text-gray-500">No users at this level</span>}
                          </div>
                        </div>
                        
                        <div>
                          <p className="text-sm font-medium">Search Permissions:</p>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {SEARCH_PERMISSIONS.map(permission => {
                              const hasPermission = levelUsers.some(u => u.search_permissions.includes(permission.value));
                              return (
                                <Badge 
                                  key={permission.value} 
                                  variant={hasPermission ? "default" : "secondary"}
                                  className="text-xs"
                                >
                                  {permission.label}
                                </Badge>
                              );
                            })}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Usage by Access Level</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {ACCESS_LEVELS.map((level) => {
                    const levelUsers = users.filter(u => u.access_level === level.value);
                    const totalUsage = levelUsers.reduce((sum, user) => sum + user.api_usage_today, 0);
                    const totalQuota = levelUsers.reduce((sum, user) => sum + user.api_quota_daily, 0);
                    const usagePercentage = totalQuota > 0 ? (totalUsage / totalQuota) * 100 : 0;
                    
                    const Icon = level.icon;
                    
                    return (
                      <div key={level.value} className="space-y-2">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Icon className="h-4 w-4" />
                            <span className="font-medium">{level.label}</span>
                            <Badge variant="secondary">{levelUsers.length}</Badge>
                          </div>
                          <span className="text-sm font-medium">
                            {totalUsage}/{totalQuota}
                          </span>
                        </div>
                        <Progress value={usagePercentage} className="h-2" />
                        <p className="text-xs text-gray-500">
                          {Math.round(usagePercentage)}% of daily quota used
                        </p>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Personality Preferences</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {PERSONALITIES.map((personality) => {
                    const personalityUsers = users.filter(u => u.preferred_personality === personality.value);
                    const percentage = users.length > 0 ? (personalityUsers.length / users.length) * 100 : 0;
                    
                    const Icon = personality.icon;
                    
                    return (
                      <div key={personality.value} className="space-y-2">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Icon className="h-4 w-4" />
                            <span className="font-medium">{personality.label}</span>
                          </div>
                          <Badge variant="secondary">{personalityUsers.length}</Badge>
                        </div>
                        <Progress value={percentage} className="h-2" />
                        <p className="text-xs text-gray-500">
                          {Math.round(percentage)}% of users prefer this personality
                        </p>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Sophia Chat Console Tab */}
        <TabsContent value="sophia-chat" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Sophia AI Administrative Console</CardTitle>
              <p className="text-sm text-gray-600">
                Chat with Sophia using CEO-level deep research capabilities for user management insights and system administration.
              </p>
            </CardHeader>
            <CardContent>
              <SophiaUniversalChatInterface
                userId="ceo"
                height="500px"
                showAdvancedControls={true}
                className="border-0 shadow-none"
              />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Create User Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Create New User</DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="user_id">User ID</Label>
                <Input
                  id="user_id"
                  value={formData.user_id}
                  onChange={(e) => setFormData({...formData, user_id: e.target.value})}
                  placeholder="e.g., john.doe"
                />
              </div>
              
              <div>
                <Label htmlFor="name">Full Name</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  placeholder="John Doe"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  placeholder="john.doe@payready.com"
                />
              </div>
              
              <div>
                <Label htmlFor="department">Department</Label>
                <Input
                  id="department"
                  value={formData.department}
                  onChange={(e) => setFormData({...formData, department: e.target.value})}
                  placeholder="Engineering"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="access_level">Access Level</Label>
                <Select value={formData.access_level} onValueChange={(value) => setFormData({...formData, access_level: value})}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {ACCESS_LEVELS.map((level) => {
                      const Icon = level.icon;
                      return (
                        <SelectItem key={level.value} value={level.value}>
                          <div className="flex items-center gap-2">
                            <Icon className="h-4 w-4" />
                            {level.label}
                          </div>
                        </SelectItem>
                      );
                    })}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="preferred_personality">Preferred Personality</Label>
                <Select value={formData.preferred_personality} onValueChange={(value) => setFormData({...formData, preferred_personality: value})}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {PERSONALITIES.map((personality) => {
                      const Icon = personality.icon;
                      return (
                        <SelectItem key={personality.value} value={personality.value}>
                          <div className="flex items-center gap-2">
                            <Icon className="h-4 w-4" />
                            {personality.label}
                          </div>
                        </SelectItem>
                      );
                    })}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div>
              <Label htmlFor="api_quota">Daily API Quota</Label>
              <Input
                id="api_quota"
                type="number"
                value={formData.api_quota_daily}
                onChange={(e) => setFormData({...formData, api_quota_daily: parseInt(e.target.value) || 1000})}
                min="100"
                max="10000"
                step="100"
              />
            </div>

            <div>
              <Label>Search Permissions</Label>
              <div className="grid grid-cols-2 gap-2 mt-2">
                {SEARCH_PERMISSIONS.map((permission) => {
                  const Icon = permission.icon;
                  const isSelected = formData.search_permissions.includes(permission.value);
                  
                  return (
                    <div
                      key={permission.value}
                      className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                        isSelected ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                      }`}
                      onClick={() => {
                        if (isSelected) {
                          setFormData({
                            ...formData,
                            search_permissions: formData.search_permissions.filter(p => p !== permission.value)
                          });
                        } else {
                          setFormData({
                            ...formData,
                            search_permissions: [...formData.search_permissions, permission.value]
                          });
                        }
                      }}
                    >
                      <div className="flex items-center gap-2">
                        <Icon className="h-4 w-4" />
                        <span className="font-medium">{permission.label}</span>
                      </div>
                      <p className="text-xs text-gray-500 mt-1">{permission.description}</p>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                Cancel
              </Button>
              <Button onClick={createUser} disabled={!formData.user_id || !formData.name || !formData.email}>
                Create User
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Edit User Dialog */}
      <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit User Permissions</DialogTitle>
          </DialogHeader>
          
          {selectedUser && (
            <div className="space-y-4">
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-full ${getAccessLevelConfig(selectedUser.access_level).color} text-white`}>
                    {React.createElement(getAccessLevelConfig(selectedUser.access_level).icon, { className: "h-4 w-4" })}
                  </div>
                  <div>
                    <h3 className="font-medium">{selectedUser.name}</h3>
                    <p className="text-sm text-gray-600">{selectedUser.email}</p>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="edit_access_level">Access Level</Label>
                  <Select value={formData.access_level} onValueChange={(value) => setFormData({...formData, access_level: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {ACCESS_LEVELS.map((level) => {
                        const Icon = level.icon;
                        return (
                          <SelectItem key={level.value} value={level.value}>
                            <div className="flex items-center gap-2">
                              <Icon className="h-4 w-4" />
                              {level.label}
                            </div>
                          </SelectItem>
                        );
                      })}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="edit_personality">Preferred Personality</Label>
                  <Select value={formData.preferred_personality} onValueChange={(value) => setFormData({...formData, preferred_personality: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {PERSONALITIES.map((personality) => {
                        const Icon = personality.icon;
                        return (
                          <SelectItem key={personality.value} value={personality.value}>
                            <div className="flex items-center gap-2">
                              <Icon className="h-4 w-4" />
                              {personality.label}
                            </div>
                          </SelectItem>
                        );
                      })}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div>
                <Label htmlFor="edit_api_quota">Daily API Quota</Label>
                <Input
                  id="edit_api_quota"
                  type="number"
                  value={formData.api_quota_daily}
                  onChange={(e) => setFormData({...formData, api_quota_daily: parseInt(e.target.value) || 1000})}
                  min="100"
                  max="10000"
                  step="100"
                />
              </div>

              <div>
                <Label>Search Permissions</Label>
                <div className="grid grid-cols-2 gap-2 mt-2">
                  {SEARCH_PERMISSIONS.map((permission) => {
                    const Icon = permission.icon;
                    const isSelected = formData.search_permissions.includes(permission.value);
                    
                    return (
                      <div
                        key={permission.value}
                        className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                          isSelected ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                        }`}
                        onClick={() => {
                          if (isSelected) {
                            setFormData({
                              ...formData,
                              search_permissions: formData.search_permissions.filter(p => p !== permission.value)
                            });
                          } else {
                            setFormData({
                              ...formData,
                              search_permissions: [...formData.search_permissions, permission.value]
                            });
                          }
                        }}
                      >
                        <div className="flex items-center gap-2">
                          <Icon className="h-4 w-4" />
                          <span className="font-medium">{permission.label}</span>
                        </div>
                        <p className="text-xs text-gray-500 mt-1">{permission.description}</p>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setShowEditDialog(false)}>
                  Cancel
                </Button>
                <Button 
                  onClick={() => updateUserPermissions(selectedUser.user_id, {
                    access_level: formData.access_level,
                    preferred_personality: formData.preferred_personality,
                    api_quota_daily: formData.api_quota_daily,
                    search_permissions: formData.search_permissions
                  })}
                >
                  Update Permissions
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}; 