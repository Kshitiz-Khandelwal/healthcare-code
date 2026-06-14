"use client";

import { CheckCircle2, TriangleAlert } from "lucide-react";
import { motion } from "framer-motion";

export default function Conclusion() {
  return (
    <section id="conclusion" className="report-section bg-slate-50 py-16 text-slate-950">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <motion.div
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.45 }}
            viewport={{ once: true }}
            className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm"
          >
            <p className="report-kicker">Conclusion</p>
            <h2 className="mb-4 text-3xl font-bold tracking-tight">
              The model is a strong ECG screening prototype with clear evidence.
            </h2>
            <p className="text-base leading-7 text-slate-700">
              The EfficientNet-B4 pipeline produced the best overall balance of
              accuracy, macro-F1, and AUC, while keeping arrhythmia recall high.
              The project demonstrates a complete workflow from raw ECG signal
              processing to model evaluation and patient-level risk reporting.
            </p>
            <p className="mt-4 text-base leading-7 text-slate-700">
              For academic demonstration, the system is ready to present as both
              a website and a report-style dashboard. For real clinical use, it
              would still require external validation, calibration testing, and
              review by medical professionals.
            </p>
          </motion.div>

          <motion.aside
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.45, delay: 0.1 }}
            viewport={{ once: true }}
            className="rounded-lg border border-amber-200 bg-amber-50 p-6"
          >
            <div className="mb-4 flex items-center gap-2 text-amber-800">
              <TriangleAlert size={20} />
              <h3 className="font-bold">Important Scope Note</h3>
            </div>
            <p className="text-sm leading-6 text-amber-900">
              This is a machine-learning project report and decision-support
              prototype. It should not be presented as a certified medical
              device or replacement for cardiologist diagnosis.
            </p>
            <div className="mt-5 flex items-start gap-2 rounded-md bg-white/70 p-3 text-sm text-slate-700">
              <CheckCircle2 className="mt-0.5 flex-none text-teal-700" size={18} />
              <p>
                Best presentation angle: emphasize engineering pipeline,
                evaluation evidence, and responsible clinical limitations.
              </p>
            </div>
          </motion.aside>
        </div>
      </div>
    </section>
  );
}
