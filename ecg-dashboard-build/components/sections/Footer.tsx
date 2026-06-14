"use client";

import { motion } from "framer-motion";

export default function Footer() {
  return (
    <footer className="bg-slate-950 border-t border-slate-800 py-12">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8"
        >
          <div>
            <h4 className="font-semibold text-white mb-4">Project</h4>
            <ul className="space-y-2 text-slate-400 text-sm">
              <li>ECG Hybrid Classification System</li>
              <li>EfficientNet-B4 + LightGBM Pipeline</li>
              <li>PhysioNet/CinC Challenge 2020 Dataset</li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold text-white mb-4">Links</h4>
            <ul className="space-y-2 text-slate-400 text-sm">
              <li>
                <a
                  href="https://github.com/Kshitiz-Khandelwal/healthcare-code"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-white transition-colors"
                >
                  GitHub Repository
                </a>
              </li>
              <li>
                <a
                  href="https://physionet.org/content/challenge-2020/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-white transition-colors"
                >
                  PhysioNet Dataset
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold text-white mb-4">Technologies</h4>
            <ul className="space-y-2 text-slate-400 text-sm">
              <li>PyTorch · torchvision · LightGBM</li>
              <li>scikit-learn · SciPy · PyWavelets</li>
              <li>Next.js · Tailwind CSS · Recharts</li>
            </ul>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          viewport={{ once: true }}
          className="border-t border-slate-800 pt-8 text-center text-slate-400 text-sm"
        >
          <p>
            Built by <span className="text-white font-medium">Kshitiz Khandelwal</span> · 2026
          </p>
        </motion.div>
      </div>
    </footer>
  );
}
