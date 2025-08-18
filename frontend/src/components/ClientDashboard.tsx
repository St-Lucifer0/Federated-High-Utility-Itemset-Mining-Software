import React, { useState, useEffect } from 'react';
import { Upload, Play, Settings, Send, FileDown, Activity, Store } from 'lucide-react';
import RegistrationTab from './client/RegistrationTab';
import UploadTab from './client/UploadTab';
import MineTab from './client/MineTab';
import ResultsTab from './client/ResultsTab';
import PrivacyTab from './client/PrivacyTab';
import SendToServerTab from './client/SendToServerTab';
import LogsTab from './client/LogsTab';
import { apiService, Transaction, Pattern } from '../services/api';

const tabs = [
  { id: 'register', name: 'Register Store', icon: Store },
  { id: 'upload', name: 'Upload Transactions', icon: Upload },
  { id: 'mine', name: 'Mine Itemsets', icon: Play },
  { id: 'results', name: 'Pattern Results', icon: FileDown },
  { id: 'privacy', name: 'Privacy Settings', icon: Settings },
  { id: 'send', name: 'Send to Server', icon: Send },
  { id: 'logs', name: 'View Logs', icon: Activity },
];

const ClientDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('register');
  const [clientData, setClientData] = useState({
    transactions: [] as Transaction[],
    minedPatterns: [] as Pattern[],
    privacyConfig: { 
      epsilon: 1.0, 
      noiseType: 'laplace' as 'laplace' | 'gaussian', 
      hashPatterns: false 
    },
    miningStats: null,
    logs: [] as any[],
    storeId: '', // Will be set after registration
    storeName: '', // Will be set after registration
    isRegistered: false
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRegistrationSuccess = (storeId: string, storeName: string) => {
    setClientData(prev => ({
      ...prev,
      storeId,
      storeName,
      isRegistered: true
    }));
    setActiveTab('upload'); // Switch to upload tab after successful registration
  };

  // Load initial data only if registered
  useEffect(() => {
    if (clientData.isRegistered && clientData.storeId) {
      loadTransactions();
    }
  }, [clientData.isRegistered, clientData.storeId]);

  const loadTransactions = async () => {
    if (!clientData.storeId) return; // Don't load if not registered
    
    try {
      setLoading(true);
      const response = await apiService.getTransactions(clientData.storeId);
      setClientData(prev => ({
        ...prev,
        transactions: response.transactions
      }));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load transactions');
    } finally {
      setLoading(false);
    }
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'register':
        return <RegistrationTab onRegistrationSuccess={handleRegistrationSuccess} />;
      case 'upload':
        return <UploadTab clientData={clientData} setClientData={setClientData} />;
      case 'mine':
        return <MineTab clientData={clientData} setClientData={setClientData} />;
      case 'results':
        return <ResultsTab clientData={clientData} setClientData={setClientData} />;
      case 'privacy':
        return <PrivacyTab clientData={clientData} setClientData={setClientData} />;
      case 'send':
        return <SendToServerTab clientData={clientData} setClientData={setClientData} />;
      case 'logs':
        return <LogsTab clientData={clientData} setClientData={setClientData} />;
      default:
        return <RegistrationTab onRegistrationSuccess={handleRegistrationSuccess} />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Store Info Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Store Dashboard</h2>
            <p className="text-gray-600 mt-1">
              {clientData.isRegistered 
                ? `${clientData.storeName} (${clientData.storeId}) - Manage local transactions and contribute to federated mining`
                : 'Register your store to connect to the regional coordinator'
              }
            </p>
          </div>
          <div className="flex items-center space-x-4 text-sm text-gray-500">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {loading ? '...' : clientData.transactions.length}
              </div>
              <div>Transactions</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {clientData.minedPatterns.length}
              </div>
              <div>Patterns</div>
            </div>
            {error && (
              <div className="text-center">
                <div className="text-sm text-red-600">
                  {error}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6" aria-label="Tabs">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center transition-colors`}
                >
                  <Icon className="h-4 w-4 mr-2" />
                  {tab.name}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {renderTabContent()}
        </div>
      </div>
    </div>
  );
};

export default ClientDashboard;