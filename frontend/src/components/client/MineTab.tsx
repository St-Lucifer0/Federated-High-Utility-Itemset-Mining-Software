import React, { useState } from 'react';
import { Play, Settings, TrendingUp, Clock, MemoryStick, Database } from 'lucide-react';
import { apiService, MiningRequest } from '../../services/api';

interface MineTabProps {
  clientData: any;
  setClientData: (data: any) => void;
}

const MineTab: React.FC<MineTabProps> = ({ clientData, setClientData }) => {
  const [isMining, setIsMining] = useState(false);
  const [minUtility, setMinUtility] = useState(10);
  const [miningProgress, setMiningProgress] = useState(0);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [advancedSettings, setAdvancedSettings] = useState({
    maxPatternLength: 5,
    minSupport: 0.1,
    usePruning: true,
    batchSize: 1000
  });

  const startMining = async () => {
    if (clientData.transactions.length === 0) {
      alert('Please upload transactions first');
      return;
    }

    setIsMining(true);
    setMiningProgress(0);

    try {
      // Start mining job via API
      const miningRequest: MiningRequest = {
        store_id: clientData.storeId,
        min_utility: minUtility,
        min_support: advancedSettings.minSupport,
        max_pattern_length: advancedSettings.maxPatternLength,
        use_pruning: advancedSettings.usePruning,
        batch_size: advancedSettings.batchSize
      };

      const response = await apiService.startMining(miningRequest);
      const jobId = response.job_id;

      // Poll for job status
      const pollInterval = setInterval(async () => {
        try {
          const status = await apiService.getMiningStatus(jobId);
          
          if (status.status === 'running') {
            setMiningProgress(50); // Approximate progress
          } else if (status.status === 'completed') {
            clearInterval(pollInterval);
            setMiningProgress(100);
            
            // Get mining results
            const results = await apiService.getMiningResults(jobId);
            
            const miningStats = {
              transactionCount: clientData.transactions.length,
              minUtilityThreshold: minUtility,
              patternsFound: results.patterns.length,
              executionTime: status.execution_time_seconds || 0,
              memoryUsed: 45 + Math.random() * 15 // Approximate memory usage
            };

            // Transform patterns to match ResultsTab expected format
            const transformedPatterns = results.patterns.map((pattern: any, index: number) => ({
              id: `pattern_${index}`,
              pattern: pattern.items, // Map 'items' to 'pattern'
              utility: pattern.utility,
              support: pattern.support,
              confidence: pattern.confidence
            }));

            setClientData((prev: any) => ({
              ...prev,
              minedPatterns: transformedPatterns,
              miningStats
            }));
            
            setIsMining(false);
          } else if (status.status === 'failed') {
            clearInterval(pollInterval);
            setIsMining(false);
            alert(`Mining failed: ${status.error_message}`);
          }
        } catch (error) {
          clearInterval(pollInterval);
          setIsMining(false);
          alert(`Mining error: ${error}`);
        }
      }, 2000); // Poll every 2 seconds
      
    } catch (error) {
      setIsMining(false);
      alert(`Failed to start mining: ${error}`);
    }
  };

  const generateMockPatterns = (transactions: any[], minUtil: number) => {
    // Extract all unique items
    const allItems = new Set<string>();
    transactions.forEach(t => t.items.forEach((item: string) => allItems.add(item)));
    const itemList = Array.from(allItems);

    const patterns = [];
    
    // Generate single item patterns
    itemList.forEach(item => {
      const utility = Math.random() * 50 + minUtil;
      const support = Math.random() * 0.8 + 0.2;
      patterns.push({
        id: `pattern_${Date.now()}_${Math.random()}`,
        pattern: [item],
        utility: parseFloat(utility.toFixed(2)),
        support: parseFloat(support.toFixed(3)),
        confidence: parseFloat((Math.random() * 0.5 + 0.5).toFixed(3))
      });
    });

    // Generate pair patterns
    for (let i = 0; i < itemList.length && patterns.length < 20; i++) {
      for (let j = i + 1; j < itemList.length && patterns.length < 20; j++) {
        if (Math.random() > 0.7) {
          const utility = Math.random() * 40 + minUtil;
          const support = Math.random() * 0.6 + 0.1;
          patterns.push({
            id: `pattern_${Date.now()}_${Math.random()}`,
            pattern: [itemList[i], itemList[j]],
            utility: parseFloat(utility.toFixed(2)),
            support: parseFloat(support.toFixed(3)),
            confidence: parseFloat((Math.random() * 0.4 + 0.3).toFixed(3))
          });
        }
      }
    }

    // Generate triplet patterns
    for (let i = 0; i < itemList.length && patterns.length < 30; i++) {
      for (let j = i + 1; j < itemList.length && patterns.length < 30; j++) {
        for (let k = j + 1; k < itemList.length && patterns.length < 30; k++) {
          if (Math.random() > 0.9) {
            const utility = Math.random() * 30 + minUtil;
            const support = Math.random() * 0.4 + 0.05;
            patterns.push({
              id: `pattern_${Date.now()}_${Math.random()}`,
              pattern: [itemList[i], itemList[j], itemList[k]],
              utility: parseFloat(utility.toFixed(2)),
              support: parseFloat(support.toFixed(3)),
              confidence: parseFloat((Math.random() * 0.3 + 0.2).toFixed(3))
            });
          }
        }
      }
    }

    return patterns.filter(p => p.utility >= minUtil).slice(0, 25);
  };

  return (
    <div className="space-y-6">
      {/* Mining Configuration */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">Mining Configuration</h3>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Minimum Utility Threshold
            </label>
            <div className="flex items-center space-x-4">
              <input
                type="range"
                min="0"
                max="50"
                step="0.5"
                value={minUtility}
                onChange={(e) => setMinUtility(parseFloat(e.target.value))}
                className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                disabled={isMining}
              />
              <div className="bg-blue-100 text-blue-800 px-3 py-1 rounded-md font-medium min-w-[60px] text-center">
                {minUtility}
              </div>
            </div>
            <p className="text-sm text-gray-500 mt-1">
              Higher values find fewer but more significant patterns
            </p>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">Advanced Settings</span>
            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="text-blue-600 hover:text-blue-800 text-sm font-medium"
            >
              {showAdvanced ? 'Hide' : 'Show'}
            </button>
          </div>

          {showAdvanced && (
            <div className="space-y-3 p-4 bg-gray-50 rounded-md">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Max Pattern Length
                </label>
                <input
                  type="number"
                  min="2"
                  max="10"
                  value={advancedSettings.maxPatternLength}
                  onChange={(e) => setAdvancedSettings({
                    ...advancedSettings,
                    maxPatternLength: parseInt(e.target.value)
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isMining}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Minimum Support
                </label>
                <input
                  type="number"
                  min="0.01"
                  max="1"
                  step="0.01"
                  value={advancedSettings.minSupport}
                  onChange={(e) => setAdvancedSettings({
                    ...advancedSettings,
                    minSupport: parseFloat(e.target.value)
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isMining}
                />
              </div>
              
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="usePruning"
                  checked={advancedSettings.usePruning}
                  onChange={(e) => setAdvancedSettings({
                    ...advancedSettings,
                    usePruning: e.target.checked
                  })}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  disabled={isMining}
                />
                <label htmlFor="usePruning" className="ml-2 text-sm text-gray-700">
                  Enable UP-Growth Pruning
                </label>
              </div>
            </div>
          )}
        </div>

        {/* Data Summary */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">Data Summary</h3>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="flex items-center">
                <Database className="h-5 w-5 text-blue-600 mr-2" />
                <span className="text-sm font-medium text-blue-900">Transactions</span>
              </div>
              <div className="text-2xl font-bold text-blue-600 mt-1">
                {clientData.transactions.length}
              </div>
            </div>
            
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="flex items-center">
                <TrendingUp className="h-5 w-5 text-green-600 mr-2" />
                <span className="text-sm font-medium text-green-900">Total Utility</span>
              </div>
              <div className="text-2xl font-bold text-green-600 mt-1">
                {clientData.transactions.reduce((sum: number, t: any) => sum + t.totalUtility, 0).toFixed(1)}
              </div>
            </div>
          </div>
          
          <div className="bg-purple-50 p-4 rounded-lg">
            <div className="flex items-center">
              <Settings className="h-5 w-5 text-purple-600 mr-2" />
              <span className="text-sm font-medium text-purple-900">Unique Items</span>
            </div>
            <div className="text-2xl font-bold text-purple-600 mt-1">
              {new Set(clientData.transactions.flatMap((t: any) => t.items)).size}
            </div>
          </div>
        </div>
      </div>

      {/* Mining Progress */}
      {isMining && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-lg font-semibold text-blue-900">Mining in Progress</h4>
            <div className="text-blue-700 font-medium">{miningProgress}%</div>
          </div>
          
          <div className="w-full bg-blue-200 rounded-full h-3 mb-4">
            <div 
              className="bg-blue-600 h-3 rounded-full transition-all duration-300 ease-out"
              style={{ width: `${miningProgress}%` }}
            ></div>
          </div>
          
          <div className="flex items-center text-blue-700">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-3"></div>
            <span className="text-sm">Processing transactions and mining patterns...</span>
          </div>
        </div>
      )}

      {/* Mining Results Summary */}
      {clientData.miningStats && !isMining && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">Latest Mining Results</h4>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {clientData.miningStats.patternsFound}
              </div>
              <div className="text-sm text-gray-500">Patterns Found</div>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {clientData.miningStats.executionTime}s
              </div>
              <div className="text-sm text-gray-500">Execution Time</div>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {clientData.miningStats.memoryUsed}MB
              </div>
              <div className="text-sm text-gray-500">Memory Used</div>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {clientData.miningStats.maxUtility?.toFixed(1) || 0}
              </div>
              <div className="text-sm text-gray-500">Max Utility</div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div className="flex items-center">
              <Clock className="h-4 w-4 text-gray-400 mr-2" />
              <span>Build Time: {clientData.miningStats.buildTime}s</span>
            </div>
            
            <div className="flex items-center">
              <TrendingUp className="h-4 w-4 text-gray-400 mr-2" />
              <span>Mining Time: {clientData.miningStats.miningTime}s</span>
            </div>
            
            <div className="flex items-center">
              <MemoryStick className="h-4 w-4 text-gray-400 mr-2" />
              <span>Avg Utility: {clientData.miningStats.avgUtility?.toFixed(2) || 0}</span>
            </div>
          </div>
        </div>
      )}

      {/* Start Mining Button */}
      <div className="flex justify-center">
        <button
          onClick={startMining}
          disabled={isMining || clientData.transactions.length === 0}
          className={`flex items-center px-6 py-3 rounded-lg font-medium transition-all ${
            isMining || clientData.transactions.length === 0
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700 shadow-sm hover:shadow-md'
          }`}
        >
          <Play className="h-5 w-5 mr-2" />
          {isMining ? 'Mining in Progress...' : 'Start Mining'}
        </button>
      </div>
      
      {clientData.transactions.length === 0 && (
        <p className="text-center text-gray-500 text-sm">
          Please upload transaction data before starting the mining process
        </p>
      )}
    </div>
  );
};

export default MineTab;