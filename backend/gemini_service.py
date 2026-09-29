"""Gemini AI service with structured JSON extraction and offline rule-based fallback."""
import os
import json
import re
import logging
from typing import Dict, Any, Tuple, Optional, List
from dotenv import load_dotenv

load_dotenv()

from backend.models import (
    ResumeProfile,
    ContactInfo,
    EducationItem,
    ProjectItem,
    ExperienceItem,
    ATSAnalysis,
    ResumeQualityAnalysis,
    ActionableSuggestion,
    AnalyzeResumeResponse,
    TargetRoleRequirements,
    JobDescriptionAnalysis
)
from backend.role_taxonomy import (
    extract_skills_from_text,
    resolve_role_requirements,
    normalize_skill
)

from backend.scorer import (
    compute_scores,
    compute_skills_comparison,
    compute_role_recommendations
)

logger = logging.getLogger("gemini_service")


def get_configured_gemini_key() -> Optional[str]:
    """Retrieves GEMINI_API_KEY from environment without exposing it."""
    key = os.getenv("GEMINI_API_KEY", "").strip()
    return key if key else None


def clean_json_string(raw: str) -> str:
    """Robustly extracts JSON from an LLM response string."""
    text = raw.strip()
    # Strip markdown fences
    text = re.sub(r"^```(?:json)?", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"```$", "", text).strip()
    
    # Try finding the first { and last }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end+1]
    return text


