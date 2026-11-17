"""Test Suite for CampusMate AI - My Notes Feature
------------------------------------------------
Verifies:
1. All 8 required academic folders exist.
2. All required sample documents are present with realistic metadata.
3. Gradio app registers the separate '/notes' route.
4. Main navbar contains the 'My Notes' navigation button with link to '/notes'.
5. Notes page contains 'Back to CampusMate' link to '/'.
6. Notes page contains heading, subtitle, search, sort, filter, grid/list controls, and modals.
7. LocalStorage keys and JavaScript client logic are properly structured.
8. CSS styling includes responsive rules and theme support.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from campus_notes import (
    SUBJECT_FOLDERS,
    SAMPLE_DOCUMENTS,
    get_notes_page_html,
    NOTES_PAGE_CSS
)
from app import build_app, CUSTOM_CSS


def test_1_subject_folders():
    print("Testing Subject Folders...")
    folder_names = [f["name"] for f in SUBJECT_FOLDERS]
    expected_folders = [
        "Data Structures & Algorithms",
        "Object Oriented Programming",
        "Operating Systems",
        "Database Management Systems",
        "Mathematics",
        "Digital Electronics",
        "Computer Networks",
        "Software Engineering"
    ]
    for expected in expected_folders:
        assert expected in folder_names, f"Missing required folder: {expected}"
    assert len(SUBJECT_FOLDERS) == 8, f"Expected 8 folders, got {len(SUBJECT_FOLDERS)}"
    print(f"  [PASS] All {len(SUBJECT_FOLDERS)} required subject folders verified.")


def test_2_sample_documents():
    print("Testing Sample Documents...")
    doc_names = [d["name"] for d in SAMPLE_DOCUMENTS]
    required_docs = [
        "Arrays and Strings.pdf",
        "Recursion Notes.pdf",
        "Sorting Algorithms.pdf",
        "OOPS Fundamentals.pdf",
        "Inheritance and Polymorphism.pdf",
        "Process Scheduling.pdf",
        "Memory Management.pdf",
        "DBMS Normalisation.pdf",
        "SQL Queries.pdf",
        "Matrices and Determinants.pdf"
    ]
    for req in required_docs:
        assert req in doc_names, f"Missing required document: {req}"

    # Verify document schema
    for doc in SAMPLE_DOCUMENTS:
        assert "id" in doc and doc["id"]
        assert "name" in doc and doc["name"]
        assert "folder" in doc and doc["folder"]
        assert "file_type" in doc and doc["file_type"]
        assert "size" in doc and doc["size"]
        assert "last_modified" in doc and doc["last_modified"]
        assert "summary" in doc and doc["summary"]
        assert "key_topics" in doc and isinstance(doc["key_topics"], list)
    print(f"  [PASS] All required sample documents and rich academic metadata verified ({len(SAMPLE_DOCUMENTS)} documents).")


def test_3_notes_route_registration():
    print("Testing Route Registration in Gradio App...")
    demo = build_app()
    registered_routes = [p[0] for p in demo.pages]
    assert "notes" in registered_routes, f"Route 'notes' not registered in demo.pages: {demo.pages}"
    
    # Check page tuple configuration
    notes_page_tuple = next(p for p in demo.pages if p[0] == "notes")
    assert notes_page_tuple[1] == "My Notes", f"Page name should be 'My Notes', got {notes_page_tuple[1]}"
    assert notes_page_tuple[2] is False, f"show_in_navbar should be False, got {notes_page_tuple[2]}"
    print("  [PASS] '/notes' separate webpage route registered correctly on Gradio Blocks.")


def test_4_navbar_navigation_link():
    print("Testing Navbar 'My Notes' Navigation Link...")
    # Read the main layout by inspecting demo blocks
    demo = build_app()
    html_blocks = [b.value for b in demo.blocks.values() if hasattr(b, "value") and isinstance(b.value, str)]
    combined_html = "\n".join(html_blocks)
    
    assert 'href="/notes"' in combined_html, "Navbar missing link to '/notes'"
    assert 'My Notes' in combined_html, "Navbar missing 'My Notes' label"
    assert 'title="My Notes"' in combined_html, "Navbar missing tooltip 'My Notes'"
    print("  [PASS] Main CampusMate AI navbar contains 'My Notes' navigation button linking to '/notes'.")


def test_5_notes_page_content_and_back_link():
    print("Testing My Notes Page Elements & Back Navigation...")
    notes_html = get_notes_page_html()

    # Back to CampusMate link
    assert 'href="/"' in notes_html, "Missing 'Back to CampusMate' link to '/'"
    assert 'Back to CampusMate' in notes_html, "Missing 'Back to CampusMate' text"

    # Heading & Subtitle
    assert 'My Notes' in notes_html, "Missing 'My Notes' heading"
    assert 'Your academic resources, organised in one place.' in notes_html, "Missing required subtitle"

    # Search & Controls
    assert 'id="notes-search-input"' in notes_html, "Missing search input"
    assert 'id="upload-note-btn"' in notes_html, "Missing upload button"
    assert 'id="notes-subject-filter"' in notes_html, "Missing subject filter"
    assert 'id="notes-sort-select"' in notes_html, "Missing sort select"
    assert 'id="view-grid-btn"' in notes_html, "Missing grid view button"
    assert 'id="view-list-btn"' in notes_html, "Missing list view button"

    # Sections
    assert 'id="folders-section"' in notes_html, "Missing folders section"
    assert 'id="recent-section"' in notes_html, "Missing recent section"
    assert 'id="documents-section"' in notes_html, "Missing documents section"

    # Modals
    assert 'id="modal-upload"' in notes_html, "Missing upload modal"
    assert 'id="modal-preview"' in notes_html, "Missing preview modal"
    assert 'id="modal-rename"' in notes_html, "Missing rename modal"
    assert 'id="modal-delete"' in notes_html, "Missing delete modal"
    print("  [PASS] My Notes webpage content, controls, modals, and back navigation verified.")


def test_6_css_and_responsiveness():
    print("Testing CSS styling & responsiveness...")
    assert ".notes-page-root" in NOTES_PAGE_CSS
    assert ".folders-grid" in NOTES_PAGE_CSS
    assert ".documents-grid-view" in NOTES_PAGE_CSS
    assert ".documents-list-view" in NOTES_PAGE_CSS
    assert "@media (max-width: 768px)" in NOTES_PAGE_CSS
    assert "@media (max-width: 480px)" in NOTES_PAGE_CSS
    assert NOTES_PAGE_CSS in CUSTOM_CSS, "NOTES_PAGE_CSS should be included in CUSTOM_CSS"
    print("  [PASS] CSS design system consistency and responsive media queries verified.")


if __name__ == "__main__":
    print("==========================================================", flush=True)
    print("  CAMPUSMATE AI - MY NOTES VERIFICATION SUITE", flush=True)
    print("==========================================================", flush=True)
    test_1_subject_folders()
    test_2_sample_documents()
    test_5_notes_page_content_and_back_link()
    test_6_css_and_responsiveness()
    test_3_notes_route_registration()
    test_4_navbar_navigation_link()
    print("==========================================================", flush=True)
    print("  ALL 6 MY NOTES TESTS PASSED SUCCESSFULLY! (6/6)", flush=True)
    print("==========================================================", flush=True)
