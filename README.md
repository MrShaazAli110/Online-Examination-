# ProctorCode: Multi-Tenant Quiz & Coding Assessment Platform

ProctorCode is an enterprise-grade, secure, multi-tenant assessment platform designed to host simultaneous quizzes and interactive coding challenges with strict anti-cheating proctoring, live movement tracking, and role-based privacy controls.

---

## 🚀 Key Features

### 1. Dual-Format Testing (Quiz + Programming Problems)
* **Multiple Choice (MCQ)**: Instant selection, randomized options, points scoring, and detailed explanations for instructors.
* **Live In-Browser Code Runner**:
  * Python 3 code execution sandbox running against standard input (`stdin`) and standard output (`stdout`).
  * Live **"Run Sample Tests"** button for candidates to test edge cases before final submission.
  * Hidden test cases evaluated strictly during final grading.
  * Execution timeout enforcement (prevents infinite loops) and sandboxed security checks.

### 2. High Concurrency & Multi-Tenancy ("Host Multiple Simultaneously")
* Multiple quizzes can run concurrently with unique quiz join codes (e.g. `PYTHON-101`, `WEB-CS-202`).
* Hundreds of concurrent students can take assessments at the same time.
* SQLite configured with **Write-Ahead Logging (`PRAGMA journal_mode=WAL`)** and asynchronous session pooling to eliminate database locks.

### 3. Strict Anti-Cheating & Movement Detection Proctoring
* **Tab Switch & Window Defocus Detection**:
  * Listens to `visibilitychange` and `window.onblur`.
  * Instantly triggers warning dialog when candidate navigates to another tab or applications (`Alt+Tab`).
* **Movement Detection**:
  * Tracks cursor boundary (`mouseleave` on the viewport).
  * Exiting the window perimeter records a timestamped movement infraction.
* **Fullscreen Lockdown**:
  * Enforces mandatory fullscreen mode (`fullscreenchange`). Exiting fullscreen registers a violation.
* **Shortcut & Clipboard Suppression**:
  * Blocks right-click context menu.
  * Disables copy, paste, and cut clipboard actions.
  * Disables inspection keys: `F12`, `Ctrl+Shift+I`, `Ctrl+Shift+J`, `Ctrl+U`, `Ctrl+S`.
* **Automated Strike System & Disqualification**:
  * Configurable violation strike limit (default: 3 strikes).
  * Plays audible synthesizer alert and opens a warning modal with remaining chances.
  * Upon reaching the limit, the platform **automatically locks and terminates the exam**, submitting it with status `auto_submitted_violations` (Disqualified).

### 4. Word, PDF, and TXT Question File Importer
* Upload question banks in Microsoft Word (`.docx`), PDF (`.pdf`), or Text (`.txt`).
* Automatically extracts question title, choices `A, B, C, D`, correct answer (`Answer: B`), explanations, and coding problems with test cases.
* **Interactive Preview**: Review all parsed questions before confirming import.
* Sample test files included in `/sample_files`:
  * `sample_quiz.docx`
  * `sample_quiz.pdf`
  * `sample_quiz.txt`

### 5. Role-Based Access & Result Privacy ("Results for Admin & Instructor Only")
* **Three Roles**:
  * **Student / Candidate**: Can only take active exams. When submitted, results and scores are **completely confidential and withheld from candidates**.
  * **Instructor**: Create and manage quizzes, modify exam duration, upload files, and inspect candidate submissions for their courses.
  * **Administrator**: System-wide oversight across all quizzes, candidates, and submissions.
* **Instructor & Admin Audit Dashboard**:
  * Detailed score and percentage breakdown.
  * Candidate's submitted code with test-case results.
  * **Timestamped Proctoring Violation Timeline** displaying exact time and nature of every tab switch or movement event.
  * Export results to CSV spreadsheet.

---

## 🔑 Default Credentials for Instant Testing

| Role | Username | Password |
|---|---|---|
| **Administrator** | `admin` | `admin123` |
| **Instructor** | `instructor` | `prof123` |
| **Candidate 1** | `student1` | `user123` |
| **Candidate 2** | `student2` | `user123` |

*(Note: You can also register a new account on the login page with any role).*

---

## 🏃 Quick Start Guide

### Step 1: Start the Web Server
Run the following command from the project root:
```bash
python quiz_platform/run.py
```
Or with uvicorn directly:
```bash
python -m uvicorn quiz_platform.app.main:app --host 127.0.0.1 --port 8000
```

### Step 2: Open in Your Browser
Navigate to:
```
http://127.0.0.1:8000
```

---

## 📁 Project Structure

```
quiz_platform/
├── app/
│   ├── main.py            # FastAPI backend routes (Auth, Quizzes, Proctoring, Results)
│   ├── models.py          # SQLAlchemy ORM models (User, Quiz, Question, Submission)
│   ├── database.py        # SQLite engine with WAL high-concurrency mode
│   ├── auth.py            # JWT token authentication & role-based route guards
│   ├── parsers.py         # Word (.docx), PDF (.pdf), and Text (.txt) question parsers
│   ├── runner.py          # Sandboxed Python code runner with stdin/stdout & timeouts
│   ├── seed_data.py       # Pre-loaded quizzes, algorithms, test cases, and users
│   └── static/
│       ├── index.html     # Responsive Single-Page Application (Tailwind CSS)
│       └── app.js         # Frontend engine with proctoring event listeners
├── sample_files/          # Ready-to-import question files
│   ├── sample_quiz.docx   # Microsoft Word test file
│   ├── sample_quiz.pdf    # PDF document test file
│   └── sample_quiz.txt    # Plain text test file
├── run.py                 # Application launcher
├── test_full_suite.py     # Automated end-to-end verification test suite
└── README.md
```
