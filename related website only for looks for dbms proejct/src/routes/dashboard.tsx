import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { 
  Users, 
  HeartPulse, 
  AlertTriangle, 
  Activity, 
  TrendingUp, 
  Brain, 
  ArrowRight, 
  Sparkles, 
  Database,
  ShieldCheck,
  Calendar,
  Layers,
  Smartphone,
  Mail,
  FileSpreadsheet,
  Download,
  CheckCircle,
  FileText,
  Clock,
  Clock3,
  User
} from "lucide-react";
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell, 
  BarChart, 
  Bar, 
  CartesianGrid 
} from "recharts";
import { AppLayout } from "@/components/AppLayout";
import { EcgWave } from "@/components/EcgWave";
import { SqlQueryCard } from "@/components/SqlQueryCard";
import { sqlQueries } from "@/lib/sql-queries";
import { 
  db, 
  type AppRole 
} from "@/lib/db-store";
import { RiskBadge } from "@/components/RiskBadge";
import { toast } from "sonner";

export const Route = createFileRoute("/dashboard")({
  head: () => ({ meta: [{ title: "Dashboard — CardioPredict" }] }),
  component: Dashboard,
});

// Recharts Static Averages
const heartRateTrend = [
  { day: "Mon", avg: 74 },
  { day: "Tue", avg: 78 },
  { day: "Wed", avg: 85 },
  { day: "Thu", avg: 92 },
  { day: "Fri", avg: 88 },
  { day: "Sat", avg: 79 },
  { day: "Sun", avg: 81 },
];

const diseaseDistribution = [
  { name: "Normal", value: 2, color: "#10b981" },
  { name: "Arrhythmia", value: 1, color: "#3b82f6" },
  { name: "Tachycardia", value: 1, color: "#f59e0b" },
];

