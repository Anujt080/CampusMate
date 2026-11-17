"""CampusMate AI - Main Application
----------------------------------
Redesigned for the IIT Hackathon ("Build for Your Campus").

Key Architecture & Hackathon Constraints:
- AI Model: gemma-4-26b-a4b-it exclusively (Google DeepMind via google-genai)
- Single-Request Rule: At most ONE model request per user action
- Navigation: Deterministic, local Python Dijkstra shortest path (0 API calls)
- Zero Database, Zero Authentication: Lightweight and privacy-first
- High-Contrast Theme Support: Seamless Light/Dark mode with local persistence
- Mathematical LaTeX Rendering: Fixed KaTeX rendering for formulas ($Av = \\lambda v$)
"""

import json
import os
import sys
import time
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Load .env locally if present
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass

import gradio as gr
from gemma_client import (
    GEMMA_MODEL_ID,
    CampusMateAPIError,
    run_campus_guide,
    run_study_mate,
    run_campus_fix,
)
from campus_map import get_campus_map_engine
from campus_notes import NOTES_PAGE_CSS, get_notes_page_html, build_notes_page
from fastapi.responses import HTMLResponse

# Initialize campus map engine
MAP_ENGINE = get_campus_map_engine()
LOCATION_CHOICES = MAP_ENGINE.get_locations_list()

# Load general campus procedures data
DATA_PATH = PROJECT_ROOT / "campus_data.json"
try:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        CAMPUS_DATA = json.load(f)
except Exception:
    CAMPUS_DATA = {
        "_notice": "Demo campus data fallback.",
        "academic_resources": [],
        "student_clubs": [],
        "library_usage": {},
        "laboratory_etiquette": {},
        "general_college_procedures": {},
        "campus_facilities": {},
        "common_student_questions": []
    }

