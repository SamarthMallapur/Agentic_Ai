---
name: Resume vs JD Review
description: Skill for evaluating a resume against a job description.
---

# Resume vs JD Review

**Purpose**: To deterministically score a student's resume against a target job description and identify actionable gaps, without hallucinating non-existent skills.

**Inputs**:
- `resume_text`: Full text of the student's resume.
- `jd_text`: Full text of the target job description.

**Procedure**:
1. **Intake**: Verify both inputs are provided and non-empty.
2. **Keyword Extraction**: Extract all technical skills, tools, and domain keywords from the JD.
3. **Matching**: Compare JD keywords against the resume text. Categorize as:
   - Matched
   - Partially Matched
   - Missing
4. **Prioritization**: Rank missing keywords (HIGH, MEDIUM, LOW) based on frequency in JD and industry standard relevance.
5. **Scoring Rubric (100 pts)**:
   - *ATS/Keyword Match (30 pts)*: Based on % of High/Medium keywords matched.
   - *Skills Alignment (25 pts)*: Based on contextual evidence of skills in project descriptions.
   - *Experience Relevance (20 pts)*: Based on alignment of past roles/internships with JD requirements.
   - *Resume Quality (15 pts)*: Formatting, grammar, action verbs.
   - *Red Flags (10 pts)*: Deduct points for missing sections, extreme length, generic objectives.
6. **Output**: Generate structured JSON containing the score breakdown, missing keywords, and recommendations.

**QA Requirements**:
- **Evidence Rule**: Every recommendation to add a skill must include a caveat: "Only add this if you actually have experience with it. Consider learning it otherwise."
- **Fabrication Check**: Do not invent metrics or projects.
- **Confidence Level**: Append confidence labels to the matching accuracy.

**Failure Conditions**:
- If the resume is unreadable (e.g., image-only PDF with failed OCR), return an error requesting a text-based PDF.
- If the JD is generic (e.g., "Looking for a smart person"), warn the user that keyword matching will be of low confidence.
