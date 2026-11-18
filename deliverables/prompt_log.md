# Prompt Log

Part 1 lists the prompt templates. Part 2 is the log captured during the sample run.
Emails and phone numbers are removed before a prompt is sent. Long text is shortened here.

## Part 1. Templates

### REWRITE_BULLETS

```text
You are the Resume-Reviewer agent. Follow this review method:
{skill}

Rewrite each resume bullet so it is clearer and starts with an action verb.
Hard rules:
- Use only facts already in that bullet. Never add a tool, skill, employer or number.
- If a metric would help, write the placeholder [add metric] instead of inventing one.
- Do not use any of these skills unless the original bullet names them: {missing_skills}

Target role: {role}
Bullets:
{bullets}
```

### INTERVIEW_QUESTIONS

```text
You are the Interview-Coach agent. Write exactly 5 mock interview questions, one for each
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
```

### EVALUATE_ANSWER

```text
You are the Interview-Coach agent. Score this mock interview answer strictly.
Give integer scores from 0 to 10 for relevance, structure, specificity and clarity.
Give up to 2 strengths and up to 3 improvements. Refer only to what the student wrote.
If the category is Behavioral, judge it against Situation, Task, Action, Result.

Category: {category}
Question: {question}
Points a strong answer covers: {points}
Student answer:
{answer}
```

### WEEKLY_SUMMARY

```text
You are the report editor. Write a plain summary of at most 80 words for the student.
Use only the verified facts below. Do not add any number, company name or claim that is not in them.
Mention the single most important next step.

Verified facts:
{facts}
```

## Part 2. Captured calls

### Call 1: rewrite_bullets

- Time: 2026-11-18T11:09:11
- Model: gemini-3.1-flash-lite
- Status: ok

Prompt (end of text):

```text
 with reasons, matched/partial/missing skills, checklist, red flags, recommendations,
hidden recommendations, verified rewrites, confidence and QA notes.


Rewrite each resume bullet so it is clearer and starts with an action verb.
Hard rules:
- Use only facts already in that bullet. Never add a tool, skill, employer or number.
- If a metric would help, write the placeholder [add metric] instead of inventing one.
- Do not use any of these skills unless the original bullet names them: Docker, AWS, System Design, Kubernetes, Redis

Target role: Backend Developer
Bullets:
- Built 6 REST APIs with FastAPI for an internal ticketing tool used by 40 staff.
- Reduced a slow PostgreSQL report query from 4 seconds to 600 ms by adding indexes.
- Wrote 35 unit tests with pytest and fixed 9 defects before release.
- Developed a Flask and SQL web application that tracks applications for 120 students.

```

Response:

```text
{
  "rewrites": [
    {
      "original": "Built 6 REST APIs with FastAPI for an internal ticketing tool used by 40 staff.",
      "rewrite": "Engineered 6 REST APIs using FastAPI to support an internal ticketing tool for 40 staff members."
    },
    {
      "original": "Reduced a slow PostgreSQL report query from 4 seconds to 600 ms by adding indexes.",
      "rewrite": "Optimized PostgreSQL report query performance from 4 seconds to 600 ms through the implementation of database indexes."
    },
    {
      "original": "Wrote 35 unit tests with pytest and fixed 9 defects before release.",
      "rewrite": "Executed 35 unit tests using pytest and resolved 9 defects prior to software release."
    },
    {
      "original": "Developed a Flask and SQL web application that tracks applications for 120 students.",
      "rewrite": "Constructed a Flask and SQL web application to manage tracking for 120 student applications."
    }
  ]
}
```

### Call 2: rewrite_bullets

- Time: 2026-11-18T11:09:13
- Model: gemini-3.1-flash-lite
- Status: ok

Prompt (end of text):

```text
 with reasons, matched/partial/missing skills, checklist, red flags, recommendations,
hidden recommendations, verified rewrites, confidence and QA notes.


Rewrite each resume bullet so it is clearer and starts with an action verb.
Hard rules:
- Use only facts already in that bullet. Never add a tool, skill, employer or number.
- If a metric would help, write the placeholder [add metric] instead of inventing one.
- Do not use any of these skills unless the original bullet names them: Docker, AWS, System Design, Kubernetes, Redis

Target role: Backend Developer
Bullets:
- Built 6 REST APIs with FastAPI for an internal ticketing tool used by 40 staff.
- Reduced a slow PostgreSQL report query from 4 seconds to 600 ms by adding indexes.
- Wrote 35 unit tests with pytest and fixed 9 defects before release.
- Developed a Flask and SQL web application that tracks applications for 120 students.

```

Response:

```text
{
  "rewrites": [
    {
      "original": "Built 6 REST APIs with FastAPI for an internal ticketing tool used by 40 staff.",
      "rewrite": "Engineered 6 REST APIs using FastAPI to support an internal ticketing tool for 40 staff members."
    },
    {
      "original": "Reduced a slow PostgreSQL report query from 4 seconds to 600 ms by adding indexes.",
      "rewrite": "Optimized a PostgreSQL report query by implementing indexes, reducing execution time from 4 seconds to 600 ms."
    },
    {
      "original": "Wrote 35 unit tests with pytest and fixed 9 defects before release.",
      "rewrite": "Executed 35 unit tests using pytest and resolved 9 defects prior to release."
    },
    {
      "original": "Developed a Flask and SQL web application that tracks applications for 120 students.",
      "rewrite": "Constructed a Flask and SQL web application to track applications for 120 students."
    }
  ]
}
```

