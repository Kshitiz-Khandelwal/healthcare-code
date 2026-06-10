export type Patient = {
  patient_id: number;
  full_name: string;
  age: number;
  gender: string;
  phone: string;
  email: string;
  address: string;
  created_at: string;
};

export type EcgRecord = {
  ecg_id: number;
  patient_id: number;
  heart_rate: number;
  qrs_duration: number;
  pr_interval: number;
  qt_interval: number;
  ecg_signal: string;
  recorded_at: string;
};

export type Prediction = {
  prediction_id: number;
  patient_id: number;
  ecg_id: number;
  disease_prediction: string;
  confidence_score: number;
  risk_level: "Low" | "Medium" | "High";
  prediction_date: string;
};

export const patients: Patient[] = [
  { patient_id: 1, full_name: "Rahul Sharma", age: 45, gender: "Male", phone: "9876543210", email: "rahul@gmail.com", address: "Bangalore", created_at: "2025-04-12 09:14" },
  { patient_id: 2, full_name: "Priya Verma", age: 38, gender: "Female", phone: "9123456701", email: "priya.v@gmail.com", address: "Mumbai", created_at: "2025-04-15 11:02" },
  { patient_id: 3, full_name: "Arjun Mehta", age: 56, gender: "Male", phone: "9988776655", email: "arjun.m@gmail.com", address: "Delhi", created_at: "2025-04-18 14:30" },
  { patient_id: 4, full_name: "Sneha Iyer", age: 29, gender: "Female", phone: "9001122334", email: "sneha.i@gmail.com", address: "Chennai", created_at: "2025-04-20 08:45" },
  { patient_id: 5, full_name: "Vikram Singh", age: 62, gender: "Male", phone: "9876501234", email: "vikram.s@gmail.com", address: "Jaipur", created_at: "2025-04-22 16:10" },
  { patient_id: 6, full_name: "Anjali Nair", age: 41, gender: "Female", phone: "9090909090", email: "anjali.n@gmail.com", address: "Kochi", created_at: "2025-04-25 10:20" },
  { patient_id: 7, full_name: "Karan Patel", age: 50, gender: "Male", phone: "9786543210", email: "karan.p@gmail.com", address: "Ahmedabad", created_at: "2025-04-27 13:55" },
];

export const ecgRecords: EcgRecord[] = [
  { ecg_id: 1, patient_id: 1, heart_rate: 92, qrs_duration: 0.11, pr_interval: 0.18, qt_interval: 0.42, ecg_signal: "ECG_SIGNAL_DATA", recorded_at: "2025-05-01 09:30" },
  { ecg_id: 2, patient_id: 2, heart_rate: 78, qrs_duration: 0.09, pr_interval: 0.16, qt_interval: 0.40, ecg_signal: "ECG_SIGNAL_DATA", recorded_at: "2025-05-02 10:15" },
  { ecg_id: 3, patient_id: 3, heart_rate: 110, qrs_duration: 0.13, pr_interval: 0.20, qt_interval: 0.45, ecg_signal: "ECG_SIGNAL_DATA", recorded_at: "2025-05-03 11:40" },
  { ecg_id: 4, patient_id: 4, heart_rate: 72, qrs_duration: 0.08, pr_interval: 0.15, qt_interval: 0.38, ecg_signal: "ECG_SIGNAL_DATA", recorded_at: "2025-05-05 08:00" },
  { ecg_id: 5, patient_id: 5, heart_rate: 105, qrs_duration: 0.12, pr_interval: 0.19, qt_interval: 0.44, ecg_signal: "ECG_SIGNAL_DATA", recorded_at: "2025-05-06 12:25" },
  { ecg_id: 6, patient_id: 6, heart_rate: 85, qrs_duration: 0.10, pr_interval: 0.17, qt_interval: 0.41, ecg_signal: "ECG_SIGNAL_DATA", recorded_at: "2025-05-07 14:00" },
  { ecg_id: 7, patient_id: 7, heart_rate: 98, qrs_duration: 0.11, pr_interval: 0.18, qt_interval: 0.43, ecg_signal: "ECG_SIGNAL_DATA", recorded_at: "2025-05-08 09:50" },
];

