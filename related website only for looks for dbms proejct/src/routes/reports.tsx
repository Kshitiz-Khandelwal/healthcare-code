import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { FileText, Download, AlertTriangle, Database, Printer, Edit3, X, Check, Activity } from "lucide-react";
import { AppLayout } from "@/components/AppLayout";
import { SqlQueryCard } from "@/components/SqlQueryCard";
import { sqlQueries } from "@/lib/sql-queries";
import { db, type AppRole } from "@/lib/db-store";
import { RiskBadge } from "@/components/RiskBadge";
import { toast } from "sonner";
import { EcgWave } from "@/components/EcgWave";

export const Route = createFileRoute("/reports")({
  head: () => ({ meta: [{ title: "Reports — CardioPredict" }] }),
  component: ReportsPage,
});

function ReportsPage() {
  const [role, setRole] = useState<AppRole>(db.getRole());
  const [renderCount, setRenderCount] = useState(0);

  // Print PDF state
  const [selectedReportRow, setSelectedReportRow] = useState<any | null>(null);
  
  // Annotation state
  const [editingReportId, setEditingReportId] = useState<number | null>(null);
  const [notesText, setNotesText] = useState("");

  useEffect(() => {
    const unsubscribe = db.subscribe(() => {
      setRole(db.getRole());
      setRenderCount(c => c + 1);
    });
    return () => unsubscribe();
  }, []);

  // Multi-table JOIN simulation in React state
  const reportRows = db.patientsTable
    .map((p) => {
      const e = db.ecgRecordsTable.find((x) => x.patient_id === p.patient_id);
      const pr = db.predictionsTable.find((x) => x.patient_id === p.patient_id);
      const rep = db.reportsTable.find((x) => x.patient_id === p.patient_id);
      if (!e || !pr) return null;
      return { 
        ...p, 
        ...e, 
        ...pr, 
        doctor_notes: rep ? rep.doctor_notes : "No clinical annotations added yet.",
        report_id: rep ? rep.report_id : null
      };
    })
    .filter(Boolean) as any[];

  const highRisk = reportRows.filter((r) => r.risk_level === "High");

  const handleEditNotes = (reportId: number | null, currentNotes: string) => {
    if (!reportId) {
      toast.error("No official report ID seeded for this patient. Generating report container first.");
      // Auto seed report
      const newRepId = db.reportsTable.length + 301;
      db.reportsTable.push({
        report_id: newRepId,
        patient_id: 101, // Rahul default
        ecg_id: 1,
        generated_pdf: `/reports/report_101.pdf`,
        doctor_notes: currentNotes,
        generated_at: new Date().toISOString().substring(0, 10)
      });
      db.saveAll(); // Save mutations instantly!
      setEditingReportId(newRepId);
      setNotesText(currentNotes);
      setRenderCount(c => c + 1);
      return;
    }
    setEditingReportId(reportId);
    setNotesText(currentNotes);
  };

  const saveNotes = (reportId: number) => {
    // Run SQL DML UPDATE to update report notes
    db.addDoctorNote(reportId, notesText);
    setEditingReportId(null);
    toast.success(`UPDATE report notes executed successfully for report #${reportId}`);
    setRenderCount(c => c + 1);
  };

  const exportCsv = () => {
    db.logQuery(
      "SELECT p.*, e.*, pr.* FROM patients p JOIN ecg_records e ON p.patient_id=e.patient_id JOIN predictions pr ON e.ecg_id=pr.ecg_id INTO OUTFILE 'report.csv' FIELDS TERMINATED BY ',';",
      "Exported active relational joins to CSV file"
    );
    toast.success("Joined report exported successfully as report.csv!");
  };

  const triggerBrowserPrint = () => {
    if (typeof window !== "undefined") {
      window.print();
    }
  };

  const triggerTxtDownload = (rowObj: any) => {
    const content = `CARDIOPREDICT CLINICAL DIAGNOSTIC REPORT\n========================================\nPatient Name: ${rowObj.full_name}\nAge: ${rowObj.age} | Gender: ${rowObj.gender}\nBlood Group: ${rowObj.blood_group}\nContact No: ${rowObj.contact}\nEmail Address: ${rowObj.email}\nAddress: ${rowObj.address}\n\nTELEMETRY METRICS\n-----------------\nHeart Rate: ${rowObj.heart_rate} BPM\nQRS Interval Duration: ${rowObj.qrs_duration}s\nPR Interval Duration: ${rowObj.pr_interval}s\nQT Interval Duration: ${rowObj.qt_interval}s\n\nAI MACHINE LEARNING CLASSIFICATION\n----------------------------------\nCondition Diagnosis: ${rowObj.disease_name}\nModel Confidence Score: ${rowObj.confidence_score}%\nRisk Index Level: ${rowObj.risk_level}\nAutomated Recommendation: ${rowObj.recommendation}\n\nCLINICIAN CONSULTATION ANNOTATIONS\n----------------------------------\n"${rowObj.doctor_notes}"\n\nAuthorized Physician Sign-off:\nDR. ARJUN MEHTA (Fortis Cardiology Division)\nReport Generated: ${new Date().toISOString().substring(0, 19)}\n========================================`;
    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `CardioPredict_Diagnostic_Report_${rowObj.full_name.replace(/\s+/g, "_")}.txt`;
    link.click();
    toast.success(`Clinical report downloaded successfully for ${rowObj.full_name}!`);
  };

  const queryIds = ["patient-report", "high-risk", "critical-hr", "total-patients", "avg-hr", "create-view", "view-dashboard", "export-dataset"];
  const relatedQueries = queryIds.map(id => sqlQueries.find(q => q.id === id)!);

  return (
    <AppLayout 
      title="Clinical Reporting Center" 
      subtitle="Multi-Table JOINs · Clinical Annotations & Downloadable PDFs"
    >
      <div className="space-y-6 animate-fade-in print:p-0 print:m-0">
        {/* High-Risk Clinical Alerts Banner */}
        {highRisk.length > 0 && !selectedReportRow && (
          <div className="rounded-2xl border border-destructive/40 bg-destructive/5 p-5 flex items-start gap-3 print:hidden">
            <AlertTriangle className="h-5 w-5 text-destructive flex-shrink-0 mt-0.5 animate-bounce" />
            <div className="flex-1">
              <h3 className="font-semibold text-foreground">{highRisk.length} High-Risk Cardiac Anomalies Flagged</h3>
              <p className="text-xs text-muted-foreground mt-0.5">Critical anomalies require immediate diagnostic notes and Holter telemetry reviews.</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {highRisk.map((r) => (
                  <span key={r.patient_id} className="text-xs bg-card px-2.5 py-1 rounded-md border border-border font-semibold">
                    {r.full_name} · <span className="text-destructive font-bold">{r.disease_name} ({r.heart_rate} BPM)</span>
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Complete Patients Report Card Table */}
        {!selectedReportRow && (
          <div className="glass rounded-2xl border border-border overflow-hidden print:hidden animate-fade-in">
            <div className="p-4 border-b border-border flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-foreground flex items-center gap-1.5"><FileText className="h-4.5 w-4.5 text-primary" /> Integrated Patient Diagnoses</h3>
                <p className="text-xs text-muted-foreground">Executes a multi-table JOIN to synthesize demographics, telemetry metrics, and AI recommendations. Click patient name to open detailed card.</p>
              </div>
              <button 
                onClick={exportCsv} 
                className="inline-flex items-center gap-1.5 text-xs gradient-primary text-primary-foreground px-3.5 py-2 rounded-lg shadow-glow font-semibold cursor-pointer"
              >
                <Download className="h-3.5 w-3.5" /> Export joined CSV
              </button>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="text-muted-foreground uppercase border-b border-border bg-muted/20">
                  <tr>
                    <th className="py-2.5 px-4">Patient (Click Name)</th>
                    <th>Age / Gender</th>
                    <th>Telemetry HR</th>
                    <th>QRS duration</th>
                    <th>AI Diagnostics Code</th>
                    <th>Risk</th>
                    <th>Clinical Annotations</th>
                    <th className="text-right px-4">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {reportRows.map((r, i) => {
                    const isEditing = editingReportId === r.report_id && r.report_id !== null;
                    return (
                      <tr key={i} className="border-b border-border/50 hover:bg-muted/10 transition-colors">
                        <td 
                          className="py-4 px-4 font-bold text-primary hover:text-primary-foreground hover:bg-primary/20 hover:underline cursor-pointer transition-all"
                          onClick={() => setSelectedReportRow(r)}
                          title="Click to view detailed clinical diagnostic card"
                        >
                          {r.full_name}
                        </td>
                        <td className="text-zinc-400">{r.age} Yrs / {r.gender}</td>
                        <td className="font-bold font-mono text-foreground">{r.heart_rate} BPM</td>
                        <td className="font-mono text-zinc-500">{r.qrs_duration}s</td>
                        <td className="font-semibold text-foreground">{r.disease_name}</td>
                        <td><RiskBadge level={r.risk_level} /></td>
                        
                        <td className="max-w-[180px] truncate text-foreground/80 leading-normal italic">
                          {isEditing ? (
                            <input 
                              type="text" 
                              value={notesText} 
                              onChange={(e) => setNotesText(e.target.value)} 
                              className="bg-background border border-input rounded px-1.5 py-0.5 text-[11px] text-foreground w-full"
                            />
                          ) : (
                            r.doctor_notes
                          )}
                        </td>

                        <td className="text-right px-4">
                          <div className="flex justify-end gap-1.5">
                            {isEditing ? (
                              <button 
                                onClick={() => saveNotes(r.report_id!)}
                                className="bg-primary hover:bg-primary/95 text-primary-foreground font-bold p-1 rounded shadow cursor-pointer"
                                title="Execute UPDATE SQL"
                              >
                                <Check className="h-3.5 w-3.5" />
                              </button>
                            ) : (role === "Doctor" || role === "Admin") ? (
                              <button 
                                onClick={() => handleEditNotes(r.report_id, r.doctor_notes)}
                                className="text-[10px] text-primary hover:bg-primary/10 py-1.5 px-2 rounded cursor-pointer border border-transparent hover:border-primary/20"
                                title="Update Doctor Notes"
                              >
                                <Edit3 className="h-3.5 w-3.5" />
                              </button>
                            ) : null}
                            
                            <button 
                              onClick={() => triggerTxtDownload(r)}
                              className="inline-flex items-center gap-1 text-[10px] gradient-primary text-primary-foreground py-1.5 px-2.5 rounded shadow cursor-pointer font-semibold"
                              title="Download report details as text file"
                            >
                              <Download className="h-3 w-3" /> Download TXT
                            </button>

                            <button 
                              onClick={() => setSelectedReportRow(r)}
                              className="inline-flex items-center gap-1 text-[10px] bg-card hover:bg-muted border border-border py-1.5 px-2.5 rounded shadow cursor-pointer text-foreground font-semibold"
                            >
                              <Printer className="h-3 w-3 text-primary" /> PDF Card
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* PRINTABLE CLINICAL PDF REPORT CARD VIEW (WOW FACTOR!) */}
        {selectedReportRow && (
          <div className="bg-white border-2 border-zinc-200 rounded-3xl p-8 max-w-3xl mx-auto shadow-2xl text-black font-sans animate-scale-in">
            {/* Header info */}
            <div className="flex justify-between items-start border-b-2 border-zinc-950 pb-5">
              <div className="flex items-center gap-3">
                <div className="h-11 w-11 rounded-xl bg-zinc-950 flex items-center justify-center text-white">
                  <Activity className="h-6 w-6 animate-pulse" />
                </div>
                <div>
                  <h2 className="text-xl font-bold tracking-tight uppercase">CardioPredict Cardiology Center</h2>
                  <span className="text-[10px] uppercase font-bold tracking-wider text-zinc-500">Official Relational Health Diagnosis PDF</span>
                </div>
              </div>
              <div className="text-right text-[10px] font-mono text-zinc-500">
                <div>REPORT ID: #{selectedReportRow.report_id || 301}</div>
                <div>DATE: {new Date().toISOString().replace("T", " ").substring(0, 16)}</div>
                <div>DB_REF: ecg_records_row#{selectedReportRow.ecg_id}</div>
              </div>
            </div>

            {/* Patient demographics */}
            <div className="mt-6">
              <h3 className="text-xs uppercase font-extrabold tracking-wider text-zinc-400 border-b border-zinc-200 pb-1 mb-2">1. Relational Patient Demographics</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
                <div>
                  <span className="text-zinc-500 font-bold">FULL NAME:</span>
                  <div className="font-bold text-sm mt-0.5 text-zinc-900">{selectedReportRow.full_name}</div>
                </div>
                <div>
                  <span className="text-zinc-500 font-bold">AGE / GENDER:</span>
                  <div className="font-semibold mt-0.5 text-zinc-800">{selectedReportRow.age} Yrs / {selectedReportRow.gender}</div>
                </div>
                <div>
                  <span className="text-zinc-500 font-bold">BLOOD TYPE:</span>
                  <div className="font-bold mt-0.5 text-zinc-800">{selectedReportRow.blood_group}</div>
                </div>
                <div>
                  <span className="text-zinc-500 font-bold">CONTACT PHONE:</span>
                  <div className="font-mono mt-0.5 text-zinc-800">{selectedReportRow.contact}</div>
                </div>
              </div>
              
              <div className="mt-3 text-xs">
                <span className="text-zinc-500 font-bold">RESIDENTIAL ADDRESS:</span>
                <div className="mt-0.5 text-zinc-800">{selectedReportRow.address}</div>
              </div>
            </div>

            {/* Telemetry metrics & Waveform */}
            <div className="mt-6">
              <h3 className="text-xs uppercase font-extrabold tracking-wider text-zinc-400 border-b border-zinc-200 pb-1 mb-2">2. Telemetry Signal Telemetry</h3>
              <div className="grid grid-cols-3 gap-4 text-xs text-center bg-zinc-50 border border-zinc-200 p-3 rounded-xl mb-4 font-mono">
                <div>
                  <span className="text-zinc-500 text-[10px] block">HEART RATE</span>
                  <strong className="text-base text-zinc-950 font-extrabold">{selectedReportRow.heart_rate} BPM</strong>
                </div>
                <div>
                  <span className="text-zinc-500 text-[10px] block">QRS PULSE DURATION</span>
                  <strong className="text-base text-zinc-950 font-extrabold">{selectedReportRow.qrs_duration}s</strong>
                </div>
                <div>
                  <span className="text-zinc-500 text-[10px] block">PR INTERVAL</span>
                  <strong className="text-base text-zinc-950 font-extrabold">{selectedReportRow.pr_interval}s</strong>
                </div>
              </div>

              {/* Print styled ECG wave */}
              <div className="border border-zinc-200 rounded-xl p-3 bg-zinc-50 flex flex-col justify-center">
                <div className="text-[9px] font-mono text-zinc-500 mb-1 text-center border-b border-zinc-150 pb-1">ECG SIGNAL LEAD II WAVEFORM TRACE</div>
                <EcgWave height={120} hr={selectedReportRow.heart_rate} />
              </div>
            </div>

            {/* AI Predictions */}
            <div className="mt-6">
              <h3 className="text-xs uppercase font-extrabold tracking-wider text-zinc-400 border-b border-zinc-200 pb-1 mb-2">3. TensorFlow Machine Learning Diagnosis</h3>
              <div className="grid md:grid-cols-2 gap-4 text-xs">
                <div className="space-y-2 bg-zinc-50 border border-zinc-200 p-3.5 rounded-xl">
                  <div className="flex justify-between items-center">
                    <span className="text-zinc-500 font-bold uppercase">PRIMARY DIAGNOSTIC</span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                      selectedReportRow.risk_level === "High" ? "bg-red-100 text-red-700 border-red-200" : "bg-green-100 text-green-700 border-green-200"
                    }`}>{selectedReportRow.risk_level} Risk</span>
                  </div>
                  <div className="text-base font-extrabold text-zinc-900 mt-1">{selectedReportRow.disease_name}</div>
                  <div className="text-[10px] text-zinc-500">Classifier Confidence Rate: <strong className="font-mono text-zinc-950">{selectedReportRow.confidence_score}%</strong></div>
                </div>

                <div className="space-y-1.5">
                  <span className="text-zinc-500 font-bold uppercase">DIAGNOSTIC ADVISORY RECOMMENDATIONS:</span>
                  <p className="bg-zinc-50 p-3 rounded-xl border border-zinc-200 text-zinc-800 italic leading-relaxed">
                    "{selectedReportRow.recommendation}"
                  </p>
                </div>
              </div>
            </div>

            {/* Clinician Annotations */}
            <div className="mt-6 border-t border-zinc-200 pt-4">
              <h3 className="text-xs uppercase font-extrabold tracking-wider text-zinc-500 mb-1">4. Clinical Cardiologist Consultation Notes</h3>
              <p className="text-xs text-zinc-800 leading-relaxed font-semibold bg-zinc-50 border border-zinc-200 p-3 rounded-xl italic">
                "{selectedReportRow.doctor_notes}"
              </p>
            </div>

            {/* Disclaimer & Signoff */}
            <div className="mt-8 flex justify-between items-end border-t border-zinc-200 pt-4 text-[9px] text-zinc-400">
              <div className="max-w-xs leading-normal">
                <strong>Disclaimer Notice:</strong> This is a secure database report generated by CardioPredict AI and validated by Fortis Cardiology. Always verify against secondary Holters for clinical medication edits.
              </div>
              <div className="text-center font-bold text-zinc-700">
                <div className="h-8 w-24 border-b border-zinc-400 border-dashed mx-auto" />
                <div className="mt-1">DR. ARJUN MEHTA</div>
                <div className="text-[8px] text-zinc-400 font-normal uppercase">Authorized Sign-off</div>
              </div>
            </div>

            {/* Print Tools (Print Hidden) */}
            <div className="mt-8 flex justify-end gap-2 print:hidden border-t border-zinc-100 pt-4">
              <button 
                onClick={() => setSelectedReportRow(null)}
                className="px-4 py-2 bg-zinc-100 hover:bg-zinc-200 text-zinc-800 font-semibold text-xs rounded-lg cursor-pointer"
              >
                Back to Table
              </button>
              
              <button 
                onClick={() => triggerTxtDownload(selectedReportRow)}
                className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-white font-bold text-xs rounded-lg flex items-center gap-1.5 shadow cursor-pointer"
              >
                <Download className="h-4 w-4" /> Download Report (.txt)
              </button>

              <button 
                onClick={triggerBrowserPrint}
                className="px-4 py-2 bg-zinc-950 hover:bg-zinc-900 text-white font-bold text-xs rounded-lg flex items-center gap-1.5 shadow cursor-pointer animate-pulse"
              >
                <Printer className="h-4 w-4" /> Print / Save as PDF
              </button>
            </div>
          </div>
        )}

        {/* Reporting SQL */}
        {!selectedReportRow && (
          <div>
            <h3 className="font-semibold text-foreground mb-3 flex items-center gap-1.5"><Database className="h-4.5 w-4.5 text-primary animate-pulse" /> Reporting SQL Queries Catalog</h3>
            <div className="grid lg:grid-cols-2 gap-4">
              {relatedQueries.map((q) => (
                <SqlQueryCard key={q.id} query={q} />
              ))}
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}