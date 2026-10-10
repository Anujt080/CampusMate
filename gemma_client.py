"""CampusMate AI - Gemma 4 Client Integration Module
---------------------------------------------------
Strict Hackathon Requirements:
- Model: gemma-4-26b-a4b-it exclusively
- Library: google-genai (from google import genai)
- Single API call per user action (Strict Single-Request Rule)
- Secure GEMINI_API_KEY loading from environment / .env
- Thinking mode disabled by default to minimize latency and token consumption
- Lightweight disk cache to protect free-tier API quotas during demo presentations
- Friendly, masked error handling with zero credential leaks
"""

import hashlib
import json
import logging
import os
import re
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any

# Root directory and .env loading
ROOT_DIR = Path(__file__).resolve().parent

try:
    from dotenv import load_dotenv
    # Load .env if present
    load_dotenv(ROOT_DIR / ".env")
except ImportError:
    pass

# Suppress verbose google_genai logs
logging.getLogger("google_genai.models").setLevel(logging.ERROR)

# Mandatory model constant - never fallback or change
GEMMA_MODEL_ID = "gemma-4-26b-a4b-it"

# Cache directory for demo resilience and quota preservation
CACHE_DIR = ROOT_DIR / ".cache"
USE_CACHE = os.environ.get("GEMMA_CACHE", "1") != "0"

# Rate limiting guard
MIN_SECONDS_BETWEEN_CALLS = 1.0
_last_call_timestamp = 0.0
_client_instance = None


class CampusMateAPIError(Exception):
    """Custom sanitized exception for CampusMate AI."""
    pass


def get_sanitized_api_key() -> str:
    """Safely retrieve GEMINI_API_KEY from environment without exposing it."""
    key = os.environ.get("GEMINI_API_KEY", "").strip().strip("\"'")
    if not key or key == "your_api_key_here" or key == "paste-your-key-here":
        raise CampusMateAPIError(
            "Gemini API key is missing or not configured. "
            "Please create a .env file based on .env.example with: GEMINI_API_KEY=your_key. "
            "Get a free key from Google AI Studio: https://aistudio.google.com"
        )
    return key


def get_genai_client():
    """Initialize or reuse the google-genai client."""
    global _client_instance
    if _client_instance is None:
        key = get_sanitized_api_key()
        from google import genai
        _client_instance = genai.Client(api_key=key)
    return _client_instance


def _cache_key(*args) -> str:
    """Generate SHA-256 hash for query caching."""
    hasher = hashlib.sha256()
    for item in args:
        if isinstance(item, bytes):
            hasher.update(item)
        else:
            hasher.update(str(item).encode("utf-8", errors="ignore"))
        hasher.update(b"\x00")
    return hasher.hexdigest()


def _get_cached_response(key: str) -> Optional[str]:
    """Retrieve saved response from cache if available."""
    if not USE_CACHE:
        return None
    cache_file = CACHE_DIR / f"{key}.json"
    if cache_file.exists():
        try:
            data = json.loads(cache_file.read_text(encoding="utf-8"))
            return data.get("response")
        except Exception:
            return None
    return None


