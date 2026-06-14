"use client";

import { Circle, CircleAlert, CircleCheck } from "lucide-react";
import { motion } from "framer-motion";
import { riskLogic } from "@/lib/data";

export default function RiskLogic() {
  const styleMap: Record<string, string> = {
    green: "bg-emerald-500/15 border-emerald-500/40 text-emerald-300",
    amber: "bg-amber-500/15 border-amber-500/40 text-amber-300",
    red: "bg-red-500/15 border-red-500/40 text-red-300",
  };

  const iconMap = {
    green: CircleCheck,
    amber: Circle,
    red: CircleAlert,
  };

  return (
    <section id="risk" className="report-section border-t border-slate-800 bg-slate-900 py-20 text-white">
      <div className="container mx-auto px-4">
        <div className="mb-12 max-w-3xl">
          <p className="report-kicker text-teal-300">Decision Support</p>
          <h2 className="mb-4 text-4xl font-bold">Risk Assessment Logic</h2>
          <p className="text-lg leading-8 text-slate-400">
            Prediction class, model confidence, and heart-rate thresholds are
            combined into a simple patient-level risk label.
          </p>
        </div>

        <div className="mx-auto grid max-w-5xl grid-cols-1 gap-6 md:grid-cols-3">
          {riskLogic.map((tier, idx) => {
            const Icon = iconMap[tier.color as keyof typeof iconMap];
            return (
              <motion.div
                key={tier.label}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: idx * 0.1 }}
                viewport={{ once: true }}
                className={`rounded-lg border p-6 backdrop-blur-sm ${styleMap[tier.color]}`}
              >
                <div className="mb-4 flex items-center gap-2">
                  <Icon size={21} />
                  <h3 className="text-lg font-bold">{tier.label}</h3>
                </div>

                <ul className="space-y-2.5">
                  {tier.rules.map((rule) => (
                    <li key={rule} className="flex items-start gap-2 text-sm opacity-95">
                      <span className="mt-1.5 h-1.5 w-1.5 flex-none rounded-full bg-current" />
                      {rule}
                    </li>
                  ))}
                </ul>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