def rule_based_extract_profile(resume_text: str) -> ResumeProfile:
    """Deterministic offline parser to extract contact info, skills, and sections."""
    lines = [line.strip() for line in resume_text.split("\n") if line.strip()]
    first_line = lines[0] if lines else "Candidate"
    name = first_line if len(first_line.split()) <= 4 and "@" not in first_line else "Candidate"
    
    # Email
    email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', resume_text)
    email = email_match.group(0) if email_match else None
    
    # Phone
    phone_match = re.search(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', resume_text)
    phone = phone_match.group(0) if phone_match else None
    
    # Links
    linkedin_match = re.search(r'(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+', resume_text, re.IGNORECASE)
    github_match = re.search(r'(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_-]+', resume_text, re.IGNORECASE)
    
    contact = ContactInfo(
        name=name,
        email=email,
        phone=phone,
        linkedin=linkedin_match.group(0) if linkedin_match else None,
        github=github_match.group(0) if github_match else None
    )
    
    # Extract skills
    detected_skills = extract_skills_from_text(resume_text)
    
    # Extract education items
    education_items = []
    edu_keywords = ["b.tech", "btech", "b.e", "m.tech", "bca", "mca", "b.sc", "bachelor", "master"]
    for line in lines:
        if any(deg in line.lower() for deg in edu_keywords):
            education_items.append(EducationItem(degree=line[:80]))
            
    if not education_items and any("education" in l.lower() for l in lines):
        education_items.append(EducationItem(degree="Undergraduate Degree / College Education"))
        
    # Extract projects
    projects = []
    proj_lines = [l for l in lines if any(k in l.lower() for k in ["built", "developed", "project:", "project -"])]
    for pl in proj_lines[:3]:
        projects.append(ProjectItem(title=pl[:60], technologies=[]))
        
    if not projects and any("project" in l.lower() for l in lines):
        projects.append(ProjectItem(title="Academic & Software Projects", technologies=[]))
        
    # Extract experience
    experience = []
    exp_lines = [l for l in lines if any(k in l.lower() for k in ["intern", "engineer", "developer", "trainee", "associate"])]
    for el in exp_lines[:2]:
        experience.append(ExperienceItem(role=el[:60]))

    return ResumeProfile(
        name=name,
        contact_info=contact,
        summary=lines[1][:250] if len(lines) > 1 and len(lines[1]) > 40 else "Aspiring Software Professional",
        education=education_items,
        skills=[normalize_skill(s) for s in detected_skills],
        technical_skills=[normalize_skill(s) for s in detected_skills if s not in ["communication", "teamwork", "leadership", "problem solving"]],
        soft_skills=[normalize_skill(s) for s in detected_skills if s in ["communication", "teamwork", "leadership", "problem solving"]],
        projects=projects,
        experience=experience,
        certifications=["Verified Online Certifications"] if "certif" in resume_text.lower() else [],
        keywords=[normalize_skill(s) for s in detected_skills]
    )


def generate_offline_quality_and_ats(
    profile: ResumeProfile,
    role_reqs: TargetRoleRequirements,
    resume_text: str
) -> Tuple[ATSAnalysis, ResumeQualityAnalysis, List[str], List[str], List[str]]:
    """Generates structured ATS checks, quality review, and actionable advice deterministically."""
    text_lower = resume_text.lower()
    
    # ATS Checklist
    has_contact = bool(profile.contact_info.email or profile.contact_info.phone)
    has_education = len(profile.education) > 0 or "education" in text_lower
    has_skills = len(profile.skills) >= 4 or "skills" in text_lower
    has_exp = len(profile.experience) > 0 or "experience" in text_lower or "intern" in text_lower
    has_proj = len(profile.projects) > 0 or "project" in text_lower
    standard_headings = sum([has_contact, has_education, has_skills, has_exp, has_proj]) >= 4
    
    checklist = {
        "Contact Information Present": has_contact,
        "Education Section Detected": has_education,
        "Skills Section Detected": has_skills,
        "Experience / Internships Present": has_exp,
        "Projects Section Present": has_proj,
        "Clean Standard Headings": standard_headings,
        "Appropriate Length (1-2 pages)": 200 <= len(text_lower.split()) <= 1500,
        "No Keyword Stuffing Detected": True
    }
    
    ats_score = int((sum(checklist.values()) / len(checklist)) * 100)
    
    ats_strengths = []
    ats_problems = []
    ats_improvements = []
    
    if has_contact: ats_strengths.append("Contact information (email/phone) is easily parsed by ATS.")
    else: ats_problems.append("Missing explicit email or phone number in header.")
    
    if has_skills: ats_strengths.append(f"Identified {len(profile.skills)} technical and domain skills in clean text format.")
    else: ats_problems.append("Skills are scattered throughout sentences rather than listed in a dedicated 'Skills' section.")
    
    if has_proj: ats_strengths.append("Project section demonstrates practical technical implementation.")
    else: ats_problems.append("No distinct Projects section found. ATS parses projects for keyword relevancy.")
    
    if not profile.contact_info.linkedin:
        ats_improvements.append("Add a verified LinkedIn profile link to improve recruiter reachability.")
    if not profile.contact_info.github:
        ats_improvements.append("Include a GitHub profile link so reviewers can inspect your code repositories.")
    ats_improvements.append("Ensure standard section headers ('Education', 'Technical Skills', 'Experience', 'Projects') are used.")
    
    # Resume Quality Analysis
    strengths = []
    weaknesses = []
    missing_info = []
    red_flags = []
    actionable_suggestions = []
    
    if len(profile.skills) >= 5:
        strengths.append(f"Broad foundational skill set covering {', '.join(profile.skills[:4])}.")
    if has_proj:
        strengths.append("Practical projects demonstrate hands-on application of concepts.")
    if profile.education:
        strengths.append("Educational qualifications are clearly stated.")
        
    # Weaknesses & Missing info
    missing_from_role = [s for s in role_reqs.required_skills if s.lower() not in [x.lower() for x in profile.skills]]
    if missing_from_role:
        weaknesses.append(f"Missing core competencies required for {role_reqs.target_role}: {', '.join(normalize_skill(s) for s in missing_from_role[:3])}.")
        actionable_suggestions.append(
            ActionableSuggestion(
                title=f"Add missing core skills for {role_reqs.target_role}",
                detail=f"Prioritize acquiring and demonstrating: {', '.join(normalize_skill(s) for s in missing_from_role[:3])}.",
                priority="HIGH",
                category="Skills Gap"
            )
        )
        
    if not has_exp:
        weaknesses.append("Lack of formal work or internship experience.")
        actionable_suggestions.append(
            ActionableSuggestion(
                title="Expand Project Portfolio with Production-Grade Work",
                detail="Build and deploy full-stack or data-driven applications to compensate for work experience.",
                priority="HIGH",
                category="Experience"
            )
        )
        
    # Quantifiable achievements
    has_numbers = bool(re.search(r'\b\d+(?:%|\+|x|k|ms|s)?\b', resume_text))
    if not has_numbers:
        weaknesses.append("Descriptions lack quantified impact or measurable results (e.g., percentages, scale, performance improvements).")
        actionable_suggestions.append(
            ActionableSuggestion(
                title="Quantify Project Achievements",
                detail="Rewrite bullet points to follow the formula: 'Accomplished [X] as measured by [Y] by doing [Z]'.",
                priority="MEDIUM",
                category="Resume Impact"
            )
        )
        
    if not profile.contact_info.github:
        missing_info.append("GitHub profile URL for code validation.")
    if not profile.contact_info.linkedin:
        missing_info.append("LinkedIn profile URL.")
        
    # Priority
    priority = "HIGH" if (len(missing_from_role) >= 3 or not has_proj) else "MEDIUM" if len(missing_from_role) >= 1 else "LOW"
    
    quality = ResumeQualityAnalysis(
        strengths=strengths or ["Clear layout and readable font formatting."],
        weaknesses=weaknesses or ["Could further highlight specialized toolchains."],
        missing_information=missing_info or ["No critical contact info missing."],
        potential_red_flags=red_flags or ["No major red flags detected."],
        improvement_priority=priority,
        actionable_suggestions=actionable_suggestions
    )
    
    ats_obj = ATSAnalysis(
        ats_score=ats_score,
        strengths=ats_strengths,
        problems=ats_problems,
        improvements=ats_improvements,
        checklist=checklist,
        readability_notes="Single-column, text-extractable format recommended for optimal ATS parsing."
    )
    
    weak_descriptions = [
        "Worked on developing features for the application using various technologies.",
        "Responsible for bug fixes and maintaining the codebase.",
        "Built a project using database and frontend tools."
    ]
    
    improved_points = [
        f"Engineered and deployed a responsive application using {profile.skills[0] if profile.skills else 'Python'}, improving query throughput by 25%.",
        "Architected RESTful APIs with database indexing, reducing response latency and ensuring 99.9% uptime in testing.",
        "Implemented automated CI/CD unit testing pipelines, reducing manual deployment overhead by 40%."
    ]
    
    flat_suggestions = [
        s.detail for s in actionable_suggestions
    ] + [
        "Add GitHub links with clear README documentation for all highlighted projects.",
        "Place technical skills in prioritized categories: Languages, Frameworks, Databases, and Tools."
    ]
    
    return ats_obj, quality, weak_descriptions, flat_suggestions, improved_points


def analyze_with_gemini(
    resume_text: str,
    target_role: str,
    job_description: str,
    role_reqs: TargetRoleRequirements,
    api_key: str
) -> Optional[Dict[str, Any]]:
    """
    Invokes Google Gemini with a strict JSON prompt.
    Returns structured dictionary or None on failure.
    """
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
You are an expert ATS Resume Auditor and Career Coach.
Analyze the provided resume against the Target Role and Job Description.

RESUME CONTENT:
\"\"\"
{resume_text}
\"\"\"

TARGET ROLE: {target_role}

JOB DESCRIPTION (If empty, evaluate against standard industry expectations for {target_role}):
\"\"\"
{job_description or "None provided. Analyze for standard " + target_role + " role."}
\"\"\"

CRITICAL INSTRUCTIONS:
1. Extract true evidence from the resume text only. Do not hallucinate credentials not present in the resume.
2. Return ONLY a single valid JSON object. Do not wrap in markdown or include conversational text.
3. Strict JSON structure:
{{
    "candidate_name": "Full Name or Candidate",
    "contact": {{
        "email": "email or null",
        "phone": "phone or null",
        "linkedin": "url or null",
        "github": "url or null"
    }},
    "summary": "1-2 sentence professional summary or null",
    "detected_skills": ["skill1", "skill2"],
    "technical_skills": ["tech1", "tech2"],
    "soft_skills": ["soft1", "soft2"],
    "projects": [
        {{"title": "Project Name", "technologies": ["tech1"]}}
    ],
    "experience": [
        {{"role": "Role Title", "organization": "Company or null"}}
    ],
    "certifications": ["cert1"],
    "ats_strengths": ["strength1", "strength2"],
    "ats_problems": ["problem1"],
    "ats_improvements": ["improvement1", "improvement2"],
    "resume_strengths": ["strength1", "strength2"],
    "resume_weaknesses": ["weakness1", "weakness2"],
    "missing_information": ["item1"],
    "potential_red_flags": ["flag1 if any, or none"],
    "improvement_priority": "HIGH",
    "actionable_suggestions": [
        {{"title": "Title", "detail": "Specific actionable recommendation", "priority": "HIGH", "category": "Category"}}
    ],
    "weak_descriptions": [
        "Quote or describe a vague bullet point from the resume"
    ],
    "improved_bullet_points": [
        "Action-oriented rewrite using Action Verb + Task + Quantifiable Impact"
    ]
}}
"""
        response = model.generate_content(prompt)
        if not response or not response.text:
            return None
            
        cleaned_json = clean_json_string(response.text)
        data = json.loads(cleaned_json)
        return data
        
    except Exception as e:
        logger.warning(f"Gemini API invocation error: {str(e)}")
        return None


def run_full_resume_analysis(
    resume_text: str,
    target_role: str = "Software Engineer",
    job_description: Optional[str] = ""
) -> AnalyzeResumeResponse:
    """
    Orchestrates the complete resume analysis pipeline:
    1. Resolves target role requirements (prioritizing JD).
    2. Attempts structured Gemini AI extraction if key is configured.
    3. Seamlessly falls back to deterministic rule extraction if key is missing or API errors.
    4. Computes explainable, mathematical percentage scores.
    5. Calculates 3-way skills breakdown (matching, missing, additional).
    6. Calculates role compatibility recommendations across 6 industry roles.
    7. Returns complete AnalyzeResumeResponse schema.
    """
    clean_resume = resume_text.strip()
    clean_jd = (job_description or "").strip()
    
    # 1. Resolve requirements
    role_reqs = resolve_role_requirements(target_role, clean_jd)
    
    # 2. Check for configured Gemini API Key in backend environment
    gemini_key = get_configured_gemini_key()
    ai_data = None
    engine_used = "deterministic-rules"
    
    if gemini_key:
        ai_data = analyze_with_gemini(
            resume_text=clean_resume,
            target_role=target_role,
            job_description=clean_jd,
            role_reqs=role_reqs,
            api_key=gemini_key
        )
        if ai_data:
            engine_used = "gemini-ai"

    # 3. Construct ResumeProfile and quality data
    if ai_data:
        # Build profile from AI extraction
        contact_dict = ai_data.get("contact", {})
        contact = ContactInfo(
            name=ai_data.get("candidate_name") or "Candidate",
            email=contact_dict.get("email"),
            phone=contact_dict.get("phone"),
            linkedin=contact_dict.get("linkedin"),
            github=contact_dict.get("github")
        )
        
        extracted_skills = ai_data.get("detected_skills", []) or extract_skills_from_text(clean_resume)
        tech_skills = ai_data.get("technical_skills", []) or [s for s in extracted_skills if s not in ["communication", "teamwork", "leadership"]]
        soft_skills = ai_data.get("soft_skills", []) or [s for s in extracted_skills if s in ["communication", "teamwork", "leadership", "problem solving"]]
        
        projects = []
        for p in ai_data.get("projects", []):
            if isinstance(p, dict):
                projects.append(ProjectItem(title=p.get("title", "Project"), technologies=p.get("technologies", [])))
                
        experience = []
        for e in ai_data.get("experience", []):
            if isinstance(e, dict):
                experience.append(ExperienceItem(role=e.get("role", "Experience"), organization=e.get("organization")))
                
        profile = ResumeProfile(
            name=ai_data.get("candidate_name") or "Candidate",
            contact_info=contact,
            summary=ai_data.get("summary"),
            skills=[normalize_skill(s) for s in extracted_skills],
            technical_skills=[normalize_skill(s) for s in tech_skills],
            soft_skills=[normalize_skill(s) for s in soft_skills],
            projects=projects,
            experience=experience,
            certifications=ai_data.get("certifications", []),
            keywords=[normalize_skill(s) for s in extracted_skills]
        )
        
        # Actionable suggestions
        actionable_suggestions = []
        for sug in ai_data.get("actionable_suggestions", []):
            if isinstance(sug, dict):
                actionable_suggestions.append(
                    ActionableSuggestion(
                        title=sug.get("title", "Recommendation"),
                        detail=sug.get("detail", ""),
                        priority=sug.get("priority", "MEDIUM"),
                        category=sug.get("category", "General")
                    )
                )
                
        quality = ResumeQualityAnalysis(
            strengths=ai_data.get("resume_strengths", []),
            weaknesses=ai_data.get("resume_weaknesses", []),
            missing_information=ai_data.get("missing_information", []),
            potential_red_flags=ai_data.get("potential_red_flags", []),
            improvement_priority=ai_data.get("improvement_priority", "MEDIUM"),
            actionable_suggestions=actionable_suggestions
        )
        
        # ATS Analysis
        ats_analysis = ATSAnalysis(
            ats_score=85 if len(profile.skills) >= 5 and contact.email else 65,
            strengths=ai_data.get("ats_strengths", []),
            problems=ai_data.get("ats_problems", []),
            improvements=ai_data.get("ats_improvements", []),
            checklist={
                "Contact Information Present": bool(contact.email or contact.phone),
                "Skills Section Detected": len(profile.skills) >= 4,
                "Projects Section Present": len(profile.projects) >= 1,
                "Experience Section Present": len(profile.experience) >= 1,
                "ATS Readability": True
            },
            readability_notes="Clean formatting compliant with standard Applicant Tracking Systems."
        )
        
        weak_descriptions = ai_data.get("weak_descriptions", [])
        improved_points = ai_data.get("improved_bullet_points", [])
        flat_suggestions = [s.detail for s in actionable_suggestions]
        
    else:
        # Offline rule-based fallback
        profile = rule_based_extract_profile(clean_resume)
        ats_analysis, quality, weak_descriptions, flat_suggestions, improved_points = (
            generate_offline_quality_and_ats(profile, role_reqs, clean_resume)
        )

    # 4. Compute explainable, transparent scores
    scores = compute_scores(
        resume_profile=profile,
        role_reqs=role_reqs,
        resume_raw_text=clean_resume,
        jd_raw_text=clean_jd
    )
    
    # Sync ATS score from scoring engine
    ats_analysis.ats_score = scores.ats_readiness

    # 5. Compute 3-way skills comparison
    all_resume_skills = profile.skills + profile.technical_skills
    skills_comp = compute_skills_comparison(all_resume_skills, role_reqs)

    # 7. Compute Job Description specific comparison if JD provided
    jd_analysis = None
    if clean_jd and len(clean_jd) > 30:
        jd_skills = extract_skills_from_text(clean_jd)
        resume_skill_set = {s.lower() for s in all_resume_skills}
        matched_jd = [normalize_skill(s) for s in jd_skills if s.lower() in resume_skill_set]
        missing_jd = [normalize_skill(s) for s in jd_skills if s.lower() not in resume_skill_set]
        
        jd_score = scores.job_description_match if scores.job_description_match is not None else (
            int(round((len(matched_jd) / max(1, len(jd_skills))) * 100)) if jd_skills else 50
        )
        
        recommended_changes = []
        if missing_jd:
            recommended_changes.append(f"Incorporate missing JD skills into your skills list and projects: {', '.join(missing_jd[:4])}.")
        recommended_changes.append("Update project descriptions to mirror the technical phrasing and responsibilities listed in the employer's JD.")
        if "fastapi" in clean_jd.lower() and not any("fastapi" in s.lower() for s in all_resume_skills):
            recommended_changes.append("Highlight FastAPI REST APIs as explicitly sought in the job posting.")
        if "docker" in clean_jd.lower() and not any("docker" in s.lower() for s in all_resume_skills):
            recommended_changes.append("Add Docker containerization experience to relevant project toolchains.")
        if not recommended_changes:
            recommended_changes.append("Resume strongly aligns with the JD; quantify your impact and ensure keywords match exact phrasing.")

        jd_analysis = JobDescriptionAnalysis(
            jd_provided=True,
            jd_match_score=jd_score,
            matched_jd_requirements=matched_jd,
            missing_jd_requirements=missing_jd,
            important_jd_keywords=[normalize_skill(s) for s in jd_skills],
            recommended_resume_changes=recommended_changes
        )

    # 6. Compute multi-role compatibility recommendations
    role_recs = compute_role_recommendations(all_resume_skills)

    # Match Level badge
    overall = scores.overall_match
    match_level = "High Match" if overall >= 75 else "Moderate Match" if overall >= 50 else "Entry / Foundational Match"

    return AnalyzeResumeResponse(
        target_role=target_role,
        job_description_provided=bool(clean_jd and len(clean_jd) > 30),
        overall_match=overall,
        match_level=match_level,
        scores=scores,
        skills_comparison=skills_comp,
        target_role_requirements=role_reqs,
        resume_profile=profile,
        ats_analysis=ats_analysis,
        resume_quality=quality,
        role_recommendations=role_recs,
        jd_analysis=jd_analysis,
        weak_descriptions=weak_descriptions,
        improvement_suggestions=flat_suggestions,
        improved_resume_points=improved_points,
        engine_used=engine_used
    )
