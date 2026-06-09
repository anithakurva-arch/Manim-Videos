import json
import re
from io import BytesIO
from pathlib import Path

from flask import Flask, Response, jsonify, render_template, request
from openai import OpenAI
from openpyxl import load_workbook


BASE_DIR = Path(__file__).parent.resolve()
SCRIPTS_DIR = BASE_DIR / "scripts"
PROMPTS_DIR = BASE_DIR / "backend_prompts"
MAX_REGENERATIONS = 3
DEFAULT_MODEL = "gpt-4.1-mini"

PROMPT_FILES = {
    "script_generation": "conceptual_script_generation.txt",
    "learning_design": "learning_design.txt",
    "lo_grouping": "lo_grouping.txt",
    "validation": "validation_prompt.txt",
}

PROMPT_META = {
    "lo_grouping": {
        "title": "LO Grouping Prompt",
        "stage": "Step 1",
        "purpose": "Groups selected Learning Outcomes into 2-minute conceptual script clusters.",
    },
    "script_generation": {
        "title": "Generation Prompt Conceptual Script",
        "stage": "Step 2",
        "purpose": "Generates voice-over-ready conceptual scripts from grouped Learning Outcomes.",
    },
    "learning_design": {
        "title": "Learning Design Final",
        "stage": "Blueprint",
        "purpose": "Defines the instructional framework used inside script generation.",
    },
    "validation": {
        "title": "Validation Prompt v2 Updated",
        "stage": "Step 3",
        "purpose": "Validates scripts and drives capped regeneration until approval.",
    },
}

app = Flask(__name__)


def load_prompt(name):
    path = PROMPTS_DIR / PROMPT_FILES[name]
    return path.read_text(encoding="utf-8")


def fill_prompt(template, **values):
    output = template
    for key, value in values.items():
        output = output.replace("{{" + key + "}}", str(value))
        output = output.replace("{{" + key.upper() + "}}", str(value))
    return output


def get_api_key():
    api_key = request.headers.get("X-OpenAI-Key", "").strip()
    if not api_key:
        payload = request.get_json(silent=True) or {}
        api_key = str(payload.get("api_key", "")).strip()
    if not api_key:
        raise ValueError("Missing API key. Save your key in the app before running AI stages.")
    return api_key


def call_openai(prompt, api_key, model=None, max_output_tokens=5000):
    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=model or DEFAULT_MODEL,
        input=prompt,
        max_output_tokens=max_output_tokens,
    )
    return response.output_text


def normalise_header(value):
    return re.sub(r"[^a-z0-9]+", "", str(value or "").strip().lower())


def find_column(headers, candidates):
    normalised = {normalise_header(header): index for index, header in enumerate(headers)}
    for candidate in candidates:
        key = normalise_header(candidate)
        if key in normalised:
            return normalised[key]
    return None


def find_header_row(rows):
    best_index = None
    best_score = -1
    for index, row in enumerate(rows[:25]):
        headers = [str(cell or "").strip() for cell in row]
        score = 0
        if find_column(headers, GRADE_COLUMNS) is not None:
            score += 1
        if find_column(headers, CHAPTER_COLUMNS) is not None:
            score += 1
        if find_column(headers, SUBTOPIC_COLUMNS) is not None:
            score += 1
        if find_column(headers, LO_COLUMNS) is not None:
            score += 3
        if find_column(headers, SUBJECT_COLUMNS) is not None:
            score += 1
        if score > best_score:
            best_index = index
            best_score = score
    if best_score >= 4:
        return best_index
    return None


def row_value(row, index):
    if index is None or index >= len(row):
        return ""
    value = row[index]
    return "" if value is None else str(value).strip()


GRADE_COLUMNS = ["Grade", "Class", "Grade Level", "Class Level"]
SUBJECT_COLUMNS = ["Subject", "Subject Name"]
CHAPTER_COLUMNS = ["Chapter", "Chapter Name", "Topic", "Topic Name", "Unit", "Unit Name"]
SUBTOPIC_COLUMNS = ["Subtopic", "Subtopic Name", "Sub Topic", "Sub-Topic", "Concept", "Concept Name"]
CC_COLUMNS = ["CC", "C.C.", "Competency Code", "Concept Code", "Content Code", "Chapter Code"]
CC_NAME_COLUMNS = ["CC Name", "Competency", "Competency Name", "Concept", "Concept Name", "Content"]
LO_COLUMNS = [
    "Learning Outcome",
    "Learning Outcomes",
    "LO",
    "LO Text",
    "Outcome",
    "Learning Objective",
    "Learning Objectives",
    "LearningOutcomes",
    "LearningOutcomesText",
]


