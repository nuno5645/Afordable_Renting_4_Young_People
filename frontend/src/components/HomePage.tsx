import React, { useState, useEffect, useCallback, memo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Filter, ChevronDown } from "lucide-react";
import { PropertyCard } from "./PropertyCard";
import { FilterSheet } from "./FilterSheet";
import api, { House } from "../services/api";

// Memoize PropertyCard to prevent unnecessary re-renders
const MemoizedPropertyCard = memo(PropertyCard);

export function HomePage() {
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [properties, setProperties] = useState<House[]>([]);
  const [filteredProperties, setFilteredProperties] = useState<House[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [sortColumn, setSortColumn] = useState<string>('Price');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [displayCount, setDisplayCount] = useState(10); // For windowed rendering

  // Use useCallback for event handlers to prevent unnecessary re-renders
  const fetchProperties = useCallback(async () => {
    setIsLoading(true);
    try {
      const houses = await api.getHouses();
      setProperties(houses);
    } catch (error) {
      console.error("Failed to fetch properties:", error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleDelete = useCallback(async (houseId: string) => {
    // The API call is already made in PropertyCard component, so we don't need to call it again here
    // Just update the local state to remove the property
    setFilteredProperties((prev) => prev.filter((prop) => prop.house_id !== houseId));
    setProperties((prev) => prev.filter((prop) => prop.house_id !== houseId));
  }, []);

  const handleContactedChange = useCallback(async (houseId: string, contacted: boolean) => {
    // The API call is already made in PropertyCard component
    // Just update the local state with the new status
    const updateProperties = (prev: House[]) =>
      prev.map((prop) =>
        prop.house_id === houseId ? { ...prop, contacted } : prop
      );
    setFilteredProperties(updateProperties);
    setProperties(updateProperties);
  }, []);

  const handleFavoriteChange = useCallback(async (houseId: string, favorite: boolean) => {
    const updateProperties = (prev: House[]) =>
      prev.map((prop) =>
        prop.house_id === houseId ? { ...prop, favorite } : prop
      );
    setFilteredProperties(updateProperties);
    setProperties(updateProperties);
  }, []);

  // Load more properties as user scrolls
  const handleScroll = useCallback(() => {
    // Check if we're near bottom of page
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 500) {
      setDisplayCount(prev => Math.min(prev + 5, filteredProperties.length));
    }
  }, [filteredProperties.length]);

  useEffect(() => {
    fetchProperties();
  }, [fetchProperties]);

  // Setup scroll event listener for windowed rendering
  useEffect(() => {
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [handleScroll]);

  // Separate effect for applying filters
  useEffect(() => {
    if (properties.length > 0) {
      setFilteredProperties(properties);
      setDisplayCount(10); // Reset display count when properties change
    }
  }, [properties]);

  // Effect for sorting the filtered properties
  useEffect(() => {
    const sortProperties = (houses: House[]) => {
      return [...houses].sort((a, b) => {
        // Handle Price and Area as numbers
        if (sortColumn === 'Price' || sortColumn === 'Area') {
          const aValue = a[sortColumn as keyof House];
          const bValue = b[sortColumn as keyof House];
          
          // Convert to numbers, removing any non-numeric characters except decimal points
          const aNum = typeof aValue === 'number' ? aValue : 
            parseFloat((aValue as string).replace(/[^\d.]/g, '')) || 0;
          const bNum = typeof bValue === 'number' ? bValue : 
            parseFloat((bValue as string).replace(/[^\d.]/g, '')) || 0;

          return sortOrder === 'asc' ? aNum - bNum : bNum - aNum;
        }
        
        // Handle Bedrooms
        if (sortColumn === 'Bedrooms') {
          const aString = String(a[sortColumn]).toLowerCase();
          const bString = String(b[sortColumn]).toLowerCase();
          
          // Convert 'studio' to '0' for sorting purposes
          const aNum = aString === 'studio' ? 0 : parseInt(aString) || 0;
          const bNum = bString === 'studio' ? 0 : parseInt(bString) || 0;
          
          return sortOrder === 'asc' ? aNum - bNum : bNum - aNum;
        }
        
        // Default string comparison for other columns
        const aString = String(a[sortColumn as keyof House] || '').toLowerCase();
        const bString = String(b[sortColumn as keyof House] || '').toLowerCase();
        return sortOrder === 'asc' 
          ? aString.localeCompare(bString)
          : bString.localeCompare(aString);
      });
    };

    setFilteredProperties(sortProperties(properties));
  }, [sortColumn, sortOrder, properties]);

  return (
    <div className="min-h-screen bg-black">
      <header className="sticky top-0 z-10 bg-black/80 backdrop-blur-lg">
        <div className="flex justify-between items-center p-4">
          <h1 className="text-xl font-semibold tracking-tight">
            Lisbon Rentals
          </h1>
          <button
            onClick={() => setIsFilterOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 hover:bg-white/10 active:scale-95 transition"
          >
            <Filter size={18} />
            <span className="text-sm font-medium">Filters</span>
            <ChevronDown size={16} className="text-zinc-400" />
          </button>
        </div>
      </header>
      <div
        className="p-4 space-y-4"
      >
        {isLoading ? (
          <div className="flex justify-center items-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-white"></div>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredProperties.slice(0, displayCount).map((property) => (
              <MemoizedPropertyCard
                key={`${property.Name}-${property.URL}`}
                house={property}
                onDelete={() => handleDelete(property.house_id)}
                onContactedChange={(contacted) => handleContactedChange(property.house_id, contacted)}
                onFavoriteChange={(favorite) => handleFavoriteChange(property.house_id, favorite)}
              />
            ))}
            {displayCount < filteredProperties.length && (
              <div className="py-8 flex justify-center">
                <div className="animate-spin rounded-full h-6 w-6 border-t-2 border-white"></div>
              </div>
            )}
          </div>
        )}
      </div>
      <AnimatePresence>
        {isFilterOpen && (
          <FilterSheet 
            onClose={() => setIsFilterOpen(false)} 
            onSort={(column, order) => {
              setSortColumn(column);
              setSortOrder(order);
            }}
            properties={properties}
            onFilter={(filtered) => {
              setFilteredProperties(filtered);
              setDisplayCount(10); // Reset display count when filters change
            }}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