# -------------------------------------------------------------------
# Modern, Polished CSS with Full Light/Dark Theme Support
# -------------------------------------------------------------------
CUSTOM_CSS = """
/* =================================================================
   CAMPUSMATE AI - FUTURISTIC PREVIEW DESIGN SYSTEM
   ================================================================= */

:root {
    --bg-page: #f8fafc;
    --bg-page-mesh: radial-gradient(circle at 20% 15%, rgba(37, 99, 235, 0.08), transparent 45%),
                    radial-gradient(circle at 80% 25%, rgba(79, 70, 229, 0.06), transparent 45%),
                    #f8fafc;
    --bg-card: rgba(255, 255, 255, 0.88);
    --bg-card-hover: rgba(255, 255, 255, 0.98);
    --bg-card-subtle: #f1f5f9;
    --text-primary: #0f172a;
    --text-secondary: #475569;
    --text-muted: #64748b;
    --border-subtle: rgba(226, 232, 240, 0.9);
    --border-card: rgba(203, 213, 225, 0.8);
    --border-strong: #94a3b8;
    --border-hover: #3b82f6;
    --accent-primary: #2563eb;
    --accent-indigo: #4f46e5;
    --accent-cyan: #0284c7;
    --accent-hover: #1d4ed8;
    --accent-soft: #eff6ff;
    --accent-soft-border: #bfdbfe;
    --accent-glow: rgba(37, 99, 235, 0.2);
    --shadow-sm: 0 2px 6px rgba(0, 0, 0, 0.04);
    --shadow-md: 0 8px 24px -4px rgba(0, 0, 0, 0.08), 0 0 15px rgba(37, 99, 235, 0.04);
    --shadow-hover: 0 16px 36px -6px rgba(0, 0, 0, 0.12), 0 0 20px rgba(79, 70, 229, 0.12);
    --code-bg: #0f172a;
    --code-text: #f8fafc;
}

.dark, body.dark, .gradio-container.dark {
    --bg-page: #060913 !important;
    --bg-page-mesh: radial-gradient(circle at 15% 15%, rgba(30, 58, 138, 0.22), transparent 45%),
                    radial-gradient(circle at 85% 20%, rgba(88, 28, 135, 0.18), transparent 45%),
                    radial-gradient(circle at 50% 90%, rgba(6, 78, 106, 0.15), transparent 50%),
                    #060913 !important;
    --bg-card: rgba(14, 20, 36, 0.72) !important;
    --bg-card-hover: rgba(18, 26, 48, 0.85) !important;
    --bg-card-subtle: rgba(22, 32, 58, 0.6) !important;
    --text-primary: #f8fafc !important;
    --text-secondary: #94a3b8 !important;
    --text-muted: #64748b !important;
    --border-subtle: rgba(255, 255, 255, 0.08) !important;
    --border-card: rgba(56, 189, 248, 0.14) !important;
    --border-strong: rgba(99, 102, 241, 0.3) !important;
    --border-hover: rgba(56, 189, 248, 0.45) !important;
    --accent-primary: #3b82f6 !important;
    --accent-indigo: #6366f1 !important;
    --accent-cyan: #06b6d4 !important;
    --accent-hover: #60a5fa !important;
    --accent-soft: rgba(59, 130, 246, 0.12) !important;
    --accent-soft-border: rgba(59, 130, 246, 0.25) !important;
    --accent-glow: rgba(59, 130, 246, 0.35) !important;
    --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.4) !important;
    --shadow-md: 0 10px 28px -4px rgba(0, 0, 0, 0.55), 0 0 20px rgba(59, 130, 246, 0.08) !important;
    --shadow-hover: 0 18px 40px -6px rgba(0, 0, 0, 0.7), 0 0 25px rgba(99, 102, 241, 0.25) !important;
    --code-bg: #030712 !important;
    --code-text: #e2e8f0 !important;
}

/* -----------------------------------------------------------------
   BASE RESETS & TYPOGRAPHY
   ----------------------------------------------------------------- */
body, .gradio-container {
    background: var(--bg-page-mesh) !important;
    background-attachment: fixed !important;
    color: var(--text-primary) !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", "Helvetica Neue", Arial, sans-serif !important;
    transition: background-color 0.3s ease, color 0.3s ease;
    overflow-x: hidden !important;
}

/* Centered layout container */
.app-container {
    max-width: 1180px !important;
    margin: 0 auto !important;
    padding: 14px 16px 40px 16px !important;
    position: relative !important;
    z-index: 1 !important;
}

/* -----------------------------------------------------------------
   SUBTLE AMBIENT BACKGROUND LIGHTING & CURSOR GLOW
   ----------------------------------------------------------------- */
.ambient-light-bg {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
}

.ambient-orb-1 {
    position: absolute;
    top: -12%;
    left: -10%;
    width: 650px;
    height: 650px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(59, 130, 246, 0.14), transparent 70%);
    filter: blur(75px);
    animation: ambientGlowShift 18s ease-in-out infinite alternate;
}

.ambient-orb-2 {
    position: absolute;
    bottom: -15%;
    right: -10%;
    width: 750px;
    height: 750px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.12), transparent 70%);
    filter: blur(85px);
    animation: ambientGlowShift 22s ease-in-out infinite alternate-reverse;
}

@keyframes ambientGlowShift {
    0% {
        transform: translate(0, 0) scale(1);
        opacity: 0.65;
    }
    50% {
        transform: translate(30px, -25px) scale(1.08);
        opacity: 0.85;
    }
    100% {
        transform: translate(-20px, 30px) scale(0.96);
        opacity: 0.7;
    }
}

#ambient-cursor-glow {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    pointer-events: none;
    z-index: 0;
    background: radial-gradient(
        600px circle at var(--cursor-x, 50vw) var(--cursor-y, 50vh),
        rgba(59, 130, 246, 0.12),
        rgba(99, 102, 241, 0.06) 35%,
        rgba(6, 182, 212, 0.03) 55%,
        transparent 75%
    );
    opacity: 0.85;
    transition: opacity 0.4s ease;
}

/* -----------------------------------------------------------------
   TOP NAVIGATION BAR
   ----------------------------------------------------------------- */
.campus-navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 22px;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    background: var(--bg-card);
    border: 1px solid var(--border-card);
    border-radius: 16px;
    margin-bottom: 20px;
    box-shadow: var(--shadow-sm);
    position: relative;
    overflow: hidden;
    transition: all 0.25s ease;
}

.campus-navbar:hover {
    border-color: var(--border-hover);
    box-shadow: var(--shadow-md);
}

.campus-navbar::before, .panel-card::before, .result-card::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: inherit;
    background: radial-gradient(
        420px circle at var(--mouse-x, -500px) var(--mouse-y, -500px),
        rgba(56, 189, 248, 0.08),
        transparent 65%
    );
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.3s ease;
    z-index: 0;
}

.campus-navbar:hover::before, .panel-card:hover::before, .result-card:hover::before {
    opacity: 1;
}

.nav-left {
    display: flex;
    align-items: center;
    gap: 12px;
    position: relative;
    z-index: 1;
}

.nav-brand-logo {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    background: linear-gradient(135deg, #2563eb, #4f46e5);
    color: #ffffff;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35);
    transition: transform 0.25s ease;
}

.campus-navbar:hover .nav-brand-logo {
    transform: scale(1.05) rotate(-2deg);
}

.nav-brand-name {
    font-size: 21px;
    font-weight: 800;
    letter-spacing: -0.4px;
    color: var(--text-primary);
}

.nav-model-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--accent-soft);
    color: var(--accent-primary);
    border: 1px solid var(--accent-soft-border);
    padding: 5px 12px;
    border-radius: 9999px;
    font-size: 11.5px;
    font-weight: 700;
    letter-spacing: 0.3px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.nav-actions {
    position: relative;
    z-index: 1;
}

.theme-toggle-btn {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: var(--bg-card-subtle);
    color: var(--text-primary);
    border: 1px solid var(--border-card);
    padding: 8px 16px;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.theme-toggle-btn:hover {
    background: var(--bg-card-hover);
    border-color: var(--accent-primary);
    color: var(--accent-hover);
    transform: translateY(-1.5px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
}

.theme-toggle-btn:active {
    transform: translateY(0.5px);
}

/* -----------------------------------------------------------------
   HERO WELCOME HEADER
   ----------------------------------------------------------------- */
.hero-box {
    margin-bottom: 22px;
    padding: 6px 4px;
    position: relative;
    z-index: 1;
}

.hero-tagline {
    font-size: 24px;
    font-weight: 800;
    letter-spacing: -0.4px;
    color: var(--text-primary) !important;
    text-shadow: 0 0 24px rgba(56, 189, 248, 0.3);
    margin-bottom: 6px;
}

.hero-subtext {
    font-size: 13.5px;
    color: var(--text-secondary);
    line-height: 1.55;
    margin: 0;
    max-width: 880px;
}

/* -----------------------------------------------------------------
   FEATURE SELECTOR (INTERACTIVE MODE TABS)
   ----------------------------------------------------------------- */
.feature-radio-group {
    background: var(--bg-card-subtle) !important;
    border: 1px solid var(--border-card) !important;
    border-radius: 14px !important;
    padding: 5px !important;
    margin-bottom: 18px !important;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2) !important;
    position: relative !important;
    z-index: 1 !important;
}

.feature-radio-group .wrap {
    display: flex !important;
    gap: 6px !important;
}

.feature-radio-group label {
    flex: 1 !important;
    text-align: center !important;
    border-radius: 10px !important;
    padding: 9px 18px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    color: var(--text-secondary) !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    border: 1px solid transparent !important;
    cursor: pointer !important;
}

.feature-radio-group label:hover {
    color: var(--text-primary) !important;
    background: rgba(255, 255, 255, 0.05) !important;
    border-color: rgba(255, 255, 255, 0.08) !important;
}

.feature-radio-group label.selected,
.feature-radio-group label:has(input:checked) {
    background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.38), inset 0 1px 0 rgba(255, 255, 255, 0.25) !important;
    border-color: rgba(255, 255, 255, 0.15) !important;
    transform: translateY(-1px) !important;
}

/* -----------------------------------------------------------------
   FORM CARDS & PANELS (HOVER & SPOTLIGHT DEPTH)
   ----------------------------------------------------------------- */
.panel-card {
    backdrop-filter: blur(14px) !important;
    -webkit-backdrop-filter: blur(14px) !important;
    background: var(--bg-card) !important;
    border: 1px solid var(--border-card) !important;
    border-radius: 16px !important;
    padding: 22px 24px !important;
    box-shadow: var(--shadow-md) !important;
    transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1),
                box-shadow 0.25s cubic-bezier(0.16, 1, 0.3, 1),
                border-color 0.25s ease,
                background 0.25s ease !important;
    position: relative !important;
    overflow: hidden !important;
}

.panel-card:hover {
    transform: translateY(-3px) !important;
    border-color: var(--border-hover) !important;
    box-shadow: var(--shadow-hover) !important;
    background: var(--bg-card-hover) !important;
}

.panel-title {
    font-size: 17px !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    margin-bottom: 2px !important;
    position: relative !important;
    z-index: 1 !important;
}

.panel-caption {
    font-size: 12.5px !important;
    color: var(--text-muted) !important;
    margin-bottom: 14px !important;
    position: relative !important;
    z-index: 1 !important;
}

/* -----------------------------------------------------------------
   QUICK PROMPT CHIP BUTTONS
   ----------------------------------------------------------------- */
.quick-prompt-btn {
    background: var(--bg-card-subtle) !important;
    color: var(--text-secondary) !important;
    border: 1px solid var(--border-card) !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    padding: 6px 12px !important;
    border-radius: 8px !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

.quick-prompt-btn:hover {
    background: linear-gradient(135deg, rgba(37, 99, 235, 0.14), rgba(99, 102, 241, 0.16)) !important;
    border-color: var(--accent-primary) !important;
    color: var(--text-primary) !important;
    transform: translateY(-1.5px) !important;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2), 0 0 10px rgba(59, 130, 246, 0.18) !important;
}

.quick-prompt-btn:active {
    transform: translateY(0.5px) !important;
}

/* -----------------------------------------------------------------
   INPUT CONTROLS & DROPDOWNS
   ----------------------------------------------------------------- */
input[type="text"], textarea, .gr-textbox input, .gr-textbox textarea, select, .gr-dropdown {
    background: var(--bg-card-subtle) !important;
    border: 1px solid var(--border-card) !important;
    color: var(--text-primary) !important;
    border-radius: 10px !important;
    transition: all 0.2s ease !important;
}

input[type="text"]:focus, textarea:focus, .gr-textbox input:focus, .gr-textbox textarea:focus {
    border-color: var(--accent-primary) !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.25), 0 0 12px rgba(6, 182, 212, 0.15) !important;
    background: var(--bg-card) !important;
    outline: none !important;
}

/* -----------------------------------------------------------------
   PRIMARY & SECONDARY ACTION BUTTONS
   ----------------------------------------------------------------- */
.btn-primary-action {
    background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 14.5px !important;
    padding: 12px 24px !important;
    border-radius: 10px !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.32), inset 0 1px 0 rgba(255, 255, 255, 0.22) !important;
    position: relative !important;
    overflow: hidden !important;
    transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1) !important;
    margin-top: 12px !important;
}

.btn-primary-action::after {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 60%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.22), transparent);
    transform: skewX(-20deg);
    transition: left 0.6s ease;
    pointer-events: none;
}

.btn-primary-action:hover {
    background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.45), 0 0 14px rgba(99, 102, 241, 0.3) !important;
}

.btn-primary-action:hover::after {
    left: 140%;
}

.btn-primary-action:active {
    transform: translateY(1px) !important;
    box-shadow: 0 2px 6px rgba(37, 99, 235, 0.3) !important;
}

.btn-secondary-action {
    background: var(--bg-card-subtle) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-card) !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    padding: 7px 14px !important;
    transition: all 0.2s ease !important;
}

.btn-secondary-action:hover {
    background: var(--bg-card-hover) !important;
    border-color: var(--accent-primary) !important;
    color: var(--accent-hover) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
}

/* -----------------------------------------------------------------
   RESULT CARD & MARKDOWN DISPLAY
   ----------------------------------------------------------------- */
.result-card {
    backdrop-filter: blur(14px) !important;
    -webkit-backdrop-filter: blur(14px) !important;
    background: var(--bg-card) !important;
    border: 1px solid var(--border-card) !important;
    border-radius: 16px !important;
    padding: 24px !important;
    box-shadow: var(--shadow-md) !important;
    min-height: 480px;
    max-height: 720px;
    overflow-y: auto !important;
    position: relative !important;
    transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1),
                box-shadow 0.25s cubic-bezier(0.16, 1, 0.3, 1),
                border-color 0.25s ease !important;
}

.result-card:hover {
    transform: translateY(-2px) !important;
    border-color: var(--border-hover) !important;
    box-shadow: var(--shadow-hover) !important;
}

.result-card * {
    color: var(--text-primary) !important;
}

.result-card h1, .result-card h2, .result-card h3, .result-card h4 {
    color: var(--accent-primary) !important;
    margin-top: 14px;
    margin-bottom: 8px;
    font-weight: 700;
}

.result-card code {
    background: var(--bg-card-subtle) !important;
    color: #38bdf8 !important;
    padding: 3px 7px;
    border-radius: 5px;
    font-size: 12.5px;
    border: 1px solid rgba(56, 189, 248, 0.15);
}

.result-card pre {
    background: var(--code-bg) !important;
    border: 1px solid var(--border-card) !important;
    border-radius: 10px;
    padding: 16px;
    overflow-x: auto;
    box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.3);
}

.result-card pre code, .result-card pre * {
    background: transparent !important;
    color: var(--code-text) !important;
}

.result-card blockquote {
    border-left: 3px solid var(--accent-primary) !important;
    background: var(--bg-card-subtle) !important;
    padding: 10px 14px;
    border-radius: 6px;
    margin: 10px 0;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.demo-notice-box {
    font-size: 12px;
    color: var(--text-muted);
    background: var(--bg-card-subtle);
    border-left: 3px solid var(--accent-primary);
    padding: 10px 14px;
    border-radius: 6px;
    margin-top: 14px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

/* -----------------------------------------------------------------
   ANIMATED EMPTY STATE (SLOW FLOATING GLOW)
   ----------------------------------------------------------------- */
@keyframes emptyIconFloat {
    0%, 100% {
        transform: translateY(0px) scale(1);
    }
    50% {
        transform: translateY(-8px) scale(1.03);
    }
}

@keyframes emptyPulseGlow {
    0%, 100% {
        box-shadow: 0 0 25px rgba(59, 130, 246, 0.15), 0 0 50px rgba(99, 102, 241, 0.08);
        border-color: rgba(59, 130, 246, 0.22);
    }
    50% {
        box-shadow: 0 0 35px rgba(59, 130, 246, 0.32), 0 0 70px rgba(99, 102, 241, 0.16);
        border-color: rgba(56, 189, 248, 0.4);
    }
}

@keyframes fadeInEntrance {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.result-placeholder-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 72px 20px;
    min-height: 380px;
    animation: fadeInEntrance 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

.placeholder-icon-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 76px;
    height: 76px;
    border-radius: 20px;
    background: radial-gradient(circle, rgba(59, 130, 246, 0.2), rgba(15, 23, 42, 0.4));
    border: 1px solid rgba(59, 130, 246, 0.25);
    margin-bottom: 18px;
    animation: emptyIconFloat 4.5s ease-in-out infinite, emptyPulseGlow 4.5s ease-in-out infinite;
}

.placeholder-icon {
    font-size: 32px;
    line-height: 1;
}

.placeholder-title {
    font-size: 19px;
    font-weight: 700;
    letter-spacing: -0.3px;
    color: var(--text-primary);
    margin-bottom: 8px;
}

.placeholder-instruction {
    font-size: 13.5px;
    color: var(--text-muted);
    max-width: 400px;
    line-height: 1.55;
}

/* -----------------------------------------------------------------
   FLOATING TOAST NOTIFICATION
   ----------------------------------------------------------------- */
.campusmate-toast {
    position: fixed;
    bottom: 28px;
    right: 28px;
    background: linear-gradient(135deg, #1e293b, #0f172a);
    color: #38bdf8;
    border: 1px solid rgba(56, 189, 248, 0.35);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.45), 0 0 18px rgba(56, 189, 248, 0.2);
    padding: 10px 18px;
    border-radius: 10px;
    font-size: 13.5px;
    font-weight: 600;
    z-index: 99999;
    animation: toastEntrance 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    transition: opacity 0.35s ease, transform 0.35s ease;
}

.campusmate-toast.hide {
    opacity: 0;
    transform: translateY(10px);
}

@keyframes toastEntrance {
    from {
        opacity: 0;
        transform: translateY(14px) scale(0.96);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

/* Footer note */
.footer-bar {
    text-align: center;
    font-size: 12px;
    color: var(--text-muted);
    margin-top: 30px;
    padding-top: 16px;
    border-top: 1px solid var(--border-subtle);
    position: relative;
    z-index: 1;
}

/* Accessibility & Reduced Motion */
@media (prefers-reduced-motion: reduce) {
    *, ::before, ::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
    #ambient-cursor-glow, .ambient-orb-1, .ambient-orb-2 {
        display: none !important;
    }
}

@media (hover: none) {
    #ambient-cursor-glow {
        display: none !important;
    }
}
""" + NOTES_PAGE_CSS

