"use client";

import { patientPredictions } from "@/lib/data";
import { motion } from "framer-motion";

export default function Predictions() {
  const riskColors: Record<string, string> = {
    HIGH: "bg-red-500/20 text-red-400 border-red-500/40",
    MEDIUM: "bg-amber-500/20 text-amber-400 border-amber-500/40",
    LOW: "bg-emerald-500/20 text-emerald-400 border-emerald-500/40",
  };

  const predColors: Record<string, string> = {
    Arrhythmia: "text-red-400",
    Normal: "text-emerald-400",
    "Other / Unknown": "text-blue-400",
  };

  const avgTime = (
    patientPredictions.reduce((s, p) => s + p.totalSeconds, 0) / patientPredictions.length
  ).toFixed(3);

  return (
    <section id="predictions" className="py-20 bg-slate-950 border-t border-slate-800">
      <div className="container mx-auto px-4">
        <div className="max-w-3xl mb-16">
          <h2 className="text-4xl font-bold text-white mb-4">
            Live Prediction Results
          </h2>
          <p className="text-slate-400 text-lg">
            Real patient predictions from the production EfficientNet-B4 pipeline.
            All data is from actual PhysioNet ECG recordings.
          </p>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="bg-white/5 border border-white/10 rounded-xl p-6 backdrop-blur-xl overflow-x-auto"
        >
          <table className="w-full text-sm min-w-[900px]">
            <thead>
              <tr className="border-b border-slate-700">
                {["Patient", "Prediction", "Confidence", "Risk", "HR (BPM)", "HRV (ms)", "SDNN", "RMSSD", "Age", "Sex", "Time (s)"].map((h) => (
                  <th key={h} className="text-left py-3 px-2 text-slate-400 font-medium text-xs uppercase tracking-wider">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {patientPredictions.map((p, i) => {
                const hrWarning = p.heartRate < 60 || p.heartRate > 100;
                return (
                  <tr key={i} className="border-b border-slate-800/50 hover:bg-white/5 transition-colors">
                    <td className="py-3 px-2 text-white font-mono font-semibold">{p.id}</td>
                    <td className={`py-3 px-2 font-semibold ${predColors[p.prediction] || "text-white"}`}>
                      {p.prediction}
                    </td>
                    <td className="py-3 px-2 text-slate-200 font-mono">{p.confidence}%</td>
                    <td className="py-3 px-2">
                      <span className={`inline-block px-2.5 py-1 rounded-full text-xs font-bold border ${riskColors[p.risk]}`}>
                        {p.risk}
                      </span>
                    </td>
                    <td className="py-3 px-2 font-mono">
                      <span className={hrWarning ? "text-amber-400" : "text-slate-200"}>
                        {p.heartRate}
                      </span>
                      {hrWarning && <span className="ml-1 text-amber-400">⚠</span>}
                    </td>
                    <td className="py-3 px-2 text-slate-300 font-mono">{p.hrv.toFixed(1)}</td>
                    <td className="py-3 px-2 text-slate-300 font-mono">{p.sdnn.toFixed(1)}</td>
                    <td className="py-3 px-2 text-slate-300 font-mono">{p.rmssd.toFixed(1)}</td>
                    <td className="py-3 px-2 text-slate-300">{p.age}</td>
                    <td className="py-3 px-2 text-slate-300">{p.sex}</td>
                    <td className="py-3 px-2 text-slate-500 font-mono text-xs">{p.totalSeconds.toFixed(3)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>

          {/* Footer badge */}
          <div className="mt-4 flex items-center gap-4 text-xs text-slate-400">
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20">
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-400" />
              Avg inference: ~{avgTime}s per patient
            </span>
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/20">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
              ⚠ = Heart rate outside 60–100 BPM range
            </span>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
