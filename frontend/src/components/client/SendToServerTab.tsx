import React, { useState } from 'react';
import { Send, CheckCircle, AlertCircle, Wifi, WifiOff, Shield } from 'lucide-react';

interface SendToServerTabProps {
  clientData: any;
  setClientData: (data: any) => void;
}

const SendToServerTab: React.FC<SendToServerTabProps> = ({ clientData, setClientData }) => {
  const [isConnected, setIsConnected] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [lastSentRound, setLastSentRound] = useState(0);
  const [serverResponse, setServerResponse] = useState<{
    status: 'success' | 'error' | null;
    message: string;
    timestamp?: Date;
  }>({ status: null, message: '' });

  const hasPatterns = clientData?.minedPatterns && clientData.minedPatterns.length > 0;
  const currentRound = 0;
  const simulateServerConnection = async () => {
    setIsSending(true);
    setServerResponse({ status: null, message: '' });

    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Simulate success/failure
    const success = Math.random() > 0.1; // 90% success rate

    if (success) {
      setServerResponse({
        status: 'success',
        message: `Successfully contributed to federated round ${currentRound}. Your patterns have been securely aggregated.`,
        timestamp: new Date()
      });
      setLastSentRound(currentRound);
      
      // Add to logs
      const newLog = {
        id: `log_${Date.now()}`,
        timestamp: new Date(),
        type: 'federated_contribution',
        message: `Contributed ${clientData.minedPatterns.length} patterns to round ${currentRound}`,
        details: { 
          round: currentRound, 
          patterns: clientData.minedPatterns.length,
          privacyBudget: clientData.privacyConfig.epsilon
        }
      };
      
      setClientData((prev: any) => ({
        ...prev,
        logs: [...(prev.logs || []), newLog]
      }));
    } else {
      setServerResponse({
        status: 'error',
        message: 'Failed to connect to federated server. Please check your network connection and try again.',
        timestamp: new Date()
      });
    }

    setIsSending(false);
  };

  const applyPrivacyToPatterns = (patterns: any[]) => {
    const { epsilon, hashPatterns } = clientData.privacyConfig;
    
    if (!patterns || patterns.length === 0) return [];
    
    return patterns.map(pattern => {
      // Apply noise based on privacy settings
      const noiseFactor = 1 + (Math.random() - 0.5) * (2 / epsilon);
      const noisyUtility = Math.max(0.1, pattern.utility * noiseFactor);
      
      return {
        ...pattern,
        utility: parseFloat(noisyUtility.toFixed(2)),
        pattern: hashPatterns 
          ? pattern.pattern.map((item: string) => `hash_${item.charCodeAt(0) + item.length}`)
          : pattern.pattern
      };
    });
  };

  const getPrivacyAppliedPatterns = () => {
    if (!hasPatterns) return [];
    return applyPrivacyToPatterns(clientData.minedPatterns.slice(0, 5)); // Send top 5 patterns
  };

  return (
    <div className="space-y-6">
      {/* Connection Status */}
      <div className={`flex items-center p-4 rounded-lg ${
        isConnected ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
      }`}>
        {isConnected ? (
          <>
            <Wifi className="h-5 w-5 text-green-600 mr-3" />
            <div>
              <p className="font-medium text-green-800">Connected to Federated Server</p>
              <p className="text-sm text-green-700">Ready to participate in federated learning rounds</p>
            </div>
          </>
        ) : (
          <>
            <WifiOff className="h-5 w-5 text-red-600 mr-3" />
            <div>
              <p className="font-medium text-red-800">Disconnected from Server</p>
              <p className="text-sm text-red-700">Check network connection or server status</p>
            </div>
          </>
        )}
      </div>

      {/* Federated Learning Status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-blue-600">{currentRound}</div>
          <div className="text-sm text-blue-900">Current Round</div>
        </div>
        
        <div className="bg-green-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-green-600">{lastSentRound}</div>
          <div className="text-sm text-green-900">Last Contributed</div>
        </div>
        
        <div className="bg-purple-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-purple-600">
            {hasPatterns ? clientData.minedPatterns.length : 0}
          </div>
          <div className="text-sm text-purple-900">Patterns Ready</div>
        </div>
      </div>

      {/* Privacy Summary */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <div className="flex items-center mb-3">
          <Shield className="h-5 w-5 text-gray-600 mr-2" />
          <h4 className="font-medium text-gray-900">Privacy Configuration</h4>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="text-gray-600">Privacy Budget:</span>
            <div className="font-medium text-gray-900">ε = {clientData.privacyConfig.epsilon}</div>
          </div>
          <div>
            <span className="text-gray-600">Noise Type:</span>
            <div className="font-medium text-gray-900 capitalize">{clientData.privacyConfig.noiseType}</div>
          </div>
          <div>
            <span className="text-gray-600">Pattern Hashing:</span>
            <div className="font-medium text-gray-900">
              {clientData.privacyConfig.hashPatterns ? 'Enabled' : 'Disabled'}
            </div>
          </div>
          <div>
            <span className="text-gray-600">Patterns to Send:</span>
            <div className="font-medium text-gray-900">
              {hasPatterns ? Math.min(5, clientData.minedPatterns.length) : 0}
            </div>
          </div>
        </div>
      </div>

      {/* Patterns Preview */}
      {hasPatterns && (
        <div className="space-y-4">
          <h4 className="font-medium text-gray-900">Patterns to be Sent (with privacy applied)</h4>
          
          <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Pattern</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Original Utility</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Private Utility</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Noise Added</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {getPrivacyAppliedPatterns().map((pattern, index) => {
                  const originalPattern = clientData.minedPatterns[index];
                  const noisePercent = ((pattern.utility - originalPattern.utility) / originalPattern.utility * 100);
                  
                  return (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm">
                        <div className="flex flex-wrap gap-1">
                          {pattern.pattern.map((item: string, idx: number) => (
                            <span
                              key={idx}
                              className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
                            >
                              {item}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900">{originalPattern.utility.toFixed(2)}</td>
                      <td className="px-4 py-3 text-sm text-gray-900">{pattern.utility.toFixed(2)}</td>
                      <td className="px-4 py-3 text-sm">
                        <span className={`font-medium ${
                          Math.abs(noisePercent) < 5 ? 'text-green-600' : 
                          Math.abs(noisePercent) < 15 ? 'text-yellow-600' : 'text-red-600'
                        }`}>
                          {noisePercent > 0 ? '+' : ''}{noisePercent.toFixed(1)}%
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Send Button */}
      <div className="flex justify-center">
        <button
          onClick={simulateServerConnection}
          disabled={!hasPatterns || !isConnected || isSending}
          className={`flex items-center px-8 py-3 rounded-lg font-medium text-lg transition-all ${
            !hasPatterns || !isConnected || isSending
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700 shadow-lg hover:shadow-xl'
          }`}
        >
          <Send className="h-5 w-5 mr-2" />
          {isSending ? 'Sending to Server...' : 'Contribute to Federated Round'}
        </button>
      </div>

      {/* Server Response */}
      {serverResponse.status && (
        <div className={`flex items-start p-4 rounded-lg ${
          serverResponse.status === 'success' 
            ? 'bg-green-50 border border-green-200' 
            : 'bg-red-50 border border-red-200'
        }`}>
          {serverResponse.status === 'success' ? (
            <CheckCircle className="h-5 w-5 text-green-600 mr-3 mt-0.5" />
          ) : (
            <AlertCircle className="h-5 w-5 text-red-600 mr-3 mt-0.5" />
          )}
          <div>
            <p className={`font-medium ${
              serverResponse.status === 'success' ? 'text-green-800' : 'text-red-800'
            }`}>
              {serverResponse.status === 'success' ? 'Success!' : 'Error'}
            </p>
            <p className={`text-sm mt-1 ${
              serverResponse.status === 'success' ? 'text-green-700' : 'text-red-700'
            }`}>
              {serverResponse.message}
            </p>
            {serverResponse.timestamp && (
              <p className={`text-xs mt-2 ${
                serverResponse.status === 'success' ? 'text-green-600' : 'text-red-600'
              }`}>
                {serverResponse.timestamp.toLocaleString()}
              </p>
            )}
          </div>
        </div>
      )}

      {/* Requirements Check */}
      {!hasPatterns && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start">
            <AlertCircle className="h-5 w-5 text-yellow-600 mr-3 mt-0.5" />
            <div>
              <p className="font-medium text-yellow-800">No Patterns Available</p>
              <p className="text-sm text-yellow-700 mt-1">
                Please mine local patterns first in the "Mine Itemsets" tab before contributing to federated learning.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SendToServerTab;