EMPTY_RESULT_PLACEHOLDER = (
    '<div class="result-placeholder-box">\n'
    '    <div class="placeholder-icon-wrapper">\n'
    '        <div class="placeholder-icon">📋</div>\n'
    '    </div>\n'
    '    <div class="placeholder-title">Your results will appear here</div>\n'
    '    <div class="placeholder-instruction">Choose a mode, enter your request, and click Generate to get started.</div>\n'
    '</div>'
)

# Client script for instant theme toggling and localStorage persistence
THEME_JS_HEAD = """
<script>
function applyCampusMateTheme(theme) {
    const isDark = theme === 'dark';
    const root = document.documentElement;
    const body = document.body;
    const cont = document.querySelector('.gradio-container');

    if (isDark) {
        root.classList.add('dark');
        body.classList.add('dark');
        if (cont) cont.classList.add('dark');
    } else {
        root.classList.remove('dark');
        body.classList.remove('dark');
        if (cont) cont.classList.remove('dark');
    }
    try {
        localStorage.setItem('campusmate_theme', theme);
    } catch(e) {}

    const icon = document.getElementById('theme-icon');
    const text = document.getElementById('theme-text');
    if (icon) icon.textContent = isDark ? '☀️' : '🌙';
    if (text) text.textContent = isDark ? 'Light' : 'Dark';
}

function toggleCampusMateTheme() {
    const isDark = document.body.classList.contains('dark') || document.documentElement.classList.contains('dark');
    applyCampusMateTheme(isDark ? 'light' : 'dark');
}

// Global Toast Notification Helper
window.showCampusMateToast = function(msg) {
    try {
        const toast = document.createElement('div');
        toast.textContent = msg;
        toast.className = 'campusmate-toast';
        document.body.appendChild(toast);
        setTimeout(() => {
            toast.classList.add('hide');
            setTimeout(() => toast.remove(), 400);
        }, 2200);
    } catch(e) {}
};

// Initial auto-detection (Default to 'dark' for premium cyber aesthetic)
(function() {
    try {
        const urlParams = new URLSearchParams(window.location.search);
        const queryTheme = urlParams.get('theme');
        const saved = queryTheme || localStorage.getItem('campusmate_theme') || 'dark';
        applyCampusMateTheme(saved);
    } catch(e) {}
    window.addEventListener('DOMContentLoaded', () => {
        try {
            const urlParams = new URLSearchParams(window.location.search);
            const queryTheme = urlParams.get('theme');
            const saved = queryTheme || localStorage.getItem('campusmate_theme') || 'dark';
            applyCampusMateTheme(saved);
        } catch(e) {}
    });
})();

// Cursor-Following Ambient Glow & Card Spotlight (Desktop only)
(function() {
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    let ticking = false;

    window.addEventListener('pointermove', function(e) {
        if (!ticking) {
            ticking = true;
            requestAnimationFrame(function() {
                document.documentElement.style.setProperty('--cursor-x', e.clientX + 'px');
                document.documentElement.style.setProperty('--cursor-y', e.clientY + 'px');
                
                // Card spotlight calculation
                const card = e.target && e.target.closest ? e.target.closest('.panel-card, .result-card, .campus-navbar, .folder-card, .recent-card, .note-card, .modal-card') : null;
                if (card) {
                    const rect = card.getBoundingClientRect();
                    card.style.setProperty('--mouse-x', (e.clientX - rect.left) + 'px');
                    card.style.setProperty('--mouse-y', (e.clientY - rect.top) + 'px');
                }
                ticking = false;
            });
        }
    }, { passive: true });
})();
</script>
"""

