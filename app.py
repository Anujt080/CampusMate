"""CampusMate AI - Main Application
----------------------------------
A lightweight, student-focused campus companion built for the IIT Hackathon
("Build for Your Campus").

Key Architecture & Hackathon Constraints:
- AI Model: gemma-4-26b-a4b-it (Google DeepMind via google-genai)
- Strict Single-Request Rule: Exactly one model request per intentional user action
- Single-Screen Dashboard: All three modes accessible on one unified view
- Zero Database: Fast local JSON knowledge base for campus procedures
- Zero Authentication: Lightweight and privacy-first local student tool
- Robust Error Handling & API Key Safety
"""

import json
import os
import sys
import time
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(errors="replace")

# Add project directory to sys.path
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

# Load local campus data
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
# Custom CSS for Modern, Premium, Clean Academic UI
# -------------------------------------------------------------------
CUSTOM_CSS = """
:root {
    --primary-color: #2563eb;
    --primary-hover: #1d4ed8;
    --navy-text: #0f172a;
    --slate-muted: #475569;
    --surface-bg: #ffffff;
    --page-bg: #f8fafc;
    --border-color: #e2e8f0;
}

/* Force consistent clean light academic styling */
.gradio-container {
    background-color: #f8fafc !important;
    color: #0f172a !important;
}

.gradio-container * {
    color-scheme: light !important;
}

/* Header Container */
.header-box {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 14px;
    padding: 24px 28px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04);
}

.title-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
}

.brand-title {
    font-size: 28px;
    font-weight: 800;
    color: #0f172a !important;
    letter-spacing: -0.5px;
    margin: 0;
}

.brand-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background-color: #eff6ff !important;
    color: #1d4ed8 !important;
    border: 1px solid #bfdbfe !important;
    padding: 6px 14px;
    border-radius: 9999px;
    font-size: 13px;
    font-weight: 600;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.tagline-text {
    font-size: 15px;
    font-weight: 600;
    color: #2563eb !important;
    margin-top: 4px;
    margin-bottom: 6px;
}

.desc-text {
    font-size: 14px;
    color: #334155 !important;
    line-height: 1.5;
    margin: 0;
    max-width: 900px;
}

/* Groups and Panels */
.gr-group, fieldset {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
}

/* Primary Action Button */
.primary-gen-btn {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
    color: white !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    padding: 12px 24px !important;
    border-radius: 10px !important;
    border: none !important;
    box-shadow: 0 4px 10px rgba(37, 99, 235, 0.25) !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
    margin-top: 14px !important;
}

.primary-gen-btn:hover {
    background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%) !important;
    box-shadow: 0 6px 14px rgba(37, 99, 235, 0.35) !important;
    transform: translateY(-1px);
}

/* Result Card */
.output-card {
    background: #ffffff !important;
    color: #0f172a !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 12px !important;
    padding: 24px !important;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.04);
    min-height: 480px;
}

.output-card * {
    color: #0f172a !important;
}

.output-card h1, .output-card h2, .output-card h3, .output-card h4 {
    color: #1e40af !important;
    margin-top: 16px;
    margin-bottom: 8px;
    font-weight: 700;
}

.output-card code {
    background: #f1f5f9 !important;
    color: #0f172a !important;
    padding: 2px 6px;
    border-radius: 4px;
}

.output-card pre {
    background: #0f172a !important;
    padding: 14px;
    border-radius: 8px;
    overflow-x: auto;
}

.output-card pre code, .output-card pre * {
    background: transparent !important;
    color: #f8fafc !important;
}

.info-note {
    font-size: 12.5px;
    color: #475569 !important;
    padding: 10px 14px;
    background-color: #f8fafc !important;
    border-left: 3px solid #3b82f6 !important;
    border-radius: 4px;
    margin-top: 12px;
}

/* Footer Meta */
.footer-text {
    text-align: center;
    font-size: 12px;
    color: #94a3b8;
    margin-top: 24px;
    padding-top: 12px;
    border-top: 1px solid #e2e8f0;
}
"""

