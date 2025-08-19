import React, { useState, useRef } from 'react';
import { Upload, Plus, Trash2, CheckCircle, AlertCircle } from 'lucide-react';
import { apiService, Transaction } from '../../services/api';

interface UploadTabProps {
  clientData: any;
  setClientData: (data: any) => void;
}

const UploadTab: React.FC<UploadTabProps> = ({ clientData, setClientData }) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [manualTransaction, setManualTransaction] = useState({
    items: '',
    quantities: '',
    unitUtilities: ''
  });
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const validateTransaction = (items: string[], quantities: number[], unitUtilities: number[]): string[] => {
    const errors: string[] = [];
    
    if (!items.length) errors.push('Items cannot be empty');
    if (!quantities.length) errors.push('Quantities cannot be empty');
    if (!unitUtilities.length) errors.push('Unit utilities cannot be empty');
    
    if (items.length !== quantities.length || items.length !== unitUtilities.length) {
      errors.push('Items, quantities, and utilities must have the same length');
    }
    
    quantities.forEach((qty, idx) => {
      if (qty <= 0) errors.push(`Quantity for item ${idx + 1} must be positive`);
    });
    
    unitUtilities.forEach((util, idx) => {
      if (util <= 0) errors.push(`Unit utility for item ${idx + 1} must be positive`);
    });
    
    return errors;
  };

  const parseCSV = (csvText: string): Transaction[] => {
    const lines = csvText.trim().split('\n');
    if (lines.length < 2) {
      setValidationErrors(['CSV file must have at least a header and one data row']);
      return [];
    }
    
    const transactions: Transaction[] = [];
    const errors: string[] = [];
    
    // Skip header line
    for (let i = 1; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line) continue;
      
      try {
        // Parse CSV line (simple implementation)
        const parts = line.split(',').map(p => p.trim().replace(/^"|"/g, ''));
        
        if (parts.length !== 3) {
          errors.push(`Line ${i + 1}: Expected 3 columns (items, quantities, unit_utilities)`);
          continue;
        }
        
        const items = parts[0].split('|').map(item => item.trim());
        const quantities = parts[1].split('|').map(q => parseFloat(q.trim()));
        const unit_utilities = parts[2].split('|').map(u => parseFloat(u.trim()));
        
        const validationErrors = validateTransaction(items, quantities, unit_utilities);
        if (validationErrors.length > 0) {
          errors.push(`Line ${i + 1}: ${validationErrors.join(', ')}`);
          continue;
        }
        
        const total_utility = quantities.reduce((sum, qty, idx) => sum + (qty * unit_utilities[idx]), 0);
        
        transactions.push({
          items,
          quantities,
          unit_utilities,
          total_utility
        });
      } catch (error) {
        errors.push(`Line ${i + 1}: Failed to parse - ${error}`);
      }
    }
    
    if (errors.length > 0) {
      setValidationErrors(errors);
      return [];
    }
    
    return transactions;
  };

  const uploadTransactionsToAPI = async (transactions: Transaction[]) => {
    try {
      setUploadStatus('uploading');
      
      // Check if store is registered
      if (!clientData.storeId) {
        throw new Error('Please register your store first in the Registration tab');
      }
      
      console.log(`Uploading ${transactions.length} transactions for store: ${clientData.storeId}`);
      await apiService.uploadTransactions(clientData.storeId, transactions);
      
      // Refresh transactions from API
      const response = await apiService.getTransactions(clientData.storeId);
      setClientData((prev: any) => ({
        ...prev,
        transactions: response.transactions
      }));
      
      setUploadStatus('success');
    } catch (error) {
      console.error('Upload failed:', error);
      console.error('Error details:', error);
      setUploadStatus('error');
      
      // More detailed error handling
      let errorMessage = 'Upload failed';
      if (error instanceof Error) {
        errorMessage = error.message;
        // If it's a validation error, try to extract more details
        if (error.message.includes('HTTP error! status: 400')) {
          errorMessage = 'Validation error: Please check your transaction data format';
        }
      }
      
      setValidationErrors([errorMessage]);
    }
  };

  const parseJSON = (jsonText: string): Transaction[] => {
    try {
      const data = JSON.parse(jsonText);
      const transactions: Transaction[] = [];
      const errors: string[] = [];
      
      if (!Array.isArray(data)) {
        throw new Error('JSON must be an array of transactions');
      }
      
      data.forEach((item, idx) => {
        if (!item.items || !item.quantities || !item.unit_utilities) {
          errors.push(`Transaction ${idx + 1}: Missing required fields`);
          return;
        }
        
        const validationErrors = validateTransaction(item.items, item.quantities, item.unit_utilities);
        if (validationErrors.length > 0) {
          errors.push(`Transaction ${idx + 1}: ${validationErrors.join(', ')}`);
          return;
        }
        
        const totalUtility = item.quantities.reduce((sum: number, qty: number, i: number) => 
          sum + (qty * item.unit_utilities[i]), 0
        );
        
        transactions.push({
          id: `txn_${Date.now()}_${idx}`,
          items: item.items,
          quantities: item.quantities,
          unit_utilities: item.unit_utilities,
          total_utility: totalUtility
        });
      });
      
      if (errors.length > 0) {
        setValidationErrors(errors);
        return [];
      }
      
      return transactions;
    } catch (error) {
      setValidationErrors([`JSON parsing error: ${error}`]);
      return [];
    }
  };

  const handleFileDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length === 0) return;
    
    const file = files[0];
    if (!file.name.endsWith('.csv')) {
      setValidationErrors(['Please upload a CSV file']);
      return;
    }
    
    const text = await file.text();
    const parsedTransactions = parseCSV(text);
    
    if (parsedTransactions.length > 0) {
      await uploadTransactionsToAPI(parsedTransactions);
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files[0]) {
      const file = files[0];
      if (!file.name.endsWith('.csv') && !file.name.endsWith('.json')) {
        setValidationErrors(['Please upload a CSV or JSON file']);
        return;
      }
      
      const text = await file.text();
      let parsedTransactions: Transaction[] = [];
      
      if (file.name.endsWith('.csv')) {
        parsedTransactions = parseCSV(text);
      } else if (file.name.endsWith('.json')) {
        parsedTransactions = parseJSON(text);
      }
      
      if (parsedTransactions.length > 0) {
        await uploadTransactionsToAPI(parsedTransactions);
      }
    }
  };

  const addManualTransaction = async () => {
    const items = manualTransaction.items.split(',').map(item => item.trim()).filter(item => item);
    const quantities = manualTransaction.quantities.split(',').map(q => parseFloat(q.trim())).filter(q => !isNaN(q));
    const unit_utilities = manualTransaction.unitUtilities.split(',').map(u => parseFloat(u.trim())).filter(u => !isNaN(u));
    
    const errors = validateTransaction(items, quantities, unit_utilities);
    if (errors.length > 0) {
      setValidationErrors(errors);
      return;
    }
    
    const total_utility = quantities.reduce((sum, qty, idx) => sum + (qty * unit_utilities[idx]), 0);
    
    const newTransaction: Transaction = {
      items,
      quantities,
      unit_utilities,
      total_utility
    };
    
    await uploadTransactionsToAPI([newTransaction]);
    
    // Reset form
    setManualTransaction({ items: '', quantities: '', unitUtilities: '' });
    setValidationErrors([]);
  };

  const deleteTransaction = async (id: string) => {
    // For now, just remove from local state
    // In a full implementation, you'd call an API to delete from backend
    setClientData({
      ...clientData,
      transactions: clientData.transactions.filter((t: Transaction) => t.id !== id)
    });
  };

  return (
    <div className="space-y-6">
      {/* File Upload Section */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Upload Transaction Data</h3>
        
        <div
          className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            dragActive 
              ? 'border-blue-400 bg-blue-50' 
              : 'border-gray-300 hover:border-gray-400'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleFileDrop}
        >
          <Upload className="mx-auto h-12 w-12 text-gray-400" />
          <div className="mt-4">
            <p className="text-lg font-medium text-gray-900">
              Drop files here or click to browse
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Supports CSV and JSON formats
            </p>
          </div>
          
          <input
            ref={fileInputRef}
            type="file"
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            accept=".csv,.json"
            onChange={handleFileSelect}
          />
          
          <button
            onClick={() => fileInputRef.current?.click()}
            className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
          >
            Select Files
          </button>
        </div>
        
        {/* Upload Status */}
        {uploadStatus !== 'idle' && (
          <div className={`flex items-center p-4 rounded-md ${
            uploadStatus === 'success' ? 'bg-green-50 text-green-800' :
            uploadStatus === 'error' ? 'bg-red-50 text-red-800' :
            'bg-blue-50 text-blue-800'
          }`}>
            {uploadStatus === 'success' && <CheckCircle className="h-5 w-5 mr-2" />}
            {uploadStatus === 'error' && <AlertCircle className="h-5 w-5 mr-2" />}
            
            {uploadStatus === 'uploading' && 'Processing file...'}
            {uploadStatus === 'success' && 'File uploaded successfully!'}
            {uploadStatus === 'error' && 'Upload failed. Please check the errors below.'}
          </div>
        )}
        
        {/* Validation Errors */}
        {validationErrors.length > 0 && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <h4 className="text-red-800 font-medium mb-2">Validation Errors:</h4>
            <ul className="text-red-700 text-sm space-y-1">
              {validationErrors.map((error, idx) => (
                <li key={idx}>• {error}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Manual Entry Section */}
      <div className="border-t pt-6 space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Manual Transaction Entry</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Items (comma-separated)
            </label>
            <input
              type="text"
              value={manualTransaction.items}
              onChange={(e) => setManualTransaction({...manualTransaction, items: e.target.value})}
              placeholder="bread, butter, milk"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Quantities (comma-separated)
            </label>
            <input
              type="text"
              value={manualTransaction.quantities}
              onChange={(e) => setManualTransaction({...manualTransaction, quantities: e.target.value})}
              placeholder="2, 1, 3"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Unit Utilities (comma-separated)
            </label>
            <input
              type="text"
              value={manualTransaction.unitUtilities}
              onChange={(e) => setManualTransaction({...manualTransaction, unitUtilities: e.target.value})}
              placeholder="5.0, 3.0, 2.0"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        
        <button
          onClick={addManualTransaction}
          className="flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
        >
          <Plus className="h-4 w-4 mr-2" />
          Add Transaction
        </button>
      </div>

      {/* Transaction Preview */}
      {clientData.transactions.length > 0 && (
        <div className="border-t pt-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">
              Transaction Preview ({clientData.transactions.length} transactions)
            </h3>
            <div className="text-sm text-gray-500">
              Total Utility: {clientData.transactions.reduce((sum: number, t: Transaction) => sum + (t.total_utility || 0), 0).toFixed(2)}
            </div>
          </div>
          
          <div className="max-h-96 overflow-y-auto border border-gray-200 rounded-md">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Items
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Quantities
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Unit Utilities
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Total Utility
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {clientData.transactions.slice(0, 10).map((transaction: Transaction) => (
                  <tr key={transaction.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {transaction.items.join(', ')}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {transaction.quantities.join(', ')}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {transaction.unit_utilities?.map((u: number) => u.toFixed(2)).join(', ') || 'N/A'}
                    </td>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">
                      {transaction.total_utility?.toFixed(2) || 'N/A'}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      <button
                        onClick={() => deleteTransaction(transaction.id || '')}
                        className="text-red-600 hover:text-red-800 transition-colors"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            {clientData.transactions.length > 10 && (
              <div className="px-4 py-3 bg-gray-50 text-sm text-gray-500 text-center">
                Showing first 10 of {clientData.transactions.length} transactions
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadTab;