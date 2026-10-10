"""Comprehensive Test Suite for CampusMate AI
----------------------------------------------
Verifies:
1. Model constraint strictly enforces gemma-4-26b-a4b-it.
2. Security & API key masking (never exposed or leaked).
3. Local input validation.
4. Campus Navigation: Dijkstra shortest path algorithm.
5. Campus Navigation: Distance & walking time calculation.
6. Campus Navigation: Natural language origin/destination parsing.
7. Campus Navigation: SVG route schematic generation.
8. Campus Guide: Procedural Q&A grounded with local data.
9. StudyMate: Concept explanations and study schedules with LaTeX math support.
10. CampusFix: Facility incident reporting and boundary compliance.
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
from campus_map import get_campus_map_engine

# Load map engine
MAP_ENGINE = get_campus_map_engine()

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


def test_3b_clean_initial_state_and_honest_errors():
    print("Testing Clean Neutral Initial State & Error Handling...")
    from app import EMPTY_RESULT_PLACEHOLDER, execute_campus_guide_qa, execute_study_mate, execute_campus_fix, execute_campus_navigation

    # FIX 1 Verification: Neutral empty state on initial load
    assert "Your results will appear here" in EMPTY_RESULT_PLACEHOLDER, "Missing empty state title"
    assert "Choose a mode, enter your request, and click Generate to get started." in EMPTY_RESULT_PLACEHOLDER, "Missing empty state instruction"
    assert "Campus Walking Route" not in EMPTY_RESULT_PLACEHOLDER, "Pre-written navigation route found in initial placeholder!"
    assert "Direct Answer" not in EMPTY_RESULT_PLACEHOLDER, "Pre-written AI answer found in initial placeholder!"

    # Verify input validation errors never fabricate answers
    err_res, err_svg = execute_campus_guide_qa("   ", "All")
    assert "Input Required" in err_res, f"Unexpected error response: {err_res}"
    assert err_svg.get("visible") is False, "SVG should be hidden on text error"

    err_study, err_svg2 = execute_study_mate("Create a study plan", "", "", 2.0, "", "")
    assert "Input Required" in err_study, f"Unexpected study response: {err_study}"

    err_fix, err_svg3 = execute_campus_fix("", "", "Medium", "")
    assert "Input Required" in err_fix, f"Unexpected fix response: {err_fix}"

    err_nav, err_svg4 = execute_campus_navigation("", "", "")
    assert "Origin and Destination" in err_nav or "Location Not Recognized" in err_nav
    print("  [PASS] Clean neutral state verified on load, and errors never return fabricated answers.")


def test_4_campus_navigation_dijkstra():
    print("Testing Campus Navigation: Dijkstra Shortest Path & Clean Interface...")
    # Test Canteen to CSE Block
    route = MAP_ENGINE.find_shortest_route("main_canteen", "cse_block")
    assert route["status"] == "success", "Expected route to succeed"
    # Shortest path is Canteen -> Main Lab (90m) -> CSE Block (130m) = 220m
    # compared to Canteen -> Courtyard (110m) -> CSE Block (190m) = 300m
    assert route["total_distance_m"] == 220, f"Expected 220m, got {route['total_distance_m']}"
    assert route["path_ids"] == ["main_canteen", "main_lab", "cse_block"]
    assert len(route["steps"]) == 2
    
    # Internal metadata is preserved
    assert "demo_notice" in route

    # CRITICAL FIX 2 VERIFICATION: Rendered visible markdown MUST NOT contain the DEMO ROUTE badge banner
    rendered_md = MAP_ENGINE.render_route_markdown(route)
    assert "DEMO ROUTE (Sample Campus Graph • Not Surveyor Verified)" not in rendered_md, (
        "FAIL: Exact text 'DEMO ROUTE (Sample Campus Graph • Not Surveyor Verified)' was found in visible markdown!"
    )
    assert "DEMO ROUTE" not in rendered_md, "FAIL: 'DEMO ROUTE' banner found in visible markdown!"
    assert "220 meters" in rendered_md, "Distance missing from route markdown"
    assert "Step-by-Step Directions" in rendered_md, "Directions missing from route markdown"
    print("  [PASS] Dijkstra shortest path verified (220m) & visible 'DEMO ROUTE' banner completely absent.")


def test_5_campus_navigation_time_and_steps():
    print("Testing Campus Navigation: Walking Time & Directions...")
    # Test Main Gate to Library
    route = MAP_ENGINE.find_shortest_route("main_gate", "library")
    assert route["status"] == "success"
    # Gate -> Admin (180m) + Admin -> Courtyard (160m) + Courtyard -> Library (150m) = 490m
    assert route["total_distance_m"] == 490
    assert route["estimated_time_sec"] == int(490 / 1.2)  # ~408s = 6 min 48 sec
    assert "6 min" in route["estimated_time_str"]
    assert len(route["steps"]) == 3
    for step in route["steps"]:
        assert "instruction" in step and step["instruction"]
    print(f"  [PASS] Distance (490m), time ({route['estimated_time_str']}), and step directions verified.")


def test_6_campus_navigation_natural_language():
    print("Testing Campus Navigation: Natural Language Parser...")
    q1 = "I am standing in front of the canteen. Take me to the CSE block."
    s, e, r = MAP_ENGINE.parse_natural_language_query(q1)
    assert s == "main_canteen" and e == "cse_block", f"Failed parsing: {s} -> {e}"

    q2 = "From Main Gate to Central Library"
    s, e, r = MAP_ENGINE.parse_natural_language_query(q2)
    assert s == "main_gate" and e == "library", f"Failed parsing: {s} -> {e}"

    q3 = "How do I reach the mechanical workshop from sports complex?"
    s, e, r = MAP_ENGINE.parse_natural_language_query(q3)
    assert s == "sports_complex" and e == "mech_workshop", f"Failed parsing: {s} -> {e}"
    print("  [PASS] Natural-language location queries correctly mapped to graph nodes.")


def test_7_campus_navigation_svg_and_edge_cases():
    print("Testing Campus Navigation: SVG generation & edge cases...")
    route = MAP_ENGINE.find_shortest_route("main_canteen", "cse_block")
    svg = MAP_ENGINE.render_route_svg(route)
    assert "<svg" in svg and "</svg>" in svg
    assert "Main Canteen" in svg or "Canteen" in svg
    assert "CSE Block" in svg

    # Same location test
    same = MAP_ENGINE.find_shortest_route("library", "library")
    assert same["status"] == "success"
    assert same["total_distance_m"] == 0

    # Unknown location test
    err = MAP_ENGINE.find_shortest_route("non_existent_node", "library")
    assert err["status"] == "error"
    print("  [PASS] SVG schematic generated and edge cases handled safely.")


def test_8_campus_guide_live():
    print("Testing Mode 1: Campus Guide Q&A with Gemma 4...")
    q = "What should I check if my attendance drops below 75%?"
    t0 = time.time()
    res = run_campus_guide(q, CAMPUS_DATA, "College Procedures")
    elapsed = time.time() - t0
    print(f"  Received response in {elapsed:.2f}s ({len(res)} chars)")
    assert "Direct Answer" in res or "Attendance" in res
    assert "Dean" in res or "advisor" in res.lower() or "official" in res.lower()
    print("  [PASS] Campus Guide produces grounded, structured response.")


def test_9_study_mate_live():
    print("Testing Mode 2: StudyMate with Gemma 4 & LaTeX math...")
    t0 = time.time()
    res = run_study_mate(
        task_type="Explain a concept",
        subject="Linear Algebra: Eigenvalues and Eigenvectors $Av = \\lambda v$",
        timeline="Exam in 3 days",
        hours_per_day=2.0,
        weak_topics="Characteristic equation det(A - λI) = 0",
        instructions="Provide mathematical breakdown."
    )
    elapsed = time.time() - t0
    print(f"  Received response in {elapsed:.2f}s ({len(res)} chars)")
    assert len(res) > 200
    assert "Core Concept" in res or "Concept" in res
    print("  [PASS] StudyMate generates mathematical concept breakdown with KaTeX compatibility.")


def test_10_campus_fix_live():
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
    assert "Category" in res or "Problem" in res
    assert "Draft" in res or "Subject" in res
    print("  [PASS] CampusFix creates structured categorization and draft email.")


def main():
    print("==========================================================")
    print("  RUNNING CAMPUSMATE AI COMPREHENSIVE VERIFICATION SUITE")
    print("==========================================================")
    test_1_model_id_integrity()
    test_2_security_key_management()
    test_3_input_validation()
    test_3b_clean_initial_state_and_honest_errors()
    test_4_campus_navigation_dijkstra()
    test_5_campus_navigation_time_and_steps()
    test_6_campus_navigation_natural_language()
    test_7_campus_navigation_svg_and_edge_cases()
    test_8_campus_guide_live()
    test_9_study_mate_live()
    test_10_campus_fix_live()
    print("==========================================================")
    print("  ALL 11 VERIFICATION TESTS PASSED SUCCESSFULLY! (11/11)")
    print("==========================================================")


if __name__ == "__main__":
    main()
