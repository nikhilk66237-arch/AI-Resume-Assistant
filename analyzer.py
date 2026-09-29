"""Legacy compatibility bridge and core analyzer interface."""
import os
from typing import Dict, Any, Tuple
from dotenv import load_dotenv

load_dotenv()

from backend.parser import extract_resume_text
from backend.gemini_service import run_full_resume_analysis
from backend.role_taxonomy import SKILL_TAXONOMY



# Backward-compatible skill aliases
SKILL_ALIASES = SKILL_TAXONOMY


def extract_text_from_pdf(uploaded_file) -> str:
    """Safely extracts text from an uploaded PDF (or file-like buffer)."""
    try:
        if hasattr(uploaded_file, "read"):
            data = uploaded_file.read()
            # Reset seek position if seekable
            if hasattr(uploaded_file, "seek"):
                uploaded_file.seek(0)
            return extract_resume_text("resume.pdf", data)
        elif isinstance(uploaded_file, (str, bytes)):
            if isinstance(uploaded_file, str):
                with open(uploaded_file, "rb") as f:
                    data = f.read()
            else:
                data = uploaded_file
            return extract_resume_text("resume.pdf", data)
        return ""
    except Exception as e:
        return f"Error extracting text: {str(e)}"


def calculate_completeness_score(resume_text: str) -> Tuple[int, Dict[str, bool]]:
    """Checks presence of standard resume sections."""
    text_lower = resume_text.lower()

    sections = {
        "Contact Information": [
            "email", "phone", "linkedin", "github",
            "contact", "mobile"
        ],
        "Education": [
            "education", "degree", "b.tech",
            "college", "university", "cgpa", "gpa"
        ],
        "Skills": [
            "skills", "technical skills", "programming",
            "languages", "frameworks", "tools"
        ],
        "Projects": [
            "projects", "project name", "github",
            "built", "developed"
        ],
        "Experience / Internships": [
            "experience", "internship", "work",
            "role", "position"
        ],
        "Certifications / Achievements": [
            "certifications", "achievements",
            "certificates", "awards"
        ]
    }

    score_details = {}
    total_found = 0

    for section, keywords in sections.items():
        found = any(keyword in text_lower for keyword in keywords)
        score_details[section] = found
        if found:
            total_found += 1

    score_percentage = int((total_found / len(sections)) * 100)
    return score_percentage, score_details


def analyze_without_ai(resume_text: str, job_description: str) -> Dict[str, Any]:
    """Offline rule-based resume analysis for backward compatibility."""
    res = run_full_resume_analysis(
        resume_text=resume_text,
        target_role="Software Engineer",
        job_description=job_description
    )
    return {
        "match_score": res.overall_match,
        "matching_skills": res.skills_comparison.matching_skills,
        "missing_skills": res.skills_comparison.missing_skills,
        "weak_descriptions": res.weak_descriptions,
        "improvement_suggestions": res.improvement_suggestions,
        "improved_resume_points": res.improved_resume_points,
        "full_data": res.model_dump()
    }


def analyze_resume_with_ai(
    resume_text: str,
    job_description: str,
    api_key: str = None
) -> Dict[str, Any]:
    """Main analysis interface for backward-compatible callers."""
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key
        
    res = run_full_resume_analysis(
        resume_text=resume_text,
        target_role="Software Engineer",
        job_description=job_description
    )
    
    return {
        "match_score": res.overall_match,
        "matching_skills": res.skills_comparison.matching_skills,
        "missing_skills": res.skills_comparison.missing_skills,
        "weak_descriptions": res.weak_descriptions,
        "improvement_suggestions": res.improvement_suggestions,
        "improved_resume_points": res.improved_resume_points,
        "full_data": res.model_dump()
    }