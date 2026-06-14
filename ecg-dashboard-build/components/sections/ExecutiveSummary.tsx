"use client";

import { Activity, ClipboardCheck, FileText, ShieldCheck } from "lucide-react";
import { motion } from "framer-motion";
import { executiveSummary, keyFindings, projectMeta } from "@/lib/data";

const icons = [FileText, Activity, ClipboardCheck, ShieldCheck];

export default function ExecutiveSummary() {
  return (
    <section id="summary" className="report-section bg-slate-50 py-16 text-slate-950">
      <div className="container mx-auto px-4">
        <div className="mb-10 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <p className="report-kicker">Executive Summary</p>
            <h2 className="text-3xl font-bold tracking-tight md:text-4xl">
              A complete project report for ECG classification.
            </h2>
            <p className="mt-3 text-base leading-7 text-slate-600">
              This page is structured like a presentation-ready technical report:
              objective, methodology, model evidence, patient predictions, dataset
              mapping, limitations, and final conclusion.
            </p>
          </div>
          <div className="rounded-lg border border-slate-200 bg-white p-4 text-sm shadow-sm">
            <p className="font-semibold text-slate-900">{projectMeta.author}</p>
            <p className="text-slate-500">{projectMeta.dataset}</p>
            <p className="text-slate-500">{projectMeta.generated}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          {executiveSummary.map((item, index) => {
            const Icon = icons[index] ?? FileText;
            return (
              <motion.article
                key={item.label}
                initial={{ opacity: 0, y: 14 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: index * 0.05 }}
                viewport={{ once: true }}
                className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
              >
                <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-teal-50 text-teal-700">
                  <Icon size={20} strokeWidth={2} />
                </div>
                <h3 className="mb-2 text-sm font-bold uppercase tracking-wide text-slate-500">
                  {item.label}
                </h3>
                <p className="text-sm leading-6 text-slate-700">{item.value}</p>
              </motion.article>
            );
          })}
        </div>

        <div className="mt-8 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="mb-4 text-lg font-bold text-slate-950">Key Findings</h3>
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
            {keyFindings.map((finding) => (
              <div key={finding} className="flex gap-3 rounded-md bg-slate-50 p-3">
                <span className="mt-2 h-2 w-2 flex-none rounded-full bg-teal-600" />
                <p className="text-sm leading-6 text-slate-700">{finding}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
