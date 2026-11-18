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

- Time: 2026-11-18T11:46:00
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
      "rewrite": "Constructed a Flask and SQL web application to manage and track applications for 120 students."
    }
  ]
}
```

### Call 2: rewrite_bullets

- Time: 2026-11-18T11:46:07
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
      "rewrite": "Optimized a slow PostgreSQL report query by implementing indexes, reducing execution time from 4 seconds to 600 ms."
    },
    {
      "original": "Wrote 35 unit tests with pytest and fixed 9 defects before release.",
      "rewrite": "Executed 35 unit tests using pytest and resolved 9 defects prior to release."
    },
    {
      "original": "Developed a Flask and SQL web application that tracks applications for 120 students.",
      "rewrite": "Created a Flask and SQL web application to track applications for 120 students."
    }
  ]
}
```

### Call 3: interview_questions

- Time: 2026-11-18T11:46:11
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
      "question": "You optimized a PostgreSQL query from 4 seconds to 600ms. Can you explain the process you used to identify the bottleneck and why adding an index was the correct solution?",
      "answer_points": [
        "Explain using EXPLAIN ANALYZE to identify sequential scans.",
        "Discuss the trade-offs of adding indexes versus query refactoring.",
        "Mention how index types like B-tree improve lookup performance."
      ]
    },
    {
      "category": "Project",
      "question": "In your Library Search Engine project, you implemented an inverted index. How would you scale this approach if the dataset grew significantly, considering your lack of experience with Redis or distributed systems?",
      "answer_points": [
        "Acknowledge the memory limitations of an in-memory inverted index.",
        "Discuss partitioning data across multiple database instances.",
        "Explain the importance of caching frequently searched terms."
      ]
    },
    {
      "category": "Behavioral",
      "question": "Tell me about a time you encountered a technical challenge while working on your Placement Tracker 
```

### Call 4: evaluate_answer

- Time: 2026-11-18T11:46:14
- Model: gemini-3.1-flash-lite
- Status: ok

Prompt (end of text):

```text
You are the Interview-Coach agent. Score this mock interview answer strictly.
Give integer scores from 0 to 10 for relevance, structure, specificity and clarity.
Give up to 2 strengths and up to 3 improvements. Refer only to what the student wrote.
If the category is Behavioral, judge it against Situation, Task, Action, Result.

Category: Behavioral
Question: Tell me about a time you encountered a technical challenge while working on your Placement Tracker project. How did you resolve it?
Points a strong answer covers: Describe a specific bug or architectural hurdle encountered.; Detail the debugging steps or research process used to find a solution.; Explain what you learned about backend reliability during the process.
Student answer:
We disagreed on an index versus a query rewrite. I tested both on real data, shared the 4 second and 600 ms results, and the team chose the index.

```

Response:

```text
{
  "relevance": 7,
  "structure": 4,
  "specificity": 6,
  "clarity": 7,
  "strengths": [
    "Used data-driven evidence to support the decision-making process.",
    "Provided a clear, concise outcome."
  ],
  "improvements": [
    "The answer lacks the Situation and Task components of the STAR method.",
    "Failed to explain the technical nature of the architectural hurdle or the specific backend reliability lessons learned.",
    "The response is too brief and does not fully address the prompt's requirements regarding the research process."
  ]
}
```

### Call 5: weekly_summary

- Time: 2026-11-18T11:46:20
- Model: gemini-3.1-flash-lite
- Status: ok

Prompt (end of text):

```text
nd Developer", "due": "2026-11-17"}, {"id": 2, "company": "Demo Company 11", "role": "Software Engineer", "due": "2026-11-13"}]}, "resume_average": 62, "interview": 5.2, "market_claims": ["SQL appears in 70% of Backend Developer / Software Engineer postings.", "Git appears in 61% of Backend Developer / Software Engineer postings.", "Python appears in 58% of Backend Developer / Software Engineer postings.", "Java appears in 46% of Backend Developer / Software Engineer postings.", "REST APIs appears in 42% of Backend Developer / Software Engineer postings.", "Docker appears in 38% of Backend Developer / Software Engineer postings."], "actions": ["Follow up on Backend Developer at Demo Company 03.", "Follow up on Software Engineer at Demo Company 11.", "Learn Java and build one small project with it.", "Close the AWS gap for your tracked roles.", "Improve your resume's skills alignment."]}

```

Response:

```text
Your current readiness score is 59, with three active job applications in various stages. To improve your prospects, focus on aligning your resume with the skills most frequently requested in job postings, such as SQL, Git, and Python. You also have pending follow-ups for your backend and software engineering applications. The single most important next step is to follow up on your pending job applications to maintain momentum in your search.
```
