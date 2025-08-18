import React from 'react';
import { Shield, Eye, Hash, Info } from 'lucide-react';

interface PrivacyTabProps {
  clientData: any;
  setClientData: (data: any) => void;
}

const PrivacyTab: React.FC<PrivacyTabProps> = ({ clientData, setClientData }) => {
  const { privacyConfig } = clientData;

  const updatePrivacyConfig = (updates: any) => {
    setClientData({
      ...clientData,
      privacyConfig: { ...privacyConfig, ...updates }
    });
  };

  const getPrivacyLevel = (epsilon: number) => {
    if (epsilon >= 2.0) return { level: 'Low', color: 'text-red-600', description: 'More accurate results, less privacy' };
    if (epsilon >= 1.0) return { level: 'Medium', color: 'text-yellow-600', description: 'Balanced privacy and accuracy' };
    if (epsilon >= 0.5) return { level: 'High', color: 'text-green-600', description: 'Strong privacy, less accurate results' };
    return { level: 'Very High', color: 'text-blue-600', description: 'Maximum privacy, significant noise added' };
  };

  const privacyLevel = getPrivacyLevel(privacyConfig.epsilon);

  return (
    <div className="space-y-6">
      {/* Privacy Overview */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <div className="flex items-start">
          <Shield className="h-6 w-6 text-blue-600 mr-3 mt-1" />
          <div>
            <h3 className="text-lg font-semibold text-blue-900 mb-2">Privacy Protection</h3>
            <p className="text-blue-700 text-sm">
              Configure differential privacy settings to protect sensitive transaction data while contributing to federated learning.
              Higher privacy levels add more noise to your patterns before sharing with the server.
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Privacy Budget (Epsilon) */}
        <div className="space-y-4">
          <div className="flex items-center">
            <Eye className="h-5 w-5 text-gray-600 mr-2" />
            <h4 className="text-md font-semibold text-gray-900">Privacy Budget (ε)</h4>
          </div>
          
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-700">Current Value:</span>
              <div className="flex items-center space-x-2">
                <span className="font-medium text-gray-900">{privacyConfig.epsilon}</span>
                <span className={`text-sm font-medium ${privacyLevel.color}`}>({privacyLevel.level})</span>
              </div>
            </div>
            
            <input
              type="range"
              min="0"
              max="3.0"
              step="0.1"
              value={privacyConfig.epsilon}
              onChange={(e) => updatePrivacyConfig({ epsilon: parseFloat(e.target.value) })}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            
            <div className="flex justify-between text-xs text-gray-500">
              <span>0 (Max Privacy)</span>
              <span>3.0 (Min Privacy)</span>
            </div>
            
            <p className="text-sm text-gray-600">
              {privacyLevel.description}
            </p>
          </div>
        </div>

        {/* Noise Type Selection */}
        <div className="space-y-4">
          <div className="flex items-center">
            <Hash className="h-5 w-5 text-gray-600 mr-2" />
            <h4 className="text-md font-semibold text-gray-900">Noise Mechanism</h4>
          </div>
          
          <div className="space-y-3">
            <div className="flex items-center">
              <input
                id="laplace"
                name="noiseType"
                type="radio"
                value="laplace"
                checked={privacyConfig.noiseType === 'laplace'}
                onChange={(e) => updatePrivacyConfig({ noiseType: e.target.value })}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
              />
              <label htmlFor="laplace" className="ml-3 text-sm">
                <span className="font-medium text-gray-900">Laplace Noise</span>
                <p className="text-gray-600">Standard differential privacy mechanism</p>
              </label>
            </div>
            
            <div className="flex items-center">
              <input
                id="gaussian"
                name="noiseType"
                type="radio"
                value="gaussian"
                checked={privacyConfig.noiseType === 'gaussian'}
                onChange={(e) => updatePrivacyConfig({ noiseType: e.target.value })}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
              />
              <label htmlFor="gaussian" className="ml-3 text-sm">
                <span className="font-medium text-gray-900">Gaussian Noise</span>
                <p className="text-gray-600">Alternative mechanism with different noise distribution</p>
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Additional Privacy Options */}
      <div className="space-y-4">
        <h4 className="text-md font-semibold text-gray-900">Additional Privacy Options</h4>
        
        <div className="space-y-3">
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center">
              <input
                id="hashPatterns"
                type="checkbox"
                checked={privacyConfig.hashPatterns}
                onChange={(e) => updatePrivacyConfig({ hashPatterns: e.target.checked })}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="hashPatterns" className="ml-3">
                <span className="font-medium text-gray-900">Hash Pattern Names</span>
                <p className="text-sm text-gray-600">Replace item names with secure hashes before sharing</p>
              </label>
            </div>
            <Info className="h-5 w-5 text-gray-400" />
          </div>
        </div>
      </div>

      {/* Privacy Impact Visualization */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h4 className="text-md font-semibold text-gray-900 mb-4">Privacy Impact Preview</h4>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {Math.round((privacyConfig.epsilon / 3.0) * 100)}%
            </div>
            <div className="text-sm text-gray-600">Data Accuracy</div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div 
                className="bg-blue-600 h-2 rounded-full"
                style={{ width: `${(privacyConfig.epsilon / 3.0) * 100}%` }}
              ></div>
            </div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {Math.round((1 - privacyConfig.epsilon / 3.0) * 100)}%
            </div>
            <div className="text-sm text-gray-600">Privacy Level</div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div 
                className="bg-green-600 h-2 rounded-full"
                style={{ width: `${(1 - privacyConfig.epsilon / 3.0) * 100}%` }}
              ></div>
            </div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              {Math.round((1 / privacyConfig.epsilon) * 10)}%
            </div>
            <div className="text-sm text-gray-600">Noise Added</div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div 
                className="bg-purple-600 h-2 rounded-full"
                style={{ width: `${Math.min((1 / privacyConfig.epsilon) * 10, 100)}%` }}
              ></div>
            </div>
          </div>
        </div>
        
        <div className="mt-4 text-sm text-gray-600 text-center">
          Current settings will add approximately {((1 / privacyConfig.epsilon) * 10).toFixed(1)}% noise to your patterns
        </div>
      </div>

      {/* Privacy Recommendations */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <div className="flex items-start">
          <Info className="h-5 w-5 text-yellow-600 mr-3 mt-0.5" />
          <div>
            <h4 className="text-md font-semibold text-yellow-800 mb-2">Privacy Recommendations</h4>
            <ul className="text-sm text-yellow-700 space-y-1">
              <li>• For sensitive retail data, use ε ≤ 1.0 for strong privacy protection</li>
              <li>• Laplace noise is recommended for most use cases</li>
              <li>• Enable pattern hashing for additional anonymization</li>
              <li>• Consider the trade-off between privacy and utility for your specific needs</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PrivacyTab;