import React from "react";
import { motion } from "framer-motion";
import { Search as SearchIcon } from "lucide-react";
export function SearchPage() {
  return (
    <div className="min-h-screen bg-black">
      <header className="sticky top-0 z-10 bg-black/80 backdrop-blur-lg">
        <div className="p-4">
          <h1 className="text-xl font-semibold mb-4">Search</h1>
          <div className="relative">
            <input
              type="text"
              placeholder="Search properties..."
              className="w-full bg-zinc-900 rounded-lg py-3 pl-4 pr-10 text-white"
            />
            <SearchIcon
              className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-400"
              size={20}
            />
          </div>
        </div>
      </header>
      <div className="p-4">
        <p className="text-zinc-400 text-center mt-8">
          Enter a location or property type to start searching
        </p>
      </div>
    </div>
  );
}
