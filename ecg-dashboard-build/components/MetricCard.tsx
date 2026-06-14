"use client";

import { motion } from "framer-motion";

interface MetricCardProps {
  label: string;
  value: string | number;
  unit?: string;
  icon?: string;
}

export default function MetricCard({
  label,
  value,
  unit = "",
  icon,
}: MetricCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      viewport={{ once: true }}
      className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50 rounded-lg p-6 backdrop-blur-sm hover:border-green-500/30 transition-colors"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-slate-400 text-sm font-medium">{label}</p>
          <div className="mt-2 flex items-baseline gap-1">
            <span className="text-3xl font-bold text-green-400">{value}</span>
            {unit && <span className="text-slate-400">{unit}</span>}
          </div>
        </div>
        {icon && <span className="text-2xl">{icon}</span>}
      </div>
    </motion.div>
  );
}
