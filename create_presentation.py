"""Script to generate the hackathon presentation for CampusMate AI."""

import os
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    # 16:9 Widescreen layout
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Theme Colors
    COLOR_BG = RGBColor(248, 250, 252)        # Slate 50
    COLOR_CARD = RGBColor(255, 255, 255)      # White
    COLOR_PRIMARY = RGBColor(37, 99, 235)     # Blue 600
    COLOR_DARK = RGBColor(15, 23, 42)         # Slate 900
    COLOR_MUTED = RGBColor(71, 85, 105)       # Slate 600
    COLOR_ACCENT = RGBColor(239, 246, 255)    # Blue 50
    COLOR_BORDER = RGBColor(226, 232, 240)    # Slate 200

    def add_blank_slide():
        blank_slide_layout = prs.slide_layouts[6]
        slide = prs.slides.add_slide(blank_slide_layout)
        # Background fill
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = COLOR_BG
        bg.line.fill.background()
        return slide

    def add_header(slide, title_text, category_badge="CAMPUSMATE AI • HACKATHON PITCH"):
        # Category Badge
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.5), Inches(0.4))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_badge.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = COLOR_PRIMARY

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.9), Inches(11.5), Inches(0.8))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(28)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_DARK

    # ==========================================
    # SLIDE 1: TITLE & TAGLINE
    # ==========================================
    s1 = add_blank_slide()
    # Centered Title Box
    title_box = s1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.333), Inches(3.8))
    tf1 = title_box.text_frame
    tf1.word_wrap = True

    p_badge = tf1.paragraphs[0]
    p_badge.text = "IIT HACKATHON: BUILD FOR YOUR CAMPUS"
    p_badge.font.size = Pt(14)
    p_badge.font.bold = True
    p_badge.font.color.rgb = COLOR_PRIMARY

    p_title = tf1.add_paragraph()
    p_title.text = "CampusMate AI"
    p_title.font.size = Pt(54)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_DARK
    p_title.space_before = Pt(14)

    p_tag = tf1.add_paragraph()
    p_tag.text = '"Your campus. Your academics. Your AI companion."'
    p_tag.font.size = Pt(22)
    p_tag.font.color.rgb = COLOR_PRIMARY
    p_tag.space_before = Pt(10)

    p_desc = tf1.add_paragraph()
    p_desc.text = (
        "A lightweight, privacy-first AI campus companion that helps students navigate campus information, "
        "master complex academic concepts, plan study schedules, and draft actionable facility incident reports.\n"
        "Powered strictly by Google DeepMind's Gemma 4 (gemma-4-26b-a4b-it)."
    )
    p_desc.font.size = Pt(14)
    p_desc.font.color.rgb = COLOR_MUTED
    p_desc.space_before = Pt(18)

    # Model Badge card at bottom
    badge_shape = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(5.8), Inches(11.333), Inches(0.8))
    badge_shape.fill.solid()
    badge_shape.fill.fore_color.rgb = COLOR_ACCENT
    badge_shape.line.color.rgb = COLOR_BORDER
    tf_b = badge_shape.text_frame
    tf_b.word_wrap = True
    p_b = tf_b.paragraphs[0]
    p_b.text = "⚡ Built with Google DeepMind's Gemma 4 (gemma-4-26b-a4b-it) • Single-Request Architecture • Zero Database"
    p_b.font.size = Pt(13)
    p_b.font.bold = True
    p_b.font.color.rgb = COLOR_PRIMARY
    p_b.alignment = PP_ALIGN.CENTER

    # ==========================================
    # SLIDE 2: THE PROBLEM
    # ==========================================
    s2 = add_blank_slide()
    add_header(s2, "The Real-World Campus Challenges We Solve")

    problems = [
        (
            "1. Information Fragmentation",
            "Campus guidelines, attendance policies, lab rules, and club orientations are scattered across circulars, notice boards, and seniors' hearsay. First-years struggle to navigate essential procedures."
        ),
        (
            "2. Academic Overwhelm & Cramming",
            "Students frequently face dense syllabi right before exams. Existing chatbots give unrealistic 14-hour study schedules or shallow explanations without concrete engineering examples."
        ),
        (
            "3. Silent Campus Breakdowns",
            "Wi-Fi outages in computer labs, broken oscilloscopes, and malfunctioning projectors often go unreported because students find official ticketing tedious or do not know how to structure an actionable report."
        )
    ]

    for i, (title, text) in enumerate(problems):
        card = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + i * 3.9), Inches(2.0), Inches(3.7), Inches(4.5))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD
        card.line.color.rgb = COLOR_BORDER
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.3)
        tf.margin_right = Inches(0.3)
        tf.margin_top = Inches(0.4)

        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.size = Pt(18)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_DARK

        p2 = tf.add_paragraph()
        p2.text = text
        p2.font.size = Pt(13)
        p2.font.color.rgb = COLOR_MUTED
        p2.space_before = Pt(14)

    # ==========================================
    # SLIDE 3: THE SOLUTION - THREE MODES
    # ==========================================
    s3 = add_blank_slide()
    add_header(s3, "CampusMate AI: Three Purpose-Built Student Modes")

    solutions = [
        (
            "🏫 Campus Guide",
            "Campus Navigation & Policy Q&A",
            "Two distinct, high-impact features in one mode:\n\n"
            "• Local Dijkstra Navigation: Finds shortest walking paths, distance in meters, and walking time (0 API calls).\n"
            "• Interactive SVG Schematics: Renders visual step-by-step landmark maps.\n"
            "• Gemma 4 Procedural Q&A: Ingests local campus_data.json with official Dean verification warnings."
        ),
        (
            "📚 StudyMate",
            "Academic Engine with LaTeX Math",
            "Builds realistic study roadmaps and clarifies complex engineering concepts.\n\n"
            "• Time-Aware: Balances theory, practice, and revision according to daily hours.\n"
            "• KaTeX Math Rendering: Cleanly displays equations like $Av = \\lambda v$ without raw string glitches.\n"
            "• Concrete code examples & common exam pitfalls."
        ),
        (
            "🛠️ CampusFix",
            "Actionable Incident Reporting",
            "Turns casual student frustration into professional incident report drafts.\n\n"
            "• Classifies technical category and urgency.\n"
            "• Evaluates academic and safety impact.\n"
            "• Produces copy-ready professional emails for estate/IT/lab coordinators."
        )
    ]

    for i, (title, subtitle, text) in enumerate(solutions):
        card = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + i * 3.9), Inches(2.0), Inches(3.7), Inches(4.7))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD
        card.line.color.rgb = COLOR_BORDER
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.3)
        tf.margin_right = Inches(0.3)
        tf.margin_top = Inches(0.3)

        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.size = Pt(19)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_PRIMARY

        p_sub = tf.add_paragraph()
        p_sub.text = subtitle
        p_sub.font.size = Pt(13)
        p_sub.font.bold = True
        p_sub.font.color.rgb = COLOR_DARK
        p_sub.space_before = Pt(4)

        p2 = tf.add_paragraph()
        p2.text = text
        p2.font.size = Pt(12)
        p2.font.color.rgb = COLOR_MUTED
        p2.space_before = Pt(12)

    # ==========================================
    # SLIDE 4: TECHNOLOGY ARCHITECTURE
    # ==========================================
    s4 = add_blank_slide()
    add_header(s4, "Lightweight, Reliable Architecture Powered by Gemma 4")

    tech_points = [
        ("AI Core: Gemma 4", "Strictly uses gemma-4-26b-a4b-it via the Google GenAI SDK (from google import genai). Fast, cost-efficient, state-of-the-art open-weights model."),
        ("Deterministic Campus Navigation", "Local Dijkstra algorithm over campus_map.json calculates optimal walking distance and time in <1ms with zero API requests."),
        ("Strict Single-Request Rule", "Every AI user action makes exactly ONE model API call. No chained agent loops, no hidden retries, zero background token burn."),
        ("Instant Theme Switcher & Math", "Persistent Light/Dark mode with local storage; full KaTeX mathematical rendering for equations ($Av = \\lambda v$)."),
        ("Resilient Error Handling & Zero DB", "Sanitizes and masks all API keys with [REDACTED_API_KEY]. Runs 100% locally on a student laptop with no database or login.")
    ]

    for i, (title, text) in enumerate(tech_points):
        y_pos = 1.9 + i * 1.0
        card = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(y_pos), Inches(11.733), Inches(0.85))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD
        card.line.color.rgb = COLOR_BORDER
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.3)
        tf.margin_top = Inches(0.12)

        p1 = tf.paragraphs[0]
        p1.text = title + ": "
        p1.font.size = Pt(14)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_PRIMARY

        p1_run = p1.add_run()
        p1_run.text = text
        p1_run.font.bold = False
        p1_run.font.color.rgb = COLOR_MUTED

    # ==========================================
    # SLIDE 5: LIVE DEMO SCENARIOS
    # ==========================================
    s5 = add_blank_slide()
    add_header(s5, "Live Demonstration: Three Realistic Campus Scenarios")

    demos = [
        (
            "Demo 1: Campus Navigation & Q&A",
            "Scenario: Student at Canteen needing directions to CSE Block.\n\n"
            "Input: Canteen ➔ CSE Block (or natural language request).\n\n"
            "Result: Dijkstra engine outputs 220m shortest route, 3 min walk time, numbered landmark steps, and SVG route schematic in 0ms without consuming API quota!"
        ),
        (
            "Demo 2: StudyMate with LaTeX",
            "Scenario: Student preparing for Linear Algebra & Algorithms.\n\n"
            "Input: Eigenvalues $Av = \\lambda v$, 2 hours/day, exam in 3 days.\n\n"
            "Result: Produces structured derivation with properly formatted mathematical formulas via KaTeX and time-balanced study checkpoints."
        ),
        (
            "Demo 3: CampusFix Incident Draft",
            "Scenario: Wi-Fi outage during a laboratory practical.\n\n"
            "Input: 'Wi-Fi keeps disconnecting in Block C Lab 302 before online exam.'\n\n"
            "Result: Classifies as Time-Sensitive Network Incident, outlines immediate verification steps, and creates a copy-ready formal email for the IT coordinator."
        )
    ]

    for i, (title, text) in enumerate(demos):
        card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + i * 3.9), Inches(2.0), Inches(3.7), Inches(4.7))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD
        card.line.color.rgb = COLOR_BORDER
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.3)
        tf.margin_right = Inches(0.3)
        tf.margin_top = Inches(0.3)

        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.size = Pt(17)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_DARK

        p2 = tf.add_paragraph()
        p2.text = text
        p2.font.size = Pt(12)
        p2.font.color.rgb = COLOR_MUTED
        p2.space_before = Pt(12)

    # ==========================================
    # SLIDE 6: REAL IMPACT, LIMITATIONS & ROADMAP
    # ==========================================
    s6 = add_blank_slide()
    add_header(s6, "Campus Impact, Honest Limitations & Future Scope")

    sections = [
        (
            "🎯 Real-World Campus Impact",
            "• Alleviates administrative friction for students and faculty.\n"
            "• Prevents exam burnout with realistic, time-aware study plans.\n"
            "• Accelerates facility repairs by converting vague complaints into precise, actionable technical reports.\n"
            "• 100% runnable locally on standard student hardware."
        ),
        (
            "⚠️ Honest Boundaries & Limitations",
            "• Sample campus data is illustrative and not live college ERP data.\n"
            "• Incident reports are drafts; they do not automatically submit tickets to campus portals.\n"
            "• Administrative policies must always be verified with college authorities."
        ),
        (
            "🚀 Future Scope (Post-Hackathon)",
            "• Offline on-device Gemma 4 inference using Ollama / local GGUF.\n"
            "• Native timetable & syllabus PDF ingestion via multimodality.\n"
            "• Optional webhook integration into university ticketing systems (e.g. Jira / Freshdesk)."
        )
    ]

    for i, (title, text) in enumerate(sections):
        card = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + i * 3.9), Inches(2.0), Inches(3.7), Inches(4.7))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD
        card.line.color.rgb = COLOR_BORDER
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.3)
        tf.margin_right = Inches(0.3)
        tf.margin_top = Inches(0.3)

        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.size = Pt(17)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_PRIMARY if i != 1 else RGBColor(220, 38, 38)

        p2 = tf.add_paragraph()
        p2.text = text
        p2.font.size = Pt(12)
        p2.font.color.rgb = COLOR_MUTED
        p2.space_before = Pt(12)

    # Save presentation
    out_dir = Path(__file__).resolve().parent / "presentation"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "CampusMate-AI.pptx"
    prs.save(str(out_file))
    print(f"Presentation successfully created at: {out_file}")

if __name__ == "__main__":
    create_deck()
