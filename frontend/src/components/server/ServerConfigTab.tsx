import React, { useState } from 'react';
import { Settings, Save, RotateCcw, AlertCircle, CheckCircle, Shield, Database } from 'lucide-react';

interface ServerConfigTabProps {
  serverData: any;
  setServerData: (data: any) => void;
}

const ServerConfigTab: React.FC<ServerConfigTabProps> = ({ serverData, setServerData }) => {
  const [config, setConfig] = useState(serverData.serverConfig);
  const [hasChanges, setHasChanges] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'success' | 'error'>('idle');

  const updateConfig = (key: string, value: any) => {
    const newConfig = { ...config, [key]: value };
    setConfig(newConfig);
    setHasChanges(JSON.stringify(newConfig) !== JSON.stringify(serverData.serverConfig));
  };

  const saveConfiguration = async () => {
    setSaveStatus('saving');
    
    try {
      // TODO: Replace with actual API call to save server configuration
      // await apiService.updateServerConfig(config);
      
      setServerData({
        ...serverData,
        serverConfig: config
      });
      
      setHasChanges(false);
      setSaveStatus('success');
      
      // Reset status after 3 seconds
      setTimeout(() => setSaveStatus('idle'), 3000);
    } catch (error) {
      setSaveStatus('error');
      setTimeout(() => setSaveStatus('idle'), 3000);
    }
  };

  const resetToDefaults = () => {
    const defaultConfig = {
      minUtility: 0,
      minSupport: 0,
      privacyBudget: 0,
      minClientsPerRound: 0,
      maxPatternLength: 0,
      noiseLevel: 0
    };
    
    setConfig(defaultConfig);
    setHasChanges(true);
  };

  const getConfigValidation = () => {
    const issues = [];
    
    if (config.minUtility < 0) issues.push('Minimum utility must be non-negative');
    if (config.minSupport < 0 || config.minSupport > 1) issues.push('Minimum support must be between 0 and 1');
    if (config.privacyBudget < 0 || config.privacyBudget > 5) issues.push('Privacy budget must be between 0 and 5');
    if (config.minClientsPerRound < 0) issues.push('Minimum clients per round must be non-negative');
    if (config.maxPatternLength < 0 || config.maxPatternLength > 10) issues.push('Max pattern length must be between 0 and 10');
    if (config.noiseLevel < 0 || config.noiseLevel > 1) issues.push('Noise level must be between 0 and 1');
    
    return issues;
  };

  const validationIssues = getConfigValidation();
  const canSave = hasChanges && validationIssues.length === 0;

  return (
    <div className="space-y-6">
      {/* Configuration Status */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start">
          <Settings className="h-5 w-5 text-blue-600 mr-3 mt-0.5" />
          <div>
            <h3 className="text-sm font-semibold text-blue-800 mb-1">Server Configuration</h3>
            <p className="text-sm text-blue-700">
              Configure federated learning parameters, privacy settings, and system thresholds. 
              Changes will apply to new federated rounds.
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Mining Parameters */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <Database className="h-5 w-5 text-gray-600 mr-2" />
            <h4 className="text-lg font-semibold text-gray-900">Mining Parameters</h4>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Minimum Utility Threshold
              </label>
              <div className="flex items-center space-x-4">
                <input
                  type="range"
                  min="1"
                  max="50"
                  step="0.5"
                  value={config.minUtility}
                  onChange={(e) => updateConfig('minUtility', parseFloat(e.target.value))}
                  className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="bg-blue-100 text-blue-800 px-3 py-1 rounded-md font-medium min-w-[60px] text-center">
                  {config.minUtility}
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Minimum utility value for patterns to be considered significant
              </p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Minimum Support Threshold
              </label>
              <div className="flex items-center space-x-4">
                <input
                  type="range"
                  min="0.01"
                  max="1"
                  step="0.01"
                  value={config.minSupport}
                  onChange={(e) => updateConfig('minSupport', parseFloat(e.target.value))}
                  className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="bg-green-100 text-green-800 px-3 py-1 rounded-md font-medium min-w-[60px] text-center">
                  {config.minSupport.toFixed(2)}
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Minimum support ratio across participating clients
              </p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Maximum Pattern Length
              </label>
              <input
                type="number"
                min="1"
                max="10"
                value={config.maxPatternLength}
                onChange={(e) => updateConfig('maxPatternLength', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">
                Maximum number of items in discovered patterns
              </p>
            </div>
          </div>
        </div>

        {/* Privacy & Security */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <Shield className="h-5 w-5 text-gray-600 mr-2" />
            <h4 className="text-lg font-semibold text-gray-900">Privacy & Security</h4>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Privacy Budget (ε)
              </label>
              <div className="flex items-center space-x-4">
                <input
                  type="range"
                  min="0.1"
                  max="5.0"
                  step="0.1"
                  value={config.privacyBudget}
                  onChange={(e) => updateConfig('privacyBudget', parseFloat(e.target.value))}
                  className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="bg-purple-100 text-purple-800 px-3 py-1 rounded-md font-medium min-w-[60px] text-center">
                  {config.privacyBudget.toFixed(1)}
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Global privacy budget for differential privacy (lower = more private)
              </p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Noise Level
              </label>
              <div className="flex items-center space-x-4">
                <input
                  type="range"
                  min="0.01"
                  max="0.5"
                  step="0.01"
                  value={config.noiseLevel}
                  onChange={(e) => updateConfig('noiseLevel', parseFloat(e.target.value))}
                  className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="bg-orange-100 text-orange-800 px-3 py-1 rounded-md font-medium min-w-[60px] text-center">
                  {(config.noiseLevel * 100).toFixed(0)}%
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Additional noise applied during secure aggregation
              </p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Minimum Clients Per Round
              </label>
              <input
                type="number"
                min="1"
                max="10"
                value={config.minClientsPerRound}
                onChange={(e) => updateConfig('minClientsPerRound', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">
                Minimum number of clients required to start a federated round
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Configuration Preview */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Configuration Summary</h4>
        
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
          <div className="bg-white p-3 rounded-md">
            <span className="text-gray-600">Min Utility:</span>
            <div className="font-semibold text-blue-600">{config.minUtility}</div>
          </div>
          <div className="bg-white p-3 rounded-md">
            <span className="text-gray-600">Min Support:</span>
            <div className="font-semibold text-green-600">{config.minSupport.toFixed(2)}</div>
          </div>
          <div className="bg-white p-3 rounded-md">
            <span className="text-gray-600">Privacy Budget:</span>
            <div className="font-semibold text-purple-600">ε = {config.privacyBudget}</div>
          </div>
          <div className="bg-white p-3 rounded-md">
            <span className="text-gray-600">Min Clients:</span>
            <div className="font-semibold text-orange-600">{config.minClientsPerRound}</div>
          </div>
          <div className="bg-white p-3 rounded-md">
            <span className="text-gray-600">Max Pattern Length:</span>
            <div className="font-semibold text-gray-600">{config.maxPatternLength}</div>
          </div>
          <div className="bg-white p-3 rounded-md">
            <span className="text-gray-600">Noise Level:</span>
            <div className="font-semibold text-red-600">{(config.noiseLevel * 100).toFixed(0)}%</div>
          </div>
        </div>
      </div>

      {/* Validation Issues */}
      {validationIssues.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start">
            <AlertCircle className="h-5 w-5 text-red-600 mr-3 mt-0.5" />
            <div>
              <h4 className="text-sm font-semibold text-red-800 mb-2">Configuration Issues</h4>
              <ul className="text-sm text-red-700 space-y-1">
                {validationIssues.map((issue, index) => (
                  <li key={index}>• {issue}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Save Status */}
      {saveStatus !== 'idle' && (
        <div className={`flex items-center p-4 rounded-lg ${
          saveStatus === 'success' ? 'bg-green-50 text-green-800' :
          saveStatus === 'error' ? 'bg-red-50 text-red-800' :
          'bg-blue-50 text-blue-800'
        }`}>
          {saveStatus === 'success' && <CheckCircle className="h-5 w-5 mr-2" />}
          {saveStatus === 'error' && <AlertCircle className="h-5 w-5 mr-2" />}
          
          {saveStatus === 'saving' && 'Saving configuration...'}
          {saveStatus === 'success' && 'Configuration saved successfully!'}
          {saveStatus === 'error' && 'Failed to save configuration. Please try again.'}
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex justify-between">
        <button
          onClick={resetToDefaults}
          className="flex items-center px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
        >
          <RotateCcw className="h-4 w-4 mr-2" />
          Reset to Defaults
        </button>
        
        <button
          onClick={saveConfiguration}
          disabled={!canSave || saveStatus === 'saving'}
          className={`flex items-center px-6 py-2 rounded-md font-medium transition-colors ${
            canSave && saveStatus !== 'saving'
              ? 'bg-blue-600 text-white hover:bg-blue-700'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          <Save className="h-4 w-4 mr-2" />
          {saveStatus === 'saving' ? 'Saving...' : 'Save Configuration'}
        </button>
      </div>
    </div>
  );
};

export default ServerConfigTab;