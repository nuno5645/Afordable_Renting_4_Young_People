import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const SplashScreen: React.FC = () => {
  const [isVisible, setIsVisible] = useState(true);
  const [progress, setProgress] = useState(0);
  const [touchStart, setTouchStart] = useState(0);
  const [touchEnd, setTouchEnd] = useState(0);
  const [touchDelta, setTouchDelta] = useState(0);

  useEffect(() => {
    // Reduced animation duration for better performance
    const duration = 1500;
    const interval = 20; // Reduced update frequency
    const steps = duration / interval;
    let currentStep = 0;

    const timer = setInterval(() => {
      currentStep++;
      // Use requestAnimationFrame for smoother progress updates
      requestAnimationFrame(() => {
        setProgress((currentStep / steps) * 100);
      });
      
      if (currentStep >= steps) {
        clearInterval(timer);
        // Optional vibration feedback, but only if available
        try {
          if (navigator.vibrate) {
            navigator.vibrate(50);
          }
        } catch (e) {
          // Ignore vibration errors
        }
        // Faster transition out
        setTimeout(() => setIsVisible(false), 100);
      }
    }, interval);

    return () => clearInterval(timer);
  }, []);

  const handleTouchStart = (e: React.TouchEvent) => {
    setTouchStart(e.targetTouches[0].clientY);
    setTouchEnd(e.targetTouches[0].clientY);
    setTouchDelta(0);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    // More conservative touch movement to prevent glitches
    const currentTouch = e.targetTouches[0].clientY;
    setTouchEnd(currentTouch);
    setTouchDelta((touchStart - currentTouch) * 0.2); // Reduced sensitivity
  };

  const handleTouchEnd = () => {
    if (touchStart - touchEnd > 100) {
      // Reduced threshold for swipe detection
      setIsVisible(false);
      try {
        if (navigator.vibrate) {
          navigator.vibrate(50);
        }
      } catch (e) {
        // Ignore vibration errors
      }
    }
    setTouchStart(0);
    setTouchEnd(0);
    setTouchDelta(0);
  };

  // Simplified animation variants
  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1, // Faster staggering
      },
    },
  };

  const item = {
    hidden: { opacity: 0, y: 10 }, // Reduced movement
    show: { 
      opacity: 1, 
      y: 0,
      transition: {
        type: "tween", // Changed from spring to tween
        duration: 0.2, // Shorter duration
      }
    },
  };

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }} // Simpler transition
          className="fixed inset-0 flex items-center justify-center bg-black z-50 touch-none"
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd}
          style={{
            willChange: 'opacity',
            backfaceVisibility: 'hidden',
            WebkitBackfaceVisibility: 'hidden',
          }}
        >
          <motion.div
            variants={container}
            initial="hidden"
            animate="show"
            className="flex flex-col items-center space-y-6"
            style={{
              willChange: 'transform',
              transform: `translateY(${-touchDelta}px)`,
              backfaceVisibility: 'hidden',
              WebkitBackfaceVisibility: 'hidden',
            }}
          >
            <div className="flex flex-col items-center">
              <motion.span 
                variants={item}
                className="text-5xl font-light tracking-widest text-gray-300"
              >
                HOUSE
              </motion.span>
              <motion.span 
                variants={item}
                className="text-7xl font-bold tracking-tight text-white mt-[-0.5rem]"
              >
                FINDER
              </motion.span>
              <motion.p
                variants={item} 
                className="text-sm tracking-wider uppercase text-gray-500 mt-2"
              >
                Lisbon, Portugal
              </motion.p>
            </div>

            <motion.div 
              variants={item}
              className="flex flex-col items-center space-y-2"
            >
              <div className="w-48 h-[1px] bg-gray-800 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-white"
                  style={{ 
                    width: `${progress}%`,
                  }}
                />
              </div>
              
              <div className="h-6 overflow-hidden">
                {progress < 100 ? (
                  <p className="text-sm tracking-wider uppercase text-gray-500">
                    <span>Discovering dream homes</span>
                    <span className="inline-block">...</span>
                  </p>
                ) : (
                  <p className="text-sm tracking-wider uppercase text-gray-300">
                    Ready to explore
                  </p>
                )}
              </div>
            </motion.div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default SplashScreen; 