'use client';

import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { ConfirmModal } from '@/components/ui/ConfirmModal';
import { ImageCarousel } from '@/components/ui/ImageCarousel';
import { Input } from '@/components/ui/Input';
import { Modal } from '@/components/ui/Modal';
import { Pagination } from '@/components/ui/Pagination';
import { County, District, House, housesAPI, locationsAPI, Parish } from '@/lib/api';
import { formatCurrency, formatDate } from '@/lib/utils';
import {
  Edit2,
  ExternalLink,
  RefreshCw,
  Search,
  Trash2,
  X
} from 'lucide-react';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import toast from 'react-hot-toast';

export default function HousesPage() {
  const [houses, setHouses] = useState<House[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeSearch, setActiveSearch] = useState(''); // The search term actually applied to the API
  const [currentPage, setCurrentPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [pageSize] = useState(10);
  
  // Location data
  const [districts, setDistricts] = useState<District[]>([]);
  const [counties, setCounties] = useState<County[]>([]);
  const [parishes, setParishes] = useState<Parish[]>([]);
  
  const [filters, setFilters] = useState({
    source: 'all',
    district: undefined as number | undefined,
    county: undefined as number | undefined,
    parish: undefined as number | undefined,
  });

  // Edit modal state
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editingHouse, setEditingHouse] = useState<House | null>(null);
  const [editForm, setEditForm] = useState({
    name: '',
    price: 0,
    bedrooms: 0,
    area: 0,
    floor: '',
    zone: '',
    description: '',
  });

  // Delete confirmation modal state
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [houseToDelete, setHouseToDelete] = useState<House | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Delete all confirmation modal state
  const [isDeleteAllModalOpen, setIsDeleteAllModalOpen] = useState(false);
  const [isDeletingAll, setIsDeletingAll] = useState(false);

  useEffect(() => {
    loadLocations();
  }, []);

  useEffect(() => {
    loadHouses();
  }, [currentPage, filters.district, filters.county, filters.parish, filters.source, activeSearch]);

  // Load counties when district changes
  useEffect(() => {
    if (filters.district) {
      loadCounties(filters.district);
      setFilters(prev => ({ ...prev, county: undefined, parish: undefined }));
    } else {
      setCounties([]);
      setParishes([]);
    }
  }, [filters.district]);

  // Load parishes when county changes
  useEffect(() => {
    if (filters.county) {
      loadParishes(filters.county);
      setFilters(prev => ({ ...prev, parish: undefined }));
    } else {
      setParishes([]);
    }
  }, [filters.county]);

  // Reset to page 1 when filters change
  useEffect(() => {
    if (currentPage !== 1) {
      setCurrentPage(1);
    }
  }, [filters.district, filters.county, filters.parish, filters.source, activeSearch]);

  const loadLocations = async () => {
    try {
      const districtsData = await locationsAPI.getDistricts();
      setDistricts(districtsData);
    } catch (error) {
      console.error('Failed to load districts:', error);
    }
  };

  const loadCounties = async (districtId: number) => {
    try {
      const countiesData = await locationsAPI.getCounties({ district: districtId });
      setCounties(countiesData);
    } catch (error) {
      console.error('Failed to load counties:', error);
    }
  };

  const loadParishes = async (countyId: number) => {
    try {
      const parishesData = await locationsAPI.getParishes({ county: countyId });
      setParishes(parishesData);
    } catch (error) {
      console.error('Failed to load parishes:', error);
    }
  };

  const loadHouses = async () => {
    setLoading(true);
    try {
      const response = await housesAPI.getAll({ 
        ordering: '-scraped_at',
        page: currentPage,
        district: filters.district,
        county: filters.county,
        parish: filters.parish,
        source: filters.source !== 'all' ? filters.source : undefined,
        search: activeSearch || undefined,
      });
      setHouses(response.results);
      setTotalCount(response.count);
    } catch (error: any) {
      toast.error('Failed to load houses');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setActiveSearch(searchTerm);
    setCurrentPage(1);
  };

  const handleClearSearch = () => {
    setSearchTerm('');
    setActiveSearch('');
    setCurrentPage(1);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const openEditModal = (house: House) => {
    setEditingHouse(house);
    setEditForm({
      name: house.name,
      price: Number(house.price),
      bedrooms: Number(house.bedrooms),
      area: Number(house.area),
      floor: house.floor || '',
      zone: house.zone,
      description: house.description,
    });
    setIsEditModalOpen(true);
  };

  const closeEditModal = () => {
    setIsEditModalOpen(false);
    setEditingHouse(null);
  };

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingHouse) return;

    try {
      // Convert numbers to strings to match the API expected format
      const updateData = {
        name: editForm.name,
        price: editForm.price.toString(),
        bedrooms: editForm.bedrooms.toString(),
        area: editForm.area.toString(),
        floor: editForm.floor || null,
        zone: editForm.zone,
        description: editForm.description,
      };
      const updated = await housesAPI.update(editingHouse.house_id, updateData);
      setHouses(houses.map(h => h.house_id === editingHouse.house_id ? updated : h));
      toast.success('House updated successfully');
      closeEditModal();
    } catch (error) {
      toast.error('Failed to update house');
    }
  };

  const openDeleteModal = (house: House) => {
    setHouseToDelete(house);
    setIsDeleteModalOpen(true);
  };

  const closeDeleteModal = () => {
    setIsDeleteModalOpen(false);
    setHouseToDelete(null);
  };

  const confirmDelete = async () => {
    if (!houseToDelete) return;
    
    setIsDeleting(true);
    try {
      await housesAPI.delete(houseToDelete.house_id);
      setHouses(houses.filter(h => h.house_id !== houseToDelete.house_id));
      toast.success('House deleted successfully');
      closeDeleteModal();
    } catch (error) {
      toast.error('Failed to delete house');
    } finally {
      setIsDeleting(false);
    }
  };

  const openDeleteAllModal = () => {
    setIsDeleteAllModalOpen(true);
  };

  const closeDeleteAllModal = () => {
    setIsDeleteAllModalOpen(false);
  };

  const confirmDeleteAll = async () => {
    setIsDeletingAll(true);
    try {
      const result = await housesAPI.deleteAll();
      toast.success(result.message);
      setHouses([]);
      setTotalCount(0);
      closeDeleteAllModal();
      await loadHouses(); // Reload to refresh
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Failed to delete all houses');
    } finally {
      setIsDeletingAll(false);
    }
  };

  // Hardcoded sources list matching the available scrapers
  const sources = ['all', 'Imovirtual', 'Idealista', 'Remax', 'ERA', 'Casa SAPO', 'SuperCasa'];

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
        <div className="flex gap-2">
          <Button 
            onClick={openDeleteAllModal} 
            variant="danger"
            disabled={houses.length === 0}
          >
            <Trash2 className="w-4 h-4 mr-2" />
            Delete All
          </Button>
          <Button onClick={loadHouses} variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Filters</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4 flex-wrap">
            <div className="flex-1 min-w-[200px]">
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    placeholder="Search by name, zone, location, or description..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        handleSearch();
                      }
                    }}
                    className="pl-10"
                  />
                </div>
                <Button onClick={handleSearch} variant="primary">
                  Search
                </Button>
                {activeSearch && (
                  <Button onClick={handleClearSearch} variant="outline">
                    <X className="w-4 h-4" />
                  </Button>
                )}
              </div>
            </div>
            <select
              value={filters.source}
              onChange={(e) => setFilters({ ...filters, source: e.target.value })}
              className="h-10 rounded-md border border-gray-300 px-3 text-sm"
            >
              {sources.map((source: string) => (
                <option key={source} value={source}>
                  {source === 'all' ? 'All Sources' : source}
                </option>
              ))}
            </select>
          </div>
          
          {/* Location Filters */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">District</label>
              <div className="flex gap-2">
                <select
                  value={filters.district || ''}
                  onChange={(e) => setFilters({ ...filters, district: e.target.value ? Number(e.target.value) : undefined })}
                  className="flex-1 h-10 rounded-md border border-gray-300 px-3 text-sm"
                >
                  <option value="">All Districts</option>
                  {districts.map(district => (
                    <option key={district.id} value={district.id}>
                      {district.name}
                    </option>
                  ))}
                </select>
                {filters.district && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setFilters({ ...filters, district: undefined, county: undefined, parish: undefined })}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                )}
              </div>
            </div>
            
            <div className="space-y-2">
              <label className={`text-sm font-medium ${!filters.district ? 'text-gray-400' : 'text-gray-700'}`}>
                County {!filters.district && '(Select district first)'}
              </label>
              <div className="flex gap-2">
                <select
                  value={filters.county || ''}
                  onChange={(e) => setFilters({ ...filters, county: e.target.value ? Number(e.target.value) : undefined })}
                  className={`flex-1 h-10 rounded-md border px-3 text-sm ${
                    !filters.district 
                      ? 'border-gray-200 bg-gray-100 text-gray-400 cursor-not-allowed' 
                      : 'border-gray-300 bg-white text-gray-900'
                  }`}
                  disabled={!filters.district}
                >
                  <option value="">All Counties</option>
                  {counties.map(county => (
                    <option key={county.id} value={county.id}>
                      {county.name}
                    </option>
                  ))}
                </select>
                {filters.county && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setFilters({ ...filters, county: undefined, parish: undefined })}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                )}
              </div>
            </div>
            
            <div className="space-y-2">
              <label className={`text-sm font-medium ${!filters.county ? 'text-gray-400' : 'text-gray-700'}`}>
                Parish {!filters.county && '(Select county first)'}
              </label>
              <div className="flex gap-2">
                <select
                  value={filters.parish || ''}
                  onChange={(e) => setFilters({ ...filters, parish: e.target.value ? Number(e.target.value) : undefined })}
                  className={`flex-1 h-10 rounded-md border px-3 text-sm ${
                    !filters.county 
                      ? 'border-gray-200 bg-gray-100 text-gray-400 cursor-not-allowed' 
                      : 'border-gray-300 bg-white text-gray-900'
                  }`}
                  disabled={!filters.county}
                >
                  <option value="">All Parishes</option>
                  {parishes.map(parish => (
                    <option key={parish.id} value={parish.id}>
                      {parish.name}
                    </option>
                  ))}
                </select>
                {filters.parish && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setFilters({ ...filters, parish: undefined })}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results */}
      {activeSearch && (
        <div className="text-sm text-gray-500">
          Showing {houses.length} results for &quot;{activeSearch}&quot; ({totalCount} total)
        </div>
      )}

      {/* Houses Grid */}
      {houses.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-gray-500">
            No houses found matching your filters
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-6">
          {houses.map((house) => (
            <Card key={house.house_id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex gap-6">
                  {/* Image Carousel */}
                  <div className="w-48 h-32 flex-shrink-0 rounded-lg overflow-hidden bg-gray-100">
                    <ImageCarousel
                      images={house.photos || []}
                      alt={house.name}
                      className="w-full h-full"
                    />
                  </div>

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
                        variant="outline"
                        size="sm"
                        onClick={() => openEditModal(house)}
                        title="Edit house"
                      >
                        <Edit2 className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="danger"
                        size="sm"
                        onClick={() => openDeleteModal(house)}
                        title="Delete house"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                      <Link href={house.url} target="_blank" rel="noopener noreferrer">
                        <Button variant="ghost" size="sm" title="View original listing">
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
      {houses.length > 0 && (
        <Pagination
          currentPage={currentPage}
          totalPages={Math.ceil(totalCount / pageSize)}
          totalItems={totalCount}
          itemsPerPage={pageSize}
          onPageChange={handlePageChange}
        />
      )}

      {/* Edit Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={closeEditModal}
        title="Edit House"
        size="lg"
      >
        <form onSubmit={handleEditSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Name
            </label>
            <Input
              type="text"
              value={editForm.name}
              onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Price (€)
              </label>
              <Input
                type="number"
                value={editForm.price}
                onChange={(e) => setEditForm({ ...editForm, price: Number(e.target.value) })}
                required
                min="0"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Bedrooms
              </label>
              <Input
                type="number"
                value={editForm.bedrooms}
                onChange={(e) => setEditForm({ ...editForm, bedrooms: Number(e.target.value) })}
                required
                min="0"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Area (m²)
              </label>
              <Input
                type="number"
                value={editForm.area}
                onChange={(e) => setEditForm({ ...editForm, area: Number(e.target.value) })}
                required
                min="0"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Floor
              </label>
              <Input
                type="text"
                value={editForm.floor}
                onChange={(e) => setEditForm({ ...editForm, floor: e.target.value })}
                placeholder="e.g., 1, 2, Ground"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Zone
            </label>
            <Input
              type="text"
              value={editForm.zone}
              onChange={(e) => setEditForm({ ...editForm, zone: e.target.value })}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={4}
              value={editForm.description}
              onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
              required
            />
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={closeEditModal}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
            >
              Save Changes
            </Button>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation Modal */}
      <ConfirmModal
        isOpen={isDeleteModalOpen}
        onClose={closeDeleteModal}
        onConfirm={confirmDelete}
        title="Delete House"
        message={
          houseToDelete ? (
            <div>
              <p className="font-medium mb-2">Are you sure you want to delete this house?</p>
              <p className="text-sm text-gray-600 mb-1">
                <strong>{houseToDelete.name}</strong>
              </p>
              <p className="text-sm text-gray-600">
                {houseToDelete.zone} • {formatCurrency(houseToDelete.price)}
              </p>
              <p className="text-sm text-red-600 mt-3">
                This action cannot be undone.
              </p>
            </div>
          ) : (
            'Are you sure you want to delete this house?'
          )
        }
        confirmText="Delete"
        cancelText="Cancel"
        variant="danger"
        isLoading={isDeleting}
      />

      {/* Delete All Confirmation Modal */}
      <ConfirmModal
        isOpen={isDeleteAllModalOpen}
        onClose={closeDeleteAllModal}
        onConfirm={confirmDeleteAll}
        title="Delete All Houses"
        message={
          <div>
            <p className="font-medium mb-2 text-red-600">⚠️ DANGER: This will delete ALL houses!</p>
            <p className="text-sm text-gray-600 mb-2">
              You are about to delete <strong>{totalCount} houses</strong> from the database.
            </p>
            <p className="text-sm text-gray-600 mb-2">
              This will also permanently delete:
            </p>
            <ul className="text-sm text-gray-600 list-disc list-inside mb-3 space-y-1">
              <li>All house photos</li>
              <li>All favorite/contacted/discarded relationships</li>
              <li>All associated metadata</li>
            </ul>
            <p className="text-sm font-bold text-red-600">
              ⚠️ THIS ACTION CANNOT BE UNDONE! ⚠️
            </p>
          </div>
        }
        confirmText="Yes, Delete Everything"
        cancelText="Cancel"
        variant="danger"
        isLoading={isDeletingAll}
      />
    </div>
  );
}