function Dashboard() {
  const [role, setRole] = useState<AppRole>(db.getRole());
  const [renderCount, setRenderCount] = useState(0);

  // Simulated Integrations States
  const [twilioMockOpen, setTwilioMockOpen] = useState(false);
  const [twilioMessage, setTwilioMessage] = useState("");
  const [googleSheetsOpen, setGoogleSheetsOpen] = useState(false);
  const [mailgunOpen, setMailgunOpen] = useState(false);
  const [mailgunRecipient, setMailgunRecipient] = useState("");
  const [mailgunSubject, setMailgunSubject] = useState("");

  useEffect(() => {
    // Subscribe to DB role updates
    const unsubscribe = db.subscribe(() => {
      setRole(db.getRole());
      setRenderCount((c) => c + 1);
    });
    return () => unsubscribe();
  }, []);

  // SQL logs log count
  db.logQuery("SELECT * FROM patient_dashboard;", "Fetched current portal dashboard metrics");

  // ==========================================
  // PERSONA ACTIONS
  // ==========================================

  // Twilio Simulator Trigger
  const triggerTwilioSMS = (patientName: string, hr: number, condition: string) => {
    const text = `[Twilio Emergency Alert] CRITICAL: Patient ${patientName} registered a highly elevated heart rate of ${hr} BPM (Risk: HIGH). Primary diagnosis flags: ${condition}. Please contact clinical team immediately at 911.`;
    setTwilioMessage(text);
    setTwilioMockOpen(true);
    db.logQuery(
      `INSERT INTO audit_logs (activity, sql_query) VALUES ('Dispatched Twilio Emergency SMS Alert', 'CALL twilio_sms_gateway("+12015550192", "${text.substring(0, 30)}...");');`,
      "Triggered emergency SMS alert via Twilio Connector"
    );
    toast.error("Twilio Emergency SMS Dispatched!");
  };

  // Google Sheets Export simulation
  const exportToGoogleSheets = () => {
    setGoogleSheetsOpen(true);
    db.logQuery(
      `INSERT INTO audit_logs (activity) VALUES ('Synchronized database records with Google Sheets spreadsheet #1EcG98B...');`,
      "Exported DBMS table structures to Google Sheets Connector"
    );
    toast.success("Database synchronized with Google Sheets successfully!");
  };

  // Mailgun Send simulation
  const openMailgunComposer = (recipient: string, name: string, condition: string) => {
    setMailgunRecipient(recipient);
    setMailgunSubject(`Official Clinical Cardiovascular Report - ${name}`);
    setMailgunOpen(true);
  };

  const executeMailgunSend = (e: React.FormEvent) => {
    e.preventDefault();
    setMailgunOpen(false);
    db.logQuery(
      `INSERT INTO audit_logs (activity) VALUES ('Sent diagnostic reports via Mailgun SMTP relay to ${mailgunRecipient}');`,
      "Dispatched patient clinical report via Mailgun SMTP Connector"
    );
    toast.success(`Diagnostic report dispatched successfully to ${mailgunRecipient} via Mailgun!`);
  };

  // Simulated Appointment checkoff
  const completeAppointment = (appointmentId: number) => {
    db.logQuery(
      `UPDATE appointments SET status = 'Completed' WHERE appointment_id = ${appointmentId};`,
      "Doctor completed patient consultation"
    );
    toast.success(`Appointment #${appointmentId} completed successfully!`);
    setRenderCount((c) => c + 1);
  };

  // ==========================================
  // DASHBOARD RENDER LOGIC
  // ==========================================

  return (
    <AppLayout 
      title={`${role} Dashboard Overview`} 
      subtitle={`CardioPredict DBMS Portal · Session: ${db.getCurrentUser().name}`}
    >
      {/* 1. PATIENT DASHBOARD */}
      {role === "Patient" && (
        <div className="space-y-6 animate-fade-in">
          {/* Welcome Patient */}
          <div className="rounded-2xl gradient-hero p-6 text-white relative overflow-hidden shadow-glow">
            <div className="absolute right-0 top-0 h-40 w-40 bg-white/10 rounded-full blur-3xl" />
            <div className="relative flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <span className="bg-white/20 text-white px-2.5 py-1 rounded-full text-xs font-semibold">Patient Account #101</span>
                <h2 className="text-3xl font-bold mt-2">Welcome Back, Rahul Sharma</h2>
                <p className="text-white/80 text-xs mt-1">Your real-time ECG telemetry and AI cardiac profiles are synchronized.</p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => triggerTwilioSMS("Rahul Sharma", 92, "Arrhythmia")}
                  className="bg-red-500 hover:bg-red-650 text-white font-bold text-xs px-4 py-2.5 rounded-lg flex items-center gap-1.5 shadow-lg border border-red-400 cursor-pointer"
                >
                  <Smartphone className="h-4 w-4" /> Trigger Emergency Alert
                </button>
              </div>
            </div>
          </div>

          {/* Grid: Patient Details & Latest Prediction */}
          <div className="grid lg:grid-cols-3 gap-6">
            {/* Demographics Profile Card */}
            <div className="glass rounded-2xl p-5 border border-border flex flex-col justify-between">
              <div>
                <h3 className="font-semibold text-foreground flex items-center gap-2 border-b border-border/60 pb-2 mb-3">
                  <User className="h-4.5 w-4.5 text-primary" /> Relational Demographics (patients table)
                </h3>
                <div className="space-y-3.5 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Patient ID</span>
                    <span className="font-mono text-foreground font-bold">#101</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Age / Gender</span>
                    <span className="text-foreground">45 Yrs / Male</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Blood Group</span>
                    <span className="text-foreground font-bold text-primary">O+</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Contact Node</span>
                    <span className="text-foreground font-mono">9876543210</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground block mb-1">Clinical History</span>
                    <p className="text-xs bg-muted/65 p-2 rounded border border-border text-foreground leading-relaxed">
                      Mild hypertension, father had myocardial infarction (heart attack risk factor).
                    </p>
                  </div>
                </div>
              </div>
              <div className="mt-4 text-[10px] font-mono text-muted-foreground border-t border-border/40 pt-2 bg-black/5 dark:bg-black/25 p-2 rounded">
                SELECT * FROM patients WHERE user_id = 1;
              </div>
            </div>

            {/* AI Diagnostics Card */}
            <div className="glass rounded-2xl p-5 border border-border flex flex-col justify-between lg:col-span-2">
              <div>
                <h3 className="font-semibold text-foreground flex items-center gap-2 border-b border-border/60 pb-2 mb-3">
                  <Brain className="h-4.5 w-4.5 text-primary" /> Active AI Prediction Output
                </h3>
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="space-y-3 bg-muted/40 p-4 rounded-xl border border-border">
                    <div className="text-xs text-muted-foreground">Primary Diagnosis</div>
                    <div className="text-xl font-bold text-foreground flex items-center gap-1.5">
                      Possible Arrhythmia <Sparkles className="h-4 w-4 text-primary animate-pulse" />
                    </div>
                    <div className="flex justify-between items-center mt-4">
                      <div>
                        <div className="text-xs text-muted-foreground">AI Confidence</div>
                        <div className="text-lg font-mono text-primary font-bold">94.5%</div>
                      </div>
                      <RiskBadge level="High" />
                    </div>
                    <div className="h-1.5 w-full bg-muted rounded-full overflow-hidden mt-2">
                      <div className="h-full gradient-primary" style={{ width: "94.5%" }} />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="text-xs text-muted-foreground font-semibold">Recommended Precautions</div>
                    <p className="text-xs text-foreground leading-relaxed bg-primary/5 p-3 rounded-lg border border-primary/20">
                      "Avoid central nervous stimulants (caffeine, nicotine). Schedule regular cardiology ECG review. Daily vitals log maintenance advised."
                    </p>
                    <div className="pt-2 flex gap-2">
                      <button
                        onClick={() => openMailgunComposer("rahul@gmail.com", "Rahul Sharma", "Arrhythmia")}
                        className="flex-1 bg-card hover:bg-muted text-foreground border border-border text-[11px] font-semibold py-2 px-3 rounded-lg flex items-center justify-center gap-1 cursor-pointer"
                      >
                        <Mail className="h-3.5 w-3.5 text-primary" /> Email Report
                      </button>
                      <button
                        onClick={() => toast.success("PDF clinical report generated! Click Reports to download.")}
                        className="flex-1 gradient-primary text-primary-foreground text-[11px] font-semibold py-2 px-3 rounded-lg flex items-center justify-center gap-1 shadow cursor-pointer"
                      >
                        <Download className="h-3.5 w-3.5" /> Download Report
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              <div className="mt-4 text-[10px] font-mono text-muted-foreground border-t border-border/40 pt-2 bg-black/5 dark:bg-black/25 p-2 rounded">
                SELECT * FROM predictions WHERE patient_id = 101 ORDER BY predicted_at DESC LIMIT 1;
              </div>
            </div>
          </div>

          {/* ECG Telemetry Wave */}
          <div className="glass rounded-2xl p-5 border border-border">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-semibold text-foreground flex items-center gap-1.5">
                  <Activity className="h-4.5 w-4.5 text-primary animate-pulse" /> Live ECG Waveform Telemetry
                </h3>
                <p className="text-xs text-muted-foreground">Lead II · Sinus rhythm synced from historical ECG record #1</p>
              </div>
              <div className="text-right">
                <span className="text-xs font-mono text-primary bg-primary/10 border border-primary/20 px-2 py-1 rounded font-bold">92 BPM</span>
              </div>
            </div>
            <EcgWave height={160} hr={92} />
          </div>

          {/* Historical ECG Record Logs */}
          <div className="glass rounded-2xl p-5 border border-border">
            <h3 className="font-semibold text-foreground mb-3">ECG Database Logs (ecg_records table)</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="text-muted-foreground uppercase border-b border-border">
                  <tr>
                    <th className="py-2.5">Record ID</th>
                    <th>Uploaded At</th>
                    <th>Heart Rate (BPM)</th>
                    <th>QRS Interval (s)</th>
                    <th>PR Interval (s)</th>
                    <th>QT Interval (s)</th>
                    <th>Upload Type</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-border/50">
                    <td className="py-2.5 font-mono font-bold text-primary">#1</td>
                    <td className="font-mono">2025-05-01 09:30:00</td>
                    <td className="font-bold">92</td>
                    <td className="font-mono">0.11s</td>
                    <td className="font-mono">0.18s</td>
                    <td className="font-mono">0.42s</td>
                    <td><span className="bg-primary/10 text-primary border border-primary/20 px-1.5 py-0.5 rounded text-[10px] uppercase font-bold">IMAGE</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* 2. DOCTOR DASHBOARD */}
      {role === "Doctor" && (
        <div className="space-y-6 animate-fade-in">
          {/* Welcome Doctor */}
          <div className="rounded-2xl gradient-hero p-6 text-white relative overflow-hidden shadow-glow">
            <div className="absolute right-0 top-0 h-40 w-40 bg-white/10 rounded-full blur-3xl" />
            <div className="relative flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <span className="bg-white/20 text-white px-2.5 py-1 rounded-full text-xs font-semibold">Doctor Profile: 201</span>
                <h2 className="text-3xl font-bold mt-2">Welcome Back, Dr. Arjun Mehta</h2>
                <p className="text-white/80 text-xs mt-1">Fortis Cardiology Department · Specialized Electrophysiology</p>
              </div>
              <div className="bg-card/25 border border-white/20 p-3 rounded-xl backdrop-blur-sm text-xs space-y-1">
                <div>Total Active Patients: <strong className="text-[#00ff66]">{db.patientsTable.length}</strong></div>
                <div>Avg Heart Rate: <strong>88.0 BPM</strong></div>
              </div>
            </div>
          </div>

          {/* Hospital Stats Grid */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { label: "Assigned Patients", value: db.patientsTable.length, icon: Users, sql: "SELECT COUNT(*) FROM patients" },
              { label: "High Risk Detected", value: db.predictionsTable.filter(p => p.risk_level === "High").length, icon: AlertTriangle, sql: "WHERE risk_level = 'High'", accent: true },
              { label: "Mean Cardiac Rate", value: "88.0 BPM", icon: HeartPulse, sql: "SELECT AVG(heart_rate)" },
              { label: "AI Predictions Run", value: db.predictionsTable.length, icon: Brain, sql: "SELECT COUNT(*) FROM predictions" }
            ].map((s, i) => (
              <div key={i} className={`glass rounded-2xl p-5 border relative overflow-hidden ${s.accent ? "border-destructive/40 bg-destructive/5" : "border-border"}`}>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground font-semibold">{s.label}</span>
                  <s.icon className={`h-4.5 w-4.5 ${s.accent ? "text-destructive animate-bounce" : "text-primary"}`} />
                </div>
                <div className="mt-3 text-2xl font-bold text-foreground">{s.value}</div>
                <div className="mt-2 text-[9px] font-mono text-muted-foreground truncate bg-muted/60 p-1 rounded border border-border/50">{s.sql}</div>
              </div>
            ))}
          </div>

          {/* Dynamic Recharts Charts */}
          <div className="grid lg:grid-cols-3 gap-6">
            <div className="glass rounded-2xl p-5 border border-border lg:col-span-2">
              <h3 className="font-semibold text-foreground flex items-center gap-1.5"><TrendingUp className="h-4.5 w-4.5 text-primary" /> Daily Cardiovascular Averages (7d)</h3>
              <div className="h-[200px] mt-4">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={heartRateTrend}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                    <XAxis dataKey="day" stroke="#888888" fontSize={11} />
                    <YAxis stroke="#888888" fontSize={11} />
                    <Tooltip contentStyle={{ background: "var(--card)", border: "1px solid var(--border)" }} />
                    <Line type="monotone" dataKey="avg" stroke="var(--primary)" strokeWidth={3} dot={{ r: 4, fill: "var(--primary)" }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="glass rounded-2xl p-5 border border-border">
              <h3 className="font-semibold text-foreground mb-1">Clinical Diagnoses</h3>
              <p className="text-xs text-muted-foreground">Distribution from predictions table</p>
              <div className="h-[150px] flex items-center justify-center mt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={diseaseDistribution} dataKey="value" nameKey="name" innerRadius={40} outerRadius={60} paddingAngle={4}>
                      {diseaseDistribution.map((d, i) => <Cell key={i} fill={d.color} />)}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex justify-center gap-4 text-xs mt-2 flex-wrap">
                {diseaseDistribution.map((d, i) => (
                  <span key={i} className="flex items-center gap-1"><span className="h-2 w-2 rounded-full" style={{ background: d.color }} /> {d.name} ({d.value})</span>
                ))}
              </div>
            </div>
          </div>

          {/* Clinic Appointment schedule */}
          <div className="glass rounded-2xl p-5 border border-border">
            <div className="flex items-center justify-between mb-4 border-b border-border/60 pb-2">
              <div>
                <h3 className="font-semibold text-foreground flex items-center gap-1.5">
                  <Calendar className="h-4.5 w-4.5 text-primary" /> Clinic Appointment Schedule (appointments table)
                </h3>
                <p className="text-xs text-muted-foreground">Seeded scheduled patient consults with doctor_id #201</p>
              </div>
              <span className="text-[10px] font-mono bg-black/10 dark:bg-black/35 p-1 rounded text-muted-foreground">SELECT * FROM appointments;</span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="text-muted-foreground uppercase border-b border-border">
                  <tr>
                    <th className="py-2.5">ID</th>
                    <th>Patient Name</th>
                    <th>Consultation Date</th>
                    <th>Clinical Status</th>
                    <th className="text-right">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {db.appointmentsTable.map((a) => {
                    const pat = db.patientsTable.find(p => p.patient_id === a.patient_id);
                    return (
                      <tr key={a.appointment_id} className="border-b border-border/50 hover:bg-muted/20">
                        <td className="py-2.5 font-mono font-bold">#{a.appointment_id}</td>
                        <td className="font-semibold text-foreground">{pat ? pat.full_name : "General Patient"}</td>
                        <td className="font-mono">{a.appointment_date}</td>
                        <td>
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                            a.status === "Completed" ? "bg-emerald-500/10 text-emerald-500 border-emerald-500/20" :
                            a.status === "Scheduled" ? "bg-blue-500/10 text-blue-500 border-blue-500/20" :
                            "bg-amber-500/10 text-amber-500 border-amber-500/20"
                          }`}>
                            {a.status}
                          </span>
                        </td>
                        <td className="text-right">
                          {a.status !== "Completed" && (
                            <button
                              onClick={() => completeAppointment(a.appointment_id)}
                              className="bg-primary hover:bg-primary/95 text-primary-foreground font-semibold px-2.5 py-1 rounded text-[10px] shadow border border-primary/20 cursor-pointer"
                            >
                              Complete Consult
                            </button>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* 3. ADMIN DASHBOARD */}
      {role === "Admin" && (
        <div className="space-y-6 animate-fade-in">
          {/* Welcome Admin */}
          <div className="rounded-2xl gradient-hero p-6 text-white relative overflow-hidden shadow-glow">
            <div className="absolute right-0 top-0 h-40 w-40 bg-white/10 rounded-full blur-3xl" />
            <div className="relative flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <span className="bg-white/20 text-white px-2.5 py-1 rounded-full text-xs font-semibold">Administrator Account</span>
                <h2 className="text-3xl font-bold mt-2">CardioPredict DBMS Dashboard</h2>
                <p className="text-white/80 text-xs mt-1">Manage users, audit query registers, and monitor connectors.</p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={exportToGoogleSheets}
                  className="bg-green-600 hover:bg-green-650 text-white font-bold text-xs px-4 py-2.5 rounded-lg flex items-center gap-1.5 shadow-lg border border-green-500 cursor-pointer animate-pulse"
                >
                  <FileSpreadsheet className="h-4 w-4" /> Sync Google Sheets
                </button>
              </div>
            </div>
          </div>

          {/* Database Normalized Tables Grid */}
          <div>
            <h3 className="font-semibold text-foreground mb-3 flex items-center gap-1.5"><Layers className="h-4.5 w-4.5 text-primary" /> Active Database Schema Tables (PostgreSQL Schema)</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
              {[
                { name: "users", count: db.usersTable.length, color: "border-blue-500/25 bg-blue-500/5 text-blue-500" },
                { name: "patients", count: db.patientsTable.length, color: "border-green-500/25 bg-green-500/5 text-green-500" },
                { name: "doctors", count: db.doctorsTable.length, color: "border-amber-500/25 bg-amber-500/5 text-amber-500" },
                { name: "ecg_records", count: db.ecgRecordsTable.length, color: "border-red-500/25 bg-red-500/5 text-red-500" },
                { name: "predictions", count: db.predictionsTable.length, color: "border-purple-500/25 bg-purple-500/5 text-purple-500" },
                { name: "reports", count: db.reportsTable.length, color: "border-cyan-500/25 bg-cyan-500/5 text-cyan-500" },
                { name: "appointments", count: db.appointmentsTable.length, color: "border-indigo-500/25 bg-indigo-500/5 text-indigo-500" },
                { name: "audit_logs", count: db.auditLogsTable.length, color: "border-pink-500/25 bg-pink-500/5 text-pink-500" },
              ].map((t, i) => (
                <div key={i} className={`glass rounded-xl p-3 border text-center ${t.color}`}>
                  <div className="text-[10px] uppercase font-bold opacity-60 tracking-wider font-mono">{t.name}</div>
                  <div className="text-2xl font-bold mt-1 text-foreground">{t.count}</div>
                  <div className="text-[9px] opacity-70 mt-0.5">rows</div>
                </div>
              ))}
            </div>
          </div>

          {/* Connectors Panel */}
          <div className="glass rounded-2xl p-5 border border-border">
            <div className="border-b border-border/60 pb-2 mb-4">
              <h3 className="font-semibold text-foreground flex items-center gap-1.5"><Sparkles className="h-4.5 w-4.5 text-primary" /> Connectors & External Integrations Hub</h3>
              <p className="text-xs text-muted-foreground">Monitor and trigger simulated operations across third-party API configurations.</p>
            </div>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Firebase Card */}
              <div className="p-4 rounded-xl border border-border bg-muted/20 relative overflow-hidden flex flex-col justify-between h-40">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-foreground">Firebase Integration</span>
                    <span className="flex h-2 w-2 relative">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                    </span>
                  </div>
                  <p className="text-[11px] text-muted-foreground">Session Token Handshakes, Auth State, Realtime Database Notifications.</p>
                </div>
                <div className="text-[10px] bg-black/10 dark:bg-black/35 p-1 rounded font-mono text-xs overflow-hidden truncate">
                  Key: ...Ipg (LOADED)
                </div>
              </div>

              {/* Google Sheets Card */}
              <div className="p-4 rounded-xl border border-border bg-muted/20 relative overflow-hidden flex flex-col justify-between h-40">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-foreground">Google Sheets API</span>
                    <span className="flex h-2 w-2 relative">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                    </span>
                  </div>
                  <p className="text-[11px] text-muted-foreground">Synchronize patients statistics, queries indexes, predictions rates into live sheet.</p>
                </div>
                <button
                  onClick={exportToGoogleSheets}
                  className="w-full text-center bg-green-600 hover:bg-green-650 text-white font-bold text-[10px] py-1.5 rounded cursor-pointer transition-colors"
                >
                  Sync Spreadsheet
                </button>
              </div>

              {/* Mailgun SMTP Card */}
              <div className="p-4 rounded-xl border border-border bg-muted/20 relative overflow-hidden flex flex-col justify-between h-40">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-foreground">Mailgun SMTP Relay</span>
                    <span className="flex h-2 w-2 relative">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                    </span>
                  </div>
                  <p className="text-[11px] text-muted-foreground">Send digital PDF clinical reports, warning alerts via automated transactional emails.</p>
                </div>
                <button
                  onClick={() => openMailgunComposer("rahul@gmail.com", "Rahul Sharma", "Arrhythmia")}
                  className="w-full text-center bg-blue-600 hover:bg-blue-650 text-white font-bold text-[10px] py-1.5 rounded cursor-pointer transition-colors"
                >
                  Send Automated Mail
                </button>
              </div>

              {/* Twilio Alert Card */}
              <div className="p-4 rounded-xl border border-border bg-muted/20 relative overflow-hidden flex flex-col justify-between h-40">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-foreground">Twilio SMS Alert Gateway</span>
                    <span className="flex h-2 w-2 relative">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                    </span>
                  </div>
                  <p className="text-[11px] text-muted-foreground">Triggers emergency clinical texts to primary emergency contacts when heart rates exceeds critical threshold.</p>
                </div>
                <button
                  onClick={() => triggerTwilioSMS("Vikram Singh", 110, "Sinus Tachycardia")}
                  className="w-full text-center bg-red-650 hover:bg-red-700 text-white font-bold text-[10px] py-1.5 rounded cursor-pointer transition-colors"
                >
                  Simulate SMS Send
                </button>
              </div>
            </div>
          </div>

          {/* Database System Audit Logs */}
          <div className="glass rounded-2xl p-5 border border-border">
            <div className="flex items-center justify-between mb-3 border-b border-border/60 pb-2">
              <div>
                <h3 className="font-semibold text-foreground flex items-center gap-1.5">
                  <Database className="h-4.5 w-4.5 text-primary" /> DBMS Engine Audit Logs (audit_logs table)
                </h3>
                <p className="text-xs text-muted-foreground">Recent transactions logged globally across CardioPredict server framework</p>
              </div>
              <Link to="/reports" className="text-xs text-primary font-semibold flex items-center gap-0.5 hover:gap-1.5 transition-all">View Full Logs <ArrowRight className="h-3 w-3" /></Link>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="text-muted-foreground uppercase border-b border-border">
                  <tr>
                    <th className="py-2">Log ID</th>
                    <th>Timestamp</th>
                    <th>User</th>
                    <th>Activity Summary</th>
                    <th>SQL Command Sample</th>
                    <th>Execution Time</th>
                  </tr>
                </thead>
                <tbody>
                  {db.auditLogsTable.slice(0, 4).map((log, i) => (
                    <tr key={i} className="border-b border-border/50 hover:bg-muted/10">
                      <td className="py-2.5 font-mono text-zinc-500">#{log.log_id}</td>
                      <td className="font-mono">{log.timestamp}</td>
                      <td><span className="bg-primary/10 text-primary border border-primary/20 px-1.5 py-0.5 rounded text-[10px] font-bold">{log.role}</span></td>
                      <td className="text-foreground">{log.activity}</td>
                      <td className="font-mono text-zinc-400 max-w-[200px] truncate">{log.sql_query}</td>
                      <td className="font-mono text-zinc-500">{log.execution_time_ms} ms</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ==========================================
      MODALS & SIMULATORS (REALTIME DEMO WOW FACTOR!)
      ========================================== */}

      {/* 1. TWILIO MOCK SMARTPHONE POPUP */}
      {twilioMockOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4" onClick={() => setTwilioMockOpen(false)}>
          <div onClick={(e) => e.stopPropagation()} className="w-full max-w-sm bg-zinc-900 border-4 border-zinc-700 rounded-[40px] p-6 shadow-2xl relative overflow-hidden animate-scale-in text-white h-[600px] flex flex-col justify-between">
            {/* Phone notch */}
            <div className="absolute top-2 left-1/2 -translate-x-1/2 h-5 w-32 bg-zinc-750 rounded-full flex items-center justify-center">
              <span className="h-1.5 w-1.5 bg-black rounded-full mr-2" />
              <span className="h-1 w-8 bg-zinc-900 rounded-full" />
            </div>

            {/* Status bar */}
            <div className="flex justify-between items-center text-[10px] text-zinc-400 mt-2 px-2">
              <span>9:41 AM</span>
              <div className="flex items-center gap-1.5">
                <span>5G</span>
                <span className="h-3 w-5 bg-zinc-600 rounded-sm border border-zinc-400 relative"><span className="absolute left-0 top-0 bottom-0 right-1 bg-white" /></span>
              </div>
            </div>

            {/* Screen Content */}
            <div className="flex-1 flex flex-col justify-center px-4 py-8">
              <div className="bg-zinc-800 border border-red-500/40 p-4 rounded-2xl space-y-3 shadow-glow relative animate-bounce">
                <div className="flex items-center gap-2 text-red-500 border-b border-zinc-700 pb-2">
                  <Smartphone className="h-5 w-5 text-red-500 animate-pulse" />
                  <span className="text-xs font-bold font-mono">TWILIO EMERGENCY SMS GATEWAY</span>
                </div>
                <div className="text-[11px] font-mono text-zinc-200 leading-relaxed font-bold break-words">
                  {twilioMessage}
                </div>
                <div className="text-[9px] text-zinc-500 text-right">
                  Sent via 127.0.0.1:TwilioAPI
                </div>
              </div>
            </div>

            {/* Bottom explanation */}
            <div className="text-center space-y-2">
              <p className="text-[10px] text-zinc-400 leading-normal">
                This is a high-fidelity visual simulator demonstrating the Twilio SMS emergency alert trigger. The audit logs capture the corresponding background SQL logs.
              </p>
              <button
                onClick={() => setTwilioMockOpen(false)}
                className="w-full h-10 rounded-xl bg-zinc-800 hover:bg-zinc-750 font-bold text-xs cursor-pointer border border-zinc-700"
              >
                Close SMS Simulator
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 2. GOOGLE SHEETS LIVE MOCKUP OVERLAY */}
      {googleSheetsOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4" onClick={() => setGoogleSheetsOpen(false)}>
          <div onClick={(e) => e.stopPropagation()} className="w-full max-w-4xl bg-white border border-zinc-300 rounded-xl shadow-2xl overflow-hidden flex flex-col h-[500px] animate-scale-in text-black">
            {/* Sheets Header */}
            <div className="bg-[#0f9d58] p-4 text-white flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileSpreadsheet className="h-6 w-6 text-white" />
                <div>
                  <h3 className="font-bold text-sm">Google Sheets Live Analytics Sync</h3>
                  <div className="text-[10px] text-white/80">File: CardioPredict_DBMS_Analytics_Export.xlsx</div>
                </div>
              </div>
              <button
                onClick={() => setGoogleSheetsOpen(false)}
                className="text-white hover:bg-white/10 p-1 rounded cursor-pointer"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Sheets Table Grid */}
            <div className="flex-1 overflow-auto p-4 bg-zinc-50 font-mono text-[11px]">
              <div className="bg-white border border-zinc-200 shadow-sm rounded-lg overflow-hidden">
                <table className="w-full border-collapse">
                  <thead>
                    <tr className="bg-zinc-100 border-b border-zinc-200">
                      <th className="border-r border-zinc-200 p-2 text-center text-zinc-500 w-10">#</th>
                      <th className="border-r border-zinc-200 p-2 text-left">A: PATIENT_NAME</th>
                      <th className="border-r border-zinc-200 p-2 text-left">B: AGE_GENDER</th>
                      <th className="border-r border-zinc-200 p-2 text-left">C: HEART_RATE_BPM</th>
                      <th className="border-r border-zinc-200 p-2 text-left">D: CLINICAL_DIAGNOSIS</th>
                      <th className="p-2 text-left">E: RISK_INDEX</th>
                    </tr>
                  </thead>
                  <tbody>
                    {patientsTable.map((p, i) => {
                      const e = ecgRecordsTable.find(rec => rec.patient_id === p.patient_id);
                      const pr = predictionsTable.find(pred => pred.patient_id === p.patient_id);
                      return (
                        <tr key={i} className="border-b border-zinc-200 hover:bg-zinc-50">
                          <td className="border-r border-zinc-200 p-2 text-center bg-zinc-50 text-zinc-400 font-bold">{i + 1}</td>
                          <td className="border-r border-zinc-200 p-2 text-foreground font-semibold">{p.full_name}</td>
                          <td className="border-r border-zinc-200 p-2">{p.age} Yrs / {p.gender}</td>
                          <td className="border-r border-zinc-200 p-2 text-[#0f9d58] font-bold">{e ? e.heart_rate : 80} BPM</td>
                          <td className="border-r border-zinc-200 p-2">{pr ? pr.disease_name : "Normal"}</td>
                          <td className="p-2">
                            <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                              pr?.risk_level === "High" ? "bg-red-100 text-red-700" : "bg-green-100 text-green-700"
                            }`}>
                              {pr ? pr.risk_level : "Low"}
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Sheets Footer status */}
            <div className="bg-zinc-100 p-3 flex justify-between items-center text-xs border-t border-zinc-200 text-zinc-600">
              <span className="flex items-center gap-1"><CheckCircle className="h-4 w-4 text-[#0f9d58]" /> Spreadsheet up-to-date and synced.</span>
              <button
                onClick={() => setGoogleSheetsOpen(false)}
                className="bg-[#0f9d58] hover:bg-[#0b8043] text-white font-semibold py-1.5 px-4 rounded cursor-pointer transition-colors"
              >
                Close Sheets Viewer
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 3. MAILGUN SMTP COMPOSER POPUP */}
      {mailgunOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4" onClick={() => setMailgunOpen(false)}>
          <form onSubmit={executeMailgunSend} onClick={(e) => e.stopPropagation()} className="w-full max-w-lg bg-zinc-950 border border-zinc-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col h-[420px] animate-scale-in text-white">
            {/* Mailgun Header */}
            <div className="bg-[#e24e42] p-4 text-white flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Mail className="h-5 w-5" />
                <div>
                  <h3 className="font-bold text-sm">Mailgun SMTP Email Relay Gateway</h3>
                  <div className="text-[10px] text-white/80">API Relay Sandbox Node</div>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setMailgunOpen(false)}
                className="text-white hover:bg-white/10 p-1 rounded cursor-pointer"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Composer form fields */}
            <div className="flex-1 p-5 space-y-3.5 overflow-y-auto">
              <div>
                <label className="text-[10px] font-bold text-zinc-400 block mb-1">RECIPIENT EMAIL (TO:)</label>
                <input
                  type="email"
                  value={mailgunRecipient}
                  onChange={(e) => setMailgunRecipient(e.target.value)}
                  className="w-full h-10 px-3 bg-zinc-900 border border-zinc-800 rounded-lg text-xs text-white focus:outline-none focus:border-red-500"
                  required
                />
              </div>
              
              <div>
                <label className="text-[10px] font-bold text-zinc-400 block mb-1">SUBJECT</label>
                <input
                  type="text"
                  value={mailgunSubject}
                  onChange={(e) => setMailgunSubject(e.target.value)}
                  className="w-full h-10 px-3 bg-zinc-900 border border-zinc-800 rounded-lg text-xs text-white focus:outline-none focus:border-red-500"
                  required
                />
              </div>

              <div className="p-3.5 bg-zinc-900 rounded-lg border border-zinc-800/80 text-[11px] font-mono leading-relaxed space-y-1.5">
                <div className="text-zinc-500 font-bold border-b border-zinc-800 pb-1 flex items-center justify-between">
                  <span>AT_ATTACHMENT: clinical_report_101.pdf</span>
                  <span>(Generated)</span>
                </div>
                <p>Hello Rahul Sharma,</p>
                <p>Please find attached your official CardioPredict clinical cardiovascular diagnosis and ECG summary records. Details:</p>
                <ul className="list-disc pl-4 space-y-0.5">
                  <li>Telemetry Heart Rate: 92 BPM</li>
                  <li>ECG Conduction Index: QRS: 0.11s, PR: 0.18s</li>
                  <li>AI Diagnostic Code: arr_pred_Arrhythmia (High)</li>
                </ul>
              </div>
            </div>

            {/* Send dispatch bar */}
            <div className="bg-zinc-900 p-3.5 flex justify-between items-center text-xs border-t border-zinc-850">
              <span className="text-zinc-500 text-[10px]">Secure Mailgun SMTP Socket</span>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setMailgunOpen(false)}
                  className="px-4 py-2 rounded-lg text-zinc-400 hover:bg-zinc-800 cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="bg-[#e24e42] hover:bg-[#c93c31] text-white font-bold px-4 py-2 rounded-lg cursor-pointer transition-colors shadow"
                >
                  Relay Outgoing Email
                </button>
              </div>
            </div>
          </form>
        </div>
      )}
    </AppLayout>
  );
}

// Reusable X close component for modals
function X(props: any) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M18 6 6 18" />
      <path d="m6 6 12 12" />
    </svg>
  );
}