### Call 3: interview_questions

- Time: 2026-11-18T11:09:22
- Model: gemini-3.1-flash-lite
- Status: ok

Prompt (end of text):

```text
a and REST APIs for login, search and status updates.
- Deployed the service on a Linux server and managed releases with Git.

Library Search Engine, 2025
- Implemented an inverted index in Python using core data structures and algorithms.
- Improved search time by 70 percent compared with a linear scan on 50000 records.

ACHIEVEMENTS
- Finalist, college hackathon, 2025.
- Solved 300 data structures and algorithms problems on practice platforms.


Job description:
SYNTHETIC DEMO JOB DESCRIPTION
Backend Developer

You will design and build reliable backend services for our product team.

Requirements:
Strong Python and SQL.
Experience building REST APIs with FastAPI or Django.
Working knowledge of PostgreSQL and Git.
Must have Docker experience.
Understanding of data structures and algorithms.

Familiarity with AWS.
Exposure to system design.
Redis is a plus.
Kubernetes is nice to have.


```

Response:

```text
{
  "questions": [
    {
      "category": "Technical",
      "question": "You optimized a PostgreSQL query from 4 seconds to 600ms. What specific steps did you take to identify the bottleneck and implement the fix?",
      "answer_points": [
        "Mention using EXPLAIN ANALYZE to identify the slow sequential scan.",
        "Explain the decision-making process for choosing which columns to index.",
        "Discuss verifying the performance improvement and monitoring for potential write-performance trade-offs."
      ]
    },
    {
      "category": "Project",
      "question": "Regarding your Library Search Engine project, how did you implement the inverted index, and what data structures did you prioritize for performance?",
      "answer_points": [
        "Describe the mapping of terms to document IDs using a hash map or dictionary.",
        "Explain how the choice of data structure enabled O(1) or O(log n) lookups compared to linear scanning.",
        "Discuss the trade-off between memory usage and search speed for your 50,000 records."
      ]
    },
    {
      "category": "Behavioral",
      "question": "Can you describe a situation during your internship where you ha
```

### Call 4: evaluate_answer

- Time: 2026-11-18T11:09:24
- Model: gemini-3.1-flash-lite
- Status: ok

Prompt (end of text):

```text
trictly.
Give integer scores from 0 to 10 for relevance, structure, specificity and clarity.
Give up to 2 strengths and up to 3 improvements. Refer only to what the student wrote.
If the category is Behavioral, judge it against Situation, Task, Action, Result.

Category: Behavioral
Question: Can you describe a situation during your internship where you had to manage a technical challenge while working under a deadline?
Points a strong answer covers: Briefly outline the specific task or bug you faced within the ticketing tool project.; Explain the systematic approach you took to isolate the issue while keeping the team informed.; Highlight the outcome, such as meeting the delivery timeline and ensuring code quality via testing.
Student answer:
We disagreed on an index versus a query rewrite. I tested both on real data, shared the 4 second and 600 ms results, and the team chose the index.

```

Response:

```text
{
  "relevance": 7,
  "structure": 3,
  "specificity": 6,
  "clarity": 7,
  "strengths": [
    "Used data-driven evidence to support the decision-making process.",
    "Provided a clear, concise outcome."
  ],
  "improvements": [
    "Apply the STAR method to provide necessary context regarding the project and the deadline.",
    "Explain the systematic approach taken to isolate the issue beyond just testing two options.",
    "Elaborate on the final result, specifically confirming if the deadline was met and the quality of the solution."
  ]
}
```

### Call 5: weekly_summary

- Time: 2026-11-18T11:09:31
- Model: gemini-3.1-flash-lite
- Status: ok

Prompt (end of text):

```text
nd Developer", "due": "2026-11-17"}, {"id": 2, "company": "Demo Company 11", "role": "Software Engineer", "due": "2026-11-13"}]}, "resume_average": 62, "interview": 5.2, "market_claims": ["SQL appears in 70% of Backend Developer / Software Engineer postings.", "Git appears in 61% of Backend Developer / Software Engineer postings.", "Python appears in 58% of Backend Developer / Software Engineer postings.", "Java appears in 46% of Backend Developer / Software Engineer postings.", "REST APIs appears in 42% of Backend Developer / Software Engineer postings.", "Docker appears in 38% of Backend Developer / Software Engineer postings."], "actions": ["Follow up on Backend Developer at Demo Company 03.", "Follow up on Software Engineer at Demo Company 11.", "Learn Java and build one small project with it.", "Close the AWS gap for your tracked roles.", "Improve your resume's skills alignment."]}

```

Response:

```text
Your current job search includes three active applications, with one interview in progress. Your resume and readiness scores indicate room for improvement. Market data shows high demand for skills like SQL, Git, and Python. To strengthen your profile, you should focus on aligning your resume with these key technical requirements. Your most important next step is to follow up on your pending job applications to maintain momentum.
```
