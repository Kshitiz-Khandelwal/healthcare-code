"use client";

import { motion } from "framer-motion";

interface StageCardProps {
  step: number;
  name: string;
  description: string;
  icon: string;
  isLast?: boolean;
}

export default function StageCard({
  step,
  name,
  description,
  icon,
  isLast,
}: StageCardProps) {
  return (
    <div className="flex flex-col items-center relative">
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        whileInView={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, delay: step * 0.1 }}
        viewport={{ once: true }}
        className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50 rounded-lg p-6 backdrop-blur-sm hover:border-blue-500/30 transition-colors w-full"
      >
        <div className="flex items-center gap-4">
          <div className="flex-shrink-0">
            <div className="flex items-center justify-center w-12 h-12 rounded-full bg-blue-500/20 border border-blue-500/50">
              <span className="text-xl">{icon}</span>
            </div>
          </div>
          <div className="flex-1">
            <div className="flex items-baseline gap-2">
              <span className="text-sm font-semibold text-blue-400">
                Step {step}
              </span>
              <h3 className="text-lg font-semibold text-white">{name}</h3>
            </div>
            <p className="text-slate-400 text-sm mt-1">{description}</p>
          </div>
        </div>
      </motion.div>

      {!isLast && (
        <div className="w-0.5 h-8 bg-gradient-to-b from-blue-500 to-transparent mt-2" />
      )}
    </div>
  );
}
