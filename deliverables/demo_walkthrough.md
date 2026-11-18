# Working Demo Walkthrough (about 5 minutes)

Start the app with a clean sample student. This deletes any data saved in the app.

```bash
cd code
python run.py --reset
```

| # | Do this | What to point out |
|---|---|---|
| 1 | Open **Home** | Readiness is calculated from real parts. The data notice says the postings are synthetic |
| 2 | Open **Resume Review**, clear **Company**, and press **Review my resume** | Intake asks for the missing detail before reviewing |
| 3 | Pick *Demo Company 03: Backend Developer* and press **Review my resume** | Fixed 100-point score, reasons, missing skills and confidence |
| 4 | Find the Kubernetes note | Earlier rejected advice is hidden, with the student's reason |
| 5 | Press **Reject** on the Docker advice, enter a reason, save, and review again | The Docker advice is now hidden. This is the feedback memory working |
| 6 | Open **Applications** and change a status | The tracker saves it, and the history is recorded |
| 7 | Open **Interview Coach**, create questions, answer one | Questions use the JD and skill gaps. Feedback shows its confidence |
| 8 | Open **Market Trends**, then a **Posting #** source | Search, extract, compare and synthesize steps, with the source behind each claim |
| 9 | Open **Weekly Report**, press **Generate new report** | Three agents merge into one report, then evidence table, QA checks and run trace |

Screenshots of a real run are in the `screenshots` folder.
