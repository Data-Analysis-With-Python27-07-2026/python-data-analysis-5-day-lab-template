# Student Submission Guide

## Your five-day workflow

Your GitHub Classroom assignment gives you an individual repository. Work in a browser-based GitHub Codespace, complete one notebook each day and push your changes. Every push automatically runs the grader.

### Start or reopen your Codespace

1. Open your assignment repository.
2. Select **Code → Codespaces**.
3. Create a codespace, or reopen the one you used previously.
4. Open the notebook for the current day.
5. Select the Python 3.12 kernel.

### Complete the notebook

- Read each objective before coding.
- Replace only the `TODO` sections.
- Preserve graded variable names.
- Run cells in order.
- Use **Restart Kernel and Run All** before submission.
- Correct every visible exception.

### Submit

Use the Source Control panel or terminal:

```bash
git status
git add notebooks outputs
git commit -m "Complete Day 2 data cleaning"
git push
```

### View your score

1. Open the repository’s **Actions** tab.
2. Select **GitHub Classroom — automatic notebook grading**.
3. Open the latest run.
4. Read the **Summary** for your overall and day-level scores.
5. Download `notebook-grade-report` for task-level feedback.
6. Correct your work and push again; the score is recalculated.

## Important

- Your repository is your submission record; do not send notebook files by email.
- Never edit `grading/` or the workflow file.
- Do not commit passwords, personal access tokens or private information.
- The facilitator can see your latest score, notebook content and commit history through GitHub Classroom.
