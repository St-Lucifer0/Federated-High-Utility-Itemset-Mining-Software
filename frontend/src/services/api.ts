/**
 * API Service Layer for HUI Federated Learning System
 * Handles all communication with the Node.js/Express backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api';

// Add a connection test function
export const testConnection = async (): Promise<boolean> => {
  try {
    const response = await fetch('http://localhost:8001/health', {
      method: 'GET',
      mode: 'cors',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return response.ok;
  } catch (error) {
    console.error('Connection test failed:', error);
    return false;
  }
};

export interface Transaction {
  id?: string;
  items: string[];
  quantities: number[];
  unit_utilities: number[];
  total_utility?: number;
  transaction_date?: string;
}

export interface MiningRequest {
  store_id: string;
  min_utility: number;
  min_support?: number;
  max_pattern_length?: number;
  use_pruning?: boolean;
  batch_size?: number;
}

export interface MiningJob {
  job_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  started_at?: string;
  completed_at?: string;
  execution_time_seconds?: number;
  patterns_found?: number;
  error_message?: string;
}

export interface Pattern {
  items: string[];
  utility: number;
  support: number;
  confidence: number;
}

export interface Store {
  id: string;
  name: string;
  location: string;
  is_active: boolean;
  transaction_count: number;
  ip_address?: string;
  connection_status: 'active' | 'inactive';
  last_seen?: string;
  created_at?: string;
}

export interface StoreRegistration {
  store_id: string;
  store_name: string;
}

export interface FederatedRound {
  id: string;
  round_number: number;
  status: 'pending' | 'running' | 'completed' | 'failed';
  participating_clients: number;
  started_at?: string;
  completed_at?: string;
  patterns_aggregated: number;
}

class ApiService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      mode: 'cors',
      credentials: 'include',
      ...options,
    };

    try {
      console.log(`Making API request to: ${url}`, config);
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error(`API error response:`, errorData);
        throw new Error(errorData.detail || errorData.message || `HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      console.log(`API request successful: ${endpoint}`, result);
      return result;
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Failed to connect to server. Please ensure the backend is running on port 8001.');
      }
      if (error instanceof Error && error.message.includes('NetworkError')) {
        throw new Error('Network error: Cannot connect to backend server.');
      }
      throw error;
    }
  }

  // Transaction Management
  async uploadTransactions(storeId: string, transactions: Transaction[]): Promise<{ message: string; store_id: string }> {
    return this.request(`/transactions/upload/${storeId}`, {
      method: 'POST',
      body: JSON.stringify(transactions),
    });
  }

  async getTransactions(storeId: string, limit: number = 100): Promise<{ transactions: Transaction[]; count: number }> {
    return this.request(`/transactions/${storeId}?limit=${limit}`);
  }

  // Mining Operations
  async startMining(request: MiningRequest): Promise<{ job_id: string; status: string }> {
    return this.request('/mining/start', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getMiningStatus(jobId: string): Promise<MiningJob> {
    return this.request(`/mining/status/${jobId}`);
  }

  async getMiningResults(jobId: string): Promise<{ patterns: Pattern[]; count: number }> {
    return this.request(`/mining/results/${jobId}`);
  }

  // Federated Learning
  async startFederatedRound(minClients: number = 2, privacyBudget: number = 1.0): Promise<{ round_id: string; status: string }> {
    return this.request('/federated/start-round', {
      method: 'POST',
      body: JSON.stringify({
        min_clients: minClients,
        privacy_budget: privacyBudget,
      }),
    });
  }

  async getFederatedRounds(): Promise<{ rounds: FederatedRound[] }> {
    return this.request('/federated/rounds');
  }

  // Store Management
  async getStores(): Promise<{ stores: Store[] }> {
    return this.request('/stores');
  }

  async registerStore(registration: StoreRegistration): Promise<{ message: string; store_id: string; store_name: string; status: string }> {
    return this.request('/stores/register', {
      method: 'POST',
      body: JSON.stringify(registration),
    });
  }

  async sendHeartbeat(storeId: string): Promise<{ message: string; store_id: string; status: string; timestamp: string }> {
    return this.request(`/stores/${storeId}/heartbeat`, {
      method: 'POST',
    });
  }

  // Utility methods
  async healthCheck(): Promise<{ message: string; version: string; status: string; timestamp: string }> {
    return fetch(`${API_BASE_URL.replace('/api', '')}/`).then(res => res.json());
  }
}

export const apiService = new ApiService();
export default apiService;
