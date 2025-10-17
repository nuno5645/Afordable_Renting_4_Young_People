'use client';

import { useEffect, useState } from 'react';
import { housesAPI, House } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Pagination } from '@/components/ui/Pagination';
import { formatCurrency, formatDate } from '@/lib/utils';
import toast from 'react-hot-toast';
import { 
  Star, 
  MessageCircle, 
  Trash2, 
  ExternalLink, 
  Search,
  Filter,
  RefreshCw
} from 'lucide-react';
import Link from 'next/link';

export default function HousesPage() {
  const [houses, setHouses] = useState<House[]>([]);
  const [filteredHouses, setFilteredHouses] = useState<House[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [filters, setFilters] = useState({
    favorites: false,
    contacted: false,
    discarded: false,
    source: 'all',
  });

  useEffect(() => {
    loadHouses();
  }, [currentPage]);

  useEffect(() => {
    applyFilters();
  }, [houses, searchTerm, filters]);

  const loadHouses = async () => {
    setLoading(true);
    try {
      const response = await housesAPI.getAll({ 
        ordering: '-scraped_at',
        page: currentPage 
      });
      setHouses(response.results);
      setTotalCount(response.count);
      // Calculate page size from the response
      if (response.results.length > 0) {
        setPageSize(response.results.length);
      }
    } catch (error: any) {
      toast.error('Failed to load houses');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const applyFilters = () => {
    let filtered = [...houses];

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(house =>
        house.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        house.zone.toLowerCase().includes(searchTerm.toLowerCase()) ||
        house.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        house.parish?.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        house.county?.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        house.district?.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Status filters
    if (filters.favorites) {
      filtered = filtered.filter(h => h.is_favorite);
    }
    if (filters.contacted) {
      filtered = filtered.filter(h => h.is_contacted);
    }
    if (filters.discarded) {
      filtered = filtered.filter(h => h.is_discarded);
    }

    // Source filter
    if (filters.source !== 'all') {
      filtered = filtered.filter(h => h.source === filters.source);
    }

    setFilteredHouses(filtered);
  };

  const toggleFavorite = async (house: House) => {
    try {
      const updated = await housesAPI.toggleFavorite(house.house_id);
      setHouses(houses.map(h => h.house_id === house.house_id ? updated : h));
      toast.success(updated.is_favorite ? 'Added to favorites' : 'Removed from favorites');
    } catch (error) {
      toast.error('Failed to update favorite status');
    }
  };

  const toggleContacted = async (house: House) => {
    try {
      const updated = await housesAPI.toggleContacted(house.house_id);
      setHouses(houses.map(h => h.house_id === house.house_id ? updated : h));
      toast.success(updated.is_contacted ? 'Marked as contacted' : 'Unmarked as contacted');
    } catch (error) {
      toast.error('Failed to update contacted status');
    }
  };

  const toggleDiscarded = async (house: House) => {
    try {
      const updated = await housesAPI.toggleDiscarded(house.house_id);
      setHouses(houses.map(h => h.house_id === house.house_id ? updated : h));
      toast.success(updated.is_discarded ? 'Marked as discarded' : 'Unmarked as discarded');
    } catch (error) {
      toast.error('Failed to update discarded status');
    }
  };

  const deleteHouse = async (house: House) => {
    if (!confirm('Are you sure you want to delete this house?')) return;
    
    try {
      await housesAPI.delete(house.house_id);
      setHouses(houses.filter(h => h.house_id !== house.house_id));
      toast.success('House deleted successfully');
    } catch (error) {
      toast.error('Failed to delete house');
    }
  };

  const sources = ['all', ...new Set(houses.map(h => h.source))];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading houses...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Houses</h1>
          <p className="text-gray-500 mt-1">Manage your rental properties</p>
        </div>
        <Button onClick={loadHouses} variant="outline">
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Filters</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4 flex-wrap">
            <div className="flex-1 min-w-[200px]">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  placeholder="Search by name, zone, location, or description..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <select
              value={filters.source}
              onChange={(e) => setFilters({ ...filters, source: e.target.value })}
              className="h-10 rounded-md border border-gray-300 px-3 text-sm"
            >
              {sources.map(source => (
                <option key={source} value={source}>
                  {source === 'all' ? 'All Sources' : source}
                </option>
              ))}
            </select>
          </div>
          <div className="flex gap-2 flex-wrap">
            <Button
              variant={filters.favorites ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setFilters({ ...filters, favorites: !filters.favorites })}
            >
              <Star className="w-4 h-4 mr-2" />
              Favorites
            </Button>
            <Button
              variant={filters.contacted ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setFilters({ ...filters, contacted: !filters.contacted })}
            >
              <MessageCircle className="w-4 h-4 mr-2" />
              Contacted
            </Button>
            <Button
              variant={filters.discarded ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setFilters({ ...filters, discarded: !filters.discarded })}
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Discarded
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Pagination - Top */}
      {!searchTerm && !filters.favorites && !filters.contacted && !filters.discarded && filters.source === 'all' && (
        <Pagination
          currentPage={currentPage}
          totalPages={Math.ceil(totalCount / pageSize)}
          totalItems={totalCount}
          itemsPerPage={pageSize}
          onPageChange={handlePageChange}
        />
      )}

      {/* Results */}
      {(searchTerm || filters.favorites || filters.contacted || filters.discarded || filters.source !== 'all') && (
        <div className="text-sm text-gray-500">
          Showing {filteredHouses.length} filtered results
        </div>
      )}

      {/* Houses Grid */}
      {filteredHouses.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-gray-500">
            No houses found matching your filters
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-6">
          {filteredHouses.map((house) => (
            <Card key={house.house_id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex gap-6">
                  {/* Image */}
                  {house.photos.length > 0 && (
                    <div className="w-48 h-32 flex-shrink-0 rounded-lg overflow-hidden bg-gray-100">
                      <img
                        src={house.photos[0].image_url}
                        alt={house.name}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          (e.target as HTMLImageElement).style.display = 'none';
                        }}
                      />
                    </div>
                  )}

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 mb-1">
                          {house.name}
                        </h3>
                        <p className="text-sm text-gray-600 mb-2">
                          {house.zone}
                        </p>
                        
                        {/* Location Information */}
                        {(house.parish || house.county || house.district) && (
                          <div className="flex items-center gap-2 text-xs text-gray-500 mb-2">
                            {house.parish && (
                              <span className="px-2 py-1 bg-gray-100 rounded">
                                📍 {house.parish.name}
                              </span>
                            )}
                            {house.county && (
                              <span className="px-2 py-1 bg-gray-100 rounded">
                                {house.county.name}
                              </span>
                            )}
                            {house.district && !house.county && (
                              <span className="px-2 py-1 bg-gray-100 rounded">
                                {house.district.name}
                              </span>
                            )}
                          </div>
                        )}
                        
                        <div className="flex items-center gap-4 text-sm text-gray-500">
                          <span>{house.bedrooms} bedrooms</span>
                          <span>•</span>
                          <span>{house.area} m²</span>
                          {house.floor && (
                            <>
                              <span>•</span>
                              <span>Floor {house.floor}</span>
                            </>
                          )}
                        </div>
                        <p className="text-sm text-gray-600 mt-2 line-clamp-2">
                          {house.description}
                        </p>
                      </div>

                      <div className="text-right">
                        <p className="text-2xl font-bold text-gray-900">
                          {formatCurrency(house.price)}
                        </p>
                        <span className="inline-block px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800 mt-1">
                          {house.source}
                        </span>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-2 mt-4">
                      <Button
                        variant={house.is_favorite ? 'primary' : 'outline'}
                        size="sm"
                        onClick={() => toggleFavorite(house)}
                      >
                        <Star className="w-4 h-4" fill={house.is_favorite ? 'currentColor' : 'none'} />
                      </Button>
                      <Button
                        variant={house.is_contacted ? 'primary' : 'outline'}
                        size="sm"
                        onClick={() => toggleContacted(house)}
                      >
                        <MessageCircle className="w-4 h-4" fill={house.is_contacted ? 'currentColor' : 'none'} />
                      </Button>
                      <Button
                        variant={house.is_discarded ? 'danger' : 'outline'}
                        size="sm"
                        onClick={() => toggleDiscarded(house)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                      <Link href={house.url} target="_blank" rel="noopener noreferrer">
                        <Button variant="ghost" size="sm">
                          <ExternalLink className="w-4 h-4" />
                        </Button>
                      </Link>
                      <div className="flex-1" />
                      <span className="text-xs text-gray-400">
                        {formatDate(house.scraped_at)}
                      </span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Pagination - Bottom */}
      {!searchTerm && !filters.favorites && !filters.contacted && !filters.discarded && filters.source === 'all' && filteredHouses.length > 0 && (
        <Pagination
          currentPage={currentPage}
          totalPages={Math.ceil(totalCount / pageSize)}
          totalItems={totalCount}
          itemsPerPage={pageSize}
          onPageChange={handlePageChange}
        />
      )}
    </div>
  );
}
