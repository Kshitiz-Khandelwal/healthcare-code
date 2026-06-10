import { useState } from "react";
import { Play, Database, Code2, ChevronDown } from "lucide-react";
import type { SqlQueryDef } from "@/lib/sql-queries";

const categoryColors: Record<string, string> = {
  DDL: "bg-primary/10 text-primary border-primary/20",
  DML: "bg-warning/10 text-warning border-warning/30",
  Query: "bg-success/10 text-success border-success/30",
  Auth: "bg-accent/10 text-accent border-accent/30",
  Analytics: "bg-primary/10 text-primary border-primary/20",
  View: "bg-muted-foreground/10 text-muted-foreground border-border",
};

export function SqlQueryCard({ query, defaultOpen = false }: { query: SqlQueryDef; defaultOpen?: boolean }) {
  const [open, setOpen] = useState(defaultOpen);
  const [result, setResult] = useState<ReturnType<SqlQueryDef["run"]> | null>(null);
  const [running, setRunning] = useState(false);

  const exec = () => {
    setRunning(true);
    setTimeout(() => {
      setResult(query.run());
      setRunning(false);
      setOpen(true);
    }, 280);
  };

  return (
    <div className="glass rounded-2xl overflow-hidden">
      <div className="p-5">
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className={`text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full border ${categoryColors[query.category]}`}>
                {query.category}
              </span>
              <h3 className="font-semibold text-foreground">{query.title}</h3>
            </div>
            <p className="text-xs text-muted-foreground mt-1">{query.description}</p>
          </div>
          <button
            onClick={exec}
            disabled={running}
            className="flex-shrink-0 inline-flex items-center gap-1.5 gradient-primary text-primary-foreground text-xs font-medium px-3 py-1.5 rounded-lg hover:shadow-glow transition-all disabled:opacity-60"
          >
            <Play className="h-3 w-3" /> {running ? "Running..." : "Run"}
          </button>
        </div>
        <div className="rounded-lg bg-foreground/95 dark:bg-black/40 text-background dark:text-foreground p-3 font-mono text-xs overflow-x-auto">
          <div className="flex items-center gap-1.5 text-[10px] text-background/60 dark:text-muted-foreground mb-1.5">
            <Code2 className="h-3 w-3" /> SQL
          </div>
          <pre className="whitespace-pre text-background/90 dark:text-foreground/90">{query.sql}</pre>
        </div>
      </div>
      {result && (
        <div className="border-t border-border bg-muted/30">
          <button onClick={() => setOpen((o) => !o)} className="w-full flex items-center justify-between px-5 py-2.5 text-xs font-medium text-foreground hover:bg-muted/50 transition-colors">
            <span className="flex items-center gap-2">
              <Database className="h-3.5 w-3.5 text-primary" />
              Result {result.affected && <span className="text-muted-foreground">— {result.affected}</span>}
              {!result.affected && <span className="text-muted-foreground">— {result.rows.length} row(s)</span>}
            </span>
            <ChevronDown className={`h-4 w-4 transition-transform ${open ? "rotate-180" : ""}`} />
          </button>
          {open && (
            <div className="px-5 pb-5 overflow-x-auto">
              <table className="w-full text-xs border-collapse">
                <thead>
                  <tr className="border-b border-border">
                    {result.columns.map((c) => (
                      <th key={c} className="text-left py-2 px-2 font-semibold text-foreground">{c}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {result.rows.map((r, i) => (
                    <tr key={i} className="border-b border-border/50 hover:bg-muted/40">
                      {r.map((c, j) => (
                        <td key={j} className="py-2 px-2 text-muted-foreground font-mono">{String(c)}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}