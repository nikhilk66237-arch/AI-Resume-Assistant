"""Production-Ready Streamlit Frontend for AI Resume Assistant Agent.
Decoupled Architecture: Frontend -> FastAPI Backend -> Gemini AI (server-side only).
Zero API key exposure, explainable scoring, comprehensive ATS & JD analysis.
"""
import os
import requests
import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8001")


# Streamlit Page Config
st.set_page_config(
    page_title="AI Resume Assistant | Career & ATS Optimizer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Adaptive, Modern CSS Design
st.markdown("""
<style>
    /* Typography & Titles */
    .app-header {
        text-align: center;
        margin-top: -15px;
        margin-bottom: 25px;
    }
    .main-title {
        font-size: 32px;
        font-weight: 800;
        color: #1E88E5;
        letter-spacing: -0.5px;
        margin-bottom: 4px;
    }
    .sub-title {
        font-size: 15px;
        color: var(--text-color, #64748B);
        opacity: 0.85;
    }
    
    /* Step Cards */
    .step-banner {
        background: var(--secondary-background-color, rgba(128, 128, 128, 0.08));
        border-left: 4px solid #1E88E5;
        border-radius: 6px;
        padding: 8px 14px;
        font-weight: 700;
        font-size: 13px;
        color: var(--text-color, #1E293B);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin: 16px 0 10px 0;
    }

    /* Metric Cards */
    .metric-card {
        background-color: var(--secondary-background-color, rgba(128, 128, 128, 0.08));
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 10px;
        padding: 14px 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        margin-bottom: 12px;
    }
    .metric-value {
        font-size: 26px;
        font-weight: 800;
        color: var(--text-color, #0F172A);
        margin: 2px 0;
    }
    .metric-label {
        font-size: 12px;
        color: var(--text-color, #64748B);
        opacity: 0.8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Hero Match Card */
    .hero-match-card {
        background: var(--secondary-background-color, rgba(30, 136, 229, 0.06));
        border: 2px solid #1E88E5;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        margin-bottom: 20px;
    }
    .hero-match-pct {
        font-size: 56px;
        font-weight: 900;
        color: #1E88E5;
        line-height: 1;
        margin: 8px 0;
    }

    /* Skill Badges */
    .skill-badge {
        display: inline-block;
        padding: 4px 11px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin: 3px 2px;
        line-height: 1.4;
    }
    .badge-match {
        background-color: rgba(16, 185, 129, 0.18);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.35);
    }
    .badge-missing {
        background-color: rgba(239, 68, 68, 0.18);
        color: #EF4444;
        border: 1px solid rgba(239, 68, 68, 0.35);
    }
    .badge-additional {
        background-color: rgba(59, 130, 246, 0.18);
        color: #3B82F6;
        border: 1px solid rgba(59, 130, 246, 0.35);
    }
    .badge-req {
        background-color: rgba(220, 38, 38, 0.18);
        color: #EF4444;
        border: 1px solid rgba(220, 38, 38, 0.35);
    }
    .badge-rec {
        background-color: rgba(245, 158, 11, 0.18);
        color: #F59E0B;
        border: 1px solid rgba(245, 158, 11, 0.35);
    }
    .badge-opt {
        background-color: rgba(100, 116, 139, 0.18);
        color: #94A3B8;
        border: 1px solid rgba(100, 116, 139, 0.35);
    }

    /* Priority Indicator Tags */
    .tag-priority-high {
        background-color: #EF4444;
        color: #FFFFFF;
        padding: 3px 9px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.5px;
    }
    .tag-priority-med {
        background-color: #F59E0B;
        color: #FFFFFF;
        padding: 3px 9px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.5px;
    }
    .tag-priority-low {
        background-color: #10B981;
        color: #FFFFFF;
        padding: 3px 9px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.5px;
    }
    
    /* Scrollable skill badge container for readability */
    .skills-scroll-box {
        max-height: 220px;
        overflow-y: auto;
        padding: 8px;
        border-radius: 8px;
        background: var(--secondary-background-color, rgba(128, 128, 128, 0.05));
        border: 1px solid rgba(128, 128, 128, 0.15);
    }
</style>
""", unsafe_allow_html=True)


# --- BACKEND API CALLS ---

def check_backend_health() -> Dict[str, Any]:
    """Queries backend health without exposing secret credentials."""
    try:
        r = requests.get(f"{BACKEND_URL}/api/health", timeout=2)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {"status": "offline", "gemini_configured": False}


def extract_text_via_api(file) -> Optional[str]:
    """Extracts text using the secure server-side parser."""
    try:
        files = {"file": (file.name, file.getvalue(), file.type or "application/octet-stream")}
        r = requests.post(f"{BACKEND_URL}/api/extract-text", files=files, timeout=12)
        if r.status_code == 200:
            return r.json().get("text")
        else:
            err = r.json().get("detail", "Error extracting text.")
            st.error(f"❌ Upload Error: {err}")
    except Exception as e:
        from backend.parser import extract_resume_text
        try:
            return extract_resume_text(file.name, file.getvalue())
        except Exception as local_err:
            st.error(f"❌ Parser Error: {str(local_err)}")
    return None


def call_analyze_api(resume_text: str, target_role: str, job_description: str) -> Optional[Dict[str, Any]]:
    """Sends analysis request to FastAPI backend."""
    try:
        payload = {
            "resume_text": resume_text,
            "target_role": target_role,
            "job_description": job_description
        }
        r = requests.post(f"{BACKEND_URL}/api/analyze-resume", json=payload, timeout=30)
        if r.status_code == 200:
            return r.json()
        else:
            st.error(f"❌ Analysis Server Error ({r.status_code}): {r.json().get('detail')}")
    except Exception:
        from backend.gemini_service import run_full_resume_analysis
        try:
            res = run_full_resume_analysis(resume_text, target_role, job_description)
            return res.model_dump()
        except Exception as e:
            st.error(f"❌ Engine Error: {str(e)}")
    return None


def call_compare_api(resume_text: str, role_1: str, jd_1: str, role_2: str, jd_2: str) -> Optional[Dict[str, Any]]:
    """Sends multi-role comparison request to backend."""
    try:
        payload = {
            "resume_text": resume_text,
            "role_1_name": role_1,
            "role_1_jd": jd_1,
            "role_2_name": role_2,
            "role_2_jd": jd_2
        }
        r = requests.post(f"{BACKEND_URL}/api/compare-roles", json=payload, timeout=35)
        if r.status_code == 200:
            return r.json()
    except Exception:
        from backend.gemini_service import run_full_resume_analysis
        res1 = run_full_resume_analysis(resume_text, role_1, jd_1)
        res2 = run_full_resume_analysis(resume_text, role_2, jd_2)
        return {
            "role_1": {
                "name": role_1,
                "overall_match": res1.overall_match,
                "matching_skills": res1.skills_comparison.matching_skills,
                "missing_skills": res1.skills_comparison.missing_skills
            },
            "role_2": {
                "name": role_2,
                "overall_match": res2.overall_match,
                "matching_skills": res2.skills_comparison.matching_skills,
                "missing_skills": res2.skills_comparison.missing_skills
            },
            "recommendation": (
                f"Your profile aligns stronger with {role_1} ({res1.overall_match}%) than {role_2} ({res2.overall_match}%)."
                if res1.overall_match > res2.overall_match else
                f"Your profile aligns stronger with {role_2} ({res2.overall_match}%) than {role_1} ({res1.overall_match}%)."
            )
        }
    return None


def generate_text_report(res: Dict[str, Any]) -> str:
    """Generates a comprehensive, formatted analytical report for offline review/download."""
    scores = res.get("scores", {})
    skills = res.get("skills_comparison", {})
    reqs = res.get("target_role_requirements", {})
    ats = res.get("ats_analysis", {})
    quality = res.get("resume_quality", {})
    jd = res.get("jd_analysis") or {}

    report = f"""# AI RESUME ANALYSIS REPORT
Generated by: AI Resume Assistant Agent (v2.0)
Target Role: {res.get('target_role')}
Job Description Supplied: {'Yes' if res.get('job_description_provided') else 'No'}
Overall Match Score: {res.get('overall_match', 0)}% ({res.get('match_level', '')})

============================================================
1. EXECUTIVE SUMMARY & METRIC BREAKDOWN
============================================================
- Overall Resume-to-Role Match : {res.get('overall_match', 0)}%
- Skills Match                 : {scores.get('skills_match', 0)}%
- Technical Skills Match       : {scores.get('technical_skills_match', 0)}%
- Soft Skills Match            : {scores.get('soft_skills_match', 0)}%
- Experience Match             : {scores.get('experience_match', 0)}%
- Education Match              : {scores.get('education_match', 0)}%
- Projects Match               : {scores.get('projects_match', 0)}%
- Certifications Match         : {scores.get('certifications_match', 0)}%
- Keywords Match               : {scores.get('keywords_match', 0)}%
- Job Description Match        : {scores.get('job_description_match', 'N/A')}%
- ATS Readiness Score          : {scores.get('ats_readiness', 0)}%

Scoring Methodology:
{scores.get('scoring_methodology', '')}

============================================================
2. SKILLS COMPARISON
============================================================
MATCHING SKILLS ({len(skills.get('matching_skills', []))}):
{', '.join(skills.get('matching_skills', [])) or 'None detected'}

MISSING / GAP SKILLS ({len(skills.get('missing_skills', []))}):
{', '.join(skills.get('missing_skills', [])) or 'None! All target competencies matched.'}

ADDITIONAL DETECTED SKILLS ({len(skills.get('additional_skills', []))}):
{', '.join(skills.get('additional_skills', [])) or 'None'}

============================================================
3. TARGET ROLE COMPETENCY REQUIREMENTS
============================================================
- Required Skills   : {', '.join(reqs.get('required_skills', []))}
- Recommended Skills: {', '.join(reqs.get('recommended_skills', []))}
- Optional Skills   : {', '.join(reqs.get('optional_skills', []))}
- Education Norm    : {reqs.get('education_expectation', '')}
- Experience Norm   : {reqs.get('experience_expectation', '')}
"""
    if jd.get("jd_provided"):
        report += f"""
============================================================
4. JOB DESCRIPTION DIRECT ALIGNMENT
============================================================
- Direct JD Match Score      : {jd.get('jd_match_score', 0)}%
- Matched JD Requirements    : {', '.join(jd.get('matched_jd_requirements', []))}
- Missing JD Requirements    : {', '.join(jd.get('missing_jd_requirements', []))}
- Important JD Keywords      : {', '.join(jd.get('important_jd_keywords', []))}
- Recommended Resume Changes :
"""
        for change in jd.get('recommended_resume_changes', []):
            report += f"  * {change}\n"

    report += f"""
============================================================
5. ATS (APPLICANT TRACKING SYSTEM) AUDIT
============================================================
- ATS Readiness Score: {ats.get('ats_score', 0)}%
- Readability Notes  : {ats.get('readability_notes', '')}

ATS Strengths:
"""
    for s in ats.get("strengths", []):
        report += f"  ✓ {s}\n"

    report += "\nATS Roadblocks / Issues to Fix:\n"
    for p in ats.get("problems", []):
        report += f"  ⚠ {p}\n"

    report += "\nRecommended ATS Improvements:\n"
    for imp in ats.get("improvements", []):
        report += f"  → {imp}\n"

    report += f"""
============================================================
6. RESUME QUALITY ANALYSIS
============================================================
Improvement Priority: {quality.get('improvement_priority', 'MEDIUM')}

Strengths:
"""
    for strg in quality.get("strengths", []):
        report += f"  * {strg}\n"

    report += "\nAreas for Growth / Weaknesses:\n"
    for w in quality.get("weaknesses", []):
        report += f"  * {w}\n"

    report += "\nMissing Information:\n"
    for m in quality.get("missing_information", []):
        report += f"  * {m}\n"

    report += """
============================================================
7. ACTIONABLE IMPROVEMENT SUGGESTIONS
============================================================
"""
    for sug in res.get("improvement_suggestions", []):
        report += f"- {sug}\n"

    if res.get("improved_resume_points"):
        report += "\nOPTIMIZED BULLET POINT EXAMPLES:\n"
        for pt in res.get("improved_resume_points", []):
            report += f"  • {pt}\n"

    report += f"""
============================================================
DISCLAIMER:
{res.get('disclaimer', '')}
============================================================
"""
    return report


# --- HEADER ---
st.markdown("""
<div class="app-header">
    <div class="main-title">🤖 PS-03: AI Resume Assistant Agent</div>
    <div class="sub-title">Intelligent Career Alignment, Skill Gap Analysis & ATS Optimization Platform</div>
</div>
""", unsafe_allow_html=True)

# System Health Banner
health = check_backend_health()
with st.sidebar:
    st.header("⚙️ Engine Status")
    if health.get("status") == "online":
        st.success("🟢 Backend API: Connected")
        if health.get("gemini_configured"):
            st.info("✨ AI Engine: Active (Google Gemini)")
        else:
            st.warning("⚡ Engine: Deterministic Mode (Configure backend environment to enable AI)")
    else:
        st.info("🔌 Engine: Direct Integrated Mode")
    
    st.markdown("---")
    st.markdown("### 📌 Navigation & Tools")
    st.caption("Switch between single role optimization, multi-role fit comparison, and section completeness checks.")

# Main Navigation Tabs
tab_main, tab_compare, tab_completeness = st.tabs([
    "🎯 Resume & Role Optimizer",
    "📊 Multi-Role Comparison",
    "📋 ATS Completeness Audit"
])

# ==============================================================================
# TAB 1: RESUME & ROLE OPTIMIZER (THE CORE SEQUENTIAL FLOW)
# ==============================================================================
with tab_main:
    # Initialize session state variables
    if "resume_content" not in st.session_state:
        st.session_state.resume_content = ""
    if "resume_filename" not in st.session_state:
        st.session_state.resume_filename = ""
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None

    # Step 1: Upload Resume
    st.markdown('<div class="step-banner">STEP 1: UPLOAD YOUR RESUME</div>', unsafe_allow_html=True)
    
    upload_tab1, upload_tab2 = st.tabs(["📁 Upload File (PDF / DOCX / TXT)", "✍️ Paste Resume Text"])
    with upload_tab1:
        uploaded_file = st.file_uploader(
            "Select resume document:",
            type=["pdf", "docx", "txt"],
            help="Maximum file size 5MB. PDF, DOCX, and TXT formats are fully supported.",
            key="file_uploader_main"
        )
        if uploaded_file is not None:
            if len(uploaded_file.getvalue()) > 5 * 1024 * 1024:
                st.error("❌ File exceeds 5MB limit. Please upload a smaller file.")
            else:
                extracted = extract_text_via_api(uploaded_file)
                if extracted:
                    st.session_state.resume_content = extracted
                    st.session_state.resume_filename = uploaded_file.name

    with upload_tab2:
        pasted_text = st.text_area(
            "Paste your resume text:",
            height=140,
            placeholder="Paste your plain text resume here...",
            key="pasted_text_input"
        )
        if pasted_text.strip():
            st.session_state.resume_content = pasted_text.strip()
            st.session_state.resume_filename = "Pasted Text Document"

    # Status confirmation badge
    if st.session_state.resume_content:
        words = len(st.session_state.resume_content.split())
        col_badge, col_clear = st.columns([4, 1])
        with col_badge:
            st.success(f"✓ **Resume Loaded:** {st.session_state.resume_filename} ({words} words detected)")
        with col_clear:
            if st.button("🗑 Clear File", key="btn_clear_resume"):
                st.session_state.resume_content = ""
                st.session_state.resume_filename = ""
                st.session_state.analysis_result = None
                st.rerun()

    # Step 2: Select / Enter Target Role & Step 3: Optional Job Description
    st.markdown('<div class="step-banner">STEP 2 & 3: TARGET ROLE & JOB DESCRIPTION</div>', unsafe_allow_html=True)
    
    cfg_col1, cfg_col2 = st.columns([1, 1])
    with cfg_col1:
        role_choices = [
            "Python Developer",
            "Full Stack Developer",
            "Data Analyst",
            "Data Scientist",
            "AI/ML Engineer",
            "Cybersecurity Analyst",
            "Cloud Engineer",
            "DevOps Engineer",
            "Software Engineer",
            "Custom Role..."
        ]
        chosen_role = st.selectbox("Select Target Role:", role_choices, index=0, key="sel_target_role")
        if chosen_role == "Custom Role...":
            custom_title = st.text_input("Enter Custom Target Role Title:", placeholder="e.g. Backend Go Developer", key="txt_custom_role")
            target_role_value = custom_title.strip() if custom_title.strip() else "Software Engineer"
        else:
            target_role_value = chosen_role

    with cfg_col2:
        jd_input = st.text_area(
            "Paste Job Description (Optional):",
            height=90,
            placeholder="Paste employer's JD here to prioritize exact company requirements over default industry expectations...",
            key="txt_job_desc"
        )

    # Step 4: Analyze Action Button
    st.markdown('<div class="step-banner">STEP 4: RUN ANALYSIS</div>', unsafe_allow_html=True)
    
    act_col1, act_col2, act_col3 = st.columns([2, 2, 4])
    with act_col1:
        analyze_btn = st.button("🚀 Analyze Resume", type="primary", use_container_width=True, key="btn_run_analysis")
    with act_col2:
        reset_btn = st.button("🔄 Reset / New Analysis", use_container_width=True, key="btn_reset_analysis")

    if reset_btn:
        st.session_state.resume_content = ""
        st.session_state.resume_filename = ""
        st.session_state.analysis_result = None
        st.rerun()

    # Determine effective resume content from file or text area
    current_resume = (st.session_state.resume_content or 
                      st.session_state.get("pasted_text_input", "").strip() or 
                      pasted_text.strip())
    if current_resume:
        st.session_state.resume_content = current_resume
        if not st.session_state.resume_filename:
            st.session_state.resume_filename = "Pasted Text Document"

    if analyze_btn:
        if not current_resume:
            st.error("⚠️ Please upload a resume file (PDF, DOCX) or paste resume text in Step 1 first!")
        else:
            with st.spinner(f"Analyzing resume against '{target_role_value}'..."):
                analysis_data = call_analyze_api(
                    resume_text=current_resume,
                    target_role=target_role_value,
                    job_description=jd_input
                )
                if analysis_data:
                    st.session_state.analysis_result = analysis_data
                    st.success("✓ Analysis completed successfully!")

    # ==============================================================================
    # RESULT DASHBOARD
    # ==============================================================================
    if st.session_state.analysis_result:
        res = st.session_state.analysis_result
        scores = res.get("scores", {})
        overall_match = res.get("overall_match", 0)
        match_level = res.get("match_level", "Moderate Match")
        role_reqs = res.get("target_role_requirements", {})
        skills_comp = res.get("skills_comparison", {})
        ats_data = res.get("ats_analysis", {})
        quality_data = res.get("resume_quality", {})
        jd_comp = res.get("jd_analysis") or {}

        st.markdown("---")
        
        # 1. OVERALL MATCH HERO SECTION (Immediately Visible)
        st.subheader("🎯 Overall Match Assessment")
        hero_left, hero_right = st.columns([1, 2])
        
        with hero_left:
            st.markdown(f"""
            <div class="hero-match-card">
                <div class="metric-label">Overall Resume ↔ Target Role Match</div>
                <div class="hero-match-pct">{overall_match}%</div>
                <div style="font-size: 15px; font-weight: 700; color: #059669; margin-bottom: 6px;">{match_level}</div>
                <div style="font-size: 12px; color: #64748B;">Target Role: <strong>{res.get('target_role')}</strong></div>
            </div>
            """, unsafe_allow_html=True)

        with hero_right:
            st.write(f"**Methodology:** {scores.get('scoring_methodology', '')}")
            st.progress(overall_match / 100)
            st.caption(res.get("disclaimer", ""))
            
            # Quick download button in hero area
            report_content = generate_text_report(res)
            st.download_button(
                label="📥 Download Full Analysis Report (.md)",
                data=report_content,
                file_name=f"resume_analysis_{res.get('target_role').lower().replace(' ', '_')}.md",
                mime="text/markdown",
                help="Download formatted analytical report including all scores, gaps, and recommendations."
            )

        # 2. METRIC CARDS GRID (All 8 Core Metrics)
        st.subheader("📊 Comprehensive Metric Breakdown")
        
        row1_c1, row1_c2, row1_c3, row1_c4 = st.columns(4)
        with row1_c1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Skills Match</div>
                <div class="metric-value">{scores.get('skills_match', 0)}%</div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(scores.get('skills_match', 0) / 100)
            
        with row1_c2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Technical Skills</div>
                <div class="metric-value">{scores.get('technical_skills_match', 0)}%</div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(scores.get('technical_skills_match', 0) / 100)
            
        with row1_c3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Experience Match</div>
                <div class="metric-value">{scores.get('experience_match', 0)}%</div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(scores.get('experience_match', 0) / 100)
            
        with row1_c4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Education Match</div>
                <div class="metric-value">{scores.get('education_match', 0)}%</div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(scores.get('education_match', 0) / 100)

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        
        row2_c1, row2_c2, row2_c3, row2_c4 = st.columns(4)
        with row2_c1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Projects Match</div>
                <div class="metric-value">{scores.get('projects_match', 0)}%</div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(scores.get('projects_match', 0) / 100)
            
        with row2_c2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Keywords Match</div>
                <div class="metric-value">{scores.get('keywords_match', 0)}%</div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(scores.get('keywords_match', 0) / 100)
            
        with row2_c3:
            jd_score = scores.get('job_description_match')
            val_str = f"{jd_score}%" if jd_score is not None else "N/A"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Job Description Match</div>
                <div class="metric-value">{val_str}</div>
            </div>
            """, unsafe_allow_html=True)
            if jd_score is not None:
                st.progress(jd_score / 100)
            else:
                st.caption("Provide a JD in Step 3 to evaluate direct alignment")
                
        with row2_c4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">ATS Score</div>
                <div class="metric-value" style="color: #059669;">{scores.get('ats_readiness', 0)}%</div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(scores.get('ats_readiness', 0) / 100)

        # Factor Drilldown
        with st.expander("🔍 View Mathematical Score Calculations & Contributing Factors"):
            for factor in scores.get("factors", []):
                st.write(f"- **{factor.get('category')}**: Score: `{factor.get('score')}%` | Weight: `{int(factor.get('weight')*100)}%` | Contribution: **+{factor.get('contribution')} pts** — {factor.get('explanation')}")

        st.markdown("---")

        # 3. JOB DESCRIPTION COMPARISON (Primary when JD provided)
        if res.get("job_description_provided") and jd_comp:
            st.subheader("🏢 Employer Job Description Direct Comparison")
            st.info("💡 **Employer-Specific JD Requirements**: This analysis evaluates direct alignment with the provided job posting, completely separated from generic role assumptions.")
            
            jd_col1, jd_col2 = st.columns([1, 2])
            with jd_col1:
                st.markdown(f"""
                <div class="metric-card" style="border-left: 6px solid #10B981; padding: 18px;">
                    <div class="metric-label">Direct JD Match</div>
                    <div class="metric-value" style="color: #059669;">{jd_comp.get('jd_match_score', 0)}%</div>
                    <div style="font-size: 11px; color: #64748B;">Based on required JD competencies</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("##### Important JD Keywords")
                keywords_list = jd_comp.get("important_jd_keywords", [])
                if keywords_list:
                    st.write(", ".join(keywords_list))
                else:
                    st.write("Keywords extracted from JD.")

            with jd_col2:
                jd_sub1, jd_sub2 = st.columns(2)
                with jd_sub1:
                    st.markdown("##### ✓ Matched JD Requirements")
                    m_jd = jd_comp.get("matched_jd_requirements", [])
                    if m_jd:
                        badges = "".join([f'<span class="skill-badge badge-match">✓ {s}</span>' for s in m_jd])
                        st.markdown(badges, unsafe_allow_html=True)
                    else:
                        st.info("No direct skill matches from JD.")

                with jd_sub2:
                    st.markdown("##### ✕ Missing JD Requirements")
                    miss_jd = jd_comp.get("missing_jd_requirements", [])
                    if miss_jd:
                        badges = "".join([f'<span class="skill-badge badge-missing">✕ {s}</span>' for s in miss_jd])
                        st.markdown(badges, unsafe_allow_html=True)
                    else:
                        st.success("All key JD requirements detected in your resume!")

                st.markdown("##### → Recommended Resume Changes for this JD")
                for rec_change in jd_comp.get("recommended_resume_changes", []):
                    st.warning(f"• {rec_change}")

            st.markdown("---")

        # 4. SKILLS COMPARISON (3 Distinct Readable Columns)
        st.subheader("⚖️ Skills Comparison")
        st.caption("Side-by-side verification of competencies found in your resume vs role demands.")
        
        sc_col1, sc_col2, sc_col3 = st.columns(3)
        with sc_col1:
            matching = skills_comp.get("matching_skills", [])
            st.markdown(f"#### ✓ Matching Skills ({len(matching)})")
            st.caption("Skills present in both your resume and target requirements:")
            if matching:
                badges = "".join([f'<span class="skill-badge badge-match">✓ {s}</span>' for s in matching])
                st.markdown(f'<div class="skills-scroll-box">{badges}</div>', unsafe_allow_html=True)
            else:
                st.info("No direct skill matches detected.")

        with sc_col2:
            missing = skills_comp.get("missing_skills", [])
            st.markdown(f"#### ✕ Missing Skills ({len(missing)})")
            st.caption("Required or recommended for the role but absent from resume:")
            if missing:
                badges = "".join([f'<span class="skill-badge badge-missing">✕ {s}</span>' for s in missing])
                st.markdown(f'<div class="skills-scroll-box">{badges}</div>', unsafe_allow_html=True)
            else:
                st.success("All target skills detected in your resume!")

        with sc_col3:
            additional = skills_comp.get("additional_skills", [])
            st.markdown(f"#### ＋ Additional Skills ({len(additional)})")
            st.caption("Bonus competencies detected on your resume not explicitly required:")
            if additional:
                badges = "".join([f'<span class="skill-badge badge-additional">＋ {s}</span>' for s in additional])
                st.markdown(f'<div class="skills-scroll-box">{badges}</div>', unsafe_allow_html=True)
            else:
                st.write("No additional standalone skills found.")

        st.markdown("---")

        # 5. TARGET ROLE REQUIREMENTS (Only relevant categories)
        st.subheader(f"📌 Target Role Requirements: {res.get('target_role')}")
        
        req_tabs = st.tabs(["Required Skills", "Recommended Skills", "Optional Skills", "Domain Toolchain"])
        with req_tabs[0]:
            st.markdown("##### 🚨 Required Skills (Must Demonstrate)")
            req_list = role_reqs.get("required_skills", [])
            if req_list:
                st.markdown("".join([f'<span class="skill-badge badge-req">{s.upper()}</span>' for s in req_list]), unsafe_allow_html=True)
            else:
                st.write("No mandatory prerequisites specified.")

        with req_tabs[1]:
            st.markdown("##### ⭐ Recommended Skills (Competitive Advantage)")
            rec_list = role_reqs.get("recommended_skills", [])
            if rec_list:
                st.markdown("".join([f'<span class="skill-badge badge-rec">{s.title()}</span>' for s in rec_list]), unsafe_allow_html=True)

        with req_tabs[2]:
            st.markdown("##### 💡 Optional Skills (Value-Add)")
            opt_list = role_reqs.get("optional_skills", [])
            if opt_list:
                st.markdown("".join([f'<span class="skill-badge badge-opt">{s.title()}</span>' for s in opt_list]), unsafe_allow_html=True)

        with req_tabs[3]:
            st.markdown(f"##### Relevant Technology Stack for {res.get('target_role')}")
            # Display only categories that have non-empty items
            if role_reqs.get("programming_languages"):
                st.write("**Programming Languages:**", ", ".join(role_reqs.get("programming_languages", [])))
            if role_reqs.get("frameworks"):
                st.write("**Frameworks & Libraries:**", ", ".join(role_reqs.get("frameworks", [])))
            if role_reqs.get("databases"):
                st.write("**Databases:**", ", ".join(role_reqs.get("databases", [])))
            if role_reqs.get("cloud_devops_tools"):
                st.write("**Cloud & DevOps Tools:**", ", ".join(role_reqs.get("cloud_devops_tools", [])))
            if role_reqs.get("ai_ml_tools") and len(role_reqs.get("ai_ml_tools")) > 0:
                st.write("**AI / Machine Learning Tools:**", ", ".join(role_reqs.get("ai_ml_tools", [])))
            if role_reqs.get("soft_skills"):
                st.write("**Soft Skills:**", ", ".join(role_reqs.get("soft_skills", [])))
            st.write(f"**Academic Norm:** {role_reqs.get('education_expectation', 'Degree in CS or related field')}")
            st.write(f"**Experience Norm:** {role_reqs.get('experience_expectation', 'Demonstrable projects or relevant experience')}")
            if role_reqs.get("recommended_certifications"):
                st.write("**Recognized Certifications:**", ", ".join(role_reqs.get("recommended_certifications", [])))

        st.markdown("---")

        # 6. HOW TO IMPROVE YOUR RESUME (Prioritized Suggestions)
        st.subheader("💡 How to Improve Your Resume")
        st.caption("Actionable recommendations prioritized by potential score impact:")
        
        # Categorize suggestions into High, Medium, Low
        missing_skills_list = skills_comp.get("missing_skills", [])
        raw_suggs = res.get("improvement_suggestions", [])
        
        high_suggs = []
        med_suggs = []
        low_suggs = []
        
        # Generate gap-based high-priority suggestions
        if missing_skills_list:
            high_suggs.append(f"**Acquire Missing Core Competencies:** Add verified experience with **{', '.join(missing_skills_list[:3])}**.")
        if not ats_data.get("checklist", {}).get("Contact Information Present", True):
            high_suggs.append("**Missing Header Contacts:** Add phone number and professional email address to the resume header.")
        if not ats_data.get("checklist", {}).get("Projects Section Present", True):
            high_suggs.append("**Missing Technical Projects:** Add 2-3 technical projects demonstrating your skills with code repositories.")
            
        # Medium priority suggestions
        med_suggs.append("**Add Quantifiable Metrics:** Rewrite bullet points to follow: *'Accomplished [X] measured by [Y] by doing [Z]'*.")
        if res.get("job_description_provided") and jd_comp.get("missing_jd_requirements"):
            med_suggs.append(f"**Mirror Target JD Keywords:** Incorporate {', '.join(jd_comp.get('missing_jd_requirements')[:3])} directly into your experience or project sections.")
        med_suggs.append("**Add GitHub & Demo URLs:** Ensure every highlighted project has an active link to source code or live deployment.")
        
        # Low priority suggestions
        low_suggs.append("**ATS Formatting Polish:** Use clean standard section headings ('Education', 'Technical Skills', 'Experience').")
        low_suggs.append("**Remove Redundant Skills:** Deprecate outdated tool references to keep the skills section crisp.")

        imp_col1, imp_col2, imp_col3 = st.columns(3)
        with imp_col1:
            st.markdown('<span class="tag-priority-high">HIGH PRIORITY</span>', unsafe_allow_html=True)
            for hs in high_suggs[:3]:
                st.error(hs)

        with imp_col2:
            st.markdown('<span class="tag-priority-med">MEDIUM PRIORITY</span>', unsafe_allow_html=True)
            for ms in med_suggs[:3]:
                st.warning(ms)

        with imp_col3:
            st.markdown('<span class="tag-priority-low">LOW PRIORITY</span>', unsafe_allow_html=True)
            for ls in low_suggs[:3]:
                st.info(ls)

        if res.get("weak_descriptions") or res.get("improved_resume_points"):
            st.markdown("#### ✨ Bullet Point Optimization (Before & After)")
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                st.markdown("##### 📌 Weak / Vague Phrasing Found")
                for w in res.get("weak_descriptions", []):
                    st.warning(f"\"{w}\"")
            with col_b2:
                st.markdown("##### 🚀 Optimized Impact Rewrites")
                for p in res.get("improved_resume_points", []):
                    st.success(f"\"{p}\"")

        st.markdown("---")

        # 7. ATS ANALYSIS (Score, Strengths, Issues, Recommended Fixes)
        st.subheader("🛡️ ATS (Applicant Tracking System) Audit")
        
        ats_col1, ats_col2 = st.columns([1, 2])
        with ats_col1:
            st.markdown(f"""
            <div class="metric-card" style="border-left: 6px solid #10B981; padding: 18px;">
                <div class="metric-label">ATS Readiness Score</div>
                <div class="metric-value" style="color: #059669;">{ats_data.get('ats_score', 0)}%</div>
                <div style="font-size: 12px; color: #64748B;">Machine Readability & Structure</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.write(f"**Why this score was given:** {ats_data.get('readability_notes', 'Score calculated from contact parsing, section clarity, standard heading conventions, and format layout.')}")
            
            st.write("**ATS System Checklist:**")
            for item, status in ats_data.get("checklist", {}).items():
                if status:
                    st.write(f"✓ :green[{item}]")
                else:
                    st.write(f"✕ :red[{item}]")

        with ats_col2:
            st.markdown("##### ✓ ATS Strengths")
            for s in ats_data.get("strengths", []):
                st.write(f"✓ {s}")
                
            st.markdown("##### ⚠ ATS Issues to Fix")
            problems = ats_data.get("problems", [])
            if problems:
                for p in problems:
                    st.warning(f"⚠ {p}")
            else:
                st.success("No major ATS formatting roadblocks detected.")
                
            st.markdown("##### → Recommended Fixes")
            for imp in ats_data.get("improvements", []):
                st.info(f"→ {imp}")

        st.markdown("---")

        # 8. RESUME QUALITY ANALYSIS
        st.subheader("💎 Resume Quality Analysis")
        q_col1, q_col2 = st.columns(2)
        with q_col1:
            st.markdown("##### Resume Strengths")
            for s in quality_data.get("strengths", []):
                st.success(f"✓ {s}")
                
            st.markdown("##### Missing Information")
            for m in quality_data.get("missing_information", []):
                st.write(f"• {m}")

        with q_col2:
            st.markdown("##### Resume Weaknesses")
            for w in quality_data.get("weaknesses", []):
                st.error(f"✕ {w}")
                
            st.markdown("##### Potential Issues / Red Flags")
            red_flags = quality_data.get("potential_red_flags", [])
            if red_flags and red_flags != ["none"]:
                for rf in red_flags:
                    st.warning(f"⚠ {rf}")
            else:
                st.write("✓ No immediate red flags identified.")

        st.markdown("---")

        # 9. ROLE COMPATIBILITY MEASUREMENTS
        st.subheader("🧭 Multi-Role Compatibility Measurements")
        st.caption("Compatibility index across industry career profiles based on detected skills (compatibility measurement, not guaranteed career outcomes):")
        
        role_recs = res.get("role_recommendations", [])
        if role_recs:
            rec_cols = st.columns(min(len(role_recs), 3))
            for i, rec in enumerate(role_recs[:6]):
                with rec_cols[i % 3]:
                    st.markdown(f"""
                    <div class="metric-card" style="margin-bottom: 12px; text-align: left;">
                        <div style="font-weight: 700; font-size: 15px; color: var(--text-color, #0F172A);">{rec.get('role_name')}</div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin: 4px 0;">
                            <span style="font-size: 22px; font-weight: 800; color: #1E88E5;">{rec.get('match_percentage')}%</span>
                            <span style="font-size: 11px; font-weight: 600; padding: 2px 6px; border-radius: 4px; background: rgba(128, 128, 128, 0.15);">{rec.get('compatibility_tier')}</span>
                        </div>
                        <div style="font-size: 12px; color: #64748B;">{rec.get('reasoning')}</div>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("---")

        # 10. RECOMMENDED NEXT STEPS
        st.subheader("📋 Recommended Next Steps")
        st.caption("Strategic action items derived from detected resume gaps and target role requirements:")
        gap_focus = ", ".join(missing_skills_list[:3]) if missing_skills_list else "advanced system design patterns"
        
        step_c1, step_c2 = st.columns(2)
        with step_c1:
            st.info(f"**Step 1: Bridge High-Priority Skill Gaps**\n\nBuild or enhance a technical project showcasing hands-on usage of **{gap_focus}**.")
            st.info("**Step 2: Quantify Achievement Metrics**\n\nAdd measurable business impact (e.g., *improved query throughput by 35%*, *served 10,000+ requests*) to each project bullet.")
        with step_c2:
            st.info("**Step 3: Align Terminology with Target JD**\n\nMirror exact keywords, tools, and technical terms from the employer job description.")
            st.info("**Step 4: Optimize Portfolio & Re-Run ATS Audit**\n\nEnsure valid GitHub repository links and LinkedIn are in your header, then re-upload to confirm >90% ATS readiness.")

        st.markdown("---")
        
        # 11. DOWNLOAD COMPLETE REPORT
        st.subheader("📄 Export Analysis Report")
        st.write("Generate a formatted summary report containing all score breakdowns, skills gap matrices, ATS evaluations, and improvement recommendations.")
        st.download_button(
            label="📥 Download Full Analysis Report (.md)",
            data=report_content,
            file_name=f"resume_analysis_{res.get('target_role').lower().replace(' ', '_')}.md",
            mime="text/markdown",
            key="btn_download_report_bottom"
        )


# ==============================================================================
# TAB 2: MULTI-ROLE COMPARISON (Preserved & Enhanced)
# ==============================================================================
with tab_compare:
    st.header("Multi-Role Fit Comparison")
    st.write("Compare your resume simultaneously against two distinct target roles or job descriptions to identify the best alignment.")
    
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        role1_name = st.selectbox("Role 1 Title:", [
            "Software Engineer", "Python Developer", "Full Stack Developer", "Data Analyst", "AI/ML Engineer", "DevOps Engineer", "Cloud Engineer"
        ], index=0, key="mr_role_1")
        role1_jd = st.text_area("Role 1 Job Description / Requirements:", height=120, placeholder="Paste JD or leave empty for default role benchmarks...", key="mr_jd_1")

    with col_r2:
        role2_name = st.selectbox("Role 2 Title:", [
            "Data Analyst", "Software Engineer", "Python Developer", "Full Stack Developer", "AI/ML Engineer", "DevOps Engineer", "Cloud Engineer"
        ], index=0, key="mr_role_2")
        role2_jd = st.text_area("Role 2 Job Description / Requirements:", height=120, placeholder="Paste JD or leave empty for default role benchmarks...", key="mr_jd_2")

    if st.button("⚡ Compare Both Roles", key="btn_compare_roles", type="primary"):
        if not st.session_state.resume_content:
            st.error("⚠️ Please upload or paste your resume in Step 1 first!")
        else:
            with st.spinner("Evaluating resume alignment across both roles..."):
                comp_data = call_compare_api(
                    st.session_state.resume_content,
                    role1_name,
                    role1_jd,
                    role2_name,
                    role2_jd
                )
                if comp_data:
                    st.session_state.multi_role_result = comp_data

    if "multi_role_result" in st.session_state and st.session_state.multi_role_result:
        comp = st.session_state.multi_role_result
        r1 = comp.get("role_1", {})
        r2 = comp.get("role_2", {})
        
        st.success(f"💡 {comp.get('recommendation', '')}")
        
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.subheader(f"Role 1: {r1.get('name')}")
            st.metric(label="Overall Match", value=f"{r1.get('overall_match', 0)}%")
            st.progress(r1.get('overall_match', 0) / 100)
            
            st.markdown("**Matching Skills:**")
            st.write(", ".join(r1.get("matching_skills", [])) or "None detected")
            
            st.markdown("**Missing Skills:**")
            missing_1 = r1.get("missing_skills", [])
            if missing_1:
                st.write(":red[" + ", ".join(missing_1) + "]")
            else:
                st.write("All core skills matched!")

        with col_res2:
            st.subheader(f"Role 2: {r2.get('name')}")
            st.metric(label="Overall Match", value=f"{r2.get('overall_match', 0)}%")
            st.progress(r2.get('overall_match', 0) / 100)
            
            st.markdown("**Matching Skills:**")
            st.write(", ".join(r2.get("matching_skills", [])) or "None detected")
            
            st.markdown("**Missing Skills:**")
            missing_2 = r2.get("missing_skills", [])
            if missing_2:
                st.write(":red[" + ", ".join(missing_2) + "]")
            else:
                st.write("All core skills matched!")


# ==============================================================================
# TAB 3: RESUME COMPLETENESS CHECK (Preserved & Enhanced)
# ==============================================================================
with tab_completeness:
    st.header("Resume Completeness & Section Verification")
    st.write("Validates that your resume contains all standard sections required by enterprise recruiters and automated ATS screeners.")
    
    if st.session_state.resume_content:
        from analyzer import calculate_completeness_score
        comp_score, details = calculate_completeness_score(st.session_state.resume_content)
        
        c_col1, c_col2 = st.columns([1, 2])
        with c_col1:
            st.markdown(f"""
            <div class="metric-card" style="border-left: 6px solid #6366F1; padding: 20px;">
                <div class="metric-label">Completeness Score</div>
                <div class="metric-value" style="color: #4F46E5;">{comp_score}%</div>
                <div style="font-size: 13px; color: #64748B;">Standard Sections Verified</div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(comp_score / 100)
            
        with c_col2:
            st.subheader("Section Verification Checklist")
            for section, present in details.items():
                if present:
                    st.success(f"✓ {section} — Present & Verified")
                else:
                    st.error(f"✕ {section} — Missing or Incomplete (Recommendation: Add this section)")
                    
        st.markdown("---")
        st.markdown("#### 💡 Resume Best Practice Tips")
        st.write("""
        1. **Contact Information:** Keep phone, professional email, LinkedIn, and GitHub links at the very top.
        2. **Standard Section Titles:** Use recognizable titles like *Education*, *Technical Skills*, *Projects*, and *Work Experience*.
        3. **Bullet Points:** Start each bullet with an active verb (e.g., *Engineered*, *Optimized*, *Architected*) and quantify achievements.
        4. **File Format:** Always save and upload in text-based PDF or DOCX format.
        """)
    else:
        st.info("Upload or paste a resume in Step 1 to view the completeness report.")