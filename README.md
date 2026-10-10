# CampusMate AI 🎓

> **"Your campus. Your academics. Your AI companion."**  
> *A lightweight, privacy-first campus intelligence system built for the IIT Hackathon ("Build for Your Campus") using Google DeepMind's Gemma 4.*

[![Model](https://img.shields.io/badge/Model-gemma--4--26b--a4b--it-blue?style=for-the-badge&logo=google)](https://ai.google.dev/gemma)
[![API](https://img.shields.io/badge/API-google--genai-green?style=for-the-badge)](https://pypi.org/project/google-genai/)
[![Frontend](https://img.shields.io/badge/Frontend-Gradio_6-orange?style=for-the-badge)](https://www.gradio.app/)
[![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)](LICENSE)

---

## 📌 Application Interface

## 📌 Application Interface (Light & Dark Themes)

| ☀️ Clean Light Theme (Navigation + SVG Schematic) | 🌙 Refined Dark Theme (Persistent Preference) |
| :---: | :---: |
| ![CampusMate AI Light Theme](assets/campusmate_screenshot.png) | ![CampusMate AI Dark Theme](assets/campusmate_dark_screenshot.png) |

---

## 📖 Project Overview

**CampusMate AI** is a lightweight, student-centric artificial intelligence companion that helps college and engineering students navigate campus landmarks, find critical college information, prepare realistically for examinations, master difficult academic concepts, and transform everyday facility or laboratory breakdowns into structured, actionable incident reports.

Rather than building an over-engineered multi-service application with databases and authentication overhead, CampusMate AI is architected as a **focused, single-screen MVP that runs entirely locally on a student's laptop** while strictly complying with hackathon resource efficiency guidelines.

---

## 🚩 Problem Statement

Students on modern technical campuses face three friction points every semester:
1. **Physical & Administrative Navigation Friction:** Navigating across sprawling campus grounds between hostels, labs, and admin blocks is confusing for first-years and visitors. Furthermore, attendance rules (e.g. the 75% norm) and administrative guidelines are fragmented across notice boards and hearsay.
2. **Academic Cramming & Shallow Concept Explanations:** Standard AI chatbots suggest unrealistic 12-hour cramming routines or generate abstract explanations without mathematical notation ($Av = \lambda v$), concrete engineering examples, or weak-area prioritization.
3. **Unresolved Infrastructure & Lab Faults:** Broken lab oscilloscopes, classroom projector overheating, or intermittent Wi-Fi during practical exams often go unreported because students lack a quick way to draft a professional, technical complaint to administration.

---

## 🌟 Key Features & Modes

CampusMate AI provides three specialized modes accessible on **one unified screen**:

### 1. 🏫 Campus Guide (Navigation & Q&A)
- **A. Deterministic Campus Navigation Engine (0 API Calls):**
  - Instant local shortest-path calculation powered by **Dijkstra's Algorithm** over `campus_map.json`.
  - Calculates walking distance in meters and walking time (based on 1.2 m/s standard walking speed).
  - Generates numbered step-by-step walking instructions with intermediate landmarks.
  - Dynamically renders a clean vector SVG route schematic showing the path sequence.
  - Natural-language endpoint extraction (e.g. *"I'm standing in front of the canteen. Take me to the CSE block."*).
  - Explicitly flags unverified sample routes with a `DEMO ROUTE` badge.
- **B. Procedural Campus Q&A (Gemma 4 • 1 API Call):**
  - Grounded in local `campus_data.json` for rules, lab safety, library hours, and student societies.
  - Generates direct answers, regulations, recommended next steps, and official verification warnings.
  - 💡 **Recommended Next Steps:** Actionable checklist for the student.
  - ⚠️ **Information Requiring Official Verification:** Explicit reminder of which submissions need formal approval from the Dean or Faculty Advisor.

### 2. 📚 StudyMate
- **Purpose:** Academic coaching engine with three sub-tasks:
  - **A. Create a Study Plan:** Generates realistic, time-respecting preparation roadmaps based on daily available hours, target exam date, and declared weak areas. Allocates exact percentages between theory, coding/practice problems, and revision checkpoints.
  - **B. Explain a Concept:** Breaks down complex engineering/computer science topics with core intuition, step-by-step logic, concrete code/hardware examples, common exam pitfalls, and a rapid revision summary.
  - **C. Solve or Explain an Academic Question:** Provides structured problem formulation, underlying theorems, step-by-step derivations, and verification edge cases.

### 3. 🛠️ CampusFix
- **Purpose:** Converts messy, informal facility grievances into formal, structured incident reports.
- **Output:**
  - 🏷️ **Problem Categorization:** Exact technical domain, 1-sentence factual summary, and suggested priority with rationale.
  - 📋 **Recommended Student Actions:** Verification steps (e.g., checking other devices, noting room numbers and timestamps).
  - 📄 **Formal Incident Report Draft:** Ready-to-copy email/ticket draft addressed to the campus IT Center, Estate Office, or Laboratory Superintendent.

---

## 🧠 Why Gemma 4 (`gemma-4-26b-a4b-it`)

CampusMate AI strictly integrates **`gemma-4-26b-a4b-it`** through the official Google GenAI SDK (`google-genai`).

- **Open-Weights Excellence:** Gemma 4 provides state-of-the-art reasoning and instruction following while maintaining minimal latency.
- **Strict Single-Request Execution Rule:** Every click on "Generate with Gemma 4" executes **exactly ONE model API call**. There are no nested classifier calls, multi-agent chaining loops, or background polling requests.
- **Optimized for Low Latency:** Thinking mode is omitted/disabled by default (`thinking_level="none"`), allowing direct, structured outputs without wasting tokens on unneeded meta-reasoning.
- **Safe Disk Caching:** Includes a local hash-based response cache (`.cache/`) to instantly fulfill repeated student queries during live hackathon demos with zero token consumption and zero rate-limit risk.

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **AI Model** | `gemma-4-26b-a4b-it` | Core intelligence and reasoning engine |
| **API Client** | `google-genai>=2.28.0` | Official Google Gemini API client (`from google import genai`) |
| **Backend & Logic** | Python 3.10+ | Lightweight processing, prompt formatting, validation |
| **Frontend** | Gradio 6.x | Single-screen, reactive UI with custom modern CSS |
| **Configuration** | `python-dotenv` | Secure local `.env` environment variable management |
| **Knowledge Base** | `campus_data.json` | Local, editable campus knowledge representation |
| **Presentation** | `python-pptx` | Automated PowerPoint slide deck generation |

---

## 📁 Project Structure

```text
CampusMate-AI/
├── app.py                   # Main Gradio application (redesigned single-screen dashboard)
├── gemma_client.py          # Gemma 4 client helper (single-request, caching, error handling)
├── campus_map.py            # Local Dijkstra shortest-path routing & SVG schematic engine
├── campus_map.json          # Local editable campus map dataset (nodes and walking edges)
├── campus_data.json         # Local editable sample campus procedures & policies
├── test_app.py              # Automated test suite (10/10 tests passing)
├── create_presentation.py   # PowerPoint deck generator script
├── requirements.txt         # Minimal production dependencies
├── .env.example             # Template for API credentials
├── .gitignore               # Strict git exclusion for secrets and cache
├── README.md                # Comprehensive documentation
├── LICENSE                  # MIT open-source license
├── SKILL.md                 # Agent Skill specification for hackathon organizers
├── assets/
│   ├── campusmate_screenshot.png       # Light theme interface screenshot
│   └── campusmate_dark_screenshot.png  # Dark theme interface screenshot
└── presentation/
    └── CampusMate-AI.pptx   # 6-slide widescreen hackathon pitch deck
```

---

## 🚀 Setup & Installation Instructions

### 1. Prerequisites
- Python 3.10 to 3.14 installed on your system.
- A free Gemini API Key from [Google AI Studio](https://aistudio.google.com).

### 2. Clone and Enter Project Directory
```bash
git clone <repository-url>
cd CampusMate-AI
```

### 3. Create and Activate Virtual Environment
**On Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**On Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure API Key
Copy `.env.example` to create your local `.env` file:
```bash
cp .env.example .env
```
Open `.env` in any text editor and insert your Gemini API Key:
```env
GEMINI_API_KEY=your_actual_api_key_here
GEMMA_MODEL=gemma-4-26b-a4b-it
```

> **Security Note:** The `.env` file is strictly listed in `.gitignore` and must never be committed or shared. The application backend automatically sanitizes all error logs to guarantee API keys are never exposed in terminal outputs or the browser UI.

---

## 🏃 How to Run the Application

Execute the verified launch command:
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:7860
```
- Click the **🌙 Dark / ☀️ Light** button in the top-right corner to toggle themes instantly.
- Theme preferences are saved to your browser's `localStorage` and persist across sessions.

---

## 📍 How to Add Verified Campus Map Data

The navigation engine is designed so that adding your actual campus's building positions and walking paths requires **editing only `campus_map.json` without modifying any Python code**:

1. **Add Building Nodes** in `locations`:
   ```json
   {
     "id": "new_cse_block",
     "name": "New CSE Building",
     "category": "Academics",
     "description": "Department of Computer Science, 3rd Floor Labs",
     "aliases": ["cse building", "new cse", "computer labs"],
     "x": 450,
     "y": 600
   }
   ```
2. **Add Walking Paths** in `edges`:
   ```json
   {
     "from": "main_canteen",
     "to": "new_cse_block",
     "distance_m": 120,
     "instruction_forward": "Walk north along the shaded corridor toward New CSE Building.",
     "instruction_backward": "Head south toward the Main Canteen.",
     "landmarks": ["Clock Tower Plaza", "Bicycle Parking"],
     "accessible": true,
     "verified": true
   }
   ```
3. Set `"verified": true` on verified edges. Verified paths automatically remove the `DEMO ROUTE` disclaimer tag.

---

## 🧪 Verification & Testing

To run the complete automated test suite validating model enforcement, single-request architecture, Dijkstra shortest path routing, natural-language location resolution, LaTeX math support, and live Gemma 4 response generation across all three modes:

```bash
python test_app.py
```

Execution output:
```text
==========================================================
  RUNNING CAMPUSMATE AI COMPREHENSIVE VERIFICATION SUITE
==========================================================
Testing Model ID integrity...
  [PASS] Model ID is strictly 'gemma-4-26b-a4b-it'.
Testing API Key safety & loading...
  [PASS] API key is loaded safely and completely masked in error messages.
Testing local input validation...
  [PASS] Local validation rejects empty inputs gracefully before calling API.
Testing Campus Navigation: Dijkstra Shortest Path...
  [PASS] Dijkstra algorithm successfully chooses the optimal shortest path (220m vs 300m).
Testing Campus Navigation: Walking Time & Directions...
  [PASS] Distance (490m), time (6 min 48 sec), and step directions verified.
Testing Campus Navigation: Natural Language Parser...
  [PASS] Natural-language location queries correctly mapped to graph nodes.
Testing Campus Navigation: SVG generation & edge cases...
  [PASS] SVG schematic generated and edge cases handled safely.
Testing Mode 1: Campus Guide Q&A with Gemma 4...
  [PASS] Campus Guide produces grounded, structured response.
Testing Mode 2: StudyMate with Gemma 4 & LaTeX math...
  [PASS] StudyMate generates mathematical concept breakdown with KaTeX compatibility.
Testing Mode 3: CampusFix with Gemma 4...
  [PASS] CampusFix creates structured categorization and draft email.
==========================================================
  ALL 10 VERIFICATION TESTS PASSED SUCCESSFULLY! (10/10)
==========================================================
```

---

## ⚠️ Limitations & Ethical Boundaries

1. **Illustrative Sample Data:** The included `campus_data.json` contains representative engineering campus procedures. It is not connected to a live university ERP system and must be adapted for specific institutions.
2. **Drafts Only:** Reports generated by **CampusFix** are structured drafts for students to review and copy. CampusMate AI does not automatically file grievances or contact maintenance staff on behalf of students.
3. **Official Verification Required:** Academic deadlines, medical condonations, and examination clearances must always be confirmed directly with the designated department office, Faculty Advisor, or Dean of Student Affairs.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