def parse_excel(file_storage):
    workbook = load_workbook(BytesIO(file_storage.read()), data_only=True)
    sheet = None
    rows = []
    header_index = None
    for candidate_sheet in workbook.worksheets:
        candidate_rows = list(candidate_sheet.iter_rows(values_only=True))
        candidate_header_index = find_header_row(candidate_rows)
        if candidate_header_index is not None:
            sheet = candidate_sheet
            rows = candidate_rows
            header_index = candidate_header_index
            break

    if sheet is None:
        sheet = workbook.active
        rows = list(sheet.iter_rows(values_only=True))

    if not rows:
        return []

    if header_index is None:
        header_index = find_header_row(rows)
    if header_index is None:
        preview_headers = [str(cell or "").strip() for cell in rows[0] if str(cell or "").strip()]
        raise ValueError(
            "Could not find the header row. Expected columns like Grade, Chapter, Subtopic, and Learning Outcome. "
            + "First row detected: "
            + (", ".join(preview_headers) if preview_headers else "blank")
        )

    headers = [str(cell or "").strip() for cell in rows[header_index]]
    columns = {
        "grade": find_column(headers, GRADE_COLUMNS),
        "subject": find_column(headers, SUBJECT_COLUMNS),
        "chapter": find_column(headers, CHAPTER_COLUMNS),
        "subtopic": find_column(headers, SUBTOPIC_COLUMNS),
        "cc": find_column(headers, CC_COLUMNS),
        "cc_name": find_column(headers, CC_NAME_COLUMNS),
        "lo": find_column(headers, LO_COLUMNS),
    }

    required = ["grade", "chapter", "subtopic", "lo"]
    missing = [name for name in required if columns[name] is None]
    if missing:
        detected = [header for header in headers if header]
        raise ValueError(
            "Missing required column(s): "
            + ", ".join(missing)
            + ". Detected headers: "
            + (", ".join(detected) if detected else "none")
        )

    parsed = []
    last_values = {
        "grade": "",
        "subject": "Mathematics",
        "chapter": "",
        "subtopic": "",
        "cc": "CC 01",
        "cc_name": "Learning Outcomes",
    }
    for index, row in enumerate(rows[header_index + 1 :], start=header_index + 2):
        lo_text = row_value(row, columns["lo"])
        if not lo_text:
            continue
        for field in last_values:
            value = row_value(row, columns.get(field))
            if value:
                last_values[field] = value
        parsed.append(
            {
                "row": index,
                "grade": last_values["grade"],
                "subject": last_values["subject"] or "Mathematics",
                "chapter": last_values["chapter"],
                "subtopic": last_values["subtopic"],
                "cc": last_values["cc"] or "CC 01",
                "cc_name": last_values["cc_name"] or "Learning Outcomes",
                "lo": lo_text,
            }
        )
    if not parsed:
        raise ValueError("No Learning Outcome rows found below the detected header row.")
    return parsed


def filters_for(rows):
    def unique(key, items):
        return sorted({row[key] for row in items if row.get(key)})

    grades = unique("grade", rows)
    chapters_by_grade = {}
    subtopics_by_chapter = {}
    for grade in grades:
        grade_rows = [row for row in rows if row["grade"] == grade]
        chapters_by_grade[grade] = unique("chapter", grade_rows)
        for chapter in chapters_by_grade[grade]:
            chapter_key = f"{grade}||{chapter}"
            subtopics_by_chapter[chapter_key] = unique(
                "subtopic", [row for row in grade_rows if row["chapter"] == chapter]
            )
    return {
        "grades": grades,
        "chaptersByGrade": chapters_by_grade,
        "subtopicsByChapter": subtopics_by_chapter,
    }


def format_ccs_and_los(outcomes):
    grouped = {}
    for outcome in outcomes:
        cc = outcome.get("cc") or "CC 01"
        cc_name = outcome.get("cc_name") or "Learning Outcomes"
        grouped.setdefault((cc, cc_name), []).append(outcome.get("lo", ""))

    blocks = []
    for (cc, cc_name), los in grouped.items():
        lines = [f"{cc} {cc_name}"]
        lines.extend(f"LO {index}. {lo}" for index, lo in enumerate(los, start=1))
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def extract_verdict(report):
    verdict_match = re.search(r"#?\s*VERDICT\s*(.*)$", report, flags=re.IGNORECASE | re.DOTALL)
    verdict_text = verdict_match.group(1) if verdict_match else report[-1000:]
    verdict_text = verdict_text.lower()
    if "approved" in verdict_text and "ready" in verdict_text:
        return "Approved"
    if "needs minor revision" in verdict_text or "minor revision" in verdict_text:
        return "Needs Minor Revision"
    if "rejected" in verdict_text or "regenerate" in verdict_text:
        return "Rejected"
    if "approved" in verdict_text:
        return "Approved"
    return "Needs Review"


