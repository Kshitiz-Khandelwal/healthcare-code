import { toast } from "sonner";

export interface User {
  user_id: number;
  name: string;
  email: string;
  password_hash: string;
  role: "Patient" | "Doctor" | "Admin";
  created_at: string;
}

export interface Patient {
  patient_id: number;
  user_id: number;
  full_name: string;
  age: number;
  gender: "Male" | "Female" | "Other";
  blood_group: string;
  contact: string;
  medical_history: string;
  email: string;
  address: string;
  created_at: string;
}

export interface Doctor {
  doctor_id: number;
  user_id: number;
  full_name: string;
  specialization: string;
  hospital: string;
  experience: number;
  contact: string;
  email: string;
}

export interface EcgRecord {
  ecg_id: number;
  patient_id: number;
  upload_url: string;
  upload_type: "image" | "csv" | "pdf";
  heart_rate: number;
  qrs_duration: number;
  pr_interval: number;
  qt_interval: number;
  ecg_signal: string;
  uploaded_at: string;
}

export interface Prediction {
  prediction_id: number;
  ecg_id: number;
  patient_id: number;
  disease_name: string;
  confidence_score: number;
  risk_level: "Low" | "Medium" | "High";
  recommendation: string;
  predicted_at: string;
}

export interface Report {
  report_id: number;
  patient_id: number;
  ecg_id: number;
  generated_pdf: string;
  doctor_notes: string;
  generated_at: string;
}

export interface Appointment {
  appointment_id: number;
  patient_id: number;
  doctor_id: number;
  appointment_date: string;
  status: "Pending" | "Scheduled" | "Completed" | "Cancelled";
}

export interface AuditLog {
  log_id: number;
  user_id: number;
  username: string;
  role: string;
  activity: string;
  sql_query?: string;
  timestamp: string;
  ip_address: string;
  status: "SUCCESS" | "FAILED";
  execution_time_ms: number;
}

// ==========================================
// SEED CONSTANTS
// ==========================================
const SEED_USERS: User[] = [
  { user_id: 1, name: "Rahul Sharma", email: "rahul@gmail.com", password_hash: "$2b$12$eImiTX..RahulHash123", role: "Patient", created_at: "2025-04-12 09:14:00" },
  { user_id: 2, name: "Priya Verma", email: "priya.v@gmail.com", password_hash: "$2b$12$eImiTX..PriyaHash123", role: "Patient", created_at: "2025-04-15 11:02:00" },
  { user_id: 3, name: "Dr. Arjun Mehta", email: "arjun.m@gmail.com", password_hash: "$2b$12$eImiTX..ArjunHash123", role: "Doctor", created_at: "2025-04-18 14:30:00" },
  { user_id: 4, name: "Dr. Anjali Nair", email: "anjali.n@gmail.com", password_hash: "$2b$12$eImiTX..AnjaliHash123", role: "Doctor", created_at: "2025-04-25 10:20:00" },
  { user_id: 5, name: "Sys Admin", email: "admin@cardiopredict.com", password_hash: "$2b$12$eImiTX..AdminHash123", role: "Admin", created_at: "2025-04-01 08:00:00" },
  { user_id: 6, name: "Sneha Iyer", email: "sneha.i@gmail.com", password_hash: "$2b$12$eImiTX..SnehaHash123", role: "Patient", created_at: "2025-04-20 08:45:00" },
  { user_id: 7, name: "Vikram Singh", email: "vikram.s@gmail.com", password_hash: "$2b$12$eImiTX..VikramHash123", role: "Patient", created_at: "2025-04-22 16:10:00" }
];

const SEED_PATIENTS: Patient[] = [
  { patient_id: 101, user_id: 1, full_name: "Rahul Sharma", age: 45, gender: "Male", blood_group: "O+", contact: "9876543210", medical_history: "Mild hypertension, father had myocardial infarction", email: "rahul@gmail.com", address: "Indiranagar, Bangalore", created_at: "2025-04-12 09:14:00" },
  { patient_id: 102, user_id: 2, full_name: "Priya Verma", age: 38, gender: "Female", blood_group: "A-", contact: "9123456701", medical_history: "None", email: "priya.v@gmail.com", address: "Andheri West, Mumbai", created_at: "2025-04-15 11:02:00" },
  { patient_id: 103, user_id: 6, full_name: "Sneha Iyer", age: 29, gender: "Female", blood_group: "B+", contact: "9001122334", medical_history: "Thyroid issues, occasional palpitations", email: "sneha.i@gmail.com", address: "Adyar, Chennai", created_at: "2025-04-20 08:45:00" },
  { patient_id: 104, user_id: 7, full_name: "Vikram Singh", age: 62, gender: "Male", blood_group: "O-", contact: "9876501234", medical_history: "Type-2 Diabetes, previous angioplasty (2022)", email: "vikram.s@gmail.com", address: "Malviya Nagar, Jaipur", created_at: "2025-04-22 16:10:00" }
];

