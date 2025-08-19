import { useState } from 'react';
import { Users, Server, Database } from 'lucide-react';
import ClientDashboard from './components/ClientDashboard';
import ServerDashboard from './components/ServerDashboard';

function App() {
  const [currentRole, setCurrentRole] = useState<'client' | 'server'>('client');
  
  // Check if this is a client-only deployment
  const isClientOnly = import.meta.env.VITE_CLIENT_ONLY === 'true' || 
                       localStorage.getItem('clientOnlyMode') === 'true';

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Database className="h-8 w-8 text-blue-600 mr-3" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  Federated HUIM System
                </h1>
                <p className="text-sm text-gray-500">
                  High Utility Itemset Mining for Retail Stores
                </p>
              </div>
            </div>
            
            {/* Role Switcher */}
            <div className="flex items-center space-x-2">
              {!isClientOnly && (
                <div className="flex bg-gray-100 rounded-lg p-1">
                  <button
                    onClick={() => setCurrentRole('client')}
                    className={`flex items-center px-4 py-2 rounded-md text-sm font-medium transition-all ${
                      currentRole === 'client'
                        ? 'bg-white text-blue-600 shadow-sm'
                        : 'text-gray-600 hover:text-gray-800'
                    }`}
                  >
                    <Users className="h-4 w-4 mr-2" />
                    Store Manager
                  </button>
                  <button
                    onClick={() => setCurrentRole('server')}
                    className={`flex items-center px-4 py-2 rounded-md text-sm font-medium transition-all ${
                      currentRole === 'server'
                        ? 'bg-white text-blue-600 shadow-sm'
                        : 'text-gray-600 hover:text-gray-800'
                    }`}
                  >
                    <Server className="h-4 w-4 mr-2" />
                    Regional Coordinator
                  </button>
                </div>
              )}
              {isClientOnly && (
                <div className="flex items-center px-4 py-2 bg-blue-50 rounded-lg">
                  <Users className="h-4 w-4 mr-2 text-blue-600" />
                  <span className="text-sm font-medium text-blue-800">Store Manager Mode</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {(currentRole === 'client' || isClientOnly) ? <ClientDashboard /> : <ServerDashboard />}
      </main>
    </div>
  );
}

export default App;