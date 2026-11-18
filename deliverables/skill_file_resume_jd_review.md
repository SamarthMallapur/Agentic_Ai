---
name: resume-jd-review
description: Review a resume against one job description using keyword match, a formatting checklist, a red-flag list and a fixed 100-point rubric.
version: 2.0
implemented_by: app/tools.py (resume_score, keyword_gap), app/agents.py (review_resume), app/governance.py (QA)
---

# Resume-vs-JD Review

## When to use
Use this for one resume and one specific job description. Do not use it to judge a person's ability.

## Step 1. Intake: clarify before reviewing
| Check | If it fails |
|---|---|
| Resume has at least 80 words | Stop and ask for a text resume |
| JD has at least 15 words | Stop and ask for the JD |
| JD has at least 40 words and names at least 3 skills | Ask for the full JD, or continue at Low confidence |
| Target role is given | Ask for it, or continue with a stated assumption |
| Company is given | Ask for it, or continue with a stated assumption |

## Step 2. Keyword match
1. Extract JD skills with the shared vocabulary.
2. Set priority from the sentence that names the skill.
   - HIGH: stated as a requirement.
   - MEDIUM: "familiarity", "exposure", "basic".
   - LOW: "preferred", "nice to have", "a plus".
3. Mark each skill as matched, partial (a related skill is present) or missing.

## Step 3. Fixed scoring rubric (100 points)
| Criterion | Points | How it is scored |
|---|---:|---|
| ATS keyword match | 30 | Priority-weighted JD coverage. HIGH=3, MEDIUM=2, LOW=1. Partial counts half |
| Skills alignment | 25 | Weighted JD skills proven in experience or projects |
| Experience relevance | 20 | Role words (6), proof bullets (6), JD terms in experience or projects (8) |
| Resume quality | 15 | Share of the formatting checklist passed |
| Red flags | 10 | Start at 10 and subtract 2 per red flag |

## Step 4. Formatting checklist
Email; phone; education section; skills section; experience or projects section; at least 4 bullets;
200 to 1000 words; at least 2 bullets with numbers; at least 3 bullets starting with an action verb.

## Step 5. Red-flag list
Generic objective; first-person wording; repeated "responsible for"; most listed skills unproven;
no dates; over 1200 words; placeholder text.

## Step 6. Use memory
Search past accepted and rejected advice. Do not repeat advice the student rejected. Show it as
hidden, with the reason they gave.

## Step 7. QA before the student sees anything
- Never tell the student to claim a skill without this note: "Add this only if you have really used it. Otherwise, learn it first."
- A bullet rewrite may not add a skill or a number. If it does, discard it.
- Never state facts about a company.
- Label weak results `LOW CONFIDENCE`. Do not state them flatly.

## Output
Score, breakdown with reasons, matched/partial/missing skills, checklist, red flags, recommendations,
hidden recommendations, verified rewrites, confidence and QA notes.
