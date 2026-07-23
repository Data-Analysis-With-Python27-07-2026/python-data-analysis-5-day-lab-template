from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

import nbformat
from nbclient import NotebookClient

NOTEBOOKS = {
    1: "day_01_python_pandas_basics.ipynb",
    2: "day_02_data_cleaning.ipynb",
    3: "day_03_eda_visualisation.ipynb",
    4: "day_04_statistical_inference.ipynb",
    5: "day_05_predictive_analytics.ipynb",
}


def grade_band(pct: float) -> str:
    if pct >= 85: return "Distinction"
    if pct >= 70: return "Merit"
    if pct >= 50: return "Pass"
    return "Further practice required"


def execute_one(root: Path, day: int, notebook_dir: Path) -> dict:
    src = notebook_dir / NOTEBOOKS[day]
    if not src.exists():
        return {"day":day,"earned":0,"possible":100,"percentage":0,"tasks":[],"error":f"Missing {src.name}"}

    nb = nbformat.read(src, as_version=4)
    grade_file = root / "grade_outputs" / f"day_{day:02d}.json"
    grade_file.parent.mkdir(exist_ok=True)
    if grade_file.exists(): grade_file.unlink()

    nb.cells.append(nbformat.v4.new_code_cell(
        "from pathlib import Path\n"
        "import json\n"
        "from grading.runtime import grade_namespace\n"
        f"__grade_result__ = grade_namespace(globals(), day={day})\n"
        f"Path(r'{grade_file.as_posix()}').write_text(json.dumps(__grade_result__, indent=2, default=str), encoding='utf-8')\n"
        "print(__grade_result__)"
    ))

    try:
        client = NotebookClient(nb, timeout=600, kernel_name="python3", resources={"metadata":{"path":str(root)}})
        client.execute()
    except Exception as exc:
        partial = None
        if grade_file.exists():
            partial=json.loads(grade_file.read_text(encoding='utf-8'))
        if partial: return partial
        return {"day":day,"earned":0,"possible":100,"percentage":0,"tasks":[],"error":f"Notebook execution failed: {type(exc).__name__}: {exc}"}

    if not grade_file.exists():
        return {"day":day,"earned":0,"possible":100,"percentage":0,"tasks":[],"error":"No grade output was produced."}
    return json.loads(grade_file.read_text(encoding="utf-8"))


def render_report(results: list[dict]) -> str:
    total=sum(x.get("earned",0) for x in results); possible=sum(x.get("possible",100) for x in results); pct=100*total/possible
    lines=[
        "# Automatic Notebook Grade Report",
        "",
        f"**Overall score: {total}/{possible} ({pct:.1f}%) — {grade_band(pct)}**",
        "",
        "| Day | Score | Percentage | Status |",
        "|---:|---:|---:|---|",
    ]
    for x in results:
        status="Executed" if not x.get("error") else "Execution error"
        lines.append(f"| {x['day']} | {x.get('earned',0)}/{x.get('possible',100)} | {x.get('percentage',0):.1f}% | {status} |")
    for x in results:
        lines += ["",f"## Day {x['day']} — {x.get('earned',0)}/{x.get('possible',100)}"]
        if x.get("error"): lines += ["",f"**Error:** `{x['error']}`"]
        if x.get("identity_complete") is False: lines += ["","> Identity placeholders are incomplete. Update your name and GitHub username."]
        if x.get("tasks"):
            lines += ["","| Task | Earned | Possible | Feedback |","|---|---:|---:|---|"]
            for t in x["tasks"]:
                fb=str(t["feedback"]).replace("|","/")
                lines.append(f"| {t['task']} | {t['earned']} | {t['possible']} | {fb} |")
    lines += ["","---","Generated automatically from the latest committed notebooks."]
    return "\n".join(lines)+"\n"


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--ci",action="store_true")
    parser.add_argument("--notebook-dir",default="notebooks")
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    notebook_dir=(root/args.notebook_dir).resolve()
    results=[execute_one(root,d,notebook_dir) for d in NOTEBOOKS]
    report=render_report(results)
    (root/"grade_report.md").write_text(report,encoding="utf-8")
    (root/"grade_report.json").write_text(json.dumps(results,indent=2),encoding="utf-8")
    print(report)
    if args.ci and any(x.get("error") for x in results):
        sys.exit(1)

if __name__=="__main__": main()
