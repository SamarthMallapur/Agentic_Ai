"""Skill vocabulary and matching. Deterministic, so scores are repeatable."""
import re

# canonical skill -> regex alternatives (case-insensitive)
SKILLS = {
    "Python": r"python", "Java": r"java", "JavaScript": r"javascript|\bjs\b", "TypeScript": r"typescript",
    "C++": r"c\+\+|\bcpp\b", "C#": r"c#|\.net\b|dotnet", "Kotlin": r"kotlin", "Swift": r"swift",
    "PHP": r"php", "Ruby": r"ruby", "Rust": r"rust", "Golang": r"golang",
    "SQL": r"sql", "MySQL": r"mysql", "PostgreSQL": r"postgres(?:ql)?", "MongoDB": r"mongo(?:db)?",
    "Redis": r"redis", "Oracle DB": r"oracle (?:db|database)",
    "HTML": r"html5?", "CSS": r"css3?", "React": r"react(?:\.?js)?", "Angular": r"angular(?:js)?",
    "Vue": r"vue(?:\.?js)?", "Next.js": r"next\.?js", "Node.js": r"node(?:\.?js)?", "Express": r"express(?:\.?js)?",
    "Django": r"django", "Flask": r"flask", "FastAPI": r"fast ?api", "Spring Boot": r"spring(?: ?boot)?",
    "REST APIs": r"rest(?:ful)?(?: web)? (?:apis?|services?)|restful", "GraphQL": r"graphql",
    "Microservices": r"micro-?services?",
    "AWS": r"aws|amazon web services", "Azure": r"azure", "GCP": r"gcp|google cloud",
    "Docker": r"docker", "Kubernetes": r"kubernetes|k8s", "Terraform": r"terraform", "Jenkins": r"jenkins",
    "CI/CD": r"ci ?/ ?cd|continuous integration", "Linux": r"linux", "Git": r"git|github|gitlab",
    "Bash": r"bash|shell scripting", "Monitoring": r"prometheus|grafana",
    "Data Structures & Algorithms": r"data structures?|algorithms?|\bdsa\b",
    "System Design": r"system design", "OOP": r"\boops?\b|object[- ]oriented",
    "Operating Systems": r"operating systems?", "DBMS": r"dbms|database management", "Computer Networks": r"computer networks?|networking",
    "Unit Testing": r"unit test(?:s|ing)?|pytest|junit", "Selenium": r"selenium",
    "Pandas": r"pandas", "NumPy": r"numpy", "Scikit-learn": r"scikit-?learn|sklearn",
    "TensorFlow": r"tensorflow", "PyTorch": r"pytorch", "Machine Learning": r"machine learning|\bml\b",
    "Deep Learning": r"deep learning", "NLP": r"\bnlp\b|natural language processing",
    "Generative AI": r"generative ai|gen ?ai|\bllms?\b|large language models?|\brag\b",
    "Statistics": r"statistics|statistical", "A/B Testing": r"a/b test(?:s|ing)?",
    "ETL": r"etl|data pipelines?", "Spark": r"spark", "Hadoop": r"hadoop", "Kafka": r"kafka", "Airflow": r"airflow",
    "Snowflake": r"snowflake", "Power BI": r"power ?bi", "Tableau": r"tableau", "Excel": r"excel",
    "Data Visualization": r"data visuali[sz]ation|dashboards?",
    "Android": r"android", "iOS": r"\bios\b", "Flutter": r"flutter", "Figma": r"figma",
    "Cybersecurity": r"cyber ?security|information security", "Agile": r"agile|scrum",
    "Project Management": r"project management", "Salesforce": r"salesforce", "SAP": r"\bsap\b",
    "SEO": r"\bseo\b", "Digital Marketing": r"digital marketing", "Accounting": r"accounting|bookkeeping",
    "Financial Analysis": r"financial analysis|financial modell?ing", "Recruitment": r"recruit(?:ment|ing)|talent acquisition",
    "Sales": r"\bsales\b", "Communication": r"communication skills?|communicat(?:e|ion)",
    "Leadership": r"leadership", "Problem Solving": r"problem[- ]solving",
}

# Having one of these is partial evidence for the other.
RELATED = [
    {"MySQL", "PostgreSQL", "SQL", "Oracle DB", "DBMS"}, {"React", "Angular", "Vue", "Next.js"},
    {"AWS", "Azure", "GCP"}, {"Docker", "Kubernetes"}, {"Flask", "FastAPI", "Django"},
    {"TensorFlow", "PyTorch"}, {"Power BI", "Tableau"}, {"Jenkins", "CI/CD"},
    {"Machine Learning", "Scikit-learn", "Deep Learning"}, {"JavaScript", "TypeScript"},
    {"Spark", "Hadoop"}, {"Node.js", "Express"},
]

_PATTERNS = {
    name: re.compile(rf"(?<![\w+#.])(?:{alt})(?![\w+#])", re.IGNORECASE) for name, alt in SKILLS.items()
}


def extract_skills(text: str) -> dict[str, int]:
    """Return {canonical skill: mention count} for skills found in text."""
    text = text or ""
    found = {}
    for name, pattern in _PATTERNS.items():
        count = len(pattern.findall(text))
        if count:
            found[name] = count
    return found


def has_skill(text: str, skill: str) -> bool:
    pattern = _PATTERNS.get(skill)
    return bool(pattern and pattern.search(text or ""))


def canonical(skill: str) -> str:
    """Map free text such as 'reactjs' to its canonical skill name."""
    matches = extract_skills(skill)
    return max(matches, key=len) if matches else skill.strip()


def related_to(skill: str) -> set[str]:
    out = set()
    for group in RELATED:
        if skill in group:
            out |= group
    out.discard(skill)
    return out
