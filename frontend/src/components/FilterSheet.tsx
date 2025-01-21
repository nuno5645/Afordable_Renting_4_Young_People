import React, { useState } from "react";
import { motion } from "framer-motion";
import { X, ChevronDown, ArrowUpDown } from "lucide-react";

interface FilterSheetProps {
  onClose: () => void;
  onSort: (column: string, order: 'asc' | 'desc') => void;
}

export function FilterSheet({ onClose, onSort }: FilterSheetProps) {
  const [priceRange, setPriceRange] = useState(1500);
  const [selectedType, setSelectedType] = useState("");
  const [sortColumn, setSortColumn] = useState("Price");
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const handleSort = (column: string) => {
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
  };

  return (
    <motion.div
      className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm"
      initial={{
        opacity: 0,
      }}
      animate={{
        opacity: 1,
      }}
      exit={{
        opacity: 0,
      }}
      onClick={handleOverlayClick}
    >
      <motion.div
        className="absolute bottom-0 w-full bg-zinc-900/95 rounded-t-3xl border-t border-white/5 backdrop-blur-xl"
        initial={{
          y: "100%",
        }}
        animate={{
          y: 0,
        }}
        exit={{
          y: "100%",
        }}
        transition={{
          type: "spring",
          damping: 25,
          stiffness: 300,
        }}
      >
        <div className="relative p-6">
          <div className="absolute left-1/2 -translate-x-1/2 top-3 w-12 h-1 bg-white/20 rounded-full" />
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold tracking-tight">Filters</h2>
            <motion.button
              whileTap={{
                scale: 0.9,
              }}
              onClick={onClose}
              className="p-2 hover:bg-white/5 rounded-full"
            >
              <X size={20} />
            </motion.button>
          </div>

          <div className="space-y-8">
            {/* Sort Options */}
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
                  <motion.button
                    key={option.value}
                    className={`flex justify-between items-center p-3 rounded-xl text-sm font-medium border ${
                      sortColumn === option.value 
                        ? "bg-white text-black border-white" 
                        : "border-white/10 hover:bg-white/5"
                    }`}
                    whileTap={{
                      scale: 0.98,
                    }}
                    onClick={() => handleSort(option.value)}
                  >
                    <span>{option.label}</span>
                    {sortColumn === option.value && (
                      <ArrowUpDown size={16} className={sortOrder === 'asc' ? 'rotate-0' : 'rotate-180'} />
                    )}
                  </motion.button>
                ))}
              </div>
            </div>

            {/* Price Range */}
            <div>
              <label className="text-sm font-medium text-zinc-400 block mb-4">
                Price Range: €{priceRange}
              </label>
              <input
                type="range"
                className="w-full accent-white"
                min="500"
                max="5000"
                step="100"
                value={priceRange}
                onChange={(e) => setPriceRange(Number(e.target.value))}
              />
              <div className="flex justify-between mt-2 text-xs text-zinc-500">
                <span>€500</span>
                <span>€5,000</span>
              </div>
            </div>

            {/* Property Type */}
            <div>
              <label className="text-sm font-medium text-zinc-400 block mb-3">
                Property Type
              </label>
              <div className="grid grid-cols-2 gap-2">
                {["Studio", "1 Bedroom", "2 Bedrooms", "3+ Bedrooms"].map(
                  (type) => (
                    <motion.button
                      key={type}
                      className={`p-3 rounded-xl text-sm font-medium border ${
                        selectedType === type 
                          ? "bg-white text-black border-white" 
                          : "border-white/10 hover:bg-white/5"
                      }`}
                      whileTap={{
                        scale: 0.98,
                      }}
                      onClick={() => setSelectedType(type)}
                    >
                      {type}
                    </motion.button>
                  )
                )}
              </div>
            </div>

            <motion.button
              className="w-full bg-white text-black py-4 rounded-xl font-medium mt-6"
              whileTap={{
                scale: 0.98,
              }}
              onClick={onClose}
            >
              Show Results
            </motion.button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}