def _save_cached_response(key: str, text: str) -> None:
    """Store generated response in disk cache."""
    if not USE_CACHE or not text:
        return
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_file = CACHE_DIR / f"{key}.json"
        cache_file.write_text(json.dumps({"response": text}, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def sanitize_error_message(err: Exception) -> str:
    """Transform low-level errors into helpful student-facing messages without leaking keys."""
    raw_msg = str(err)
    low_msg = raw_msg.lower()

    if isinstance(err, CampusMateAPIError):
        return str(err)
    if "429" in low_msg or "resource_exhausted" in low_msg:
        return "Gemma API quota limit reached or busy (429). Please wait 30 seconds before retrying."
    if "401" in low_msg or "403" in low_msg or "api_key" in low_msg or "permission" in low_msg:
        return "Authentication error: The provided GEMINI_API_KEY is invalid or lacks permission. Check your .env file."
    if "500" in low_msg or "503" in low_msg or "unavailable" in low_msg:
        return "Google AI server is momentarily busy (503). Please retry your request in a few moments."
    if any(k in low_msg for k in ["timeout", "timed out", "connection", "getaddrinfo", "ssl"]):
        return "Network connection issue. Please check your internet connectivity or hotspot."

    # Strip the real key explicitly, plus any general key patterns
    key = os.environ.get("GEMINI_API_KEY", "").strip().strip("\"'")
    safe_text = raw_msg
    if key and len(key) > 8:
        safe_text = safe_text.replace(key, "[REDACTED_API_KEY]")
    safe_text = re.sub(r"AIza[0-9A-Za-z_-]{35}", "[REDACTED_API_KEY]", safe_text)
    safe_text = re.sub(r"AQ\.[0-9A-Za-z_-]{30,}", "[REDACTED_API_KEY]", safe_text)
    return f"Request failed: {safe_text[:250]}"


def _call_gemma_single_request(contents: Any, system_instruction: str) -> str:
    """Core function executing exactly ONE API request to Gemma 4."""
    global _last_call_timestamp

    # Enforce minimum spacing between calls to respect rate-limits
    elapsed = time.monotonic() - _last_call_timestamp
    if elapsed < MIN_SECONDS_BETWEEN_CALLS:
        time.sleep(MIN_SECONDS_BETWEEN_CALLS - elapsed)

    client = get_genai_client()
    from google.genai import types

    # Strictly disabled thinking mode by default for lightweight, low-latency execution
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.3,
        max_output_tokens=2048,
    )

    # Transient error retry for Google side glitches (500, 503, 429)
    max_retries = 3
    retry_delays = (2, 4, 8)
    
    last_err = None
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=GEMMA_MODEL_ID,
                contents=contents,
                config=config,
            )
            _last_call_timestamp = time.monotonic()
            if response and response.text:
                return response.text
            return "Gemma 4 completed processing but returned no text. Please refine your query."
        except Exception as exc:
            _last_call_timestamp = time.monotonic()
            last_err = exc
            err_str = str(exc).lower()
            is_transient = (
                "500" in err_str or "503" in err_str or "internal error" in err_str or
                "unavailable" in err_str or "429" in err_str or "resource_exhausted" in err_str
            )
            if is_transient and attempt < max_retries - 1:
                wait_sec = retry_delays[attempt]
                time.sleep(wait_sec)
                continue
            raise CampusMateAPIError(sanitize_error_message(exc)) from exc

    if last_err:
        raise CampusMateAPIError(sanitize_error_message(last_err))
    return "No response received."


