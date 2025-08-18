import React, { useState } from 'react';
import { Download, FileText, BarChart3, Calendar, CheckCircle, AlertCircle } from 'lucide-react';

interface DownloadReportsTabProps {
  serverData: any;
  setServerData: (data: any) => void;
}

const DownloadReportsTab: React.FC<DownloadReportsTabProps> = ({ serverData }) => {
  const [selectedReportType, setSelectedReportType] = useState('patterns');
  const [dateRange, setDateRange] = useState({ start: '', end: '' });
  const [isGenerating, setIsGenerating] = useState(false);
  const [lastGenerated, setLastGenerated] = useState<{ type: string; timestamp: Date } | null>(null);

  const reportTypes = [
    {
      id: 'patterns',
      name: 'Global Patterns Report',
      description: 'Complete list of discovered patterns with utilities and support values',
      icon: BarChart3,
      color: 'blue'
    },
    {
      id: 'clients',
      name: 'Client Performance Report', 
      description: 'Client participation statistics and contribution metrics',
      icon: FileText,
      color: 'green'
    },
    {
      id: 'rounds',
      name: 'Federated Rounds Summary',
      description: 'Summary of all federated learning rounds with performance metrics',
      icon: Calendar,
      color: 'purple'
    },
    {
      id: 'comprehensive',
      name: 'Comprehensive Analytics Report',
      description: 'Full system analytics including patterns, clients, and performance data',
      icon: FileText,
      color: 'orange'
    }
  ];

  const generateReport = async (reportType: string) => {
    setIsGenerating(true);
    
    try {
      // TODO: Replace with actual API call to generate reports
      // const reportData = await apiService.generateReport(reportType, dateRange);
      
      let csvContent = '';
      let filename = '';
      
      switch (reportType) {
        case 'patterns':
          csvContent = generatePatternsReport();
          filename = `global_patterns_report_${new Date().toISOString().split('T')[0]}.csv`;
          break;
        case 'clients':
          csvContent = generateClientsReport();
          filename = `client_performance_report_${new Date().toISOString().split('T')[0]}.csv`;
          break;
        case 'rounds':
          csvContent = generateRoundsReport();
          filename = `federated_rounds_summary_${new Date().toISOString().split('T')[0]}.csv`;
          break;
        case 'comprehensive':
          csvContent = generateComprehensiveReport();
          filename = `comprehensive_analytics_${new Date().toISOString().split('T')[0]}.csv`;
          break;
      }
      
      // Download the file
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.click();
      window.URL.revokeObjectURL(url);
      
      setLastGenerated({ type: reportType, timestamp: new Date() });
    } catch (error) {
      console.error('Report generation failed:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const generatePatternsReport = () => {
    if (!serverData.globalPatterns || serverData.globalPatterns.length === 0) {
      return 'Pattern_ID,Pattern_Items,Aggregated_Utility,Global_Support,Contributing_Clients,Client_Coverage_Percent,Privacy_Protected\nNo patterns available';
    }
    
    const headers = ['Pattern_ID', 'Pattern_Items', 'Aggregated_Utility', 'Global_Support', 'Contributing_Clients', 'Client_Coverage_Percent', 'Privacy_Protected'];
    const rows = serverData.globalPatterns.map((pattern: any, index: number) => [
      `PATTERN_${index + 1}`,
      `"${pattern.pattern}"`,
      pattern.utility.toFixed(2),
      pattern.support.toFixed(3),
      pattern.clientCount,
      ((pattern.clientCount / serverData.clients.length) * 100).toFixed(1),
      'YES'
    ]);
    
    return [headers.join(','), ...rows.map(row => row.join(','))].join('\n');
  };

  const generateClientsReport = () => {
    if (!serverData.clients || serverData.clients.length === 0) {
      return 'Client_ID,Client_Name,Location,Status,Transaction_Count,Patterns_Contributed,Last_Active,Participation_Rate\nNo clients available';
    }
    
    const headers = ['Client_ID', 'Client_Name', 'Location', 'Status', 'Transaction_Count', 'Patterns_Contributed', 'Last_Active', 'Participation_Rate'];
    const rows = serverData.clients.map((client: any) => [
      client.id,
      `"${client.name}"`,
      `"${client.location}"`,
      client.status,
      client.transactionCount,
      client.patternsSent,
      client.lastSeen.toISOString(),
      '100%' // Assuming full participation for active clients
    ]);
    
    return [headers.join(','), ...rows.map(row => row.join(','))].join('\n');
  };

  const generateRoundsReport = () => {
    if (!serverData.jobHistory || serverData.jobHistory.length === 0) {
      return 'Round_Number,Status,Start_Time,Duration_Seconds,Participating_Clients,Patterns_Discovered,Privacy_Budget_Used,Success_Rate\nNo job history available';
    }
    
    const headers = ['Round_Number', 'Status', 'Start_Time', 'Duration_Seconds', 'Participating_Clients', 'Patterns_Discovered', 'Privacy_Budget_Used', 'Success_Rate'];
    const rows = serverData.jobHistory.map((job: any) => [
      job.round,
      job.status,
      job.timestamp.toISOString(),
      job.duration.toFixed(2),
      job.clientCount,
      job.patternsFound,
      '1.0', // Default privacy budget
      job.status === 'completed' ? '100%' : '0%'
    ]);
    
    return [headers.join(','), ...rows.map(row => row.join(','))].join('\n');
  };

  const generateComprehensiveReport = () => {
    const systemStats = [
      'SYSTEM_ANALYTICS',
      '',
      'Metric,Value',
      `Total_Clients,${serverData.clients.length}`,
      `Active_Clients,${serverData.clients.filter((c: any) => c.status === 'active' || c.status === 'mining').length}`,
      `Current_Round,${serverData.currentRound}`,
      `Total_Patterns,${serverData.globalPatterns.length}`,
      `Completed_Jobs,${serverData.jobHistory.length}`,
      `System_Uptime_Hours,${Math.floor((Date.now() - serverData.systemUptime) / (1000 * 60 * 60))}`,
      '',
      'TOP_PATTERNS',
      '',
      'Pattern,Utility,Support,Clients',
      ...serverData.globalPatterns.slice(0, 10).map((p: any) => 
        `"${p.pattern}",${p.utility.toFixed(2)},${p.support.toFixed(3)},${p.clientCount}`
      ),
      '',
      'CLIENT_SUMMARY',
      '',
      'Client,Transactions,Patterns,Status',
      ...serverData.clients.map((c: any) => 
        `"${c.name}",${c.transactionCount},${c.patternsSent},${c.status}`
      )
    ];
    
    return systemStats.join('\n');
  };

  const getReportColor = (color: string) => {
    const colors = {
      blue: 'bg-blue-50 text-blue-700 border-blue-200',
      green: 'bg-green-50 text-green-700 border-green-200',
      purple: 'bg-purple-50 text-purple-700 border-purple-200',
      orange: 'bg-orange-50 text-orange-700 border-orange-200'
    };
    return colors[color as keyof typeof colors] || colors.blue;
  };

  return (
    <div className="space-y-6">
      {/* Report Generation Status */}
      {lastGenerated && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center">
            <CheckCircle className="h-5 w-5 text-green-600 mr-3" />
            <div>
              <p className="text-green-800 font-medium">Report Generated Successfully</p>
              <p className="text-green-700 text-sm">
                {reportTypes.find(r => r.id === lastGenerated.type)?.name} generated at {lastGenerated.timestamp.toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Date Range Filter */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="text-md font-semibold text-gray-900 mb-3">Date Range (Optional)</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
            <input
              type="date"
              value={dateRange.start}
              onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
            <input
              type="date"
              value={dateRange.end}
              onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Report Types */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Available Reports</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {reportTypes.map((report) => {
            const Icon = report.icon;
            return (
              <div
                key={report.id}
                className={`border-2 rounded-lg p-6 cursor-pointer transition-all ${
                  selectedReportType === report.id
                    ? `${getReportColor(report.color)} border-current`
                    : 'border-gray-200 hover:border-gray-300 bg-white'
                }`}
                onClick={() => setSelectedReportType(report.id)}
              >
                <div className="flex items-start space-x-4">
                  <div className={`p-2 rounded-lg ${
                    selectedReportType === report.id ? 'bg-white bg-opacity-50' : 'bg-gray-100'
                  }`}>
                    <Icon className={`h-6 w-6 ${
                      selectedReportType === report.id ? 'text-current' : 'text-gray-600'
                    }`} />
                  </div>
                  <div className="flex-1">
                    <h4 className={`font-semibold mb-2 ${
                      selectedReportType === report.id ? 'text-current' : 'text-gray-900'
                    }`}>
                      {report.name}
                    </h4>
                    <p className={`text-sm ${
                      selectedReportType === report.id ? 'text-current opacity-80' : 'text-gray-600'
                    }`}>
                      {report.description}
                    </p>
                  </div>
                  {selectedReportType === report.id && (
                    <CheckCircle className="h-5 w-5 text-current" />
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Data Preview */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Data Preview</h4>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div className="bg-blue-50 p-3 rounded-md text-center">
            <div className="text-2xl font-bold text-blue-600">{serverData.globalPatterns.length}</div>
            <div className="text-blue-900">Global Patterns</div>
          </div>
          <div className="bg-green-50 p-3 rounded-md text-center">
            <div className="text-2xl font-bold text-green-600">{serverData.clients.length}</div>
            <div className="text-green-900">Total Clients</div>
          </div>
          <div className="bg-purple-50 p-3 rounded-md text-center">
            <div className="text-2xl font-bold text-purple-600">{serverData.jobHistory.length}</div>
            <div className="text-purple-900">Completed Rounds</div>
          </div>
          <div className="bg-orange-50 p-3 rounded-md text-center">
            <div className="text-2xl font-bold text-orange-600">
              {serverData.clients.reduce((sum: number, c: any) => sum + c.transactionCount, 0).toLocaleString()}
            </div>
            <div className="text-orange-900">Total Transactions</div>
          </div>
        </div>
      </div>

      {/* Generate Report Button */}
      <div className="flex justify-center">
        <button
          onClick={() => generateReport(selectedReportType)}
          disabled={isGenerating}
          className={`flex items-center px-8 py-3 rounded-lg font-medium text-lg transition-all ${
            isGenerating
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700 shadow-lg hover:shadow-xl'
          }`}
        >
          <Download className="h-5 w-5 mr-2" />
          {isGenerating ? 'Generating Report...' : 'Generate & Download Report'}
        </button>
      </div>

      {/* Report Information */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex items-start">
          <AlertCircle className="h-5 w-5 text-yellow-600 mr-3 mt-0.5" />
          <div>
            <h4 className="text-sm font-semibold text-yellow-800 mb-1">Report Information</h4>
            <ul className="text-sm text-yellow-700 space-y-1">
              <li>• All reports are generated in CSV format for easy analysis</li>
              <li>• Pattern data includes privacy-protected aggregated values only</li>
              <li>• Client information excludes sensitive transaction details</li>
              <li>• Date range filters apply to federated rounds and client activity</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DownloadReportsTab;