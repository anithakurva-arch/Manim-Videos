import json
import re
import urllib.error
import urllib.request
import zipfile
from io import BytesIO
from pathlib import Path

from flask import Flask, Response, jsonify, render_template, request
from openpyxl import load_workbook


BASE_DIR = Path(__file__).parent.resolve()
SCRIPTS_DIR = BASE_DIR / "scripts"
PROMPTS_DIR = BASE_DIR / "backend_prompts"
MAX_REGENERATIONS = 3
DEFAULT_CLAUDE_MODEL = "claude-sonnet-4-5"

PROMPT_FILES = {
    "script_generation": "conceptual_script_generation.txt",
    "learning_design": "learning_design.txt",
    "lo_grouping": "lo_grouping.txt",
    "grouping_validation": "grouping_validation.txt",
    "validation": "validation_prompt.txt",
    "animation_phase": "animation_phase_master_prompt.txt",
}

PROMPT_META = {
    "lo_grouping": {
        "title": "LO Grouping Prompt",
        "stage": "Step 1",
        "purpose": "Groups selected Learning Outcomes into 2-minute conceptual script clusters.",
    },
    "grouping_validation": {
        "title": "Grouping Validation Prompt",
        "stage": "Step 1 QA",
        "purpose": "Validates LO grouping against completeness, no-duplication, and no-cross-CC rules.",
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
    "animation_phase": {
        "title": "Animation Phase Master Prompt",
        "stage": "Phase 2",
        "purpose": "Turns approved transcripts into storyboard, position table, and Manim Python code.",
    },
}

app = Flask(__name__)


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Claude-Key"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


def load_prompt(name):
    path = PROMPTS_DIR / PROMPT_FILES[name]
    return path.read_text(encoding="utf-8")


def fill_prompt(template, **values):
    output = template
    for key, value in values.items():
        output = output.replace("{{" + key + "}}", str(value))
        output = output.replace("{{" + key.upper() + "}}", str(value))
    return output


def get_claude_api_key():
    api_key = request.headers.get("X-Claude-Key", "").strip()
    if not api_key:
        payload = request.get_json(silent=True) or {}
        api_key = str(payload.get("claude_api_key", "")).strip()
    if not api_key:
        api_key = str(request.form.get("claude_api_key", "")).strip()
    if not api_key:
        raise ValueError("Missing Claude API key. Save your Claude key before running Phase 2.")
    return api_key


def call_claude(prompt, api_key, model=None, max_output_tokens=16000):
    body = json.dumps(
        {
            "model": model or DEFAULT_CLAUDE_MODEL,
            "max_tokens": max_output_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "content-type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ValueError(f"Claude API request failed: {detail}") from exc
    except urllib.error.URLError as exc:
        raise ValueError(f"Claude API request failed: {exc.reason}") from exc

    text_parts = []
    for block in data.get("content", []):
        if block.get("type") == "text":
            text_parts.append(block.get("text", ""))
    output = "\n".join(text_parts).strip()
    if not output:
        raise ValueError("Claude returned an empty response.")
    return output


def normalise_header(value):
    return re.sub(r"[^a-z0-9]+", "", str(value or "").strip().lower())


def find_column(headers, candidates):
    normalised = {normalise_header(header): index for index, header in enumerate(headers)}
    for candidate in candidates:
        key = normalise_header(candidate)
        if key in normalised:
            return normalised[key]
    return None


def find_columns(headers, candidates):
    normalised = {normalise_header(header): index for index, header in enumerate(headers)}
    matches = []
    for candidate in candidates:
        key = normalise_header(candidate)
        if key in normalised and normalised[key] not in matches:
            matches.append(normalised[key])
    return matches


def find_header_row(rows):
    best_index = None
    best_score = -1
    for index, row in enumerate(rows[:25]):
        headers = [str(cell or "").strip() for cell in row]
        score = 0
        if find_column(headers, GRADE_COLUMNS) is not None:
            score += 1
        if find_column(headers, CHAPTER_COLUMNS) is not None:
            score += 3
        if find_column(headers, SUBTOPIC_COLUMNS) is not None:
            score += 1
        if find_column(headers, LO_COLUMNS) is not None:
            score += 3
        if find_column(headers, SUBJECT_COLUMNS) is not None:
            score += 1
        if score > best_score:
            best_index = index
            best_score = score
    if best_score >= 6:
        return best_index
    return None


def row_value(row, index):
    if isinstance(index, (list, tuple)):
        for item in index:
            value = row_value(row, item)
            if value:
                return value
        return ""
    if index is None or index >= len(row):
        return ""
    value = row[index]
    return "" if value is None else str(value).strip()


GRADE_COLUMNS = ["gradeName", "Grade Name", "Grade", "Class", "Class Name", "Grade Level", "Class Level"]
SUBJECT_COLUMNS = ["subjectName", "Subject Name", "Subject"]
CHAPTER_COLUMNS = [
    "topicName",
    "Topic Name",
    "Chapter Name",
    "Chapter Names",
    "Chapter Title",
    "Chapter",
    "Topic",
    "Unit Name",
    "Unit",
    "Lesson",
    "Lesson Name",
    "Session",
    "Session Name",
]
SUBTOPIC_COLUMNS = [
    "subTopicName",
    "Subtopic Name",
    "Sub Topic",
    "Sub-Topic",
    "Subtopic",
    "Subtopic Title",
    "KnowledgeCellName",
    "Knowledge Cell Name",
    "Concept Name",
    "Concept",
]
CC_COLUMNS = ["KnowledgeCellId", "Knowledge Cell Id", "CC", "C.C.", "Competency Code", "Concept Code", "Content Code", "Chapter Code"]
CC_NAME_COLUMNS = ["KnowledgeCellName", "Knowledge Cell Name", "CC Name", "Competency Name", "Competency", "Concept Name", "Concept", "Content"]
LO_COLUMNS = [
    "LearningOutcomeName",
    "Learning Outcome Name",
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
    workbook = load_workbook(BytesIO(file_storage.read()), read_only=True, data_only=True)
    selected_sheet = None
    preview_rows = []
    header_index = None
    try:
        for candidate_sheet in workbook.worksheets:
            candidate_preview = []
            for row_index, row in enumerate(candidate_sheet.iter_rows(values_only=True)):
                if row_index >= 25:
                    break
                candidate_preview.append(row)
            candidate_header_index = find_header_row(candidate_preview)
            if candidate_header_index is not None:
                selected_sheet = candidate_sheet
                preview_rows = candidate_preview
                header_index = candidate_header_index
                break

        if selected_sheet is None:
            selected_sheet = workbook.active
            preview_rows = []
            for row_index, row in enumerate(selected_sheet.iter_rows(values_only=True)):
                if row_index >= 25:
                    break
                preview_rows.append(row)
            header_index = find_header_row(preview_rows)

        if not preview_rows:
            return []

        if header_index is None:
            preview_headers = [str(cell or "").strip() for cell in preview_rows[0] if str(cell or "").strip()]
            raise ValueError(
                "Could not find the header row. Expected columns like Chapter/Topic and Learning Outcome. "
                + "Optional columns include Grade/Class, Subject, and Subtopic/Sub Topic. "
                + "First row detected: "
                + (", ".join(preview_headers) if preview_headers else "blank")
            )

        headers = [str(cell or "").strip() for cell in preview_rows[header_index]]
        columns = {
            "grade": find_columns(headers, GRADE_COLUMNS),
            "subject": find_columns(headers, SUBJECT_COLUMNS),
            "chapter": find_columns(headers, CHAPTER_COLUMNS),
            "subtopic": find_columns(headers, SUBTOPIC_COLUMNS),
            "cc": find_columns(headers, CC_COLUMNS),
            "cc_name": find_columns(headers, CC_NAME_COLUMNS),
            "lo": find_columns(headers, LO_COLUMNS),
        }

        required = ["chapter", "lo"]
        missing = [name for name in required if not columns[name]]
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
            "grade": "All Grades",
            "subject": "Mathematics",
            "chapter": "",
            "subtopic": "",
            "cc": "CC 01",
            "cc_name": "",
        }
        seen_learning_outcomes = set()
        for row_number, row in enumerate(selected_sheet.iter_rows(values_only=True), start=1):
            if row_number <= header_index + 1:
                continue
            for field in last_values:
                value = row_value(row, columns.get(field))
                if value:
                    last_values[field] = value
            if not last_values["chapter"]:
                continue
            lo_text = row_value(row, columns["lo"])
            if not lo_text:
                continue
            item_key = (
                last_values["grade"],
                last_values["subject"],
                last_values["chapter"],
                last_values["subtopic"],
                lo_text,
            )
            if item_key in seen_learning_outcomes:
                continue
            seen_learning_outcomes.add(item_key)
            parsed.append(
                {
                    "row": row_number,
                    "grade": last_values["grade"] or "All Grades",
                    "subject": last_values["subject"] or "Mathematics",
                    "chapter": last_values["chapter"],
                    "subtopic": last_values["subtopic"],
                    "cc": last_values["cc"] or "CC 01",
                    "cc_name": last_values["cc_name"] or "Learning Outcomes",
                    "lo": lo_text,
                    "source": "learning_outcome",
                }
            )
        if not parsed:
            raise ValueError("No Learning Outcome rows found below the detected header row.")
        return parsed
    finally:
        workbook.close()


def filters_for(rows):
    def unique(key, items):
        return sorted({row[key] for row in items if row.get(key)})

    grades = unique("grade", rows)
    all_chapters = unique("chapter", rows)
    all_subtopics = unique("subtopic", rows)
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
        "allChapters": all_chapters,
        "allSubtopics": all_subtopics,
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
        "No textbook PDF has been attached in Phase 1. Validate against the selected Learning Outcomes, "
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


def animation_metadata(payload):
    title = str(payload.get("title") or payload.get("chapter") or "Concept Animation").strip()
    return {
        "title": title,
        "subject": str(payload.get("subject") or "Mathematics").strip(),
        "grade": str(payload.get("grade") or "").strip(),
        "duration": str(payload.get("duration") or "90 seconds").strip(),
        "content_type": str(payload.get("contentType") or "Concept Video").strip(),
    }


def animation_prompt(payload, mode):
    transcript = str(payload.get("transcript") or "").strip()
    if not transcript:
        raise ValueError("Paste a transcript or use the approved script first.")

    meta = animation_metadata(payload)
    master_prompt = load_prompt("animation_phase")
    stage_instruction = {
        "storyboard": (
            "Run only STEP 0, STEP 1, STEP 2, STEP 3a, STEP 3b, and the pre-code/audit planning items "
            "needed for the storyboard. Do not output Python code."
        ),
        "code": (
            "Using the transcript and storyboard below, output STEP 4 only: raw production-ready Python code. "
            "Do not wrap the code in markdown fences. Do not include prose before or after the Python."
        ),
        "package": (
            "Run the full pipeline in the final output order: STEP 0, STEP 1, STEP 2, STEP 3a, STEP 3b, "
            "STEP 4, STEP 5, and STEP 6."
        ),
    }[mode]

    storyboard = str(payload.get("storyboard") or "").strip()
    storyboard_block = f"\n\nEXISTING STORYBOARD PACKAGE:\n{storyboard}\n" if storyboard else ""
    return (
        f"{master_prompt}\n\n"
        "USER INPUT FOR THIS RUN:\n"
        f'INPUT:\n"""\n{transcript}\n"""\n\n'
        "METADATA:\n"
        f"Title: {meta['title']}\n"
        f"Subject: {meta['subject']}\n"
        f"Grade: {meta['grade']}\n"
        f"Duration: {meta['duration']}\n"
        f"Content Type: {meta['content_type']}\n"
        f"{storyboard_block}\n"
        "EXECUTION MODE:\n"
        f"{stage_instruction}"
    )


def extract_python_code(text):
    fenced = re.search(r"```(?:python)?\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
    return fenced.group(1).strip() if fenced else text.strip()


def slugify_filename(value, fallback="animation"):
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", str(value or "").strip().lower()).strip("_")
    return slug[:80] or fallback


def unique_python_filename(outcome, used_names):
    parts = [
        outcome.get("grade"),
        outcome.get("chapter"),
        outcome.get("subtopic"),
        outcome.get("cc"),
        f"row_{outcome.get('row')}" if outcome.get("row") else "",
    ]
    base = slugify_filename("_".join(str(part) for part in parts if part), "animation_scene")
    filename = f"{base}.py"
    counter = 2
    while filename in used_names:
        filename = f"{base}_{counter}.py"
        counter += 1
    used_names.add(filename)
    return filename


def animation_title_for_outcome(outcome):
    return " - ".join(
        str(part)
        for part in [outcome.get("chapter"), outcome.get("subtopic"), outcome.get("cc")]
        if part
    ) or "Concept Animation"


def bulk_groups_from_outcomes(outcomes):
    grouped = {}
    for outcome in outcomes:
        key = (
            outcome.get("grade") or "",
            outcome.get("subject") or "Mathematics",
            outcome.get("chapter") or "",
            outcome.get("subtopic") or "",
            outcome.get("cc") or "",
            outcome.get("cc_name") or "",
        )
        if key not in grouped:
            grouped[key] = {
                "grade": key[0],
                "subject": key[1],
                "chapter": key[2],
                "subtopic": key[3],
                "cc": key[4],
                "cc_name": key[5],
                "rows": [],
                "outcomes": [],
            }
        grouped[key]["rows"].append(outcome.get("row"))
        grouped[key]["outcomes"].append(outcome)
    return list(grouped.values())


def group_filename_seed(group):
    rows = [str(row) for row in group.get("rows", []) if row]
    return {
        "grade": group.get("grade"),
        "chapter": group.get("chapter"),
        "subtopic": group.get("subtopic"),
        "cc": group.get("cc"),
        "row": rows[0] if rows else None,
    }


def bulk_learning_outcomes_text(outcomes):
    return "\n".join(
        f"LO {index}. {outcome.get('lo', '')}"
        for index, outcome in enumerate(outcomes, start=1)
        if outcome.get("lo")
    )


def grouping_validation_prompt(grade, chapter, ccs_and_los, grouping_table):
    return fill_prompt(
        load_prompt("grouping_validation"),
        Grade=grade,
        ChapterName=chapter,
        CCsAndLOs=ccs_and_los,
        GroupingTable=grouping_table,
    )


def grouping_validation_status(report):
    verdict = str(report or "").upper()
    if "REJECTED" in verdict:
        return "Rejected"
    if "NEEDS MINOR REVISION" in verdict:
        return "Needs Minor Revision"
    if "APPROVED" in verdict:
        return "Approved"
    return "Needs Review"


def grouped_script_blocks(grouping_text):
    text = str(grouping_text or "").strip()
    if not text:
        return []
    matches = list(re.finditer(r"(?im)^\s*(Script\s+\d+\s+CC\s+[A-Za-z0-9._-]+.*?)\s*$", text))
    if not matches:
        return [{"title": "Script 1", "learningOutcomes": text}]

    blocks = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[start:end].strip()
        title = match.group(1).strip()
        if block:
            blocks.append({"title": title, "learningOutcomes": block})
    return blocks


@app.get("/")
def index():
    return render_template(
        "index.html",
        max_regenerations=MAX_REGENERATIONS,
        default_claude_model=DEFAULT_CLAUDE_MODEL,
    )


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api")
def api():
    return jsonify(
        {
            "service": "Conceptual Script Generator",
            "status": "ok",
            "phase": "1+2",
            "max_regenerations": MAX_REGENERATIONS,
            "default_claude_model": DEFAULT_CLAUDE_MODEL,
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


@app.post("/api/validate-key")
@app.post("/api/validate-claude-key")
def validate_claude_key_route():
    try:
        api_key = get_claude_api_key()
        call_claude("Reply with only OK.", api_key, max_output_tokens=16)
    except Exception as exc:
        return jsonify({"valid": False, "error": "Claude API key validation failed: " + str(exc)}), 400
    return jsonify({"valid": True, "message": "Claude API key is valid."})


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
        api_key = get_claude_api_key()
        text = call_claude(prompt, api_key, payload.get("claudeModel"), max_output_tokens=5000)
        validation = call_claude(
            grouping_validation_prompt(grade, chapter, ccs_and_los, text),
            api_key,
            payload.get("claudeModel"),
            max_output_tokens=5000,
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(
        {
            "grouping": text,
            "groupingValidation": validation,
            "groupingStatus": grouping_validation_status(validation),
            "groups": grouped_script_blocks(text),
            "promptUsed": "lo_grouping",
            "validationPromptUsed": "grouping_validation",
        }
    )


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
        script = call_claude(prompt, get_claude_api_key(), payload.get("claudeModel"), max_output_tokens=8000)
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
        report = call_claude(prompt, get_claude_api_key(), payload.get("claudeModel"), max_output_tokens=8000)
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
        script = call_claude(prompt, get_claude_api_key(), payload.get("claudeModel"), max_output_tokens=8000)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"script": script, "attempt": attempt})


@app.post("/api/run-approved")
def run_approved_route():
    payload = request.get_json(force=True)
    outcomes_text = payload.get("learningOutcomes", "").strip()
    if not outcomes_text:
        return jsonify({"error": "Missing grouped Learning Outcomes."}), 400

    try:
        api_key = get_claude_api_key()
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400
    model = payload.get("claudeModel")
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
            script = call_claude(prompt, api_key, model, max_output_tokens=8000)
            report = call_claude(
                validation_prompt(grade, chapter, subtopic, outcomes_text, script, textbook_reference),
                api_key,
                model,
                max_output_tokens=8000,
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


@app.post("/api/animation/storyboard")
def animation_storyboard_route():
    payload = request.get_json(force=True)
    try:
        prompt = animation_prompt(payload, "storyboard")
        storyboard = call_claude(
            prompt,
            get_claude_api_key(),
            payload.get("claudeModel"),
            max_output_tokens=int(payload.get("maxTokens") or 16000),
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(
        {
            "storyboard": storyboard,
            "model": payload.get("claudeModel") or DEFAULT_CLAUDE_MODEL,
            "promptUsed": "animation_phase",
        }
    )


@app.post("/api/animation/code")
def animation_code_route():
    payload = request.get_json(force=True)
    try:
        prompt = animation_prompt(payload, "code")
        raw_code = call_claude(
            prompt,
            get_claude_api_key(),
            payload.get("claudeModel"),
            max_output_tokens=int(payload.get("maxTokens") or 24000),
        )
        code = extract_python_code(raw_code)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(
        {
            "code": code,
            "raw": raw_code,
            "model": payload.get("claudeModel") or DEFAULT_CLAUDE_MODEL,
            "promptUsed": "animation_phase",
        }
    )


@app.post("/api/animation/package")
def animation_package_route():
    payload = request.get_json(force=True)
    try:
        prompt = animation_prompt(payload, "package")
        package = call_claude(
            prompt,
            get_claude_api_key(),
            payload.get("claudeModel"),
            max_output_tokens=int(payload.get("maxTokens") or 30000),
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(
        {
            "package": package,
            "code": extract_python_code(package),
            "model": payload.get("claudeModel") or DEFAULT_CLAUDE_MODEL,
            "promptUsed": "animation_phase",
        }
    )


@app.post("/api/bulk/python-scripts")
def bulk_python_scripts_route():
    payload = request.get_json(force=True)
    outcomes = payload.get("outcomes") or []
    if not outcomes:
        return jsonify({"error": "Select at least one Learning Outcome for bulk generation."}), 400

    try:
        api_key = get_claude_api_key()
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400
    model = payload.get("claudeModel")
    duration = payload.get("duration") or "90 seconds"
    content_type = payload.get("contentType") or "Concept Video"
    groups = bulk_groups_from_outcomes(outcomes)
    max_items = int(payload.get("maxItems") or len(groups))
    selected_groups = groups[:max_items]

    used_names = set()
    manifest = []
    archive_buffer = BytesIO()

    with zipfile.ZipFile(archive_buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for index, group in enumerate(selected_groups, start=1):
            grade = str(group.get("grade") or payload.get("grade") or "").strip()
            chapter = str(group.get("chapter") or payload.get("chapter") or "").strip()
            subtopic = str(group.get("subtopic") or payload.get("subtopic") or "").strip()
            title = animation_title_for_outcome(group)
            outcomes_text = bulk_learning_outcomes_text(group["outcomes"])
            filename = unique_python_filename(group_filename_seed(group), used_names)
            stem = filename[:-3]
            if not outcomes_text:
                manifest.append({"index": index, "status": "skipped", "title": title, "error": "Missing Learning Outcome text."})
                continue

            try:
                grouped_los = call_claude(
                    fill_prompt(
                        load_prompt("lo_grouping"),
                        Grade=grade,
                        ChapterName=chapter,
                        CCsAndLOs=format_ccs_and_los(group["outcomes"]),
                    ),
                    api_key,
                    model,
                    max_output_tokens=8000,
                )

                transcript = ""
                validation_report = ""
                status = "Not Started"
                for attempt in range(1, MAX_REGENERATIONS + 1):
                    if attempt == 1:
                        transcript_prompt = script_prompt(grade, chapter, subtopic, grouped_los)
                    else:
                        transcript_prompt = (
                            script_prompt(grade, chapter, subtopic, grouped_los)
                            + "\n\nThe previous transcript was not approved. Regenerate using this validation report.\n\n"
                            + f"Previous Transcript:\n{transcript}\n\nValidation Report:\n{validation_report}\n\n"
                            + f"This is regeneration attempt {attempt} of {MAX_REGENERATIONS}."
                        )
                    transcript = call_claude(transcript_prompt, api_key, model, max_output_tokens=8000)
                    validation_report = call_claude(
                        validation_prompt(grade, chapter, subtopic, grouped_los, transcript, payload.get("textbookReference", "")),
                        api_key,
                        model,
                        max_output_tokens=8000,
                    )
                    status = extract_verdict(validation_report)
                    if status == "Approved":
                        break

                archive.writestr(f"{stem}_grouped_los.txt", grouped_los)
                archive.writestr(f"{stem}_validated_transcript.txt", transcript)
                archive.writestr(f"{stem}_validation_report.txt", validation_report)

                if status != "Approved":
                    manifest.append(
                        {
                            "index": index,
                            "status": "validation_failed",
                            "validation_status": status,
                            "title": title,
                            "rows": group.get("rows"),
                            "transcript": f"{stem}_validated_transcript.txt",
                            "validation_report": f"{stem}_validation_report.txt",
                        }
                    )
                    continue

                storyboard = call_claude(
                    animation_prompt(
                        {
                            "transcript": transcript,
                            "title": title,
                            "subject": group.get("subject") or "Mathematics",
                            "grade": grade,
                            "duration": duration,
                            "contentType": content_type,
                        },
                        "storyboard",
                    ),
                    api_key,
                    model,
                    max_output_tokens=16000,
                )
                code_response = call_claude(
                    animation_prompt(
                        {
                            "transcript": transcript,
                            "title": title,
                            "subject": group.get("subject") or "Mathematics",
                            "grade": grade,
                            "duration": duration,
                            "contentType": content_type,
                            "storyboard": storyboard,
                        },
                        "code",
                    ),
                    api_key,
                    model,
                    max_output_tokens=24000,
                )
                archive.writestr(f"{stem}_storyboard.txt", storyboard)
                archive.writestr(filename, extract_python_code(code_response) + "\n")
                manifest.append(
                    {
                        "index": index,
                        "status": "generated",
                        "validation_status": status,
                        "filename": filename,
                        "title": title,
                        "grade": grade,
                        "chapter": chapter,
                        "subtopic": subtopic,
                        "rows": group.get("rows"),
                        "grouped_los": f"{stem}_grouped_los.txt",
                        "validated_transcript": f"{stem}_validated_transcript.txt",
                        "validation_report": f"{stem}_validation_report.txt",
                        "storyboard": f"{stem}_storyboard.txt",
                    }
                )
            except Exception as exc:
                manifest.append(
                    {
                        "index": index,
                        "status": "failed",
                        "title": title,
                        "rows": group.get("rows"),
                        "error": str(exc),
                    }
                )

        archive.writestr("manifest.json", json.dumps({"items": manifest}, ensure_ascii=False, indent=2))

    archive_buffer.seek(0)
    return Response(
        archive_buffer.getvalue(),
        mimetype="application/zip",
        headers={"Content-Disposition": "attachment; filename=bulk_python_scripts.zip"},
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
