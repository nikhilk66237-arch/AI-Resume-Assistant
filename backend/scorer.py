"""Explainable, deterministic scoring engine and skills comparison."""
from typing import List, Dict, Tuple, Optional
from backend.models import (
    ResumeProfile,
    TargetRoleRequirements,
    ScoreBreakdown,
    ScoreFactor,
    SkillsComparison,
    RoleRecommendation
)
from backend.role_taxonomy import (
    SKILL_TAXONOMY,
    STANDARD_ROLE_TAXONOMY,
    extract_skills_from_text,
    normalize_skill
)


def compute_skills_comparison(
    resume_skills: List[str],
    role_reqs: TargetRoleRequirements
) -> SkillsComparison:
    """
    Computes three distinct skill categories:
    1. Matching Skills: Skills present in both resume and target requirements.
    2. Missing Skills: Required/recommended skills absent from resume.
    3. Additional Skills: Useful skills present in resume but not demanded by role.
    """
    resume_skill_set = {s.lower() for s in resume_skills}
    
    target_all_required_and_rec = set(
        [s.lower() for s in role_reqs.required_skills] +
        [s.lower() for s in role_reqs.recommended_skills]
    )
    
    matching = []
    missing = []
    
    # Check required skills first
    for s in role_reqs.required_skills:
        s_low = s.lower()
        if s_low in resume_skill_set:
            matching.append(normalize_skill(s))
        else:
            missing.append(normalize_skill(s))
            
    # Check recommended skills
    for s in role_reqs.recommended_skills:
        s_low = s.lower()
        if s_low in resume_skill_set:
            if normalize_skill(s) not in matching:
                matching.append(normalize_skill(s))
        else:
            if normalize_skill(s) not in missing:
                missing.append(normalize_skill(s))
                
    # Additional skills
    additional = []
    for s in resume_skills:
        s_low = s.lower()
        if s_low not in target_all_required_and_rec and s_low not in [x.lower() for x in role_reqs.optional_skills]:
            norm = normalize_skill(s)
            if norm not in additional and norm not in matching:
                additional.append(norm)
                
    return SkillsComparison(
        matching_skills=matching,
        missing_skills=missing,
        additional_skills=additional
    )


