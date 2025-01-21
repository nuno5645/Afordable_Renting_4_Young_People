import React from "react";
import { motion } from "framer-motion";
import { Settings, Bell, HelpCircle } from "lucide-react";
export function ProfilePage() {
  return (
    <div className="min-h-screen bg-black">
      <header className="sticky top-0 z-10 bg-black/80 backdrop-blur-lg">
        <div className="p-4">
          <h1 className="text-xl font-semibold">Profile</h1>
        </div>
      </header>
      <div className="p-4">
        <div className="flex items-center space-x-4 mb-8">
          <div className="w-20 h-20 rounded-full bg-zinc-800" />
          <div>
            <h2 className="text-lg font-semibold">Guest User</h2>
            <p className="text-zinc-400">Sign in to save properties</p>
          </div>
        </div>
        {[
          {
            icon: Settings,
            label: "Settings",
          },
          {
            icon: Bell,
            label: "Notifications",
          },
          {
            icon: HelpCircle,
            label: "Help Center",
          },
        ].map(({ icon: Icon, label }) => (
          <motion.button
            key={label}
            className="flex items-center space-x-4 w-full p-4 bg-zinc-900 rounded-lg mb-2"
            whileTap={{
              scale: 0.98,
            }}
          >
            <Icon size={20} />
            <span>{label}</span>
          </motion.button>
        ))}
      </div>
    </div>
  );
}
