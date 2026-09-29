"""Taxonomy of target roles, skill aliases, and requirement resolvers."""
import re
from typing import Dict, List, Set, Optional
from backend.models import TargetRoleRequirements



# Comprehensive skill aliases mapping alias -> canonical skill name
SKILL_TAXONOMY = {
    # Languages
    "python": ["python", "python3", "py"],
    "javascript": ["javascript", "js", "ecmascript"],
    "typescript": ["typescript", "ts"],
    "java": ["java", "core java", "j2ee", "jdk"],
    "c++": ["c++", "cpp"],
    "c#": ["c#", "csharp", ".net c#"],
    "c": ["c programming", "c language"],
    "sql": ["sql", "structured query language"],
    "go": ["golang", "go programming"],
    "rust": ["rust"],
    "r": ["r programming", "r language"],
    "php": ["php"],
    "ruby": ["ruby"],
    "html": ["html", "html5"],
    "css": ["css", "css3"],
    "bash": ["bash", "shell scripting", "powershell", "shell script"],
    
    # Frameworks & Libraries
    "react": ["react", "react.js", "reactjs"],
    "node.js": ["node.js", "nodejs", "node"],
    "express": ["express", "express.js", "expressjs"],
    "django": ["django"],
    "flask": ["flask"],
    "fastapi": ["fastapi"],
    "spring boot": ["spring boot", "springboot", "spring framework"],
    "angular": ["angular", "angularjs"],
    "vue.js": ["vue", "vue.js", "vuejs"],
    "next.js": ["next.js", "nextjs"],
    ".net": [".net", "asp.net", ".net core"],
    
    # Databases
    "postgresql": ["postgresql", "postgres"],
    "mysql": ["mysql"],
    "mongodb": ["mongodb", "mongo"],
    "sqlite": ["sqlite"],
    "redis": ["redis"],
    "oracle": ["oracle db", "oracle sql"],
    "dynamodb": ["dynamodb"],
    
    # Data & AI / ML
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "tensorflow": ["tensorflow", "tf"],
    "pytorch": ["pytorch", "torch"],
    "machine learning": ["machine learning", "ml"],
    "deep learning": ["deep learning", "dl"],
    "nlp": ["nlp", "natural language processing"],
    "computer vision": ["computer vision", "cv", "opencv"],
    "power bi": ["power bi", "powerbi"],
    "tableau": ["tableau"],
    "excel": ["excel", "advanced excel", "spreadsheets"],
    "data analysis": ["data analysis", "data analytics"],
    "data visualization": ["data visualization", "data visualisation"],
    "statistics": ["statistics", "statistical analysis", "probability"],
    
    # Cloud & DevOps
    "aws": ["aws", "amazon web services", "ec2", "s3", "lambda"],
    "azure": ["azure", "microsoft azure"],
    "gcp": ["gcp", "google cloud", "google cloud platform"],
    "docker": ["docker", "containerization"],
    "kubernetes": ["kubernetes", "k8s"],
    "ci/cd": ["ci/cd", "ci cd", "continuous integration", "continuous deployment", "github actions", "jenkins"],
    "git": ["git", "version control"],
    "github": ["github", "gitlab"],
    "linux": ["linux", "ubuntu", "unix"],
    "terraform": ["terraform"],
    
    # Core CS & Architecture
    "dsa": ["dsa", "data structures", "algorithms", "data structures and algorithms"],
    "oop": ["oop", "object oriented programming", "object-oriented programming"],
    "dbms": ["dbms", "database management", "rdbms"],
    "operating systems": ["operating systems", "os concepts"],
    "computer networks": ["computer networks", "networking", "tcp/ip", "http"],
    "system design": ["system design", "distributed systems", "microservices"],
    "rest api": ["rest api", "restful api", "rest apis", "restful web services"],
    "graphql": ["graphql"],
    
    # Cybersecurity
    "cybersecurity": ["cybersecurity", "information security", "infosec", "network security"],
    "penetration testing": ["penetration testing", "pen testing", "ethical hacking"],
    "siem": ["siem", "splunk", "wireshark"],
    "cryptography": ["cryptography", "encryption", "ssl/tls"],
    
    # Soft Skills
    "communication": ["communication", "verbal communication", "written communication", "presentation skills"],
    "problem solving": ["problem solving", "analytical thinking", "critical thinking"],
    "teamwork": ["teamwork", "collaboration", "cross-functional collaboration"],
    "time management": ["time management", "prioritization", "multitasking"],
    "leadership": ["leadership", "mentoring", "team lead"],
    "adaptability": ["adaptability", "flexibility", "quick learner"]
}


