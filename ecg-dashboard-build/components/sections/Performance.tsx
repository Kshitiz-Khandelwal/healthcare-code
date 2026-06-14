"use client";

import { confusionMatrix, perClassMetrics, strategyChartData } from "@/lib/data";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { motion } from "framer-motion";
import AnimatedCounter from "../AnimatedCounter";

export default function Performance() {
  const topMetrics = [
    { label: "Test Accuracy", value: 92.0, color: "text-emerald-400" },
    { label: "Macro-F1", value: 89.5, color: "text-indigo-400" },
    { label: "Weighted-F1", value: 91.8, color: "text-purple-400" },
    { label: "AUC (weighted)", value: 97.1, color: "text-amber-400" },
  ];

  // Confusion matrix cell color based on value
  const getCellColor = (row: number, col: number, value: number) => {
    if (row === col) {
      // Diagonal = correct
      const intensity = Math.min(value / 420, 1);
      return `rgba(34, 197, 94, ${0.15 + intensity * 0.45})`;
    }
    // Off-diagonal = errors
    if (value === 0) return "rgba(255,255,255,0.02)";
    const intensity = Math.min(value / 40, 1);
    return `rgba(239, 68, 68, ${0.05 + intensity * 0.35})`;
  };

  return (
    <section id="performance" className="py-20 bg-slate-950 border-t border-slate-800">
      <div className="container mx-auto px-4">
        <div className="max-w-3xl mb-16">
          <h2 className="text-4xl font-bold text-white mb-4">
            Model Performance
          </h2>
          <p className="text-slate-400 text-lg">
            Production model (EfficientNet-B4 backbone) evaluated on 1000 records
            with stratified 80/20 split and 3-fold cross-validation.
          </p>
        </div>

        {/* Top metric cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
          {topMetrics.map((m, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: i * 0.1 }}
              viewport={{ once: true }}
              className="bg-white/5 border border-white/10 rounded-xl p-5 backdrop-blur-xl text-center"
            >
              <p className="text-slate-400 text-xs uppercase tracking-wider mb-2">{m.label}</p>
              <p className={`text-3xl font-bold ${m.color}`}>
                <AnimatedCounter from={0} to={m.value} duration={2} decimals={1} suffix="%" />
              </p>
            </motion.div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          {/* Confusion Matrix */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="bg-white/5 border border-white/10 rounded-xl p-6 backdrop-blur-xl"
          >
            <h3 className="text-xl font-semibold text-white mb-2">Confusion Matrix</h3>
            <p className="text-slate-400 text-sm mb-6">800 validation samples · Rows = Actual · Cols = Predicted</p>

            {/* Matrix grid */}
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr>
                    <th className="p-2 text-slate-500 text-xs font-medium text-right">Actual ↓ / Predicted →</th>
                    {confusionMatrix.labels.map((l) => (
                      <th key={l} className="p-2 text-slate-300 text-xs font-semibold text-center">{l}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {confusionMatrix.matrix.map((row, ri) => (
                    <tr key={ri}>
                      <td className="p-2 text-slate-300 text-xs font-semibold text-right pr-4">
                        {confusionMatrix.labels[ri]}
                        <span className="text-slate-500 ml-1">(n={confusionMatrix.support[ri]})</span>
                      </td>
                      {row.map((val, ci) => (
                        <td key={ci} className="p-1">
                          <div
                            className="rounded-lg p-3 text-center font-mono transition-all hover:scale-105"
                            style={{ backgroundColor: getCellColor(ri, ci, val) }}
                          >
                            <span className={`text-lg font-bold ${ri === ci ? "text-emerald-300" : val > 0 ? "text-red-300" : "text-slate-600"}`}>
                              {val}
                            </span>
                            <br />
                            <span className="text-[10px] text-slate-400">
                              {((val / confusionMatrix.support[ri]) * 100).toFixed(1)}%
                            </span>
                          </div>
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>

          {/* Per-Class Metrics Table */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            viewport={{ once: true }}
            className="bg-white/5 border border-white/10 rounded-xl p-6 backdrop-blur-xl"
          >
            <h3 className="text-xl font-semibold text-white mb-2">Classification Report</h3>
            <p className="text-slate-400 text-sm mb-6">Per-class precision, recall, and F1-score (200-sample test set)</p>

            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left py-3 text-slate-400 font-medium">Class</th>
                  <th className="text-center py-3 text-slate-400 font-medium">Precision</th>
                  <th className="text-center py-3 text-slate-400 font-medium">Recall</th>
                  <th className="text-center py-3 text-slate-400 font-medium">F1-Score</th>
                  <th className="text-center py-3 text-slate-400 font-medium">Support</th>
                </tr>
              </thead>
              <tbody>
                {perClassMetrics.map((row, i) => {
                  const isLast = i === perClassMetrics.length - 1;
                  const classColors: Record<string, string> = {
                    "Normal": "text-emerald-400",
                    "Arrhythmia": "text-red-400",
                    "Other / Unknown": "text-blue-400",
                    "Weighted Avg": "text-white",
                  };
                  return (
                    <tr key={i} className={`${isLast ? "border-t-2 border-slate-600 font-semibold" : "border-b border-slate-800/50"}`}>
                      <td className={`py-3 ${classColors[row.class] || "text-white"}`}>
                        {row.class}
                      </td>
                      <td className="py-3 text-center text-slate-200">{row.precision}%</td>
                      <td className="py-3 text-center text-slate-200">{row.recall}%</td>
                      <td className="py-3 text-center text-slate-200">{row.f1}%</td>
                      <td className="py-3 text-center text-slate-500">{row.support}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>

            {/* Key insight */}
            <div className="mt-6 p-3 rounded-lg bg-red-500/10 border border-red-500/20">
              <p className="text-xs text-slate-300">
                <span className="text-red-400 font-semibold">Critical: </span>
                95.6% Arrhythmia recall means the model almost never misses a dangerous arrhythmia.
                False negatives in cardiac diagnosis can be life-threatening.
              </p>
            </div>
          </motion.div>
        </div>

        {/* Strategy Comparison Bar Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="bg-white/5 border border-white/10 rounded-xl p-6 backdrop-blur-xl"
        >
          <h3 className="text-xl font-semibold text-white mb-2">Feature Strategy Comparison</h3>
          <p className="text-slate-400 text-sm mb-6">
            Three strategies were benchmarked. EfficientNet-only was selected for best test Macro-F1 and AUC.
          </p>

          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={strategyChartData} barGap={4}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="name" stroke="#94a3b8" tick={{ fontSize: 11 }} />
              <YAxis stroke="#94a3b8" domain={[85, 100]} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1e293b",
                  border: "1px solid #334155",
                  borderRadius: "0.5rem",
                }}
                labelStyle={{ color: "#e2e8f0" }}
              />
              <Legend />
              <Bar dataKey="accuracy" name="Test Accuracy %" fill="#22c55e" radius={[6, 6, 0, 0]} />
              <Bar dataKey="macroF1" name="Macro-F1 %" fill="#8b5cf6" radius={[6, 6, 0, 0]} />
              <Bar dataKey="auc" name="AUC %" fill="#f59e0b" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      </div>
    </section>
  );
}
