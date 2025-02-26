import React from "react";
import { Routes, Route, useLocation } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { BottomNav } from "./BottomNav";
import { HomePage } from "./HomePage";
import { FavoritesPage } from "./FavoritesPage";
import { SearchPage } from "./SearchPage";
import { ProfilePage } from "./ProfilePage";
import { AnalyticsPage } from "./AnalyticsPage";

// Optimized page transitions for better performance on mobile
const pageVariants = {
  initial: {
    opacity: 0,
    x: 0, // Removed horizontal movement which can cause flickering
  },
  animate: {
    opacity: 1,
    x: 0,
  },
  exit: {
    opacity: 0,
    x: 0, // Removed horizontal movement which can cause flickering
  },
};

export function Layout() {
  const location = useLocation();

  return (
    <div className="flex flex-col min-h-screen bg-black text-white">
      <div className="flex-1 relative">
        <AnimatePresence mode="wait" initial={false}>
          <motion.main
            key={location.pathname}
            variants={pageVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={{
              type: "tween", // Changed from "spring" to "tween" for smoother performance
              duration: 0.2, // Shorter duration for better performance
            }}
            className="w-full min-h-[calc(100vh-4rem)] pb-16"
            style={{
              willChange: "opacity", // Optimized for opacity changes only
              backfaceVisibility: "hidden",
              WebkitBackfaceVisibility: "hidden",
            }}
          >
            <Routes location={location}>
              <Route path="/" element={<HomePage />} />
              <Route path="/favorites" element={<FavoritesPage />} />
              <Route path="/search" element={<SearchPage />} />
              <Route path="/analytics" element={<AnalyticsPage />} />
              <Route path="/profile" element={<ProfilePage />} />
            </Routes>
          </motion.main>
        </AnimatePresence>
      </div>
      <BottomNav />
    </div>
  );
}