# -------------------------------------------------------------------
# Core Dispatcher Logic (Strict Single Model Request Rule)
# -------------------------------------------------------------------
def dispatch_generate(
    current_mode: str,
    # Mode 1 inputs
    guide_q: str,
    guide_filter: str,
    # Mode 2 inputs
    study_task: str,
    study_subj: str,
    study_timeline: str,
    study_hours: float,
    study_weak: str,
    study_inst: str,
    # Mode 3 inputs
    fix_desc: str,
    fix_loc: str,
    fix_urgency: str,
    fix_context: str,
):
    """Executes exactly ONE API request for the active mode."""
    start_t = time.time()
    try:
        if current_mode == "Campus Guide":
            if not guide_q or not guide_q.strip():
                return "⚠️ **Input Required**: Please enter a question or click one of the suggested sample questions below."
            res = run_campus_guide(guide_q, CAMPUS_DATA, guide_filter)

        elif current_mode == "StudyMate":
            if not study_subj or not study_subj.strip():
                return "⚠️ **Input Required**: Please provide a subject, topic, or question in the StudyMate input field."
            res = run_study_mate(study_task, study_subj, study_timeline, study_hours, study_weak, study_inst)

        elif current_mode == "CampusFix":
            if not fix_desc or not fix_desc.strip():
                return "⚠️ **Input Required**: Please provide an issue description for CampusFix."
            res = run_campus_fix(fix_desc, fix_loc, fix_urgency, fix_context)

        else:
            return "⚠️ Unknown mode selected."

        duration = round(time.time() - start_t, 2)
        badge = (
            f"\n\n---\n"
            f"<div style='font-size: 11.5px; color: #64748b; display: flex; justify-content: space-between;'>"
            f"<span>⚡ <b>Model:</b> {GEMMA_MODEL_ID}</span>"
            f"<span>🎯 <b>Single-Request Execution:</b> {duration}s</span>"
            f"<span>🏫 <b>CampusMate AI Engine</b></span>"
            f"</div>"
        )
        return res + badge

    except CampusMateAPIError as err:
        return f"### ❌ Request Error\n\n{str(err)}"
    except Exception as exc:
        return f"### ❌ Unexpected Error\n\nSomething went wrong: {str(exc)[:200]}"


# -------------------------------------------------------------------
# Gradio UI Construction (Single-Screen Dashboard)
# -------------------------------------------------------------------
def build_app():
    with gr.Blocks(title="CampusMate AI - Powered by Gemma 4") as demo:
        # State to track currently selected mode
        active_mode_state = gr.State(value="Campus Guide")

        # 1. Header Section
        gr.HTML(f"""
        <div class="header-box">
            <div class="title-row">
                <div>
                    <h1 class="brand-title">CampusMate AI</h1>
                    <div class="tagline-text">Your campus. Your academics. Your AI companion.</div>
                </div>
                <div class="brand-badge">
                    <span>⚡ Powered by Gemma 4</span>
                    <span style="font-size:11px; opacity:0.8;">({GEMMA_MODEL_ID})</span>
                </div>
            </div>
            <p class="desc-text">
                CampusMate AI is a lightweight AI campus companion that helps students find campus information, 
                prepare for examinations, understand academic concepts, and turn everyday campus problems into actionable reports 
                using Google DeepMind's Gemma 4.
            </p>
        </div>
        """)

        # 2. Main Interaction Area (Single Screen Layout)
        with gr.Row():
            # Left Column: Inputs & Controls
            with gr.Column(scale=5):
                gr.Markdown("### 🎓 Select Companion Mode")
                mode_selector = gr.Radio(
                    choices=["Campus Guide", "StudyMate", "CampusFix"],
                    value="Campus Guide",
                    label="Mode",
                    show_label=False,
                    interactive=True
                )

                # ==========================================
                # MODE 1 CONTAINER: CAMPUS GUIDE
                # ==========================================
                with gr.Group(visible=True) as guide_group:
                    gr.Markdown("#### 🏫 Campus Guide")
                    gr.Markdown("<span style='font-size:13px; color:#64748b;'>Find academic resources, lab rules, student clubs, and college procedures.</span>")
                    
                    guide_filter_input = gr.Dropdown(
                        choices=["All", "Academics & Library", "Clubs & Activities", "Lab Etiquette", "College Procedures", "Campus Facilities"],
                        value="College Procedures",
                        label="Topic Filter",
                        interactive=True
                    )

                    gr.Markdown("**Quick Prompts (Click to populate):**")
                    with gr.Row():
                        btn_g1 = gr.Button("First-Year Prep", size="sm", variant="secondary")
                        btn_g2 = gr.Button("Attendance Shortfall", size="sm", variant="secondary")
                    with gr.Row():
                        btn_g3 = gr.Button("Practical Exam Rules", size="sm", variant="secondary")
                        btn_g4 = gr.Button("Technical Clubs & Hackathons", size="sm", variant="secondary")

                    guide_q_input = gr.Textbox(
                        label="Your Campus Question",
                        value="What should I check if my attendance drops below 75%?",
                        placeholder="e.g., How should I prepare for laboratory practical examinations, and what etiquette is expected?",
                        lines=3,
                        max_lines=6,
                        interactive=True
                    )

                    gr.HTML("<div class='info-note'>ℹ️ Campus information is augmented with local sample data (campus_data.json). Always verify official deadlines and policies with college authorities.</div>")

                # ==========================================
                # MODE 2 CONTAINER: STUDYMATE
                # ==========================================
                with gr.Group(visible=False) as study_group:
                    gr.Markdown("#### 📚 StudyMate")
                    gr.Markdown("<span style='font-size:13px; color:#64748b;'>Create custom revision schedules, simplify complex concepts, or break down difficult questions.</span>")
                    
                    study_task_input = gr.Radio(
                        choices=["Create a study plan", "Explain a concept", "Solve or explain an academic question"],
                        value="Create a study plan",
                        label="Study Objective",
                        interactive=True
                    )

                    gr.Markdown("**Quick Prompts (Click to populate):**")
                    with gr.Row():
                        btn_s1 = gr.Button("DSA 7-Day Plan", size="sm", variant="secondary")
                        btn_s2 = gr.Button("Explain Dijkstra's Algorithm", size="sm", variant="secondary")
                    with gr.Row():
                        btn_s3 = gr.Button("Deadlock Condition Breakdown", size="sm", variant="secondary")

                    study_subj_input = gr.Textbox(
                        label="Subject, Topic, or Question",
                        placeholder="e.g., Data Structures & Algorithms: Graphs and Dynamic Programming",
                        lines=2,
                        interactive=True
                    )

                    with gr.Row():
                        study_timeline_input = gr.Textbox(
                            label="Preparation Period / Exam Date",
                            placeholder="e.g., Mid-semester exam in 7 days",
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
                        label="Weak Topics / High-Priority Areas (Optional)",
                        placeholder="e.g., Graph traversals (BFS/DFS), Dynamic Programming memoization",
                        lines=1,
                        interactive=True
                    )

                    study_inst_input = gr.Textbox(
                        label="Additional Instructions or Question Specifics (Optional)",
                        placeholder="e.g., Include daily revision sessions and practice problem suggestions.",
                        lines=2,
                        interactive=True
                    )

                # ==========================================
                # MODE 3 CONTAINER: CAMPUSFIX
                # ==========================================
                with gr.Group(visible=False) as fix_group:
                    gr.Markdown("#### 🛠️ CampusFix")
                    gr.Markdown("<span style='font-size:13px; color:#64748b;'>Transform campus facility, Wi-Fi, or lab issues into a professional, actionable incident report draft.</span>")

                    gr.Markdown("**Quick Prompts (Click to populate):**")
                    with gr.Row():
                        btn_f1 = gr.Button("Lab Wi-Fi Disconnecting", size="sm", variant="secondary")
                        btn_f2 = gr.Button("Broken Digital Oscilloscope", size="sm", variant="secondary")
                    with gr.Row():
                        btn_f3 = gr.Button("Classroom Projector Malfunction", size="sm", variant="secondary")

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
                        placeholder="e.g., Our batch has a graded online practical examination scheduled in this lab tomorrow at 10:00 AM.",
                        lines=2,
                        interactive=True
                    )

                    gr.HTML("<div class='info-note'>⚠️ <b>Notice:</b> CampusFix generates a structured incident report draft for you to review and copy. It does not automatically file tickets or contact administration.</div>")

                # Generate Button (Primary Call-to-action)
                generate_btn = gr.Button(
                    "⚡ Generate with Gemma 4",
                    variant="primary",
                    elem_classes=["primary-gen-btn"],
                    size="lg"
                )

            # Right Column: Unified Output Display (Same Screen!)
            with gr.Column(scale=6):
                gr.Markdown("### 📋 Generated Intelligence")
                output_markdown = gr.Markdown(
                    value=(
                        "### 📌 Direct Answer\n\n"
                        "According to standard college policy, a **minimum of 75% attendance** is required across both theory and laboratory courses to remain eligible to appear for your end-semester examinations.\n\n"
                        "If your attendance has fallen below this threshold, your options and next steps depend on your exact percentage and the reason for absence.\n\n"
                        "### 🔍 Important Details & Regulations\n\n"
                        "- **Moderate Shortfall (Between 65% and 75%):** If your shortfall is due to certified medical reasons or representing the institute in recognized technical/sports competitions, you can apply for condonation. You must submit official medical certificates or representation letters to the Academic Dean within 7 days of returning to campus.\n"
                        "- **Critical Shortfall (Below 65%):** Attendance below 65% generally leads to grade penalties, debarment, or mandatory course repeating. Immediate consultation with your Faculty Advisor is required.\n\n"
                        "### 💡 Recommended Next Steps\n\n"
                        "1. **Check ERP Records:** Verify your current attendance logs on the official student portal.\n"
                        "2. **Calculate Required Classes:** Determine the exact number of consecutive sessions needed to cross the 75% threshold.\n"
                        "3. **Gather Proof:** Obtain certified documentation (Health Center medical slip or sports representation certificate).\n"
                        "4. **Meet Course Instructor & Advisor:** Meet during designated office hours to discuss remediation.\n\n"
                        "### ⚠️ Information Requiring Official Verification\n\n"
                        "Individual academic departments may have specific rules regarding condonation fees or maximum allowable medical leaves. **You must confirm your specific attendance status and formal condonation petition with your Faculty Advisor, Head of Department (HOD), or the Academic Dean's office.**\n\n"
                        "---\n"
                        "<div style='font-size: 11.5px; color: #64748b; display: flex; justify-content: space-between;'>"
                        f"<span>⚡ <b>Model:</b> {GEMMA_MODEL_ID}</span>"
                        "<span>🎯 <b>Single-Request Execution:</b> 2.4s</span>"
                        "<span>🏫 <b>CampusMate AI Engine</b></span>"
                        "</div>"
                    ),
                    elem_classes=["output-card"]
                )

                with gr.Row():
                    clear_btn = gr.Button("🗑️ Clear Output", size="sm", variant="secondary")

        # 3. Footer Section
        gr.HTML("""
        <div class="footer-text">
            CampusMate AI • Developed for "Build for Your Campus" Hackathon • Powered by Google DeepMind's Gemma 4 (gemma-4-26b-a4b-it) • MIT License
        </div>
        """)

        # ==========================================
        # Dynamic Visibility & State Handlers
        # ==========================================
        def on_mode_change(mode):
            return (
                mode,
                gr.update(visible=(mode == "Campus Guide")),
                gr.update(visible=(mode == "StudyMate")),
                gr.update(visible=(mode == "CampusFix")),
            )

        mode_selector.change(
            fn=on_mode_change,
            inputs=[mode_selector],
            outputs=[active_mode_state, guide_group, study_group, fix_group]
        )

        # Clear output handler
        clear_btn.click(
            fn=lambda: "*(Output cleared. Select a mode and click Generate to run again.)*",
            inputs=[],
            outputs=[output_markdown]
        )

        # ==========================================
        # Example Prompt Click Handlers
        # ==========================================
        # Campus Guide Prompts
        btn_g1.click(
            fn=lambda: "How should a first-year engineering student prepare for college academics, time management, and campus life?",
            inputs=[],
            outputs=[guide_q_input]
        )
        btn_g2.click(
            fn=lambda: "What should I check and what official procedure should I follow if I have an attendance shortfall below the 75% norm?",
            inputs=[],
            outputs=[guide_q_input]
        )
        btn_g3.click(
            fn=lambda: "How can I prepare effectively for practical examinations, and what laboratory etiquette must I follow?",
            inputs=[],
            outputs=[guide_q_input]
        )
        btn_g4.click(
            fn=lambda: "How can I get started with technical societies, coding clubs, and hackathons as a college student?",
            inputs=[],
            outputs=[guide_q_input]
        )

        # StudyMate Prompts
        btn_s1.click(
            fn=lambda: (
                "Create a study plan",
                "Data Structures and Algorithms (Trees, Graphs, and Dynamic Programming)",
                "Mid-semester examination in 7 days",
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
                "Explain the intuition simply with a small step-by-step example."
            ),
            inputs=[],
            outputs=[study_task_input, study_subj_input, study_timeline_input, study_hours_input, study_weak_input, study_inst_input]
        )
        btn_s3.click(
            fn=lambda: (
                "Solve or explain an academic question",
                "Operating Systems: What are the four Coffman conditions for deadlock, and how does Banker's algorithm achieve deadlock avoidance?",
                "End-semester exam preparation",
                2.5,
                "Resource Allocation Graph cycles and safe state calculation",
                "Provide a clear verification example with safe state check."
            ),
            inputs=[],
            outputs=[study_task_input, study_subj_input, study_timeline_input, study_hours_input, study_weak_input, study_inst_input]
        )

        # CampusFix Prompts
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

        # ==========================================
        # Generate Action (Single API Request Rule)
        # ==========================================
        generate_btn.click(
            fn=dispatch_generate,
            inputs=[
                active_mode_state,
                guide_q_input,
                guide_filter_input,
                study_task_input,
                study_subj_input,
                study_timeline_input,
                study_hours_input,
                study_weak_input,
                study_inst_input,
                fix_desc_input,
                fix_loc_input,
                fix_urgency_input,
                fix_context_input
            ],
            outputs=[output_markdown],
            api_name="generate"
        )

    return demo


def main():
    """Launch the CampusMate AI application."""
    port = int(os.environ.get("PORT", 7860))
    app = build_app()
    print("==================================================================")
    print("Starting CampusMate AI (Powered by Gemma 4: gemma-4-26b-a4b-it)")
    print(f"Local Server: http://127.0.0.1:{port}")
    print("==================================================================")
    app.launch(
        server_name="127.0.0.1",
        server_port=port,
        inbrowser=False,
        theme=gr.themes.Soft(primary_hue="blue", neutral_hue="slate"),
        css=CUSTOM_CSS
    )


if __name__ == "__main__":
    main()
