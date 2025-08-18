import React, { useState, useEffect } from 'react';
import { Users, MapPin, Activity, Clock, Database, AlertTriangle } from 'lucide-react';
import { apiService } from '../../services/api';

interface ClientStatusTabProps {
  serverData: any;
  setServerData: (data: any) => void;
}

const ClientStatusTab: React.FC<ClientStatusTabProps> = ({ serverData, setServerData }) => {
  const [refreshing, setRefreshing] = useState(false);

  const refreshClients = async () => {
    setRefreshing(true);
    try {
      const response = await apiService.getStores();
      setServerData((prev: any) => ({
        ...prev,
        clients: response.stores.map((store: any) => ({
          id: store.id,
          name: store.name,
          location: store.location || 'Unknown',
          status: store.connection_status === 'active' ? 'active' : 'inactive',
          lastSeen: store.last_seen ? new Date(store.last_seen) : new Date(),
          transactionCount: store.transaction_count || 0,
          patternsSent: store.mining_jobs_count || 0,
          ipAddress: store.ip_address || 'Unknown'
        }))
      }));
    } catch (error) {
      console.error('Failed to refresh clients:', error);
    } finally {
      setRefreshing(false);
    }
  };

  // Load clients on component mount and set up auto-refresh
  useEffect(() => {
    refreshClients();
    
    // Auto-refresh every 10 seconds for real-time updates
    const interval = setInterval(refreshClients, 10000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'mining':
        return 'bg-blue-100 text-blue-800';
      case 'inactive':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-red-100 text-red-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <Activity className="h-4 w-4 text-green-600" />;
      case 'mining':
        return <Database className="h-4 w-4 text-blue-600 animate-pulse" />;
      case 'inactive':
        return <Clock className="h-4 w-4 text-gray-600" />;
      default:
        return <AlertTriangle className="h-4 w-4 text-red-600" />;
    }
  };

  const getTimeSince = (date: Date) => {
    const seconds = Math.floor((new Date().getTime() - date.getTime()) / 1000);
    
    if (seconds < 60) return `${seconds}s ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  };

  const activeClients = serverData.clients.filter((c: any) => c.status === 'active' || c.status === 'mining');
  const totalTransactions = serverData.clients.reduce((sum: number, c: any) => sum + c.transactionCount, 0);
  const totalPatterns = serverData.clients.reduce((sum: number, c: any) => sum + c.patternsSent, 0);

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="flex items-center">
            <Users className="h-5 w-5 text-blue-600 mr-2" />
            <span className="text-sm font-medium text-blue-900">Active Clients</span>
          </div>
          <div className="text-2xl font-bold text-blue-600 mt-1">
            {activeClients.length}
          </div>
        </div>
        
        <div className="bg-green-50 p-4 rounded-lg">
          <div className="flex items-center">
            <Database className="h-5 w-5 text-green-600 mr-2" />
            <span className="text-sm font-medium text-green-900">Total Transactions</span>
          </div>
          <div className="text-2xl font-bold text-green-600 mt-1">
            {totalTransactions.toLocaleString()}
          </div>
        </div>
        
        <div className="bg-purple-50 p-4 rounded-lg">
          <div className="flex items-center">
            <Activity className="h-5 w-5 text-purple-600 mr-2" />
            <span className="text-sm font-medium text-purple-900">Patterns Received</span>
          </div>
          <div className="text-2xl font-bold text-purple-600 mt-1">
            {totalPatterns}
          </div>
        </div>
        
        <div className="bg-orange-50 p-4 rounded-lg">
          <div className="flex items-center">
            <Clock className="h-5 w-5 text-orange-600 mr-2" />
            <span className="text-sm font-medium text-orange-900">System Uptime</span>
          </div>
          <div className="text-2xl font-bold text-orange-600 mt-1">
            {Math.floor((Date.now() - serverData.systemUptime) / (1000 * 60 * 60))}h
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-900">Connected Clients</h3>
        <button
          onClick={refreshClients}
          disabled={refreshing}
          className={`flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            refreshing
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          <Activity className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
          {refreshing ? 'Refreshing...' : 'Refresh Status'}
        </button>
      </div>

      {/* Clients Table */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Client
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Location
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Seen
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Transactions
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Patterns Sent
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {serverData.clients.map((client: any) => (
                <tr key={client.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10">
                        <div className="h-10 w-10 rounded-full bg-gradient-to-r from-blue-400 to-blue-600 flex items-center justify-center">
                          <span className="text-white font-medium text-sm">
                            {client.name.split(' ').map((n: string) => n[0]).join('')}
                          </span>
                        </div>
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">{client.name}</div>
                        <div className="text-sm text-gray-500">{client.id}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {getStatusIcon(client.status)}
                      <span className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(client.status)}`}>
                        {client.status}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div className="flex items-center">
                      <MapPin className="h-4 w-4 text-gray-400 mr-1" />
                      {client.location}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {getTimeSince(client.lastSeen)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {client.transactionCount.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div className="flex items-center">
                      <span className="text-lg font-bold text-blue-600">{client.patternsSent}</span>
                      <span className="ml-1 text-xs text-gray-500">patterns</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button className="text-blue-600 hover:text-blue-900 mr-3">
                      View Details
                    </button>
                    <button className="text-red-600 hover:text-red-900">
                      Disconnect
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Client Activity Timeline */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h4>
        <div className="space-y-3">
          {serverData.clients
            .sort((a: any, b: any) => b.lastSeen.getTime() - a.lastSeen.getTime())
            .slice(0, 5)
            .map((client: any, index: number) => (
              <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-md">
                {getStatusIcon(client.status)}
                <div className="flex-1">
                  <span className="text-sm font-medium text-gray-900">{client.name}</span>
                  <span className="text-sm text-gray-500 ml-2">
                    {client.status === 'mining' ? 'is currently mining patterns' :
                     client.status === 'active' ? 'is connected and ready' :
                     'went offline'}
                  </span>
                </div>
                <span className="text-xs text-gray-500">{getTimeSince(client.lastSeen)}</span>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
};

export default ClientStatusTab;