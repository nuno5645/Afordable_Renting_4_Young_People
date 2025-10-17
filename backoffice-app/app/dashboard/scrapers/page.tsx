'use client';

import { useEffect, useState } from 'react';
import { scrapersAPI, ScrapersStatusResponse, ScraperInfo } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { formatDate } from '@/lib/utils';
import toast from 'react-hot-toast';
import { Play, RefreshCw, AlertCircle, CheckCircle, Clock, Activity } from 'lucide-react';

export default function ScrapersPage() {
  const [statusData, setStatusData] = useState<ScrapersStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    loadScrapers();
    // Auto-refresh every 10 seconds if main run is running
    const interval = setInterval(() => {
      if (statusData?.main_run?.status === 'running') {
        loadScrapers();
      }
    }, 10000);
    
    return () => clearInterval(interval);
  }, [statusData?.main_run?.status]);

  const loadScrapers = async () => {
    setLoading(true);
    try {
      const data = await scrapersAPI.getStatus();
      console.log('API Response:', JSON.stringify(data, null, 2));
      setStatusData(data);
    } catch (error: any) {
      toast.error('Failed to load scraper status');
      console.error('Error loading scrapers:', error);
    } finally {
      setLoading(false);
    }
  };

  const runScrapers = async () => {
    setRunning(true);
    try {
      await scrapersAPI.runScrapers();
      toast.success('Scrapers started successfully! Check back in a few minutes.');
      setTimeout(loadScrapers, 3000);
    } catch (error: any) {
      toast.error('Failed to start scrapers');
      console.error(error);
    } finally {
      setRunning(false);
    }
  };

  const getStatusColor = (status: string | null) => {
    if (!status) return 'bg-gray-100 text-gray-800';
    
    switch (status.toLowerCase()) {
      case 'running':
        return 'bg-blue-100 text-blue-800';
      case 'success':
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'error':
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string | null) => {
    if (!status) return <Clock className="w-5 h-5 text-gray-500" />;
    
    switch (status.toLowerCase()) {
      case 'running':
        return <Activity className="w-5 h-5 text-blue-500 animate-pulse" />;
      case 'success':
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'error':
      case 'failed':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-500" />;
    }
  };

  if (loading && !statusData) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading scrapers...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Scrapers</h1>
          <p className="text-gray-500 mt-1">Manage and monitor your data scrapers</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={loadScrapers} variant="outline" disabled={loading || running}>
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button 
            onClick={runScrapers} 
            disabled={running || statusData?.main_run?.status === 'running'}
          >
            <Play className="w-4 h-4 mr-2" />
            {statusData?.main_run?.status === 'running' ? 'Running...' : 'Run All Scrapers'}
          </Button>
        </div>
      </div>

      {/* Main Run Status Card */}
      {statusData?.main_run && (
        <Card className="border-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-xl">Main Run Status</CardTitle>
              {getStatusIcon(statusData.main_run.status)}
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {statusData.main_run.status ? (
              <>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Status</p>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(statusData.main_run.status)}`}>
                      {statusData.main_run.status}
                    </span>
                  </div>
                  
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Total Houses</p>
                    <p className="text-lg font-semibold">{statusData.main_run.total_houses}</p>
                  </div>
                  
                  <div>
                    <p className="text-xs text-gray-500 mb-1">New Houses</p>
                    <p className="text-lg font-semibold text-green-600">{statusData.main_run.new_houses}</p>
                  </div>
                  
                  {statusData.main_run.start_time && (
                    <div>
                      <p className="text-xs text-gray-500 mb-1">Start Time</p>
                      <p className="text-sm">{formatDate(statusData.main_run.start_time)}</p>
                    </div>
                  )}
                </div>

                {statusData.main_run.end_time && (
                  <div>
                    <p className="text-xs text-gray-500 mb-1">End Time</p>
                    <p className="text-sm">{formatDate(statusData.main_run.end_time)}</p>
                  </div>
                )}

                {statusData.main_run.last_run_date && (
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Last Run Date</p>
                    <p className="text-sm">{formatDate(statusData.main_run.last_run_date)}</p>
                  </div>
                )}

                {statusData.main_run.error_message && (
                  <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
                    <p className="text-xs font-semibold text-red-800 mb-1">Error:</p>
                    <p className="text-xs text-red-700">{statusData.main_run.error_message}</p>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Clock className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                <p className="text-sm font-medium">No scraper runs yet</p>
                <p className="text-xs mt-1">Click &quot;Run All Scrapers&quot; to start the first run</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Individual Scrapers */}
      {statusData?.scrapers && Object.keys(statusData.scrapers).length > 0 ? (
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Individual Scrapers</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Object.entries(statusData.scrapers).map(([key, scraper]) => (
              <Card key={key}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{scraper.name}</CardTitle>
                    {getStatusIcon(scraper.status)}
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Status:</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(scraper.status)}`}>
                      {scraper.status || 'N/A'}
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Houses Found:</span>
                    <span className="font-semibold text-green-600">{scraper.houses_found}</span>
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Houses Processed:</span>
                    <span className="font-semibold">{scraper.houses_processed}</span>
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Last Updated:</span>
                    <span className="text-gray-900 text-xs">{formatDate(scraper.timestamp)}</span>
                  </div>

                  {scraper.error_message && (
                    <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
                      <p className="text-xs font-semibold text-red-800 mb-1">Error:</p>
                      <p className="text-xs text-red-700">{scraper.error_message}</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      ) : (
        statusData?.main_run?.status && (
          <Card>
            <CardContent className="py-12 text-center text-gray-500">
              <AlertCircle className="w-12 h-12 mx-auto mb-3 text-gray-400" />
              <p className="text-sm font-medium">No individual scraper data available</p>
              <p className="text-xs mt-1">Scraper details will appear here during and after runs</p>
            </CardContent>
          </Card>
        )
      )}

    </div>
  );
}
