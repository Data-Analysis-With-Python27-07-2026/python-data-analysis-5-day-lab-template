# Five-Day Python Data Analysis Laboratory

**Training dates:** 27–31 July 2026  
**Facilitator and author:** Enock Ndunda

This is a student-facing, fully hands-on laboratory for learners with mixed programming experience. It contains five partially completed Jupyter notebooks. Complete the marked `TODO` cells, run the notebook, commit your work and push to GitHub. The included GitHub Actions workflow executes the notebooks and publishes your score automatically.

## Learning progression

| Day | Theme | Main output | Marks |
|---|---|---|---:|
| 1 | Python, NumPy and pandas foundations | Basic analysis and first chart | 100 |
| 2 | Flight-data loading and cleaning | Reproducible cleaned dataset | 100 |
| 3 | Exploratory analytics and visualisation | Evidence-based EDA report | 100 |
| 4 | Statistical inference | Confidence intervals and hypothesis tests | 100 |
| 5 | Predictive analytics | Delay-classification model and evaluation | 100 |

**Total:** 500 marks.

## Dataset

Days 2–5 use `data/flights_sample.csv`, a committed 50,000-row training subset based on the `flights.csv` dataset published on Figshare:

- Dataset page: <https://figshare.com/articles/dataset/flights_csv/9820139>
- DOI: `10.6084/m9.figshare.9820139`
- Upstream file size: approximately 565 MB
- Licence shown by Figshare: MIT

The manageable subset is included to make every student repository, Codespace and GitHub Actions run reproducible. It retains the original 31 analytical columns. Twenty-five exact duplicate rows were intentionally introduced for the Day 2 cleaning exercise. See `data/DATA_SOURCE.json` for provenance, coverage and preparation notes.

## Online workflow

1. Open the individual GitHub repository supplied by the facilitator.
2. Select **Code → Codespaces → Create codespace on main**.
3. Wait until the terminal reports that the environment is ready.
4. Open the notebook for the current day.
5. Select the Python kernel when prompted.
6. Enter your name and GitHub username.
7. Complete every `TODO` cell and use **Restart Kernel and Run All**.
8. Commit and push:

```bash
git add notebooks outputs
git commit -m "Complete Day 1 notebook"
git push
```

9. Open **Actions → GitHub Classroom — automatic notebook grading → latest run → Summary**.
10. Read your score and task-level feedback, correct your work and push again.

The workflow name retains “GitHub Classroom” for compatibility, but it runs in an ordinary GitHub repository as well.

## Local workflow

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
jupyter lab
```

The dataset is already included. Verify it with:

```powershell
python scripts\prepare_data.py
```

Run the same grader locally:

```powershell
python grading\grade_all.py
```

## Submission rules

- Replace the identity placeholders in every notebook.
- Do not rename notebooks or graded variables.
- Do not modify `grading/` or `.github/workflows/`.
- Run each notebook from top to bottom before pushing.
- Commit meaningful progress at least once per day.
- Read the Actions Summary after every submission.
- Open-ended interpretations are checked for completion; numerical and code tasks are checked for correctness.

## Academic integrity

The autograder gives rapid formative feedback. Discussion of concepts and debugging is encouraged, but the submitted notebook must represent the student’s own work. The facilitator may review commit history, explanations, code quality and live participation in addition to the automatic score.
