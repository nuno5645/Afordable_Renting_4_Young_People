import React, { useState, useMemo, useCallback, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { X, ArrowUpDown, ChevronUp } from "lucide-react";
import { House } from "../services/api";

interface FilterSheetProps {
  onClose: () => void;
  onSort: (column: string, order: 'asc' | 'desc') => void;
  properties: House[];
  onFilter: (filteredProperties: House[]) => void;
}

// Optimized sheet animation variants
const sheetVariants = {
  hidden: { y: "100%" },
  visible: { 
    y: 0,
    transition: {
      type: "tween",
      duration: 0.3,
      ease: "easeOut"
    }
  },
  exit: { 
    y: "100%", 
    transition: {
      type: "tween",
      duration: 0.2,
      ease: "easeIn"
    }
  }
};

export function FilterSheet({ onClose, onSort, properties, onFilter }: FilterSheetProps) {
  const [priceRange, setPriceRange] = useState(1500);
  const [selectedType, setSelectedType] = useState("");
  const [selectedSource, setSelectedSource] = useState("");
  const [sortColumn, setSortColumn] = useState("Price");
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [isExpanded, setIsExpanded] = useState(false);
  const contentRef = useRef<HTMLDivElement>(null);
  const touchStartY = useRef(0);
  const touchMoveY = useRef(0);

  // Calculate initial height (40% of viewport)
  const initialHeight = typeof window !== 'undefined' ? `${window.innerHeight * 0.4}px` : '40vh';

  const filteredProperties = useMemo(() => {
    return properties.filter(property => {
      const price = property.Price;
      const matchesPrice = price <= priceRange;
      
      const matchesType = !selectedType || (
        selectedType === "Studio" 
          ? property.Bedrooms === "0" || property.Bedrooms.toLowerCase().includes("studio")
          : selectedType === "1 Bedroom" 
          ? property.Bedrooms === "1"
          : selectedType === "2 Bedrooms"
          ? property.Bedrooms === "2"
          : selectedType === "3+ Bedrooms"
          ? Number(property.Bedrooms) >= 3
          : true
      );

      const matchesSource = !selectedSource || property.Source === selectedSource;
      
      return matchesPrice && matchesType && matchesSource;
    });
  }, [properties, priceRange, selectedType, selectedSource]);

  const handleOverlayClick = useCallback((e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  }, [onClose]);

  const handleSort = useCallback((column: string) => {
    if (sortColumn === column) {
      // Toggle order if same column
      const newOrder = sortOrder === 'asc' ? 'desc' : 'asc';
      setSortOrder(newOrder);
      onSort(column, newOrder);
    } else {
      // New column, default to ascending
      setSortColumn(column);
      setSortOrder('asc');
      onSort(column, 'asc');
    }
  }, [sortColumn, sortOrder, onSort]);

  const handleTouchStart = useCallback((e: React.TouchEvent) => {
    touchStartY.current = e.touches[0].clientY;
  }, []);

  const handleTouchMove = useCallback((e: React.TouchEvent) => {
    touchMoveY.current = e.touches[0].clientY;
  }, []);

  const handleTouchEnd = useCallback(() => {
    const deltaY = touchStartY.current - touchMoveY.current;
    
    // If swiped up more than 50px, expand the sheet
    if (deltaY > 50 && !isExpanded) {
      setIsExpanded(true);
    }
    // If swiped down more than 50px and already expanded, collapse the sheet
    else if (deltaY < -50 && isExpanded) {
      setIsExpanded(false);
    }
    
    // Reset values
    touchStartY.current = 0;
    touchMoveY.current = 0;
  }, [isExpanded]);

  return (
    <div
      className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm"
      onClick={handleOverlayClick}
    >
      <motion.div
        className="absolute bottom-0 w-full bg-zinc-900/95 rounded-t-3xl border-t border-white/5 backdrop-blur-xl overflow-hidden"
        variants={sheetVariants}
        initial="hidden"
        animate="visible"
        exit="exit"
        style={{
          willChange: 'transform',
          transform: 'translate3d(0,0,0)',
          backfaceVisibility: 'hidden',
          WebkitBackfaceVisibility: 'hidden',
          perspective: 1000,
          WebkitPerspective: 1000,
          height: isExpanded ? 'auto' : initialHeight,
          maxHeight: isExpanded ? '90vh' : initialHeight,
          transition: 'height 0.3s ease, max-height 0.3s ease',
          display: 'flex',
          flexDirection: 'column'
        }}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
      >
        {/* Handle bar at top of sheet */}
        <div className="h-1.5 w-12 bg-white/20 rounded-full mx-auto my-3" />
        
        {/* Expandable indicator */}
        <div 
          className="flex flex-col items-center cursor-pointer mb-4"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <ChevronUp size={16} className={`transition-transform duration-300 ${isExpanded ? 'rotate-180' : ''}`} />
          <span className="text-xs mt-1">{isExpanded ? 'Collapse' : 'Expand'}</span>
        </div>
        
        <div 
          className="overflow-auto px-6 pb-6 flex-1" 
          style={{ 
            overflowY: 'auto',
            paddingBottom: '100px' // Extra padding to ensure bottom content is visible
          }}
          ref={contentRef}
        >
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold tracking-tight">Filters</h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/5 active:scale-90 rounded-full transition-transform"
            >
              <X size={20} />
            </button>
          </div>

          <div className="space-y-8">
            {/* Sort Options - Always visible initially */}
            <div>
              <label className="text-sm font-medium text-zinc-400 block mb-3">
                Sort By
              </label>
              <div className="grid grid-cols-1 gap-2">
                {[
                  { label: "Price", value: "Price" },
                  { label: "Area", value: "Area" },
                  { label: "Bedrooms", value: "Bedrooms" }
                ].map((option) => (
                  <button
                    key={option.value}
                    className={`flex justify-between items-center p-3 rounded-xl text-sm font-medium border active:scale-98 transition-transform ${
                      sortColumn === option.value 
                        ? "bg-white text-black border-white" 
                        : "border-white/10 hover:bg-white/5"
                    }`}
                    onClick={() => handleSort(option.value)}
                  >
                    <span>{option.label}</span>
                    {sortColumn === option.value && (
                      <ArrowUpDown size={16} className={sortOrder === 'asc' ? 'rotate-0' : 'rotate-180'} />
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* Price Range - Partially visible until expanded */}
            <div>
              <label className="text-sm font-medium text-zinc-400 block mb-4">
                Price Range: €{priceRange}
              </label>
              <input
                type="range"
                className="w-full accent-white"
                min="500"
                max="3000"
                step="100"
                value={priceRange}
                onChange={(e) => setPriceRange(Number(e.target.value))}
              />
              <div className="flex justify-between mt-2 text-xs text-zinc-500">
                <span>€500</span>
                <span>€3,000</span>
              </div>
            </div>

            {/* Property Type - Hidden until expanded */}
            <div>
              <label className="text-sm font-medium text-zinc-400 block mb-3">
                Property Type
              </label>
              <div className="grid grid-cols-2 gap-2">
                {["Studio", "1 Bedroom", "2 Bedrooms", "3+ Bedrooms"].map(
                  (type) => (
                    <button
                      key={type}
                      className={`p-3 rounded-xl text-sm font-medium border active:scale-95 transition-transform ${
                        selectedType === type 
                          ? "bg-white text-black border-white" 
                          : "border-white/10 hover:bg-white/5"
                      }`}
                      onClick={() => setSelectedType(type === selectedType ? "" : type)}
                    >
                      {type}
                    </button>
                  )
                )}
              </div>
            </div>

            {/* Source - Hidden until expanded */}
            <div>
              <label className="text-sm font-medium text-zinc-400 block mb-3">
                Source
              </label>
              <div className="grid grid-cols-2 gap-2">
                {["ERA", "Idealista", "Imovirtual", "Casa SAPO", "Remax"].map(
                  (source) => (
                    <button
                      key={source}
                      className={`p-3 rounded-xl text-sm font-medium border active:scale-95 transition-transform ${
                        selectedSource === source 
                          ? "bg-white text-black border-white" 
                          : "border-white/10 hover:bg-white/5"
                      }`}
                      onClick={() => setSelectedSource(source === selectedSource ? "" : source)}
                    >
                      {source}
                    </button>
                  )
                )}
              </div>
            </div>

            <button
              className="w-full bg-white text-black py-4 rounded-xl font-medium mt-6 mb-8 active:scale-98 transition-transform"
              onClick={() => {
                onFilter(filteredProperties);
                onClose();
              }}
            >
              Show Results ({filteredProperties.length})
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