const SEED_DOCTORS: Doctor[] = [
  { doctor_id: 201, user_id: 3, full_name: "Dr. Arjun Mehta", specialization: "Cardiologist", hospital: "Fortis Cardiology", experience: 18, contact: "9988776655", email: "arjun.m@gmail.com" },
  { doctor_id: 202, user_id: 4, full_name: "Dr. Anjali Nair", specialization: "Electrophysiologist", hospital: "Apollo Hospitals", experience: 12, contact: "9090909090", email: "anjali.n@gmail.com" }
];

const SEED_ECG: EcgRecord[] = [
  { ecg_id: 1, patient_id: 101, upload_url: "ecg_rahul_1.png", upload_type: "image", heart_rate: 92, qrs_duration: 0.11, pr_interval: 0.18, qt_interval: 0.42, ecg_signal: "Lead II Signal", uploaded_at: "2025-05-01 09:30:00" },
  { ecg_id: 2, patient_id: 102, upload_url: "ecg_priya_2.csv", upload_type: "csv", heart_rate: 78, qrs_duration: 0.09, pr_interval: 0.16, qt_interval: 0.40, ecg_signal: "Lead II Signal", uploaded_at: "2025-05-02 10:15:00" },
  { ecg_id: 3, patient_id: 103, upload_url: "ecg_sneha_3.pdf", upload_type: "pdf", heart_rate: 72, qrs_duration: 0.08, pr_interval: 0.15, qt_interval: 0.38, ecg_signal: "Lead II Signal", uploaded_at: "2025-05-05 08:00:00" },
  { ecg_id: 4, patient_id: 104, upload_url: "ecg_vikram_4.png", upload_type: "image", heart_rate: 110, qrs_duration: 0.13, pr_interval: 0.20, qt_interval: 0.45, ecg_signal: "Lead II Signal", uploaded_at: "2025-05-06 12:25:00" }
];

const SEED_PREDICTIONS: Prediction[] = [
  { prediction_id: 1, ecg_id: 1, patient_id: 101, disease_name: "Possible Arrhythmia", confidence_score: 94.5, risk_level: "High", recommendation: "Avoid stimulants, schedule cardiologist ECG review, check vitals daily.", predicted_at: "2025-05-01 09:35:00" },
  { prediction_id: 2, ecg_id: 2, patient_id: 102, disease_name: "Normal Sinus Rhythm", confidence_score: 88.2, risk_level: "Low", recommendation: "Maintain active lifestyle, regular annual cardiovascular checkup.", predicted_at: "2025-05-02 10:20:00" },
  { prediction_id: 3, ecg_id: 3, patient_id: 103, disease_name: "Normal Sinus Rhythm", confidence_score: 96.4, risk_level: "Low", recommendation: "No immediate threat, continue healthy diet and hydration.", predicted_at: "2025-05-05 08:05:00" },
  { prediction_id: 4, ecg_id: 4, patient_id: 104, disease_name: "Tachycardia & Heart Attack Risk", confidence_score: 91.0, risk_level: "High", recommendation: "EMERGENCY: Immediate clinical intervention required. Beta-blockers as directed.", predicted_at: "2025-05-06 12:30:00" }
];

const SEED_REPORTS: Report[] = [
  { report_id: 301, patient_id: 101, ecg_id: 1, generated_pdf: "/reports/report_101.pdf", doctor_notes: "Patient shows signs of premature ventricular contractions. Advised Holter monitoring.", generated_at: "2025-05-01 10:00:00" },
  { report_id: 302, patient_id: 104, ecg_id: 4, generated_pdf: "/reports/report_104.pdf", doctor_notes: "Severe sinus tachycardia noted. Administered IV Metoprolol. Stabilized and monitoring.", generated_at: "2025-05-06 13:00:00" }
];

