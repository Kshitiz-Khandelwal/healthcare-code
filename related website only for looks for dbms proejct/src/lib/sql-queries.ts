export type SqlQueryDef = {
  id: string;
  title: string;
  category: "DDL" | "DML" | "Query" | "Auth" | "Analytics" | "View";
  sql: string;
  description: string;
  run: () => { columns: string[]; rows: (string | number)[][]; affected?: string };
};

import { patients, ecgRecords, predictions, ecgDataset } from "./mock-data";

const toRows = <T extends Record<string, any>>(arr: T[], cols: (keyof T)[]) =>
  arr.map((r) => cols.map((c) => r[c] as string | number));

export const sqlQueries: SqlQueryDef[] = [
  {
    id: "create-db",
    title: "Create Database",
    category: "DDL",
    description: "Initialize the ECG heart prediction database.",
    sql: `CREATE DATABASE ecg_heart_prediction;\nUSE ecg_heart_prediction;`,
    run: () => ({ columns: ["status"], rows: [["Database 'ecg_heart_prediction' created"]], affected: "OK" }),
  },
  {
    id: "create-patients",
    title: "Create Patients Table",
    category: "DDL",
    description: "Stores patient demographics.",
    sql: `CREATE TABLE patients (\n  patient_id INT PRIMARY KEY AUTO_INCREMENT,\n  full_name VARCHAR(100),\n  age INT,\n  gender VARCHAR(10),\n  phone VARCHAR(15),\n  email VARCHAR(100),\n  address TEXT,\n  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n);`,
    run: () => ({ columns: ["status"], rows: [["Table 'patients' created"]], affected: "OK" }),
  },
  {
    id: "insert-patient",
    title: "Insert Patient",
    category: "DML",
    description: "Add a new patient record.",
    sql: `INSERT INTO patients (full_name, age, gender, phone, email, address)\nVALUES ('Rahul Sharma', 45, 'Male', '9876543210', 'rahul@gmail.com', 'Bangalore');`,
    run: () => ({ columns: ["status"], rows: [["1 row inserted (patient_id=1)"]], affected: "1 row" }),
  },
  {
    id: "view-patients",
    title: "View All Patients",
    category: "Query",
    description: "Returns every patient row.",
    sql: `SELECT * FROM patients;`,
    run: () => ({
      columns: ["patient_id", "full_name", "age", "gender", "phone", "email", "address"],
      rows: toRows(patients, ["patient_id", "full_name", "age", "gender", "phone", "email", "address"]),
    }),
  },
  {
    id: "create-ecg",
    title: "Create ECG Records Table",
    category: "DDL",
    description: "Stores ECG signal measurements.",
    sql: `CREATE TABLE ecg_records (\n  ecg_id INT PRIMARY KEY AUTO_INCREMENT,\n  patient_id INT,\n  heart_rate INT,\n  qrs_duration FLOAT,\n  pr_interval FLOAT,\n  qt_interval FLOAT,\n  ecg_signal TEXT,\n  recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n  FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE\n);`,
    run: () => ({ columns: ["status"], rows: [["Table 'ecg_records' created"]], affected: "OK" }),
  },
  {
    id: "insert-ecg",
    title: "Insert ECG Record",
    category: "DML",
    description: "Save a new ECG measurement.",
    sql: `INSERT INTO ecg_records (patient_id, heart_rate, qrs_duration, pr_interval, qt_interval, ecg_signal)\nVALUES (1, 92, 0.11, 0.18, 0.42, 'ECG_SIGNAL_DATA');`,
    run: () => ({ columns: ["status"], rows: [["1 row inserted (ecg_id=1)"]], affected: "1 row" }),
  },
  {
    id: "view-ecg",
    title: "View ECG Records",
    category: "Query",
    sql: `SELECT * FROM ecg_records;`,
    description: "All ECG measurements stored.",
    run: () => ({
      columns: ["ecg_id", "patient_id", "heart_rate", "qrs_duration", "pr_interval", "qt_interval"],
      rows: toRows(ecgRecords, ["ecg_id", "patient_id", "heart_rate", "qrs_duration", "pr_interval", "qt_interval"]),
    }),
  },
  {
    id: "create-predictions",
    title: "Create Predictions Table",
    category: "DDL",
    description: "Stores AI prediction outputs.",
    sql: `CREATE TABLE predictions (\n  prediction_id INT PRIMARY KEY AUTO_INCREMENT,\n  patient_id INT,\n  ecg_id INT,\n  disease_prediction VARCHAR(100),\n  confidence_score FLOAT,\n  risk_level VARCHAR(20),\n  prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n  FOREIGN KEY (patient_id) REFERENCES patients(patient_id),\n  FOREIGN KEY (ecg_id) REFERENCES ecg_records(ecg_id)\n);`,
    run: () => ({ columns: ["status"], rows: [["Table 'predictions' created"]], affected: "OK" }),
  },
  {
    id: "insert-prediction",
    title: "Insert Prediction",
    category: "DML",
    sql: `INSERT INTO predictions (patient_id, ecg_id, disease_prediction, confidence_score, risk_level)\nVALUES (1, 1, 'Possible Arrhythmia', 94.5, 'High');`,
    description: "Record an AI prediction.",
    run: () => ({ columns: ["status"], rows: [["1 row inserted (prediction_id=1)"]], affected: "1 row" }),
  },
  {
    id: "view-predictions",
    title: "View Predictions",
    category: "Query",
    sql: `SELECT * FROM predictions;`,
    description: "All AI prediction results.",
    run: () => ({
      columns: ["prediction_id", "patient_id", "ecg_id", "disease_prediction", "confidence_score", "risk_level"],
      rows: toRows(predictions, ["prediction_id", "patient_id", "ecg_id", "disease_prediction", "confidence_score", "risk_level"]),
    }),
  },
  {
    id: "create-users",
    title: "Create Users Table",
    category: "Auth",
    sql: `CREATE TABLE users (\n  user_id INT PRIMARY KEY AUTO_INCREMENT,\n  username VARCHAR(50) UNIQUE,\n  password VARCHAR(255),\n  role VARCHAR(20)\n);`,
    description: "Authentication table.",
    run: () => ({ columns: ["status"], rows: [["Table 'users' created"]], affected: "OK" }),
  },
  {
    id: "insert-admin",
    title: "Insert Admin User",
    category: "Auth",
    sql: `INSERT INTO users (username, password, role)\nVALUES ('admin', 'admin123', 'Admin');`,
    description: "Seed default admin account.",
    run: () => ({ columns: ["status"], rows: [["1 row inserted (user_id=1)"]], affected: "1 row" }),
  },
  {
    id: "login-query",
    title: "Login Query",
    category: "Auth",
    sql: `SELECT * FROM users WHERE username='admin' AND password='admin123';`,
    description: "Verify admin credentials.",
    run: () => ({ columns: ["user_id", "username", "role"], rows: [[1, "admin", "Admin"]] }),
  },
  {
    id: "patient-report",
    title: "Complete Patient Report (JOIN)",
    category: "Query",
    sql: `SELECT p.patient_id, p.full_name, p.age, p.gender,\n  e.heart_rate, e.qrs_duration, e.pr_interval, e.qt_interval,\n  pr.disease_prediction, pr.confidence_score, pr.risk_level\nFROM patients p\nJOIN ecg_records e ON p.patient_id = e.patient_id\nJOIN predictions pr ON e.ecg_id = pr.ecg_id;`,
    description: "Three-table join — full report.",
    run: () => {
      const rows = patients
        .map((p) => {
          const e = ecgRecords.find((x) => x.patient_id === p.patient_id);
          const pr = predictions.find((x) => x.patient_id === p.patient_id);
          if (!e || !pr) return null;
          return [p.patient_id, p.full_name, p.age, p.gender, e.heart_rate, e.qrs_duration, pr.disease_prediction, pr.confidence_score, pr.risk_level];
        })
        .filter(Boolean) as (string | number)[][];
      return { columns: ["patient_id", "full_name", "age", "gender", "heart_rate", "qrs_duration", "disease_prediction", "confidence_score", "risk_level"], rows };
    },
  },
  {
    id: "high-risk",
    title: "High Risk Patients",
    category: "Analytics",
    sql: `SELECT p.full_name, pr.disease_prediction, pr.risk_level\nFROM patients p\nJOIN predictions pr ON p.patient_id = pr.patient_id\nWHERE pr.risk_level = 'High';`,
    description: "Filter — only high risk.",
    run: () => {
      const rows = predictions
        .filter((p) => p.risk_level === "High")
        .map((pr) => {
          const p = patients.find((x) => x.patient_id === pr.patient_id)!;
          return [p.full_name, pr.disease_prediction, pr.risk_level];
        });
      return { columns: ["full_name", "disease_prediction", "risk_level"], rows };
    },
  },
  {
    id: "total-patients",
    title: "Total Patients",
    category: "Analytics",
    sql: `SELECT COUNT(*) AS total_patients FROM patients;`,
    description: "Aggregate count.",
    run: () => ({ columns: ["total_patients"], rows: [[patients.length]] }),
  },
  {
    id: "avg-hr",
    title: "Average Heart Rate",
    category: "Analytics",
    sql: `SELECT AVG(heart_rate) AS avg_heart_rate FROM ecg_records;`,
    description: "Mean heart rate across all ECGs.",
    run: () => {
      const avg = ecgRecords.reduce((s, r) => s + r.heart_rate, 0) / ecgRecords.length;
      return { columns: ["avg_heart_rate"], rows: [[+avg.toFixed(2)]] };
    },
  },
  {
    id: "delete-patient",
    title: "Delete Patient",
    category: "DML",
    sql: `DELETE FROM patients WHERE patient_id = 1;`,
    description: "Remove a patient (cascades to ECG).",
    run: () => ({ columns: ["status"], rows: [["1 row deleted (cascade applied)"]], affected: "1 row" }),
  },
  {
    id: "update-prediction",
    title: "Update Prediction",
    category: "DML",
    sql: `UPDATE predictions SET risk_level = 'Medium' WHERE prediction_id = 1;`,
    description: "Modify a risk level.",
    run: () => ({ columns: ["status"], rows: [["1 row updated"]], affected: "1 row" }),
  },
  {
    id: "search-patient",
    title: "Search Patient (LIKE)",
    category: "Query",
    sql: `SELECT * FROM patients WHERE full_name LIKE '%Rahul%';`,
    description: "Pattern match on name.",
    run: () => {
      const rows = patients
        .filter((p) => p.full_name.toLowerCase().includes("rahul"))
        .map((p) => [p.patient_id, p.full_name, p.age, p.gender, p.email]);
      return { columns: ["patient_id", "full_name", "age", "gender", "email"], rows };
    },
  },
  {
    id: "create-dataset",
    title: "Create ECG Dataset Table",
    category: "DDL",
    sql: `CREATE TABLE ecg_dataset (\n  data_id INT PRIMARY KEY AUTO_INCREMENT,\n  age INT, sex INT, chest_pain_type INT,\n  resting_bp FLOAT, cholesterol FLOAT,\n  fasting_sugar INT, resting_ecg INT,\n  max_heart_rate FLOAT, exercise_angina INT,\n  oldpeak FLOAT, target INT\n);`,
    description: "ML training dataset table.",
    run: () => ({ columns: ["status"], rows: [["Table 'ecg_dataset' created"]], affected: "OK" }),
  },
  {
    id: "export-dataset",
    title: "Export Dataset",
    category: "Query",
    sql: `SELECT * FROM ecg_dataset;`,
    description: "Full ML dataset.",
    run: () => ({
      columns: ["data_id", "age", "sex", "resting_bp", "cholesterol", "max_heart_rate", "oldpeak", "target"],
      rows: ecgDataset.map((d) => [d.data_id, d.age, d.sex, d.resting_bp, d.cholesterol, d.max_heart_rate, d.oldpeak, d.target]),
    }),
  },
  {
    id: "create-view",
    title: "Create Patient Dashboard VIEW",
    category: "View",
    sql: `CREATE VIEW patient_dashboard AS\nSELECT p.full_name, e.heart_rate, pr.disease_prediction, pr.risk_level\nFROM patients p\nJOIN ecg_records e ON p.patient_id = e.patient_id\nJOIN predictions pr ON e.ecg_id = pr.ecg_id;`,
    description: "Reusable dashboard view.",
    run: () => ({ columns: ["status"], rows: [["View 'patient_dashboard' created"]], affected: "OK" }),
  },
  {
    id: "view-dashboard",
    title: "Query Dashboard View",
    category: "View",
    sql: `SELECT * FROM patient_dashboard;`,
    description: "Read from the view.",
    run: () => {
      const rows = patients
        .map((p) => {
          const e = ecgRecords.find((x) => x.patient_id === p.patient_id);
          const pr = predictions.find((x) => x.patient_id === p.patient_id);
          if (!e || !pr) return null;
          return [p.full_name, e.heart_rate, pr.disease_prediction, pr.risk_level];
        })
        .filter(Boolean) as (string | number)[][];
      return { columns: ["full_name", "heart_rate", "disease_prediction", "risk_level"], rows };
    },
  },
  {
    id: "recent-predictions",
    title: "Recent Predictions (LIMIT)",
    category: "Analytics",
    sql: `SELECT * FROM predictions ORDER BY prediction_date DESC LIMIT 5;`,
    description: "Latest 5 predictions.",
    run: () => {
      const rows = [...predictions]
        .sort((a, b) => b.prediction_date.localeCompare(a.prediction_date))
        .slice(0, 5)
        .map((p) => [p.prediction_id, p.patient_id, p.disease_prediction, p.confidence_score, p.risk_level, p.prediction_date]);
      return { columns: ["prediction_id", "patient_id", "disease_prediction", "confidence_score", "risk_level", "prediction_date"], rows };
    },
  },
  {
    id: "critical-hr",
    title: "Critical Heart Rate (> 100)",
    category: "Analytics",
    sql: `SELECT p.full_name, e.heart_rate\nFROM patients p\nJOIN ecg_records e ON p.patient_id = e.patient_id\nWHERE e.heart_rate > 100;`,
    description: "Patients with tachycardia.",
    run: () => {
      const rows = ecgRecords
        .filter((e) => e.heart_rate > 100)
        .map((e) => {
          const p = patients.find((x) => x.patient_id === e.patient_id)!;
          return [p.full_name, e.heart_rate];
        });
      return { columns: ["full_name", "heart_rate"], rows };
    },
  },
];