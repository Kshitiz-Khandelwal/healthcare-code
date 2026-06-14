"use client";

import { prototypeComparison } from "@/lib/data";
import { motion } from "framer-motion";

export default function Prototype() {
  return (
    <section id="comparison" className="report-section border-t border-slate-800 bg-slate-900 py-20 text-white">
      <div className="container mx-auto px-4">
        <div className="mb-12 max-w-3xl">
          <p className="report-kicker text-teal-300">Model Iteration</p>
          <h2 className="mb-4 text-4xl font-bold">Prototype to Production Evolution</h2>
          <p className="text-lg leading-8 text-slate-400">
            Performance upgrade from EfficientNet-B0 phase-one testing to the
            EfficientNet-B4 production experiment.
          </p>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="mx-auto max-w-4xl overflow-x-auto rounded-lg border border-white/10 bg-white/[0.06] p-6 backdrop-blur"
        >
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="py-3 text-left font-medium text-slate-400">Metric</th>
                <th className="py-3 text-center font-medium text-amber-300">Phase 1: B0</th>
                <th className="py-3 text-center font-medium text-emerald-300">Phase 2: B4</th>
                <th className="py-3 text-center font-medium text-slate-400">Improvement</th>
              </tr>
            </thead>
            <tbody>
              {prototypeComparison.map((row) => (
                <tr key={row.metric} className="border-b border-slate-800/70">
                  <td className="py-3 font-medium text-white">{row.metric}</td>
                  <td className="py-3 text-center font-mono text-amber-300">{row.b0}</td>
                  <td className="py-3 text-center font-mono font-semibold text-emerald-300">{row.b4}</td>
                  <td className="py-3 text-center">
                    <span className="inline-block rounded-full bg-emerald-500/20 px-2 py-0.5 text-xs font-semibold text-emerald-300">
                      {row.improvement}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </motion.div>
      </div>
    </section>
  );
}