const SEED_APPOINTMENTS: Appointment[] = [
  { appointment_id: 401, patient_id: 101, doctor_id: 201, appointment_date: "2025-05-18 10:00:00", status: "Scheduled" },
  { appointment_id: 402, patient_id: 102, doctor_id: 202, appointment_date: "2025-05-19 11:30:00", status: "Pending" },
  { appointment_id: 403, patient_id: 104, doctor_id: 201, appointment_date: "2025-05-17 16:00:00", status: "Completed" }
];

const SEED_AUDIT: AuditLog[] = [
  { log_id: 1, user_id: 5, username: "admin", role: "Admin", activity: "Initialized DB and loaded default configurations.", sql_query: "CREATE DATABASE ecg_heart_prediction;", timestamp: "2025-04-01 08:00:00", ip_address: "192.168.1.1", status: "SUCCESS", execution_time_ms: 15 },
  { log_id: 2, user_id: 3, username: "arjun.m", role: "Doctor", activity: "Loaded patients records from Fortis system.", sql_query: "SELECT * FROM patients WHERE doctor_id = 201;", timestamp: "2025-05-01 09:00:00", ip_address: "192.168.1.45", status: "SUCCESS", execution_time_ms: 4 }
];

export type AppRole = "Patient" | "Doctor" | "Admin";

class DatabaseEngine {
  public usersTable: User[] = [];
  public patientsTable: Patient[] = [];
  public doctorsTable: Doctor[] = [];
  public ecgRecordsTable: EcgRecord[] = [];
  public predictionsTable: Prediction[] = [];
  public reportsTable: Report[] = [];
  public appointmentsTable: Appointment[] = [];
  public auditLogsTable: AuditLog[] = [];

  private currentRole: AppRole = "Admin";
  private currentUserObj: User = SEED_USERS[4];
  private listeners: (() => void)[] = [];

