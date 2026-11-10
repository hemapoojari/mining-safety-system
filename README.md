---
title: AI Mining Safety And Worker Evacuation System
emoji: 🦺
colorFrom: red
colorTo: slate
sdk: docker
app_port: 7860
pinned: false
---

# AI/ML-Powered Mining Safety and Worker Evacuation System

> **Academic Research & Demonstration Platform**  
> *Notice: This application is an advanced academic research and demonstration prototype integrating synthetic geotechnical and atmospheric sensor telemetry, machine learning predictive models, point-in-polygon spatial geofencing, and automated emergency evacuation routing. It is designed for design validation, algorithm benchmarking, and educational demonstration.*

---

## 1. Project Introduction & Problem Statement

### The Problem
Mining environments—both surface open-pit excavations and deep underground extraction driftways—present some of the most unforgiving occupational hazards in modern industry. 
- **Open-Pit Hazards**: Heavy precipitation and continuous blasting vibrations weaken bench walls, leading to catastrophic slope instabilities and sudden rockfalls with minimal warning.
- **Underground Hazards**: Enclosed sub-surface drifts suffer from invisible toxic gas inrushes (methane $CH_4$ explosions, carbon monoxide $CO$ poisoning, oxygen $O_2$ asphyxiation) and spontaneous combustion thermal runaways.
- **The Evacuation Gap**: Traditional mine safety relies on manual reporting or siloed alarm klaxons. Evacuation orders are frequently delayed, non-targeted, or send workers into obstructed corridors that already contain fire, rockfall, or toxic gas.

### The Solution
The **AI/ML-Powered Mining Safety and Worker Evacuation System** is an end-to-end multi-hazard digital twin command platform. It ingests high-frequency 12-parameter sensor streams, applies a **Defense-in-Depth dual-engine fusion** (combining trained XGBoost and Random Forest classifiers with strict statutory failsafes), tracks personnel via spatial ray-casting geofences, calculates verified geometric egress routes to blast-proof refuge chambers, and orchestrates two-way emergency acknowledgements across a real-time WebSocket telemetry stream.

---

## 2. Project Objectives & Scope

