# Known Limitations & Governance Note

## Dataset Bias
- The current market analyst module relies on a local dataset (`data/sample_jobs.csv`). The trends reported are limited entirely by the recency and sampling methodology of this specific dataset. Real-world market analysis would require robust live integration or much larger, frequently refreshed CSV ingestion.

## LLM Hallucination Risk
- Despite the implementation of a strict 100-point rubric and deterministic instructions, LLMs can occasionally misinterpret resume formatting or miss keywords that are phrased creatively.
- The `resume_score()` tries to be as deterministic as possible using `response_schema` (Structured Outputs), but slight variances may occur between identical runs due to LLM nature. (Temperature is set to 0.1 to mitigate this).

## No Guarantee of Hiring Outcomes
- The recommendations provided by this companion (e.g., "Add Docker to your skills", "Focus on System Design") are derived from statistical pattern matching and prompt heuristics. Following them does not guarantee a job offer. 

## Confidence Labels
- As enforced by our QA Agent, any market claim must have evidence. If the sample size is small (< 50 jobs) or the dataset is older than 6 months, the claim is presented with a **LOW CONFIDENCE** label.
