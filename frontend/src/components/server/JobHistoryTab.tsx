import React, { useState } from 'react';
import { History, Download, Calendar, Clock, Users, TrendingUp, CheckCircle, XCircle } from 'lucide-react';

interface JobHistoryTabProps {
  serverData: any;
  setServerData: (data: any) => void;
}

const JobHistoryTab: React.FC<JobHistoryTabProps> = ({ serverData }) => {
  const [selectedTimeframe, setSelectedTimeframe] = useState('all');
  const [sortField, setSortField] = useState('timestamp');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');

  const jobs = serverData.jobHistory || [];

  // TODO: Replace with actual API call to fetch job history
  // const jobs = await apiService.getJobHistory();

  const filterJobsByTimeframe = (jobs: any[]) => {
    const now = new Date();
    const timeframes = {
      'all': () => true,
      '24h': (job: any) => (now.getTime() - job.timestamp.getTime()) <= 24 * 60 * 60 * 1000,
      '7d': (job: any) => (now.getTime() - job.timestamp.getTime()) <= 7 * 24 * 60 * 60 * 1000,
      '30d': (job: any) => (now.getTime() - job.timestamp.getTime()) <= 30 * 24 * 60 * 60 * 1000,
    };
    
    return jobs.filter(timeframes[selectedTimeframe as keyof typeof timeframes]);
  };

  const sortedJobs = filterJobsByTimeframe(jobs).sort((a, b) => {
    const aVal = a[sortField];
    const bVal = b[sortField];
    
    if (sortDirection === 'asc') {
      return aVal > bVal ? 1 : -1;
    } else {
      return aVal < bVal ? 1 : -1;
    }
  });

  const exportJobHistory = () => {
    const csvContent = [
      'Round,Status,Duration_Seconds,Client_Count,Patterns_Found,Timestamp',
      ...sortedJobs.map(job => [
        job.round,
        job.status,
        job.duration.toFixed(2),
        job.clientCount,
        job.patternsFound,
        job.timestamp.toISOString()
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `federated_job_history_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'running':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-600" />;
      default:
        return <Clock className="h-4 w-4 text-blue-600" />;
    }
  };

  const calculateStats = () => {
    const completedJobs = sortedJobs.filter(job => job.status === 'completed');
    const totalPatterns = completedJobs.reduce((sum, job) => sum + job.patternsFound, 0);
    const avgDuration = completedJobs.length > 0 
      ? completedJobs.reduce((sum, job) => sum + job.duration, 0) / completedJobs.length 
      : 0;
    const avgClients = completedJobs.length > 0
      ? completedJobs.reduce((sum, job) => sum + job.clientCount, 0) / completedJobs.length
      : 0;
    
    return { totalPatterns, avgDuration, avgClients, completedJobs: completedJobs.length };
  };

  const stats = calculateStats();

  if (jobs.length === 0) {
    return (
      <div className="text-center py-12">
        <History className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-4 text-lg font-medium text-gray-900">No job history available</h3>
        <p className="mt-2 text-gray-500">
          Federated learning job history will appear here after rounds are completed
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Statistics Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-green-50 p-4 rounded-lg">
          <div className="flex items-center">
            <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
            <span className="text-sm font-medium text-green-900">Completed Jobs</span>
          </div>
          <div className="text-2xl font-bold text-green-600 mt-1">
            {stats.completedJobs}
          </div>
        </div>
        
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="flex items-center">
            <TrendingUp className="h-5 w-5 text-blue-600 mr-2" />
            <span className="text-sm font-medium text-blue-900">Total Patterns</span>
          </div>
          <div className="text-2xl font-bold text-blue-600 mt-1">
            {stats.totalPatterns}
          </div>
        </div>
        
        <div className="bg-purple-50 p-4 rounded-lg">
          <div className="flex items-center">
            <Clock className="h-5 w-5 text-purple-600 mr-2" />
            <span className="text-sm font-medium text-purple-900">Avg Duration</span>
          </div>
          <div className="text-2xl font-bold text-purple-600 mt-1">
            {stats.avgDuration.toFixed(1)}s
          </div>
        </div>
        
        <div className="bg-orange-50 p-4 rounded-lg">
          <div className="flex items-center">
            <Users className="h-5 w-5 text-orange-600 mr-2" />
            <span className="text-sm font-medium text-orange-900">Avg Participants</span>
          </div>
          <div className="text-2xl font-bold text-orange-600 mt-1">
            {stats.avgClients.toFixed(1)}
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Calendar className="h-4 w-4 text-gray-500" />
            <select
              value={selectedTimeframe}
              onChange={(e) => setSelectedTimeframe(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            >
              <option value="all">All Time</option>
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
            </select>
          </div>
          
          <div className="text-sm text-gray-500">
            Showing {sortedJobs.length} of {jobs.length} jobs
          </div>
        </div>
        
        <button
          onClick={exportJobHistory}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm"
        >
          <Download className="h-4 w-4 mr-2" />
          Export History
        </button>
      </div>

      {/* Jobs Table */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th 
                  onClick={() => {
                    setSortField('round');
                    setSortDirection(sortField === 'round' && sortDirection === 'desc' ? 'asc' : 'desc');
                  }}
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                >
                  Round
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th 
                  onClick={() => {
                    setSortField('timestamp');
                    setSortDirection(sortField === 'timestamp' && sortDirection === 'desc' ? 'asc' : 'desc');
                  }}
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                >
                  Started
                </th>
                <th 
                  onClick={() => {
                    setSortField('duration');
                    setSortDirection(sortField === 'duration' && sortDirection === 'desc' ? 'asc' : 'desc');
                  }}
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                >
                  Duration
                </th>
                <th 
                  onClick={() => {
                    setSortField('clientCount');
                    setSortDirection(sortField === 'clientCount' && sortDirection === 'desc' ? 'asc' : 'desc');
                  }}
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                >
                  Participants
                </th>
                <th 
                  onClick={() => {
                    setSortField('patternsFound');
                    setSortDirection(sortField === 'patternsFound' && sortDirection === 'desc' ? 'asc' : 'desc');
                  }}
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                >
                  Patterns Found
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Performance
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {sortedJobs.map((job) => (
                <tr key={job.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      Round {job.round}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {getStatusIcon(job.status)}
                      <span className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(job.status)}`}>
                        {job.status}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div>{job.timestamp.toLocaleDateString()}</div>
                    <div className="text-xs text-gray-500">{job.timestamp.toLocaleTimeString()}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {job.duration.toFixed(2)}s
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <Users className="h-4 w-4 text-gray-400 mr-1" />
                      <span className="text-sm text-gray-900">{job.clientCount}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <TrendingUp className="h-4 w-4 text-gray-400 mr-1" />
                      <span className="text-sm font-medium text-blue-600">{job.patternsFound}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-xs text-gray-500">
                      {(job.patternsFound / job.duration).toFixed(1)} patterns/sec
                    </div>
                    <div className="text-xs text-gray-500">
                      {(job.duration / job.clientCount).toFixed(1)}s per client
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {sortedJobs.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            No jobs found for the selected timeframe
          </div>
        )}
      </div>

      {/* Performance Trends */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Performance Trends</h4>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h5 className="text-sm font-medium text-gray-700 mb-3">Duration by Round</h5>
            <div className="space-y-2">
              {sortedJobs.slice(0, 5).map((job, index) => (
                <div key={job.id} className="flex items-center space-x-3">
                  <div className="w-20 text-sm text-gray-600">Round {job.round}</div>
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${(job.duration / Math.max(...sortedJobs.map(j => j.duration))) * 100}%` }}
                    ></div>
                  </div>
                  <div className="text-sm text-gray-900 min-w-[60px]">{job.duration.toFixed(1)}s</div>
                </div>
              ))}
            </div>
          </div>
          
          <div>
            <h5 className="text-sm font-medium text-gray-700 mb-3">Patterns Found by Round</h5>
            <div className="space-y-2">
              {sortedJobs.slice(0, 5).map((job, index) => (
                <div key={job.id} className="flex items-center space-x-3">
                  <div className="w-20 text-sm text-gray-600">Round {job.round}</div>
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-green-600 h-2 rounded-full"
                      style={{ width: `${(job.patternsFound / Math.max(...sortedJobs.map(j => j.patternsFound))) * 100}%` }}
                    ></div>
                  </div>
                  <div className="text-sm text-gray-900 min-w-[60px]">{job.patternsFound}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default JobHistoryTab;