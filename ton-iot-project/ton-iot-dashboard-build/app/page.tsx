"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Shield,
  ShieldAlert,
  Database,
  BarChart3,
  Cpu,
  Layers,
  Terminal,
  ExternalLink,
  Activity,
  CheckCircle2,
  TrendingUp,
  Settings,
  HelpCircle,
  Play,
  ArrowRight,
  Info
} from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
  PieChart,
  Pie,
  Legend,
  AreaChart,
  Area
} from "recharts";
import {
  projectMeta,
  labelDistribution,
  attackTypeDistribution,
  binaryResults,
  multiclassResults,
  featureImportance,
  engineeredFeatures,
  attackDescriptions
} from "./data";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"overview" | "features" | "models" | "threats">("overview");
  const [selectedAttack, setSelectedAttack] = useState<string>("ddos");
  const [hoveredFeature, setHoveredFeature] = useState<string | null>(null);

  // Tab variants for smooth transitions
  const tabVariants = {
    hidden: { opacity: 0, y: 15 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.3 } },
    exit: { opacity: 0, y: -15, transition: { duration: 0.2 } }
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 font-sans antialiased selection:bg-emerald-500 selection:text-black">
      {/* BACKGROUND DECORATIVE ELEMENTS */}
      <div className="absolute top-0 left-0 w-full h-[500px] bg-gradient-to-b from-emerald-950/20 to-transparent pointer-events-none" />
      <div className="absolute top-40 right-10 w-96 h-96 bg-emerald-500/5 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute top-[600px] left-10 w-[500px] h-[500px] bg-indigo-500/5 rounded-full blur-[120px] pointer-events-none" />

      {/* HEADER SECTION */}
      <header className="sticky top-0 z-40 border-b border-zinc-900 bg-zinc-950/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 py-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-emerald-500/10 rounded-xl border border-emerald-500/30 text-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.1)]">
              <Shield className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                {projectMeta.title}
                <span className="px-2 py-0.5 text-[10px] font-mono tracking-normal bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 rounded-full">
                  Vercel Live
                </span>
              </h1>
              <p className="text-xs text-zinc-400 font-medium">
                {projectMeta.subtitle}
              </p>
            </div>
          </div>
          
          {/* NAVIGATION TABS */}
          <nav className="flex bg-zinc-900/60 p-1 border border-zinc-800 rounded-xl">
            {(["overview", "features", "models", "threats"] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`relative px-4 py-2 text-xs font-semibold rounded-lg transition-all capitalize ${
                  activeTab === tab ? "text-white" : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                {activeTab === tab && (
                  <motion.div
                    layoutId="activeTabIndicator"
                    className="absolute inset-0 bg-zinc-800 border border-zinc-700/50 rounded-lg shadow-sm"
                    transition={{ type: "spring", stiffness: 380, damping: 30 }}
                  />
                )}
                <span className="relative z-10">{tab}</span>
              </button>
            ))}
          </nav>
        </div>
      </header>

      {/* MAIN CONTAINER */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        
        {/* STATS OVERVIEW CARDS */}
        <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
          {[
            { title: "Total Observations", val: projectMeta.totalRows.toLocaleString(), desc: "Network flows analyzed", icon: Database, color: "text-emerald-400" },
            { title: "Avg Attack Rate", val: "76.3%", desc: "161,043 malicious flows", icon: ShieldAlert, color: "text-rose-400" },
            { title: "Engineered Features", val: projectMeta.totalFeatures.toString(), desc: "From 44 raw variables", icon: Layers, color: "text-indigo-400" },
            { title: "Best Model F1-Score", val: "99.93%", desc: "Random Forest (Binary)", icon: Cpu, color: "text-teal-400" }
          ].map((card, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="bg-zinc-900/55 border border-zinc-800/80 p-5 rounded-2xl flex items-center justify-between hover:border-zinc-700/50 transition-all hover:bg-zinc-900/80 group"
            >
              <div>
                <span className="text-[11px] font-semibold text-zinc-500 uppercase tracking-wider block mb-1">
                  {card.title}
                </span>
                <span className="text-2xl font-bold tracking-tight text-white block mb-0.5 group-hover:text-emerald-400 transition-colors">
                  {card.val}
                </span>
                <span className="text-xs text-zinc-400 font-medium">
                  {card.desc}
                </span>
              </div>
              <div className={`p-3 bg-zinc-800/60 rounded-xl border border-zinc-700/30 ${card.color}`}>
                <card.icon className="w-5 h-5" />
              </div>
            </motion.div>
          ))}
        </section>

        {/* ACTIVE TAB CONTENT */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial="hidden"
            animate="visible"
            exit="exit"
            variants={tabVariants}
          >
            {/* ── OVERVIEW TAB ────────────────────────────────────────────────── */}
            {activeTab === "overview" && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Column 1 & 2: Overview & Charts */}
                <div className="lg:col-span-2 space-y-6">
                  {/* Pipeline Context */}
                  <div className="bg-zinc-900/40 border border-zinc-900 p-6 rounded-2xl relative overflow-hidden">
                    <div className="absolute top-0 right-0 p-8 opacity-5">
                      <Shield className="w-40 h-40 text-emerald-400" />
                    </div>
                    <h2 className="text-lg font-bold text-white flex items-center gap-2 mb-3">
                      <Activity className="w-5 h-5 text-emerald-400" />
                      Cybersecurity Detection Pipeline
                    </h2>
                    <p className="text-sm text-zinc-400 leading-relaxed max-w-2xl mb-4">
                      This ML suite detects network intrusions in smart IoT environments. We leverage supervised models 
                      to automatically separate benign traffic from 9 distinct attack vectors (including DDoS, Ransomware, 
                      and SQL injection) with ultra-high precision, supporting real-time alerts.
                    </p>
                    <div className="flex flex-wrap gap-3">
                      <a
                        href={projectMeta.datasetUrl}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-2 text-xs font-semibold px-4 py-2 bg-zinc-800 hover:bg-zinc-700 border border-zinc-700/50 rounded-xl text-zinc-200 hover:text-white transition-all"
                      >
                        Dataset Source
                        <ExternalLink className="w-3.5 h-3.5" />
                      </a>
                      <button
                        onClick={() => setActiveTab("models")}
                        className="inline-flex items-center gap-2 text-xs font-semibold px-4 py-2 bg-emerald-500 hover:bg-emerald-400 rounded-xl text-black transition-all"
                      >
                        Explore ML Performance
                        <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>

                  {/* Distribution Charts */}
                  <div className="bg-zinc-900/40 border border-zinc-900 p-6 rounded-2xl">
                    <h3 className="text-sm font-bold uppercase tracking-wider text-zinc-400 mb-6 flex items-center gap-2">
                      <BarChart3 className="w-4.5 h-4.5 text-indigo-400" />
                      Data Audit & Class Balance
                    </h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                      {/* Binary Chart */}
                      <div className="bg-zinc-950/50 border border-zinc-900 p-4 rounded-xl flex flex-col items-center">
                        <span className="text-xs font-bold text-zinc-400 mb-4 block">
                          Binary Label Distribution
                        </span>
                        <div className="w-full h-56">
                          <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                              <Pie
                                data={labelDistribution}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={80}
                                paddingAngle={4}
                                dataKey="count"
                              >
                                {labelDistribution.map((entry, index) => (
                                  <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                              </Pie>
                              <Tooltip 
                                contentStyle={{ backgroundColor: "#18181b", borderColor: "#27272a", borderRadius: "8px" }}
                                itemStyle={{ color: "#fff" }}
                              />
                              <Legend verticalAlign="bottom" height={36} formatter={(value, entry: any) => (
                                <span className="text-xs text-zinc-400 font-semibold">{entry.payload.name} ({entry.payload.pct}%)</span>
                              )} />
                            </PieChart>
                          </ResponsiveContainer>
                        </div>
                      </div>

                      {/* Multi-class Chart */}
                      <div className="bg-zinc-950/50 border border-zinc-900 p-4 rounded-xl flex flex-col">
                        <span className="text-xs font-bold text-zinc-400 mb-4 block text-center">
                          Attack Type Distribution
                        </span>
                        <div className="w-full h-56">
                          <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={attackTypeDistribution} layout="vertical">
                              <XAxis type="number" hide />
                              <YAxis dataKey="name" type="category" width={80} stroke="#71717a" fontSize={10} tickLine={false} />
                              <Tooltip
                                contentStyle={{ backgroundColor: "#18181b", borderColor: "#27272a", borderRadius: "8px" }}
                                labelStyle={{ color: "#fff", fontWeight: "bold" }}
                              />
                              <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                                {attackTypeDistribution.map((entry, index) => (
                                  <Cell 
                                    key={`cell-${index}`} 
                                    fill={entry.name === "normal" ? "#10b981" : "#4f46e5"} 
                                    opacity={entry.name === "normal" ? 0.9 : 0.8 - (index * 0.04)}
                                  />
                                ))}
                              </Bar>
                            </BarChart>
                          </ResponsiveContainer>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Column 3: Sidebar Context */}
                <div className="space-y-6">
                  {/* System Integrity & Hash */}
                  <div className="bg-zinc-900/40 border border-zinc-900 p-6 rounded-2xl">
                    <h3 className="text-sm font-bold uppercase tracking-wider text-zinc-400 mb-4 flex items-center gap-2">
                      <CheckCircle2 className="w-4.5 h-4.5 text-emerald-400" />
                      Pipeline Provenance
                    </h3>
                    <div className="space-y-4">
                      <div className="p-3.5 bg-zinc-950/60 border border-zinc-800 rounded-xl font-mono text-[11px] leading-relaxed">
                        <div className="text-zinc-500 mb-1">FEATURE SIGNATURE HASH:</div>
                        <div className="text-zinc-300 select-all truncate">{projectMeta.featureHash}</div>
                      </div>
                      <div className="space-y-2 text-xs">
                        <div className="flex justify-between py-1.5 border-b border-zinc-800/50">
                          <span className="text-zinc-500">Seed Alignment</span>
                          <span className="text-zinc-300 font-semibold">{projectMeta.seed}</span>
                        </div>
                        <div className="flex justify-between py-1.5 border-b border-zinc-800/50">
                          <span className="text-zinc-500">Splitting Strategy</span>
                          <span className="text-zinc-300 font-semibold">80/20 Stratified</span>
                        </div>
                        <div className="flex justify-between py-1.5 border-b border-zinc-800/50">
                          <span className="text-zinc-500">Validation Mode</span>
                          <span className="text-zinc-300 font-semibold">5-Fold Stratified CV</span>
                        </div>
                        <div className="flex justify-between py-1.5">
                          <span className="text-zinc-500">Framework Preset</span>
                          <span className="text-emerald-400 font-semibold">Next.js App Router</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Architecture Flow Info */}
                  <div className="bg-zinc-900/40 border border-zinc-900 p-6 rounded-2xl">
                    <h3 className="text-sm font-bold uppercase tracking-wider text-zinc-400 mb-4 flex items-center gap-2">
                      <Settings className="w-4.5 h-4.5 text-indigo-400" />
                      Intrusion Dashboard Tech
                    </h3>
                    <p className="text-xs text-zinc-400 leading-relaxed mb-4">
                      Built with Next.js, React, TailwindCSS, and Framer Motion, running metrics sourced 
                      directly from Python/Scikit-learn/XGBoost pipelines saved to pickle binaries.
                    </p>
                    <div className="flex items-center gap-2 p-3 bg-zinc-800/20 rounded-xl border border-zinc-800/50">
                      <Terminal className="w-4 h-4 text-emerald-400" />
                      <code className="text-[10px] font-mono text-zinc-300">npm run build</code>
                      <span className="text-[10px] font-medium text-emerald-500 ml-auto flex items-center gap-1">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
                        SUCCESS
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* ── FEATURES TAB ────────────────────────────────────────────────── */}
            {activeTab === "features" && (
              <div className="space-y-6">
                {/* Feature Engineering Rationale */}
                <div className="bg-zinc-900/40 border border-zinc-900 p-6 rounded-2xl">
                  <div className="flex flex-col md:flex-row gap-6 items-start md:items-center justify-between mb-6">
                    <div>
                      <h2 className="text-lg font-bold text-white flex items-center gap-2">
                        <Layers className="w-5 h-5 text-indigo-400" />
                        Feature Engineering Rationale
                      </h2>
                      <p className="text-xs text-zinc-400 mt-1 max-w-2xl">
                        Intrusion detection models can easily overfit or fail if they learn specific lab IP addresses or high-cardinality strings. 
                        We clean, transform, and derive 33 robust variables that generalize well to other networks.
                      </p>
                    </div>
                    <span className="px-3 py-1.5 bg-zinc-950 border border-zinc-800 rounded-xl text-xs font-semibold text-zinc-300">
                      Variables Dropped: {projectMeta.rawFeatures - projectMeta.totalFeatures}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {engineeredFeatures.map((feat) => (
                      <div
                        key={feat.name}
                        onMouseEnter={() => setHoveredFeature(feat.name)}
                        onMouseLeave={() => setHoveredFeature(null)}
                        className={`p-4 border rounded-xl transition-all ${
                          hoveredFeature === feat.name
                            ? "bg-zinc-900/90 border-indigo-500/40 shadow-[0_0_10px_rgba(79,70,229,0.05)]"
                            : "bg-zinc-950/40 border-zinc-800/80"
                        }`}
                      >
                        <div className="flex items-center justify-between gap-2 mb-2">
                          <span className="text-xs font-mono font-bold text-white">{feat.name}</span>
                          <span className={`px-2 py-0.5 text-[9px] font-semibold rounded-md ${
                            feat.type === "Derived" 
                              ? "bg-emerald-500/10 border border-emerald-500/25 text-emerald-400"
                              : feat.type === "LabelEncoder"
                              ? "bg-indigo-500/10 border border-indigo-500/25 text-indigo-400"
                              : "bg-zinc-800 text-zinc-300"
                          }`}>
                            {feat.type}
                          </span>
                        </div>
                        <p className="text-[11px] text-zinc-400 leading-normal">{feat.rationale}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Feature Importance visual */}
                <div className="bg-zinc-900/40 border border-zinc-900 p-6 rounded-2xl">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-zinc-400 mb-6 flex items-center gap-2">
                    <TrendingUp className="w-4.5 h-4.5 text-indigo-400" />
                    Top Predictive Features (LightGBM Multi-class Importance)
                  </h3>
                  <div className="w-full h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={featureImportance} margin={{ bottom: 20 }}>
                        <XAxis dataKey="feature" stroke="#71717a" fontSize={9} interval={0} angle={-35} textAnchor="end" height={60} />
                        <YAxis stroke="#71717a" fontSize={10} label={{ value: "Feature Importance Score", angle: -95, position: "insideLeft", style: { fill: "#71717a", fontSize: 10, fontWeight: "bold" } }} />
                        <Tooltip
                          contentStyle={{ backgroundColor: "#18181b", borderColor: "#27272a", borderRadius: "8px" }}
                          labelStyle={{ color: "#fff", fontWeight: "bold" }}
                        />
                        <Bar dataKey="importance" fill="#6366f1" radius={[3, 3, 0, 0]}>
                          {featureImportance.map((entry, index) => (
                            <Cell key={`cell-${index}`} opacity={1 - (index * 0.03)} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            )}

            {/* ── MODELS TAB ───────────────────────────────────────────────────── */}
            {activeTab === "models" && (
              <div className="space-y-8">
                
                {/* 1. Binary Results */}
                <div className="bg-zinc-900/40 border border-zinc-900 p-6 rounded-2xl">
                  <div className="border-b border-zinc-800/60 pb-4 mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div>
                      <h2 className="text-base font-bold text-white flex items-center gap-2">
                        <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                        Binary Classification (Benign vs Attack)
                      </h2>
                      <p className="text-xs text-zinc-400 mt-0.5">
                        Detecting intrusion events. RandomForestClassifier achieves near-perfect Test F1 = 99.93% and ROC-AUC = 1.0000.
                      </p>
                    </div>
                    <span className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-xs font-bold text-emerald-400 self-start">
                      Best: {binaryResults.bestModel}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Performance Table */}
                    <div className="lg:col-span-2 overflow-x-auto">
                      <table className="w-full text-left border-collapse text-xs">
                        <thead>
                          <tr className="border-b border-zinc-800 text-zinc-400 font-bold">
                            <th className="py-3 px-2">Classifier Model</th>
                            <th className="py-3 px-2 text-right">CV Acc</th>
                            <th className="py-3 px-2 text-right">CV F1</th>
                            <th className="py-3 px-2 text-right">CV AUC</th>
                            <th className="py-3 px-2 text-right">Test Acc</th>
                            <th className="py-3 px-2 text-right">Test F1</th>
                            <th className="py-3 px-2 text-right">Test AUC</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-zinc-900">
                          {binaryResults.models.map((m) => (
                            <tr
                              key={m.name}
                              className={`hover:bg-zinc-900/30 transition-all ${
                                m.best ? "bg-emerald-500/5 text-white font-semibold" : "text-zinc-400"
                              }`}
                            >
                              <td className="py-3.5 px-2 font-medium flex items-center gap-2">
                                {m.name}
                                {m.best && (
                                  <span className="px-1.5 py-0.5 text-[8px] bg-emerald-500/15 border border-emerald-500/30 rounded text-emerald-400">
                                    Best
                                  </span>
                                )}
                              </td>
                              <td className="py-3.5 px-2 text-right font-mono">{m.cvAcc.toFixed(4)}</td>
                              <td className="py-3.5 px-2 text-right font-mono">{m.cvF1.toFixed(4)}</td>
                              <td className="py-3.5 px-2 text-right font-mono">{m.cvAuc.toFixed(4)}</td>
                              <td className="py-3.5 px-2 text-right font-mono text-white">{m.testAcc.toFixed(4)}</td>
                              <td className="py-3.5 px-2 text-right font-mono text-white">{m.testF1.toFixed(4)}</td>
                              <td className="py-3.5 px-2 text-right font-mono text-white">{m.testAuc.toFixed(4)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                    {/* Confusion Matrix Visual */}
                    <div className="bg-zinc-950/50 border border-zinc-900 p-5 rounded-2xl flex flex-col justify-between">
                      <div>
                        <span className="text-xs font-bold text-zinc-400 block mb-4 uppercase tracking-wider">
                          RF Confusion Matrix (Test Set)
                        </span>
                        
                        <div className="grid grid-cols-2 gap-2 text-center text-xs mb-4">
                          <div className="p-3 bg-zinc-900/60 border border-zinc-800 rounded-lg">
                            <div className="text-[10px] text-zinc-500 mb-0.5">True Negative (Benign)</div>
                            <div className="text-base font-bold text-white">
                              {binaryResults.confusionMatrix.matrix[0][0].toLocaleString()}
                            </div>
                          </div>
                          <div className="p-3 bg-zinc-900/60 border border-zinc-800 rounded-lg">
                            <div className="text-[10px] text-zinc-500 mb-0.5">False Positive (False Alert)</div>
                            <div className="text-base font-bold text-rose-500/90">
                              {binaryResults.confusionMatrix.matrix[0][1].toLocaleString()}
                            </div>
                          </div>
                          <div className="p-3 bg-zinc-900/60 border border-zinc-800 rounded-lg">
                            <div className="text-[10px] text-zinc-500 mb-0.5">False Negative (Missed)</div>
                            <div className="text-base font-bold text-rose-500/90">
                              {binaryResults.confusionMatrix.matrix[1][0].toLocaleString()}
                            </div>
                          </div>
                          <div className="p-3 bg-zinc-900/60 border border-zinc-800 rounded-lg">
                            <div className="text-[10px] text-zinc-500 mb-0.5">True Positive (Blocked)</div>
                            <div className="text-base font-bold text-white">
                              {binaryResults.confusionMatrix.matrix[1][1].toLocaleString()}
                            </div>
                          </div>
                        </div>
                      </div>

                      <div className="space-y-1.5 text-[11px] pt-4 border-t border-zinc-900">
                        <div className="flex justify-between text-zinc-500">
                          <span>Precision:</span>
                          <span className="text-zinc-300 font-semibold">{(binaryResults.confusionMatrix.testPrecision * 100).toFixed(2)}%</span>
                        </div>
                        <div className="flex justify-between text-zinc-500">
                          <span>Recall (Detection Rate):</span>
                          <span className="text-zinc-300 font-semibold">{(binaryResults.confusionMatrix.testRecall * 100).toFixed(2)}%</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* 2. Multi-class Results */}
                <div className="bg-zinc-900/40 border border-zinc-900 p-6 rounded-2xl">
                  <div className="border-b border-zinc-800/60 pb-4 mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div>
                      <h2 className="text-base font-bold text-white flex items-center gap-2">
                        <Layers className="w-5 h-5 text-indigo-400" />
                        Multi-Class Classification (Attack Type Identification)
                      </h2>
                      <p className="text-xs text-zinc-400 mt-0.5">
                        Identifying the specific classification of attack. RandomForestClassifier leads with Test Macro-F1 = 96.58%.
                      </p>
                    </div>
                    <span className="px-3 py-1 bg-indigo-500/10 border border-indigo-500/30 rounded-xl text-xs font-bold text-indigo-400 self-start">
                      Best: {multiclassResults.bestModel}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Performance Table */}
                    <div className="lg:col-span-2 space-y-6">
                      <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse text-xs">
                          <thead>
                            <tr className="border-b border-zinc-800 text-zinc-400 font-bold">
                              <th className="py-3 px-2">Classifier Model</th>
                              <th className="py-3 px-2 text-right">CV Accuracy</th>
                              <th className="py-3 px-2 text-right">CV Macro-F1</th>
                              <th className="py-3 px-2 text-right">Test Accuracy</th>
                              <th className="py-3 px-2 text-right">Test Macro-F1</th>
                              <th className="py-3 px-2 text-right">Test Wt-F1</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-zinc-900">
                            {multiclassResults.models.map((m) => (
                              <tr
                                key={m.name}
                                className={`hover:bg-zinc-900/30 transition-all ${
                                  m.best ? "bg-indigo-500/5 text-white font-semibold" : "text-zinc-400"
                                }`}
                              >
                                <td className="py-3.5 px-2 font-medium flex items-center gap-2">
                                  {m.name}
                                  {m.best && (
                                    <span className="px-1.5 py-0.5 text-[8px] bg-indigo-500/15 border border-indigo-500/30 rounded text-indigo-400">
                                      Best
                                    </span>
                                  )}
                                </td>
                                <td className="py-3.5 px-2 text-right font-mono">
                                  {m.cvAcc ? m.cvAcc.toFixed(4) : <span className="text-zinc-600">—</span>}
                                </td>
                                <td className="py-3.5 px-2 text-right font-mono">
                                  {m.cvMacroF1 ? m.cvMacroF1.toFixed(4) : <span className="text-zinc-600">—</span>}
                                </td>
                                <td className="py-3.5 px-2 text-right font-mono text-white">
                                  {m.testAcc ? m.testAcc.toFixed(4) : <span className="text-zinc-600">—</span>}
                                </td>
                                <td className="py-3.5 px-2 text-right font-mono text-white">
                                  {m.testMacroF1 ? m.testMacroF1.toFixed(4) : <span className="text-indigo-400 animate-pulse font-semibold">Running</span>}
                                </td>
                                <td className="py-3.5 px-2 text-right font-mono text-white">
                                  {m.testWtF1 ? m.testWtF1.toFixed(4) : <span className="text-zinc-600">—</span>}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>

                    {/* Per-class F1 performance */}
                    <div className="bg-zinc-950/50 border border-zinc-900 p-5 rounded-2xl flex flex-col">
                      <span className="text-xs font-bold text-zinc-400 block mb-4 uppercase tracking-wider">
                        Per-Class Performance (RF)
                      </span>
                      
                      <div className="space-y-2 flex-1 overflow-y-auto max-h-56 pr-2">
                        {multiclassResults.perClassF1.map((item) => (
                          <div key={item.cls} className="flex items-center justify-between text-xs py-1 border-b border-zinc-900/60">
                            <span className="font-mono text-zinc-300">{item.cls}</span>
                            <div className="flex items-center gap-3">
                              <div className="w-16 bg-zinc-800 rounded-full h-1.5 overflow-hidden">
                                <div 
                                  className={`h-full rounded-full ${
                                    item.f1 >= 0.95 ? "bg-emerald-400" : item.f1 >= 0.85 ? "bg-indigo-400" : "bg-orange-400"
                                  }`} 
                                  style={{ width: `${item.f1 * 100}%` }}
                                />
                              </div>
                              <span className="font-mono font-bold text-white">{item.f1.toFixed(2)}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* ── THREATS TAB ─────────────────────────────────────────────────── */}
            {activeTab === "threats" && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Attack list */}
                <div className="bg-zinc-900/40 border border-zinc-900 p-6 rounded-2xl lg:col-span-1">
                  <h2 className="text-base font-bold text-white flex items-center gap-2 mb-4">
                    <ShieldAlert className="w-5 h-5 text-rose-400" />
                    Intrusion Class Encyclopedia
                  </h2>
                  <p className="text-xs text-zinc-400 leading-normal mb-4">
                    Click an attack type to inspect its network flow signature and alignment with the MITRE ATT&CK framework.
                  </p>

                  <div className="space-y-2">
                    {Object.keys(attackDescriptions).map((attack) => (
                      <button
                        key={attack}
                        onClick={() => setSelectedAttack(attack)}
                        className={`w-full text-left p-3 rounded-xl border transition-all text-xs font-semibold flex items-center justify-between ${
                          selectedAttack === attack
                            ? "bg-rose-500/10 border-rose-500/40 text-rose-400 font-bold"
                            : "bg-zinc-950/30 border-zinc-900 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/30"
                        }`}
                      >
                        <span className="capitalize">{attack}</span>
                        {attack === "normal" ? (
                          <span className="px-1.5 py-0.5 text-[9px] bg-emerald-500/10 text-emerald-400 rounded">
                            Benign
                          </span>
                        ) : (
                          <span className="px-1.5 py-0.5 text-[9px] bg-rose-500/10 text-rose-400 rounded">
                            Malicious
                          </span>
                        )}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Details view */}
                <div className="bg-zinc-900/40 border border-zinc-900 p-6 rounded-2xl lg:col-span-2">
                  <AnimatePresence mode="wait">
                    {selectedAttack && (
                      <motion.div
                        key={selectedAttack}
                        initial={{ opacity: 0, x: 10 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -10 }}
                        transition={{ duration: 0.2 }}
                        className="space-y-6"
                      >
                        {/* Title header */}
                        <div className="flex items-center gap-3 border-b border-zinc-800/80 pb-4">
                          <div className={`p-2.5 rounded-xl border ${
                            selectedAttack === "normal"
                              ? "bg-emerald-500/10 border-emerald-500/25 text-emerald-400"
                              : "bg-rose-500/10 border-rose-500/25 text-rose-400"
                          }`}>
                            <Shield className="w-5 h-5" />
                          </div>
                          <div>
                            <h3 className="text-lg font-bold text-white capitalize">{selectedAttack}</h3>
                            <span className="text-[11px] font-mono text-zinc-500 uppercase">
                              MITRE ATT&CK: {attackDescriptions[selectedAttack].mitre}
                            </span>
                          </div>
                        </div>

                        {/* Description */}
                        <div>
                          <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider block mb-1">
                            Operational Description:
                          </span>
                          <p className="text-sm text-zinc-300 leading-relaxed">
                            {attackDescriptions[selectedAttack].description}
                          </p>
                        </div>

                        {/* Packet signature info */}
                        <div className="bg-zinc-950/60 border border-zinc-800 p-5 rounded-xl">
                          <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider block mb-2 flex items-center gap-1.5">
                            <Info className="w-3.5 h-3.5 text-indigo-400" />
                            Flow Signature Markers
                          </span>
                          <p className="text-xs font-mono text-zinc-300 leading-relaxed">
                            {attackDescriptions[selectedAttack].indicators}
                          </p>
                        </div>

                        {/* Recommendation details */}
                        <div className="space-y-2 text-xs">
                          <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider block">
                            Threat Mitigation Guidelines:
                          </span>
                          <ul className="list-disc pl-4 space-y-1 text-zinc-400">
                            {selectedAttack === "normal" ? (
                              <>
                                <li>Monitor baseline network traffic volumes for sudden spikes.</li>
                                <li>Update device firmware periodically.</li>
                              </>
                            ) : (
                              <>
                                <li>Enforce firewalls and block signatures matching these packet ratios.</li>
                                <li>Isolate infected IoT hubs to segregated subnets.</li>
                                <li>Apply packet rate-limiting on ports identified in the signature.</li>
                              </>
                            )}
                          </ul>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </div>
            )}
          </motion.div>
        </AnimatePresence>

      </main>

      {/* FOOTER */}
      <footer className="border-t border-zinc-900 mt-20 bg-zinc-950 text-zinc-600 text-xs py-8">
        <div className="max-w-7xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <span>&copy; {new Date().getFullYear()} Kshitiz Khandelwal. All Rights Reserved.</span>
          <div className="flex gap-4">
            <span className="text-zinc-500">TON_IoT network dataset capture (CC BY 4.0)</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
