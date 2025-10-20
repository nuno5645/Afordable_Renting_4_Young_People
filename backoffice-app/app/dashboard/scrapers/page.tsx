'use client';

import { useEffect, useState } from 'react';
import { scrapersAPI, ScrapersStatusResponse } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { formatDate } from '@/lib/utils';
import toast from 'react-hot-toast';
import { Play, RefreshCw, AlertCircle, CheckCircle, Clock, Activity } from 'lucide-react';

export default function ScrapersPage() {
  const [statusData, setStatusData] = useState<ScrapersStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [stopping, setStopping] = useState(false);
  const [selectedScrapers, setSelectedScrapers] = useState<string[]>([]);
  const [showScraperSelection, setShowScraperSelection] = useState(false);
  const [listingType, setListingType] = useState<'rent' | 'buy' | 'all'>('buy');

  const availableScrapers = ['ImoVirtual', 'Idealista', 'Remax', 'ERA', 'CasaSapo', 'SuperCasa'];
  const isScraperRunning = statusData?.results?.[0]?.status === 'running';

  useEffect(() => {
    loadScrapers();
  }, []); // Only run once on mount

  useEffect(() => {
    // Auto-refresh every 10 seconds if latest main run is running
    const interval = setInterval(() => {
      if (statusData?.results?.[0]?.status === 'running') {
        loadScrapers();
      }
    }, 10000);
    
    return () => clearInterval(interval);
  }, [statusData?.results?.[0]?.status]); // Only depend on the status, not the entire results array

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

  const runScrapers = async (scrapers?: string[]) => {
    setRunning(true);
    try {
      const request = scrapers && scrapers.length > 0 
        ? { scrapers, listing_type: listingType } 
        : { all: true, listing_type: listingType };
      
      const response = await scrapersAPI.runScrapers(request);
      
      if (response.status === 'success') {
        toast.success(response.message || 'Scrapers started successfully! Check back in a few minutes.');
      } else {
        toast.error(response.error || 'Failed to start scrapers');
      }
      
      setTimeout(loadScrapers, 3000);
      setShowScraperSelection(false);
      setSelectedScrapers([]);
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Failed to start scrapers');
      console.error(error);
    } finally {
      setRunning(false);
    }
  };

  const toggleScraperSelection = (scraper: string) => {
    setSelectedScrapers(prev => 
      prev.includes(scraper)
        ? prev.filter(s => s !== scraper)
        : [...prev, scraper]
    );
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
        <div className="flex gap-2 items-center">
          <Button onClick={loadScrapers} variant="outline" disabled={loading || running || stopping}>
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button 
            onClick={() => setShowScraperSelection(!showScraperSelection)} 
            variant="outline"
            disabled={running || statusData?.results?.[0]?.status === 'running'}
          >
            {showScraperSelection ? 'Cancel' : 'Select Scrapers'}
          </Button>
          <Button 
            onClick={() => runScrapers()} 
            disabled={running || statusData?.results?.[0]?.status === 'running'}
          >
            <Play className="w-4 h-4 mr-2" />
            {statusData?.results?.[0]?.status === 'running' ? 'Running...' : 'Run All Scrapers'}
          </Button>
        </div>
      </div>

      {/* Scraper Selection Modal */}
      {showScraperSelection && (
        <Card className="border-2 border-blue-500">
          <CardHeader>
            <CardTitle>Select Scrapers to Run</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Listing Type Selector */}
              <div className="p-4 rounded-lg border border-gray-200">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Listing Type
                </label>
                <select
                  value={listingType}
                  onChange={(e) => setListingType(e.target.value as 'rent' | 'buy' | 'all')}
                  className="w-full h-10 rounded-md border border-gray-300 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={running || stopping}
                >
                  <option value="buy">💰 Buy (Comprar)</option>
                  <option value="rent">🏠 Rent (Arrendar)</option>
                  <option value="all">🔄 Both</option>
                </select>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {availableScrapers.map((scraper) => (
                  <label
                    key={scraper}
                    className={`flex items-center p-3 border-2 rounded-lg cursor-pointer transition-colors ${
                      selectedScrapers.includes(scraper)
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={selectedScrapers.includes(scraper)}
                      onChange={() => toggleScraperSelection(scraper)}
                      className="mr-2"
                    />
                    <span className="text-sm font-medium">{scraper}</span>
                  </label>
                ))}
              </div>
              
              <div className="flex gap-2 justify-end pt-4 border-t">
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowScraperSelection(false);
                    setSelectedScrapers([]);
                  }}
                >
                  Cancel
                </Button>
                <Button
                  onClick={() => runScrapers(selectedScrapers)}
                  disabled={selectedScrapers.length === 0 || running}
                >
                  <Play className="w-4 h-4 mr-2" />
                  Run Selected ({selectedScrapers.length})
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* All Main Runs */}
      {statusData?.results && statusData.results.length > 0 ? (
        <div className="space-y-6">
          <h2 className="text-xl font-semibold text-gray-900">Main Scraper Runs</h2>
          {statusData.results.map((mainRun) => {
            const scraperRuns = mainRun.scraper_runs || [];
            return (
              <Card key={mainRun.id} className="border-2">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-xl">Run #{mainRun.id}</CardTitle>
                      {mainRun.start_time && (
                        <p className="text-sm text-gray-500 mt-1">
                          {formatDate(mainRun.start_time)}
                        </p>
                      )}
                    </div>
                    {getStatusIcon(mainRun.status)}
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <p className="text-xs text-gray-500 mb-1">Status</p>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(mainRun.status)}`}>
                        {mainRun.status || 'N/A'}
                      </span>
                    </div>
                    
                    <div>
                      <p className="text-xs text-gray-500 mb-1">Total Houses</p>
                      <p className="text-lg font-semibold">{mainRun.total_houses}</p>
                    </div>
                    
                    <div>
                      <p className="text-xs text-gray-500 mb-1">New Houses</p>
                      <p className="text-lg font-semibold text-green-600">{mainRun.new_houses}</p>
                    </div>
                    
                    {mainRun.end_time && (
                      <div>
                        <p className="text-xs text-gray-500 mb-1">End Time</p>
                        <p className="text-sm">{formatDate(mainRun.end_time)}</p>
                      </div>
                    )}
                  </div>

                  {mainRun.error_message && (
                    <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                      <p className="text-xs font-semibold text-red-800 mb-1">Error:</p>
                      <p className="text-xs text-red-700">{mainRun.error_message}</p>
                    </div>
                  )}

                  {/* Scraper Runs for this Main Run */}
                  {scraperRuns.length > 0 && (
                    <div className="mt-4 pt-4 border-t">
                      <p className="text-sm font-medium text-gray-700 mb-3">Individual Scrapers</p>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {scraperRuns.map((scraper) => (
                          <div key={scraper.id} className="p-3 border rounded-lg bg-gray-50">
                            <div className="flex items-center justify-between mb-2">
                              <p className="font-medium text-sm">{scraper.name}</p>
                              {getStatusIcon(scraper.status)}
                            </div>
                            
                            <div className="space-y-2">
                              <div className="flex items-center justify-between text-xs">
                                <span className="text-gray-500">Status:</span>
                                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getStatusColor(scraper.status)}`}>
                                  {scraper.status || 'N/A'}
                                </span>
                              </div>

                              <div className="flex items-center justify-between text-xs">
                                <span className="text-gray-500">New Houses:</span>
                                <span className="font-semibold text-green-600">{scraper.new_houses}</span>
                              </div>

                              <div className="flex items-center justify-between text-xs">
                                <span className="text-gray-500">Processed:</span>
                                <span className="font-semibold">{scraper.total_houses}</span>
                              </div>

                              {scraper.error_message && (
                                <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded">
                                  <p className="text-xs text-red-700">{scraper.error_message}</p>
                                </div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      ) : (
        <Card>
          <CardContent className="py-12 text-center text-gray-500">
            <Clock className="w-12 h-12 mx-auto mb-3 text-gray-400" />
            <p className="text-sm font-medium">No scraper runs yet</p>
            <p className="text-xs mt-1">Click &quot;Run All Scrapers&quot; to start the first run</p>
          </CardContent>
        </Card>
      )}

    </div>
  );
}
