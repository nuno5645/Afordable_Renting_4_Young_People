import React from "react";
import { motion } from "framer-motion";
import {
  TrendingUp,
  Users,
  Home as HomeIcon,
  ArrowUp,
  ArrowDown,
} from "lucide-react";
const StatCard = ({ icon: Icon, label, value, trend, trendValue }: any) => (
  <motion.div
    className="bg-zinc-900/90 backdrop-blur-lg p-4 rounded-2xl"
    initial={{
      opacity: 0,
      y: 20,
    }}
    animate={{
      opacity: 1,
      y: 0,
    }}
    transition={{
      type: "spring",
      damping: 20,
    }}
  >
    <div className="flex justify-between items-start">
      <div className="p-2 bg-blue-500/10 rounded-xl">
        <Icon className="text-blue-500" size={20} />
      </div>
      <motion.div
        className={`flex items-center ${trend === "up" ? "text-green-500" : "text-red-500"}`}
        initial={{
          opacity: 0,
          x: 10,
        }}
        animate={{
          opacity: 1,
          x: 0,
        }}
        transition={{
          delay: 0.2,
        }}
      >
        {trend === "up" ? <ArrowUp size={16} /> : <ArrowDown size={16} />}
        <span className="text-sm ml-1">{trendValue}%</span>
      </motion.div>
    </div>
    <div className="mt-3">
      <h3 className="text-zinc-400 text-sm">{label}</h3>
      <motion.p
        className="text-2xl font-bold mt-1"
        initial={{
          opacity: 0,
          y: 5,
        }}
        animate={{
          opacity: 1,
          y: 0,
        }}
        transition={{
          delay: 0.1,
        }}
      >
        {value}
      </motion.p>
    </div>
  </motion.div>
);
export function AnalyticsPage() {
  return (
    <div className="min-h-screen bg-black">
      <header className="sticky top-0 z-10 bg-black/80 backdrop-blur-lg">
        <div className="p-4">
          <h1 className="text-xl font-semibold">Analytics</h1>
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
        transition={{
          duration: 0.3,
        }}
      >
        <div className="grid grid-cols-2 gap-4">
          <StatCard
            icon={TrendingUp}
            label="Total Views"
            value="2,847"
            trend="up"
            trendValue="12.5"
          />
          <StatCard
            icon={Users}
            label="Inquiries"
            value="164"
            trend="up"
            trendValue="8.2"
          />
          <StatCard
            icon={HomeIcon}
            label="Listed Properties"
            value="28"
            trend="down"
            trendValue="3.1"
          />
          <StatCard
            icon={TrendingUp}
            label="Conversion Rate"
            value="5.8%"
            trend="up"
            trendValue="2.4"
          />
        </div>
        <motion.div
          className="mt-8 bg-zinc-900/90 backdrop-blur-lg p-4 rounded-2xl"
          initial={{
            opacity: 0,
            y: 20,
          }}
          animate={{
            opacity: 1,
            y: 0,
          }}
          transition={{
            delay: 0.3,
            type: "spring",
            damping: 20,
          }}
        >
          <h2 className="text-lg font-semibold mb-4">Popular Areas</h2>
          {["Alfama", "Bairro Alto", "Chiado"].map((area, index) => (
            <motion.div
              key={area}
              className="flex justify-between items-center py-3 border-b border-zinc-800 last:border-0"
              initial={{
                opacity: 0,
                x: -20,
              }}
              animate={{
                opacity: 1,
                x: 0,
              }}
              transition={{
                delay: 0.4 + index * 0.1,
              }}
            >
              <span>{area}</span>
              <span className="text-zinc-400">{90 - index * 15}% match</span>
            </motion.div>
          ))}
        </motion.div>
      </motion.div>
    </div>
  );
}