export const predictions: Prediction[] = [
  { prediction_id: 1, patient_id: 1, ecg_id: 1, disease_prediction: "Possible Arrhythmia", confidence_score: 94.5, risk_level: "High", prediction_date: "2025-05-01 09:35" },
  { prediction_id: 2, patient_id: 2, ecg_id: 2, disease_prediction: "Normal Sinus Rhythm", confidence_score: 88.2, risk_level: "Low", prediction_date: "2025-05-02 10:20" },
  { prediction_id: 3, patient_id: 3, ecg_id: 3, disease_prediction: "Tachycardia", confidence_score: 91.0, risk_level: "High", prediction_date: "2025-05-03 11:45" },
  { prediction_id: 4, patient_id: 4, ecg_id: 4, disease_prediction: "Normal Sinus Rhythm", confidence_score: 96.4, risk_level: "Low", prediction_date: "2025-05-05 08:05" },
  { prediction_id: 5, patient_id: 5, ecg_id: 5, disease_prediction: "Atrial Fibrillation", confidence_score: 89.7, risk_level: "High", prediction_date: "2025-05-06 12:30" },
  { prediction_id: 6, patient_id: 6, ecg_id: 6, disease_prediction: "Mild Bradycardia Risk", confidence_score: 76.3, risk_level: "Medium", prediction_date: "2025-05-07 14:05" },
  { prediction_id: 7, patient_id: 7, ecg_id: 7, disease_prediction: "Borderline Arrhythmia", confidence_score: 82.1, risk_level: "Medium", prediction_date: "2025-05-08 09:55" },
];

export const ecgDataset = [
  { data_id: 1, age: 52, sex: 1, chest_pain_type: 2, resting_bp: 130, cholesterol: 250, fasting_sugar: 0, resting_ecg: 1, max_heart_rate: 170, exercise_angina: 0, oldpeak: 1.2, target: 1 },
  { data_id: 2, age: 41, sex: 0, chest_pain_type: 1, resting_bp: 120, cholesterol: 210, fasting_sugar: 0, resting_ecg: 0, max_heart_rate: 165, exercise_angina: 0, oldpeak: 0.8, target: 0 },
  { data_id: 3, age: 67, sex: 1, chest_pain_type: 3, resting_bp: 140, cholesterol: 286, fasting_sugar: 1, resting_ecg: 2, max_heart_rate: 108, exercise_angina: 1, oldpeak: 2.4, target: 1 },
  { data_id: 4, age: 35, sex: 0, chest_pain_type: 0, resting_bp: 110, cholesterol: 190, fasting_sugar: 0, resting_ecg: 0, max_heart_rate: 180, exercise_angina: 0, oldpeak: 0.0, target: 0 },
];

export function generateEcgWave(points = 200, hr = 80) {
  const data: { x: number; y: number }[] = [];
  const period = 60 / hr;
  for (let i = 0; i < points; i++) {
    const t = (i / points) * period * 4;
    const phase = (t % period) / period;
    let y = 0;
    if (phase < 0.1) y = Math.sin(phase * Math.PI * 10) * 0.1;
    else if (phase < 0.18) y = 0;
    else if (phase < 0.22) y = -0.15;
    else if (phase < 0.26) y = 1.4;
    else if (phase < 0.3) y = -0.35;
    else if (phase < 0.5) y = Math.sin((phase - 0.3) * Math.PI * 5) * 0.25;
    data.push({ x: i, y: +y.toFixed(3) });
  }
  return data;
}

export const heartRateTrend = [
  { day: "Mon", avg: 78 },
  { day: "Tue", avg: 82 },
  { day: "Wed", avg: 91 },
  { day: "Thu", avg: 86 },
  { day: "Fri", avg: 95 },
  { day: "Sat", avg: 88 },
  { day: "Sun", avg: 84 },
];

export const diseaseDistribution = [
  { name: "Normal", value: 2, color: "oklch(0.65 0.18 155)" },
  { name: "Arrhythmia", value: 2, color: "oklch(0.6 0.24 25)" },
  { name: "Tachycardia", value: 1, color: "oklch(0.78 0.16 75)" },
  { name: "Atrial Fib.", value: 1, color: "oklch(0.55 0.18 280)" },
  { name: "Bradycardia", value: 1, color: "oklch(0.55 0.18 200)" },
];