1. **Continuous Multi-Parameter Telemetry**: Ingest and process 6 surface parameters (Rainfall, Vibration, Slope Displacement, Crack Dilation, Soil Moisture, Displacement Rate) and 6 underground parameters ($CH_4$, $CO$, $O_2$, Temperature, Smoke Density, Ventilation Velocity).
2. **Predictive AI/ML Multi-Hazard Classification**: Detect combinatorial geotechnical and atmospheric anomalies with $>98\%$ test accuracy before individual sensor thresholds breach.
3. **Statutory Defense-in-Depth Safeguards**: Enforce DGMS (Directorate General of Mines Safety), USBM, and MSHA mandatory limits to immediately override predictions during extreme events.
4. **Spatial Personnel Tracking & Geofencing**: Map workers to specific zones in real time and target emergency dispatches exclusively to affected personnel.
5. **Dynamic Evacuation Routing**: Compute verified geometric escapeways to safe refuges (*North Pit Surface Muster Station* or *Underground Fresh-Air Refuge Chamber #1*) while actively routing around hazardous corridors.
6. **Statutory Two-Way Worker Acknowledgement**: Enforce the lifecycle: $\text{Notified} \to \text{Acknowledged} \to \text{Evacuating} \to \text{Safe in Refuge} \text{ / Trapped}$, guaranteeing alarm receipt never counts as safe until arrival at refuge coordinates.
7. **Executive Decision-Support & Statutory Reporting**: Deliver a 4-tab analytics suite with predictive trend velocities, ReportLab-generated multi-page PDF incident dossiers, and CSV telemetry exports.

---

## 3. Complete System Architecture

```text
+---------------------------------------------------------------------------------------------------------+
|                                        MINING COMMAND-CENTER DASHBOARD                                  |
|                                       (React 18 + Vite + Tailwind CSS)                                  |
|  [Overview]  [Open-Pit]  [Underground]  [Sensors]  [Worker Tracking]  [Alerts]  [Analytics]  [Settings]   |
+------------------------------------+------------------------------------+-------------------------------+
                                     | HTTP REST APIs                     | WebSockets (/ws/telemetry)
                                     v                                    v
+---------------------------------------------------------------------------------------------------------+
|                                            FASTAPI BACKEND GATEWAY                                      |
|  * routes_zones.py        * routes_workers.py     * routes_sensors.py     * routes_simulation.py        |
|  * routes_alerts.py       * routes_analytics.py   * routes_reports.py     * websocket.py                |
+------------------------------------+------------------------------------+-------------------------------+
                                     |                                    |
          +--------------------------+                                    +-------------------------+
          v                                                                                         v
+----------------------------------------+                                 +--------------------------------+
|          DEFENSE-IN-DEPTH              |                                 |       EMERGENCY EVACUATION     |
|          RISK FUSION ENGINE            |                                 |         ROUTING ENGINE         |
|  * SlopeStabilityModel (XGBoost)       |                                 |  * Geometric Haversine Paths   |
|  * RockfallRiskModel (Random Forest)   |                                 |  * Surface Muster Points       |
|  * ToxicGasModel (XGBoost)             |                                 |  * Fresh-Air Refuge Chambers   |
|  * FireHazardModel (Random Forest)     |                                 |  * Hazard Corridor Blockage    |
|  * DGMS / MSHA Statutory Failsafes     |                                 |  * 2-Way Wearable ACK Tracker  |
+-------------------+--------------------+                                 +----------------+---------------+
                    |                                                                       |
                    +-----------------------------------+-----------------------------------+
                                                        |
                                                        v
+---------------------------------------------------------------------------------------------------------+
|                                    PERSISTENT DATA LAYER (SQLAlchemy ORM)                               |
|                     SQLite (mining_safety.db)  /  PostgreSQL (Enterprise Ready)                         |
|  * mining_zones        * workers            * sensors              * sensor_readings                    |
|  * risk_predictions    * emergency_alerts   * worker_evacuation_status                                  |
+---------------------------------------------------------------------------------------------------------+
```

---

## 4. Technology Stack

| Layer | Technology | Version | Purpose |
| :--- | :--- | :---: | :--- |
| **Frontend UI** | React.js | 18.3.1 | Single-Page Command Dashboard UI |
| **Bundler & Tooling** | Vite | 5.4.21 | Hot Module Replacement (HMR) & production builds |
| **Styling** | Tailwind CSS | 3.4.17 | Industrial dark command-center theme |
| **Mapping Engine** | Leaflet / React-Leaflet | 1.9.4 / 4.2.1 | 2D Mine Digital Twin with polygon zones & escapeways |
| **Icons** | Lucide React | 0.468.0 | Industrial instrumentation & hazard iconography |
| **Backend Framework** | FastAPI | 0.115.0+ | Asynchronous REST API Gateway |
| **ASGI Server** | Uvicorn | 0.32.0+ | High-throughput asynchronous HTTP & WebSocket server |
| **ORM & Database** | SQLAlchemy | 2.0.0+ | Relational schemas, queries, and connection pools |
| **Local Database** | SQLite | 3.x | Persistent development & audit database (`mining_safety.db`) |
| **Document Generation** | ReportLab | 5.1.0 | Multi-page statutory PDF audit reports |
| **Machine Learning** | Scikit-learn, XGBoost | 1.5.0+, 2.1.0+ | Gradient boosted trees and random forest classifiers |
| **Numerical Processing**| NumPy, Pandas | 2.0.0+, 2.2.0+ | Feature engineering, matrices, and moving averages |
| **Model Serialization** | Joblib | 1.4.0+ | High-performance model weight loading (`.joblib`) |

---

## 5. Development Roadmap: All 7 Completed Steps

- **Step 1: Project Setup & System Architecture Specification**  
  Defined complete functional requirements, multi-hazard taxonomy, statutory thresholds, and baseline project structure.
- **Step 2: Relational Database Schema & Seeding**  
  Implemented 7 SQLAlchemy models (`mining_zones`, `workers`, `sensors`, `sensor_readings`, `risk_predictions`, `emergency_alerts`, `worker_evacuation_status`) with foreign keys and cascade rules. Seeded 6 mining zones and registered personnel.
- **Step 3: Core Backend REST API & WebSocket Server**  
  Engineered FastAPI endpoints for sensors, zones, workers, alerts, and real-time `/ws/telemetry` WebSocket hub with automatic broadcast dispatch.
- **Step 4: Frontend Command-Center Dashboard Development**  
  Built React dashboard with dark navy/charcoal industrial UI, dynamic StatCards, Leaflet digital twin mine map, and 8 responsive views.
- **Step 5: Machine Learning Multi-Hazard Model Development**  
  Created synthetic datasets ($N=10,000$) with realistic physical correlations. Trained, evaluated, and serialized 4 ML models for Open-Pit and Underground hazards. Built feature extractors (Graham's ratio, displacement rate).
- **Step 6: Real-Time Simulation & Evacuation Workflow Integration**  
  Built 12-parameter real-time sensor simulator with 5 physical scenarios (`normal`, `progressive_drift`, `open_pit_hazard`, `gas_leak`, `fire_hazard`). Integrated ray-casting worker geofencing, geometric escapeway routing, safe refuge destinations, and 2-way wearable ACK tracking.
- **Step 7: Advanced Analytics, Predictive Insights & Reporting**  
  Engineered executive 4-tab decision-support center with predictive trend velocities, multi-parameter time-series chart, ML benchmark comparison, ReportLab statutory PDF incident dossiers, and CSV telemetry exports.

---

## 6. Machine Learning Models & Performance Benchmarks

The system deploys 4 production classifiers persisted under `ml_engine/saved_models/`:

| Hazard Model | Sector | Algorithm | Primary Input Features | Test Accuracy | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :--- | :---: | :---: | :---: | :---: |
| **Slope Instability** | Open-Pit | XGBoost Classifier | Rainfall, Vibration, Slope Displacement, Crack Dilation, Soil Moisture, Displacement Rate | **98.9%** | 0.989 | 0.989 | 0.989 |
| **Rockfall Risk** | Open-Pit | Random Forest | Crack Expansion, Displacement Rate, Vibration PPV, Slope Displacement | **98.3%** | 0.984 | 0.983 | 0.983 |
| **Toxic Gas Inrush** | Underground | XGBoost Classifier | Methane ($CH_4$), Carbon Monoxide ($CO$), Oxygen ($O_2$), Ventilation Velocity | **99.2%** | 0.992 | 0.992 | 0.992 |
| **Fire & Thermal Runaway** | Underground | Random Forest | Ambient Temperature, Smoke Optical Density, Carbon Monoxide, Graham's Ratio | **98.7%** | 0.987 | 0.987 | 0.987 |

### Dual-Engine Risk Fusion (Defense-in-Depth)
1. **Machine Learning Layer**: Evaluates multi-parameter combinatorial risks and assigns continuous probability distributions across 5 standardized risk tiers (`Safe`, `Low`, `Medium`, `High`, `Critical`).
2. **Statutory Override Layer**: Implements hardcoded physical threshold interlocks based on DGMS / USBM standards:
   - If $CH_4 \ge 1.25\%$, system forces **Critical** risk immediately regardless of model confidence.
   - If $CO \ge 50\,ppm$, system forces **Critical** risk.
   - If $O_2 \le 17.0\%$, system forces **Critical** risk (asphyxiation threshold).
   - If Open-Pit Slope Displacement $\ge 12\,mm$ or Vibration $\ge 25\,mm/s$, system forces **Critical** risk.

---

## 7. Database Relational Design (7 Tables)

```text
+-------------------+       +-----------------------+       +-------------------+
|   mining_zones    |1     *|        workers        |1     *|worker_evacuation_ |
|-------------------|-------|-----------------------|-------|     status        |
| id (PK)           |       | id (PK)               |       |-------------------|
| zone_code         |       | worker_code           |       | id (PK)           |
| name              |       | full_name             |       | alert_id (FK)     |
| mine_type         |       | role, phone           |       | worker_id (FK)    |
| boundary_geo      |       | zone_id (FK)          |       | status (notified/ |
| current_risk_tier |       | current_lat, lng      |       |   ack/evac/safe)  |
| updated_at        |       | elevation_or_level    |       | acknowledged_at   |
+---------+---------+       | status, last_ping     |       | safe_at           |
          |                 +-----------------------+       +---------+---------+
          |1                                                          |*
          |         +-------------------+                             |
          +--------*| emergency_alerts |-----------------------------+
          |         |-------------------|1
          |         | id (PK)           |
          |         | alert_code        |
          |         | zone_id (FK)      |
          |         | risk_tier         |
          |         | hazard_type       |
          |         | affected_count    |
          |         | acknowledged_count|
          |         | evacuated_safe_cnt|
          |         | trapped_count     |
          |         | route_details     |
          |         | is_active         |
          |         +-------------------+
          |1
          |         +-------------------+       +-------------------+
          +--------*|      sensors      |1     *|  sensor_readings  |
          |         |-------------------|-------|-------------------|
          |         | id (PK)           |       | id (PK)           |
          |         | sensor_code       |       | sensor_id (FK)    |
          |         | zone_id (FK)      |       | sensor_code       |
          |         | mine_type         |       | zone_id (FK)      |
          |         | sensor_type       |       | value, unit       |
          |         | unit, status      |       | timestamp         |
          |         +-------------------+       +-------------------+
          |1
          |         +-------------------+
          +--------*|  risk_predictions |
                    |-------------------|
                    | id (PK)           |
                    | zone_id (FK)      |
                    | hazard_type       |
                    | risk_score        |
                    | risk_tier         |
                    | confidence        |
                    | model_name        |
                    | timestamp         |
                    +-------------------+
```

---

## 8. Backend API & WebSocket Reference

### REST Endpoints Catalog

#### System & Zones
- `GET /health` — Diagnostic health check and database connection verification.
- `GET /api/zones` — List all mining sectors with boundary polygons and active risk tiers.
- `GET /api/zones/{zone_code}` — Detailed zone profile with sensor inventory and worker count.
- `POST /api/zones/{zone_code}/override-risk` — Manual geotechnical / safety officer tier override.

#### Workers & Tracking
- `GET /api/workers` — Retrieve all personnel with live coordinates, zones, and duty status.
- `POST /api/workers` — Register new mine worker.
- `PUT /api/workers/{id}/location` — Update worker GPS / level coordinate ping.

#### Sensor Telemetry
- `GET /api/sensors/` — List all registered physical hardware instruments.
- `GET /api/sensors/readings/current` — Current latest values across all 36 active sensors.
- `GET /api/sensors/readings/history/{sensor_code}` — Historical time-series telemetry.
- `POST /api/sensors/readings` — Ingest live or simulated sensor reading (triggers risk engine).

#### Emergency Evacuation & Alerts
- `GET /api/alerts/active` — All ongoing unresolved emergency incidents.
- `GET /api/alerts/history` — Historical emergency ledger with resolution timestamps.
- `POST /api/alerts/trigger` — Manual or automated targeted emergency evacuation trigger.
- `POST /api/alerts/{id}/acknowledge` — 2-Way worker status update (`acknowledged`, `evacuating`, `safe`, `trapped`).
- `POST /api/alerts/{id}/resolve` — Incident stand-down and safe return authorization.
- `GET /api/alerts/{id}/evacuation-status` — Real-time per-worker evacuation roster and progress.

#### Simulation Controls
- `GET /api/simulation/status` — Running state, active scenario, interval, and tick counters.
- `POST /api/simulation/start` — Start continuous background telemetry loop (3.5s interval).
- `POST /api/simulation/stop` — Pause simulation loop.
- `POST /api/simulation/reset` — Reset mine to nominal baseline and clear active incidents.
- `POST /api/simulation/scenario` — Switch physical hazard scenario.
- `POST /api/simulation/tick` — Execute single manual simulation cycle.

#### Advanced Analytics & Reporting
- `GET /api/analytics/kpis` — High-level KPI cards, risk distribution bars, and sector comparisons.
- `GET /api/analytics/historical-risk` — Filtered risk prediction time-series.
- `GET /api/analytics/predictive-trends` — 4-hazard rolling rate-of-change velocity indicators.
- `GET /api/analytics/evacuation-performance` — Evacuation efficiency metrics and clearance rates.
- `GET /api/analytics/ml-model-comparison` — Accuracy, precision, recall, and F1 benchmarks.
- `GET /api/reports/incident/{alert_id}/pdf` — Download statutory multi-page Incident Audit PDF.
- `GET /api/reports/zone/{zone_id}/pdf` — Download comprehensive Sector Safety Summary PDF.
- `GET /api/reports/sensors/csv` — Stream historical sensor telemetry CSV.
- `GET /api/reports/incidents/csv` — Stream emergency incidents audit ledger CSV.

### WebSocket Protocol (`/ws/telemetry`)
Real-time full-duplex communication hub broadcasting 7 standardized events:
1. `SENSOR_READING`: Real-time telemetry tick with sensor code, zone, value, and unit.
2. `RISK_UPDATE`: Zone risk tier transition, composite score, ML confidence, and breakdown.
3. `WORKER_LOCATION`: Worker coordinate ping and dynamic point-in-polygon zone mapping.
4. `EMERGENCY_ALERT`: High-priority evacuation alarm with designated refuge and escape route.
5. `EVACUATION_STATUS`: Real-time tally updates (ACK count, safe-in-refuge count, trapped count).
6. `SIMULATION_STATE`: Changes in simulation play/pause state or scenario.
7. `EMERGENCY_ALERT_RESOLVED`: Incident stand-down notification.

---

## 9. Installation & Execution Guide

### Prerequisites
- **Python**: 3.10+ (Tested on Python 3.13)
- **Node.js**: v18+ (Tested on Node.js v24, npm 11)
- **Git**

### Step 1: Clone Repository & Setup Virtual Environment
```powershell
# Open terminal in project root
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install Python requirements
pip install -r requirements.txt
```

### Step 2: Initialize Database & Seed Baseline Records
```powershell
# Database initializes automatically on first run, or run backend test suite to seed:
python test_backend.py
```

### Step 3: Start FastAPI Backend Server
```powershell
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
- Swagger API Docs: `http://127.0.0.1:8000/docs`
- Health Endpoint: `http://127.0.0.1:8000/health`

### Step 4: Start React Frontend Dashboard
```powershell
# In a second terminal:
cd frontend
npm install
npm run dev
```
- Command Center Dashboard: `http://localhost:5173`

---

## 10. Automated Verification Suites & Test Results

The platform is fortified with 6 automated test suites executing across all application layers:

```powershell
# 1. Master Consolidated End-to-End Verification Suite (8 Dimensions)
python test_master_end_to_end.py

# 2. Step 7 Advanced Analytics & Statutory Reporting Suite
python test_step7_analytics_reports.py

# 3. Step 6 Real-Time Simulation & Evacuation Workflow Suite
python test_simulation_evacuation.py

# 4. Emergency Scenarios Audit Suite (All 4 Hazard Scenarios)
python audit_emergency_scenarios.py

# 5. Machine Learning Integration & Model Benchmark Suite
python test_ml_integration.py

# 6. Core Database & Backend REST API Suite
python test_backend.py

# 7. Frontend Production Vite Compilation
cd frontend
npm run build
```

### Actual Test Execution Summary
```text
================================================================================
ALL TEST SUITES VERIFIED: 100% PASS RATE
================================================================================
1. test_master_end_to_end.py         : 8/8 Dimensions Passed       [100% PASS]
2. test_step7_analytics_reports.py   : 10/10 Tests Passed          [100% PASS]
3. test_simulation_evacuation.py     : 14/14 Tests Passed          [100% PASS]
4. audit_emergency_scenarios.py      : 4/4 Scenarios Verified      [100% PASS]
5. test_ml_integration.py            : 6/6 Pipeline Stages Passed  [100% PASS]
6. test_backend.py                   : 9/9 Tests Passed            [100% PASS]
7. npm run build                     : 1630 Modules Transformed    [0 ERRORS]
================================================================================
```

---

## 11. Project Outcomes, Ethical Scope & Limitations

### Key Outcomes
- Successfully demonstrated a unified surface-and-subsurface mining digital twin.
- Reduced simulated alarm-to-evacuation calculation latency to $<50\,ms$.
- Guaranteed life safety via statutory physical threshold interlocks overriding probabilistic ML models.
- Established a statutory compliance audit trail with automated ReportLab PDF dossiers.

### Academic Scope & Limitations
- **Simulated Telemetry**: Sensor values, worker GPS coordinates, and sub-surface beacons are synthetically generated for research demonstration.
- **Atmospheric Modeling**: The simulation utilizes point-sensor empirical approximations rather than full 3D Computational Fluid Dynamics (CFD).
- **Certification Disclaimer**: This software is an academic demonstration platform and is not certified under IEC 61508 / ISO 13849 for real-world life-critical mine safety operations.

---

## 12. Cloud Deployment Guide: Render.com & Neon Serverless PostgreSQL

The application is architected for **100% Free Long-Term Hosting** with **NO fixed 30-day database expiration date**:
- **Application Layer**: Render.com Free Web Service (serves FastAPI backend, compiled React 18 dashboard, REST APIs, and WebSockets on a single unified HTTPS URL).
- **Persistence Layer**: Neon Serverless PostgreSQL Free Tier (0.5 GB persistent cloud storage, autoscales to zero when idle, automatic wake-up, no 30-day wipeout).

```text
+-----------------------------------------------------------------------------------------+
|                                    USER'S WEB BROWSER                                   |
|                      https://mining-safety-system.onrender.com                         |
+--------------------------------------------+--------------------------------------------+
                                             |  (Single HTTPS / WSS Origin)
                                             v
+-----------------------------------------------------------------------------------------+
|                               RENDER.COM FREE WEB SERVICE                               |
|   +------------------------------------+  +-----------------------------------------+   |
|   |   Compiled React 18 SPA (Vite)     |  |         FastAPI Unified Gateway         |   |
|   |   [Dashboard] [Maps] [Simulation]  |  |  /api/...  |  /ws/telemetry  |  /assets |   |
|   +------------------------------------+  +-----------------------------------------+   |
|                                     |                                                   |
|                        +------------+------------+                                      |
|                        v                         v                                      |
|              [4 Pre-Trained Models]    [Emergency Router]                               |
+--------------------------------------------+--------------------------------------------+
                                             |  DATABASE_URL (SSL Encrypted Pool)
                                             v
+-----------------------------------------------------------------------------------------+
|                         NEON SERVERLESS POSTGRESQL (FREE TIER)                          |
|         mining_zones | workers | sensors | sensor_readings | emergency_alerts           |
|                 (Persistent Cloud Storage with Zero Expiry Date)                        |
+-----------------------------------------------------------------------------------------+
```

### Step 1: Create Free Neon Serverless PostgreSQL Database
1. Go to **[neon.tech](https://neon.tech)** and sign up for a free account (GitHub / Google login, no credit card required).
2. Click **Create Project**:
   - **Project Name**: `mining-safety-system`
   - **Region**: Choose closest to your Render service (e.g. `US East / Ohio` or `US East / N. Virginia`).
   - Click **Create Project**.
3. In your project dashboard, copy the connection string under **Connection Details**:
   Select **Connection string** $\to$ choose **SQLAlchemy** or **PostgreSQL**:
   ```text
   postgresql://username:password@ep-cool-fog-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

### Step 2: Push Repository to GitHub
1. Create a new repository on **[github.com/new](https://github.com/new)** named `mining-safety-system` (Public or Private).
2. Push your local workspace:
   ```powershell
   git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/mining-safety-system.git
   git branch -M main
   git push -u origin main
   ```

### Step 3: Deploy on Render.com (Free Web Service)
1. Go to **[dashboard.render.com](https://dashboard.render.com)** and sign in.
2. Click **New +** $\to$ **Web Service**.
3. Connect your GitHub repository `mining-safety-system`.
4. Configure Web Service settings:
   - **Name**: `mining-safety-system`
   - **Region**: Oregon (US West) or Ohio (US East)
   - **Branch**: `main`
   - **Runtime**: **Python** (or **Docker**)
   - **Build Command**: `bash build.sh`
   - **Start Command**: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: **Free**
5. Add **Environment Variables**:
   | Variable | Value | Description |
   | :--- | :--- | :--- |
   | `DATABASE_URL` | `postgresql://...neon.tech/neondb?sslmode=require` | Your Neon connection string |
   | `APP_ENV` | `production` | Production mode |
   | `PYTHON_VERSION` | `3.11.9` | Optimized Python runtime |
6. Click **Deploy Web Service**.

### Step 4: Automatic Database Migration & Cold-Start Wakeup
- On initial startup, the backend connects to Neon PostgreSQL. If the database is empty, the lifespan manager **automatically migrates all 2,752 historical sensor readings, 6 zones, 12 workers, 17 sensors, 136 alerts, and 266 evacuation records** from `mining_safety.db` into Neon!
- **Free-Tier Sleep Behavior**:
  - Render free services sleep after 15 minutes of inactivity; the first request takes ~30–50 seconds to spin up.
  - Neon computes auto-suspend when inactive and wake up in $<500\,ms$ (handled seamlessly by SQLAlchemy `pool_pre_ping=True`).
  - All new simulation ticks, emergency alerts, and worker acknowledgements persist permanently in Neon.

