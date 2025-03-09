import React, { useState, useEffect, useRef } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Heart, Bed, Square, Train, MapPin, Trash2, Check, ChevronLeft, ChevronRight, ImageOff } from "lucide-react";
import { House } from "../services/api";
import api from "../services/api";

interface PropertyCardProps {
  house: House;
  onDelete?: () => void;
  onContactedChange?: (contacted: boolean) => void;
  onFavoriteChange?: (favorite: boolean) => void;
}

// Add back mockImages for fallback
const mockImages = [
  "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80",
  "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80",
  "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80",
];

export function PropertyCard({ 
  house,
  onDelete,
  onContactedChange,
  onFavoriteChange,
}: PropertyCardProps) {
  const [isContacted, setIsContacted] = useState(house.contacted);
  const [isFavorite, setIsFavorite] = useState(house.favorite);
  const [isDeleting, setIsDeleting] = useState(false);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [isImageLoaded, setIsImageLoaded] = useState(false);
  const cardRef = useRef<HTMLDivElement>(null);

  // Check if we have any images
  const hasImages = Array.isArray(house.image_urls) && house.image_urls.length > 0;
  
  const images = hasImages ? house.image_urls : [];
  
  const currentImage = images[currentImageIndex];

  // Preload all images upfront
  useEffect(() => {
    if (hasImages && images.length > 0) {
      // Preload current image first
      const img = new Image();
      img.onload = () => setIsImageLoaded(true);
      img.src = currentImage;

      // Then preload the rest in the background
      if (images.length > 1) {
        const preloadImages = images.filter((_: string, i: number) => i !== currentImageIndex);
        preloadImages.forEach((src: string) => {
          const img = new Image();
          img.src = src;
        });
      }
    }
  }, []);

  // Reset image loaded state when changing images
  useEffect(() => {
    setIsImageLoaded(false);
    const img = new Image();
    img.onload = () => setIsImageLoaded(true);
    img.src = currentImage;
  }, [currentImageIndex, currentImage]);

  const handleContact = () => {
    try {
      if (navigator.vibrate) {
        navigator.vibrate([1, 30, 1]);
      }
    } catch (e) {
      // Ignore vibration errors
    }
    window.open(house.url, '_blank');
  };

  const handleContactedToggle = async () => {
    try {
      const newStatus = await api.toggleContacted(house.house_id);
      setIsContacted(newStatus);
      if (onContactedChange) {
        onContactedChange(newStatus);
      }
    } catch (error) {
      console.error("Error toggling contacted status:", error);
    }
  };

  const handleFavoriteToggle = async (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent card click
    
    // Add vibration feedback
    try {
      if (navigator.vibrate) {
        navigator.vibrate([1, 30, 1]);
      }
    } catch (error) {
      // Ignore vibration errors
    }
    
    try {
      const newStatus = await api.toggleFavorite(house.house_id);
      setIsFavorite(newStatus);
      if (onFavoriteChange) {
        onFavoriteChange(newStatus);
      }
    } catch (error) {
      console.error("Error toggling favorite status:", error);
    }
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    
    try {
      const discarded = await api.toggleDiscarded(house.house_id);
      if (discarded && onDelete) {
        // Add a small delay before calling onDelete to allow the animation to play
        setTimeout(() => {
          onDelete();
        }, 300);
      } else {
        // If the request failed or was unsuccessful, reset the deleting state
        setIsDeleting(false);
      }
    } catch (error) {
      console.error("Error discarding property:", error);
      setIsDeleting(false);
    }
  };

  const handleNextImage = () => {
    setCurrentImageIndex((prev) => (prev + 1) % images.length);
  };

  const handlePrevImage = () => {
    setCurrentImageIndex((prev) => (prev - 1 + images.length) % images.length);
  };

  // Simplified animation for better performance
  return (
    <div className={`transform transition-all duration-200 ease-out ${isDeleting ? 'opacity-0 translate-y-4' : ''}`}>
      {!isDeleting && (
        <div
          ref={cardRef}
          className="bg-zinc-900/95 backdrop-blur-xl rounded-3xl overflow-hidden shadow-2xl border border-white/5 transition-transform duration-200 ease-out hover:-translate-y-1"
          style={{
            willChange: 'opacity, transform',
            backfaceVisibility: 'hidden',
            WebkitBackfaceVisibility: 'hidden',
            transform: 'translateZ(0)',
            WebkitTransform: 'translateZ(0)',
          }}
        >
          <div className="relative">
            <div
              className="aspect-[16/10] bg-zinc-800 relative overflow-hidden"
              style={{
                willChange: 'transform',
                backfaceVisibility: 'hidden',
                WebkitBackfaceVisibility: 'hidden',
                transform: 'translateZ(0)',
              }}
            >
              {!hasImages ? (
                // Show No Photo Warning when no images are available
                <div className="w-full h-full flex flex-col items-center justify-center bg-zinc-800 text-zinc-400">
                  <ImageOff size={48} className="mb-2 text-zinc-500" />
                  <div className="text-lg font-medium">No Photo Available</div>
                  <div className="text-sm text-zinc-500">Property image has been hidden</div>
                </div>
              ) : (
                // Show actual image when available with optimized loading
                <div className="w-full h-full relative">
                  {images.map((src: string, index: number) => (
                    <img
                      key={src}
                      src={src}
                      alt={`Property view ${index + 1}`}
                      className="absolute inset-0 w-full h-full object-cover transition-opacity duration-300"
                      style={{
                        opacity: index === currentImageIndex && isImageLoaded ? 1 : 0,
                        transform: 'translateZ(0)',
                      }}
                      onLoad={() => {
                        if (index === currentImageIndex) {
                          setIsImageLoaded(true);
                        }
                      }}
                    />
                  ))}
                  {!isImageLoaded && (
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="w-8 h-8 border-2 border-white/20 border-t-white/80 rounded-full animate-spin"></div>
                    </div>
                  )}
                </div>
              )}
              
              <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent" />
              
              {/* Image navigation - simplified with better touch target */}
              {hasImages && images.length > 1 && (
                <>
                  <button
                    className="absolute left-2 top-1/2 -translate-y-1/2 p-2 bg-black/20 hover:bg-black/40 backdrop-blur-sm rounded-full border border-white/10 active:scale-95 transition-transform"
                    onClick={handlePrevImage}
                    style={{ touchAction: 'manipulation' }}
                  >
                    <ChevronLeft size={24} className="text-white" />
                  </button>
                  <button
                    className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-black/20 hover:bg-black/40 backdrop-blur-sm rounded-full border border-white/10 active:scale-95 transition-transform"
                    onClick={handleNextImage}
                    style={{ touchAction: 'manipulation' }}
                  >
                    <ChevronRight size={24} className="text-white" />
                  </button>
                  
                  {/* Image counter - now static */}
                  <div className="absolute bottom-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-black/40 backdrop-blur-sm rounded-full text-xs text-white/90 font-medium border border-white/10">
                    {currentImageIndex + 1} / {images.length}
                  </div>
                </>
              )}
            </div>
            <button
              className={`absolute top-4 right-4 p-3 ${
                isFavorite 
                  ? "bg-red-500 border-red-600" 
                  : "bg-white/10 border-white/20"
              } backdrop-blur-xl rounded-full border active:scale-95 transition-transform`}
              style={{
                transform: 'translateZ(0)',
                touchAction: 'manipulation'
              }}
              onClick={handleFavoriteToggle}
            >
              <Heart 
                size={20} 
                className={isFavorite ? "text-white" : "text-white"} 
                fill={isFavorite ? "currentColor" : "none"}
              />
            </button>
          </div>
          <div className="p-4">
            <div className="flex items-center gap-2 text-zinc-400 text-sm mb-2">
              <MapPin size={14} />
              <span>
                {[house.freguesia, house.concelho].filter(Boolean).join(", ") || house.zone}
              </span>
            </div>
            <div className="text-2xl font-bold text-white tracking-tight">
              €{parseFloat(house.price || '0').toLocaleString()}/month
            </div>
            <div className="mt-3 flex gap-6 text-zinc-400">
              <div className="flex items-center gap-2">
                <Bed size={16} />
                <span className="text-sm">{house.bedrooms}</span>
              </div>
              <div className="flex items-center gap-2">
                <Square size={16} />
                <span className="text-sm">{house.area} m²</span>
                <span className="text-xs text-zinc-500 ml-2">·</span>
                <span className="text-xs text-zinc-500">{house.source}</span>
              </div>
            </div>
            <div className="mt-4 flex gap-3">
              <button
                className="flex-1 bg-white text-black py-3.5 rounded-xl font-medium shadow-lg hover:bg-white/90 active:scale-95 transition-transform"
                onClick={handleContact}
                style={{ touchAction: 'manipulation' }}
              >
                Contact Agent
              </button>
              <button
                className={`px-4 py-3.5 rounded-xl font-medium border transition-colors active:scale-95 ${
                  isContacted 
                    ? "bg-green-500 border-green-600 text-white" 
                    : "border-white/10 hover:bg-white/5 text-white"
                }`}
                onClick={handleContactedToggle}
                style={{ touchAction: 'manipulation' }}
              >
                <Check size={20} className={isContacted ? "text-white" : "text-zinc-400"} />
              </button>
              <button
                className="px-4 py-3.5 rounded-xl font-medium bg-red-500/10 hover:bg-red-500/20 border-red-500/30 border text-red-500 transition-colors active:scale-95"
                onClick={handleDelete}
                style={{ touchAction: 'manipulation' }}
              >
                <Trash2 size={20} />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
