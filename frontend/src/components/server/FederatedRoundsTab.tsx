import React, { useState, useEffect } from 'react';
import { Play, Users, Clock, TrendingUp, AlertCircle, CheckCircle, RotateCcw } from 'lucide-react';
import { apiService } from '../../services/api';

interface FederatedRoundsTabProps {
  serverData: any;
  setServerData: (data: any) => void;
}

const FederatedRoundsTab: React.FC<FederatedRoundsTabProps> = ({ serverData, setServerData }) => {
  const [isRunningRound, setIsRunningRound] = useState(false);
  const [roundProgress, setRoundProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState('');
  const [federatedRounds, setFederatedRounds] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const activeClients = serverData.clients.filter((c: any) => c.status === 'active' || c.status === 'mining');
  const minClientsRequired = serverData.serverConfig.minClientsPerRound || 2;
  const canStartRound = activeClients.length >= minClientsRequired;

  // Load federated rounds on component mount
  useEffect(() => {
    loadFederatedRounds();
  }, []);

  const loadFederatedRounds = async () => {
    try {
      setLoading(true);
      const response = await apiService.getFederatedRounds();
      setFederatedRounds(response.rounds || []);
      
      // Update server data with latest round info
      if (response.rounds && response.rounds.length > 0) {
        const latestRound = response.rounds[0];
        setServerData((prev: any) => ({
          ...prev,
          currentRound: latestRound.round_number || 0,
          jobHistory: response.rounds.map((round: any) => ({
            id: round.id,
            round: round.round_number,
            timestamp: new Date(round.started_at || Date.now()),
            clientCount: round.participating_clients,
            patternsFound: round.patterns_aggregated,
            duration: round.completed_at && round.started_at ? 
              (new Date(round.completed_at).getTime() - new Date(round.started_at).getTime()) / 1000 : 0
          }))
        }));
      }
    } catch (error) {
      console.error('Failed to load federated rounds:', error);
    } finally {
      setLoading(false);
    }
  };

  const startFederatedRound = async () => {
    if (!canStartRound) {
      alert(`Need at least ${minClientsRequired} active clients to start a round`);
      return;
    }

    setIsRunningRound(true);
    setRoundProgress(0);
    setCurrentStep('Initiating federated learning round...');

    try {
      const response = await apiService.startFederatedRound(activeClients.length, serverData.serverConfig.privacyBudget || 1.0);
      
      setCurrentStep('Federated round started successfully');
      setRoundProgress(100);
      
      // Refresh the rounds list
      setTimeout(() => {
        loadFederatedRounds();
        setIsRunningRound(false);
        setCurrentStep('');
        setRoundProgress(0);
      }, 2000);
      
    } catch (error) {
      console.error('Failed to start federated round:', error);
      setCurrentStep('Failed to start federated round');
      setTimeout(() => {
        setIsRunningRound(false);
        setCurrentStep('');
        setRoundProgress(0);
      }, 2000);
    }
  };

  const getRoundStatus = () => {
    if (isRunningRound) return 'running';
    if (!canStartRound) return 'waiting';
    return 'ready';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'bg-blue-100 text-blue-800';
      case 'waiting':
        return 'bg-yellow-100 text-yellow-800';
      case 'ready':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <RotateCcw className="h-5 w-5 text-blue-600 animate-spin" />;
      case 'waiting':
        return <AlertCircle className="h-5 w-5 text-yellow-600" />;
      case 'ready':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      default:
        return <Clock className="h-5 w-5 text-gray-600" />;
    }
  };

  const currentStatus = getRoundStatus();

  return (
    <div className="space-y-6">
      {/* Round Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="flex items-center">
            <RotateCcw className="h-5 w-5 text-blue-600 mr-2" />
            <span className="text-sm font-medium text-blue-900">Current Round</span>
          </div>
          <div className="text-2xl font-bold text-blue-600 mt-1">
            {serverData.currentRound}
          </div>
        </div>
        
        <div className="bg-green-50 p-4 rounded-lg">
          <div className="flex items-center">
            <Users className="h-5 w-5 text-green-600 mr-2" />
            <span className="text-sm font-medium text-green-900">Active Participants</span>
          </div>
          <div className="text-2xl font-bold text-green-600 mt-1">
            {activeClients.length}
          </div>
        </div>
        
        <div className="bg-purple-50 p-4 rounded-lg">
          <div className="flex items-center">
            <TrendingUp className="h-5 w-5 text-purple-600 mr-2" />
            <span className="text-sm font-medium text-purple-900">Patterns Found</span>
          </div>
          <div className="text-2xl font-bold text-purple-600 mt-1">
            {serverData.jobHistory.length > 0 ? serverData.jobHistory[0].patternsFound : 0}
          </div>
        </div>
        
        <div className="bg-orange-50 p-4 rounded-lg">
          <div className="flex items-center">
            <Clock className="h-5 w-5 text-orange-600 mr-2" />
            <span className="text-sm font-medium text-orange-900">Last Duration</span>
          </div>
          <div className="text-2xl font-bold text-orange-600 mt-1">
            {serverData.jobHistory.length > 0 ? `${serverData.jobHistory[0].duration.toFixed(1)}s` : '0s'}
          </div>
        </div>
      </div>

      {/* Current Round Status */}
      <div className={`border rounded-lg p-6 ${
        currentStatus === 'running' ? 'bg-blue-50 border-blue-200' :
        currentStatus === 'waiting' ? 'bg-yellow-50 border-yellow-200' :
        'bg-green-50 border-green-200'
      }`}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            {getStatusIcon(currentStatus)}
            <h3 className="text-lg font-semibold ml-3">
              {currentStatus === 'running' ? 'Federated Round in Progress' :
               currentStatus === 'waiting' ? 'Waiting for Clients' :
               'Ready to Start New Round'}
            </h3>
          </div>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(currentStatus)}`}>
            {currentStatus.charAt(0).toUpperCase() + currentStatus.slice(1)}
          </span>
        </div>

        {currentStatus === 'waiting' && (
          <div className="mb-4">
            <p className="text-yellow-700 mb-2">
              Need {minClientsRequired - activeClients.length} more active client(s) to start a federated round.
            </p>
            <div className="flex items-center space-x-2">
              <div className="flex-1 bg-yellow-200 rounded-full h-2">
                <div 
                  className="bg-yellow-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${(activeClients.length / minClientsRequired) * 100}%` }}
                ></div>
              </div>
              <span className="text-sm text-yellow-700">
                {activeClients.length}/{minClientsRequired}
              </span>
            </div>
          </div>
        )}

        {currentStatus === 'running' && (
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <p className="text-blue-700">{currentStep}</p>
              <span className="text-blue-700 font-medium">{roundProgress}%</span>
            </div>
            <div className="w-full bg-blue-200 rounded-full h-3">
              <div 
                className="bg-blue-600 h-3 rounded-full transition-all duration-300 ease-out"
                style={{ width: `${roundProgress}%` }}
              ></div>
            </div>
          </div>
        )}

        {currentStatus === 'ready' && (
          <div className="mb-4">
            <p className="text-green-700 mb-2">
              All systems ready. {activeClients.length} clients are available for federated learning.
            </p>
          </div>
        )}

        <div className="flex justify-center">
          <button
            onClick={startFederatedRound}
            disabled={!canStartRound || isRunningRound}
            className={`flex items-center px-8 py-3 rounded-lg font-medium text-lg transition-all ${
              !canStartRound || isRunningRound
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700 shadow-lg hover:shadow-xl'
            }`}
          >
            <Play className="h-5 w-5 mr-2" />
            {isRunningRound ? 'Round in Progress...' : 'Start New Federated Round'}
          </button>
        </div>
      </div>

      {/* Participating Clients */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Participating Clients</h4>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {activeClients.map((client: any) => (
            <div key={client.id} className="flex items-center p-4 bg-gray-50 rounded-lg">
              <div className="flex-shrink-0 h-10 w-10">
                <div className="h-10 w-10 rounded-full bg-gradient-to-r from-blue-400 to-blue-600 flex items-center justify-center">
                  <span className="text-white font-medium text-sm">
                    {client.name.split(' ').map((n: string) => n[0]).join('')}
                  </span>
                </div>
              </div>
              <div className="ml-3 flex-1">
                <div className="text-sm font-medium text-gray-900">{client.name}</div>
                <div className="text-xs text-gray-500">{client.transactionCount} transactions</div>
              </div>
              <div className="flex items-center">
                {client.status === 'mining' ? (
                  <div className="h-2 w-2 bg-blue-400 rounded-full animate-pulse"></div>
                ) : (
                  <div className="h-2 w-2 bg-green-400 rounded-full"></div>
                )}
              </div>
            </div>
          ))}
        </div>

        {activeClients.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            No active clients available for federated learning
          </div>
        )}
      </div>

      {/* Recent Rounds History */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Recent Rounds</h4>
        
        <div className="space-y-3">
          {serverData.jobHistory.slice(0, 5).map((job: any) => (
            <div key={job.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-4">
                <div className="flex-shrink-0">
                  <CheckCircle className="h-6 w-6 text-green-600" />
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-900">
                    Round {job.round}
                  </div>
                  <div className="text-xs text-gray-500">
                    {job.timestamp.toLocaleString()}
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-6 text-sm text-gray-600">
                <div className="text-center">
                  <div className="font-medium text-blue-600">{job.clientCount}</div>
                  <div className="text-xs">Clients</div>
                </div>
                <div className="text-center">
                  <div className="font-medium text-green-600">{job.patternsFound}</div>
                  <div className="text-xs">Patterns</div>
                </div>
                <div className="text-center">
                  <div className="font-medium text-purple-600">{job.duration.toFixed(1)}s</div>
                  <div className="text-xs">Duration</div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {serverData.jobHistory.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            No federated rounds completed yet
          </div>
        )}
      </div>
    </div>
  );
};

export default FederatedRoundsTab;