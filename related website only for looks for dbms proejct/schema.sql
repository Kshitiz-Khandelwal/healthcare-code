-- ==========================================================
-- CARDIOPREDICT SYSTEM DATABASE SCHEMA (PostgreSQL / Supabase)
-- Target Engine: PostgreSQL 14+ / MySQL 8.0+
-- File: schema.sql
-- ==========================================================

-- 1. Create users lookup table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('Patient', 'Doctor', 'Admin')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Create doctors entity table
CREATE TABLE doctors (
    doctor_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    full_name VARCHAR(100) NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    hospital VARCHAR(150) NOT NULL,
    experience INT NOT NULL CHECK (experience >= 0),
    contact VARCHAR(15) UNIQUE,
    email VARCHAR(150) UNIQUE,
    CONSTRAINT fk_doctor_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 3. Create patients entity table
CREATE TABLE patients (
    patient_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    full_name VARCHAR(100) NOT NULL,
    age INT NOT NULL CHECK (age >= 0 AND age <= 130),
    gender VARCHAR(10) CHECK (gender IN ('Male', 'Female', 'Other')),
    blood_group VARCHAR(5) NOT NULL,
    contact VARCHAR(15) NOT NULL,
    medical_history TEXT,
    email VARCHAR(150) UNIQUE,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_patient_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 4. Create ecg_records table
CREATE TABLE ecg_records (
    ecg_id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL REFERENCES patients(patient_id) ON DELETE CASCADE,
    upload_url VARCHAR(255) NOT NULL,
    upload_type VARCHAR(10) CHECK (upload_type IN ('image', 'csv', 'pdf')),
    heart_rate INT NOT NULL CHECK (heart_rate >= 0),
    qrs_duration DECIMAL(5,3) NOT NULL,
    pr_interval DECIMAL(5,3) NOT NULL,
    qt_interval DECIMAL(5,3) NOT NULL,
    ecg_signal TEXT, -- Waveform coordinates
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_ecg_patient FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
);

-- 5. Create predictions table (ML classifications output)
CREATE TABLE predictions (
    prediction_id SERIAL PRIMARY KEY,
    ecg_id INT NOT NULL REFERENCES ecg_records(ecg_id) ON DELETE CASCADE,
    patient_id INT NOT NULL REFERENCES patients(patient_id) ON DELETE CASCADE,
    disease_name VARCHAR(100) NOT NULL,
    confidence_score DECIMAL(5,2) NOT NULL CHECK (confidence_score >= 0.00 AND confidence_score <= 100.00),
    risk_level VARCHAR(10) CHECK (risk_level IN ('Low', 'Medium', 'High')),
    recommendation TEXT,
    predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_pred_ecg FOREIGN KEY (ecg_id) REFERENCES ecg_records(ecg_id) ON DELETE CASCADE,
    CONSTRAINT fk_pred_patient FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
);

-- 6. Create clinical reports view-sync table
CREATE TABLE reports (
    report_id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL REFERENCES patients(patient_id) ON DELETE CASCADE,
    ecg_id INT NOT NULL REFERENCES ecg_records(ecg_id) ON DELETE CASCADE,
    generated_pdf VARCHAR(255) NOT NULL,
    doctor_notes TEXT DEFAULT 'No clinical annotations added yet.',
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_report_patient FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    CONSTRAINT fk_report_ecg FOREIGN KEY (ecg_id) REFERENCES ecg_records(ecg_id) ON DELETE CASCADE
);

-- 7. Create clinic appointments table
CREATE TABLE appointments (
    appointment_id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL REFERENCES patients(patient_id) ON DELETE CASCADE,
    doctor_id INT NOT NULL REFERENCES doctors(doctor_id) ON DELETE CASCADE,
    appointment_date TIMESTAMP NOT NULL,
    status VARCHAR(15) DEFAULT 'Pending' CHECK (status IN ('Pending', 'Scheduled', 'Completed', 'Cancelled')),
    CONSTRAINT fk_app_patient FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    CONSTRAINT fk_app_doctor FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE
);

-- 8. Create security audit logging tables
CREATE TABLE audit_logs (
    log_id SERIAL PRIMARY KEY,
    user_id INT,
    username VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL,
    activity VARCHAR(255) NOT NULL,
    sql_query TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    status VARCHAR(10) CHECK (status IN ('SUCCESS', 'FAILED')),
    execution_time_ms INT
);

-- ==========================================================
-- INDEXES & PERFORMANCE OPTIMIZATION
-- ==========================================================
CREATE INDEX idx_patient_user ON patients(user_id);
CREATE INDEX idx_ecg_patient ON ecg_records(patient_id);
CREATE INDEX idx_prediction_patient ON predictions(patient_id);
CREATE INDEX idx_appointment_doctor ON appointments(doctor_id);

-- ==========================================================
-- THREE-TABLE JOIN VIEW (Visual reporting shortcut)
-- ==========================================================
CREATE OR REPLACE VIEW patient_diagnoses_view AS
SELECT 
    p.patient_id,
    p.full_name,
    p.age,
    p.gender,
    e.heart_rate,
    e.qrs_duration,
    pr.disease_name,
    pr.risk_level,
    rep.doctor_notes
FROM patients p
JOIN ecg_records e ON p.patient_id = e.patient_id
JOIN predictions pr ON e.ecg_id = pr.ecg_id
LEFT JOIN reports rep ON p.patient_id = rep.patient_id AND e.ecg_id = rep.ecg_id;
