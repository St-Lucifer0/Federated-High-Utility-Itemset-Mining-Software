import React, { useState } from 'react';
import { Download, Filter, Search, Calendar, AlertCircle, CheckCircle, Activity, Upload } from 'lucide-react';

interface LogsTabProps {
  clientData: any;
  setClientData: (data: any) => void;
}

const LogsTab: React.FC<LogsTabProps> = ({ clientData }) => {
  const [filterType, setFilterType] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedLog, setSelectedLog] = useState<any>(null);

  const logs = clientData.logs || [];

  const getLogIcon = (type: string) => {
    switch (type) {
      case 'upload':
        return <Upload className="h-4 w-4 text-blue-600" />;
      case 'mining':
        return <Activity className="h-4 w-4 text-green-600" />;
      case 'federated_contribution':
        return <CheckCircle className="h-4 w-4 text-purple-600" />;
      case 'manual_entry':
        return <Activity className="h-4 w-4 text-orange-600" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-600" />;
      default:
        return <Activity className="h-4 w-4 text-gray-600" />;
    }
  };

  const getLogColor = (type: string) => {
    switch (type) {
      case 'upload':
        return 'bg-blue-50 border-blue-200';
      case 'mining':
        return 'bg-green-50 border-green-200';
      case 'federated_contribution':
        return 'bg-purple-50 border-purple-200';
      case 'manual_entry':
        return 'bg-orange-50 border-orange-200';
      case 'error':
        return 'bg-red-50 border-red-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  const filteredLogs = logs
    .filter(log => filterType === 'all' || log.type === filterType)
    .filter(log => 
      searchTerm === '' || 
      log.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.type.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

  const exportLogs = () => {
    const csvContent = [
      'Timestamp,Type,Message,Details',
      ...filteredLogs.map(log => [
        log.timestamp.toISOString(),
        log.type,
        `"${log.message}"`,
        `"${JSON.stringify(log.details || {})}"`
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `client_logs_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  if (logs.length === 0) {
    return (
      <div className="text-center py-12">
        <Activity className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-4 text-lg font-medium text-gray-900">No logs available</h3>
        <p className="mt-2 text-gray-500">
          Activity logs will appear here as you use the application
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Logs Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-blue-600">
            {logs.filter(l => l.type === 'upload').length}
          </div>
          <div className="text-sm text-blue-900">Uploads</div>
        </div>
        
        <div className="bg-green-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-green-600">
            {logs.filter(l => l.type === 'mining').length}
          </div>
          <div className="text-sm text-green-900">Mining Jobs</div>
        </div>
        
        <div className="bg-purple-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-purple-600">
            {logs.filter(l => l.type === 'federated_contribution').length}
          </div>
          <div className="text-sm text-purple-900">FL Contributions</div>
        </div>
        
        <div className="bg-red-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-red-600">
            {logs.filter(l => l.type === 'error').length}
          </div>
          <div className="text-sm text-red-900">Errors</div>
        </div>
      </div>

      {/* Controls */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
          <div className="flex items-center space-x-2">
            <Search className="h-4 w-4 text-gray-500" />
            <input
              type="text"
              placeholder="Search logs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            />
          </div>
          
          <div className="flex items-center space-x-2">
            <Filter className="h-4 w-4 text-gray-500" />
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            >
              <option value="all">All Types</option>
              <option value="upload">Uploads</option>
              <option value="mining">Mining</option>
              <option value="federated_contribution">FL Contributions</option>
              <option value="manual_entry">Manual Entry</option>
              <option value="error">Errors</option>
            </select>
          </div>
        </div>
        
        <button
          onClick={exportLogs}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm"
        >
          <Download className="h-4 w-4 mr-2" />
          Export Logs
        </button>
      </div>

      {/* Logs List */}
      <div className="space-y-3">
        {filteredLogs.map((log) => (
          <div
            key={log.id}
            className={`border rounded-lg p-4 cursor-pointer hover:shadow-md transition-all duration-200 ${getLogColor(log.type)}`}
            onClick={() => setSelectedLog(log)}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-3">
                {getLogIcon(log.type)}
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <span className="font-medium text-gray-900 capitalize">
                      {log.type.replace('_', ' ')}
                    </span>
                    <span className="text-xs text-gray-500">
                      {log.timestamp.toLocaleString()}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 mt-1">{log.message}</p>
                </div>
              </div>
              <Calendar className="h-4 w-4 text-gray-400" />
            </div>
          </div>
        ))}
      </div>

      {filteredLogs.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No logs match the current filters
        </div>
      )}

      {/* Log Detail Modal */}
      {selectedLog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Log Details</h3>
              <button
                onClick={() => setSelectedLog(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="text-sm font-medium text-gray-700">Type:</span>
                  <div className="flex items-center mt-1">
                    {getLogIcon(selectedLog.type)}
                    <span className="ml-2 capitalize">{selectedLog.type.replace('_', ' ')}</span>
                  </div>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-700">Timestamp:</span>
                  <div className="mt-1">{selectedLog.timestamp.toLocaleString()}</div>
                </div>
              </div>
              
              <div>
                <span className="text-sm font-medium text-gray-700">Message:</span>
                <div className="mt-1 p-3 bg-gray-50 rounded-md">{selectedLog.message}</div>
              </div>
              
              {selectedLog.details && (
                <div>
                  <span className="text-sm font-medium text-gray-700">Details:</span>
                  <div className="mt-1 p-3 bg-gray-50 rounded-md">
                    <pre className="text-sm text-gray-800 whitespace-pre-wrap">
                      {JSON.stringify(selectedLog.details, null, 2)}
                    </pre>
                  </div>
                </div>
              )}
            </div>
            
            <div className="mt-6 flex justify-end">
              <button
                onClick={() => setSelectedLog(null)}
                className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LogsTab;