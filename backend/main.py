"""FastAPI Backend Server for AI Resume Assistant."""
import os
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.models import (
    AnalyzeResumeRequest,
    AnalyzeResumeResponse,
    MultiRoleCompareRequest,
    TargetRoleRequirements
)
from backend.parser import extract_resume_text

from backend.gemini_service import (
    run_full_resume_analysis,
    get_configured_gemini_key,
    resolve_role_requirements
)
from backend.role_taxonomy import STANDARD_ROLE_TAXONOMY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend_api")

app = FastAPI(
    title="AI Resume Assistant API",
    description="Backend API for Resume Analysis, Role Matching, and ATS Optimization",
    version="2.0.0"
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow local Streamlit and web frontends
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/api/health")
def health_check() -> Dict[str, Any]:
    """Health check endpoint. Confirms backend status and AI readiness without leaking keys."""
    has_key = bool(get_configured_gemini_key())
    return {
        "status": "online",
        "service": "AI Resume Assistant Backend",
        "gemini_configured": has_key,
        "engine": "Google Gemini 1.5 Flash + Rule Scorer" if has_key else "Deterministic Rule Scorer",
        "version": "2.0.0"
    }


@app.get("/api/target-roles")
def get_target_roles() -> List[str]:
    """Returns the list of pre-configured industry target roles."""
    return list(STANDARD_ROLE_TAXONOMY.keys())


@app.get("/api/target-role-requirements/{role_name}")
def get_role_requirements(role_name: str) -> TargetRoleRequirements:
    """Returns baseline taxonomy requirements for a given target role."""
    return resolve_role_requirements(role_name, jd_text="")


@app.post("/api/extract-text")
async def extract_text_endpoint(file: UploadFile = File(...)):
    """
    Safely validates and extracts text from an uploaded PDF, DOCX, or TXT file.
    Validates file headers, enforces max 5MB limit, and sanitizes output.
    """
    try:
        file_bytes = await file.read()
        filename = file.filename or "uploaded_file"
        extracted_text = extract_resume_text(filename, file_bytes)
        
        return {
            "status": "success",
            "filename": filename,
            "character_count": len(extracted_text),
            "word_count": len(extracted_text.split()),
            "text": extracted_text
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error in /api/extract-text: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process the uploaded file. Please try again.")


@app.post("/api/analyze-resume", response_model=AnalyzeResumeResponse)
def analyze_resume_endpoint(request: AnalyzeResumeRequest):
    """
    Main resume analysis endpoint.
    Processes resume text against target role and optional Job Description.
    Calculates 10 percentage metrics, 3-way skills comparison, ATS analysis, and recommendations.
    """
    if not request.resume_text or len(request.resume_text.strip()) < 30:
        raise HTTPException(
            status_code=400,
            detail="Resume content is too short or empty. Please upload or paste a complete resume."
        )
    
    target_role = (request.target_role or "Software Engineer").strip()
    jd_text = (request.job_description or "").strip()
    
    try:
        response = run_full_resume_analysis(
            resume_text=request.resume_text,
            target_role=target_role,
            job_description=jd_text
        )
        return response
    except Exception as e:
        logger.error(f"Error during resume analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/compare-roles")
def compare_roles_endpoint(request: MultiRoleCompareRequest):
    """
    Preserved & enhanced feature: Compares a single resume against two roles or job descriptions.
    """
    if not request.resume_text or len(request.resume_text.strip()) < 30:
        raise HTTPException(status_code=400, detail="Resume content is required.")
        
    res_1 = run_full_resume_analysis(
        resume_text=request.resume_text,
        target_role=request.role_1_name or "Role 1",
        job_description=request.role_1_jd
    )
    
    res_2 = run_full_resume_analysis(
        resume_text=request.resume_text,
        target_role=request.role_2_name or "Role 2",
        job_description=request.role_2_jd
    )
    
    return {
        "role_1": {
            "name": request.role_1_name,
            "overall_match": res_1.overall_match,
            "scores": res_1.scores,
            "matching_skills": res_1.skills_comparison.matching_skills,
            "missing_skills": res_1.skills_comparison.missing_skills,
            "summary": res_1.resume_quality.strengths[:2]
        },
        "role_2": {
            "name": request.role_2_name,
            "overall_match": res_2.overall_match,
            "scores": res_2.scores,
            "matching_skills": res_2.skills_comparison.matching_skills,
            "missing_skills": res_2.skills_comparison.missing_skills,
            "summary": res_2.resume_quality.strengths[:2]
        },
        "recommendation": (
            f"Your profile aligns stronger with {request.role_1_name} ({res_1.overall_match}%) than {request.role_2_name} ({res_2.overall_match}%)."
            if res_1.overall_match > res_2.overall_match else
            f"Your profile aligns stronger with {request.role_2_name} ({res_2.overall_match}%) than {request.role_1_name} ({res_1.overall_match}%)."
            if res_2.overall_match > res_1.overall_match else
            f"Your profile demonstrates equal alignment ({res_1.overall_match}%) with both roles."
        )
    }


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("BACKEND_HOST", "127.0.0.1")
    port = int(os.getenv("BACKEND_PORT", "8000"))
    uvicorn.run("backend.main:app", host=host, port=port, reload=True)
