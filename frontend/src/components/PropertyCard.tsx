import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Heart, Bed, Square, Train, MapPin, Trash2, Check } from "lucide-react";
import { House } from "../services/api";

interface PropertyCardProps {
  house: House;
  onDelete?: () => void;
  onContactedChange?: (contacted: boolean) => void;
}

const mockImages = [
  "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80",
  "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80",
  "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80",
];

export function PropertyCard({ 
  house,
  onDelete,
  onContactedChange,
}: PropertyCardProps) {
  const [isContacted, setIsContacted] = useState(house.contacted);
  const [isFavorite, setIsFavorite] = useState(house.favorite);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleContact = () => {
    navigator.vibrate?.([1, 30, 1]);
    window.open(house.URL, '_blank');
  };

  const handleContactedToggle = () => {
    const newState = !isContacted;
    setIsContacted(newState);
    onContactedChange?.(newState);
  };

  const handleFavoriteToggle = async () => {
    navigator.vibrate?.([1, 30, 1]);
    const newState = await api.toggleFavorite(house.Name);
    setIsFavorite(newState);
  };

  const handleDelete = () => {
    setIsDeleting(true);
    setTimeout(() => {
      onDelete?.();
    }, 500); // Increased duration to match new animation
  };

  const randomImage = mockImages[Math.floor(Math.random() * mockImages.length)];

  return (
    <AnimatePresence mode="popLayout">
      {!isDeleting && (
        <motion.div
          key={house.Name}
          className="bg-zinc-900/95 backdrop-blur-xl rounded-3xl overflow-hidden shadow-2xl border border-white/5"
          initial={{
            opacity: 0,
            y: 20,
            scale: 0.95,
          }}
          whileInView={{
            opacity: 1,
            y: 0,
            scale: 1,
          }}
          exit={{
            opacity: 0,
            scale: 0.98,
            y: 20,
            transition: {
              duration: 0.5,
              ease: [0.32, 0.72, 0, 1], // Custom easing for more natural motion
            }
          }}
          viewport={{
            once: true,
            margin: "-50px",
          }}
          transition={{
            type: "spring",
            damping: 20,
            stiffness: 300,
          }}
          whileHover={{
            y: -4,
            transition: {
              duration: 0.2,
            },
          }}
        >
          <div className="relative">
            <motion.div
              className="aspect-[16/9] bg-zinc-800 relative overflow-hidden"
              whileHover={{
                scale: 1.02,
              }}
              transition={{
                type: "spring",
                damping: 20,
                stiffness: 300,
              }}
            >
              <motion.img
                src={randomImage}
                alt="Property"
                className="w-full h-full object-cover"
                initial={{
                  scale: 1.2,
                  opacity: 0,
                }}
                animate={{
                  scale: 1,
                  opacity: 1,
                }}
                transition={{
                  duration: 0.5,
                }}
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent" />
            </motion.div>
            <motion.button
              className={`absolute top-4 right-4 p-3 ${
                isFavorite 
                  ? "bg-red-500 border-red-600" 
                  : "bg-white/10 border-white/20"
              } backdrop-blur-xl rounded-full border`}
              whileTap={{
                scale: 0.9,
              }}
              whileHover={{
                scale: 1.1,
                backgroundColor: isFavorite ? "rgb(239, 68, 68)" : "rgba(255, 255, 255, 0.2)",
              }}
              transition={{
                type: "spring",
                damping: 15,
                stiffness: 400,
              }}
              onClick={handleFavoriteToggle}
            >
              <Heart 
                size={20} 
                className={isFavorite ? "text-white" : "text-white"} 
                fill={isFavorite ? "currentColor" : "none"}
              />
            </motion.button>
          </div>
          <div className="p-6">
            <motion.div
              className="flex items-center gap-2 text-zinc-400 text-sm mb-3"
              initial={{
                opacity: 0,
              }}
              animate={{
                opacity: 1,
              }}
            >
              <MapPin size={14} />
              <span>{house.Location}</span>
            </motion.div>
            <motion.div
              className="text-3xl font-bold text-white tracking-tight"
              initial={{
                opacity: 0,
                y: 10,
              }}
              animate={{
                opacity: 1,
                y: 0,
              }}
              transition={{
                delay: 0.1,
              }}
            >
              €{house.Price.toLocaleString()}/month
            </motion.div>
            <motion.div
              className="mt-4 flex gap-6 text-zinc-400"
              initial={{
                opacity: 0,
                y: 10,
              }}
              animate={{
                opacity: 1,
                y: 0,
              }}
              transition={{
                delay: 0.2,
              }}
            >
              <div className="flex items-center gap-2">
                <Bed size={18} />
                <span className="text-sm">{house.Bedrooms}</span>
              </div>
              <div className="flex items-center gap-2">
                <Square size={18} />
                <span className="text-sm">{house.Area}</span>
              </div>
            </motion.div>
            <div className="mt-6 flex gap-3">
              <motion.button
                className="flex-1 bg-white text-black py-3.5 rounded-xl font-medium shadow-lg"
                whileTap={{
                  scale: 0.98,
                }}
                whileHover={{
                  scale: 1.02,
                  backgroundColor: "rgba(255, 255, 255, 0.9)",
                }}
                transition={{
                  type: "spring",
                  damping: 15,
                  stiffness: 400,
                }}
                onClick={handleContact}
              >
                Contact Agent
              </motion.button>
              <motion.button
                className={`px-4 py-3.5 rounded-xl font-medium border ${
                  isContacted 
                    ? "bg-green-500 border-green-600 text-white" 
                    : "border-white/10 hover:bg-white/5 text-white"
                }`}
                whileTap={{
                  scale: 0.98,
                }}
                whileHover={{
                  scale: 1.02,
                }}
                transition={{
                  type: "spring",
                  damping: 15,
                  stiffness: 400,
                }}
                onClick={handleContactedToggle}
              >
                <Check size={20} className={isContacted ? "text-white" : "text-zinc-400"} />
              </motion.button>
              <motion.button
                className="px-4 py-3.5 rounded-xl font-medium bg-red-500/10 hover:bg-red-500/20 border-red-500/30 border text-red-500"
                whileTap={{
                  scale: 0.98,
                }}
                whileHover={{
                  scale: 1.02,
                  backgroundColor: "rgba(239, 68, 68, 0.3)", // red-500 with more opacity
                }}
                transition={{
                  type: "spring",
                  damping: 15,
                  stiffness: 400,
                }}
                onClick={handleDelete}
              >
                <Trash2 size={20} />
              </motion.button>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
