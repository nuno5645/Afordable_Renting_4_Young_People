import React from "react";
import { MemoryRouter as Router } from "react-router-dom";
import { Layout } from "./components/Layout";
import { AnimatePresence } from "framer-motion";
export function App() {
  return (
    <Router>
      <AnimatePresence mode="wait">
        <Layout />
      </AnimatePresence>
    </Router>
  );
}