def script_prompt(grade, chapter, subtopic, outcomes_text):
    generation = fill_prompt(
        load_prompt("script_generation"),
        Grade=grade,
        ChapterName=chapter,
        SubtopicName=subtopic,
        LearningOutcomes=outcomes_text,
    )
    learning_design = load_prompt("learning_design")
    return (
        "Use the following Learning Design as the instructional blueprint.\n\n"
        f"{learning_design}\n\n"
        "Now generate the conceptual script using this generation prompt.\n\n"
        f"{generation}"
    )


def validation_prompt(grade, chapter, subtopic, outcomes_text, script, textbook_reference=""):
    textbook_reference = textbook_reference or (
        "No textbook PDF has been attached in Phase 1. Validate against the Learning Outcomes, "
        "the Learning Design, and mathematical correctness. Do not invent page references."
    )
    return fill_prompt(
        load_prompt("validation"),
        GRADE=grade,
        TOPIC=chapter,
        SUBTOPIC=subtopic,
        LEARNING_OUTCOMES=outcomes_text,
        SCRIPT_TO_REVIEW=script,
        ATTACHED_TEXTBOOK_PDF=textbook_reference,
    )


@app.get("/")
def index():
    return render_template("index.html", max_regenerations=MAX_REGENERATIONS, default_model=DEFAULT_MODEL)


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api")
def api():
    return jsonify(
        {
            "service": "Conceptual Script Generator",
            "status": "ok",
            "phase": 1,
            "max_regenerations": MAX_REGENERATIONS,
            "default_model": DEFAULT_MODEL,
            "prompts": sorted(PROMPT_FILES),
            "media_storage": "local-only; media/ is intentionally not tracked in Git",
        }
    )


@app.get("/api/prompts")
def prompts_route():
    prompts = []
    for key, meta in PROMPT_META.items():
        text = load_prompt(key)
        prompts.append(
            {
                "key": key,
                "title": meta["title"],
                "stage": meta["stage"],
                "purpose": meta["purpose"],
                "characters": len(text),
            }
        )
    return jsonify({"prompts": prompts})


@app.get("/api/prompts/<name>")
def prompt_detail_route(name):
    if name not in PROMPT_FILES:
        return jsonify({"error": "Unknown prompt."}), 404
    meta = PROMPT_META[name]
    return jsonify(
        {
            "key": name,
            "title": meta["title"],
            "stage": meta["stage"],
            "purpose": meta["purpose"],
            "text": load_prompt(name),
        }
    )


@app.post("/api/parse-excel")
def parse_excel_route():
    if "file" not in request.files:
        return jsonify({"error": "Upload an Excel file first."}), 400
    try:
        rows = parse_excel(request.files["file"])
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"rows": rows, "filters": filters_for(rows)})


@app.post("/api/group")
def group_route():
    payload = request.get_json(force=True)
    outcomes = payload.get("outcomes") or []
    if not outcomes:
        return jsonify({"error": "Select at least one Learning Outcome."}), 400
    grade = payload.get("grade", "")
    chapter = payload.get("chapter", "")
    ccs_and_los = format_ccs_and_los(outcomes)
    prompt = fill_prompt(
        load_prompt("lo_grouping"),
        Grade=grade,
        ChapterName=chapter,
        CCsAndLOs=ccs_and_los,
    )
    try:
        text = call_openai(prompt, get_api_key(), payload.get("model"))
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"grouping": text, "promptUsed": "lo_grouping"})


@app.post("/api/generate")
def generate_route():
    payload = request.get_json(force=True)
    outcomes_text = payload.get("learningOutcomes", "").strip()
    if not outcomes_text:
        return jsonify({"error": "Missing grouped Learning Outcomes."}), 400
    prompt = script_prompt(
        payload.get("grade", ""),
        payload.get("chapter", ""),
        payload.get("subtopic", ""),
        outcomes_text,
    )
    try:
        script = call_openai(prompt, get_api_key(), payload.get("model"), max_output_tokens=3500)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"script": script, "attempt": 1})


