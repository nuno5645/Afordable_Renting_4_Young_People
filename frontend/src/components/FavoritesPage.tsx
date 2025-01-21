import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { PropertyCard } from "./PropertyCard";
import api, { House } from "../services/api";

export function FavoritesPage() {
  const [favorites, setFavorites] = useState<House[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchFavorites();
  }, []);

  const fetchFavorites = async () => {
    setIsLoading(true);
    const houses = await api.getHouses();
    setFavorites(houses.filter(house => house.favorite));
    setIsLoading(false);
  };

  const handleDelete = async (name: string) => {
    await api.toggleDiscarded(name);
    setFavorites((prev) => prev.filter((prop) => prop.Name !== name));
  };

  const handleContactedChange = async (name: string, contacted: boolean) => {
    const newState = await api.toggleContacted(name);
    setFavorites((prev) =>
      prev.map((prop) =>
        prop.Name === name ? { ...prop, contacted: newState } : prop
      )
    );
  };

  return (
    <div className="min-h-screen bg-black">
      <header className="sticky top-0 z-10 bg-black/80 backdrop-blur-lg">
        <div className="flex justify-between items-center p-4">
          <h1 className="text-xl font-semibold">Saved Properties</h1>
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
        ) : favorites.length > 0 ? (
          favorites.map((property) => (
            <PropertyCard
              key={property.Name}
              house={property}
              onDelete={() => handleDelete(property.Name)}
              onContactedChange={(contacted) => handleContactedChange(property.Name, contacted)}
            />
          ))
        ) : (
          <div className="flex flex-col items-center justify-center h-[60vh] text-zinc-400">
            <p className="text-center">No saved properties yet</p>
            <p className="text-center text-sm mt-2">
              Tap the heart icon on properties you like to save them here
            </p>
          </div>
        )}
      </motion.div>
    </div>
  );
}
