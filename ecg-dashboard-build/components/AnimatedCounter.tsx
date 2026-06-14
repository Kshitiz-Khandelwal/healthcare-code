"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";

interface AnimatedCounterProps {
  from: number;
  to: number;
  duration?: number;
  decimals?: number;
  suffix?: string;
}

export default function AnimatedCounter({
  from,
  to,
  duration = 2,
  decimals = 1,
  suffix = "",
}: AnimatedCounterProps) {
  const [count, setCount] = useState(from);

  useEffect(() => {
    const start = Date.now();
    const range = to - from;

    const timer = setInterval(() => {
      const elapsed = Date.now() - start;
      const progress = Math.min(elapsed / (duration * 1000), 1);
      const current = from + range * progress;
      setCount(parseFloat(current.toFixed(decimals)));

      if (progress === 1) {
        clearInterval(timer);
      }
    }, 16);

    return () => clearInterval(timer);
  }, [from, to, duration, decimals]);

  return (
    <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      {count}
      {suffix}
    </motion.span>
  );
}
