# Memory Schema

Storage is one SQLite file, `code/placement.db`, defined in `code/app/db.py`.

## Memory layers

| Table | Layer | Purpose |
|---|---|---|
| profile | Long-term | Skills, target roles, weak areas and resume |
| session_state | Session | Today's application and last review |
| feedback | Retrieval store | Advice accepted or rejected, with reasons |
| applications | Tracking store | Every application and its current status |
| application_events | Tracking store | Status history |
| postings | Evidence store | Job postings cited by market claims |
| reviews | History | Saved resume reviews |
| interview_attempts | History | Mock answers and feedback |
| reports | History | Saved weekly reports |

## How feedback retrieval works

1. Each new recommendation is compared with saved decisions.
2. An exact skill match wins, and advice about a different skill never matches. Otherwise text cosine similarity must be at least 0.75.
3. Rejected matches are hidden and shown with the student's reason.
4. Accepted matches stay visible with a note.

## Tables

### profile

| Column | Type | Required | Key |
|---|---|---|---|
| id | INTEGER | No | Yes |
| data | TEXT | Yes |  |
| updated_at | TEXT | Yes |  |

### session_state

| Column | Type | Required | Key |
|---|---|---|---|
| key | TEXT | No | Yes |
| value | TEXT | Yes |  |
| updated_at | TEXT | Yes |  |

### feedback

| Column | Type | Required | Key |
|---|---|---|---|
| id | INTEGER | No | Yes |
| suggestion | TEXT | Yes |  |
| skill | TEXT | No |  |
| decision | TEXT | Yes |  |
| reason | TEXT | No |  |
| context | TEXT | No |  |
| created_at | TEXT | Yes |  |

### applications

| Column | Type | Required | Key |
|---|---|---|---|
| id | INTEGER | No | Yes |
| company | TEXT | Yes |  |
| role | TEXT | Yes |  |
| job_description | TEXT | No |  |
| status | TEXT | Yes |  |
| applied_on | TEXT | No |  |
| follow_up_on | TEXT | No |  |
| resume_score | INTEGER | No |  |
| notes | TEXT | No |  |
| updated_at | TEXT | Yes |  |

### application_events

| Column | Type | Required | Key |
|---|---|---|---|
| id | INTEGER | No | Yes |
| application_id | INTEGER | Yes |  |
| from_status | TEXT | No |  |
| to_status | TEXT | Yes |  |
| at | TEXT | Yes |  |

### postings

| Column | Type | Required | Key |
|---|---|---|---|
| id | INTEGER | No | Yes |
| title | TEXT | Yes |  |
| company | TEXT | No |  |
| location | TEXT | No |  |
| description | TEXT | Yes |  |
| skills | TEXT | No |  |
| posted_on | TEXT | No |  |
| source | TEXT | Yes |  |
| source_row | INTEGER | Yes |  |
| is_demo | INTEGER | Yes |  |

### reviews

| Column | Type | Required | Key |
|---|---|---|---|
| id | INTEGER | No | Yes |
| application_id | INTEGER | No |  |
| company | TEXT | No |  |
| role | TEXT | No |  |
| score | INTEGER | Yes |  |
| confidence | TEXT | Yes |  |
| result | TEXT | Yes |  |
| created_at | TEXT | Yes |  |

### interview_attempts

| Column | Type | Required | Key |
|---|---|---|---|
| id | INTEGER | No | Yes |
| application_id | INTEGER | No |  |
| category | TEXT | Yes |  |
| skill | TEXT | No |  |
| question | TEXT | Yes |  |
| answer | TEXT | Yes |  |
| score | REAL | Yes |  |
| method | TEXT | Yes |  |
| confidence | TEXT | Yes |  |
| feedback | TEXT | Yes |  |
| created_at | TEXT | Yes |  |

### reports

| Column | Type | Required | Key |
|---|---|---|---|
| id | INTEGER | No | Yes |
| data | TEXT | Yes |  |
| markdown | TEXT | Yes |  |
| created_at | TEXT | Yes |  |
