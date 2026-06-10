import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Search, UserPlus, Trash2, Mail, Phone, Database, ShieldAlert, ArrowRight } from "lucide-react";
import { toast } from "sonner";
import { AppLayout } from "@/components/AppLayout";
import { SqlQueryCard } from "@/components/SqlQueryCard";
import { sqlQueries } from "@/lib/sql-queries";
import { db, type Patient, type AppRole } from "@/lib/db-store";

export const Route = createFileRoute("/patients")({
  head: () => ({ meta: [{ title: "Patients — CardioPredict" }] }),
  component: PatientsPage,
});

function PatientsPage() {
  const [role, setRole] = useState<AppRole>(db.getRole());
  const [renderCount, setRenderCount] = useState(0);

  const [search, setSearch] = useState("");
  const [open, setOpen] = useState(false);

  // New Patient Form state
  const [fullName, setFullName] = useState("");
  const [age, setAge] = useState(30);
  const [gender, setGender] = useState<"Male" | "Female" | "Other">("Male");
  const [bloodGroup, setBloodGroup] = useState("O+");
  const [contact, setContact] = useState("");
  const [email, setEmail] = useState("");
  const [address, setAddress] = useState("");
  const [history, setHistory] = useState("");

  useEffect(() => {
    const unsubscribe = db.subscribe(() => {
      setRole(db.getRole());
      setRenderCount(c => c + 1);
    });
    return () => unsubscribe();
  }, []);

  const handleAddPatient = () => {
    if (!fullName.trim() || !contact.trim() || !email.trim()) {
      return toast.error("Please fill in Name, Email and Contact Number!");
    }

    // Call dynamic SQL INSERT
    db.insertPatient({
      full_name: fullName,
      age,
      gender,
      blood_group: bloodGroup,
      contact,
      email,
      address,
      medical_history: history || "None recorded"
    });

    toast.success("Patient created! 2 tables modified (users, patients)");
    setOpen(false);
    
    // Clear form
    setFullName("");
    setAge(30);
    setGender("Male");
    setBloodGroup("O+");
    setContact("");
    setEmail("");
    setAddress("");
    setHistory("");
    
    setRenderCount(c => c + 1);
  };

  const handleDeletePatient = (id: number) => {
    // Call dynamic SQL DELETE
    db.deletePatient(id);
    toast.success(`DELETE query executed successfully for patient #${id}!`);
    setRenderCount(c => c + 1);
  };

  // Dynamic LIKE query filtering
  const filteredPatients = db.patientsTable.filter(
    (p) =>
      p.full_name.toLowerCase().includes(search.toLowerCase()) ||
      p.email.toLowerCase().includes(search.toLowerCase()) ||
      p.patient_id.toString() === search
  );

  const queryIds = ["create-patients", "insert-patient", "view-patients", "search-patient", "delete-patient"];
  const relatedQueries = queryIds.map(id => sqlQueries.find(q => q.id === id)!);

  return (
    <AppLayout 
      title="Patient Records Registry" 
      subtitle="patients Table · Demographics demographics, Medical History & Cascading SQL DELETEs"
    >
      <div className="space-y-6 animate-fade-in">
        {/* Search bar and Insert Button */}
        <div className="flex flex-col md:flex-row md:items-center gap-3 justify-between">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by Patient Name or Email (LIKE query)..."
              className="w-full h-10 pl-9 pr-3 rounded-lg bg-card border border-border text-xs text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
          {(role === "Doctor" || role === "Admin") && (
            <button 
              onClick={() => setOpen(true)} 
              className="inline-flex items-center gap-2 gradient-primary text-primary-foreground text-xs font-semibold px-4 py-2.5 rounded-lg shadow-glow cursor-pointer"
            >
              <UserPlus className="h-4.5 w-4.5" /> Register New Patient
            </button>
          )}
        </div>

        {/* Patients Registry Table */}
        <div className="glass rounded-2xl border border-border overflow-hidden">
          <div className="p-4 border-b border-border flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-foreground flex items-center gap-1.5">Registered Patient Records</h3>
              <p className="text-xs text-muted-foreground">Select query output reflecting patient records synchronized with user IDs.</p>
            </div>
            <span className="text-[10px] font-mono text-muted-foreground bg-black/10 dark:bg-black/35 px-2.5 py-1 rounded">
              SELECT * FROM patients WHERE full_name LIKE '%{search}%';
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="text-muted-foreground uppercase border-b border-border bg-muted/20">
                <tr>
                  <th className="py-2.5 px-4">Patient ID</th>
                  <th>Full Name</th>
                  <th>Age / Gender</th>
                  <th>Blood Group</th>
                  <th>Contact Nodes</th>
                  <th>Medical History Remarks</th>
                  <th>Joined Date</th>
                  {(role === "Doctor" || role === "Admin") && <th className="text-right px-4">Action</th>}
                </tr>
              </thead>
              <tbody>
                {filteredPatients.map((p) => (
                  <tr key={p.patient_id} className="border-b border-border/50 hover:bg-muted/10 transition-colors">
                    <td className="py-3.5 px-4 font-mono font-bold text-primary">#{p.patient_id}</td>
                    <td className="font-semibold text-foreground">{p.full_name}</td>
                    <td className="text-zinc-400">{p.age} Yrs / {p.gender}</td>
                    <td className="font-bold text-primary font-mono">{p.blood_group}</td>
                    <td className="space-y-0.5 text-zinc-500 font-mono">
                      <div className="flex items-center gap-1"><Mail className="h-3 w-3 text-muted-foreground" />{p.email}</div>
                      <div className="flex items-center gap-1"><Phone className="h-3 w-3 text-muted-foreground" />{p.contact}</div>
                    </td>
                    <td className="max-w-[180px] truncate text-foreground/80 leading-normal" title={p.medical_history}>
                      {p.medical_history}
                    </td>
                    <td className="font-mono text-zinc-500">{p.created_at.substring(0, 16)}</td>
                    {(role === "Doctor" || role === "Admin") && (
                      <td className="text-right px-4">
                        <button 
                          onClick={() => handleDeletePatient(p.patient_id)} 
                          className="inline-flex items-center gap-1 text-[10px] text-destructive hover:bg-destructive/10 py-1.5 px-2.5 rounded transition-all cursor-pointer border border-transparent hover:border-destructive/20"
                        >
                          <Trash2 className="h-3 w-3" /> DELETE ROW
                        </button>
                      </td>
                    )}
                  </tr>
                ))}
                {filteredPatients.length === 0 && (
                  <tr>
                    <td colSpan={8} className="text-center py-8 text-muted-foreground italic">
                      -- No clinical patient records found matching search query --
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
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
      </div>

      {/* NEW PATIENT MODAL FORM */}
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4" onClick={() => setOpen(false)}>
          <div onClick={(e) => e.stopPropagation()} className="w-full max-w-lg bg-card rounded-2xl p-6 border border-border shadow-2xl overflow-hidden flex flex-col h-[520px] justify-between animate-scale-in">
            <div>
              <h3 className="font-bold text-foreground text-lg flex items-center gap-2"><UserPlus className="h-5 w-5 text-primary" /> Register New Clinical Profile</h3>
              <p className="text-xs text-muted-foreground">Inserts record into <code className="text-primary">patients</code> and credentials into <code className="text-primary">users</code> tables linked by FK constraints.</p>
              
              <div className="mt-4 space-y-3 overflow-y-auto max-h-[340px] pr-2 scrollbar-thin">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-[10px] uppercase font-bold text-muted-foreground block mb-1">Full Name</label>
                    <input 
                      type="text" 
                      placeholder="Rahul Sharma" 
                      value={fullName} 
                      onChange={(e) => setFullName(e.target.value)} 
                      className="w-full h-10 px-3 bg-background border border-input rounded-lg text-xs focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="text-[10px] uppercase font-bold text-muted-foreground block mb-1">Email Address</label>
                    <input 
                      type="email" 
                      placeholder="rahul@gmail.com" 
                      value={email} 
                      onChange={(e) => setEmail(e.target.value)} 
                      className="w-full h-10 px-3 bg-background border border-input rounded-lg text-xs focus:outline-none"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-3">
                  <div>
                    <label className="text-[10px] uppercase font-bold text-muted-foreground block mb-1">Age</label>
                    <input 
                      type="number" 
                      value={age} 
                      onChange={(e) => setAge(+e.target.value)} 
                      className="w-full h-10 px-3 bg-background border border-input rounded-lg text-xs focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="text-[10px] uppercase font-bold text-muted-foreground block mb-1">Gender</label>
                    <select 
                      value={gender} 
                      onChange={(e) => setGender(e.target.value as any)} 
                      className="w-full h-10 px-2 bg-background border border-input rounded-lg text-xs focus:outline-none text-foreground"
                    >
                      <option>Male</option>
                      <option>Female</option>
                      <option>Other</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-[10px] uppercase font-bold text-muted-foreground block mb-1">Blood Group</label>
                    <input 
                      type="text" 
                      placeholder="O+" 
                      value={bloodGroup} 
                      onChange={(e) => setBloodGroup(e.target.value)} 
                      className="w-full h-10 px-3 bg-background border border-input rounded-lg text-xs focus:outline-none"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-[10px] uppercase font-bold text-muted-foreground block mb-1">Contact Phone</label>
                    <input 
                      type="text" 
                      placeholder="9876543210" 
                      value={contact} 
                      onChange={(e) => setContact(e.target.value)} 
                      className="w-full h-10 px-3 bg-background border border-input rounded-lg text-xs focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="text-[10px] uppercase font-bold text-muted-foreground block mb-1">Residential Address</label>
                    <input 
                      type="text" 
                      placeholder="Bangalore, India" 
                      value={address} 
                      onChange={(e) => setAddress(e.target.value)} 
                      className="w-full h-10 px-3 bg-background border border-input rounded-lg text-xs focus:outline-none"
                    />
                  </div>
                </div>

                <div>
                  <label className="text-[10px] uppercase font-bold text-muted-foreground block mb-1">Cardiovascular / Medical History Remarks</label>
                  <textarea 
                    placeholder="Hypertension history, diabetes records, previous surgery details..."
                    value={history} 
                    onChange={(e) => setHistory(e.target.value)} 
                    className="w-full h-16 p-3 bg-background border border-input rounded-lg text-xs focus:outline-none resize-none"
                  />
                </div>
              </div>
            </div>

            <div className="mt-4 flex justify-end gap-2 border-t border-border pt-4">
              <button 
                onClick={() => setOpen(false)} 
                className="px-4 py-2 rounded-lg text-xs text-muted-foreground hover:bg-muted cursor-pointer"
              >
                Cancel
              </button>
              <button 
                onClick={handleAddPatient} 
                className="px-4 py-2 rounded-lg text-xs gradient-primary text-primary-foreground font-semibold shadow cursor-pointer"
              >
                Execute INSERT INTO patients
              </button>
            </div>
          </div>
        </div>
      )}
    </AppLayout>
  );
}