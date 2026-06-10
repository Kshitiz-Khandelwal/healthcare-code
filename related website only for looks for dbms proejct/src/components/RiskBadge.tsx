import React from "react";

export interface RiskBadgeProps {
  level: "Low" | "Medium" | "High";
}

export function RiskBadge({ level }: RiskBadgeProps) {
  const styles = {
    Low: "bg-emerald-500/10 text-emerald-500 border-emerald-500/20 dark:bg-emerald-500/15",
    Medium: "bg-amber-500/10 text-amber-500 border-amber-500/20 dark:bg-amber-500/15",
    High: "bg-red-500/10 text-red-500 border-red-500/20 dark:bg-red-500/15 animate-pulse",
  };

  const badgeStyle = styles[level] || styles.Low;

  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider border ${badgeStyle}`}>
      ● {level} Risk
    </span>
  );
}