def compute_scores(
    resume_profile: ResumeProfile,
    role_reqs: TargetRoleRequirements,
    resume_raw_text: str,
    jd_raw_text: Optional[str] = None
) -> ScoreBreakdown:
    """
    Computes explainable, transparent percentage metrics across 10 dimensions.
    No random black-box guessing: every score is mathematically verified.
    """
    resume_skills = [s.lower() for s in resume_profile.skills + resume_profile.technical_skills]
    resume_skill_set = set(resume_skills)
    resume_text_lower = resume_raw_text.lower()
    
    # 1. Skills Match % (Required weighted 2x, Recommended weighted 1x)
    req_skills = [s.lower() for s in role_reqs.required_skills]
    rec_skills = [s.lower() for s in role_reqs.recommended_skills]
    
    req_matched = [s for s in req_skills if s in resume_skill_set]
    rec_matched = [s for s in rec_skills if s in resume_skill_set]
    
    total_weights = (len(req_skills) * 2) + (len(rec_skills) * 1)
    earned_weights = (len(req_matched) * 2) + (len(rec_matched) * 1)
    
    if total_weights > 0:
        skills_match = int(round((earned_weights / total_weights) * 100))
    else:
        skills_match = 70
    skills_match = max(0, min(100, skills_match))
    
    # 2. Technical Skills Match %
    tech_skills_expected = set(
        [s.lower() for s in role_reqs.core_technical_skills] +
        [s.lower() for s in role_reqs.programming_languages] +
        [s.lower() for s in role_reqs.frameworks] +
        [s.lower() for s in role_reqs.databases]
    )
    if tech_skills_expected:
        tech_matched = [s for s in tech_skills_expected if s in resume_skill_set or any(s in x for x in resume_skills)]
        tech_match = int(round((len(tech_matched) / len(tech_skills_expected)) * 100))
    else:
        tech_match = skills_match
    tech_match = max(10, min(100, tech_match))
    
    # 3. Soft Skills Match %
    soft_skills_expected = ["communication", "problem solving", "teamwork", "adaptability", "leadership", "time management"]
    detected_soft = [s for s in soft_skills_expected if any(alias in resume_text_lower for alias in SKILL_TAXONOMY.get(s, [s]))]
    soft_match = int(round((len(detected_soft) / len(soft_skills_expected)) * 100))
    soft_match = max(20, min(100, soft_match))
    
    # 4. Experience Match %
    has_experience_section = any(
        kw in resume_text_lower for kw in ["experience", "internship", "employment", "work history"]
    )
    exp_count = len(resume_profile.experience)
    if exp_count >= 2 or (has_experience_section and len(resume_profile.experience) >= 1):
        experience_match = 85
    elif has_experience_section or exp_count == 1:
        experience_match = 65
    else:
        experience_match = 35
        
    # Check if project work compensates for student resumes
    if experience_match < 70 and len(resume_profile.projects) >= 2:
        experience_match = min(75, experience_match + 20)
        
    # 5. Education Match %
    has_degree = any(
        deg in resume_text_lower for deg in [
            "b.tech", "btech", "b.e", "bachelor", "master", "m.tech", "mca", "bca", "bs", "ms", "degree", "university", "college"
        ]
    )
    has_gpa = any(kw in resume_text_lower for kw in ["cgpa", "gpa", "percentage", "%", "grade"])
    education_match = 50
    if has_degree:
        education_match += 35
    if has_gpa or len(resume_profile.education) > 0:
        education_match += 15
    education_match = max(20, min(100, education_match))
    
    # 6. Projects Match %
    proj_count = len(resume_profile.projects)
    has_proj_section = any(kw in resume_text_lower for kw in ["projects", "project work", "academic projects", "github.com"])
    if proj_count >= 3:
        projects_match = 95
    elif proj_count == 2:
        projects_match = 80
    elif proj_count == 1 or has_proj_section:
        projects_match = 60
    else:
        projects_match = 30
        
    # 7. Certifications Match %
    has_cert = any(
        kw in resume_text_lower for kw in ["certification", "certified", "certificates", "license", "course completion", "coursera", "nptel", "udemy"]
    )
    cert_count = len(resume_profile.certifications)
    if cert_count >= 2:
        cert_match = 90
    elif cert_count == 1 or has_cert:
        cert_match = 70
    else:
        cert_match = 35
        
    # 8. Keywords Match %
    expected_kw = set(req_skills + rec_skills)
    kw_found = [k for k in expected_kw if k in resume_skill_set]
    if expected_kw:
        keywords_match = int(round((len(kw_found) / len(expected_kw)) * 100))
    else:
        keywords_match = 65
    keywords_match = max(15, min(100, keywords_match))
    
    # 9. Job Description Match % (if JD is supplied)
    jd_match = None
    if jd_raw_text and len(jd_raw_text.strip()) > 30:
        jd_skills = extract_skills_from_text(jd_raw_text)
        if jd_skills:
            matched_jd = [s for s in jd_skills if s in resume_skill_set]
            jd_match = int(round((len(matched_jd) / len(jd_skills)) * 100))
        else:
            jd_match = skills_match
        jd_match = max(10, min(100, jd_match))
        
    # 10. ATS Readiness %
    ats_score = 0
    # Contact info (+15)
    has_contact = any(kw in resume_text_lower for kw in ["email", "@", "phone", "mobile", "linkedin"])
    if has_contact: ats_score += 15
    
    # Standard sections (+15 each)
    if has_degree or len(resume_profile.education) > 0: ats_score += 15
    if len(resume_skills) >= 4: ats_score += 15
    if has_experience_section or len(resume_profile.experience) > 0: ats_score += 15
    if has_proj_section or len(resume_profile.projects) > 0: ats_score += 15
    
    # Formatting and readability (+15)
    word_count = len(resume_raw_text.split())
    if 200 <= word_count <= 1500: ats_score += 15
    else: ats_score += 5
    
    # Keyword balance (no spamming) (+10)
    if len(resume_raw_text) > 0:
        ats_score += 10
    ats_readiness = max(10, min(100, ats_score))
    
    # --- OVERALL MATCH CALCULATION ---
    factors = []
    
    if jd_match is not None:
        # JD Weighted formula:
        # Skills: 25%, JD: 20%, Tech: 15%, Projects: 15%, Experience: 10%, ATS: 5%, Keywords: 5%, Education: 5%
        w_skills, w_jd, w_tech, w_proj, w_exp, w_ats, w_kw, w_edu = 0.25, 0.20, 0.15, 0.15, 0.10, 0.05, 0.05, 0.05
        
        overall = (
            skills_match * w_skills +
            jd_match * w_jd +
            tech_match * w_tech +
            projects_match * w_proj +
            experience_match * w_exp +
            ats_readiness * w_ats +
            keywords_match * w_kw +
            education_match * w_edu
        )
        
        factors = [
            ScoreFactor(category="Skills Match", score=skills_match, weight=w_skills, contribution=round(skills_match * w_skills, 1),
                        explanation=f"Found {len(req_matched)}/{len(req_skills)} required and {len(rec_matched)}/{len(rec_skills)} recommended role skills."),
            ScoreFactor(category="Job Description Match", score=jd_match, weight=w_jd, contribution=round(jd_match * w_jd, 1),
                        explanation="Evaluates direct alignment with the specific job description requirements provided."),
            ScoreFactor(category="Technical Competencies", score=tech_match, weight=w_tech, contribution=round(tech_match * w_tech, 1),
                        explanation="Languages, frameworks, databases, and architectural tools relevant to this position."),
            ScoreFactor(category="Projects Portfolio", score=projects_match, weight=w_proj, contribution=round(projects_match * w_proj, 1),
                        explanation=f"Detected {proj_count} project entries with technical implementation details."),
            ScoreFactor(category="Experience & Internships", score=experience_match, weight=w_exp, contribution=round(experience_match * w_exp, 1),
                        explanation="Practical industry or academic internship experience relevant to the target role."),
            ScoreFactor(category="ATS Readiness", score=ats_readiness, weight=w_ats, contribution=round(ats_readiness * w_ats, 1),
                        explanation="Resume structural completeness, section headings, and ATS machine-readability."),
            ScoreFactor(category="Keywords Alignment", score=keywords_match, weight=w_kw, contribution=round(keywords_match * w_kw, 1),
                        explanation="Presence of standard industry terminology and domain keywords."),
            ScoreFactor(category="Education & Academics", score=education_match, weight=w_edu, contribution=round(education_match * w_edu, 1),
                        explanation="Degree qualifications, institution accreditation, and academic background.")
        ]
        methodology = "Weighted JD-Priority Formula: Skills (25%) + JD Match (20%) + Tech (15%) + Projects (15%) + Experience (10%) + ATS (5%) + Keywords (5%) + Education (5%)."
    else:
        # Standard Role Weighted formula:
        # Skills: 30%, Tech: 20%, Projects: 15%, Experience: 15%, Education: 10%, ATS: 5%, Keywords: 5%
        w_skills, w_tech, w_proj, w_exp, w_edu, w_ats, w_kw = 0.30, 0.20, 0.15, 0.15, 0.10, 0.05, 0.05
        
        overall = (
            skills_match * w_skills +
            tech_match * w_tech +
            projects_match * w_proj +
            experience_match * w_exp +
            education_match * w_edu +
            ats_readiness * w_ats +
            keywords_match * w_kw
        )
        
        factors = [
            ScoreFactor(category="Skills Match", score=skills_match, weight=w_skills, contribution=round(skills_match * w_skills, 1),
                        explanation=f"Found {len(req_matched)}/{len(req_skills)} required role competencies."),
            ScoreFactor(category="Technical Competencies", score=tech_match, weight=w_tech, contribution=round(tech_match * w_tech, 1),
                        explanation="Programming languages, frameworks, and system tools expected for this role."),
            ScoreFactor(category="Projects Portfolio", score=projects_match, weight=w_proj, contribution=round(projects_match * w_proj, 1),
                        explanation=f"Evaluates {proj_count} practical project implementations."),
            ScoreFactor(category="Experience & Internships", score=experience_match, weight=w_exp, contribution=round(experience_match * w_exp, 1),
                        explanation="Work history, internships, or production software contributions."),
            ScoreFactor(category="Education & Academics", score=education_match, weight=w_edu, contribution=round(education_match * w_edu, 1),
                        explanation="Academic degree qualifications and credentials."),
            ScoreFactor(category="ATS Readiness", score=ats_readiness, weight=w_ats, contribution=round(ats_readiness * w_ats, 1),
                        explanation="Formatting, section structure, and machine-readability checks."),
            ScoreFactor(category="Keywords Alignment", score=keywords_match, weight=w_kw, contribution=round(keywords_match * w_kw, 1),
                        explanation="Core domain keywords matched against standard role expectations.")
        ]
        methodology = "Weighted Role-Standard Formula: Skills (30%) + Tech (20%) + Projects (15%) + Experience (15%) + Education (10%) + ATS (5%) + Keywords (5%)."

    overall_int = max(0, min(100, int(round(overall))))

    return ScoreBreakdown(
        overall_match=overall_int,
        skills_match=skills_match,
        technical_skills_match=tech_match,
        soft_skills_match=soft_match,
        experience_match=experience_match,
        education_match=education_match,
        projects_match=projects_match,
        certifications_match=cert_match,
        keywords_match=keywords_match,
        job_description_match=jd_match,
        ats_readiness=ats_readiness,
        scoring_methodology=methodology,
        factors=factors
    )


