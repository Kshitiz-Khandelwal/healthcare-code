"use client";

import { pipelineStages } from "@/lib/data";
import { motion } from "framer-motion";

export default function Pipeline() {
  return (
    <section id="pipeline" className="py-20 bg-slate-950 border-t border-slate-800">
      <div className="container mx-auto px-4">
        <div className="max-w-3xl mb-16">
          <h2 className="text-4xl font-bold text-white mb-4">
            Diagnostic Pipeline
          </h2>
          <p className="text-slate-400 text-lg">
            Six-stage processing pipeline transforms raw 12-lead ECG recordings
            into clinically actionable predictions with risk scores.
          </p>
        </div>

        <div className="max-w-3xl mx-auto">
          {pipelineStages.map((stage, idx) => (
            <motion.div
              key={stage.step}
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: idx * 0.08 }}
              viewport={{ once: true }}
              className="relative pl-12 pb-8 last:pb-0"
            >
              {/* Connector line */}
              {idx < pipelineStages.length - 1 && (
                <div className="absolute left-[18px] top-10 w-0.5 h-full bg-gradient-to-b from-indigo-500/40 to-indigo-500/10" />
              )}

              {/* Step circle */}
              <div className="absolute left-0 top-0 w-10 h-10 rounded-full bg-indigo-500/20 border-2 border-indigo-500/50 flex items-center justify-center">
                <span className="text-lg">{stage.icon}</span>
              </div>

              {/* Content */}
              <div className="bg-white/5 border border-white/10 rounded-xl p-5 backdrop-blur-xl hover:border-indigo-500/30 transition-all">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-indigo-400 text-xs font-mono font-bold">
                    STEP {stage.step}
                  </span>
                  <h3 className="text-white font-semibold">{stage.name}</h3>
                </div>
                <p className="text-slate-400 text-sm leading-relaxed">
                  {stage.description}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