# -------------------------------------------------------------------
# Core Dispatcher & Route Engine Handlers
# -------------------------------------------------------------------

def execute_campus_navigation(start_loc: str, end_loc: str, query_text: str):
    """
    Dijkstra Shortest Path Navigation (Pure Local Python • 0 API Calls).
    Calculates walking distance, time, directions, and SVG map diagram.
    """
    t0 = time.time()
    s_id = start_loc
    e_id = end_loc

    # If student provided free-form text, attempt to resolve endpoints
    nl_note = ""
    if query_text and query_text.strip():
        detected_s, detected_e, reason = MAP_ENGINE.parse_natural_language_query(query_text)
        if detected_s and detected_e:
            s_id = detected_s
            e_id = detected_e
            nl_note = f"\n> 🔍 *Detected endpoints: **{MAP_ENGINE.locations[s_id]['name']}** to **{MAP_ENGINE.locations[e_id]['name']}** ({reason})*\n\n"
        elif not s_id or not e_id:
            return (
                "⚠️ **Location Not Recognized:**\n\n"
                f"Could not clearly resolve both a starting point and destination from: *\"{query_text}\"*\n\n"
                "**Please select your Origin and Destination from the dropdown menus**, or try phrasing like:\n"
                "- *\"From Canteen to CSE Block\"*\n"
                "- *\"I'm standing near the library. Take me to the sports complex.\"*",
                gr.update(value="", visible=False)
            )

    if not s_id or not e_id:
        return "⚠️ **Please select both an Origin and Destination location.**", gr.update(value="", visible=False)

    # Execute deterministic Dijkstra route search
    route = MAP_ENGINE.find_shortest_route(s_id, e_id)
    if route.get("status") != "success":
        return f"⚠️ **Navigation Error:** {route.get('message', 'Route not found.')}", gr.update(value="", visible=False)

    md_content = MAP_ENGINE.render_route_markdown(route)
    svg_diagram = MAP_ENGINE.render_route_svg(route)

    elapsed_ms = round((time.time() - t0) * 1000, 1)
    footer_badge = (
        f"\n\n---\n"
        f"<div style='font-size: 11.5px; color: var(--text-muted); display: flex; justify-content: space-between;'>"
        f"<span>🧭 <b>Local Dijkstra Engine:</b> {elapsed_ms}ms</span>"
        f"<span>⚡ <b>API Calls:</b> 0 (Pure Local Routing)</span>"
        f"<span>📏 <b>Dataset:</b> campus_map.json</span>"
        f"</div>"
    )

    combined_output = nl_note + md_content + footer_badge
    return combined_output, gr.update(value=svg_diagram, visible=bool(svg_diagram))