# Pre-defined Role Templates based on industry standards
STANDARD_ROLE_TAXONOMY = {
    "Python Developer": {
        "required_skills": ["python", "sql", "git", "oop", "rest api"],
        "recommended_skills": ["django", "flask", "fastapi", "postgresql", "docker", "dsa", "linux"],
        "optional_skills": ["aws", "redis", "ci/cd", "pandas", "pytest"],
        "core_technical_skills": ["Python", "Object-Oriented Programming", "REST APIs", "Debugging"],
        "programming_languages": ["Python", "SQL", "Bash"],
        "frameworks": ["Django", "Flask", "FastAPI"],
        "databases": ["PostgreSQL", "MySQL", "SQLite", "Redis"],
        "cloud_devops_tools": ["Docker", "Git", "GitHub Actions", "Linux"],
        "ai_ml_tools": ["Pandas (optional)", "NumPy (optional)"],
        "data_analytics_tools": ["SQL Querying"],
        "soft_skills": ["Problem Solving", "Code Quality Mindset", "Communication", "Teamwork"],
        "education_expectation": "B.Tech / B.E. / B.S. in Computer Science, IT, or equivalent experience",
        "experience_expectation": "Demonstrated personal/academic projects in Python, or 0-2+ years practical software experience",
        "recommended_certifications": ["PCAP / PCPP (Python Institute)", "AWS Certified Cloud Practitioner"],
        "recommended_projects": ["Full-stack or RESTful API web service with database", "Data automation / ETL or scraping tool"],
        "other_recommended_skills": ["Virtual Environments", "Unit Testing", "API Documentation (Swagger/OpenAPI)"]
    },
    "Full Stack Developer": {
        "required_skills": ["javascript", "react", "node.js", "html", "css", "sql", "git", "rest api"],
        "recommended_skills": ["typescript", "mongodb", "postgresql", "express", "docker", "tailwind"],
        "optional_skills": ["next.js", "aws", "graphql", "ci/cd", "redis"],
        "core_technical_skills": ["Frontend State Management", "Backend API Development", "Responsive UI", "REST APIs"],
        "programming_languages": ["JavaScript", "TypeScript", "HTML5", "CSS3", "SQL"],
        "frameworks": ["React", "Node.js", "Express", "Next.js"],
        "databases": ["MongoDB", "PostgreSQL", "MySQL"],
        "cloud_devops_tools": ["Git", "GitHub", "Docker", "Vercel / Netlify", "AWS basics"],
        "ai_ml_tools": [],
        "data_analytics_tools": [],
        "soft_skills": ["Agile Collaboration", "Problem Solving", "Attention to Detail", "Communication"],
        "education_expectation": "Degree in Computer Science, IT, or demonstrable full-stack portfolio",
        "experience_expectation": "End-to-end web apps deployed live with GitHub repositories",
        "recommended_certifications": ["Meta Front-End / Back-End Professional Certificate", "AWS Certified Developer"],
        "recommended_projects": ["End-to-end SaaS/CRUD application with authentication & database", "E-commerce or real-time collaborative tool"],
        "other_recommended_skills": ["State Management (Redux/Zustand)", "JWT Authentication", "Responsive Design"]
    },
    "Data Analyst": {
        "required_skills": ["sql", "excel", "python", "data analysis", "data visualization"],
        "recommended_skills": ["power bi", "tableau", "pandas", "numpy", "statistics"],
        "optional_skills": ["r", "machine learning", "git", "bigquery"],
        "core_technical_skills": ["Data Cleaning", "Data Exploration", "Metrics & KPI Tracking", "Dashboard Design"],
        "programming_languages": ["SQL", "Python", "R (optional)"],
        "frameworks": ["Pandas", "NumPy", "Matplotlib / Seaborn"],
        "databases": ["PostgreSQL", "MySQL", "Snowflake / BigQuery"],
        "cloud_devops_tools": ["Git"],
        "ai_ml_tools": ["Scikit-learn (basic)"],
        "data_analytics_tools": ["Advanced Excel (VLOOKUP, Pivot Tables)", "Power BI", "Tableau"],
        "soft_skills": ["Analytical Thinking", "Data Storytelling", "Business Acumen", "Written Communication"],
        "education_expectation": "Bachelor's degree in Statistics, Mathematics, Computer Science, Economics, or Business",
        "experience_expectation": "Portfolio of exploratory data analysis, dashboard reports, or internship experience",
        "recommended_certifications": ["Google Data Analytics Professional Certificate", "Microsoft Certified: Power BI Data Analyst (PL-300)"],
        "recommended_projects": ["Interactive Business Dashboard in Power BI/Tableau", "End-to-end Python EDA with actionable business insights"],
        "other_recommended_skills": ["A/B Testing Basics", "ETL Pipelines", "Statistical Hypothesis Testing"]
    },
    "Data Scientist": {
        "required_skills": ["python", "sql", "machine learning", "statistics", "pandas", "numpy", "data analysis"],
        "recommended_skills": ["scikit-learn", "deep learning", "nlp", "data visualization", "git"],
        "optional_skills": ["tensorflow", "pytorch", "docker", "aws", "bigquery", "computer vision"],
        "core_technical_skills": ["Statistical Modeling", "Feature Engineering", "Predictive Analytics", "Hypothesis Testing"],
        "programming_languages": ["Python", "SQL", "R"],
        "frameworks": ["Scikit-Learn", "Pandas", "NumPy", "TensorFlow / PyTorch"],
        "databases": ["PostgreSQL", "MongoDB", "Data Warehouses"],
        "cloud_devops_tools": ["Git", "Docker", "MLflow", "AWS SageMaker (optional)"],
        "ai_ml_tools": ["Scikit-Learn", "XGBoost", "Hugging Face Transformers"],
        "data_analytics_tools": ["Matplotlib", "Seaborn", "Jupyter Notebooks"],
        "soft_skills": ["Scientific Methodology", "Critical Thinking", "Stakeholder Communication"],
        "education_expectation": "Master's or Bachelor's in CS, Data Science, Statistics, Mathematics, or AI",
        "experience_expectation": "Proven ML modeling projects with measurable metric evaluation (AUC, RMSE, F1)",
        "recommended_certifications": ["TensorFlow Developer Certificate", "AWS Certified Machine Learning - Specialty"],
        "recommended_projects": ["Customer Churn or Predictive Classification Model with deployment", "NLP Sentiment Analysis or Recommendation Engine"],
        "other_recommended_skills": ["Cross-Validation", "Model Monitoring", "Data Wrangling"]
    },
    "AI/ML Engineer": {
        "required_skills": ["python", "machine learning", "deep learning", "dsa", "git", "numpy"],
        "recommended_skills": ["pytorch", "tensorflow", "nlp", "computer vision", "docker", "fastapi"],
        "optional_skills": ["mlops", "aws", "kubernetes", "rest api", "ci/cd"],
        "core_technical_skills": ["Model Training & Fine-Tuning", "Model Optimization", "API Serving", "Mathematical Foundations"],
        "programming_languages": ["Python", "C++", "SQL"],
        "frameworks": ["PyTorch", "TensorFlow", "Hugging Face", "FastAPI"],
        "databases": ["PostgreSQL", "Vector DBs (Pinecone, Chroma, Milvus)"],
        "cloud_devops_tools": ["Docker", "Kubernetes", "Git", "MLflow", "Weights & Biases"],
        "ai_ml_tools": ["PyTorch", "TensorFlow", "CUDA / GPU acceleration", "LangChain / LLM APIs"],
        "data_analytics_tools": ["NumPy", "Pandas"],
        "soft_skills": ["Research Aptitude", "Problem Decomposition", "Technical Writing"],
        "education_expectation": "Degree in Computer Science, AI, Robotics, or Electrical Engineering",
        "experience_expectation": "Practical implementation of neural architectures and end-to-end model deployments",
        "recommended_certifications": ["DeepLearning.AI AI Specializations", "AWS Machine Learning"],
        "recommended_projects": ["Fine-tuned LLM or RAG application", "Computer Vision detection system or Transformer model"],
        "other_recommended_skills": ["Vector Embeddings", "Prompt Engineering", "Quantization & ONNX"]
    },
    "Cybersecurity Analyst": {
        "required_skills": ["cybersecurity", "computer networks", "operating systems", "linux", "siem"],
        "recommended_skills": ["python", "bash", "penetration testing", "cryptography"],
        "optional_skills": ["wireshark", "cloud security", "docker", "firewalls"],
        "core_technical_skills": ["Vulnerability Assessment", "Log Analysis", "Incident Response", "Network Protocols"],
        "programming_languages": ["Python", "Bash", "PowerShell"],
        "frameworks": ["NIST Cybersecurity Framework", "MITRE ATT&CK"],
        "databases": ["SQL Log queries"],
        "cloud_devops_tools": ["Linux (Kali, Ubuntu)", "Wireshark", "Splunk / ELK Stack"],
        "ai_ml_tools": [],
        "data_analytics_tools": ["Log Analyzers", "SIEM Platforms"],
        "soft_skills": ["Attention to Anomalies", "Ethical Mindset", "Crisis Management", "Communication"],
        "education_expectation": "Degree in Information Security, Computer Science, or Network Engineering",
        "experience_expectation": "Hands-on labs (TryHackMe, HackTheBox) or SOC / security internship",
        "recommended_certifications": ["CompTIA Security+", "CEH (Certified Ethical Hacker)", "Cisco CCNA Security"],
        "recommended_projects": ["Home SOC Lab with SIEM alerting", "Network Vulnerability Scan and Remediation Report"],
        "other_recommended_skills": ["Threat Modeling", "Compliance (ISO 27001)", "Access Controls"]
    },
    "Cloud Engineer": {
        "required_skills": ["aws", "linux", "computer networks", "git", "bash", "docker"],
        "recommended_skills": ["terraform", "kubernetes", "ci/cd", "python", "azure"],
        "optional_skills": ["gcp", "system design", "ansible", "monitoring"],
        "core_technical_skills": ["Cloud Architecture", "Infrastructure as Code", "Networking (VPC, DNS, Subnets)", "Security Groups"],
        "programming_languages": ["Bash", "Python", "YAML / HCL"],
        "frameworks": ["Terraform", "CloudFormation", "Ansible"],
        "databases": ["Amazon RDS", "DynamoDB", "Aurora"],
        "cloud_devops_tools": ["AWS (EC2, S3, IAM, CloudWatch)", "Azure / GCP", "Docker", "Git"],
        "ai_ml_tools": [],
        "data_analytics_tools": ["CloudWatch", "Grafana / Prometheus"],
        "soft_skills": ["Troubleshooting", "Reliability Focus", "Cross-team Collaboration"],
        "education_expectation": "Bachelor's in CS, IT, Computer Engineering, or Cloud Certifications",
        "experience_expectation": "Cloud infrastructure provisioning labs or 1-2 years cloud support experience",
        "recommended_certifications": ["AWS Solutions Architect - Associate", "Azure Administrator (AZ-104)"],
        "recommended_projects": ["Multi-tier Web App deployed via Terraform on AWS", "Serverless microservice pipeline with Lambda & API Gateway"],
        "other_recommended_skills": ["Cost Optimization", "High Availability & Disaster Recovery"]
    },
    "DevOps Engineer": {
        "required_skills": ["docker", "ci/cd", "linux", "git", "bash", "computer networks"],
        "recommended_skills": ["kubernetes", "terraform", "aws", "python", "system design"],
        "optional_skills": ["ansible", "jenkins", "azure", "prometheus", "grafana"],
        "core_technical_skills": ["Build Automation", "Pipeline Orchestration", "Configuration Management", "Monitoring"],
        "programming_languages": ["Bash", "Python", "Go", "YAML"],
        "frameworks": ["Docker Compose", "Helm", "Terraform"],
        "databases": ["PostgreSQL / Redis operations"],
        "cloud_devops_tools": ["Kubernetes", "GitHub Actions", "GitLab CI", "Docker", "Prometheus", "Grafana"],
        "ai_ml_tools": [],
        "data_analytics_tools": ["ELK Stack", "Grafana"],
        "soft_skills": ["Systems Thinking", "Agile Operations", "Communication", "Problem Solving"],
        "education_expectation": "Degree in Computer Science, Systems Engineering, or equivalent background",
        "experience_expectation": "Proven CI/CD automated deployment pipelines and container clusters",
        "recommended_certifications": ["Certified Kubernetes Administrator (CKA)", "AWS Certified DevOps Engineer"],
        "recommended_projects": ["Complete CI/CD pipeline building, testing, and deploying Docker images to Kubernetes", "Automated Zero-Downtime deployment setup"],
        "other_recommended_skills": ["GitOps (ArgoCD)", "Secret Management (Vault)", "Log Aggregation"]
    },
    "Software Engineer": {
        "required_skills": ["dsa", "oop", "git", "sql", "operating systems", "computer networks"],
        "recommended_skills": ["python", "java", "c++", "rest api", "system design", "docker"],
        "optional_skills": ["linux", "ci/cd", "nosql", "cloud basics"],
        "core_technical_skills": ["Data Structures & Algorithms", "Object-Oriented Design", "Clean Code", "Debugging"],
        "programming_languages": ["Java / C++ / Python / Go", "SQL"],
        "frameworks": ["Spring Boot / Express / Django / FastAPI"],
        "databases": ["RDBMS (MySQL, PostgreSQL)", "NoSQL basics"],
        "cloud_devops_tools": ["Git", "GitHub", "Docker", "Linux"],
        "ai_ml_tools": [],
        "data_analytics_tools": [],
        "soft_skills": ["Analytical Problem Solving", "Team Collaboration", "Code Review Readiness"],
        "education_expectation": "B.Tech / B.E. / B.S. in Computer Science or related STEM field",
        "experience_expectation": "Strong competitive programming / DSA foundations and 2+ solid software projects",
        "recommended_certifications": ["Oracle Certified Associate Java", "AWS Certified Cloud Practitioner"],
        "recommended_projects": ["Scalable backend service with caching and database indexing", "Complex distributed application or desktop software"],
        "other_recommended_skills": ["Design Patterns", "Unit Testing & TDD", "Concurrency / Multithreading"]
    }
}