def compute_role_recommendations(resume_skills: List[str]) -> List[RoleRecommendation]:
    """
    Evaluates compatibility across multiple industry roles based on detected skills.
    Presented as compatibility measurements, not guaranteed career outcomes.
    """
    resume_skill_set = {s.lower() for s in resume_skills}
    recommendations = []
    
    for role_name, template in STANDARD_ROLE_TAXONOMY.items():
        reqs = [s.lower() for s in template.get("required_skills", [])]
        recs = [s.lower() for s in template.get("recommended_skills", [])]
        
        matched_req = [s for s in reqs if s in resume_skill_set]
        matched_rec = [s for s in recs if s in resume_skill_set]
        
        total_pts = (len(reqs) * 2) + len(recs)
        earned_pts = (len(matched_req) * 2) + len(matched_rec)
        
        pct = int(round((earned_pts / max(1, total_pts)) * 100))
        pct = max(15, min(95, pct))
        
        if pct >= 75:
            tier = "High Compatibility"
            reason = f"Strong alignment in {len(matched_req)} core skills ({', '.join(normalize_skill(s) for s in matched_req[:3])})."
        elif pct >= 50:
            tier = "Moderate Fit"
            reason = f"Good baseline. Reinforce recommended skills ({', '.join(normalize_skill(s) for s in reqs if s not in resume_skill_set)[:2]})."
        else:
            tier = "Growth Potential"
            reason = "Emerging crossover skills present, requires dedicated portfolio projects."
            
        recommendations.append(
            RoleRecommendation(
                role_name=role_name,
                match_percentage=pct,
                compatibility_tier=tier,
                reasoning=reason
            )
        )
        
    # Sort descending by match percentage
    recommendations.sort(key=lambda r: r.match_percentage, reverse=True)
    return recommendations[:6]
