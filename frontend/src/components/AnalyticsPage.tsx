import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  TrendingUp,
  Users,
  Home as HomeIcon,
  ArrowUp,
  ArrowDown,
  CheckCircle,
  XCircle,
  Clock,
  Loader2,
} from "lucide-react";
import api, { ScraperStatus as ApiScraperStatus } from "../services/api";

interface ScraperStatusProps {
  name: string;
  status: string;
  timestamp: string;
  houses_processed: number;
  houses_found: number;
}

const ScraperStatusCard = ({ status }: { status: ScraperStatusProps }) => {
  const getStatusIcon = () => {
    switch (status.status) {
      case 'running':
        return <div className="w-5 h-5 rounded-full border-2 border-yellow-500 border-t-transparent animate-spin" />;
      case 'completed':
        return <CheckCircle className="text-green-500" size={20} />;
      case 'error':
        return <XCircle className="text-red-500" size={20} />;
      case 'initialized':
        return <Clock className="text-blue-500" size={20} />;
      default:
        return <Clock className="text-zinc-500" size={20} />;
    }
  };

  // Format timestamp to relative time (e.g., "2 hours ago")
  const formatTimestamp = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffMins = Math.floor(diffMs / 60000);
      
      if (diffMins < 1) return 'Just now';
      if (diffMins < 60) return `${diffMins} min${diffMins > 1 ? 's' : ''} ago`;
      
      const diffHours = Math.floor(diffMins / 60);
      if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
      
      const diffDays = Math.floor(diffHours / 24);
      return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    } catch (e) {
      return timestamp;
    }
  };

  return (
    <motion.div
      className="bg-zinc-900/90 backdrop-blur-lg p-4 rounded-xl flex items-center justify-between"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: "spring", damping: 20 }}
    >
      <div className="flex items-center gap-3">
        {getStatusIcon()}
        <div>
          <h3 className="font-medium">{status.name}</h3>
          <p className="text-sm text-zinc-400">Last run: {formatTimestamp(status.timestamp)}</p>
        </div>
      </div>
      <div className="text-right">
        <p className="text-sm text-zinc-400">Items scraped</p>
        <p className="font-medium">{status.houses_processed}</p>
      </div>
    </motion.div>
  );
};

const StatCard = ({ icon: Icon, label, value, trend, trendValue }: any) => (
  <motion.div
    className="bg-zinc-900/90 backdrop-blur-lg p-4 rounded-2xl"
    initial={{
      opacity: 0,
      y: 10,
    }}
    animate={{
      opacity: 1,
      y: 0,
    }}
    transition={{
      type: "tween",
      duration: 0.2,
    }}
    style={{
      willChange: 'opacity, transform',
      backfaceVisibility: 'hidden',
      WebkitBackfaceVisibility: 'hidden',
    }}
  >
    <div className="flex justify-between items-start">
      <div className="p-2 bg-blue-500/10 rounded-xl">
        <Icon className="text-blue-500" size={20} />
      </div>
      <div
        className={`flex items-center ${trend === "up" ? "text-green-500" : "text-red-500"}`}
      >
        {trend === "up" ? <ArrowUp size={16} /> : <ArrowDown size={16} />}
        <span className="text-sm ml-1">{trendValue}%</span>
      </div>
    </div>
    <div className="mt-3">
      <h3 className="text-zinc-400 text-sm">{label}</h3>
      <p className="text-2xl font-bold mt-1">{value}</p>
    </div>
  </motion.div>
);

export function AnalyticsPage() {
  const [scraperStatuses, setScraperStatuses] = useState<ScraperStatusProps[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchScraperStatus = async () => {
      try {
        setLoading(true);
        const response = await api.getScraperStatus();
        
        // Convert the response object to an array
        const statusArray = Object.values(response).map(status => ({
          name: status.name,
          status: status.status,
          timestamp: status.timestamp,
          houses_processed: status.houses_processed,
          houses_found: status.houses_found
        }));
        
        setScraperStatuses(statusArray);
      } catch (error) {
        console.error('Error fetching scraper status:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchScraperStatus();
    
    // Set up polling every 10 seconds to update scraper status
    const intervalId = setInterval(fetchScraperStatus, 10000);
    
    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, []);

  return (
    <div className="min-h-screen bg-black">
      <header className="sticky top-0 z-10 bg-black/80 backdrop-blur-lg">
        <div className="p-4">
          <h1 className="text-xl font-semibold">Analytics</h1>
        </div>
      </header>
      <motion.div
        className="p-4 space-y-6"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
      >
        <motion.div
          className="bg-zinc-900/90 backdrop-blur-lg p-4 rounded-2xl"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ type: "spring", damping: 20 }}
        >
          <h2 className="text-lg font-semibold mb-4">Scraper Status</h2>
          <div className="space-y-3">
            {loading ? (
              <div className="flex justify-center py-4">
                <Loader2 className="animate-spin text-zinc-500" size={24} />
              </div>
            ) : scraperStatuses.length > 0 ? (
              scraperStatuses.map((status) => (
                <ScraperStatusCard key={status.name} status={status} />
              ))
            ) : (
              <p className="text-zinc-500 text-center py-4">No scraper data available</p>
            )}
          </div>
        </motion.div>

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
          className="bg-zinc-900/90 backdrop-blur-lg p-4 rounded-2xl"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2, type: "tween" }}
          style={{ willChange: 'opacity, transform' }}
        >
          <h2 className="text-lg font-semibold mb-4">Popular Areas</h2>
          {["Alfama", "Bairro Alto", "Chiado"].map((area, index) => (
            <div
              key={area}
              className="flex justify-between items-center py-3 border-b border-zinc-800 last:border-0"
            >
              <span>{area}</span>
              <span className="text-zinc-400">{90 - index * 15}% match</span>
            </div>
          ))}
        </motion.div>
      </motion.div>
    </div>
  );
}
