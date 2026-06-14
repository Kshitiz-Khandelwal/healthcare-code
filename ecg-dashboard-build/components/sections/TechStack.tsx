"use client";

import { techStack } from "@/lib/data";
import { motion } from "framer-motion";

export default function TechStack() {
  return (
    <section id="tech" className="py-20 bg-slate-950 border-t border-slate-800">
      <div className="container mx-auto px-4">
        <div className="max-w-3xl mb-16">
          <h2 className="text-4xl font-bold text-white mb-4">Technology Stack</h2>
          <p className="text-slate-400 text-lg">
            The tools and frameworks powering the ECG classification pipeline.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 max-w-6xl mx-auto">
          {techStack.map((item, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 15 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: idx * 0.05 }}
              viewport={{ once: true }}
              className="bg-white/5 border border-white/10 rounded-xl p-5 backdrop-blur-xl hover:border-indigo-500/30 transition-all hover:bg-white/[0.07]"
            >
              <p className="text-indigo-400 text-xs font-semibold uppercase tracking-wider mb-2">
                {item.category}
              </p>
              <p className="text-white text-sm font-medium">{item.tech}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
