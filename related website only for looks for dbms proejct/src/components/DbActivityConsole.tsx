import { useEffect, useState, useRef } from "react";
import { Terminal, ChevronUp, ChevronDown, CheckCircle, XCircle, Clock, Database, Copy, RefreshCw } from "lucide-react";
import { type AuditLog, db } from "@/lib/db-store";
import { toast } from "sonner";

export function DbActivityConsole() {
  const [open, setOpen] = useState(false);
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const consoleEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Initial load
    setLogs([...db.auditLogsTable].reverse());

    // Listen to live SQL queries
    const handleQuery = (e: Event) => {
      const customEvent = e as CustomEvent<AuditLog>;
      setLogs((prev) => [...prev, customEvent.detail]);
    };

    window.addEventListener("ecg-sql-query", handleQuery);
    return () => window.removeEventListener("ecg-sql-query", handleQuery);
  }, []);

  useEffect(() => {
    if (open && consoleEndRef.current) {
      consoleEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs, open]);

  const copyQuery = (sql: string) => {
    navigator.clipboard.writeText(sql);
    toast.success("SQL query copied to clipboard");
  };

  const clearLogs = () => {
    setLogs([]);
    toast.info("Console log cleared locally");
  };

  return (
    <div className="fixed bottom-0 left-0 right-0 z-40 transition-all duration-300 pointer-events-none md:left-64">
      {/* Console Tab */}
      <div className="flex justify-end px-6 pointer-events-auto">
        <button
          onClick={() => setOpen(!open)}
          className="flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-t-xl bg-card-foreground dark:bg-card border-x border-t border-border shadow-glow font-mono text-[#00ff66] hover:bg-black/90 transition-all cursor-pointer"
        >
          <Terminal className="h-4.5 w-4.5 animate-pulse" />
          <span>{open ? "COLLAPSE SQL CONSOLE" : "OPEN LIVE SQL CONSOLE"}</span>
          <span className="bg-[#00ff66]/20 px-1.5 py-0.5 rounded text-[10px]">
            {logs.length} queries
          </span>
          {open ? <ChevronDown className="h-3.5 w-3.5" /> : <ChevronUp className="h-3.5 w-3.5" />}
        </button>
      </div>

      {/* Terminal Area */}
      {open && (
        <div className="w-full h-64 bg-black/95 dark:bg-black border-t border-border flex flex-col font-mono text-sm pointer-events-auto shadow-2xl relative">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-2 bg-zinc-900 border-b border-zinc-800 text-xs text-muted-foreground select-none">
            <div className="flex items-center gap-2">
              <Database className="h-3.5 w-3.5 text-primary" />
              <span className="font-bold text-zinc-300">POSTGRESQL ACTIVITY MONITOR & QUERY CONSOLE</span>
              <span className="bg-zinc-800 text-zinc-400 px-1.5 py-0.5 rounded text-[10px]">
                DB: ecg_heart_prediction
              </span>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={clearLogs}
                className="hover:text-zinc-200 transition-colors flex items-center gap-1 cursor-pointer"
              >
                <RefreshCw className="h-3 w-3" /> Clear
              </button>
              <span className="text-[#00ff66]/70">● Engine Online (127.0.0.1:5432)</span>
            </div>
          </div>

          {/* Log List */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3 scrollbar-thin">
            {logs.length === 0 ? (
              <div className="text-zinc-500 text-center py-10 italic">
                -- No query logs recorded in this session. Trigger SQL events by interacting with the UI. --
              </div>
            ) : (
              logs.map((log, i) => (
                <div
                  key={log.log_id || i}
                  className="p-3.5 rounded-lg bg-zinc-950 border border-zinc-800 hover:border-zinc-700 transition-colors flex flex-col md:flex-row md:items-start justify-between gap-3 text-zinc-300"
                >
                  <div className="space-y-1.5 flex-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2 text-xs">
                      <span className="text-zinc-500">#{log.log_id}</span>
                      <span className="text-zinc-400 font-bold">{log.timestamp}</span>
                      <span className="bg-primary/10 text-primary px-2 py-0.5 rounded font-semibold text-[10px]">
                        USER: {log.username} ({log.role})
                      </span>
                      <span className="text-zinc-500">IP: {log.ip_address}</span>
                      <span className="text-zinc-400 italic">-- {log.activity}</span>
                    </div>

                    <div className="relative group mt-1 bg-zinc-900/60 p-2.5 rounded border border-zinc-850 font-mono text-[#00ff66] break-all whitespace-pre-wrap pr-10 text-xs">
                      {log.sql_query}
                      <button
                        onClick={() => copyQuery(log.sql_query || "")}
                        className="absolute right-2 top-2 opacity-0 group-hover:opacity-100 transition-opacity p-1 text-zinc-400 hover:text-white bg-zinc-800 rounded cursor-pointer"
                        title="Copy Query"
                      >
                        <Copy className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </div>

                  <div className="flex flex-row md:flex-col items-center md:items-end justify-between md:justify-center gap-1.5 text-xs flex-shrink-0">
                    <div className="flex items-center gap-1">
                      {log.status === "SUCCESS" ? (
                        <span className="text-[#00ff66] font-bold bg-[#00ff66]/10 px-2 py-0.5 rounded flex items-center gap-1 border border-[#00ff66]/20">
                          <CheckCircle className="h-3.5 w-3.5" /> SUCCESS
                        </span>
                      ) : (
                        <span className="text-destructive font-bold bg-destructive/10 px-2 py-0.5 rounded flex items-center gap-1 border border-destructive/20">
                          <XCircle className="h-3.5 w-3.5" /> BLOCKED
                        </span>
                      )}
                    </div>
                    <div className="text-zinc-500 text-[10px] flex items-center gap-1 mt-1">
                      <Clock className="h-3 w-3" /> {log.execution_time_ms} ms
                    </div>
                  </div>
                </div>
              ))
            )}
            <div ref={consoleEndRef} />
          </div>
        </div>
      )}
    </div>
  );
}