def execute_campus_guide_qa(question: str, topic_filter: str):
    """Answers general campus procedure queries using Gemma 4 (1 API Call)."""
    t0 = time.time()
    try:
        if not question or not question.strip():
            return "⚠️ **Input Required:** Please enter your campus question or click a quick prompt.", gr.update(value="", visible=False)
        res = run_campus_guide(question, CAMPUS_DATA, topic_filter)
        duration = round(time.time() - t0, 2)
        badge = (
            f"\n\n---\n"
            f"<div style='font-size: 11.5px; color: var(--text-muted); display: flex; justify-content: space-between;'>"
            f"<span>⚡ <b>Model:</b> {GEMMA_MODEL_ID}</span>"
            f"<span>🎯 <b>Single-Request Execution:</b> {duration}s</span>"
            f"<span>🏫 <b>CampusMate AI Engine</b></span>"
            f"</div>"
        )
        return res + badge, gr.update(value="", visible=False)
    except CampusMateAPIError as err:
        return f"### ❌ Request Error\n\n{str(err)}", gr.update(value="", visible=False)
    except Exception as exc:
        return f"### ❌ Unexpected Error\n\n{str(exc)[:200]}", gr.update(value="", visible=False)


def execute_study_mate(task_type: str, subject: str, timeline: str, hours: float, weak: str, inst: str):
    """Generates study plans or concept explanations with KaTeX math using Gemma 4 (1 API Call)."""
    t0 = time.time()
    try:
        if not subject or not subject.strip():
            return "⚠️ **Input Required:** Please enter a subject, topic, or question in the StudyMate input field.", gr.update(value="", visible=False)
        res = run_study_mate(task_type, subject, timeline, hours, weak, inst)
        duration = round(time.time() - t0, 2)
        badge = (
            f"\n\n---\n"
            f"<div style='font-size: 11.5px; color: var(--text-muted); display: flex; justify-content: space-between;'>"
            f"<span>⚡ <b>Model:</b> {GEMMA_MODEL_ID}</span>"
            f"<span>🎯 <b>Single-Request Execution:</b> {duration}s</span>"
            f"<span>📚 <b>StudyMate Academic Tutor</b></span>"
            f"</div>"
        )
        return res + badge, gr.update(value="", visible=False)
    except CampusMateAPIError as err:
        return f"### ❌ Request Error\n\n{str(err)}", gr.update(value="", visible=False)
    except Exception as exc:
        return f"### ❌ Unexpected Error\n\n{str(exc)[:200]}", gr.update(value="", visible=False)


def execute_campus_fix(desc: str, loc: str, urgency: str, context: str):
    """Produces structured facility incident reports using Gemma 4 (1 API Call)."""
    t0 = time.time()
    try:
        if not desc or not desc.strip():
            return "⚠️ **Input Required:** Please describe the campus facility or lab issue.", gr.update(value="", visible=False)
        res = run_campus_fix(desc, loc, urgency, context)
        duration = round(time.time() - t0, 2)
        badge = (
            f"\n\n---\n"
            f"<div style='font-size: 11.5px; color: var(--text-muted); display: flex; justify-content: space-between;'>"
            f"<span>⚡ <b>Model:</b> {GEMMA_MODEL_ID}</span>"
            f"<span>🎯 <b>Single-Request Execution:</b> {duration}s</span>"
            f"<span>🛠️ <b>CampusFix Reporting Engine</b></span>"
            f"</div>"
        )
        return res + badge, gr.update(value="", visible=False)
    except CampusMateAPIError as err:
        return f"### ❌ Request Error\n\n{str(err)}", gr.update(value="", visible=False)
    except Exception as exc:
        return f"### ❌ Unexpected Error\n\n{str(exc)[:200]}", gr.update(value="", visible=False)


# -------------------------------------------------------------------
# Gradio UI Construction (Single-Screen Centered Layout)
# -------------------------------------------------------------------

