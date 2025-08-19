import React, { useState } from 'react';
import { Users, RotateCcw, TrendingUp, Settings, History, Download } from 'lucide-react';

interface Client {
  id: string;
  name: string;
  status: 'active' | 'mining' | 'offline';
  lastSeen: Date;
  transactionCount: number;
  patternsSent: number;
  location: string;
}
import ClientStatusTab from './server/ClientStatusTab';
import FederatedRoundsTab from './server/FederatedRoundsTab';
import GlobalPatternsTab from './server/GlobalPatternsTab';
import ServerConfigTab from './server/ServerConfigTab';
import JobHistoryTab from './server/JobHistoryTab';
import DownloadReportsTab from './server/DownloadReportsTab';

const tabs = [
  { id: 'clients', name: 'Client Status', icon: Users },
  { id: 'rounds', name: 'Federated Rounds', icon: RotateCcw },
  { id: 'patterns', name: 'Global Patterns', icon: TrendingUp },
  { id: 'config', name: 'Server Config', icon: Settings },
  { id: 'history', name: 'Job History', icon: History },
  { id: 'reports', name: 'Download Reports', icon: Download },
];

const ServerDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('clients');
  const [serverData, setServerData] = useState({
    clients: [] as Client[],
    globalPatterns: [],
    jobHistory: [],
    serverConfig: {
      minUtility: 0,
      minSupport: 0,
      privacyBudget: 0,
      minClientsPerRound: 0,
      maxPatternLength: 0,
      noiseLevel: 0
    },
    currentRound: 0,
    systemUptime: Date.now()
  });

  const renderTabContent = () => {
    switch (activeTab) {
      case 'clients':
        return <ClientStatusTab serverData={serverData} setServerData={setServerData} />;
      case 'rounds':
        return <FederatedRoundsTab serverData={serverData} setServerData={setServerData} />;
      case 'patterns':
        return <GlobalPatternsTab serverData={serverData} setServerData={setServerData} />;
      case 'config':
        return <ServerConfigTab serverData={serverData} setServerData={setServerData} />;
      case 'history':
        return <JobHistoryTab serverData={serverData} setServerData={setServerData} />;
      case 'reports':
        return <DownloadReportsTab serverData={serverData} setServerData={setServerData} />;
      default:
        return <ClientStatusTab serverData={serverData} setServerData={setServerData} />;
    }
  };

  const activeClients = serverData.clients.filter(c => c.status === 'active' || c.status === 'mining').length;

  return (
    <div className="space-y-6">
      {/* Server Status Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Regional Coordinator</h2>
            <p className="text-gray-600 mt-1">
              Manage federated learning and global pattern aggregation
            </p>
          </div>
          <div className="grid grid-cols-4 gap-6 text-sm text-gray-500">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{activeClients}</div>
              <div>Active Clients</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{serverData.currentRound}</div>
              <div>Current Round</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{serverData.globalPatterns.length}</div>
              <div>Global Patterns</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">{serverData.jobHistory.length}</div>
              <div>Completed Jobs</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex flex-wrap gap-2 sm:gap-4 lg:gap-8 px-4 sm:px-6 overflow-x-auto" aria-label="Tabs">
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
                  } whitespace-nowrap py-4 px-1 sm:px-2 border-b-2 font-medium text-xs sm:text-sm flex items-center transition-colors flex-shrink-0`}
                >
                  <Icon className="h-3 w-3 sm:h-4 sm:w-4 mr-1 sm:mr-2" />
                  <span className="hidden sm:inline">{tab.name}</span>
                  <span className="sm:hidden">{tab.name.split(' ')[0]}</span>
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

export default ServerDashboard;