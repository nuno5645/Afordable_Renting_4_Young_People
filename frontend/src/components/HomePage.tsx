import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Filter, ChevronDown } from "lucide-react";
import { PropertyCard } from "./PropertyCard";
import { FilterSheet } from "./FilterSheet";
import api, { House } from "../services/api";

export function HomePage() {
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [properties, setProperties] = useState<House[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [sortColumn, setSortColumn] = useState<string>('Price');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  useEffect(() => {
    fetchProperties();
  }, [sortColumn, sortOrder]);

  const fetchProperties = async () => {
    setIsLoading(true);
    const houses = await api.getHouses(sortColumn, sortOrder);
    setProperties(houses);
    setIsLoading(false);
  };

  const handleDelete = async (name: string) => {
    await api.toggleDiscarded(name);
    setProperties((prev) => prev.filter((prop) => prop.Name !== name));
  };

  const handleContactedChange = async (name: string, contacted: boolean) => {
    const newState = await api.toggleContacted(name);
    setProperties((prev) =>
      prev.map((prop) =>
        prop.Name === name ? { ...prop, contacted: newState } : prop
      )
    );
  };

  return (
    <div className="min-h-screen bg-black">
      <header className="sticky top-0 z-10 bg-black/80 backdrop-blur-lg">
        <div className="flex justify-between items-center p-4">
          <h1 className="text-xl font-semibold tracking-tight">
            Lisbon Rentals
          </h1>
          <motion.button
            whileTap={{
              scale: 0.95,
            }}
            onClick={() => setIsFilterOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 hover:bg-white/10 transition-colors"
          >
            <Filter size={18} />
            <span className="text-sm font-medium">Filters</span>
            <ChevronDown size={16} className="text-zinc-400" />
          </motion.button>
        </div>
      </header>
      <motion.div
        className="p-4 space-y-4"
        initial={{
          opacity: 0,
        }}
        animate={{
          opacity: 1,
        }}
      >
        {isLoading ? (
          <div className="flex justify-center items-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-white"></div>
          </div>
        ) : (
          properties.map((property) => (
            <PropertyCard
              key={property.Name}
              house={property}
              onDelete={() => handleDelete(property.Name)}
              onContactedChange={(contacted) => handleContactedChange(property.Name, contacted)}
            />
          ))
        )}
      </motion.div>
      <AnimatePresence>
        {isFilterOpen && (
          <FilterSheet 
            onClose={() => setIsFilterOpen(false)} 
            onSort={(column, order) => {
              setSortColumn(column);
              setSortOrder(order);
            }}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
