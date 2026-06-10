import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { 
  Database, 
  Search, 
  Terminal, 
  BookOpen, 
  ArrowRight, 
  Play, 
  CheckCircle, 
  Layers, 
  Activity, 
  Key, 
  HelpCircle,
  Clock,
  Sparkles
} from "lucide-react";
import { AppLayout } from "@/components/AppLayout";
import { SqlQueryCard } from "@/components/SqlQueryCard";
import { sqlQueries } from "@/lib/sql-queries";
import { db } from "@/lib/db-store";
import { toast } from "sonner";

export const Route = createFileRoute("/sql-queries")({
  head: () => ({ meta: [{ title: "DBMS Console & SQL — CardioPredict" }] }),
  component: SqlPage,
});

const cats = ["All", "DDL", "DML", "Query", "Auth", "Analytics", "View"] as const;

function SqlPage() {
  const [activeTab, setActiveTab] = useState<"catalog" | "playground" | "docs">("catalog");
  
  // Catalog tab state
  const [cat, setCat] = useState<(typeof cats)[number]>("All");
  const [search, setSearch] = useState("");

  // Playground tab state
  const [rawSql, setRawSql] = useState(
    `-- Write your freeform SELECT queries here. Try one of these:\n-- SELECT * FROM patients;\n-- SELECT * FROM ecg_records;\n-- SELECT * FROM predictions;\n-- SELECT * FROM users;\n-- SELECT p.full_name, e.heart_rate, pr.disease_name, pr.risk_level FROM patients p JOIN ecg_records e ON p.patient_id = e.patient_id JOIN predictions pr ON p.patient_id = pr.patient_id;\n\nSELECT * FROM patients;`
  );
  const [queryResult, setQueryResult] = useState<{
    columns: string[];
    rows: (string | number)[][];
    affected?: string;
    error?: string;
    executionTimeMs?: number;
  } | null>(null);

  // Catalog filtering
  const list = useMemo(
    () =>
      sqlQueries.filter(
        (q) =>
          (cat === "All" || q.category === cat) &&
          (q.title.toLowerCase().includes(search.toLowerCase()) || q.sql.toLowerCase().includes(search.toLowerCase()))
      ),
    [cat, search]
  );

  const counts = useMemo(() => {
    const m: Record<string, number> = { All: sqlQueries.length };
    sqlQueries.forEach((q) => (m[q.category] = (m[q.category] || 0) + 1));
    return m;
  }, []);

  const handleRunRawSql = () => {
    const startTime = performance.now();
    const res = db.execute(rawSql);
    const executionTimeMs = +Math.max(1, Math.round(performance.now() - startTime));
    
    setQueryResult({
      ...res,
      executionTimeMs
    });

    if (res.error) {
      toast.error("SQL query execution failed. Inspect compiler logs.");
    } else {
      toast.success(`SQL query executed successfully in ${executionTimeMs}ms!`);
    }
  };

  return (
    <AppLayout 
      title="DBMS Console & Diagnostics Studio" 
      subtitle="Relational schemas, Step-by-step normalizations & Live SQL engines"
    >
      <div className="space-y-6">
        {/* Navigation Tabs */}
        <div className="flex border-b border-border bg-card/40 p-1.5 rounded-xl border max-w-md">
          {[
            { id: "catalog", label: "SQL Catalog", icon: Database },
            { id: "playground", label: "SQL Playground", icon: Terminal },
            { id: "docs", label: "DBMS Schema Docs", icon: BookOpen }
          ].map((t) => (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id as any)}
              className={`flex-1 py-2 text-xs font-semibold rounded-lg flex items-center justify-center gap-1.5 transition-all cursor-pointer ${
                activeTab === t.id
                  ? "gradient-primary text-primary-foreground shadow"
                  : "text-muted-foreground hover:text-foreground hover:bg-muted/40"
              }`}
            >
              <t.icon className="h-4 w-4" />
              {t.label}
            </button>
          ))}
        </div>

        {/* ==========================================
        TAB 1: SQL CATALOG
        ========================================== */}
        {activeTab === "catalog" && (
          <div className="space-y-5 animate-fade-in">
            <div className="glass rounded-2xl p-5 border border-border">
              <div className="flex items-center gap-3">
                <Database className="h-6 w-6 text-primary" />
                <div>
                  <h2 className="font-semibold text-foreground">Relational Operations Catalog</h2>
                  <p className="text-xs text-muted-foreground">Filter by category or search target SQL statement. Click <strong className="text-primary">Run</strong> to execute against active tables.</p>
                </div>
              </div>
              <div className="mt-5 flex flex-col md:flex-row gap-3">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <input 
                    value={search} 
                    onChange={(e) => setSearch(e.target.value)} 
                    placeholder="Search title or SQL keyword..." 
                    className="w-full h-10 pl-9 pr-3 rounded-lg bg-background border border-input text-xs text-foreground focus:outline-none focus:ring-2 focus:ring-ring" 
                  />
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {cats.map((c) => (
                    <button 
                      key={c} 
                      onClick={() => setCat(c)} 
                      className={`text-xs font-semibold px-3 py-1.5 rounded-lg border transition-all cursor-pointer ${
                        cat === c ? "gradient-primary text-primary-foreground border-transparent shadow-glow" : "border-border text-muted-foreground hover:bg-muted"
                      }`}
                    >
                      {c} <span className="opacity-60">({counts[c] || 0})</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="grid lg:grid-cols-2 gap-4">
              {list.map((q) => <SqlQueryCard key={q.id} query={q} />)}
            </div>
          </div>
        )}

        {/* ==========================================
        TAB 2: SQL PLAYGROUND
        ========================================== */}
        {activeTab === "playground" && (
          <div className="grid lg:grid-cols-3 gap-6 animate-fade-in">
            {/* Editor block */}
            <div className="glass rounded-2xl p-5 border border-border lg:col-span-1 flex flex-col justify-between h-[420px]">
              <div className="space-y-4 flex-1 flex flex-col min-h-0">
                <div>
                  <h3 className="font-semibold text-foreground flex items-center gap-1.5"><Terminal className="h-4.5 w-4.5 text-primary" /> SQL Query Editor</h3>
                  <p className="text-xs text-muted-foreground mt-1">Execute safe PostgreSQL SELECT queries against active seeded tables.</p>
                </div>
                
                <textarea
                  value={rawSql}
                  onChange={(e) => setRawSql(e.target.value)}
                  className="flex-1 w-full p-4 rounded-xl bg-black border border-border font-mono text-xs text-[#00ff66] focus:outline-none resize-none leading-relaxed shadow-inner"
                  placeholder="SELECT * FROM patients;"
                />
              </div>

              <div className="pt-4 flex gap-2">
                <button
                  onClick={() => setRawSql(`SELECT * FROM patients;`)}
                  className="px-3 py-2 border border-border rounded-lg text-xs font-semibold hover:bg-muted cursor-pointer"
                >
                  Reset
                </button>
                <button
                  onClick={handleRunRawSql}
                  className="flex-1 py-2 rounded-lg gradient-primary text-primary-foreground font-semibold shadow-glow flex items-center justify-center gap-1.5 cursor-pointer hover:opacity-95"
                >
                  <Play className="h-4 w-4" /> Run Raw Query
                </button>
              </div>
            </div>

            {/* Results Grid block */}
            <div className="glass rounded-2xl p-5 border border-border lg:col-span-2 flex flex-col justify-between h-[420px]">
              <div className="flex flex-col h-full justify-between">
                <div className="flex items-center justify-between border-b border-border/60 pb-2.5 mb-3 flex-shrink-0">
                  <h3 className="font-semibold text-foreground flex items-center gap-1.5"><Database className="h-4.5 w-4.5 text-primary" /> Live SQL Query Result Set</h3>
                  {queryResult && (
                    <div className="flex items-center gap-3 text-xs text-zinc-500 font-mono">
                      <span className="flex items-center gap-1"><Clock className="h-3.5 w-3.5 text-primary" /> {queryResult.executionTimeMs} ms</span>
                      {queryResult.affected && <span className="bg-primary/10 text-primary px-1.5 py-0.5 rounded text-[10px] font-bold">{queryResult.affected} affected</span>}
                    </div>
                  )}
                </div>

                <div className="flex-1 overflow-auto rounded-lg border border-border bg-card/20 p-2 scrollbar-thin">
                  {!queryResult ? (
                    <div className="text-zinc-500 text-center py-20 italic text-xs">
                      -- Write a query and click "Run Raw Query" to see data streams --
                    </div>
                  ) : queryResult.error ? (
                    <div className="p-4 border border-destructive/35 bg-destructive/5 rounded-xl text-destructive font-mono text-xs space-y-2 animate-scale-in">
                      <div className="font-bold flex items-center gap-1">● [PostgreSQL Server Error] Execution Blocked</div>
                      <p className="leading-relaxed">{queryResult.error}</p>
                    </div>
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-[11px] font-mono border-collapse">
                        <thead>
                          <tr className="bg-muted border-b border-border text-muted-foreground uppercase text-[10px]">
                            {queryResult.columns.map((c, i) => (
                              <th key={i} className="p-2 border-r border-border/60 last:border-0">{c}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {queryResult.rows.map((row, ri) => (
                            <tr key={ri} className="border-b border-border/40 hover:bg-muted/15">
                              {row.map((val, vi) => (
                                <td key={vi} className="p-2 border-r border-border/30 last:border-0 text-foreground break-words">{val}</td>
                              ))}
                            </tr>
                          ))}
                          {queryResult.rows.length === 0 && (
                            <tr>
                              <td colSpan={queryResult.columns.length} className="text-center py-6 text-zinc-500 italic">
                                -- (Empty Result Set) --
                              </td>
                            </tr>
                          )}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ==========================================
        TAB 3: DBMS SCHEMA & DIAGRAMS
        ========================================== */}
        {activeTab === "docs" && (
          <div className="space-y-8 animate-fade-in font-sans">
            {/* Grid 1: ER Diagram & Relational Schema */}
            <div className="grid lg:grid-cols-2 gap-6">
              
              {/* ER DIAGRAM: PREMIUM MONOCHROME BOARD */}
              <div className="glass rounded-2xl p-5 border border-border">
                <h3 className="font-semibold text-foreground flex items-center gap-1.5 border-b border-border/60 pb-2 mb-4">
                  <Layers className="h-4.5 w-4.5 text-primary" /> Entity-Relationship (ER) Diagram (Monochrome Design)
                </h3>
                
                <div className="space-y-4 bg-black/45 p-4 rounded-xl border border-zinc-800 text-xs text-foreground font-mono leading-relaxed relative overflow-x-auto min-w-[320px]">
                  <div className="flex flex-col gap-6">
                    {/* Level 1: Core Identities */}
                    <div className="flex justify-between gap-4">
                      {/* USERS */}
                      <div className="border border-zinc-700 bg-zinc-950 p-2.5 rounded-lg w-40 flex-shrink-0">
                        <div className="font-bold border-b border-zinc-800 pb-1 text-primary text-center">users (Entity)</div>
                        <div className="text-[10px] space-y-0.5 mt-1 text-zinc-400">
                          <div>PK: user_id (INT)</div>
                          <div>name (VARCHAR)</div>
                          <div>email (VARCHAR)</div>
                          <div>role (VARCHAR)</div>
                        </div>
                      </div>
                      <div className="flex items-center text-zinc-500 font-bold">1 : N ➔</div>
                      {/* PATIENTS */}
                      <div className="border border-zinc-700 bg-zinc-950 p-2.5 rounded-lg w-40 flex-shrink-0">
                        <div className="font-bold border-b border-zinc-800 pb-1 text-primary text-center">patients (Entity)</div>
                        <div className="text-[10px] space-y-0.5 mt-1 text-zinc-400">
                          <div>PK: patient_id (INT)</div>
                          <div>FK: user_id (INT)</div>
                          <div>full_name (VARCHAR)</div>
                          <div>age / gender</div>
                          <div>blood_group</div>
                        </div>
                      </div>
                    </div>

                    {/* Cardinality Lines */}
                    <div className="flex justify-around items-center h-4 text-zinc-750 font-bold">
                      <div>↓ 1:N</div>
                      <div>↓ 1:N</div>
                    </div>

                    {/* Level 2: Clinical Records */}
                    <div className="flex justify-between gap-4">
                      {/* ECG_RECORDS */}
                      <div className="border border-zinc-700 bg-zinc-950 p-2.5 rounded-lg w-40 flex-shrink-0">
                        <div className="font-bold border-b border-zinc-800 pb-1 text-primary text-center">ecg_records (Entity)</div>
                        <div className="text-[10px] space-y-0.5 mt-1 text-zinc-400">
                          <div>PK: ecg_id (INT)</div>
                          <div>FK: patient_id (INT)</div>
                          <div>heart_rate (INT)</div>
                          <div>qrs_duration (DEC)</div>
                          <div>pr_interval (DEC)</div>
                        </div>
                      </div>
                      <div className="flex items-center text-zinc-500 font-bold">1 : 1 ➔</div>
                      {/* PREDICTIONS */}
                      <div className="border border-zinc-700 bg-zinc-950 p-2.5 rounded-lg w-40 flex-shrink-0">
                        <div className="font-bold border-b border-zinc-800 pb-1 text-primary text-center">predictions (Entity)</div>
                        <div className="text-[10px] space-y-0.5 mt-1 text-zinc-400">
                          <div>PK: prediction_id (INT)</div>
                          <div>FK: ecg_id (INT)</div>
                          <div>FK: patient_id (INT)</div>
                          <div>disease_name (VAR)</div>
                          <div>confidence (DEC)</div>
                        </div>
                      </div>
                    </div>

                    {/* Level 3: Outputs & Operations */}
                    <div className="flex justify-between gap-4 border-t border-zinc-900 pt-4">
                      {/* REPORTS */}
                      <div className="border border-zinc-800 bg-zinc-950/60 p-2 rounded-lg w-36 flex-shrink-0">
                        <div className="font-bold border-b border-zinc-900 pb-1 text-zinc-500 text-center">reports (Entity)</div>
                        <div className="text-[9px] mt-1 text-zinc-500">
                          <div>PK: report_id (INT)</div>
                          <div>FK: patient_id (INT)</div>
                          <div>FK: ecg_id (INT)</div>
                          <div>doctor_notes (TEXT)</div>
                        </div>
                      </div>

                      {/* APPOINTMENTS */}
                      <div className="border border-zinc-800 bg-zinc-950/60 p-2 rounded-lg w-36 flex-shrink-0">
                        <div className="font-bold border-b border-zinc-900 pb-1 text-zinc-500 text-center">appointments</div>
                        <div className="text-[9px] mt-1 text-zinc-500">
                          <div>PK: appointment_id</div>
                          <div>FK: patient_id</div>
                          <div>FK: doctor_id</div>
                          <div>status (VARCHAR)</div>
                        </div>
                      </div>

                      {/* AUDIT_LOGS */}
                      <div className="border border-zinc-800 bg-zinc-950/60 p-2 rounded-lg w-36 flex-shrink-0">
                        <div className="font-bold border-b border-zinc-900 pb-1 text-zinc-500 text-center">audit_logs</div>
                        <div className="text-[9px] mt-1 text-zinc-500">
                          <div>PK: log_id (INT)</div>
                          <div>FK: user_id (INT)</div>
                          <div>activity (VARCHAR)</div>
                          <div>sql_query (TEXT)</div>
                        </div>
                      </div>
                    </div>

                  </div>
                </div>
              </div>

              {/* RELATIONAL SCHEMAS & KEY INTEGRITY MAP */}
              <div className="glass rounded-2xl p-5 border border-border">
                <h3 className="font-semibold text-foreground flex items-center gap-1.5 border-b border-border/60 pb-2 mb-4">
                  <Key className="h-4.5 w-4.5 text-primary" /> Relational Schema & Key Mappings
                </h3>
                
                <div className="space-y-3.5 text-xs text-foreground">
                  {[
                    { name: "users", ddl: "users (user_id [PK], name, email, password_hash, role, created_at)" },
                    { name: "patients", ddl: "patients (patient_id [PK], user_id [FK REFERENCES users CASCADE], full_name, age, gender, blood_group, contact, email, address, created_at)" },
                    { name: "doctors", ddl: "doctors (doctor_id [PK], user_id [FK REFERENCES users], full_name, specialization, hospital, experience, contact, email)" },
                    { name: "ecg_records", ddl: "ecg_records (ecg_id [PK], patient_id [FK REFERENCES patients CASCADE], upload_url, upload_type, heart_rate, qrs_duration, pr_interval, qt_interval, ecg_signal, uploaded_at)" },
                    { name: "predictions", ddl: "predictions (prediction_id [PK], ecg_id [FK REFERENCES ecg_records], patient_id [FK REFERENCES patients], disease_name, confidence_score, risk_level, recommendation, predicted_at)" },
                    { name: "reports", ddl: "reports (report_id [PK], patient_id [FK REFERENCES patients], ecg_id [FK REFERENCES ecg_records], doctor_notes, generated_at)" },
                    { name: "appointments", ddl: "appointments (appointment_id [PK], patient_id [FK], doctor_id [FK], appointment_date, status)" },
                  ].map((s, i) => (
                    <div key={i} className="bg-muted/40 p-3 rounded-lg border border-border/80 font-mono">
                      <div className="font-bold text-primary flex items-center gap-1 text-[11px] mb-1">
                        <span className="h-1.5 w-1.5 rounded-full bg-primary" /> {s.name} Schema Definition
                      </div>
                      <p className="text-[10px] text-foreground leading-relaxed font-bold break-all bg-black/10 dark:bg-black/35 p-1 rounded mt-1.5">{s.ddl}</p>
                    </div>
                  ))}
                </div>
              </div>

            </div>

            {/* NORMALIZATION SHOWCASE: Step-by-Step Flow */}
            <div className="glass rounded-2xl p-5 border border-border">
              <h3 className="font-semibold text-foreground flex items-center gap-1.5 border-b border-border/60 pb-2 mb-4">
                <CheckCircle className="h-4.5 w-4.5 text-primary" /> Database Normalization Decomposition (UNF ➔ 3NF)
              </h3>
              
              <div className="space-y-6 text-xs text-foreground leading-normal">
                {/* 1. UNF */}
                <div className="border border-border p-4 rounded-xl bg-card/30">
                  <span className="bg-zinc-800 text-white font-mono px-2 py-0.5 rounded text-[10px] font-bold">1. UNF (Unnormalized Form)</span>
                  <p className="mt-2 text-muted-foreground leading-relaxed">
                    Single flat patient file recording repeating nested array groups representing various ECG signals, different predicted disease codes, and doctor credentials in the same table. Leading to major insert/update anomalies.
                  </p>
                  <div className="overflow-x-auto mt-3 border rounded border-zinc-800/80 bg-zinc-950 font-mono text-[9px] p-2 text-zinc-400">
                    UNF_Patient_Card = [PatientID, Name, Contact, Address, [ECG_ID, BPM, QRS_Signal_Array], [Pred_ID, Disease_Name, Conf], Doctor_Name, Specialty]
                  </div>
                </div>

                {/* 2. 1NF */}
                <div className="border border-border p-4 rounded-xl bg-card/30">
                  <span className="bg-zinc-800 text-white font-mono px-2 py-0.5 rounded text-[10px] font-bold">2. 1NF (First Normal Form)</span>
                  <p className="mt-2 text-muted-foreground">
                    Eliminate all multi-valued repeating groups. Ensure atomic values for each cell (no arrays/embedded tables). The signals array and disease listings are split into distinct flat row rows.
                  </p>
                  <div className="overflow-x-auto mt-3 border rounded border-zinc-800/80 bg-zinc-950 font-mono text-[9px] p-2 text-zinc-400">
                    1NF_Table = [PatientID, Name, Contact, ECG_ID, BPM, QRS_Duration, Pred_ID, Disease_Name, Doctor_Name]
                    <div className="mt-1 text-zinc-500">// Anomalies: Duplicate patient data row-for-row per prediction. Redundant names and addresses.</div>
                  </div>
                </div>

                {/* 3. 2NF */}
                <div className="border border-border p-4 rounded-xl bg-card/30">
                  <span className="bg-zinc-800 text-white font-mono px-2 py-0.5 rounded text-[10px] font-bold">3. 2NF (Second Normal Form)</span>
                  <p className="mt-2 text-muted-foreground">
                    Ensure 1NF first. Then remove all partial functional dependencies. Attributes must depend on the whole composite primary key. We split the database into three separate logical tables: Demographics, Signal records, and Predictions.
                  </p>
                  <div className="grid md:grid-cols-3 gap-3 mt-3">
                    <div className="bg-zinc-950 p-2.5 rounded border border-zinc-850 font-mono text-[9px] text-zinc-400">
                      <strong>patients</strong><br />
                      [patient_id (PK), name, contact, history, doc_name]
                    </div>
                    <div className="bg-zinc-950 p-2.5 rounded border border-zinc-850 font-mono text-[9px] text-zinc-400">
                      <strong>ecg_records</strong><br />
                      [ecg_id (PK), patient_id (FK), BPM, QRS_dur]
                    </div>
                    <div className="bg-zinc-950 p-2.5 rounded border border-zinc-850 font-mono text-[9px] text-zinc-400">
                      <strong>predictions</strong><br />
                      [pred_id (PK), ecg_id (FK), disease]
                    </div>
                  </div>
                </div>

                {/* 4. 3NF */}
                <div className="border border-border p-4 rounded-xl bg-card/30">
                  <span className="bg-primary text-primary-foreground font-mono px-2 py-0.5 rounded text-[10px] font-bold">4. 3NF (Third Normal Form) -- PRODUCTION BASES</span>
                  <p className="mt-2 text-muted-foreground">
                    Ensure 2NF first. Then remove all transitive functional dependencies (non-key fields must not depend on other non-key fields). We split doctors into a dedicated table, and split authentication logins/roles into a separate `users` table so patient records do not carry redundant logins!
                  </p>
                  <div className="bg-zinc-950 p-3 rounded-lg border border-primary/20 font-mono text-[9px] text-[#00ff66] space-y-1.5">
                    <div>✔ users = [user_id (PK), name, email, password_hash, role]</div>
                    <div>✔ patients = [patient_id (PK), user_id (FK), age, gender, blood_group, history]</div>
                    <div>✔ doctors = [doctor_id (PK), user_id (FK), specialization, hospital, experience]</div>
                    <div>✔ ecg_records = [ecg_id (PK), patient_id (FK), heart_rate, qrs_duration, pr_interval]</div>
                    <div>✔ predictions = [prediction_id (PK), ecg_id (FK), patient_id (FK), disease_name]</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Level 0 & Level 1 Data Flow Diagrams (DFD) */}
            <div className="glass rounded-2xl p-5 border border-border">
              <h3 className="font-semibold text-foreground flex items-center gap-1.5 border-b border-border/60 pb-2 mb-4">
                <Activity className="h-4.5 w-4.5 text-primary" /> Data Flow Diagrams (DFD Levels 0 & 1)
              </h3>
              
              <div className="grid md:grid-cols-2 gap-6 text-xs text-foreground">
                <div className="border border-border p-4 rounded-xl bg-card/30">
                  <span className="font-bold text-foreground block mb-2 font-mono border-b border-border/40 pb-1">Level 0: System Context DFD</span>
                  <div className="space-y-3 font-mono text-[10px] leading-relaxed">
                    <div className="flex items-center justify-between">
                      <span className="bg-zinc-900 border border-zinc-700 px-2 py-1 rounded">Patient Entity</span>
                      <span className="text-zinc-500">── ECG File Telemetry ──➔</span>
                      <span className="bg-primary/10 text-primary border border-primary/20 px-2 py-1 rounded font-bold">CardioPredict SaaS</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="bg-zinc-900 border border-zinc-700 px-2 py-1 rounded">Doctor Entity</span>
                      <span className="text-zinc-500">── Annotates History ──➔</span>
                      <span className="bg-primary/10 text-primary border border-primary/20 px-2 py-1 rounded font-bold">CardioPredict SaaS</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="bg-[#00ff66]/10 text-[#00ff66] border border-[#00ff66]/20 px-2 py-1 rounded font-bold">Twilio Gateway</span>
                      <span className="text-zinc-500">⮠ ── emergency arrhythmia text ──</span>
                      <span className="bg-zinc-900 border border-zinc-700 px-2 py-1 rounded">Clinician Staff</span>
                    </div>
                  </div>
                </div>

                <div className="border border-border p-4 rounded-xl bg-card/30">
                  <span className="font-bold text-foreground block mb-2 font-mono border-b border-border/40 pb-1">Level 1: System Process DFD</span>
                  <div className="space-y-2.5 font-mono text-[9px] leading-relaxed">
                    <div className="flex items-center justify-between bg-black/10 dark:bg-black/35 p-1.5 rounded">
                      <span className="text-zinc-500 font-bold">1.0 Ingestion Process</span>
                      <span className="text-primary font-bold">Parse CSV/Image ➔ insert ecg_records</span>
                    </div>
                    <div className="flex items-center justify-between bg-black/10 dark:bg-black/35 p-1.5 rounded">
                      <span className="text-zinc-500 font-bold">2.0 Model Inference</span>
                      <span className="text-primary font-bold">TensorFlow model ➔ insert predictions</span>
                    </div>
                    <div className="flex items-center justify-between bg-black/10 dark:bg-black/35 p-1.5 rounded">
                      <span className="text-zinc-500 font-bold">3.0 Report Compiler</span>
                      <span className="text-primary font-bold">JOIN tables (300) ➔ render print layout</span>
                    </div>
                    <div className="flex items-center justify-between bg-black/10 dark:bg-black/35 p-1.5 rounded">
                      <span className="text-zinc-500 font-bold">4.0 Sys Auditor</span>
                      <span className="text-primary font-bold">Hook actions ➔ insert audit_logs DDL</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

          </div>
        )}
      </div>
    </AppLayout>
  );
}