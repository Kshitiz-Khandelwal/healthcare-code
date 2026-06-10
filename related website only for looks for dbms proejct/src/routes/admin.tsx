import { createFileRoute } from "@tanstack/react-router";
import { ShieldCheck, Users, Database, HeartPulse, Brain, UserCheck, Clock, RefreshCw, Server, CheckCircle, AlertCircle } from "lucide-react";
import { useEffect, useState } from "react";
import { AppLayout } from "@/components/AppLayout";
import { SqlQueryCard } from "@/components/SqlQueryCard";
import { sqlQueries } from "@/lib/sql-queries";
import { db, type AppRole } from "@/lib/db-store";
import { supabaseSync, type SupabaseStatus } from "@/lib/supabase-sync";
import { toast } from "sonner";

export const Route = createFileRoute("/admin")({
  head: () => ({ meta: [{ title: "System Administration — CardioPredict" }] }),
  component: AdminPage,
});

function AdminPage() {
  const [role, setRole] = useState<AppRole>(db.getRole());
  const [renderCount, setRenderCount] = useState(0);

  // Supabase Sync States
  const [supabaseStatus, setSupabaseStatus] = useState<SupabaseStatus>({
    connected: false,
    message: "Verifying credentials handshake..."
  });
  const [syncing, setSyncing] = useState(false);
  const [showSqlAlert, setShowSqlAlert] = useState(false);

  useEffect(() => {
    // Check connection on load
    checkSupabaseHandshake();

    const unsubscribe = db.subscribe(() => {
      setRole(db.getRole());
      setRenderCount(c => c + 1);
    });
    return () => unsubscribe();
  }, []);

  const checkSupabaseHandshake = async () => {
    const res = await supabaseSync.testConnection();
    setSupabaseStatus(res);
  };

  const handleSyncToSupabase = async () => {
    setSyncing(true);
    toast.loading("Initiating Supabase transaction sync...", { id: "sb-sync" });

    // 1. Double check connection
    const conn = await supabaseSync.testConnection();
    if (!conn.connected) {
      setSyncing(false);
      return toast.error("Supabase endpoint is currently unreachable. Check network credentials.", { id: "sb-sync" });
    }

    try {
      // 2. Synchronize tables one by one (Upsert behavior via pure REST API!)
      const uRes = await supabaseSync.pushTable("users", db.usersTable);
      if (!uRes.success) throw new Error(uRes.msg);

      const dRes = await supabaseSync.pushTable("doctors", db.doctorsTable);
      if (!dRes.success) throw new Error(dRes.msg);

      const pRes = await supabaseSync.pushTable("patients", db.patientsTable);
      if (!pRes.success) throw new Error(pRes.msg);

      const eRes = await supabaseSync.pushTable("ecg_records", db.ecgRecordsTable);
      if (!eRes.success) throw new Error(eRes.msg);

      const prRes = await supabaseSync.pushTable("predictions", db.predictionsTable);
      if (!prRes.success) throw new Error(prRes.msg);

      toast.success("Successfully synchronized all DBMS records to remote Supabase tables!", { id: "sb-sync" });
    } catch (err: any) {
      console.error(err);
      toast.error(err.message || "Failed to complete Supabase transaction.", { id: "sb-sync", duration: 6000 });
      if (err.message.includes("not found")) {
        setShowSqlAlert(true);
      }
    } finally {
      setSyncing(false);
    }
  };

  const tables = [
    { name: "users", icon: ShieldCheck, count: db.usersTable.length, color: "text-blue-500", bg: "bg-blue-500/5 border-blue-500/20" },
    { name: "patients", icon: Users, count: db.patientsTable.length, color: "text-green-500", bg: "bg-green-500/5 border-green-500/20" },
    { name: "doctors", icon: UserCheck, count: db.doctorsTable.length, color: "text-amber-500", bg: "bg-amber-500/5 border-amber-500/20" },
    { name: "ecg_records", icon: HeartPulse, count: db.ecgRecordsTable.length, color: "text-red-500", bg: "bg-red-500/5 border-red-500/20" },
    { name: "predictions", icon: Brain, count: db.predictionsTable.length, color: "text-purple-500", bg: "bg-purple-500/5 border-purple-500/20" },
  ];

  return (
    <AppLayout 
      title="Database System Administration" 
      subtitle="users Table · Access Control & Supabase Database Integrations"
    >
      <div className="space-y-6 animate-fade-in">
        {/* Supabase Live Status & Sync Center (Wow Factor!) */}
        <div className="glass rounded-2xl p-5 border border-border flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className={`p-2.5 rounded-xl border flex items-center justify-center flex-shrink-0 ${
              supabaseStatus.connected ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-500" : "bg-red-500/10 border-red-500/30 text-red-500"
            }`}>
              <Server className="h-6 w-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-foreground">Supabase Remote Database Status</h3>
                <span className="flex h-2 w-2 relative">
                  <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                    supabaseStatus.connected ? "bg-emerald-400" : "bg-red-400"
                  }`}></span>
                  <span className={`relative inline-flex rounded-full h-2 w-2 ${
                    supabaseStatus.connected ? "bg-emerald-500" : "bg-red-500"
                  }`}></span>
                </span>
              </div>
              <p className="text-xs text-muted-foreground mt-0.5 font-mono">
                Host: <strong className="text-primary">{supabaseSync.getSupabaseUrl()}</strong>
              </p>
              <p className={`text-xs mt-1.5 font-semibold ${supabaseStatus.connected ? "text-emerald-500" : "text-muted-foreground"}`}>
                {supabaseStatus.message}
              </p>
            </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={checkSupabaseHandshake}
              className="h-10 w-10 border border-border hover:bg-muted rounded-xl flex items-center justify-center text-foreground cursor-pointer"
              title="Refresh Connection"
            >
              <RefreshCw className="h-4 w-4" />
            </button>
            
            <button
              onClick={handleSyncToSupabase}
              disabled={syncing || !supabaseStatus.connected}
              className="h-10 px-4 gradient-primary text-primary-foreground font-semibold text-xs rounded-xl shadow-glow flex items-center gap-1.5 cursor-pointer disabled:opacity-60"
            >
              <RefreshCw className={`h-4 w-4 ${syncing ? "animate-spin" : ""}`} />
              Push Local DBMS to Supabase
            </button>
          </div>
        </div>

        {/* Dynamic Database Statistics Grid */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {tables.map((t) => (
            <div key={t.name} className={`glass rounded-2xl p-4 border ${t.bg}`}>
              <t.icon className={`h-5 w-5 ${t.color} animate-pulse`} />
              <div className="mt-3 text-xs text-muted-foreground font-mono">{t.name}</div>
              <div className="text-2xl font-bold text-foreground mt-1">{t.count}</div>
              <div className="text-[10px] text-muted-foreground">tuples (rows)</div>
            </div>
          ))}
        </div>

        {/* Users credentials Registry */}
        <div className="glass rounded-2xl p-5 border border-border">
          <div className="flex items-center justify-between border-b border-border/60 pb-2.5">
            <div>
              <h3 className="font-semibold text-foreground flex items-center gap-1.5"><ShieldCheck className="h-4.5 w-4.5 text-primary" /> users Credentials Table</h3>
              <p className="text-xs text-muted-foreground">Admin-only display of secure patient, doctor, and administrator login credentials.</p>
            </div>
            <span className="text-[10px] font-mono text-muted-foreground bg-black/10 dark:bg-black/35 px-2.5 py-1 rounded">
              SELECT user_id, name, email, password_hash, role FROM users;
            </span>
          </div>

          <div className="overflow-x-auto mt-4">
            <table className="w-full text-xs text-left">
              <thead className="text-muted-foreground uppercase border-b border-border bg-muted/20">
                <tr>
                  <th className="py-2.5 px-4">User ID</th>
                  <th>Display Name</th>
                  <th>Auth Email</th>
                  <th>Secure Password Hash (Bcrypt)</th>
                  <th>User Role</th>
                  <th>Created At</th>
                </tr>
              </thead>
              <tbody>
                {db.usersTable.map((u) => (
                  <tr key={u.user_id} className="border-b border-border/50 hover:bg-muted/10 transition-colors">
                    <td className="py-3 px-4 font-mono font-bold text-primary">#{u.user_id}</td>
                    <td className="font-semibold text-foreground">{u.name}</td>
                    <td className="font-mono text-zinc-400">{u.email}</td>
                    <td className="font-mono text-zinc-500 text-[10px] tracking-tight">{u.password_hash}</td>
                    <td>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                        u.role === "Admin" ? "bg-red-500/10 text-red-500 border-red-500/20" :
                        u.role === "Doctor" ? "bg-amber-500/10 text-amber-500 border-amber-500/20" :
                        "bg-blue-500/10 text-blue-500 border-blue-500/20"
                      }`}>
                        {u.role}
                      </span>
                    </td>
                    <td className="font-mono text-zinc-500"><Clock className="h-3 w-3 inline mr-1" />{u.created_at}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Database DDL Queries */}
        <div>
          <h3 className="font-semibold text-foreground mb-3 flex items-center gap-1.5"><Database className="h-4.5 w-4.5 text-primary" /> Related Administration & Auth DDL/DML</h3>
          <div className="grid lg:grid-cols-2 gap-4">
            {["create-db", "create-users", "insert-admin", "login-query"].map((id) => (
              <SqlQueryCard key={id} query={sqlQueries.find((q) => q.id === id)!} />
            ))}
          </div>
        </div>
      </div>

      {/* SQL SCHEMA SETUP ALERT MODAL */}
      {showSqlAlert && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4" onClick={() => setShowSqlAlert(false)}>
          <div onClick={(e) => e.stopPropagation()} className="w-full max-w-lg bg-card rounded-2xl p-6 border border-border shadow-2xl space-y-4 animate-scale-in">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-amber-500/10 text-amber-500 rounded-lg border border-amber-500/20">
                <AlertCircle className="h-6 w-6 animate-pulse" />
              </div>
              <div>
                <h3 className="font-bold text-foreground text-base">Schema Setup Required on Supabase</h3>
                <p className="text-xs text-muted-foreground mt-1">
                  We successfully connected to your Supabase instance, but the target tables do not exist yet! 
                </p>
              </div>
            </div>

            <div className="text-xs text-foreground bg-muted/65 p-4 rounded-xl space-y-2 border border-border leading-relaxed">
              <span className="font-bold text-primary block">How to populate remote tables:</span>
              <ol className="list-decimal pl-4 space-y-1 text-zinc-600 dark:text-zinc-300">
                <li>Go to your **Supabase Dashboard** online.</li>
                <li>Open the **SQL Editor** tab in the sidebar.</li>
                <li>Click **New Query** and copy-paste the entire contents of our <code className="text-primary font-bold">schema.sql</code> file (located at the root of the project).</li>
                <li>Click **Run** to stand up all tables, PK/FK relationships, and cascade triggers.</li>
                <li>Return here and click **"Push Local DBMS to Supabase"** to seed all patients rows!</li>
              </ol>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setShowSqlAlert(false)}
                className="px-4 py-2 bg-primary text-primary-foreground font-semibold text-xs rounded-xl shadow cursor-pointer"
              >
                Got it, Thanks!
              </button>
            </div>
          </div>
        </div>
      )}
    </AppLayout>
  );
}