@app.post("/api/validate")
def validate_route():
    payload = request.get_json(force=True)
    script = payload.get("script", "").strip()
    outcomes_text = payload.get("learningOutcomes", "").strip()
    if not script or not outcomes_text:
        return jsonify({"error": "Missing script or Learning Outcomes for validation."}), 400
    prompt = validation_prompt(
        payload.get("grade", ""),
        payload.get("chapter", ""),
        payload.get("subtopic", ""),
        outcomes_text,
        script,
        payload.get("textbookReference", ""),
    )
    try:
        report = call_openai(prompt, get_api_key(), payload.get("model"), max_output_tokens=5000)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"report": report, "status": extract_verdict(report)})


@app.post("/api/revise")
def revise_route():
    payload = request.get_json(force=True)
    attempt = int(payload.get("attempt", 1))
    if attempt > MAX_REGENERATIONS:
        return jsonify({"error": "Maximum regeneration limit reached.", "max": MAX_REGENERATIONS}), 400

    outcomes_text = payload.get("learningOutcomes", "").strip()
    previous_script = payload.get("script", "").strip()
    report = payload.get("validationReport", "").strip()
    if not outcomes_text or not previous_script or not report:
        return jsonify({"error": "Missing script, Learning Outcomes, or validation report."}), 400

    prompt = (
        script_prompt(
            payload.get("grade", ""),
            payload.get("chapter", ""),
            payload.get("subtopic", ""),
            outcomes_text,
        )
        + "\n\nThe previous script was not approved. Regenerate a corrected version using the validation report below.\n"
        + "Do not preserve rejected lines. Produce only a fresh final script that can pass validation.\n\n"
        + f"Previous Script:\n{previous_script}\n\nValidation Report:\n{report}\n\n"
        + f"This is regeneration attempt {attempt} of {MAX_REGENERATIONS}."
    )
    try:
        script = call_openai(prompt, get_api_key(), payload.get("model"), max_output_tokens=3500)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"script": script, "attempt": attempt})


@app.post("/api/run-approved")
def run_approved_route():
    payload = request.get_json(force=True)
    outcomes_text = payload.get("learningOutcomes", "").strip()
    if not outcomes_text:
        return jsonify({"error": "Missing grouped Learning Outcomes."}), 400

    api_key = get_api_key()
    model = payload.get("model")
    grade = payload.get("grade", "")
    chapter = payload.get("chapter", "")
    subtopic = payload.get("subtopic", "")
    textbook_reference = payload.get("textbookReference", "")

    history = []
    script = ""
    report = ""
    status = "Not Started"

    for attempt in range(1, MAX_REGENERATIONS + 1):
        if attempt == 1:
            prompt = script_prompt(grade, chapter, subtopic, outcomes_text)
        else:
            prompt = (
                script_prompt(grade, chapter, subtopic, outcomes_text)
                + "\n\nRegenerate using the previous validation report. Produce a fresh approved script.\n\n"
                + f"Previous Script:\n{script}\n\nValidation Report:\n{report}\n\n"
                + f"This is regeneration attempt {attempt} of {MAX_REGENERATIONS}."
            )
        try:
            script = call_openai(prompt, api_key, model, max_output_tokens=3500)
            report = call_openai(
                validation_prompt(grade, chapter, subtopic, outcomes_text, script, textbook_reference),
                api_key,
                model,
                max_output_tokens=5000,
            )
        except Exception as exc:
            return jsonify({"error": str(exc), "history": history}), 400

        status = extract_verdict(report)
        history.append({"attempt": attempt, "status": status, "script": script, "validationReport": report})
        if status == "Approved":
            break

    return jsonify(
        {
            "status": status,
            "approved": status == "Approved",
            "attemptsUsed": len(history),
            "maxRegenerations": MAX_REGENERATIONS,
            "script": script,
            "validationReport": report,
            "history": history,
        }
    )


@app.post("/api/download")
def download_route():
    payload = request.get_json(force=True)
    scripts = payload.get("scripts") or []
    approved = [script for script in scripts if script.get("status") == "Approved"]
    if len(approved) != len(scripts):
        return jsonify({"error": "Download is blocked until every selected script is Approved."}), 400
    body = json.dumps({"approved_scripts": approved}, ensure_ascii=False, indent=2)
    return Response(
        body,
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=approved_conceptual_scripts.json"},
    )
