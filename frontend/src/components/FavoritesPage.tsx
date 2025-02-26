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

  // Add effect to refetch favorites when page becomes visible
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        fetchFavorites();
      }
    };

    // Refetch when the page gets focus
    const handleFocus = () => {
      fetchFavorites();
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('focus', handleFocus);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('focus', handleFocus);
    };
  }, []);

  const fetchFavorites = async () => {
    setIsLoading(true);
    const houses = await api.getHouses();
    setFavorites(houses.filter(house => house.favorite));
    setIsLoading(false);
  };

  const handleDelete = async (houseId: string) => {
    // The API call is already made in PropertyCard component, so we don't need to call it again here
    // Just update the local state to remove the property
    setFavorites((prev) => prev.filter((prop) => prop.house_id !== houseId));
  };

  const handleContactedChange = async (houseId: string, contacted: boolean) => {
    // The API call is already made in PropertyCard component
    // Just update the local state with the new status
    setFavorites((prev) =>
      prev.map((prop) =>
        prop.house_id === houseId ? { ...prop, contacted } : prop
      )
    );
  };

  const handleFavoriteChange = async (houseId: string, favorite: boolean) => {
    // If favorite is set to false, remove from the list
    if (!favorite) {
      setFavorites((prev) => prev.filter((prop) => prop.house_id !== houseId));
    } else {
      // Update the favorite status (this shouldn't happen in this view but adding for completeness)
      setFavorites((prev) =>
        prev.map((prop) =>
          prop.house_id === houseId ? { ...prop, favorite } : prop
        )
      );
    }
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
              onDelete={() => handleDelete(property.house_id)}
              onContactedChange={(contacted) => handleContactedChange(property.house_id, contacted)}
              onFavoriteChange={(favorite) => handleFavoriteChange(property.house_id, favorite)}
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
