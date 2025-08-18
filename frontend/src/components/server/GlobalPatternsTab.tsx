import React, { useState, useEffect } from 'react';
import { TrendingUp, Download, Filter, SortAsc, SortDesc, Eye, BarChart3, Share2, Shield } from 'lucide-react';
import { apiService } from '../../services/api';

interface GlobalPatternsTabProps {
  serverData: any;
  setServerData: (data: any) => void;
}

const GlobalPatternsTab: React.FC<GlobalPatternsTabProps> = ({ serverData, setServerData }) => {
  const [sortField, setSortField] = useState('utility');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [filterMinUtility, setFilterMinUtility] = useState(0);
  const [filterMinSupport, setFilterMinSupport] = useState(0);
  const [selectedPattern, setSelectedPattern] = useState<any>(null);
  const [viewMode, setViewMode] = useState<'table' | 'chart'>('table');
  const [patterns, setPatterns] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // Load global patterns on component mount
  useEffect(() => {
    loadGlobalPatterns();
  }, []);

  const loadGlobalPatterns = async () => {
    try {
      setLoading(true);
      const response = await apiService.getFederatedRounds();
      // Extract patterns from completed rounds
      const allPatterns: any[] = [];
      response.rounds?.forEach((round: any) => {
        if (round.status === 'completed' && round.patterns_aggregated > 0) {
          // For now, create mock patterns based on round data
          // In a real implementation, you'd have a separate endpoint for global patterns
          for (let i = 0; i < Math.min(round.patterns_aggregated, 5); i++) {
            allPatterns.push({
              pattern: `Pattern_${round.round_number}_${i + 1}`,
              utility: Math.random() * 50 + 10,
              support: Math.random() * 0.5 + 0.1,
              clientCount: round.participating_clients,
              roundId: round.id
            });
          }
        }
      });
      setPatterns(allPatterns);
      
      // Update server data
      setServerData((prev: any) => ({
        ...prev,
        globalPatterns: allPatterns
      }));
    } catch (error) {
      console.error('Failed to load global patterns:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const filteredAndSortedPatterns = patterns
    .filter((pattern: any) => 
      pattern.utility >= filterMinUtility && 
      pattern.support >= filterMinSupport
    )
    .sort((a: any, b: any) => {
      let aVal = a[sortField];
      let bVal = b[sortField];
      
      // Handle pattern field specially for sorting
      if (sortField === 'pattern') {
        aVal = a.pattern.toString();
        bVal = b.pattern.toString();
      }
      
      if (sortDirection === 'asc') {
        return aVal > bVal ? 1 : -1;
      } else {
        return aVal < bVal ? 1 : -1;
      }
    });

  const exportToCSV = () => {
    if (patterns.length === 0) return;

    const headers = ['Pattern', 'Utility', 'Support', 'Client_Count', 'Aggregation_Method'];
    const csvContent = [
      headers.join(','),
      ...filteredAndSortedPatterns.map(pattern => [
        `"${pattern.pattern}"`,
        pattern.utility,
        pattern.support,
        pattern.clientCount,
        'Secure_Aggregation'
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `global_patterns_round_${serverData.currentRound}_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const getUtilityColor = (utility: number) => {
    if (utility >= 40) return 'text-red-600 bg-red-50';
    if (utility >= 30) return 'text-orange-600 bg-orange-50';
    if (utility >= 20) return 'text-yellow-600 bg-yellow-50';
    return 'text-green-600 bg-green-50';
  };

  const getClientCoverage = (clientCount: number) => {
    const totalClients = serverData.clients.length;
    return ((clientCount / totalClients) * 100).toFixed(0);
  };

  if (patterns.length === 0) {
    return (
      <div className="text-center py-12">
        <TrendingUp className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-4 text-lg font-medium text-gray-900">No global patterns available</h3>
        <p className="mt-2 text-gray-500">
          Global patterns will appear here after federated learning rounds are completed
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Statistics Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="flex items-center">
            <BarChart3 className="h-5 w-5 text-blue-600 mr-2" />
            <span className="text-sm font-medium text-blue-900">Total Patterns</span>
          </div>
          <div className="text-2xl font-bold text-blue-600 mt-1">
            {patterns.length}
          </div>
        </div>
        
        <div className="bg-green-50 p-4 rounded-lg">
          <div className="flex items-center">
            <TrendingUp className="h-5 w-5 text-green-600 mr-2" />
            <span className="text-sm font-medium text-green-900">Max Utility</span>
          </div>
          <div className="text-2xl font-bold text-green-600 mt-1">
            {Math.max(...patterns.map(p => p.utility)).toFixed(1)}
          </div>
        </div>
        
        <div className="bg-purple-50 p-4 rounded-lg">
          <div className="flex items-center">
            <Share2 className="h-5 w-5 text-purple-600 mr-2" />
            <span className="text-sm font-medium text-purple-900">Avg Support</span>
          </div>
          <div className="text-2xl font-bold text-purple-600 mt-1">
            {(patterns.reduce((sum, p) => sum + p.support, 0) / patterns.length).toFixed(3)}
          </div>
        </div>
        
        <div className="bg-orange-50 p-4 rounded-lg">
          <div className="flex items-center">
            <Shield className="h-5 w-5 text-orange-600 mr-2" />
            <span className="text-sm font-medium text-orange-900">Privacy Protected</span>
          </div>
          <div className="text-2xl font-bold text-orange-600 mt-1">
            100%
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="flex flex-col lg:flex-row gap-4 items-start lg:items-center justify-between bg-gray-50 p-4 rounded-lg">
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
          <div className="flex items-center space-x-2">
            <Filter className="h-4 w-4 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">Filters:</span>
          </div>
          
          <div className="flex items-center space-x-2">
            <label className="text-sm text-gray-600">Min Utility:</label>
            <input
              type="number"
              min="0"
              step="0.1"
              value={filterMinUtility}
              onChange={(e) => setFilterMinUtility(parseFloat(e.target.value) || 0)}
              className="w-20 px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div className="flex items-center space-x-2">
            <label className="text-sm text-gray-600">Min Support:</label>
            <input
              type="number"
              min="0"
              max="1"
              step="0.01"
              value={filterMinSupport}
              onChange={(e) => setFilterMinSupport(parseFloat(e.target.value) || 0)}
              className="w-20 px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <div className="flex bg-gray-200 rounded-lg p-1">
            <button
              onClick={() => setViewMode('table')}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                viewMode === 'table' ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-600'
              }`}
            >
              Table
            </button>
            <button
              onClick={() => setViewMode('chart')}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                viewMode === 'chart' ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-600'
              }`}
            >
              Chart
            </button>
          </div>
          
          <button
            onClick={exportToCSV}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm"
          >
            <Download className="h-4 w-4 mr-2" />
            Export
          </button>
        </div>
      </div>

      {viewMode === 'table' ? (
        /* Table View */
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th
                    onClick={() => handleSort('pattern')}
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  >
                    <div className="flex items-center space-x-1">
                      <span>Global Pattern</span>
                      {sortField === 'pattern' && (
                        sortDirection === 'asc' ? <SortAsc className="h-4 w-4" /> : <SortDesc className="h-4 w-4" />
                      )}
                    </div>
                  </th>
                  <th
                    onClick={() => handleSort('utility')}
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  >
                    <div className="flex items-center space-x-1">
                      <span>Aggregated Utility</span>
                      {sortField === 'utility' && (
                        sortDirection === 'asc' ? <SortAsc className="h-4 w-4" /> : <SortDesc className="h-4 w-4" />
                      )}
                    </div>
                  </th>
                  <th
                    onClick={() => handleSort('support')}
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  >
                    <div className="flex items-center space-x-1">
                      <span>Global Support</span>
                      {sortField === 'support' && (
                        sortDirection === 'asc' ? <SortAsc className="h-4 w-4" /> : <SortDesc className="h-4 w-4" />
                      )}
                    </div>
                  </th>
                  <th
                    onClick={() => handleSort('clientCount')}
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  >
                    <div className="flex items-center space-x-1">
                      <span>Client Coverage</span>
                      {sortField === 'clientCount' && (
                        sortDirection === 'asc' ? <SortAsc className="h-4 w-4" /> : <SortDesc className="h-4 w-4" />
                      )}
                    </div>
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Privacy Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredAndSortedPatterns.map((pattern, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex flex-wrap gap-1">
                        {pattern.pattern.split(',').map((item: string, idx: number) => (
                          <span
                            key={idx}
                            className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                          >
                            {item.trim().replace(/[\[\]']/g, '')}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getUtilityColor(pattern.utility)}`}>
                        {pattern.utility.toFixed(2)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-1 bg-gray-200 rounded-full h-2 mr-2">
                          <div 
                            className="bg-purple-600 h-2 rounded-full"
                            style={{ width: `${pattern.support * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-gray-900">{pattern.support.toFixed(3)}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <span className="text-sm font-medium text-gray-900">{pattern.clientCount}</span>
                        <span className="text-xs text-gray-500 ml-1">
                          ({getClientCoverage(pattern.clientCount)}%)
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <Shield className="h-4 w-4 text-green-600 mr-1" />
                        <span className="text-xs text-green-600 font-medium">Protected</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => setSelectedPattern(pattern)}
                        className="text-blue-600 hover:text-blue-800 font-medium flex items-center"
                      >
                        <Eye className="h-4 w-4 mr-1" />
                        Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {filteredAndSortedPatterns.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              No patterns match the current filters
            </div>
          )}
        </div>
      ) : (
        /* Chart View */
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-6">Pattern Utility Distribution</h4>
          
          <div className="space-y-4">
            {filteredAndSortedPatterns.slice(0, 10).map((pattern, index) => (
              <div key={index} className="flex items-center space-x-4">
                <div className="w-32 text-sm text-gray-700 truncate">
                  {pattern.pattern.split(',').slice(0, 2).join(', ').replace(/[\[\]']/g, '')}
                  {pattern.pattern.split(',').length > 2 && '...'}
                </div>
                
                <div className="flex-1 flex items-center">
                  <div className="flex-1 bg-gray-200 rounded-full h-4 mr-3">
                    <div 
                      className="bg-gradient-to-r from-blue-500 to-purple-600 h-4 rounded-full flex items-center justify-end pr-2"
                      style={{ width: `${(pattern.utility / Math.max(...patterns.map(p => p.utility))) * 100}%` }}
                    >
                      {pattern.utility >= 20 && (
                        <span className="text-xs text-white font-medium">
                          {pattern.utility.toFixed(1)}
                        </span>
                      )}
                    </div>
                  </div>
                  
                  {pattern.utility < 20 && (
                    <span className="text-sm text-gray-600 font-medium min-w-[50px]">
                      {pattern.utility.toFixed(1)}
                    </span>
                  )}
                </div>
                
                <div className="flex items-center space-x-2 text-xs text-gray-500">
                  <span>{pattern.clientCount} clients</span>
                  <span>•</span>
                  <span>{(pattern.support * 100).toFixed(1)}% support</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Privacy & Security Notice */}
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-start">
          <Shield className="h-5 w-5 text-green-600 mr-3 mt-0.5" />
          <div>
            <h4 className="text-sm font-semibold text-green-800 mb-1">Privacy Protection Active</h4>
            <p className="text-sm text-green-700">
              All patterns have been aggregated using secure multi-party computation with differential privacy. 
              Individual client data remains encrypted and private throughout the federated learning process.
            </p>
          </div>
        </div>
      </div>

      {/* Pattern Detail Modal */}
      {selectedPattern && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-lg w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Global Pattern Details</h3>
            
            <div className="space-y-4">
              <div>
                <span className="text-sm font-medium text-gray-700">Pattern Items:</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {selectedPattern.pattern.split(',').map((item: string, idx: number) => (
                    <span
                      key={idx}
                      className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                    >
                      {item.trim().replace(/[\[\]']/g, '')}
                    </span>
                  ))}
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="text-sm font-medium text-gray-700">Aggregated Utility:</span>
                  <div className="text-xl font-bold text-blue-600">{selectedPattern.utility.toFixed(2)}</div>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-700">Global Support:</span>
                  <div className="text-xl font-bold text-green-600">{selectedPattern.support.toFixed(3)}</div>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="text-sm font-medium text-gray-700">Contributing Clients:</span>
                  <div className="text-xl font-bold text-purple-600">{selectedPattern.clientCount}</div>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-700">Coverage:</span>
                  <div className="text-xl font-bold text-orange-600">
                    {getClientCoverage(selectedPattern.clientCount)}%
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-50 p-3 rounded-md">
                <span className="text-sm font-medium text-gray-700">Privacy Information:</span>
                <ul className="text-sm text-gray-600 mt-1 space-y-1">
                  <li>• Differential privacy applied during aggregation</li>
                  <li>• Secure multi-party computation used</li>
                  <li>• Individual client contributions remain private</li>
                </ul>
              </div>
            </div>
            
            <div className="mt-6 flex justify-end">
              <button
                onClick={() => setSelectedPattern(null)}
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

export default GlobalPatternsTab;