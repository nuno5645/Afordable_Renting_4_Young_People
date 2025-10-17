'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Pagination } from '@/components/ui/Pagination';
import { housesAPI, scrapersAPI, House, ScrapersStatusResponse, HouseStats } from '@/lib/api';
import { Home, TrendingUp, Activity, AlertCircle } from 'lucide-react';
import { formatCurrency, formatDate } from '@/lib/utils';
import toast from 'react-hot-toast';

export default function DashboardPage() {
  const [houses, setHouses] = useState<House[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [stats, setStats] = useState<HouseStats>({ total_houses: 0, average_price: 0 });
  const [scraperStatus, setScraperStatus] = useState<ScrapersStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [currentPage]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [housesResponse, statsData, statusData] = await Promise.all([
        housesAPI.getAll({ ordering: '-scraped_at', page: currentPage }),
        housesAPI.getStats(),
        scrapersAPI.getStatus()
      ]);
      setHouses(housesResponse.results);
      setTotalCount(housesResponse.count);
      if (housesResponse.results.length > 0) {
        setPageSize(housesResponse.results.length);
      }
      setStats(statsData);
      setScraperStatus(statusData);
    } catch (error: any) {
      toast.error('Failed to load dashboard data');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const latestMainRun = scraperStatus?.results?.[0];
  const latestScraperRuns = latestMainRun?.scraper_runs || [];

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
            <div className="text-2xl font-bold">{stats.total_houses}</div>
            <p className="text-xs text-gray-500 mt-1">Available properties</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg. Price</CardTitle>
            <TrendingUp className="h-4 w-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(stats.average_price)}</div>
            <p className="text-xs text-gray-500 mt-1">Average rental price</p>
          </CardContent>
        </Card>
      </div>

      {/* Pagination */}
      <Pagination
        currentPage={currentPage}
        totalPages={Math.ceil(totalCount / pageSize)}
        totalItems={totalCount}
        itemsPerPage={pageSize}
        onPageChange={handlePageChange}
      />

      {/* Recent Houses */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Properties</CardTitle>
        </CardHeader>
        <CardContent>
          {houses.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No properties found</p>
          ) : (
            <div className="space-y-4">
              {houses.map((house) => (
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

      {/* Pagination - Bottom */}
      {houses.length > 0 && (
        <Pagination
          currentPage={currentPage}
          totalPages={Math.ceil(totalCount / pageSize)}
          totalItems={totalCount}
          itemsPerPage={pageSize}
          onPageChange={handlePageChange}
        />
      )}

      {/* Scraper Status */}
      {latestMainRun && (
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
                    {latestMainRun.start_time 
                      ? `Started: ${formatDate(latestMainRun.start_time)}`
                      : 'No runs yet'}
                  </p>
                </div>
                <div className="text-right">
                  <span className={`inline-block px-2 py-1 text-xs rounded-full ${
                    latestMainRun.status === 'completed' || latestMainRun.status === 'success'
                      ? 'bg-green-100 text-green-800'
                      : latestMainRun.status === 'running'
                      ? 'bg-blue-100 text-blue-800'
                      : latestMainRun.status === 'failed' || latestMainRun.status === 'error'
                      ? 'bg-red-100 text-red-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {latestMainRun.status || 'N/A'}
                  </span>
                  <p className="text-xs text-gray-500 mt-1">
                    {latestMainRun.new_houses} new houses
                  </p>
                </div>
              </div>

              {/* Individual Scrapers */}
              {latestScraperRuns.length > 0 && (
                <div className="space-y-3">
                  <p className="text-sm font-medium text-gray-700">Individual Scrapers</p>
                  {latestScraperRuns.map((scraper) => (
                    <div key={scraper.id} className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-gray-900">{scraper.name}</p>
                        <p className="text-xs text-gray-500">
                          Last run: {formatDate(scraper.start_time || '')}
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
                          {scraper.new_houses} houses found
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
