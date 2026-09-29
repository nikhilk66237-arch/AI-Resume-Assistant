"""Pydantic schemas and data models for Resume Analyzer."""
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class ContactInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio_or_website: Optional[str] = None
    location: Optional[str] = None


class EducationItem(BaseModel):
    degree: str
    institution: Optional[str] = None
    year: Optional[str] = None
    gpa: Optional[str] = None


class ProjectItem(BaseModel):
    title: str
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)


class ExperienceItem(BaseModel):
    role: str
    organization: Optional[str] = None
    duration: Optional[str] = None
    highlights: List[str] = Field(default_factory=list)


class ResumeProfile(BaseModel):
    name: Optional[str] = "Applicant"
    contact_info: ContactInfo = Field(default_factory=ContactInfo)
    summary: Optional[str] = None
    education: List[EducationItem] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    technical_skills: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    experience: List[ExperienceItem] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    tools_and_technologies: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)


class TargetRoleRequirements(BaseModel):

    target_role: str
    jd_provided: bool = False
    
    # Requirement Tiering
    required_skills: List[str] = Field(default_factory=list)
    recommended_skills: List[str] = Field(default_factory=list)
    optional_skills: List[str] = Field(default_factory=list)
    
    # Category Breakdowns
    core_technical_skills: List[str] = Field(default_factory=list)
    programming_languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    cloud_devops_tools: List[str] = Field(default_factory=list)
    ai_ml_tools: List[str] = Field(default_factory=list)
    data_analytics_tools: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
    education_expectation: str = "Bachelor's degree in Computer Science, IT, or related field"
    experience_expectation: str = "Entry to mid level (internship or 0-2+ years relevant experience)"
    recommended_certifications: List[str] = Field(default_factory=list)
    recommended_projects: List[str] = Field(default_factory=list)
    other_recommended_skills: List[str] = Field(default_factory=list)

    # Source Attribution
    jd_explicit_requirements: List[str] = Field(default_factory=list)
    general_role_expectations: List[str] = Field(default_factory=list)
    inferred_skills: List[str] = Field(default_factory=list)


class ScoreFactor(BaseModel):
    category: str
    score: int
    weight: float
    contribution: float
    explanation: str


class ScoreBreakdown(BaseModel):
    overall_match: int
    skills_match: int
    technical_skills_match: int
    soft_skills_match: int
    experience_match: int
    education_match: int
    projects_match: int
    certifications_match: int
    keywords_match: int
    job_description_match: Optional[int] = None
    ats_readiness: int
    
    scoring_methodology: str
    factors: List[ScoreFactor] = Field(default_factory=list)


class SkillsComparison(BaseModel):
    matching_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    additional_skills: List[str] = Field(default_factory=list)


class ATSAnalysis(BaseModel):
    ats_score: int
    strengths: List[str] = Field(default_factory=list)
    problems: List[str] = Field(default_factory=list)
    improvements: List[str] = Field(default_factory=list)
    checklist: Dict[str, bool] = Field(default_factory=dict)
    readability_notes: str = ""


class ActionableSuggestion(BaseModel):
    title: str
    detail: str
    priority: str  # HIGH, MEDIUM, LOW
    category: str


class ResumeQualityAnalysis(BaseModel):
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    potential_red_flags: List[str] = Field(default_factory=list)
    improvement_priority: str  # HIGH, MEDIUM, LOW
    actionable_suggestions: List[ActionableSuggestion] = Field(default_factory=list)


class RoleRecommendation(BaseModel):
    role_name: str
    match_percentage: int
    compatibility_tier: str  # High Compatibility, Moderate Fit, Growth Potential
    reasoning: str


class AnalyzeResumeRequest(BaseModel):
    resume_text: str
    target_role: str = "Software Engineer"
    job_description: Optional[str] = ""


class MultiRoleCompareRequest(BaseModel):
    resume_text: str
    role_1_name: str = "Role 1"
    role_1_jd: str = ""
    role_2_name: str = "Role 2"
    role_2_jd: str = ""


class JobDescriptionAnalysis(BaseModel):
    jd_provided: bool = False
    jd_match_score: Optional[int] = None
    matched_jd_requirements: List[str] = Field(default_factory=list)
    missing_jd_requirements: List[str] = Field(default_factory=list)
    important_jd_keywords: List[str] = Field(default_factory=list)
    recommended_resume_changes: List[str] = Field(default_factory=list)


class AnalyzeResumeResponse(BaseModel):
    target_role: str
    job_description_provided: bool
    overall_match: int
    match_level: str
    
    scores: ScoreBreakdown
    skills_comparison: SkillsComparison
    target_role_requirements: TargetRoleRequirements
    resume_profile: ResumeProfile
    ats_analysis: ATSAnalysis
    resume_quality: ResumeQualityAnalysis
    role_recommendations: List[RoleRecommendation]
    jd_analysis: Optional[JobDescriptionAnalysis] = None
    
    weak_descriptions: List[str] = Field(default_factory=list)
    improvement_suggestions: List[str] = Field(default_factory=list)
    improved_resume_points: List[str] = Field(default_factory=list)
    
    engine_used: str  # "gemini-ai" or "deterministic-rules"
    disclaimer: str = (
        "Role compatibility and percentage scores are analytical benchmarks "
        "calculated from detected resume text vs role competencies, not guaranteed career outcomes."
    )

