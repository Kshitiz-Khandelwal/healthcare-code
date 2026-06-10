# 🫀 CardioPredict — AI-Powered Cardiac Diagnostic DBMS Portal

> A full-stack relational database management system for cardiac health analysis, powered by AI diagnostics, real-time ECG telemetry simulation, multi-role access control, and live SQL query execution.

![CardioPredict Banner](https://img.shields.io/badge/CardioPredict-DBMS%20Portal-red?style=for-the-badge&logo=heart&logoColor=white)
![React](https://img.shields.io/badge/React-18-blue?style=for-the-badge&logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5-blue?style=for-the-badge&logo=typescript)
![Vite](https://img.shields.io/badge/Vite-7-purple?style=for-the-badge&logo=vite)
![Supabase](https://img.shields.io/badge/Supabase-Remote%20DB-green?style=for-the-badge&logo=supabase)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Database Schema](#database-schema)
- [Roles & Access Control](#roles--access-control)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Demo Credentials](#demo-credentials)
- [API Keys & Environment](#api-keys--environment)
- [Screenshots](#screenshots)

---

## 🧠 Overview

**CardioPredict** is a comprehensive healthcare DBMS portal built as a Database Management Systems (DBMS) academic project. It simulates a real-world relational database environment for a cardiology clinic, featuring:

- **Normalized relational schema** (PostgreSQL-style) with 8 interconnected tables
- **AI-powered cardiac disease prediction** using the Gemini API
- **Real-time ECG telemetry waveform** simulation (Lead II)
- **Multi-role authentication** (Admin, Doctor, Patient)
- **Live SQL console** showing every operation as real PostgreSQL queries
- **Persistent LocalStorage database** — all data survives page refreshes
- **Supabase remote sync** — push local DBMS state to a real cloud database

---

## ✨ Features

### 🔐 Authentication & Roles
- Role-based login system with 3 distinct access levels
- Quick-login cards for instant role switching demo
- Session persistence via LocalStorage

### 👤 Patient Management
- Add new patients via `INSERT INTO patients` form
- View complete patient roster with demographics
- Delete patients (with CASCADE simulation)
- All records persist permanently across page reloads

### 📊 Dashboard (Role-Specific)
- **Patient Dashboard** — personal ECG telemetry, AI diagnosis, Twilio emergency alerts
- **Doctor Dashboard** — patient roster, clinic appointments, cardiovascular averages chart
- **Admin Dashboard** — full schema table counts, connectors hub, audit logs

### 🫀 ECG Telemetry
- Real-time animated ECG Lead II waveform
- Upload simulation (IMAGE / CSV / PDF)
- AI classification trigger using Gemini API
- Historical ECG records table

### 🤖 AI Predictions
- Gemini-powered cardiac disease classification
- Confidence score, risk level (Low / Medium / High)
- Automated clinical recommendations
- Update predictions as Doctor/Admin

### 📋 Clinical Reports
- Multi-table JOIN visualization (patients ⋈ ecg_records ⋈ predictions)
- **Click any patient name** to open a detailed AI diagnostic card
- **Download clinical report** as `.txt` file
- **Print / Save as PDF** via browser print dialog
- Doctor can annotate reports with clinical notes (triggers `UPDATE` SQL)

### 🖥️ Live SQL Console
- Floating terminal at the bottom of every page
- Shows real PostgreSQL-style queries for every action
- Copy query to clipboard
- Color-coded SUCCESS / FAILED status with execution time

### 🔗 External Connectors (Simulated)
- **Firebase** — Auth state & realtime notifications
- **Twilio SMS** — Emergency cardiac alerts with mock smartphone UI
- **Mailgun SMTP** — Send diagnostic reports via email
- **Google Sheets API** — Export database to spreadsheet

### ☁️ Supabase Remote Sync
- Live connection status indicator
- Push all local DBMS tables to Supabase cloud
- Admin-only feature with schema setup guide

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend Framework** | React 18 + TypeScript |
| **Build Tool** | Vite 7 |
| **Routing** | TanStack Router (file-based) |
| **Styling** | Vanilla CSS + CSS Variables |
| **Charts** | Recharts |
| **Icons** | Lucide React |
| **Notifications** | Sonner |
| **AI / LLM** | Google Gemini API |
| **Remote Database** | Supabase (PostgreSQL) |
| **Local Database** | LocalStorage (relational simulation) |
| **Auth Simulation** | Role-based session store |

---

## 🗄️ Database Schema

```sql
-- 8 normalized tables with PK/FK relationships

users          (user_id PK, name, email, password_hash, role, created_at)
patients       (patient_id PK, user_id FK, full_name, age, gender, blood_group, contact, medical_history, email, address)
doctors        (doctor_id PK, user_id FK, full_name, specialization, hospital, experience, contact, email)
ecg_records    (ecg_id PK, patient_id FK, upload_url, upload_type, heart_rate, qrs_duration, pr_interval, qt_interval, ecg_signal, uploaded_at)
predictions    (prediction_id PK, ecg_id FK, patient_id FK, disease_name, confidence_score, risk_level, recommendation, predicted_at)
reports        (report_id PK, patient_id FK, ecg_id FK, generated_pdf, doctor_notes, generated_at)
appointments   (appointment_id PK, patient_id FK, doctor_id FK, appointment_date, status)
audit_logs     (log_id PK, user_id FK, username, role, activity, sql_query, timestamp, ip_address, status, execution_time_ms)
```

Key relationships:
- `users` → `patients` (one-to-one via `user_id`)
- `patients` → `ecg_records` → `predictions` (one-to-many chain)
- `patients` + `ecg_records` → `reports` (JOIN)
- All write operations cascade to `audit_logs`

---

## 👥 Roles & Access Control

| Feature | Patient | Doctor | Admin |
|---|:---:|:---:|:---:|
| View own dashboard | ✅ | ✅ | ✅ |
| View patient roster | ❌ | ✅ | ✅ |
| Add / Delete patients | ❌ | ❌ | ✅ |
| Upload ECG & trigger AI | ✅ | ✅ | ✅ |
| Annotate doctor notes | ❌ | ✅ | ✅ |
| View all reports | ❌ | ✅ | ✅ |
| View users table | ❌ | ❌ | ✅ |
| Supabase sync | ❌ | ❌ | ✅ |
| Google Sheets export | ❌ | ❌ | ✅ |
| SQL Console | ✅ | ✅ | ✅ |

---

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ and npm

### Installation

```bash
# Clone the repository
git clone https://github.com/A760-st/heartscan-ai.git
cd heartscan-ai

# Install dependencies
npm install

# Start the development server
npm run dev
```

The app will be available at **http://localhost:8080/**

### Build for Production

```bash
npm run build
npm run preview
```

---

## 📁 Project Structure

```
heartscan-ai/
├── src/
│   ├── components/
│   │   ├── AppLayout.tsx        # Sidebar navigation shell
│   │   ├── AiAssistant.tsx      # Gemini AI chat assistant
│   │   ├── DbActivityConsole.tsx # Floating SQL terminal
│   │   ├── EcgWave.tsx          # Animated ECG waveform
│   │   ├── RiskBadge.tsx        # Risk level indicator
│   │   └── SqlQueryCard.tsx     # SQL syntax display card
│   ├── lib/
│   │   ├── db-store.ts          # Core DBMS engine (LocalStorage)
│   │   ├── supabase-sync.ts     # Supabase remote sync client
│   │   ├── sql-queries.ts       # SQL query catalog
│   │   └── mock-data.ts         # Seed data definitions
│   ├── routes/
│   │   ├── index.tsx            # Landing page
│   │   ├── login.tsx            # Authentication gate
│   │   ├── dashboard.tsx        # Role-based dashboard
│   │   ├── patients.tsx         # Patient management
│   │   ├── ecg.tsx              # ECG upload & telemetry
│   │   ├── predictions.tsx      # AI predictions viewer
│   │   ├── reports.tsx          # Clinical reporting center
│   │   ├── sql-queries.tsx      # DBMS SQL console
│   │   └── admin.tsx            # System administration
│   ├── styles.css               # Global design system
│   └── main.tsx                 # App entry point
├── schema.sql                   # Full PostgreSQL DDL schema
├── .env                         # API keys (Gemini, Firebase, Supabase)
└── README.md
```

---

## 🔑 Demo Credentials

| Role | Email | Password |
|---|---|---|
| 🛡️ **Admin** | `admin@cardiopredict.com` | `admin123` |
| 🩺 **Doctor** | `arjun.m@gmail.com` | `admin123` |
| 🧑‍⚕️ **Patient** | `rahul@gmail.com` | `admin123` |
| 🧑‍⚕️ **Patient** | `priya.v@gmail.com` | `admin123` |
| 🧑‍⚕️ **Patient** | `vikram.s@gmail.com` | `admin123` |

---

## 🌐 API Keys & Environment

Create a `.env` file in the root directory:

```env
VITE_GEMINI_API_KEY=your_gemini_api_key
VITE_FIREBASE_API_KEY=your_firebase_api_key
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### Setting up Supabase (Optional)

1. Create a project at [supabase.com](https://supabase.com)
2. Open the **SQL Editor** and run the contents of `schema.sql`
3. Copy your **Project URL** and **anon key** into `.env`
4. Login as Admin → go to **System Administration** → click **"Push Local DBMS to Supabase"**

---

## 📚 DBMS Concepts Demonstrated

This project demonstrates the following database concepts:

- ✅ **Normalization** — 3NF-compliant schema design
- ✅ **Primary & Foreign Keys** — All tables linked with referential integrity
- ✅ **Multi-table JOINs** — Reports page executes 3-way JOIN
- ✅ **DDL** — `CREATE DATABASE`, `CREATE TABLE`, `CREATE VIEW`
- ✅ **DML** — `INSERT`, `UPDATE`, `DELETE` with real SQL output
- ✅ **Aggregate Functions** — `COUNT(*)`, `AVG()`, `MAX()`
- ✅ **Views** — `CREATE VIEW patient_dashboard`
- ✅ **Audit Logging** — Every operation logged to `audit_logs`
- ✅ **Role-Based Access Control** — Three-tier permission system
- ✅ **Cascade Triggers** — Patient delete cascades to related records
- ✅ **Transaction Simulation** — Supabase sync as atomic batch operation

---

## 👨‍💻 Author

**Adithya,Anusha,Lakshmi,Anjali** — DBMS Academic Project  
Built with ❤️ using React, TypeScript, Gemini AI & Supabase

---

*CardioPredict is an academic simulation project. All patient data is fictitious and for demonstration purposes only.*
