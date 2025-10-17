'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { housesAPI, scrapersAPI, House, ScrapersStatusResponse } from '@/lib/api';
import { Home, TrendingUp, Activity, AlertCircle } from 'lucide-react';
import { formatCurrency, formatDate } from '@/lib/utils';
import toast from 'react-hot-toast';

export default function DashboardPage() {
  const [houses, setHouses] = useState<House[]>([]);
  const [totalHouses, setTotalHouses] = useState(0);
  const [scraperStatus, setScraperStatus] = useState<ScrapersStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [housesResponse, statusData] = await Promise.all([
        housesAPI.getAll({ ordering: '-scraped_at', page: 1 }),
        scrapersAPI.getStatus()
      ]);
      setHouses(housesResponse.results);
      setTotalHouses(housesResponse.count);
      setScraperStatus(statusData);
    } catch (error: any) {
      toast.error('Failed to load dashboard data');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const stats = {
    total: totalHouses,
    favorites: houses.filter(h => h.is_favorite).length,
    contacted: houses.filter(h => h.is_contacted).length,
    avgPrice: houses.length > 0 
      ? houses.reduce((sum, h) => sum + parseFloat(h.price), 0) / houses.length 
      : 0,
  };

  const recentHouses = houses.slice(0, 5);
  const scrapers = scraperStatus?.scrapers ? Object.entries(scraperStatus.scrapers) : [];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 mt-1">Overview of your rental properties</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Houses</CardTitle>
            <Home className="h-4 w-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
            <p className="text-xs text-gray-500 mt-1">Available properties</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Favorites</CardTitle>
            <Activity className="h-4 w-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.favorites}</div>
            <p className="text-xs text-gray-500 mt-1">Marked as favorites</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Contacted</CardTitle>
            <AlertCircle className="h-4 w-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.contacted}</div>
            <p className="text-xs text-gray-500 mt-1">Already contacted</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg. Price</CardTitle>
            <TrendingUp className="h-4 w-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(stats.avgPrice)}</div>
            <p className="text-xs text-gray-500 mt-1">Average rental price</p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Houses */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Properties</CardTitle>
        </CardHeader>
        <CardContent>
          {recentHouses.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No properties found</p>
          ) : (
            <div className="space-y-4">
              {recentHouses.map((house) => (
                <div key={house.house_id} className="flex items-start justify-between border-b pb-4 last:border-0">
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900">{house.name}</h3>
                    <p className="text-sm text-gray-500 mt-1">
                      {house.zone} • {house.bedrooms} • {house.area}
                    </p>
                    <p className="text-xs text-gray-400 mt-1">
                      {formatDate(house.scraped_at)}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-semibold text-gray-900">
                      {formatCurrency(house.price)}
                    </p>
                    <span className="inline-block px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800 mt-1">
                      {house.source}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Scraper Status */}
      {scraperStatus?.main_run && (
        <Card>
          <CardHeader>
            <CardTitle>Latest Scraper Run</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Main Run Status */}
              <div className="flex items-center justify-between border-b pb-3">
                <div>
                  <p className="font-medium text-gray-900">Main Run</p>
                  <p className="text-xs text-gray-500">
                    {scraperStatus.main_run.start_time 
                      ? `Started: ${formatDate(scraperStatus.main_run.start_time)}`
                      : 'No runs yet'}
                  </p>
                </div>
                <div className="text-right">
                  <span className={`inline-block px-2 py-1 text-xs rounded-full ${
                    scraperStatus.main_run.status === 'completed' || scraperStatus.main_run.status === 'success'
                      ? 'bg-green-100 text-green-800'
                      : scraperStatus.main_run.status === 'running'
                      ? 'bg-blue-100 text-blue-800'
                      : scraperStatus.main_run.status === 'failed' || scraperStatus.main_run.status === 'error'
                      ? 'bg-red-100 text-red-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {scraperStatus.main_run.status || 'N/A'}
                  </span>
                  <p className="text-xs text-gray-500 mt-1">
                    {scraperStatus.main_run.new_houses} new houses
                  </p>
                </div>
              </div>

              {/* Individual Scrapers */}
              {scrapers.length > 0 && (
                <div className="space-y-3">
                  <p className="text-sm font-medium text-gray-700">Individual Scrapers</p>
                  {scrapers.map(([key, scraper]) => (
                    <div key={key} className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-gray-900">{scraper.name}</p>
                        <p className="text-xs text-gray-500">
                          Last run: {formatDate(scraper.timestamp)}
                        </p>
                      </div>
                      <div className="text-right">
                        <span className={`inline-block px-2 py-1 text-xs rounded-full ${
                          scraper.status === 'completed' || scraper.status === 'success'
                            ? 'bg-green-100 text-green-800'
                            : scraper.status === 'running'
                            ? 'bg-blue-100 text-blue-800'
                            : scraper.status === 'failed' || scraper.status === 'error'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {scraper.status || 'N/A'}
                        </span>
                        <p className="text-xs text-gray-500 mt-1">
                          {scraper.houses_found} houses found
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
