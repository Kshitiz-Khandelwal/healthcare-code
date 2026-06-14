"use client";

import { classDistribution, datasetStats, labelMapping } from "@/lib/data";
import {
  PieChart,
  Pie,
  Cell,
  Legend,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { motion } from "framer-motion";

export default function Dataset() {
  return (
    <section id="dataset" className="py-20 bg-gradient-to-b from-slate-950 to-slate-900 border-t border-slate-800">
      <div className="container mx-auto px-4">
        <div className="max-w-3xl mb-16">
          <h2 className="text-4xl font-bold text-white mb-4">Dataset &amp; Label Mapping</h2>
          <p className="text-slate-400 text-lg">
            1,000 records from the PhysioNet/CinC Challenge 2020 dataset.
            12-lead ECG recordings sampled at 500 Hz in WFDB format.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          {/* Donut Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="bg-white/5 border border-white/10 rounded-xl p-6 backdrop-blur-xl"
          >
            <h3 className="text-xl font-semibold text-white mb-6">
              Class Distribution
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={classDistribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={3}
                  dataKey="value"
                  label={({ name, percent }) =>
                    `${name} ${(percent * 100).toFixed(0)}%`
                  }
                  labelLine={{ stroke: "#64748b" }}
                >
                  {classDistribution.map((entry, index) => (
                    <Cell key={index} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#1e293b",
                    border: "1px solid #334155",
                    borderRadius: "0.5rem",
                  }}
                  labelStyle={{ color: "#e2e8f0" }}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </motion.div>

          {/* Stats Grid */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            viewport={{ once: true }}
            className="grid grid-cols-2 gap-4 content-start"
          >
            {datasetStats.map((stat, idx) => (
              <div
                key={idx}
                className="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-xl"
              >
                <p className="text-slate-400 text-xs uppercase tracking-wider mb-2">{stat.label}</p>
                <p className="text-xl font-bold text-white">{stat.value}</p>
              </div>
            ))}
          </motion.div>
        </div>

        {/* SNOMED Label Mapping Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          viewport={{ once: true }}
          className="bg-white/5 border border-white/10 rounded-xl p-6 backdrop-blur-xl max-w-4xl mx-auto"
        >
          <h3 className="text-xl font-semibold text-white mb-6">
            SNOMED-CT Label Mapping
          </h3>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left py-3 text-slate-400 font-medium">Class</th>
                <th className="text-left py-3 text-slate-400 font-medium">Label</th>
                <th className="text-left py-3 text-slate-400 font-medium">SNOMED-CT Codes</th>
                <th className="text-left py-3 text-slate-400 font-medium">Description</th>
              </tr>
            </thead>
            <tbody>
              {labelMapping.map((row, i) => {
                const classColors = ["text-emerald-400", "text-red-400", "text-blue-400"];
                return (
                  <tr key={i} className="border-b border-slate-800/50">
                    <td className="py-3 text-slate-300 font-mono">{row.classId}</td>
                    <td className={`py-3 font-semibold ${classColors[i]}`}>{row.label}</td>
                    <td className="py-3 text-slate-400 font-mono text-xs">{row.snomed}</td>
                    <td className="py-3 text-slate-400">{row.description}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </motion.div>
      </div>
    </section>
  );
}
