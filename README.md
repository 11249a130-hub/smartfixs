# SmartFix – NLP-Based Smart Campus & Hostel Complaint Management System

![SmartFix Banner](https://img.shields.io/badge/SmartFix-Campus%20Maintenance-2563eb?style=for-the-badge&logo=appveyor)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-black?style=for-the-badge&logo=flask)
![Machine Learning](https://img.shields.io/badge/Algorithm-Linear%20SVM%20%2B%20TF--IDF-purple?style=for-the-badge)
![Deployment](https://img.shields.io/badge/Vercel-Deployment%20Ready-black?style=for-the-badge&logo=vercel)

**SmartFix** is an intelligent, web-based campus and hostel maintenance complaint management system powered by **Natural Language Processing (NLP)** and **Machine Learning (Linear Support Vector Machine)**. It allows students to report facility issues in plain English while the system automatically categorizes the complaint, identifies the affected campus asset, calculates priority, and monitors SLA repair deadlines.

---

## 🌟 Key Features

### 1. 🧠 Natural Language Processing (NLP) & Machine Learning
- **Linear Support Vector Machine (Linear SVM)**: High-accuracy classification of student complaints into 6 core campus maintenance domains:
  - `Electrical` (Fans, lights, switchboards, MCBs, geysers, ACs)
  - `Plumbing` (Taps, pipes, washbasins, flush tanks, drainage, RO coolers)
  - `Furniture` (Beds, cots, mattresses, study tables, chairs, cupboards)
  - `Hostel Infrastructure` (Windows, doors, ceiling plaster, damp walls, mesh)
  - `IT & Equipment` (Projectors, audio/mics, lab PCs, Wi-Fi routers, LAN)
  - `Safety & Hazard` (Sparks, burning odors, exposed live wires, gas leaks)
- **Facility & Asset Extraction**: Automatically detects over 25+ specific campus assets (Ceiling Fan, Geyser, Switchboard, Flush Tank, Study Table, etc.).
- **Urgency & Priority Scoring**:
  - `Emergency (Urgent)`: 4-Hour SLA (sparks, fire hazards, exposed wires, flooding)
  - `High`: 24-Hour SLA (broken door locks, severe pipe leaks, major exam room disruptions)
  - `Medium`: 48-Hour SLA (fan regulator stuck, dim lights, broken chair castor)
  - `Low`: 72-Hour SLA (minor scratches, routine adjustments)
- **Real-Time Interactive Preview**: As students type their complaint, the UI displays real-time prediction badges and risk indicators before submission.

### 2. 🎓 Student Portal
- Submit complaints with hostel block and room number.
- Instant 1-click test scenarios for fast demonstration.
- Real-time complaint progress tracking (`Submitted` ➔ `Assigned` ➔ `In Progress` ➔ `Resolved` ➔ `Closed`).
- "Confirm Problem Fixed" feature with 5-star rating and satisfaction feedback.

### 3. 🛡️ Administrator Console
- Comprehensive KPI Analytics dashboard (Total, Unassigned, Overdue, Critical Hazards, Resolution Rate).
- Critical safety hazard alert banner for immediate attention.
- Search, filter by category/status, and sort complaints.
- 1-click staff assignment with auto-matching based on the complaint category.
- Full audit trail / timeline history for every complaint.

### 4. 👷 Maintenance Staff Workdesk
- Dedicated dashboard for campus technicians (Electrician, Plumber, Carpenter, IT specialist).
- View assigned tasks, locations, and student contact numbers.
- Update repair progress to `In Progress` or `Resolved`.
- Add technical notes detailing the root cause and replacement parts used.

### 5. ⏱️ SLA Deadline Monitoring
- Automatic deadline countdown per ticket based on predicted urgency.
- Overdue badge highlights tasks that breached the expected SLA window.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | HTML5, CSS3 (Modern Glassmorphism & Responsive Design), JavaScript (ES6+) |
| **Backend** | Python Flask (WSGI & Serverless-ready) |
| **NLP & Text Processing** | TF-IDF (Term Frequency – Inverse Document Frequency), N-grams, Stopwords Cleaning |
| **Classification Model** | Linear Support Vector Machine (Linear SVM) |
| **Database** | MySQL (with seamless SQLite fallback for zero-config local & Vercel deployment) |
| **Hosting & Deployment** | Vercel Serverless (`@vercel/python`) |

---

## 📂 Project Directory Structure

```
SmartFIT/
├── api/
│   └── index.py            # Vercel Serverless Function entry point
├── static/
│   ├── css/
│   │   └── style.css       # Complete modern styling & animations
│   └── js/
│       └── app.js          # Client-side controller, real-time NLP & modals
├── templates/
│   └── index.html          # Unified portal (Student, Admin, Staff views)
├── app.py                  # Main Flask application & REST API routes
├── database.py             # Database layer (MySQL + SQLite hybrid with seed data)
├── nlp_engine.py           # Linear SVM NLP classification & entity extraction engine
├── requirements.txt        # Python dependencies
├── schema.sql              # MySQL/SQLite relational database schema
├── vercel.json             # Vercel deployment configuration
└── README.md               # Documentation & Deployment Guide
```

---

## 🚀 Running Locally

### Step 1: Clone or Open Project
```bash
cd c:\Users\ADMIN\OneDrive\Desktop\SmartFIT
```

### Step 2: Install Dependencies (Optional if already in virtualenv)
```bash
pip install -r requirements.txt
```

### Step 3: Run the Application
```bash
python app.py
```
Open your browser at: **`http://localhost:5000`**

The application automatically initializes the database, creates all necessary tables, and seeds realistic test complaints, students, and staff accounts.

---

## 🗄️ MySQL Database Configuration (Optional)

By default, SmartFix uses SQLite out of the box with zero setup required. If you want to connect to a **MySQL** server (such as local MySQL, Amazon RDS, PlanetScale, or Aiven):

Set the following environment variables (or in a `.env` file):

```bash
# Option A: Full Connection String
export DATABASE_URL="mysql://username:password@localhost:3306/smartfix"

# Option B: Individual Variables
export MYSQL_HOST="localhost"
export MYSQL_USER="root"
export MYSQL_PASSWORD="your_password"
export MYSQL_DB="smartfix"
export MYSQL_PORT="3306"
```

To create the database and tables manually in MySQL:
```bash
mysql -u root -p < schema.sql
```

---

## ☁️ Deploying to Vercel

SmartFix is structured with `vercel.json` and `api/index.py` for immediate deployment to Vercel.

### Method 1: Deploy via GitHub (Recommended)
1. Push this project to your GitHub repository:
   ```bash
   git add .
   git commit -m "Initial commit of SmartFix NLP Complaint System"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/smartfix.git
   git push -u origin main
   ```
2. Go to [vercel.com](https://vercel.com) and log in.
3. Click **"Add New..."** ➔ **"Project"**.
4. Import your **`smartfix`** repository.
5. In the project settings:
   - Framework Preset: **Other**
   - Root Directory: `./` (leave default)
6. *(Optional)* Add your MySQL `DATABASE_URL` in the **Environment Variables** section if you have a remote MySQL database. If not provided, it will automatically use SQLite in `/tmp`.
7. Click **Deploy**. Your app will be live with an active `.vercel.app` URL!

### Method 2: Deploy using Vercel CLI
```bash
# 1. Install or run Vercel CLI
npx vercel

# 2. Follow prompts to link to your account and deploy
# 3. For production deployment:
npx vercel --prod
```

---

## 🧪 Testing the NLP Engine

You can test the NLP engine directly from Python CLI:

```bash
python nlp_engine.py
```

### Sample Predictions:
| Input Complaint Text | Predicted Category | Identified Asset | Urgency / SLA | Target Staff |
|---|---|---|---|---|
| *"Sparks coming out from the ceiling fan switchboard and smells like burning wire"* | **Electrical / Hazard** | Ceiling Fan / Socket | **Emergency (4h)** | Electrician |
| *"Washbasin drain pipe is ruptured and flooding washroom"* | **Plumbing** | Washbasin / Sink | **High (24h)** | Plumber |
| *"Hostel cot wooden plank is fractured and chair wheel broken"* | **Furniture** | Study Table / Chair | **Medium (48h)** | Carpenter |
| *"Classroom 301 ceiling projector is not turning on and HDMI cable loose"* | **IT & Equipment** | Projector / Display | **Medium (36h)** | IT Systems Tech |

---

## 👥 Demo Accounts

You can switch between any of these users instantly using the **Role Switcher** & **User Selector** in the top navigation bar:

- **Student**: Rahul Verma (`rahul.verma@college.edu` - Hostel Block A, Room 204)
- **Student**: Priya Sharma (`priya.sharma@college.edu` - Hostel Block B, Room 112)
- **Admin**: Campus Estate Office (`admin@smartfix.campus`)
- **Staff (Electrician)**: Ramesh Kumar
- **Staff (Plumber)**: Suresh Patil
- **Staff (Carpenter)**: Mahendra Singh
- **Staff (IT Tech)**: Ankit Verma

---

## 📄 License
MIT License. Built for Smart Campus & Hostel Administration.
