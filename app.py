from pathlib import Path

from flask import Flask, jsonify


BASE_DIR = Path(__file__).parent.resolve()
SCRIPTS_DIR = BASE_DIR / "scripts"

app = Flask(__name__)


@app.get("/")
def index():
    scripts = sorted(path.name for path in SCRIPTS_DIR.glob("*.py"))
    return jsonify(
        {
            "service": "Manim Videos",
            "status": "ok",
            "scripts": scripts,
            "media_storage": "local-only; media/ is intentionally not tracked in Git",
        }
    )


@app.get("/health")
def health():
    return jsonify({"status": "ok"})
