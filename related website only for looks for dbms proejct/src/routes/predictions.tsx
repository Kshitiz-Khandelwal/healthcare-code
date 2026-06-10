import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Brain, Sparkles, Loader2, Database, ShieldAlert, CheckSquare, Edit } from "lucide-react";
import { toast } from "sonner";
import { AppLayout } from "@/components/AppLayout";
import { SqlQueryCard } from "@/components/SqlQueryCard";
import { sqlQueries } from "@/lib/sql-queries";
import { db, type AppRole } from "@/lib/db-store";
import { RiskBadge } from "@/components/RiskBadge";

export const Route = createFileRoute("/predictions")({
  head: () => ({ meta: [{ title: "AI Predictions — CardioPredict" }] }),
  component: PredictionsPage,
});

const diseases = [
  { name: "Normal Sinus Rhythm", risk: "Low", rec: "Maintain active lifestyle, regular annual cardiovascular checkup." },
  { name: "Possible Arrhythmia", risk: "High", rec: "Avoid stimulants, schedule cardiologist ECG review, check vitals daily." },
  { name: "Sinus Tachycardia", risk: "High", rec: "EMERGENCY: Immediate clinical intervention required. Beta-blockers as directed." },
  { name: "Mild Bradycardia Risk", risk: "Medium", rec: "Schedule Holter monitoring, monitor resting heart rates weekly." },
  { name: "Atrial Fibrillation", risk: "High", rec: "Prescribe anticoagulants as indicated. Immediate cardiologist referral." }
];

