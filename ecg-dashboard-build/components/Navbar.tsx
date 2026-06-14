"use client";

import { Activity } from "lucide-react";
import { useEffect, useState } from "react";

const navLinks = [
  { href: "#summary", label: "Summary" },
  { href: "#pipeline", label: "Pipeline" },
  { href: "#features", label: "Features" },
  { href: "#performance", label: "Performance" },
  { href: "#comparison", label: "B0 vs B4" },
  { href: "#predictions", label: "Predictions" },
  { href: "#risk", label: "Risk" },
  { href: "#dataset", label: "Dataset" },
  { href: "#conclusion", label: "Conclusion" },
];

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <nav
      className={`fixed left-0 right-0 top-0 z-50 transition-all duration-300 print:hidden ${
        scrolled
          ? "border-b border-slate-200/10 bg-slate-950/92 shadow-lg backdrop-blur-xl"
          : "bg-slate-950/20 backdrop-blur-sm"
      }`}
    >
      <div className="container mx-auto flex h-14 items-center justify-between px-4">
        <a href="#hero" className="flex items-center gap-2 text-sm font-bold tracking-wide text-white">
          <Activity className="text-teal-300" size={18} />
          ECG Report
        </a>
        <div className="hidden items-center gap-1 lg:flex">
          {navLinks.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="rounded-md px-3 py-1.5 text-xs text-slate-300 transition hover:bg-white/10 hover:text-white"
            >
              {link.label}
            </a>
          ))}
        </div>
      </div>
    </nav>
  );
}
