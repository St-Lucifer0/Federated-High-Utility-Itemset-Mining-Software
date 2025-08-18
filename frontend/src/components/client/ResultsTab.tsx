import React, { useState } from 'react';
import { Download, SortAsc, SortDesc, Filter, Eye, TrendingUp, BarChart3 } from 'lucide-react';

interface ResultsTabProps {
  clientData: any;
  setClientData: (data: any) => void;
}

const ResultsTab: React.FC<ResultsTabProps> = ({ clientData }) => {
  const [sortField, setSortField] = useState('utility');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [filterMinUtility, setFilterMinUtility] = useState(0);
  const [filterMinSupport, setFilterMinSupport] = useState(0);
  const [selectedPattern, setSelectedPattern] = useState<any>(null);

  const patterns = clientData.minedPatterns || [];

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const filteredAndSortedPatterns = patterns
    .filter(pattern => 
      pattern.utility >= filterMinUtility && 
      pattern.support >= filterMinSupport
    )
    .sort((a, b) => {
      let aVal = a[sortField];
      let bVal = b[sortField];
      
      // Handle pattern field specially for sorting
      if (sortField === 'pattern') {
        aVal = a.pattern.join(',');
        bVal = b.pattern.join(',');
      }
      
      if (sortDirection === 'asc') {
        return aVal > bVal ? 1 : -1;
      } else {
        return aVal < bVal ? 1 : -1;
      }
    });

  const exportToCSV = () => {
    if (patterns.length === 0) return;

    const headers = ['Pattern', 'Utility', 'Support', 'Confidence'];
    const csvContent = [
      headers.join(','),
      ...filteredAndSortedPatterns.map(pattern => [
        `"${pattern.pattern.join(', ')}"`,
        pattern.utility,
        pattern.support,
        pattern.confidence
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `high_utility_patterns_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const getPatternLength = (pattern: string[]) => pattern.length;
  const getUtilityColor = (utility: number) => {
    if (utility >= 40) return 'text-red-600 bg-red-50';
    if (utility >= 25) return 'text-orange-600 bg-orange-50';
    if (utility >= 15) return 'text-yellow-600 bg-yellow-50';
    return 'text-green-600 bg-green-50';
  };

  if (patterns.length === 0) {
    return (
      <div className="text-center py-12">
        <TrendingUp className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-4 text-lg font-medium text-gray-900">No patterns found</h3>
        <p className="mt-2 text-gray-500">
          Start by mining itemsets in the Mine Itemsets tab
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
            <Eye className="h-5 w-5 text-purple-600 mr-2" />
            <span className="text-sm font-medium text-purple-900">Avg Support</span>
          </div>
          <div className="text-2xl font-bold text-purple-600 mt-1">
            {(patterns.reduce((sum, p) => sum + p.support, 0) / patterns.length).toFixed(3)}
          </div>
        </div>
        
        <div className="bg-orange-50 p-4 rounded-lg">
          <div className="flex items-center">
            <Filter className="h-5 w-5 text-orange-600 mr-2" />
            <span className="text-sm font-medium text-orange-900">Filtered</span>
          </div>
          <div className="text-2xl font-bold text-orange-600 mt-1">
            {filteredAndSortedPatterns.length}
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between bg-gray-50 p-4 rounded-lg">
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
        
        <button
          onClick={exportToCSV}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm"
        >
          <Download className="h-4 w-4 mr-2" />
          Export CSV
        </button>
      </div>

      {/* Patterns Table */}
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
                    <span>Pattern</span>
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
                    <span>Utility</span>
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
                    <span>Support</span>
                    {sortField === 'support' && (
                      sortDirection === 'asc' ? <SortAsc className="h-4 w-4" /> : <SortDesc className="h-4 w-4" />
                    )}
                  </div>
                </th>
                <th
                  onClick={() => handleSort('confidence')}
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                >
                  <div className="flex items-center space-x-1">
                    <span>Confidence</span>
                    {sortField === 'confidence' && (
                      sortDirection === 'asc' ? <SortAsc className="h-4 w-4" /> : <SortDesc className="h-4 w-4" />
                    )}
                  </div>
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Length
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredAndSortedPatterns.map((pattern, index) => (
                <tr key={pattern.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex flex-wrap gap-1">
                      {pattern.pattern.map((item: string, idx: number) => (
                        <span
                          key={idx}
                          className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                        >
                          {item}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getUtilityColor(pattern.utility)}`}>
                      {pattern.utility.toFixed(2)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {pattern.support.toFixed(3)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {pattern.confidence.toFixed(3)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                      {getPatternLength(pattern.pattern)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <button
                      onClick={() => setSelectedPattern(pattern)}
                      className="text-blue-600 hover:text-blue-800 font-medium"
                    >
                      View Details
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

      {/* Pattern Detail Modal */}
      {selectedPattern && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Pattern Details</h3>
            
            <div className="space-y-3">
              <div>
                <span className="text-sm font-medium text-gray-700">Items:</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {selectedPattern.pattern.map((item: string, idx: number) => (
                    <span
                      key={idx}
                      className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                    >
                      {item}
                    </span>
                  ))}
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="text-sm font-medium text-gray-700">Utility:</span>
                  <div className="text-lg font-bold text-blue-600">{selectedPattern.utility.toFixed(2)}</div>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-700">Support:</span>
                  <div className="text-lg font-bold text-green-600">{selectedPattern.support.toFixed(3)}</div>
                </div>
              </div>
              
              <div>
                <span className="text-sm font-medium text-gray-700">Confidence:</span>
                <div className="text-lg font-bold text-purple-600">{selectedPattern.confidence.toFixed(3)}</div>
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

export default ResultsTab;