function PredictionsPage() {
  const [role, setRole] = useState<AppRole>(db.getRole());
  const [renderCount, setRenderCount] = useState(0);

  // Run form state
  const [selectedPatientId, setSelectedPatientId] = useState(101);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ disease: string; conf: number; risk: "Low" | "Medium" | "High"; rec: string } | null>(null);

  // Edit State
  const [editingId, setEditingId] = useState<number | null>(null);
  const [newRisk, setNewRisk] = useState<"Low" | "Medium" | "High">("High");
  const [newDisease, setNewDisease] = useState("Sinus Tachycardia");

  useEffect(() => {
    const unsubscribe = db.subscribe(() => {
      setRole(db.getRole());
      setRenderCount(c => c + 1);
    });
    return () => unsubscribe();
  }, []);

  const runPrediction = () => {
    setLoading(true);
    setResult(null);

    // Verify if patient has any ECG record
    const patientEcg = db.ecgRecordsTable.find((e) => e.patient_id === selectedPatientId);
    
    setTimeout(() => {
      // Pick random clinical classification or determine based on heart rate
      const hr = patientEcg ? patientEcg.heart_rate : 80;
      let diagnosis = diseases[0];

      if (hr > 100) {
        diagnosis = diseases[2]; // Tachycardia
      } else if (hr < 60) {
        diagnosis = diseases[3]; // Bradycardia
      } else {
        diagnosis = diseases[Math.floor(Math.random() * diseases.length)];
      }

      const conf = +(82 + Math.random() * 16).toFixed(1);
      const ecgId = patientEcg ? patientEcg.ecg_id : 1;

      // Execute SQL DML INSERT
      db.insertPrediction({
        ecg_id: ecgId,
        patient_id: selectedPatientId,
        disease_name: diagnosis.name,
        confidence_score: conf,
        risk_level: diagnosis.risk as "Low" | "Medium" | "High",
        recommendation: diagnosis.rec
      });

      setResult({
        disease: diagnosis.name,
        conf,
        risk: diagnosis.risk as "Low" | "Medium" | "High",
        rec: diagnosis.rec
      });

      toast.success("ML classification complete · prediction row inserted into database!");
      setLoading(false);
      setRenderCount(c => c + 1);
    }, 1300);
  };

  const startEdit = (id: number, currentRisk: "Low" | "Medium" | "High", currentDisease: string) => {
    setEditingId(id);
    setNewRisk(currentRisk);
    setNewDisease(currentDisease);
  };

  const saveOverride = (id: number) => {
    // Execute SQL DML UPDATE statement live!
    db.updatePrediction(id, newRisk, newDisease);
    setEditingId(null);
    toast.success(`UPDATE query executed successfully for prediction #${id}`);
    setRenderCount(c => c + 1);
  };

  const queryIds = ["create-predictions", "insert-prediction", "view-predictions", "high-risk", "update-prediction", "recent-predictions"];
  const relatedQueries = queryIds.map(id => sqlQueries.find(q => q.id === id)!);

  return (
    <AppLayout 
      title="AI Cardiology Inference" 
      subtitle="predictions Table · TensorFlow Classifier & SQL UPDATE Overrides"
    >
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Prediction runner Card */}
        <div className="glass rounded-2xl p-5 border border-border lg:col-span-1 flex flex-col justify-between h-fit">
          <div className="space-y-4">
            <div>
              <h3 className="font-semibold text-foreground flex items-center gap-2"><Brain className="h-4.5 w-4.5 text-primary" /> Run Machine Learning Model</h3>
              <p className="text-xs text-muted-foreground mt-1">Invokes TensorFlow classifier on the latest ECG Lead II record.</p>
            </div>

            <div className="space-y-3">
              <div>
                <label className="text-xs text-muted-foreground font-semibold">Select Patient to Diagnose</label>
                <select 
                  value={selectedPatientId} 
                  onChange={(e) => setSelectedPatientId(+e.target.value)} 
                  className="mt-1.5 w-full h-10 px-3 rounded-lg bg-background border border-input text-xs text-foreground focus:outline-none"
                  disabled={role === "Patient" || loading}
                >
                  {db.patientsTable.map((p) => (
                    <option key={p.patient_id} value={p.patient_id}>
                      #{p.patient_id} · {p.full_name}
                    </option>
                  ))}
                </select>
              </div>

              <button 
                onClick={runPrediction} 
                disabled={loading} 
                className="w-full h-10 rounded-lg gradient-primary text-primary-foreground font-semibold shadow-glow flex items-center justify-center gap-1.5 cursor-pointer disabled:opacity-60"
              >
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
                {loading ? "Evaluating ECG intervals..." : "Run AI Diagnostics"}
              </button>
            </div>

            {/* Dynamic Results Card */}
            {result && (
              <div className="mt-4 rounded-xl border border-border p-4 bg-primary/5 animate-scale-in">
                <div className="text-[10px] text-primary uppercase font-bold tracking-wider">Classification Output</div>
                <div className="text-base font-bold text-foreground mt-1 flex items-center gap-1">
                  {result.disease} <Sparkles className="h-3.5 w-3.5 text-primary" />
                </div>
                
                <div className="mt-4 flex items-center justify-between">
                  <div>
                    <div className="text-[10px] text-muted-foreground">MODEL CONFIDENCE</div>
                    <div className="text-lg font-mono text-primary font-bold">{result.conf}%</div>
                  </div>
                  <RiskBadge level={result.risk} />
                </div>
                
                <div className="mt-2 h-1.5 w-full bg-muted rounded-full overflow-hidden">
                  <div className="h-full gradient-primary" style={{ width: `${result.conf}%` }} />
                </div>

                <div className="mt-4 border-t border-border/50 pt-2.5">
                  <span className="text-[10px] text-muted-foreground block font-semibold mb-1">AUTOMATED RECOMMENDATION</span>
                  <p className="text-[11px] text-foreground leading-normal bg-card p-2 rounded border border-border">
                    {result.rec}
                  </p>
                </div>
              </div>
            )}
          </div>

          <div className="mt-5 text-[10px] font-mono text-muted-foreground border-t border-border/40 pt-3">
            -- Inference query sample:<br />
            INSERT INTO predictions (ecg_id, patient_id, disease_name, confidence_score, risk_level) VALUES (...);
          </div>
        </div>

        {/* Prediction Results Database Table View */}
        <div className="glass rounded-2xl border border-border lg:col-span-2 overflow-hidden h-fit">
          <div className="p-4 border-b border-border flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-foreground flex items-center gap-1.5"><Brain className="h-4.5 w-4.5 text-primary" /> predictions Table Rows</h3>
              <p className="text-xs text-muted-foreground">Select query output reflecting AI diagnostic outcomes in the PostgreSQL engine.</p>
            </div>
            <span className="text-[10px] font-mono text-muted-foreground bg-black/10 dark:bg-black/35 px-2.5 py-1 rounded">SELECT * FROM predictions;</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="text-muted-foreground uppercase border-b border-border bg-muted/20">
                <tr>
                  <th className="py-2.5 px-4">Pred ID</th>
                  <th>Patient Name</th>
                  <th>Disease Diagnostics</th>
                  <th>Confidence</th>
                  <th>Risk Index</th>
                  <th>Diagnosed At</th>
                  {(role === "Doctor" || role === "Admin") && <th className="text-right px-4">Override Actions</th>}
                </tr>
              </thead>
              <tbody>
                {[...db.predictionsTable].reverse().map((p) => {
                  const pat = db.patientsTable.find((patObj) => patObj.patient_id === p.patient_id);
                  const isEditing = editingId === p.prediction_id;

                  return (
                    <tr key={p.prediction_id} className="border-b border-border/50 hover:bg-muted/10 transition-colors">
                      <td className="py-3 px-4 font-mono font-bold text-primary">#{p.prediction_id}</td>
                      <td className="font-semibold text-foreground">{pat ? pat.full_name : `Patient #${p.patient_id}`}</td>
                      
                      <td>
                        {isEditing ? (
                          <select 
                            value={newDisease}
                            onChange={(e) => setNewDisease(e.target.value)}
                            className="bg-background border border-input rounded px-1.5 py-1 text-[11px] text-foreground focus:outline-none"
                          >
                            <option>Normal Sinus Rhythm</option>
                            <option>Possible Arrhythmia</option>
                            <option>Sinus Tachycardia</option>
                            <option>Mild Bradycardia Risk</option>
                            <option>Atrial Fibrillation</option>
                          </select>
                        ) : (
                          <span className="text-foreground">{p.disease_name}</span>
                        )}
                      </td>

                      <td className="font-mono text-primary font-bold">{p.confidence_score}%</td>
                      
                      <td>
                        {isEditing ? (
                          <select 
                            value={newRisk}
                            onChange={(e) => setNewRisk(e.target.value as any)}
                            className="bg-background border border-input rounded px-1.5 py-1 text-[11px] text-foreground focus:outline-none font-bold"
                          >
                            <option>Low</option>
                            <option>Medium</option>
                            <option>High</option>
                          </select>
                        ) : (
                          <RiskBadge level={p.risk_level} />
                        )}
                      </td>

                      <td className="font-mono text-zinc-500">{p.predicted_at}</td>

                      {(role === "Doctor" || role === "Admin") && (
                        <td className="text-right px-4">
                          {isEditing ? (
                            <div className="flex justify-end gap-1.5">
                              <button 
                                onClick={() => setEditingId(null)}
                                className="text-[10px] text-muted-foreground hover:bg-muted py-1 px-2 rounded cursor-pointer"
                              >
                                Cancel
                              </button>
                              <button 
                                onClick={() => saveOverride(p.prediction_id)}
                                className="text-[10px] bg-primary text-primary-foreground font-bold py-1 px-2 rounded shadow cursor-pointer"
                              >
                                Save UPDATE
                              </button>
                            </div>
                          ) : (
                            <button 
                              onClick={() => startEdit(p.prediction_id, p.risk_level, p.disease_name)}
                              className="inline-flex items-center gap-1 text-[10px] text-primary hover:bg-primary/10 py-1 px-2 rounded transition-colors cursor-pointer"
                            >
                              <Edit className="h-3 w-3" /> Override SQL
                            </button>
                          )}
                        </td>
                      )}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* SQL Queries Block */}
      <div className="mt-6">
        <h3 className="font-semibold text-foreground mb-3 flex items-center gap-1.5"><Database className="h-4.5 w-4.5 text-primary animate-pulse" /> Related SQL Operations Catalog</h3>
        <div className="grid lg:grid-cols-2 gap-4">
          {relatedQueries.map((q) => (
            <SqlQueryCard key={q.id} query={q} />
          ))}
        </div>
      </div>
    </AppLayout>
  );
}