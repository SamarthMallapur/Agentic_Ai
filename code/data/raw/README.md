# Put real job-posting CSV files here

1. Download a dataset from Kaggle, such as "Job Title and Job Description Dataset" or "Naukri.com Job Postings".
2. Copy its `.csv` file into this folder.
3. From the `code` folder, run `python run.py --reset`.

The app reads title and description columns automatically. Once a file is recognised, it replaces the demo data.
Up to 5000 rows are read per file. `--reset` also clears saved profile and application data.

CSV files here are not uploaded to GitHub.
