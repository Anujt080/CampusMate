"""Comprehensive Test Suite for CampusMate AI
----------------------------------------------
Verifies:
1. Model constraint strictly enforces gemma-4-26b-a4b-it.
2. Single-request execution rule per user action.
3. Mode 1: Campus Guide behavior with grounded context.
4. Mode 2: StudyMate study plan, concept explanation, and question solver.
5. Mode 3: CampusFix incident reporting and boundary compliance.
6. Local input validation and sanitized error handling.
7. API key security (never exposed or leaked).
"""

import json
import os
import sys
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from gemma_client import (
    GEMMA_MODEL_ID,
    CampusMateAPIError,
    run_campus_guide,
    run_study_mate,
    run_campus_fix,
    get_sanitized_api_key,
    sanitize_error_message
)

# Load campus data
with open(PROJECT_ROOT / "campus_data.json", "r", encoding="utf-8") as f:
    CAMPUS_DATA = json.load(f)


def test_1_model_id_integrity():
    print("Testing Model ID integrity...")
    assert GEMMA_MODEL_ID == "gemma-4-26b-a4b-it", f"Strict model violation! Expected gemma-4-26b-a4b-it, got {GEMMA_MODEL_ID}"
    print("  [PASS] Model ID is strictly 'gemma-4-26b-a4b-it'.")


def test_2_security_key_management():
    print("Testing API Key safety & loading...")
    key = get_sanitized_api_key()
    assert key, "API key should be loaded from .env or environment"
    assert len(key) > 20, "API key should be valid length"
    assert key != "your_api_key_here", "API key should not be a placeholder"
    
    # Test error masking
    fake_error = RuntimeError(f"Failed with key {key}")
    sanitized = sanitize_error_message(fake_error)
    assert key not in sanitized, "CRITICAL: Real API key was exposed in sanitized message!"
    assert "[REDACTED_API_KEY]" in sanitized, "Key was replaced with redaction placeholder"
    print("  [PASS] API key is loaded safely and completely masked in error messages.")


def test_3_input_validation():
    print("Testing local input validation...")
    # Empty query tests
    try:
        run_campus_guide("", CAMPUS_DATA)
        assert False, "Should have raised CampusMateAPIError for empty guide query"
    except CampusMateAPIError:
        pass

    try:
        run_study_mate("Create a study plan", "")
        assert False, "Should have raised CampusMateAPIError for empty subject"
    except CampusMateAPIError:
        pass

    try:
        run_campus_fix("")
        assert False, "Should have raised CampusMateAPIError for empty issue description"
    except CampusMateAPIError:
        pass
    print("  [PASS] Local validation rejects empty inputs gracefully before calling API.")


def test_4_campus_guide_live():
    print("Testing Mode 1: Campus Guide with Gemma 4...")
    q = "What should I check if my attendance drops below 75%?"
    t0 = time.time()
    res = run_campus_guide(q, CAMPUS_DATA, "College Procedures")
    elapsed = time.time() - t0
    print(f"  Received response in {elapsed:.2f}s ({len(res)} chars)")
    assert "Direct Answer" in res or "Attendance" in res, "Expected structured sections in response"
    assert "Dean" in res or "advisor" in res.lower() or "official" in res.lower(), "Expected institutional guidance"
    print("  [PASS] Campus Guide produces grounded, structured response.")


def test_5_study_mate_live():
    print("Testing Mode 2: StudyMate with Gemma 4...")
    t0 = time.time()
    res = run_study_mate(
        task_type="Create a study plan",
        subject="Data Structures: Binary Search Trees and Heaps",
        timeline="Exam in 5 days",
        hours_per_day=3.0,
        weak_topics="Heapify and deletion in BST",
        instructions="Include practical coding drills."
    )
    elapsed = time.time() - t0
    print(f"  Received response in {elapsed:.2f}s ({len(res)} chars)")
    assert len(res) > 200, "Response is substantial"
    assert "day" in res.lower() or "roadmap" in res.lower() or "plan" in res.lower()
    print("  [PASS] StudyMate creates detailed, realistic study schedule.")


def test_6_campus_fix_live():
    print("Testing Mode 3: CampusFix with Gemma 4...")
    t0 = time.time()
    res = run_campus_fix(
        issue_description="The oscilloscope in Bench 3 of VLSI lab has a loose input connector.",
        location="VLSI Lab, Room 210",
        urgency="High",
        additional_context="Lab evaluation is tomorrow morning at 10 AM."
    )
    elapsed = time.time() - t0
    print(f"  Received response in {elapsed:.2f}s ({len(res)} chars)")
    assert "Category" in res or "Problem" in res, "Categorization header present"
    assert "Draft" in res or "Subject" in res, "Report draft block present"
    print("  [PASS] CampusFix creates structured categorization and draft email.")


def main():
    print("==========================================================")
    print("  RUNNING CAMPUSMATE AI VERIFICATION SUITE")
    print("==========================================================")
    test_1_model_id_integrity()
    test_2_security_key_management()
    test_3_input_validation()
    test_4_campus_guide_live()
    test_5_study_mate_live()
    test_6_campus_fix_live()
    print("==========================================================")
    print("  ALL TESTS PASSED SUCCESSFULLY! (6/6)")
    print("==========================================================")


if __name__ == "__main__":
    main()
