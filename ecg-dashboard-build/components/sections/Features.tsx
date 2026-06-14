"use client";

import { BrainCircuit, Calculator } from "lucide-react";
import { motion } from "framer-motion";
import { handcraftedFeatures, deepFeatureSteps } from "@/lib/data";

export default function Features() {
  return (
    <section id="features" className="report-section bg-slate-900 py-20 text-white">
      <div className="container mx-auto px-4">
        <div className="mb-12 max-w-3xl">
          <p className="report-kicker text-teal-300">Methodology</p>
          <h2 className="mb-4 text-4xl font-bold">Dual Feature Extraction</h2>
          <p className="text-lg leading-8 text-slate-400">
            The pipeline compares clinical handcrafted features with deep CNN
            embeddings extracted from ECG scalogram images.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="rounded-lg border border-white/10 bg-white/[0.06] p-6 backdrop-blur"
          >
            <div className="mb-6 flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-teal-500/15 text-teal-300">
                <Calculator size={22} />
              </div>
              <div>
                <h3 className="text-xl font-semibold">Handcrafted Features</h3>
                <p className="font-mono text-sm text-teal-300">
                  17 dimensions | Lead II | scipy.signal
                </p>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="py-2 text-left font-medium text-slate-400">#</th>
                    <th className="py-2 text-left font-medium text-slate-400">Feature</th>
                    <th className="py-2 text-left font-medium text-slate-400">Type</th>
                    <th className="py-2 text-left font-medium text-slate-400">Description</th>
                  </tr>
                </thead>
                <tbody>
                  {handcraftedFeatures.map((f, i) => (
                    <tr key={f.name} className="border-b border-slate-800/70">
                      <td className="py-2 font-mono text-xs text-slate-500">{i + 1}</td>
                      <td className="py-2 font-mono text-xs text-indigo-300">{f.name}</td>
                      <td className="py-2">
                        <span
                          className={`rounded-full px-2 py-0.5 text-xs ${
                            f.category === "HRV"
                              ? "bg-amber-500/20 text-amber-300"
                              : "bg-blue-500/20 text-blue-300"
                          }`}
                        >
                          {f.category}
                        </span>
                      </td>
                      <td className="py-2 text-xs text-slate-400">{f.description}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="rounded-lg border border-white/10 bg-white/[0.06] p-6 backdrop-blur"
          >
            <div className="mb-6 flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-indigo-500/15 text-indigo-300">
                <BrainCircuit size={22} />
              </div>
              <div>
                <h3 className="text-xl font-semibold">Deep CNN Features</h3>
                <p className="font-mono text-sm text-indigo-300">
                  1792 dimensions | EfficientNet-B4 | transfer learning
                </p>
              </div>
            </div>

            <div className="space-y-6">
              {deepFeatureSteps.map((step, idx) => (
                <div key={step.step} className="relative pl-8">
                  <div className="absolute left-0 top-0 flex h-6 w-6 items-center justify-center rounded-full border border-indigo-400/50 bg-indigo-500/25">
                    <span className="text-xs font-bold text-indigo-200">{idx + 1}</span>
                  </div>
                  {idx < deepFeatureSteps.length - 1 && (
                    <div className="absolute left-[11px] top-6 h-full w-0.5 bg-indigo-500/20" />
                  )}
                  <h4 className="mb-2 font-semibold text-white">{step.step}</h4>
                  <p className="text-sm leading-7 text-slate-400">{step.description}</p>
                </div>
              ))}
            </div>

            <div className="mt-8 rounded-lg border border-teal-500/20 bg-teal-500/10 p-4">
              <p className="text-sm leading-6 text-slate-300">
                <span className="font-semibold text-teal-300">Feature fusion: </span>
                17 handcrafted + 1792 deep + 2 demographics ={" "}
                <span className="font-bold text-white">1,811 total features</span>
                {" -> StandardScaler -> PCA (30 components) -> LightGBM."}
              </p>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
