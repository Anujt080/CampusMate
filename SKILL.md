---
name: campusmate-ai
description: Operational skill and workflow reference for CampusMate AI, a lightweight campus companion powered by Google DeepMind's Gemma 4 (gemma-4-26b-a4b-it). Covers architecture, the three operating modes (Campus Guide, StudyMate, CampusFix), institutional verification boundaries, and single-request execution constraints.
---

# CampusMate AI - Agent Skill Specification

## 1. Overview & Purpose
CampusMate AI is a lightweight, student-centric artificial intelligence application developed for the IIT Hackathon under the theme **"Build for Your Campus"**. It addresses three persistent collegiate challenges faced by students:
1. Fragmented, informal campus guidelines and orientation procedures.
2. Unrealistic, overwhelming exam cramming schedules and abstract academic explanations.
3. Vague, slow-to-resolve facility, laboratory, and infrastructure breakdowns.

CampusMate AI unifies these solutions into a **single-screen, zero-database, privacy-first dashboard** powered strictly by **Google DeepMind's Gemma 4 (`gemma-4-26b-a4b-it`)**.

---

## 2. Core Operational Constraints

| Constraint | Specification | Verification Rule |
| :--- | :--- | :--- |
| **Model** | `gemma-4-26b-a4b-it` | Strict. Never switch to Gemini Pro/Flash, OpenAI, Anthropic, or local substitutes. |
| **API Client** | `google-genai` (`from google import genai`) | Documented Gemini API client only. No legacy `google-generativeai`. |
| **Single-Request Rule** | Maximum 1 model call per Generate action | Never chain prompt classifiers or multi-turn reasoning loops. |
| **Thinking Mode** | Disabled by default (`thinking_level="none"` / omitted) | Minimizes latency and token overhead. |
| **State & Database** | Zero database / No authentication | Stateless, runs entirely locally on a student's machine. |
| **API Key Safety** | `GEMINI_API_KEY` in `.env` | Never print, log, hardcode, or expose in frontend code. |

---

## 3. The Three Operating Modes

### Mode 1: Campus Guide (🏫)
- **When to Use:** When navigating between campus buildings or seeking guidance on academic resources, attendance shortfall steps, library borrowing norms, laboratory etiquette, clubs, or facilities.
- **Two Capabilities:**
  1. **Campus Navigation (Local Dijkstra Engine • 0 API Calls):**
     - Resolves starting location and destination from dropdowns or natural-language queries.
     - Deterministically calculates the shortest walking path using Dijkstra's algorithm over `campus_map.json`.
     - Computes total distance in meters and estimated walking time (based on 1.2 m/s standard walking speed).
     - Generates numbered, landmark-guided walking directions and a lightweight SVG path schematic.
     - Never hallucinates unverified GPS coordinates; clearly tags unverified paths as `DEMO ROUTE`.
  2. **Campus Q&A (Gemma 4 • Single API Call):**
     - Answers policy and campus life queries grounded in local `campus_data.json`.
     - Structures answers into: Direct Answer, Important Regulations, Recommended Next Steps, and Official Verification Required.
- **Uncertain Information Policy:**
  - Never invent official college circulars, faculty contact numbers, emergency helplines, or specific semester cutoff dates.
  - Clearly instruct students to cross-verify submissions with their Faculty Advisor, Department Office, or Dean of Student Affairs.

### Mode 2: StudyMate (📚)
- **When to Use:** When students need structured revision plans, conceptual explanations, or step-by-step academic question derivations.
- **Sub-tasks:**
  - **A. Create a Study Plan:** Takes available study hours, timeline, and weak areas. Produces realistic daily quotas, balanced time slots (theory vs. practice vs. revision), and a final review checklist. Avoids burnout schedules.
  - **B. Explain a Concept:** Delivers core intuition in plain English, step-by-step breakdown, a concrete practical/engineering example, common pitfalls/mistakes in exams, and a rapid revision summary.
  - **C. Solve or Explain an Academic Question:** Breaks down given parameters, foundational theorems/laws applied, step-by-step mathematical or algorithmic derivation, and edge cases.

### Mode 3: CampusFix (🛠️)
- **When to Use:** When reporting classroom, laboratory, hostel, or campus infrastructure issues (e.g., intermittent Wi-Fi, broken oscilloscope, projector failure, electrical faults).
- **Output Requirements:**
  - **Problem Categorization:** Exact technical domain, 1-sentence objective summary, suggested priority with rationale.
  - **Recommended Student Actions:** Verification steps (e.g. check other devices, record timestamps, note room number).
  - **Incident Report Draft:** A complete, polite, copy-ready email/ticket draft addressed to the relevant campus authority (Estate Office, IT Center, or Lab In-Charge).
- **Strict Boundaries:**
  - The tool is a **report drafting assistant**.
  - Never state that a ticket has been created, dispatched, or resolved.
  - Never fabricate official support URLs or internal ticketing endpoints.

---

## 4. Error Handling & Recovery

1. **Missing or Invalid Key:**
   - Detect `GEMINI_API_KEY` absence early.
   - Display a human-friendly message instructing the student to check their `.env` file.
2. **Quota Exhaustion (HTTP 429) / Rate Limits:**
   - Display: *"Gemma API quota limit reached or busy (429). Please wait 30 seconds before retrying."*
   - Leverage local disk caching (`.cache/`) to return previously generated identical demo queries immediately without consuming tokens.
3. **Network Interruption:**
   - Display a concise message advising verification of Wi-Fi or mobile hotspot connectivity.
   - Never fabricate an AI response when network calls fail.

---

## 5. Demonstration Checklist for Judges

1. **Verify Model:** Ensure output metadata card confirms `gemma-4-26b-a4b-it`.
2. **Campus Guide Demo:** Click "Attendance Shortfall" or "First-Year Prep" -> Click Generate -> Verify structured response with official verification notice.
3. **StudyMate Demo:** Click "DSA 7-Day Plan" -> Click Generate -> Verify time-respecting study allocation and targeted weak-area roadmap.
4. **CampusFix Demo:** Click "Lab Wi-Fi Disconnecting" -> Click Generate -> Verify structured category, urgency justification, and copy-ready email draft.
5. **Inspect Efficiency:** Confirm single-request execution, fast response time, and zero database footprint.
