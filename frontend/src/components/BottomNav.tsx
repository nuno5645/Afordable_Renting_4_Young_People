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
        y: 50,
      }}
      animate={{
        y: 0,
      }}
      transition={{
        type: "tween",
        duration: 0.2,
      }}
      style={{
        willChange: 'transform',
        backfaceVisibility: 'hidden',
        WebkitBackfaceVisibility: 'hidden',
        transform: 'translateZ(0)',
        WebkitTransform: 'translateZ(0)',
      }}
    >
      <div className="flex justify-around items-center h-16 px-2 max-w-lg mx-auto">
        {navItems.map(({ icon: Icon, path, label }) => (
          <motion.button
            key={path}
            className={`flex flex-col items-center justify-center w-16 h-16 relative ${location.pathname === path ? "text-white" : "text-zinc-500"}`}
            onClick={() => handleNavigation(path)}
            whileTap={{
              scale: 0.95,
            }}
            transition={{
              duration: 0.1,
            }}
          >
            {location.pathname === path && (
              <motion.div
                className="absolute inset-0 bg-white/5 rounded-xl"
                layoutId="navBackground"
                transition={{
                  type: "tween",
                  duration: 0.2,
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