  constructor() {
    this.loadAll();
    
    // Sync current role from localStorage
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("ecg-role") as AppRole;
      if (saved) {
        this.currentRole = saved;
        this.currentUserObj = this.usersTable.find((u) => u.role === saved) || this.usersTable[4];
      }
    }
  }

  private loadAll() {
    if (typeof window === "undefined") {
      this.usersTable = [...SEED_USERS];
      this.patientsTable = [...SEED_PATIENTS];
      this.doctorsTable = [...SEED_DOCTORS];
      this.ecgRecordsTable = [...SEED_ECG];
      this.predictionsTable = [...SEED_PREDICTIONS];
      this.reportsTable = [...SEED_REPORTS];
      this.appointmentsTable = [...SEED_APPOINTMENTS];
      this.auditLogsTable = [...SEED_AUDIT];
      return;
    }

    const seeded = localStorage.getItem("cp-db-seeded") === "true";
    if (seeded) {
      try {
        this.usersTable = JSON.parse(localStorage.getItem("cp-users") || "[]");
        this.patientsTable = JSON.parse(localStorage.getItem("cp-patients") || "[]");
        this.doctorsTable = JSON.parse(localStorage.getItem("cp-doctors") || "[]");
        this.ecgRecordsTable = JSON.parse(localStorage.getItem("cp-ecg") || "[]");
        this.predictionsTable = JSON.parse(localStorage.getItem("cp-predictions") || "[]");
        this.reportsTable = JSON.parse(localStorage.getItem("cp-reports") || "[]");
        this.appointmentsTable = JSON.parse(localStorage.getItem("cp-appointments") || "[]");
        this.auditLogsTable = JSON.parse(localStorage.getItem("cp-audit") || "[]");
        return;
      } catch (e) {
        console.error("Failed to parse LocalStorage database. Resetting seed...", e);
      }
    }

    // Default seed
    this.usersTable = [...SEED_USERS];
    this.patientsTable = [...SEED_PATIENTS];
    this.doctorsTable = [...SEED_DOCTORS];
    this.ecgRecordsTable = [...SEED_ECG];
    this.predictionsTable = [...SEED_PREDICTIONS];
    this.reportsTable = [...SEED_REPORTS];
    this.appointmentsTable = [...SEED_APPOINTMENTS];
    this.auditLogsTable = [...SEED_AUDIT];

    this.saveAll();
    localStorage.setItem("cp-db-seeded", "true");
  }

  public saveAll() {
    if (typeof window === "undefined") return;
    localStorage.setItem("cp-users", JSON.stringify(this.usersTable));
    localStorage.setItem("cp-patients", JSON.stringify(this.patientsTable));
    localStorage.setItem("cp-doctors", JSON.stringify(this.doctorsTable));
    localStorage.setItem("cp-ecg", JSON.stringify(this.ecgRecordsTable));
    localStorage.setItem("cp-predictions", JSON.stringify(this.predictionsTable));
    localStorage.setItem("cp-reports", JSON.stringify(this.reportsTable));
    localStorage.setItem("cp-appointments", JSON.stringify(this.appointmentsTable));
    localStorage.setItem("cp-audit", JSON.stringify(this.auditLogsTable));
  }

  getRole(): AppRole {
    return this.currentRole;
  }

  getCurrentUser(): User {
    return this.currentUserObj;
  }

  setRole(role: AppRole) {
    this.currentRole = role;
    this.currentUserObj = this.usersTable.find((u) => u.role === role) || this.usersTable[4];
    if (typeof window !== "undefined") {
      localStorage.setItem("ecg-role", role);
      localStorage.setItem("ecg-auth", role === "Admin" ? "1" : "0");
    }
    toast.info(`Switched role to: ${role} (SQL operations mapped dynamically)`);
    this.notify();
  }

  subscribe(listener: () => void) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter((l) => l !== listener);
    };
  }

  private notify() {
    this.listeners.forEach((l) => l());
  }

  // Record audit logs
  logQuery(sql: string, activity: string, status: "SUCCESS" | "FAILED" = "SUCCESS", executionTimeMs = 2) {
    const newLog: AuditLog = {
      log_id: this.auditLogsTable.length + 1,
      user_id: this.currentUserObj.user_id,
      username: this.currentUserObj.name.toLowerCase().replace(/\s/g, "."),
      role: this.currentRole,
      activity,
      sql_query: sql,
      timestamp: new Date().toISOString().replace("T", " ").substring(0, 19),
      ip_address: "127.0.0.1",
      status,
      execution_time_ms: executionTimeMs
    };
    this.auditLogsTable.unshift(newLog);
    this.saveAll();
    this.notify();
    
    if (typeof window !== "undefined") {
      window.dispatchEvent(new CustomEvent("ecg-sql-query", { detail: newLog }));
    }
  }

  // Safe client-side SQL parser
  execute(sql: string): { columns: string[]; rows: (string | number)[][]; affected?: string; error?: string } {
    const startTime = performance.now();
    const cleanSql = sql.trim().replace(/;$/, "");
    const lower = cleanSql.toLowerCase();

    if (lower.includes("drop database") || lower.includes("drop table") || lower.includes("truncate")) {
      const errMsg = "Access Denied: DROP DATABASE, DROP TABLE, and TRUNCATE operations are restricted.";
      this.logQuery(sql, "Executed destructive query (Blocked)", "FAILED", 1);
      return { columns: ["error"], rows: [[errMsg]], error: errMsg };
    }

    try {
      if (lower.startsWith("select") && lower.includes("from patients") && !lower.includes("join") && !lower.includes("where") && !lower.includes("count")) {
        this.logQuery(sql, "Queried patients table", "SUCCESS", Math.round(performance.now() - startTime));
        return {
          columns: ["patient_id", "user_id", "full_name", "age", "gender", "blood_group", "contact", "email"],
          rows: this.patientsTable.map((p) => [p.patient_id, p.user_id, p.full_name, p.age, p.gender, p.blood_group, p.contact, p.email])
        };
      }

      if (lower.startsWith("select") && lower.includes("from ecg_records") && !lower.includes("join") && !lower.includes("where")) {
        this.logQuery(sql, "Queried ecg_records table", "SUCCESS", Math.round(performance.now() - startTime));
        return {
          columns: ["ecg_id", "patient_id", "upload_url", "upload_type", "heart_rate", "qrs_duration", "uploaded_at"],
          rows: this.ecgRecordsTable.map((r) => [r.ecg_id, r.patient_id, r.upload_url, r.upload_type, r.heart_rate, r.qrs_duration, r.uploaded_at])
        };
      }

      if (lower.startsWith("select") && lower.includes("from predictions") && !lower.includes("join") && !lower.includes("where")) {
        this.logQuery(sql, "Queried predictions table", "SUCCESS", Math.round(performance.now() - startTime));
        return {
          columns: ["prediction_id", "ecg_id", "patient_id", "disease_name", "confidence_score", "risk_level"],
          rows: this.predictionsTable.map((p) => [p.prediction_id, p.ecg_id, p.patient_id, p.disease_name, p.confidence_score, p.risk_level])
        };
      }

      if (lower.startsWith("select") && lower.includes("from users") && !lower.includes("where")) {
        this.logQuery(sql, "Queried users table", "SUCCESS", Math.round(performance.now() - startTime));
        return {
          columns: ["user_id", "name", "email", "role", "created_at"],
          rows: this.usersTable.map((u) => [u.user_id, u.name, u.email, u.role, u.created_at])
        };
      }

      if (lower.includes("join patients") || lower.includes("join ecg_records") || lower.includes("join predictions")) {
        this.logQuery(sql, "Executed multi-table JOIN query", "SUCCESS", Math.round(performance.now() - startTime));
        const merged = this.patientsTable.map((p) => {
          const e = this.ecgRecordsTable.find((rec) => rec.patient_id === p.patient_id);
          const pr = this.predictionsTable.find((pred) => pred.patient_id === p.patient_id);
          return { p, e, pr };
        }).filter((x) => x.e && x.pr);

        return {
          columns: ["patient_id", "full_name", "heart_rate", "disease_name", "confidence_score", "risk_level"],
          rows: merged.map((m) => [
            m.p.patient_id,
            m.p.full_name,
            m.e!.heart_rate,
            m.pr!.disease_name,
            m.pr!.confidence_score,
            m.pr!.risk_level
          ])
        };
      }

      if (lower.includes("count(*)")) {
        this.logQuery(sql, "Executed aggregate COUNT query", "SUCCESS", Math.round(performance.now() - startTime));
        if (lower.includes("patients")) return { columns: ["COUNT(*)"], rows: [[this.patientsTable.length]] };
        if (lower.includes("predictions")) return { columns: ["COUNT(*)"], rows: [[this.predictionsTable.length]] };
        if (lower.includes("ecg_records")) return { columns: ["COUNT(*)"], rows: [[this.ecgRecordsTable.length]] };
      }

      if (lower.includes("avg(heart_rate)")) {
        this.logQuery(sql, "Executed aggregate AVG query", "SUCCESS", Math.round(performance.now() - startTime));
        const avg = this.ecgRecordsTable.reduce((s, r) => s + r.heart_rate, 0) / this.ecgRecordsTable.length;
        return { columns: ["AVG(heart_rate)"], rows: [[+avg.toFixed(2)]] };
      }

      // Simulate generic select
      this.logQuery(sql, "Executed custom SELECT query", "SUCCESS", Math.round(performance.now() - startTime));
      return {
        columns: ["column_name", "data_type", "nullable", "key_type"],
        rows: [
          ["patient_id", "INT", "NO", "PRI"],
          ["user_id", "INT", "NO", "MUL"],
          ["full_name", "VARCHAR(100)", "NO", ""]
        ]
      };
    } catch (e: any) {
      this.logQuery(sql, `SQL execution failed: ${e.message}`, "FAILED", Math.round(performance.now() - startTime));
      return { columns: ["error"], rows: [[e.message]], error: e.message };
    }
  }

  insertPatient(patient: Omit<Patient, "patient_id" | "user_id" | "created_at">) {
    const newUserId = this.usersTable.length + 1;
    const newPatientId = this.patientsTable.length > 0 
      ? this.patientsTable[this.patientsTable.length - 1].patient_id + 1 
      : 101;
    const timestamp = new Date().toISOString().replace("T", " ").substring(0, 19);

    const newUser: User = {
      user_id: newUserId,
      name: patient.full_name,
      email: patient.email,
      password_hash: "$2b$12$eImiTX..SimulatedHashVal",
      role: "Patient",
      created_at: timestamp
    };
    this.usersTable.push(newUser);

    const newPatient: Patient = {
      ...patient,
      patient_id: newPatientId,
      user_id: newUserId,
      created_at: timestamp
    };
    this.patientsTable.push(newPatient);
    
    // Persist permanently!
    this.saveAll();

    const sql = `INSERT INTO users (name, email, password_hash, role) VALUES ('${patient.full_name}', '${patient.email}', '...', 'Patient');\nINSERT INTO patients (user_id, age, gender, blood_group, contact, medical_history) VALUES (${newUserId}, ${patient.age}, '${patient.gender}', '${patient.blood_group}', '${patient.contact}', '${patient.medical_history}');`;
    this.logQuery(sql, `Created patient ${patient.full_name} and mapped user_id ${newUserId}`);
    this.notify();
    return newPatient;
  }

  insertEcg(ecg: Omit<EcgRecord, "ecg_id" | "uploaded_at">) {
    const newEcgId = this.ecgRecordsTable.length + 1;
    const timestamp = new Date().toISOString().replace("T", " ").substring(0, 19);

    const newEcg: EcgRecord = {
      ...ecg,
      ecg_id: newEcgId,
      uploaded_at: timestamp
    };
    this.ecgRecordsTable.push(newEcg);
    this.saveAll();

    const sql = `INSERT INTO ecg_records (patient_id, upload_url, upload_type, heart_rate, qrs_duration, pr_interval, qt_interval, ecg_signal) VALUES (${ecg.patient_id}, '${ecg.upload_url}', '${ecg.upload_type}', ${ecg.heart_rate}, ${ecg.qrs_duration}, ${ecg.pr_interval}, ${ecg.qt_interval}, 'Lead II Signal');`;
    this.logQuery(sql, `Uploaded ECG report for patient_id ${ecg.patient_id}`);
    this.notify();
    return newEcg;
  }

  insertPrediction(pred: Omit<Prediction, "prediction_id" | "predicted_at">) {
    const newPredId = this.predictionsTable.length + 1;
    const timestamp = new Date().toISOString().replace("T", " ").substring(0, 19);

    const newPred: Prediction = {
      ...pred,
      prediction_id: newPredId,
      predicted_at: timestamp
    };
    this.predictionsTable.push(newPred);
    this.saveAll();

    const sql = `INSERT INTO predictions (ecg_id, patient_id, disease_name, confidence_score, risk_level, recommendation) VALUES (${pred.ecg_id}, ${pred.patient_id}, '${pred.disease_name}', ${pred.confidence_score}, '${pred.risk_level}', '${pred.recommendation.replace(/'/g, "''")}');`;
    this.logQuery(sql, `Generated AI prediction for ecg_id ${pred.ecg_id}`);
    this.notify();
    return newPred;
  }

  deletePatient(patientId: number) {
    this.patientsTable = this.patientsTable.filter((p) => p.patient_id !== patientId);
    this.saveAll();
    
    const sql = `DELETE FROM patients WHERE patient_id = ${patientId};`;
    this.logQuery(sql, `Deleted patient record #${patientId} (CASCADE triggers applied)`);
    this.notify();
  }

  updatePrediction(predictionId: number, riskLevel: "Low" | "Medium" | "High", diseaseName?: string) {
    this.predictionsTable = this.predictionsTable.map((p) => {
      if (p.prediction_id === predictionId) {
        return {
          ...p,
          risk_level: riskLevel,
          disease_name: diseaseName || p.disease_name
        };
      }
      return p;
    });
    this.saveAll();

    const sql = `UPDATE predictions SET risk_level = '${riskLevel}'${diseaseName ? `, disease_name = '${diseaseName}'` : ""} WHERE prediction_id = ${predictionId};`;
    this.logQuery(sql, `Updated prediction assessment for prediction #${predictionId}`);
    this.notify();
  }

  addDoctorNote(reportId: number, notes: string) {
    this.reportsTable = this.reportsTable.map((r) => {
      if (r.report_id === reportId) {
        return { ...r, doctor_notes: notes };
      }
      return r;
    });
    this.saveAll();
    
    const sql = `UPDATE reports SET doctor_notes = '${notes.replace(/'/g, "''")}' WHERE report_id = ${reportId};`;
    this.logQuery(sql, `Annotated diagnostic notes on report #${reportId}`);
    this.notify();
  }
}

export const db = new DatabaseEngine();