# -------------------------------------------------------------
# MODE 1: CAMPUS GUIDE
# -------------------------------------------------------------
def run_campus_guide(question: str, campus_data: Dict[str, Any], topic_filter: str = "All") -> str:
    """Process a Campus Guide query with local knowledge base injection in a single request."""
    clean_q = question.strip()
    if not clean_q:
        raise CampusMateAPIError("Please enter a question or select an example prompt.")
    if len(clean_q) > 1000:
        raise CampusMateAPIError("Question exceeds character limit (1000 chars). Please keep it concise.")

    # Select relevant subset of local campus data to keep context concise
    selected_context = {}
    if topic_filter == "All" or topic_filter == "Academics & Library":
        selected_context["academic_resources"] = campus_data.get("academic_resources", [])
        selected_context["library_usage"] = campus_data.get("library_usage", {})
    if topic_filter == "All" or topic_filter == "Clubs & Activities":
        selected_context["student_clubs"] = campus_data.get("student_clubs", [])
    if topic_filter == "All" or topic_filter == "Lab Etiquette":
        selected_context["laboratory_etiquette"] = campus_data.get("laboratory_etiquette", {})
    if topic_filter == "All" or topic_filter == "College Procedures":
        selected_context["general_college_procedures"] = campus_data.get("general_college_procedures", {})
    if topic_filter == "All" or topic_filter == "Campus Facilities":
        selected_context["campus_facilities"] = campus_data.get("campus_facilities", {})

    context_json = json.dumps(selected_context, indent=2)

    cache_k = _cache_key("CAMPUS_GUIDE", GEMMA_MODEL_ID, topic_filter, clean_q)
    cached = _get_cached_response(cache_k)
    if cached:
        return cached

    system_instruction = (
        "You are CampusMate AI's Campus Guide, powered by Google DeepMind's Gemma 4 (gemma-4-26b-a4b-it).\n"
        "Your purpose is to help college and engineering students navigate campus life, academic resources, clubs, and college procedures.\n"
        "CRITICAL RULES:\n"
        "1. Reference the provided sample campus reference data where helpful.\n"
        "2. Do NOT invent official college policies, specific semester deadlines, faculty phone numbers, or emergency numbers.\n"
        "3. You do NOT have access to live administrative records.\n"
        "4. Always advise students to confirm specific administrative procedures with their department office, faculty advisor, or Dean.\n"
        "5. Structure every response clearly into the following 4 sections:\n"
        "   - ### 📌 Direct Answer\n"
        "   - ### 🔍 Important Details & Regulations\n"
        "   - ### 💡 Recommended Next Steps\n"
        "   - ### ⚠️ Information Requiring Official Verification"
    )

    prompt = (
        f"--- SAMPLE CAMPUS REFERENCE DATA ---\n"
        f"{context_json}\n\n"
        f"--- STUDENT QUESTION ---\n"
        f"Category: {topic_filter}\n"
        f"Question: {clean_q}\n\n"
        f"Provide a structured, empathetic, and highly actionable response following the required format."
    )

    result = _call_gemma_single_request(prompt, system_instruction)
    _save_cached_response(cache_k, result)
    return result


# -------------------------------------------------------------
# MODE 2: STUDYMATE
# -------------------------------------------------------------
def run_study_mate(
    task_type: str,
    subject: str,
    timeline: str = "",
    hours_per_day: float = 2.0,
    weak_topics: str = "",
    instructions: str = ""
) -> str:
    """Generate study plans, concept explanations, or problem breakdowns in a single request."""
    clean_subj = subject.strip()
    if not clean_subj:
        raise CampusMateAPIError("Please provide a subject, topic, or question.")
    if len(clean_subj) > 1000:
        raise CampusMateAPIError("Subject/Question exceeds 1000 characters limit.")

    cache_k = _cache_key("STUDYMATE", GEMMA_MODEL_ID, task_type, clean_subj, timeline, hours_per_day, weak_topics, instructions)
    cached = _get_cached_response(cache_k)
    if cached:
        return cached

    system_instruction = (
        "You are CampusMate AI's StudyMate, powered by Google DeepMind's Gemma 4 (gemma-4-26b-a4b-it).\n"
        "You are an expert academic tutor and study architect for college students.\n"
        "CRITICAL RULES:\n"
        "- Deliver rigorous, realistic, high-value academic guidance tailored to engineering/college students.\n"
        "- Never hallucinate unsupported syllabus details; provide clear, standard curriculum structures if specifics are unstated.\n"
        "- Keep explanations direct, intuitive, and mathematically sound without unnecessary verbosity.\n\n"
        "FORMATTING REQUIREMENT BASED ON TASK:\n"
        "1. If Task is 'Create a study plan':\n"
        "   - ### 🎯 Preparation Overview (Timeline & Daily Commitment)\n"
        "   - ### 📅 Phased Study Roadmap (Daily/Weekly goals & specific topics)\n"
        "   - ### ⏱️ Recommended Daily Time Allocation (Theory, Problem Solving, Revision)\n"
        "   - ### 🛠️ Targeted Practice & Weak Areas Strategy\n"
        "   - ### 📝 Self-Assessment & Final Revision Checkpoints\n\n"
        "2. If Task is 'Explain a concept':\n"
        "   - ### 💡 Core Concept (Intuitive explanation in plain words)\n"
        "   - ### 🔬 Step-by-Step Breakdown (Mechanism, math/logic, or architecture)\n"
        "   - ### 💻 Practical Concrete Example\n"
        "   - ### ⚠️ Common Pitfalls & Exam Mistakes\n"
        "   - ### 📌 Quick Revision Summary\n\n"
        "3. If Task is 'Solve or explain an academic question':\n"
        "   - ### 🎯 Problem Analysis & Given Data\n"
        "   - ### 🧠 Conceptual Principle Applied\n"
        "   - ### 🔢 Step-by-Step Derivation / Solution\n"
        "   - ### 🔍 Key Verification & Edge Cases"
    )

    user_prompt = (
        f"Task Mode: {task_type}\n"
        f"Subject / Topic / Question: {clean_subj}\n"
        f"Preparation Timeline / Exam Date: {timeline or 'Standard semester revision period'}\n"
        f"Available Study Hours Per Day: {hours_per_day} hours/day\n"
        f"Weak Areas / Focus Areas: {weak_topics or 'Not specified (cover comprehensive fundamentals)'}\n"
        f"Additional Context / Question Details: {instructions or 'None'}\n\n"
        f"Generate the complete response now adhering strictly to the required format."
    )

    result = _call_gemma_single_request(user_prompt, system_instruction)
    _save_cached_response(cache_k, result)
    return result


