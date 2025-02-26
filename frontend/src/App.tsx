import React from "react";
import { MemoryRouter as Router } from "react-router-dom";
import { Layout } from "./components/Layout";
import { AnimatePresence } from "framer-motion";
import SplashScreen from "./components/SplashScreen";

export function App() {
  return (
    <>
      <SplashScreen />
      <Router>
        <AnimatePresence mode="wait">
          <Layout />
        </AnimatePresence>
      </Router>
    </>
  );
}
