import { createFileRoute, Link } from "@tanstack/react-router";
import { Activity, Brain, Database, HeartPulse, ShieldCheck, ArrowRight, Sparkles } from "lucide-react";
import { EcgWave } from "@/components/EcgWave";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "CardioPredict — ECG Based Heart Disease Prediction System" },
      { name: "description", content: "AI-powered ECG analysis with full DBMS integration. View, run, and explore live SQL queries on a medical-grade dashboard." },
    ],
  }),
  component: Landing,
});

function Landing() {
  return (
    <div className="min-h-screen bg-background overflow-hidden">
      <header className="px-6 md:px-10 py-5 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <div className="h-9 w-9 rounded-xl gradient-primary flex items-center justify-center shadow-glow animate-ecg-pulse">
            <Activity className="h-5 w-5 text-primary-foreground" />
          </div>
          <div>
            <div className="font-bold text-foreground leading-tight">CardioPredict</div>
            <div className="text-[10px] uppercase tracking-wider text-muted-foreground">ECG AI System</div>
          </div>
        </Link>
        <nav className="hidden md:flex items-center gap-6 text-sm text-muted-foreground">
          <a href="#features" className="hover:text-foreground transition-colors">Features</a>
          <a href="#dbms" className="hover:text-foreground transition-colors">DBMS</a>
          <Link to="/sql-queries" className="hover:text-foreground transition-colors">SQL Queries</Link>
        </nav>
        <div className="flex items-center gap-2">
          <Link to="/login" className="text-sm text-foreground hover:text-primary px-3 py-2 transition-colors">Login</Link>
          <Link to="/dashboard" className="inline-flex items-center gap-1.5 gradient-primary text-primary-foreground text-sm font-medium px-4 py-2 rounded-lg shadow-glow hover:opacity-95">
            Open Dashboard <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>
      </header>

      <section className="relative px-6 md:px-10 pt-10 pb-20">
        <div className="absolute inset-0 -z-10 opacity-30 dark:opacity-20">
          <div className="absolute top-20 left-10 h-72 w-72 rounded-full bg-primary/30 blur-3xl" />
          <div className="absolute bottom-0 right-10 h-72 w-72 rounded-full bg-accent/30 blur-3xl" />
        </div>
        <div className="max-w-5xl mx-auto text-center">
          <span className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1 rounded-full glass">
            <Sparkles className="h-3 w-3 text-primary" /> DBMS Mini Project · Full Stack Demo
          </span>
          <h1 className="mt-5 text-4xl md:text-6xl font-bold tracking-tight text-foreground leading-[1.05]">
            ECG-Based Heart Disease<br />
            <span className="text-gradient-hero">Prediction System</span>
          </h1>
          <p className="mt-5 text-lg text-muted-foreground max-w-2xl mx-auto">
            A complete healthcare platform with patient records, ECG analytics, AI predictions and a live <strong className="text-foreground">MySQL query playground</strong> showcasing every database operation on the dashboard.
          </p>
          <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
            <Link to="/dashboard" className="inline-flex items-center gap-2 gradient-primary text-primary-foreground font-medium px-6 py-3 rounded-xl shadow-glow hover:opacity-95">
              Launch Dashboard <ArrowRight className="h-4 w-4" />
            </Link>
            <Link to="/sql-queries" className="inline-flex items-center gap-2 glass text-foreground font-medium px-6 py-3 rounded-xl hover:bg-card">
              <Database className="h-4 w-4" /> Browse SQL Queries
            </Link>
          </div>

          <div className="mt-14 glass rounded-3xl p-4 md:p-6">
            <div className="flex items-center justify-between mb-2 px-2">
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <span className="h-2 w-2 rounded-full bg-success animate-pulse" /> Live ECG · Lead II
              </div>
              <div className="text-xs font-mono text-primary">HR 84 BPM</div>
            </div>
            <EcgWave height={140} hr={84} />
          </div>
        </div>
      </section>

      <section id="features" className="px-6 md:px-10 py-16 bg-card/30">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-foreground">Built for Healthcare Analytics</h2>
            <p className="mt-2 text-muted-foreground">Twelve modules backed by a normalized MySQL schema.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-5">
            {[
              { icon: HeartPulse, title: "ECG Upload & Storage", text: "Capture heart rate, QRS, PR, and QT intervals for every patient." },
              { icon: Brain, title: "AI Disease Prediction", text: "Confidence-scored predictions with risk-level classification." },
              { icon: Database, title: "Live SQL Playground", text: "Run every CREATE, INSERT, JOIN and VIEW from the dashboard." },
              { icon: ShieldCheck, title: "Role-Based Auth", text: "JWT-style admin/doctor login backed by the users table." },
              { icon: Activity, title: "Realtime Analytics", text: "Heart rate trends, disease distribution, high-risk alerts." },
              { icon: Sparkles, title: "Reports & Exports", text: "Three-table joins produce complete patient reports." },
            ].map((f) => (
              <div key={f.title} className="glass rounded-2xl p-6 hover:shadow-glow transition-shadow">
                <div className="h-10 w-10 rounded-xl gradient-primary flex items-center justify-center mb-4">
                  <f.icon className="h-5 w-5 text-primary-foreground" />
                </div>
                <h3 className="font-semibold text-foreground">{f.title}</h3>
                <p className="text-sm text-muted-foreground mt-1.5">{f.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="dbms" className="px-6 md:px-10 py-16">
        <div className="max-w-6xl mx-auto grid md:grid-cols-2 gap-10 items-center">
          <div>
            <h2 className="text-3xl font-bold text-foreground">Every SQL operation, on the dashboard</h2>
            <p className="mt-3 text-muted-foreground">
              This DBMS mini project showcases <strong className="text-foreground">26+ MySQL queries</strong> — DDL, DML, JOINs, aggregates, views and analytics — that you can run live and inspect the result set in-page.
            </p>
            <ul className="mt-5 space-y-2 text-sm">
              {["CREATE / INSERT / UPDATE / DELETE", "Multi-table JOINs (patients · ecg · predictions)", "Aggregates: COUNT, AVG", "VIEW creation & queries", "Pattern search with LIKE", "Risk-level filtering for alerts"].map((t) => (
                <li key={t} className="flex items-center gap-2 text-muted-foreground"><span className="h-1.5 w-1.5 rounded-full bg-primary" /> {t}</li>
              ))}
            </ul>
            <Link to="/sql-queries" className="mt-6 inline-flex items-center gap-2 text-primary font-medium hover:gap-3 transition-all">
              Open SQL playground <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
          <div className="glass rounded-2xl p-5 font-mono text-xs">
            <div className="text-muted-foreground mb-2">-- Three-table JOIN</div>
            <pre className="text-foreground/90 whitespace-pre-wrap">{`SELECT p.full_name, e.heart_rate,
       pr.disease_prediction,
       pr.risk_level
FROM patients p
JOIN ecg_records e
  ON p.patient_id = e.patient_id
JOIN predictions pr
  ON e.ecg_id = pr.ecg_id;`}</pre>
          </div>
        </div>
      </section>

      <footer className="border-t border-border px-6 md:px-10 py-8 text-center text-xs text-muted-foreground">
        © 2026 CardioPredict · DBMS Mini Project · Built with React + TanStack Start + MySQL
      </footer>
    </div>
  );
}