# -------------------------------------------------------------
# MODE 3: CAMPUSFIX
# -------------------------------------------------------------
def run_campus_fix(
    issue_description: str,
    location: str = "",
    urgency: str = "Medium",
    additional_context: str = ""
) -> str:
    """Analyze a campus issue and produce a professional incident report draft in a single request."""
    clean_desc = issue_description.strip()
    if not clean_desc:
        raise CampusMateAPIError("Please describe the campus problem or facility issue.")
    if len(clean_desc) > 1000:
        raise CampusMateAPIError("Issue description exceeds 1000 characters limit.")

    cache_k = _cache_key("CAMPUS_FIX", GEMMA_MODEL_ID, clean_desc, location, urgency, additional_context)
    cached = _get_cached_response(cache_k)
    if cached:
        return cached

    system_instruction = (
        "You are CampusMate AI's CampusFix engine, powered by Google DeepMind's Gemma 4 (gemma-4-26b-a4b-it).\n"
        "Your role is to help students structure campus infrastructure, IT, or facility issues into clear, professional reports.\n"
        "CRITICAL BOUNDARIES:\n"
        "- Do NOT claim that a ticket has been created or submitted.\n"
        "- Do NOT claim technicians or faculty have been notified.\n"
        "- Do NOT invent official submission URLs, emails, or helpline numbers.\n"
        "- Clarify that this output is a DRAFT and set of recommendations for the student to submit through their institution's official channels.\n\n"
        "REQUIRED OUTPUT STRUCTURE:\n"
        "### 🏷️ Problem Categorization\n"
        "**Category:** [Specific category, e.g. Network Connectivity / Electrical / Lab Hardware]\n"
        "**Summary:** [1-sentence factual description]\n"
        "**Suggested Priority:** [Priority level with objective justification]\n\n"
        "### 📋 Recommended Student Actions\n"
        "[Actionable steps: evidence to gather, whom to approach on campus, temporary workarounds]\n\n"
        "### 📄 Formal Incident Report Draft\n"
        "*(Copy and submit this draft through your college's designated portal or department email)*\n"
        "```text\n"
        "To: [Campus Estate Office / IT Helpdesk / Laboratory In-Charge]\n"
        "Subject: [Formal Subject Line]\n\n"
        "[Concise, professional report body detailing issue, exact location, impact, and requested resolution]\n"
        "```\n\n"
        "### ⚠️ Verification Notice\n"
        "[Reminder that this is an AI-generated draft to be verified by the student before submission]"
    )

    user_prompt = (
        f"Issue Description: {clean_desc}\n"
        f"Campus Location: {location or 'Not specified by student'}\n"
        f"Student Stated Urgency: {urgency}\n"
        f"Additional Academic / Safety Context: {additional_context or 'None'}\n\n"
        f"Analyze the issue and generate the structured categorization, recommended actions, and copy-ready incident report draft."
    )

    result = _call_gemma_single_request(user_prompt, system_instruction)
    _save_cached_response(cache_k, result)
    return result
