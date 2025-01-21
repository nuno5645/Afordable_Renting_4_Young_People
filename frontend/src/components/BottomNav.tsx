import React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Home, Heart, Search, User, BarChart2 } from "lucide-react";
import { motion } from "framer-motion";
export function BottomNav() {
  const navigate = useNavigate();
  const location = useLocation();
  const handleNavigation = (path: string) => {
    navigator.vibrate?.([1, 30, 1]);
    navigate(path);
  };
  const navItems = [
    {
      icon: Home,
      path: "/",
      label: "Home",
    },
    {
      icon: Heart,
      path: "/favorites",
      label: "Favorites",
    },
    {
      icon: Search,
      path: "/search",
      label: "Search",
    },
    {
      icon: BarChart2,
      path: "/analytics",
      label: "Analytics",
    },
    {
      icon: User,
      path: "/profile",
      label: "Profile",
    },
  ];
  return (
    <motion.nav
      className="fixed bottom-0 w-full bg-black/80 backdrop-blur-xl border-t border-white/5"
      initial={{
        y: 100,
      }}
      animate={{
        y: 0,
      }}
      transition={{
        type: "spring",
        stiffness: 300,
        damping: 30,
      }}
    >
      <div className="flex justify-around items-center h-16 px-2 max-w-lg mx-auto">
        {navItems.map(({ icon: Icon, path, label }) => (
          <motion.button
            key={path}
            className={`flex flex-col items-center justify-center w-16 h-16 relative ${location.pathname === path ? "text-white" : "text-zinc-500"}`}
            onClick={() => handleNavigation(path)}
            whileTap={{
              scale: 0.9,
            }}
            whileHover={{
              scale: 1.1,
            }}
            transition={{
              type: "spring",
              stiffness: 400,
              damping: 17,
            }}
          >
            {location.pathname === path && (
              <motion.div
                className="absolute inset-0 bg-white/5 rounded-xl"
                layoutId="navBackground"
                transition={{
                  type: "spring",
                  stiffness: 300,
                  damping: 30,
                }}
              />
            )}
            <Icon size={22} />
            <span className="text-xs mt-1 font-medium">{label}</span>
          </motion.button>
        ))}
      </div>
    </motion.nav>
  );
}