def build_app():
    with gr.Blocks(title="CampusMate AI - Powered by Gemma 4") as demo:
        # State tracker for main mode
        active_mode = gr.State(value="Campus Guide")
        guide_submode = gr.State(value="Navigation")

        with gr.Column(elem_classes=["app-container"]):
            # Ambient background effect & cursor glow elements
            gr.HTML("""
            <div class="ambient-light-bg" aria-hidden="true">
                <div class="ambient-orb-1"></div>
                <div class="ambient-orb-2"></div>
            </div>
            <div id="ambient-cursor-glow" aria-hidden="true"></div>
            """)

            # 1. Top Navigation Bar (with Logo, Model Badge, and Theme Switcher)
            gr.HTML("""
            <div class="campus-navbar">
                <div class="nav-left">
                    <div class="nav-brand-logo">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
                            <path d="M6 12v5c3 3 9 3 12 0v-5"/>
                        </svg>
                    </div>
                    <div>
                        <div class="nav-brand-name">CampusMate AI</div>
                    </div>
                    <div class="nav-model-pill">
                        <span>⚡ Powered by Gemma 4</span>
                        <span style="opacity: 0.8; font-weight: normal;">(gemma-4-26b-a4b-it)</span>
                    </div>
                </div>
                <div class="nav-actions">
                    <a href="/notes" id="nav-notes-link" class="nav-notes-btn" title="My Notes" aria-label="My Notes">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
                            <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
                        </svg>
                        <span>My Notes</span>
                    </a>
                    <button id="theme-toggle" class="theme-toggle-btn" onclick="toggleCampusMateTheme()" title="Switch Light/Dark Mode">
                        <span id="theme-icon">🌙</span> <span id="theme-text">Dark</span>
                    </button>
                </div>
            </div>
            """)

            # 2. Hero Headline
            gr.HTML("""
            <div class="hero-box">
                <div class="hero-tagline">"Your campus. Your academics. Your AI companion."</div>
                <p class="hero-subtext">
                    A lightweight, privacy-first companion engineered for college students to navigate campus facilities, 
                    craft realistic examination schedules, master challenging concepts, and generate structured incident reports.
                </p>
            </div>
            """)

            # 3. Three Unified Feature Selectors (Clean Horizontal Tabs)
            mode_selector = gr.Radio(
                choices=["Campus Guide", "StudyMate", "CampusFix"],
                value="Campus Guide",
                label="Select Mode",
                show_label=False,
                interactive=True,
                elem_classes=["feature-radio-group"]
            )

            # 4. Main Interaction Grid (Inputs on Left, Results on Right)
            with gr.Row():
                # LEFT COLUMN: INPUT PANELS
                with gr.Column(scale=5):
                    # ==========================================
                    # MODE 1: CAMPUS GUIDE (Navigation & Q&A)
                    # ==========================================
                    with gr.Group(visible=True, elem_classes=["panel-card"]) as guide_panel:
                        gr.HTML("""
                        <div class="panel-title">🏫 Campus Guide</div>
                        <div class="panel-caption">Navigate physical buildings or ask procedural questions about rules, labs, and clubs.</div>
                        """)

                        # Segmented submode switch
                        guide_mode_switch = gr.Radio(
                            choices=["Campus Navigation", "Campus Q&A"],
                            value="Campus Navigation",
                            label="Campus Guide Feature",
                            show_label=False,
                            interactive=True
                        )

                        # SUB-PANEL A: CAMPUS NAVIGATION
                        with gr.Group(visible=True) as nav_subgroup:
                            with gr.Row():
                                nav_start_drop = gr.Dropdown(
                                    choices=LOCATION_CHOICES,
                                    value="main_canteen",
                                    label="Starting Location (Origin)",
                                    interactive=True,
                                    scale=1
                                )
                                nav_end_drop = gr.Dropdown(
                                    choices=LOCATION_CHOICES,
                                    value="cse_block",
                                    label="Destination (Target Building)",
                                    interactive=True,
                                    scale=1
                                )

                            gr.Markdown("**Quick Route Samples (Click to load):**")
                            with gr.Row():
                                btn_r1 = gr.Button("Canteen ➔ CSE Block", size="sm", elem_classes=["quick-prompt-btn"])
                                btn_r2 = gr.Button("Main Gate ➔ Library", size="sm", elem_classes=["quick-prompt-btn"])
                            with gr.Row():
                                btn_r3 = gr.Button("Admin ➔ Sports Complex", size="sm", elem_classes=["quick-prompt-btn"])
                                btn_r4 = gr.Button("Main Lab ➔ Mech Workshop", size="sm", elem_classes=["quick-prompt-btn"])

                            nav_query_input = gr.Textbox(
                                label="Or Ask in Natural Language (Optional)",
                                placeholder="e.g., I'm standing in front of the canteen. Take me to the CSE block.",
                                lines=2,
                                interactive=True
                            )

                            find_route_btn = gr.Button(
                                "🧭 Find Shortest Route (Local Dijkstra)",
                                variant="primary",
                                elem_classes=["btn-primary-action"],
                                size="lg"
                            )

                            gr.HTML("""
                            <div class="demo-notice-box">
                                ℹ️ <b>Deterministic Routing:</b> Computed instantly using local Dijkstra graph algorithm in Python (0 API calls). 
                                Local pathways are defined in <code>campus_map.json</code>.
                            </div>
                            """)

                        # SUB-PANEL B: CAMPUS Q&A (Powered by Gemma 4)
                        with gr.Group(visible=False) as qa_subgroup:
                            qa_topic_filter = gr.Dropdown(
                                choices=["All", "Academics & Library", "Clubs & Activities", "Lab Etiquette", "College Procedures", "Campus Facilities"],
                                value="College Procedures",
                                label="Topic Filter",
                                interactive=True
                            )

                            gr.Markdown("**Quick Prompts (Click to populate):**")
                            with gr.Row():
                                btn_q1 = gr.Button("Attendance Shortfall (75%)", size="sm", elem_classes=["quick-prompt-btn"])
                                btn_q2 = gr.Button("First-Year Prep", size="sm", elem_classes=["quick-prompt-btn"])
                            with gr.Row():
                                btn_q3 = gr.Button("Practical Exam Rules", size="sm", elem_classes=["quick-prompt-btn"])
                                btn_q4 = gr.Button("Technical Clubs & Societies", size="sm", elem_classes=["quick-prompt-btn"])

                            qa_query_input = gr.Textbox(
                                label="Your Campus Question",
                                placeholder="e.g., What should I check if my attendance drops below the 75% requirement?",
                                lines=3,
                                interactive=True
                            )

                            ask_gemma_btn = gr.Button(
                                "⚡ Ask Gemma 4 (Single Call)",
                                variant="primary",
                                elem_classes=["btn-primary-action"],
                                size="lg"
                            )

                            gr.HTML("""
                            <div class="demo-notice-box">
                                ℹ️ Campus procedures are augmented from local reference data (<code>campus_data.json</code>). 
                                Always confirm official submissions with college authorities.
                            </div>
                            """)

                    # ==========================================
                    # MODE 2: STUDYMATE
                    # ==========================================
                    with gr.Group(visible=False, elem_classes=["panel-card"]) as study_panel:
                        gr.HTML("""
                        <div class="panel-title">📚 StudyMate</div>
                        <div class="panel-caption">Generate realistic study roadmaps, understand complex concepts, and solve questions.</div>
                        """)

                        study_task_input = gr.Radio(
                            choices=["Create a study plan", "Explain a concept", "Solve or explain an academic question"],
                            value="Create a study plan",
                            label="Study Objective",
                            interactive=True
                        )

                        gr.Markdown("**Quick Prompts (Click to populate):**")
                        with gr.Row():
                            btn_s1 = gr.Button("DSA 7-Day Plan", size="sm", elem_classes=["quick-prompt-btn"])
                            btn_s2 = gr.Button("Dijkstra vs Bellman-Ford", size="sm", elem_classes=["quick-prompt-btn"])
                        with gr.Row():
                            btn_s3 = gr.Button("Deadlock & Banker's Algo", size="sm", elem_classes=["quick-prompt-btn"])
                            btn_s4 = gr.Button("Eigenvalues: Av = λv", size="sm", elem_classes=["quick-prompt-btn"])

                        study_subj_input = gr.Textbox(
                            label="Subject, Topic, or Question",
                            placeholder="e.g., Data Structures: Trees, Graphs, and Dynamic Programming",
                            lines=2,
                            interactive=True
                        )

                        with gr.Row():
                            study_timeline_input = gr.Textbox(
                                label="Timeline / Exam Date",
                                placeholder="e.g., Mid-semester in 7 days",
                                scale=3,
                                interactive=True
                            )
                            study_hours_input = gr.Slider(
                                minimum=1.0,
                                maximum=12.0,
                                value=3.0,
                                step=0.5,
                                label="Daily Study Hours",
                                scale=2,
                                interactive=True
                            )

                        study_weak_input = gr.Textbox(
                            label="Weak Areas / Priority Topics (Optional)",
                            placeholder="e.g., Graph traversals (BFS/DFS), Dynamic Programming memoization",
                            lines=1,
                            interactive=True
                        )

                        study_inst_input = gr.Textbox(
                            label="Additional Notes / Question Details (Optional)",
                            placeholder="e.g., Include daily revision sessions and practice problem suggestions.",
                            lines=2,
                            interactive=True
                        )

                        study_gen_btn = gr.Button(
                            "⚡ Generate StudyMate Plan with Gemma 4",
                            variant="primary",
                            elem_classes=["btn-primary-action"],
                            size="lg"
                        )

                    # ==========================================
                    # MODE 3: CAMPUSFIX
                    # ==========================================
                    with gr.Group(visible=False, elem_classes=["panel-card"]) as fix_panel:
                        gr.HTML("""
                        <div class="panel-title">🛠️ CampusFix</div>
                        <div class="panel-caption">Transform campus facility, Wi-Fi, or lab issues into a professional, actionable incident report draft.</div>
                        """)

                        gr.Markdown("**Quick Prompts (Click to populate):**")
                        with gr.Row():
                            btn_f1 = gr.Button("Lab Wi-Fi Disconnecting", size="sm", elem_classes=["quick-prompt-btn"])
                            btn_f2 = gr.Button("Oscilloscope Noise", size="sm", elem_classes=["quick-prompt-btn"])
                        with gr.Row():
                            btn_f3 = gr.Button("Projector Overheating", size="sm", elem_classes=["quick-prompt-btn"])

                        fix_desc_input = gr.Textbox(
                            label="Issue Description",
                            placeholder="e.g., The Wi-Fi router in the ECE Microprocessor laboratory keeps disconnecting every 5 minutes.",
                            lines=3,
                            interactive=True
                        )

                        with gr.Row():
                            fix_loc_input = gr.Textbox(
                                label="Campus Location",
                                placeholder="e.g., Block 3, 2nd Floor, Room 214 (VLSI Lab)",
                                scale=3,
                                interactive=True
                            )
                            fix_urgency_input = gr.Dropdown(
                                choices=["Low", "Medium", "High", "Critical / Time-sensitive"],
                                value="Medium",
                                label="Urgency",
                                scale=2,
                                interactive=True
                            )

                        fix_context_input = gr.Textbox(
                            label="Academic / Safety Context",
                            placeholder="e.g., Graded online practical examination scheduled tomorrow at 9:00 AM.",
                            lines=2,
                            interactive=True
                        )

                        fix_gen_btn = gr.Button(
                            "⚡ Generate Incident Report with Gemma 4",
                            variant="primary",
                            elem_classes=["btn-primary-action"],
                            size="lg"
                        )

                        gr.HTML("""
                        <div class="demo-notice-box">
                            ⚠️ <b>Draft Only:</b> Produces a structured draft for student review. Does not auto-submit tickets.
                        </div>
                        """)

                # RIGHT COLUMN: GENERATED RESULT PANEL (SAME SCREEN)
                with gr.Column(scale=6):
                    gr.Markdown("### 📋 Generated Intelligence & Navigation")
                    
                    # Interactive SVG Route Visualizer Display (starts empty and hidden)
                    svg_display = gr.HTML(
                        value="",
                        visible=False
                    )

                    # Formatted Markdown Display with KaTeX LaTeX Delimiters Enabled
                    # Starts with a clean, neutral placeholder state - zero pre-computed answers on initial load
                    output_markdown = gr.Markdown(
                        value=EMPTY_RESULT_PLACEHOLDER,
                        latex_delimiters=[
                            {"left": "$$", "right": "$$", "display": True},
                            {"left": "$", "right": "$", "display": False}
                        ],
                        elem_classes=["result-card"]
                    )

                    with gr.Row():
                        copy_btn = gr.Button("📋 Copy Response", size="sm", elem_classes=["btn-secondary-action"])
                        clear_btn = gr.Button("🗑️ Clear Output", size="sm", elem_classes=["btn-secondary-action"])

            # 5. Footer Bar
            gr.HTML("""
            <div class="footer-bar">
                CampusMate AI • Developed for "Build for Your Campus" Hackathon • Powered by Google DeepMind's Gemma 4 (gemma-4-26b-a4b-it) • MIT License
            </div>
            """)

        # =================================================================
        # Mode Switching Event Handlers
        # =================================================================
        def on_mode_switch(selected):
            return (
                selected,
                gr.update(visible=(selected == "Campus Guide")),
                gr.update(visible=(selected == "StudyMate")),
                gr.update(visible=(selected == "CampusFix"))
            )

        mode_selector.change(
            fn=on_mode_switch,
            inputs=[mode_selector],
            outputs=[active_mode, guide_panel, study_panel, fix_panel]
        )

        def on_guide_submode_switch(submode):
            return (
                submode,
                gr.update(visible=(submode == "Campus Navigation")),
                gr.update(visible=(submode == "Campus Q&A"))
            )

        guide_mode_switch.change(
            fn=on_guide_submode_switch,
            inputs=[guide_mode_switch],
            outputs=[guide_submode, nav_subgroup, qa_subgroup]
        )

        # Clear output resets to clean empty state
        clear_btn.click(
            fn=lambda: (gr.update(value="", visible=False), EMPTY_RESULT_PLACEHOLDER),
            inputs=[],
            outputs=[svg_display, output_markdown]
        )

        # Copy to clipboard
        copy_btn.click(
            fn=None,
            inputs=[output_markdown],
            js="""(text) => {
                if (navigator.clipboard) {
                    navigator.clipboard.writeText(text).then(() => {
                        if (window.showCampusMateToast) {
                            window.showCampusMateToast('✓ Response copied to clipboard!');
                        } else {
                            alert('Copied response to clipboard!');
                        }
                    }).catch(() => {
                        alert('Could not copy response to clipboard.');
                    });
                } else {
                    alert('Clipboard API not supported on this browser.');
                }
            }"""
        )

        # =================================================================
        # Quick Prompt Click Handlers
        # =================================================================
        # Route quick presets
        btn_r1.click(fn=lambda: ("main_canteen", "cse_block", "I am standing in front of the canteen. Take me to the CSE block."), inputs=[], outputs=[nav_start_drop, nav_end_drop, nav_query_input])
        btn_r2.click(fn=lambda: ("main_gate", "library", "From Main Gate to Central Library"), inputs=[], outputs=[nav_start_drop, nav_end_drop, nav_query_input])
        btn_r3.click(fn=lambda: ("admin_block", "sports_complex", "Take me from Admin Block to Sports Complex"), inputs=[], outputs=[nav_start_drop, nav_end_drop, nav_query_input])
        btn_r4.click(fn=lambda: ("main_lab", "mech_workshop", "From Main Lab to Mechanical Workshop"), inputs=[], outputs=[nav_start_drop, nav_end_drop, nav_query_input])

        # Campus Q&A quick presets
        btn_q1.click(fn=lambda: "What should I check and what official procedure should I follow if I have an attendance shortfall below the 75% norm?", inputs=[], outputs=[qa_query_input])
        btn_q2.click(fn=lambda: "How should a first-year engineering student prepare for college academics, time management, and campus life?", inputs=[], outputs=[qa_query_input])
        btn_q3.click(fn=lambda: "How can I prepare effectively for practical examinations, and what laboratory etiquette must I follow?", inputs=[], outputs=[qa_query_input])
        btn_q4.click(fn=lambda: "How can I get started with technical societies, coding clubs, and hackathons as a college student?", inputs=[], outputs=[qa_query_input])

        # StudyMate quick presets
        btn_s1.click(
            fn=lambda: (
                "Create a study plan",
                "Data Structures & Algorithms (Trees, Graphs, and Dynamic Programming)",
                "Mid-semester exam in 7 days",
                3.0,
                "Dynamic programming memoization and Graph BFS/DFS traversal",
                "Include daily practice problem quotas and revision time."
            ),
            inputs=[],
            outputs=[study_task_input, study_subj_input, study_timeline_input, study_hours_input, study_weak_input, study_inst_input]
        )
        btn_s2.click(
            fn=lambda: (
                "Explain a concept",
                "Dijkstra's Shortest Path Algorithm vs Bellman-Ford",
                "Upcoming theory exam",
                2.0,
                "Negative weight cycle detection",
                "Explain the intuition simply with a step-by-step example and big-O complexities."
            ),
            inputs=[],
            outputs=[study_task_input, study_subj_input, study_timeline_input, study_hours_input, study_weak_input, study_inst_input]
        )
        btn_s3.click(
            fn=lambda: (
                "Solve or explain an academic question",
                "Operating Systems: Explain the four Coffman conditions for deadlock, and how Banker's algorithm achieves deadlock avoidance with resource vectors.",
                "End-semester examination",
                2.5,
                "Resource Allocation Graph cycles and safe state calculation",
                "Provide a clear safe state mathematical verification example."
            ),
            inputs=[],
            outputs=[study_task_input, study_subj_input, study_timeline_input, study_hours_input, study_weak_input, study_inst_input]
        )
        btn_s4.click(
            fn=lambda: (
                "Explain a concept",
                "Linear Algebra: Eigenvalues and Eigenvectors defined by equation $Av = \\lambda v$, and characteristic polynomial $\\det(A - \\lambda I) = 0$",
                "Engineering Mathematics II Exam",
                2.0,
                "Diagonalization and multiplicity",
                "Provide step-by-step derivation for a 2x2 matrix with clear mathematical notation."
            ),
            inputs=[],
            outputs=[study_task_input, study_subj_input, study_timeline_input, study_hours_input, study_weak_input, study_inst_input]
        )

        # CampusFix quick presets
        btn_f1.click(
            fn=lambda: (
                "The Wi-Fi in my laboratory keeps disconnecting every few minutes, causing session timeouts on terminal connections.",
                "Block C, 3rd Floor, Room 302 (Network Simulation Lab)",
                "Critical / Time-sensitive",
                "Our class has an online practical examination scheduled here tomorrow morning at 9:00 AM."
            ),
            inputs=[],
            outputs=[fix_desc_input, fix_loc_input, fix_urgency_input, fix_context_input]
        )
        btn_f2.click(
            fn=lambda: (
                "Digital Storage Oscilloscope (Bench 4) has a faulty CH1 probe connector causing heavy noise and signal clipping.",
                "ECE Block, Ground Floor, Electronics Circuits Lab",
                "Medium",
                "Affects two lab groups during daily afternoon practical experiments."
            ),
            inputs=[],
            outputs=[fix_desc_input, fix_loc_input, fix_urgency_input, fix_context_input]
        )
        btn_f3.click(
            fn=lambda: (
                "The ceiling HDMI projector in Lecture Hall 101 blinks continuously and powers down after 10 minutes of usage due to overheating.",
                "Main Academic Block, Lecture Hall 101",
                "High",
                "Major guest lecture and core theory class scheduled tomorrow."
            ),
            inputs=[],
            outputs=[fix_desc_input, fix_loc_input, fix_urgency_input, fix_context_input]
        )

        # =================================================================
        # Execution Button Click Triggers
        # =================================================================
        # 1. Campus Navigation (Local Dijkstra - 0 API calls)
        find_route_btn.click(
            fn=execute_campus_navigation,
            inputs=[nav_start_drop, nav_end_drop, nav_query_input],
            outputs=[output_markdown, svg_display]
        )

        # 2. Campus Q&A (Gemma 4 - 1 API call)
        ask_gemma_btn.click(
            fn=execute_campus_guide_qa,
            inputs=[qa_query_input, qa_topic_filter],
            outputs=[output_markdown, svg_display]
        )

        # 3. StudyMate (Gemma 4 - 1 API call)
        study_gen_btn.click(
            fn=execute_study_mate,
            inputs=[study_task_input, study_subj_input, study_timeline_input, study_hours_input, study_weak_input, study_inst_input],
            outputs=[output_markdown, svg_display]
        )

        # 4. CampusFix (Gemma 4 - 1 API call)
        fix_gen_btn.click(
            fn=execute_campus_fix,
            inputs=[fix_desc_input, fix_loc_input, fix_urgency_input, fix_context_input],
            outputs=[output_markdown, svg_display]
        )

    # Register /notes route and page metadata
    demo.pages.append(("notes", "My Notes", False))

    def render_notes_html():
        return HTMLResponse(
            content=f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>My Notes - CampusMate AI</title>
    {THEME_JS_HEAD}
    <style>
    {CUSTOM_CSS}
    </style>
</head>
<body class="dark">
    {get_notes_page_html()}
</body>
</html>"""
        )

    if hasattr(demo, "app") and demo.app is not None:
        demo.app.add_api_route("/notes", render_notes_html, methods=["GET"], response_class=HTMLResponse)
        demo.app.add_api_route("/notes/", render_notes_html, methods=["GET"], response_class=HTMLResponse)

    return demo


def main():
    """Launch the modernized CampusMate AI application."""
    port = int(os.environ.get("PORT", 7860))
    app = build_app()
    
    # Ensure notes endpoints are attached to the server app
    def render_notes_html():
        return HTMLResponse(
            content=f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>My Notes - CampusMate AI</title>
    {THEME_JS_HEAD}
    <style>
    {CUSTOM_CSS}
    </style>
</head>
<body class="dark">
    {get_notes_page_html()}
</body>
</html>"""
        )

    if hasattr(app, "app") and app.app is not None:
        app.app.add_api_route("/notes", render_notes_html, methods=["GET"], response_class=HTMLResponse)
        app.app.add_api_route("/notes/", render_notes_html, methods=["GET"], response_class=HTMLResponse)

    print("==================================================================")
    print("Starting CampusMate AI (Redesigned • Powered by Gemma 4)")
    print(f"Chatbot Interface: http://127.0.0.1:{port}")
    print(f"My Notes Webpage:  http://127.0.0.1:{port}/notes")
    print("==================================================================")
    app.launch(
        server_name="127.0.0.1",
        server_port=port,
        inbrowser=False,
        head=THEME_JS_HEAD,
        css=CUSTOM_CSS,
        _app=app.app if hasattr(app, "app") else None
    )


if __name__ == "__main__":
    main()
