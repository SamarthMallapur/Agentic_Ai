"""All LLM prompts, in one place so they can be reviewed and logged."""

REWRITE_BULLETS = """You are the Resume-Reviewer agent. Follow this review method:
{skill}

Rewrite each resume bullet so it is clearer and starts with an action verb.
Hard rules:
- Use only facts already in that bullet. Never add a tool, skill, employer or number.
- If a metric would help, write the placeholder [add metric] instead of inventing one.
- Do not use any of these skills unless the original bullet names them: {missing_skills}

Target role: {role}
Bullets:
{bullets}
"""

INTERVIEW_QUESTIONS = """You are the Interview-Coach agent. Write exactly 5 mock interview questions, one for each
category: Technical, Project, Behavioral, Resume, Weakness.
Rules:
- Base them only on the student profile, resume excerpt, job description and skill gaps below.
- Do not state or imply facts about the company (culture, products, salary, hiring process).
- Give 3 short points a strong answer would cover.

Role: {role}
Student skills: {skills}
Skill gaps: {gaps}
Resume excerpt:
{resume}

Job description:
{jd}
"""

EVALUATE_ANSWER = """You are the Interview-Coach agent. Score this mock interview answer strictly.
Give integer scores from 0 to 10 for relevance, structure, specificity and clarity.
Give up to 2 strengths and up to 3 improvements. Refer only to what the student wrote.
If the category is Behavioral, judge it against Situation, Task, Action, Result.

Category: {category}
Question: {question}
Points a strong answer covers: {points}
Student answer:
{answer}
"""

WEEKLY_SUMMARY = """You are the report editor. Write a plain summary of at most 80 words for the student.
Use only the verified facts below. Do not add any number, company name or claim that is not in them.
Mention the single most important next step.

Verified facts:
{facts}
"""