def normalize_skill(raw_skill: str) -> str:
    """Finds canonical skill name from raw string or alias."""
    clean = raw_skill.strip().lower()
    for canonical, aliases in SKILL_TAXONOMY.items():
        if clean == canonical or clean in aliases:
            return canonical.title() if len(canonical) > 3 else canonical.upper()
    return raw_skill.strip().title()


def extract_skills_from_text(text: str) -> List[str]:
    """Detects all known skills and technologies present in raw text."""
    if not text:
        return []
    
    text_lower = " " + text.lower() + " "
    detected = []
    
    for canonical, aliases in SKILL_TAXONOMY.items():
        for alias in aliases:
            # Word boundary check to prevent substring false positives
            pattern = r'(?<![a-zA-Z0-9_\-\+\#])' + re.escape(alias) + r'(?![a-zA-Z0-9_\-\+\#])'
            if re.search(pattern, text_lower):
                detected.append(canonical)
                break
                
    return sorted(list(set(detected)))


def resolve_role_requirements(target_role: str, jd_text: Optional[str] = None) -> TargetRoleRequirements:
    """
    Builds the TargetRoleRequirements schema.
    Clearly separates:
    - Requirements found in the provided Job Description
    - General role expectations
    - Skills inferred from the target role
    Prioritizes JD when provided!
    """
    target_role_clean = target_role.strip()
    
    # 1. Match against standard role template or fallback
    matched_role_key = None
    for standard_role in STANDARD_ROLE_TAXONOMY:
        if standard_role.lower() in target_role_clean.lower() or target_role_clean.lower() in standard_role.lower():
            matched_role_key = standard_role
            break
            
    base_template = STANDARD_ROLE_TAXONOMY.get(
        matched_role_key or "Software Engineer"
    )
    
    jd_skills = extract_skills_from_text(jd_text or "")
    jd_provided = bool(jd_text and len(jd_text.strip()) > 30 and jd_skills)
    
    # Base expectations from taxonomy
    gen_required = list(base_template.get("required_skills", []))
    gen_recommended = list(base_template.get("recommended_skills", []))
    gen_optional = list(base_template.get("optional_skills", []))
    
    if jd_provided:
        # Prioritize JD skills!
        # If skills are mentioned in the JD, they become Required or Recommended
        jd_explicit = [s for s in jd_skills]
        
        # Split JD skills into Required and Recommended based on JD context keywords
        jd_lower = jd_text.lower()
        required_from_jd = []
        recommended_from_jd = []
        
        for s in jd_skills:
            aliases = SKILL_TAXONOMY.get(s, [s])
            is_req = False
            for alias in aliases:
                # Look for "required", "must have", "minimum", "proficient in", "experience with" near skill
                req_pattern = r'(?:must have|required|minimum|proficient|essential|need|hands-on).*?' + re.escape(alias)
                if re.search(req_pattern, jd_lower):
                    is_req = True
                    break
            if is_req:
                required_from_jd.append(s)
            else:
                recommended_from_jd.append(s)
                
        if not required_from_jd:
            # If no strict phrasing, first half or overlap with base is required
            required_from_jd = [s for s in jd_skills if s in gen_required] or jd_skills[:max(3, len(jd_skills)//2)]
            recommended_from_jd = [s for s in jd_skills if s not in required_from_jd]
            
        final_required = list(dict.fromkeys(required_from_jd))
        final_recommended = list(dict.fromkeys(recommended_from_jd + [s for s in gen_required if s not in final_required]))
        final_optional = list(dict.fromkeys([s for s in gen_recommended + gen_optional if s not in final_required and s not in final_recommended]))
        
        inferred = [s for s in final_recommended if s not in jd_skills]
        general_exp = [s for s in gen_required + gen_recommended]
    else:
        final_required = gen_required
        final_recommended = gen_recommended
        final_optional = gen_optional
        jd_explicit = []
        inferred = []
        general_exp = gen_required + gen_recommended

    return TargetRoleRequirements(
        target_role=target_role_clean,
        jd_provided=jd_provided,
        required_skills=final_required,
        recommended_skills=final_recommended,
        optional_skills=final_optional,
        core_technical_skills=base_template.get("core_technical_skills", []),
        programming_languages=base_template.get("programming_languages", []),
        frameworks=base_template.get("frameworks", []),
        databases=base_template.get("databases", []),
        cloud_devops_tools=base_template.get("cloud_devops_tools", []),
        ai_ml_tools=base_template.get("ai_ml_tools", []),
        data_analytics_tools=base_template.get("data_analytics_tools", []),
        soft_skills=base_template.get("soft_skills", []),
        education_expectation=base_template.get("education_expectation", "Degree in CS or related field"),
        experience_expectation=base_template.get("experience_expectation", "Relevant hands-on projects or 0-2 years experience"),
        recommended_certifications=base_template.get("recommended_certifications", []),
        recommended_projects=base_template.get("recommended_projects", []),
        other_recommended_skills=base_template.get("other_recommended_skills", []),
        jd_explicit_requirements=jd_explicit,
        general_role_expectations=general_exp,
        inferred_skills=inferred
    )
