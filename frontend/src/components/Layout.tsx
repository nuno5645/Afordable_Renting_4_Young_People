import React from "react";
import { Routes, Route, useLocation } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { BottomNav } from "./BottomNav";
import { HomePage } from "./HomePage";
import { FavoritesPage } from "./FavoritesPage";
import { SearchPage } from "./SearchPage";
import { ProfilePage } from "./ProfilePage";
import { AnalyticsPage } from "./AnalyticsPage";
const pageVariants = {
  initial: {
    opacity: 0,
    x: "100%",
  },
  animate: {
    opacity: 1,
    x: 0,
  },
  exit: {
    opacity: 0,
    x: "-100%",
  },
};
export function Layout() {
  const location = useLocation();
  return (
    <div className="w-full min-h-screen bg-black text-white overflow-hidden">
      <AnimatePresence mode="wait">
        <motion.main
          key={location.pathname}
          variants={pageVariants}
          initial="initial"
          animate="animate"
          exit="exit"
          transition={{
            type: "spring",
            stiffness: 300,
            damping: 30,
          }}
          className="pb-16"
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
      <BottomNav />
    </div>
  );
}
