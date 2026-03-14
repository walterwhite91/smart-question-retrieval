from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from flask import Flask, jsonify, render_template, request

from services.search_controller import FilterState, SearchController

QObj = Dict[str, Any]

BASE_DIR = Path(__file__).resolve().parents[1]
DATASET_PATH = BASE_DIR / "dataset.json"
WEBAPP_DIR = Path(__file__).resolve().parent

app = Flask(
    __name__,
    template_folder=str(Path(__file__).resolve().parent / "templates"),
    static_folder=str(Path(__file__).resolve().parent / "static"),
)
controller = SearchController(DATASET_PATH)


def current_asset_version() -> int:
    paths = [
        WEBAPP_DIR / "static" / "app.js",
        WEBAPP_DIR / "static" / "styles.css",
        WEBAPP_DIR / "templates" / "index.html",
    ]
    return max(int(path.stat().st_mtime) for path in paths)


def sanitize_question(question: QObj) -> QObj:
    return {key: value for key, value in question.items() if key != "_id"}


def parse_state(payload: dict[str, Any]) -> FilterState:
    semester = payload.get("semester")
    semester_value = int(semester) if semester not in (None, "") and str(semester).strip() else None
    chapters = payload.get("chapters") or []
    if not isinstance(chapters, list):
        chapters = []

    return FilterState(
        semester=semester_value,
        subject=str(payload.get("subject", "")).strip(),
        filter_mode=str(payload.get("filter_mode", "all")).strip() or "all",
        chapters=tuple(str(ch).strip() for ch in chapters if str(ch).strip()),
        paper_type=str(payload.get("paper_type", "")).strip(),
        section=str(payload.get("section", "")).strip(),
    )


@app.get("/")
def index():
    return render_template(
        "index.html",
        dataset_path=str(controller.dataset_path),
        asset_version=current_asset_version(),
    )


@app.after_request
def disable_cache(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.get("/api/options")
def options():
    semester_raw = request.args.get("semester", "").strip()
    semester = int(semester_raw) if semester_raw else None
    subject = request.args.get("subject", "").strip()
    paper_type = request.args.get("paper_type", "").strip()
    return jsonify(
        {
            "semesters": controller.get_semesters(),
            "subjects": controller.get_subjects(semester),
            "chapters": controller.get_chapter_counts(semester, subject),
            "paper_types": controller.get_paper_types(semester, subject),
            "sections": controller.get_sections(semester, subject, paper_type),
            "dataset_folder": str(controller.dataset_folder),
        }
    )


@app.post("/api/filter")
def filter_questions():
    payload = request.get_json(silent=True) or {}
    state = parse_state(payload)
    questions = controller.filter_questions(state)
    return jsonify(
        {
            "questions": [sanitize_question(question) for question in questions],
            "count": len(questions),
        }
    )


@app.post("/api/search")
def search_questions():
    payload = request.get_json(silent=True) or {}
    state = parse_state(payload)
    query = str(payload.get("query", "")).strip()
    filtered_questions = controller.filter_questions(state)
    results = controller.search_questions(query=query, filtered_questions=filtered_questions)
    return jsonify(
        {
            "questions": [sanitize_question(question) for question in results],
            "count": len(results),
            "filtered_count": len(filtered_questions),
        }
    )


@app.post("/api/open-dataset-folder")
def open_dataset_folder():
    folder = controller.dataset_folder
    try:
        if sys.platform.startswith("linux"):
            subprocess.Popen(["xdg-open", str(folder)])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(folder)])
        elif sys.platform.startswith("win"):
            subprocess.Popen(["explorer", str(folder)])
        else:
            return jsonify({"ok": False, "message": "Unsupported platform."}), 400
    except OSError as exc:
        return jsonify({"ok": False, "message": str(exc)}), 500
    return jsonify({"ok": True, "path": str(folder)})


def main() -> int:
    app.run(debug=False, host="127.0.0.1", port=5001)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
