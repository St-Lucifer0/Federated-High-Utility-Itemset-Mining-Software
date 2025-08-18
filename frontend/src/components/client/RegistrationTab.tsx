import React, { useState } from 'react';
import { Store, Wifi, WifiOff, CheckCircle, AlertCircle, Loader } from 'lucide-react';
import { apiService, StoreRegistration } from '../../services/api';

interface RegistrationTabProps {
  onRegistrationSuccess: (storeId: string, storeName: string) => void;
}

const RegistrationTab: React.FC<RegistrationTabProps> = ({ onRegistrationSuccess }) => {
  const [registration, setRegistration] = useState<StoreRegistration>({
    store_id: '',
    store_name: ''
  });
  const [isRegistering, setIsRegistering] = useState(false);
  const [registrationStatus, setRegistrationStatus] = useState<{
    type: 'success' | 'error' | null;
    message: string;
  }>({ type: null, message: '' });
  const [isConnected, setIsConnected] = useState(false);

  const handleInputChange = (field: keyof StoreRegistration, value: string) => {
    setRegistration(prev => ({
      ...prev,
      [field]: value
    }));
    // Clear status when user starts typing
    if (registrationStatus.type) {
      setRegistrationStatus({ type: null, message: '' });
    }
  };

  const validateForm = (): boolean => {
    if (!registration.store_id.trim()) {
      setRegistrationStatus({
        type: 'error',
        message: 'Store ID is required'
      });
      return false;
    }
    if (!registration.store_name.trim()) {
      setRegistrationStatus({
        type: 'error',
        message: 'Store Name is required'
      });
      return false;
    }
    return true;
  };

  const handleRegister = async () => {
    if (!validateForm()) return;

    setIsRegistering(true);
    setRegistrationStatus({ type: null, message: '' });

    try {
      const response = await apiService.registerStore(registration);
      
      setRegistrationStatus({
        type: 'success',
        message: `Successfully registered as ${response.store_name} (ID: ${response.store_id})`
      });
      
      setIsConnected(true);
      onRegistrationSuccess(response.store_id, response.store_name);
      
      // Start heartbeat to maintain connection
      startHeartbeat(response.store_id);
      
    } catch (error) {
      setRegistrationStatus({
        type: 'error',
        message: error instanceof Error ? error.message : 'Registration failed'
      });
      setIsConnected(false);
    } finally {
      setIsRegistering(false);
    }
  };

  const startHeartbeat = (storeId: string) => {
    // Send heartbeat every 30 seconds to maintain active status
    const heartbeatInterval = setInterval(async () => {
      try {
        await apiService.sendHeartbeat(storeId);
        setIsConnected(true);
      } catch (error) {
        console.error('Heartbeat failed:', error);
        setIsConnected(false);
        clearInterval(heartbeatInterval);
      }
    }, 30000);

    // Store interval ID for cleanup
    (window as any).heartbeatInterval = heartbeatInterval;
  };

  const testConnection = async () => {
    try {
      const response = await fetch('http://localhost:8001/health');
      if (response.ok) {
        setRegistrationStatus({
          type: 'success',
          message: 'Connection to server successful!'
        });
      } else {
        throw new Error(`Server responded with status: ${response.status}`);
      }
    } catch (error) {
      console.error('Connection test error:', error);
      setRegistrationStatus({
        type: 'error',
        message: `Cannot connect to server: ${error instanceof Error ? error.message : 'Unknown error'}`
      });
    }
  };

  return (
    <div className="space-y-6">
      {/* Connection Status */}
      <div className={`p-4 rounded-lg border-2 ${
        isConnected 
          ? 'bg-green-50 border-green-200' 
          : 'bg-gray-50 border-gray-200'
      }`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {isConnected ? (
              <Wifi className="h-6 w-6 text-green-600" />
            ) : (
              <WifiOff className="h-6 w-6 text-gray-400" />
            )}
            <div>
              <h3 className="font-semibold text-gray-900">
                {isConnected ? 'Connected to Server' : 'Not Connected'}
              </h3>
              <p className="text-sm text-gray-600">
                {isConnected 
                  ? 'Your store is registered and active'
                  : 'Register your store to connect to the regional coordinator'
                }
              </p>
            </div>
          </div>
          <button
            onClick={testConnection}
            className="px-4 py-2 text-sm bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-colors"
          >
            Test Connection
          </button>
        </div>
      </div>

      {/* Registration Status */}
      {registrationStatus.type && (
        <div className={`p-4 rounded-lg border ${
          registrationStatus.type === 'success'
            ? 'bg-green-50 border-green-200'
            : 'bg-red-50 border-red-200'
        }`}>
          <div className="flex items-center">
            {registrationStatus.type === 'success' ? (
              <CheckCircle className="h-5 w-5 text-green-600 mr-3" />
            ) : (
              <AlertCircle className="h-5 w-5 text-red-600 mr-3" />
            )}
            <p className={`text-sm font-medium ${
              registrationStatus.type === 'success' ? 'text-green-800' : 'text-red-800'
            }`}>
              {registrationStatus.message}
            </p>
          </div>
        </div>
      )}

      {/* Registration Form */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="flex items-center mb-6">
          <Store className="h-6 w-6 text-blue-600 mr-3" />
          <h2 className="text-xl font-semibold text-gray-900">Store Registration</h2>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Store ID *
            </label>
            <input
              type="text"
              value={registration.store_id}
              onChange={(e) => handleInputChange('store_id', e.target.value)}
              placeholder="Enter unique store identifier (e.g., STORE001)"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              disabled={isRegistering || isConnected}
            />
            <p className="text-xs text-gray-500 mt-1">
              This should be a unique identifier for your store
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Store Name *
            </label>
            <input
              type="text"
              value={registration.store_name}
              onChange={(e) => handleInputChange('store_name', e.target.value)}
              placeholder="Enter store display name (e.g., Downtown Branch)"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              disabled={isRegistering || isConnected}
            />
            <p className="text-xs text-gray-500 mt-1">
              This is the display name that will appear on the server dashboard
            </p>
          </div>
        </div>

        <div className="mt-6">
          <button
            onClick={handleRegister}
            disabled={isRegistering || isConnected || !registration.store_id.trim() || !registration.store_name.trim()}
            className={`w-full flex items-center justify-center px-4 py-3 rounded-md font-medium transition-all ${
              isConnected
                ? 'bg-green-100 text-green-700 cursor-not-allowed'
                : isRegistering
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700 shadow-lg hover:shadow-xl'
            }`}
          >
            {isRegistering ? (
              <>
                <Loader className="h-5 w-5 mr-2 animate-spin" />
                Registering...
              </>
            ) : isConnected ? (
              <>
                <CheckCircle className="h-5 w-5 mr-2" />
                Registered & Connected
              </>
            ) : (
              <>
                <Store className="h-5 w-5 mr-2" />
                Register Store
              </>
            )}
          </button>
        </div>
      </div>

      {/* Information Panel */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-blue-800 mb-2">How Registration Works</h4>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• Your store will be registered with the regional coordinator</li>
          <li>• Connection status is automatically tracked and updated</li>
          <li>• The server dashboard will show your store as active when connected</li>
          <li>• Heartbeat signals are sent every 30 seconds to maintain connection</li>
          <li>• You can start uploading transactions and mining patterns after registration</li>
        </ul>
      </div>
    </div>
  );
};

export default RegistrationTab;
