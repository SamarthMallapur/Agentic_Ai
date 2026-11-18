"""Regenerate data/demo_postings.csv. The postings are synthetic and labelled so."""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "demo_postings.csv"
START, DAYS = date(2026, 8, 24), 82
LOCATIONS = ["Bengaluru", "Hyderabad", "Pune", "Chennai", "Gurugram", "Mumbai", "Remote"]
# role: {skill: (share in older postings, share in newer postings)}
ROLES = {
    "Backend Developer": {"Python": (.6, .65), "Java": (.4, .35), "SQL": (.8, .8), "REST APIs": (.75, .8), "Docker": (.4, .62), "AWS": (.4, .5), "Git": (.6, .6), "Redis": (.25, .3), "Microservices": (.35, .45), "Kubernetes": (.15, .3), "System Design": (.3, .4), "Generative AI": (.02, .18)},
    "Software Engineer": {"Data Structures": (.7, .7), "Java": (.4, .4), "Python": (.5, .55), "C++": (.3, .25), "SQL": (.55, .55), "Git": (.6, .6), "OOP": (.5, .45), "System Design": (.25, .35), "AWS": (.25, .35), "Docker": (.2, .4), "Generative AI": (.03, .2)},
    "Full Stack Developer": {"JavaScript": (.8, .75), "TypeScript": (.3, .55), "React": (.7, .75), "Node.js": (.6, .6), "SQL": (.45, .45), "MongoDB": (.4, .35), "REST APIs": (.55, .6), "Git": (.55, .55), "AWS": (.25, .35), "Docker": (.2, .35)},
    "Frontend Developer": {"JavaScript": (.85, .8), "TypeScript": (.35, .6), "React": (.7, .75), "HTML": (.75, .7), "CSS": (.75, .7), "Git": (.5, .5), "Next.js": (.1, .3), "Figma": (.2, .2), "Unit Testing": (.2, .25)},
    "Data Analyst": {"SQL": (.85, .85), "Excel": (.7, .6), "Python": (.5, .6), "Power BI": (.45, .5), "Tableau": (.35, .3), "Statistics": (.45, .45), "Data Visualization": (.5, .5), "Pandas": (.3, .4), "A/B Testing": (.12, .2)},
    "Data Engineer": {"Python": (.75, .8), "SQL": (.85, .85), "ETL": (.65, .65), "Spark": (.5, .55), "Airflow": (.3, .45), "AWS": (.45, .5), "Kafka": (.25, .3), "Snowflake": (.2, .35), "Docker": (.2, .3)},
    "Machine Learning Engineer": {"Python": (.9, .9), "Machine Learning": (.85, .8), "PyTorch": (.4, .55), "TensorFlow": (.4, .3), "Scikit-learn": (.4, .35), "SQL": (.35, .35), "Generative AI": (.15, .5), "NLP": (.3, .4), "Docker": (.25, .35), "AWS": (.25, .3)},
    "DevOps Engineer": {"Linux": (.75, .75), "Docker": (.75, .8), "Kubernetes": (.55, .7), "AWS": (.6, .6), "Terraform": (.35, .55), "CI/CD": (.7, .75), "Jenkins": (.4, .3), "Bash": (.45, .4), "Git": (.55, .55), "Python": (.35, .4)},
}
PHRASE = {"Data Structures": "data structures and algorithms", "OOP": "object-oriented programming", "ETL": "ETL pipelines", "Generative AI": "generative AI"}


def main() -> None:
    rng = random.Random(42)
    rows = []
    for role, skills in ROLES.items():
        for _ in range(40):
            posted = START + timedelta(days=rng.randrange(DAYS))
            newer = (posted - START).days >= DAYS / 2
            chosen = [s for s, (old, new) in skills.items() if rng.random() < (new if newer else old)] or [next(iter(skills))]
            rng.shuffle(chosen)
            split = max(1, round(len(chosen) * 0.7))
            names = lambda items: ", ".join(PHRASE.get(s, s) for s in items)
            text = f"SYNTHETIC DEMO POSTING. We are hiring a {role} for our product team. Required skills: {names(chosen[:split])}."
            if chosen[split:]:
                text += f" Nice to have: {names(chosen[split:])}."
            rows.append({"title": role, "company": f"Demo Company {rng.randint(1, 24):02d}", "location": rng.choice(LOCATIONS),
                         "description": text, "skills": "", "posted_on": posted.isoformat()})
    rows.sort(key=lambda r: r["posted_on"])
    with OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} synthetic postings to {OUT}")


if __name__ == "__main__":
    main()
