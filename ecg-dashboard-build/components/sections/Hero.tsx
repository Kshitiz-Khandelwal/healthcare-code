"use client";

import { Activity, Download, FileText, ShieldCheck } from "lucide-react";
import { motion } from "framer-motion";
import AnimatedCounter from "../AnimatedCounter";
import { heroMetrics, projectMeta } from "@/lib/data";

export default function Hero() {
  return (
    <section
      id="hero"
      className="min-h-[92vh] bg-[radial-gradient(circle_at_20%_20%,rgba(20,184,166,0.18),transparent_34%),linear-gradient(135deg,#020617_0%,#0f172a_48%,#111827_100%)] pt-20 pb-14"
    >
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
          className="grid min-h-[78vh] grid-cols-1 items-center gap-10 lg:grid-cols-[1.05fr_0.95fr]"
        >
          <div>
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-teal-400/30 bg-teal-400/10 px-4 py-2 text-sm font-semibold text-teal-200">
              <ShieldCheck size={17} />
              {projectMeta.subtitle}
            </div>

            <h1 className="max-w-4xl text-4xl font-bold leading-tight tracking-tight text-white md:text-6xl">
              {projectMeta.title}
            </h1>

            <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-300 md:text-xl">
              A presentation-ready website and technical report for automated
              12-lead ECG analysis using EfficientNet-B4 embeddings and a
              LightGBM classification pipeline.
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              <a
                href="#summary"
                className="inline-flex items-center gap-2 rounded-md bg-teal-500 px-5 py-3 text-sm font-bold text-slate-950 transition hover:bg-teal-400"
              >
                <FileText size={18} />
                View Report
              </a>
              <a
                href="#performance"
                className="inline-flex items-center gap-2 rounded-md border border-white/20 bg-white/5 px-5 py-3 text-sm font-bold text-white transition hover:bg-white/10"
              >
                <Activity size={18} />
                See Metrics
              </a>
              <button
                type="button"
                onClick={() => window.print()}
                className="inline-flex items-center gap-2 rounded-md border border-white/20 bg-white/5 px-5 py-3 text-sm font-bold text-white transition hover:bg-white/10"
              >
                <Download size={18} />
                Print / Save PDF
              </button>
            </div>

            <div className="mt-8 grid max-w-3xl grid-cols-2 gap-3 md:grid-cols-4">
              {heroMetrics.map((stat) => (
                <div
                  key={stat.label}
                  className="rounded-lg border border-white/10 bg-white/[0.06] p-4 backdrop-blur"
                >
                  <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
                    {stat.label}
                  </p>
                  <p className="text-2xl font-bold text-teal-300 md:text-3xl">
                    <AnimatedCounter
                      from={0}
                      to={stat.value}
                      duration={2.2}
                      decimals={stat.value >= 100 ? 0 : 1}
                      suffix={stat.suffix}
                    />
                  </p>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-lg border border-white/10 bg-white/[0.06] p-6 shadow-2xl backdrop-blur">
            <div className="mb-5 flex items-center justify-between border-b border-white/10 pb-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                  Report Card
                </p>
                <h2 className="text-xl font-bold text-white">{projectMeta.author}</h2>
              </div>
              <Activity className="text-teal-300" size={28} />
            </div>
            <dl className="space-y-4 text-sm">
              <div>
                <dt className="text-slate-400">Model</dt>
                <dd className="mt-1 font-medium text-white">{projectMeta.model}</dd>
              </div>
              <div>
                <dt className="text-slate-400">Dataset</dt>
                <dd className="mt-1 font-medium text-white">{projectMeta.dataset}</dd>
              </div>
              <div>
                <dt className="text-slate-400">Validation Protocol</dt>
                <dd className="mt-1 font-medium text-white">{projectMeta.split}</dd>
              </div>
              <div>
                <dt className="text-slate-400">Main Outcome</dt>
                <dd className="mt-1 font-medium text-teal-200">
                  92.0% accuracy with 95.6% arrhythmia recall
                </dd>
              </div>
            </dl>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
