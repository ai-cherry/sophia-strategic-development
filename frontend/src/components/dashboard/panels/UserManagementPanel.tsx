import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Users, 
  UserPlus, 
  Shield, 
  Activity, 
  Settings, 
  Mail, 
  Calendar,
  AlertTriangle,
  CheckCircle,
  Clock,
  Search,
  Filter,
  MoreVertical,
  Edit,
  Trash2,
  Key,
  Bell
} from 'lucide-react';

interface User {
  id: string;
  name: string;
  email: string;
  role: 'CEO' | 'CPO' | 'VP_Strategic' | 'Admin' | 'Manager' | 'User';
  status: 'active' | 'invited' | 'inactive' | 'suspended';
  lastLogin: string;
  createdAt: string;
  permissions: string[];
  department?: string;
}

interface UserActivity {
  id: string;
  userId: string;
  userName: string;
  action: string;
  resource: string;
  timestamp: string;
  ipAddress: string;
  status: 'success' | 'failed' | 'warning';
}

interface InviteUserData {
  name: string;
  email: string;
  role: string;
  department: string;
}

const UserManagementPanel: React.FC = () => {
  const [activeTab, setActiveTab] = useState('users');
  const [users, setUsers] = useState<User[]>([]);
  const [activities, setActivities] = useState<UserActivity[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterRole, setFilterRole] = useState('all');
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [inviteData, setInviteData] = useState<InviteUserData>({
    name: '',
    email: '',
    role: 'Admin',
    department: ''
  });

  // Mock data for initial display
  useEffect(() => {
    setUsers([
      {
        id: '1',
        name: 'Lynn Patrick Musil',
        email: 'lynn@payready.com',
        role: 'CEO',
        status: 'active',
        lastLogin: '2025-01-12T10:30:00Z',
        createdAt: '2025-01-01T00:00:00Z',
        permissions: ['*'],
        department: 'Executive'
      },
      {
        id: '2',
        name: 'Tiffany York',
        email: 'tiffany@payready.com',
        role: 'CPO',
        status: 'active',
        lastLogin: '2025-01-12T09:15:00Z',
        createdAt: '2025-01-01T00:00:00Z',
        permissions: ['*'],
        department: 'Product'
      },
      {
        id: '3',
        name: 'Steve Gabel',
        email: 'steve@payready.com',
        role: 'VP_Strategic',
        status: 'active',
        lastLogin: '2025-01-12T08:45:00Z',
        createdAt: '2025-01-01T00:00:00Z',
        permissions: ['*'],
        department: 'Strategy'
      }
    ]);

    setActivities([
      {
        id: '1',
        userId: '1',
        userName: 'Lynn Patrick Musil',
        action: 'Dashboard Access',
        resource: 'Strategic Overview',
        timestamp: '2025-01-12T10:30:00Z',
        ipAddress: '192.168.1.100',
        status: 'success'
      },
      {
        id: '2',
        userId: '2',
        userName: 'Tiffany York',
        action: 'MCP Query',
        resource: 'Asana Product Health',
        timestamp: '2025-01-12T09:15:00Z',
        ipAddress: '192.168.1.101',
        status: 'success'
      },
      {
        id: '3',
        userId: '3',
        userName: 'Steve Gabel',
        action: 'Strategic Analysis',
        resource: 'Cross-Platform Intelligence',
        timestamp: '2025-01-12T08:45:00Z',
        ipAddress: '192.168.1.102',
        status: 'success'
      }
    ]);
  }, []);

  const handleInviteUser = async () => {
    try {
      // TODO: Implement actual API call
      const newUser: User = {
        id: Date.now().toString(),
        name: inviteData.name,
        email: inviteData.email,
        role: inviteData.role as any,
        status: 'invited',
        lastLogin: 'Never',
        createdAt: new Date().toISOString(),
        permissions: ['*'], // Start with full permissions as requested
        department: inviteData.department
      };
      
      setUsers(prev => [...prev, newUser]);
      setShowInviteModal(false);
      setInviteData({ name: '', email: '', role: 'Admin', department: '' });
    } catch (error) {
      console.error('Failed to invite user:', error);
    }
  };

  const getRoleColor = (role: string) => {
    const colors = {
      'CEO': 'bg-purple-100 text-purple-800',
      'CPO': 'bg-blue-100 text-blue-800',
      'VP_Strategic': 'bg-green-100 text-green-800',
      'Admin': 'bg-red-100 text-red-800',
      'Manager': 'bg-yellow-100 text-yellow-800',
      'User': 'bg-gray-100 text-gray-800'
    };
    return colors[role] || colors['User'];
  };

  const getStatusColor = (status: string) => {
    const colors = {
      'active': 'bg-green-100 text-green-800',
      'invited': 'bg-yellow-100 text-yellow-800',
      'inactive': 'bg-gray-100 text-gray-800',
      'suspended': 'bg-red-100 text-red-800'
    };
    return colors[status] || colors['inactive'];
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = filterRole === 'all' || user.role === filterRole;
    return matchesSearch && matchesRole;
  });

  const userStats = {
    total: users.length,
    active: users.filter(u => u.status === 'active').length,
    invited: users.filter(u => u.status === 'invited').length,
    inactive: users.filter(u => u.status === 'inactive').length
  };

  return (
    <div className="space-y-6">
      {/* Header with Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Users className="h-5 w-5 text-blue-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">Total Users</p>
                <p className="text-2xl font-bold text-gray-900">{userStats.total}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">Active Users</p>
                <p className="text-2xl font-bold text-green-600">{userStats.active}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Clock className="h-5 w-5 text-yellow-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">Pending Invites</p>
                <p className="text-2xl font-bold text-yellow-600">{userStats.invited}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Shield className="h-5 w-5 text-purple-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">Admin Users</p>
                <p className="text-2xl font-bold text-purple-600">3</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="users">Users</TabsTrigger>
          <TabsTrigger value="roles">Roles & Permissions</TabsTrigger>
          <TabsTrigger value="activity">Activity Log</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        {/* Users Tab */}
        <TabsContent value="users" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  User Management
                </CardTitle>
                <Button onClick={() => setShowInviteModal(true)} className="flex items-center gap-2">
                  <UserPlus className="h-4 w-4" />
                  Invite User
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {/* Search and Filter */}
              <div className="flex flex-col sm:flex-row gap-4 mb-4">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Search users..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
                                 <select
                   value={filterRole}
                   onChange={(e) => setFilterRole(e.target.value)}
                   className="px-3 py-2 border border-gray-300 rounded-md bg-white"
                   aria-label="Filter users by role"
                 >
                  <option value="all">All Roles</option>
                  <option value="CEO">CEO</option>
                  <option value="CPO">CPO</option>
                  <option value="VP_Strategic">VP Strategic</option>
                  <option value="Admin">Admin</option>
                  <option value="Manager">Manager</option>
                  <option value="User">User</option>
                </select>
              </div>

              {/* Users Table */}
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-3 px-4 font-medium text-gray-600">User</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Role</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Status</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Last Login</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Department</th>
                      <th className="text-right py-3 px-4 font-medium text-gray-600">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredUsers.map((user) => (
                      <tr key={user.id} className="border-b hover:bg-gray-50">
                        <td className="py-3 px-4">
                          <div>
                            <div className="font-medium text-gray-900">{user.name}</div>
                            <div className="text-sm text-gray-500">{user.email}</div>
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          <Badge className={getRoleColor(user.role)}>
                            {user.role.replace('_', ' ')}
                          </Badge>
                        </td>
                        <td className="py-3 px-4">
                          <Badge className={getStatusColor(user.status)}>
                            {user.status}
                          </Badge>
                        </td>
                        <td className="py-3 px-4 text-sm text-gray-600">
                          {user.lastLogin === 'Never' ? 'Never' : new Date(user.lastLogin).toLocaleDateString()}
                        </td>
                        <td className="py-3 px-4 text-sm text-gray-600">{user.department}</td>
                        <td className="py-3 px-4 text-right">
                          <Button variant="ghost" size="sm">
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Roles & Permissions Tab */}
        <TabsContent value="roles" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Roles & Permissions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {['CEO', 'CPO', 'VP_Strategic', 'Admin', 'Manager', 'User'].map((role) => (
                    <Card key={role} className="border">
                      <CardContent className="p-4">
                        <h3 className="font-medium text-gray-900 mb-2">{role.replace('_', ' ')}</h3>
                        <div className="space-y-2">
                          <div className="flex items-center gap-2">
                            <CheckCircle className="h-4 w-4 text-green-600" />
                            <span className="text-sm">Dashboard Access</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <CheckCircle className="h-4 w-4 text-green-600" />
                            <span className="text-sm">Strategic Overview</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <CheckCircle className="h-4 w-4 text-green-600" />
                            <span className="text-sm">MCP Server Access</span>
                          </div>
                          {['CEO', 'CPO', 'VP_Strategic', 'Admin'].includes(role) && (
                            <div className="flex items-center gap-2">
                              <CheckCircle className="h-4 w-4 text-green-600" />
                              <span className="text-sm">User Management</span>
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Activity Log Tab */}
        <TabsContent value="activity" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                User Activity Log
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {activities.map((activity) => (
                  <div key={activity.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center gap-4">
                      <div className={`w-3 h-3 rounded-full ${
                        activity.status === 'success' ? 'bg-green-500' :
                        activity.status === 'failed' ? 'bg-red-500' : 'bg-yellow-500'
                      }`} />
                      <div>
                        <div className="font-medium text-gray-900">{activity.userName}</div>
                        <div className="text-sm text-gray-600">{activity.action} - {activity.resource}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-gray-600">
                        {new Date(activity.timestamp).toLocaleString()}
                      </div>
                      <div className="text-xs text-gray-400">{activity.ipAddress}</div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                User Management Settings
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div>
                  <h3 className="font-medium text-gray-900 mb-2">Security Settings</h3>
                  <div className="space-y-2">
                    <label className="flex items-center gap-2">
                      <input type="checkbox" defaultChecked />
                      <span className="text-sm">Require two-factor authentication</span>
                    </label>
                    <label className="flex items-center gap-2">
                      <input type="checkbox" defaultChecked />
                      <span className="text-sm">Log all user activities</span>
                    </label>
                    <label className="flex items-center gap-2">
                      <input type="checkbox" />
                      <span className="text-sm">Auto-suspend inactive users (90 days)</span>
                    </label>
                  </div>
                </div>

                <div>
                  <h3 className="font-medium text-gray-900 mb-2">Invitation Settings</h3>
                  <div className="space-y-2">
                    <label className="flex items-center gap-2">
                      <input type="checkbox" defaultChecked />
                      <span className="text-sm">Send welcome email to new users</span>
                    </label>
                    <label className="flex items-center gap-2">
                      <input type="checkbox" defaultChecked />
                      <span className="text-sm">Require email verification</span>
                    </label>
                  </div>
                </div>

                <div>
                  <h3 className="font-medium text-gray-900 mb-2">Default Permissions</h3>
                  <p className="text-sm text-gray-600 mb-2">
                    New users will start with full administrative privileges as requested by the executive team.
                  </p>
                  <Badge className="bg-purple-100 text-purple-800">Full Admin Access</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Invite User Modal */}
      {showInviteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Invite New User</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                <Input
                  value={inviteData.name}
                  onChange={(e) => setInviteData(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="Enter full name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
                <Input
                  type="email"
                  value={inviteData.email}
                  onChange={(e) => setInviteData(prev => ({ ...prev, email: e.target.value }))}
                  placeholder="Enter email address"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
                                 <select
                   value={inviteData.role}
                   onChange={(e) => setInviteData(prev => ({ ...prev, role: e.target.value }))}
                   className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white"
                   aria-label="Select user role"
                 >
                  <option value="Admin">Admin</option>
                  <option value="Manager">Manager</option>
                  <option value="User">User</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Department</label>
                <Input
                  value={inviteData.department}
                  onChange={(e) => setInviteData(prev => ({ ...prev, department: e.target.value }))}
                  placeholder="e.g., Engineering, Product, Sales"
                />
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <Button onClick={handleInviteUser} className="flex-1">
                Send Invitation
              </Button>
              <Button variant="outline" onClick={() => setShowInviteModal(false)} className="flex-1">
                Cancel
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserManagementPanel; 