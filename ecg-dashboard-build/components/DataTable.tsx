"use client";

import { motion } from "framer-motion";

interface DataTableProps {
  columns: string[];
  data: Record<string, string | number>[];
}

export default function DataTable({ columns, data }: DataTableProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      viewport={{ once: true }}
      className="overflow-x-auto bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50 rounded-lg backdrop-blur-sm"
    >
      <table className="w-full">
        <thead>
          <tr className="border-b border-slate-700/50">
            {columns.map((col) => (
              <th
                key={col}
                className="px-6 py-4 text-left text-sm font-semibold text-slate-300 bg-slate-900/50"
              >
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr
              key={idx}
              className="border-b border-slate-700/30 hover:bg-slate-800/30 transition-colors"
            >
              {columns.map((col) => (
                <td key={col} className="px-6 py-4 text-sm text-slate-300">
                  {typeof row[col.toLowerCase()] === "number"
                    ? row[col.toLowerCase()].toFixed(1)
                    : row[col.toLowerCase()]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </motion.div>
  );
}
