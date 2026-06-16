import argparse
import os
import sys
import subprocess
import re
import time
import json
from pathlib import Path
from datetime import datetime

BASE_DIR        = Path(__file__).parent.resolve()
DEFAULT_SCRIPTS = Path(os.environ.get("MANIM_SCRIPTS_DIR", BASE_DIR / "scripts")).expanduser()
DEFAULT_MEDIA   = BASE_DIR / "media"
LOG_DIR         = BASE_DIR / "logs"
RESULTS_FILE    = BASE_DIR / "run_results.json"


class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    GREEN  = "\033[92m"
    ORANGE = "\033[93m"
    RED    = "\033[91m"
    BLUE   = "\033[94m"
    PURPLE = "\033[95m"
    CYAN   = "\033[96m"
    GREY   = "\033[90m"
    WHITE  = "\033[97m"


def ok(msg):   print(f"{C.GREEN}  [OK]  {msg}{C.RESET}")
def info(msg): print(f"{C.BLUE}  [..]  {msg}{C.RESET}")
def warn(msg): print(f"{C.ORANGE}  [!!]  {msg}{C.RESET}")
def err(msg):  print(f"{C.RED}  [XX]  {msg}{C.RESET}")
def fix(msg):  print(f"{C.PURPLE}  [FX]  {msg}{C.RESET}")
def div():     print(f"{C.GREY}{'=' * 62}{C.RESET}")
def blank():   print()


QUALITY_MAP = {
    "1": ("l", "480p  -- Low     (fastest preview)"),
    "2": ("m", "720p  -- Medium  (recommended)"),
    "3": ("h", "1080p -- High    (production)"),
    "4": ("k", "4K    -- Ultra   (slowest)"),
}


def quality_label(q):
    for v in QUALITY_MAP.values():
        if v[0] == q:
            return v[1]
    return q


def print_banner():
    blank()
    div()
    print(f"{C.BOLD}{C.WHITE}   COSCHOOL MANIM LAUNCHER  v2{C.RESET}")
    print(f"{C.GREY}   Auto-repair bookmarks | Fix assets | Propagate .env{C.RESET}")
    div()
    blank()


def build_env():
    env = {**os.environ}
    for env_file in [BASE_DIR / ".env", DEFAULT_SCRIPTS / ".env"]:
        if not env_file.exists():
            continue
        try:
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key and key not in env:
                    env[key] = val
        except Exception as e:
            warn(f"Could not read {env_file}: {e}")
    return env


def _collect_bookmark_tags(code):
    BM_RE = re.compile(
        r"<bookmark\s+mark=['\"]([^'\"]+)['\"]\s*/?>",
        re.IGNORECASE,
    )
    found = set()
    for m in re.finditer(r'"""([\s\S]*?)"""', code):
        for bm in BM_RE.finditer(m.group(1)):
            found.add(bm.group(1))
    for m in re.finditer(r"text\s*=\s*r?'([^']*)'", code):
        for bm in BM_RE.finditer(m.group(1)):
            found.add(bm.group(1))
    for m in re.finditer(r'text\s*=\s*\(([\s\S]*?)\)', code):
        inner = m.group(1)
        if "'" in inner or '"' in inner:
            for bm in BM_RE.finditer(inner):
                found.add(bm.group(1))
    return found


def _collect_wait_calls(code):
    return re.findall(
        r'self\.wait_until_bookmark\s*\(\s*["\']([^"\']+)["\']\s*\)',
        code,
    )


def repair_script(code):
    wt_fixes  = []
    new_lines = []
    for i, line in enumerate(code.split('\n')):
        if re.search(r'\b(?:MarkupText|Text)\s*\(', line):
            new_lines.append(line)
            continue
        if re.search(r'\bweight\s*=', line):
            fixed = line
            fixed = re.sub(
                r',\s*weight\s*=\s*(?:"[^"]*"|\'[^\']*\'|[A-Z_][A-Z_0-9]*|\d+)',
                '', fixed)
            fixed = re.sub(
                r'\bweight\s*=\s*(?:"[^"]*"|\'[^\']*\'|[A-Z_][A-Z_0-9]*|\d+)\s*,\s*',
                '', fixed)
            fixed = re.sub(
                r'\bweight\s*=\s*(?:"[^"]*"|\'[^\']*\'|[A-Z_][A-Z_0-9]*|\d+)',
                '', fixed)
            if fixed != line:
                wt_fixes.append(f'Line {i + 1}')
            new_lines.append(fixed)
        else:
            new_lines.append(line)
    code = '\n'.join(new_lines)

    bm_errors = []
    for _ in range(60):
        existing = _collect_bookmark_tags(code)
        waits    = _collect_wait_calls(code)
        missing  = next((w for w in waits if w not in existing), None)
        if missing is None:
            break
        pat = (
            r'[ \t]*self\.wait_until_bookmark\s*\(\s*["\']'
            + re.escape(missing)
            + r'["\']\s*\)\s*\n?'
        )
        cleaned = re.sub(pat, '\n', code)
        if cleaned != code:
            code = cleaned
            bm_errors.append(missing)
        else:
            break

    return code, wt_fixes, bm_errors


def _extract_prelude(code):
    match = re.search(r"(?m)^class\s+\w+\s*\([^)]*Scene[^)]*\)\s*:", code)
    if not match:
        return ""
    prelude = code[:match.start()].rstrip()
    if "from manim import" in prelude and "VoiceoverScene" in prelude:
        return prelude
    return ""


def _needs_shared_prelude(code):
    starts_with_scene = re.match(r"\s*class\s+\w+\s*\([^)]*Scene[^)]*\)\s*:", code) is not None
    has_imports = "from manim import" in code[:500] or "import manim" in code[:500]
    uses_shared_helpers = any(
        token in code
        for token in ("VoiceoverScene", "clear_and_transition", "create_heading_badge", "LAVENDER_BG")
    )
    return starts_with_scene and not has_imports and uses_shared_helpers


def _find_sibling_prelude(script_path):
    try:
        for sibling in sorted(script_path.parent.glob("*.py"), key=natural_sort_key):
            if sibling == script_path:
                continue
            try:
                prelude = _extract_prelude(sibling.read_text(encoding="utf-8", errors="ignore"))
            except Exception:
                continue
            if prelude:
                return prelude
    except Exception:
        return ""
    return ""


def add_shared_prelude_if_needed(script_path, code):
    if not _needs_shared_prelude(code):
        return code, False
    prelude = _find_sibling_prelude(script_path)
    if not prelude:
        prelude = "\n".join([
            "import os",
            "from dotenv import load_dotenv",
            "from manim import *",
            "from manim_voiceover import VoiceoverScene",
            "from manim_voiceover.services.openai import OpenAIService",
            "",
            "load_dotenv()",
            "",
            'LAVENDER_BG = "#E7E5F3"',
            'PURPLE = "#7464CE"',
            'ORANGE_HL = "#FF9302"',
            'PALE_PURPLE = "#9495D7"',
            "",
        ]).rstrip()
    return prelude + "\n\n" + code.lstrip(), True


def run_repair_on_script(script_path):
    try:
        original      = script_path.read_text(encoding="utf-8")
        with_prelude, prelude_added = add_shared_prelude_if_needed(script_path, original)
        fixed, wt, bm = repair_script(with_prelude)
        total         = len(wt) + len(bm) + (1 if prelude_added else 0)
        if total > 0:
            script_path.write_text(fixed, encoding="utf-8")
            if prelude_added:
                fix("shared Manim prelude added")
            for f in wt:
                fix(f"weight= removed at {f}")
            for b in bm:
                warn(f"Removed unfixable bookmark: '{b}'")
            ok(f"Auto-repair: {total} fix(es) applied")
        else:
            info("Auto-repair: script is clean")
        return wt, bm
    except Exception as e:
        warn(f"Auto-repair error: {e} -- rendering anyway")
        return [], []


def detect_class(filepath):
    try:
        text = filepath.read_text(encoding="utf-8", errors="ignore")
        m = re.search(
            r"^class\s+(\w+)\s*\(\s*VoiceoverScene\s*\)",
            text, re.MULTILINE)
        if m:
            return m.group(1)
        m = re.search(
            r"^class\s+(\w+)\s*\([^)]*Scene[^)]*\)",
            text, re.MULTILINE)
        if m:
            return m.group(1)
        m = re.search(r"^class\s+(\w+)", text, re.MULTILINE)
        if m:
            return m.group(1)
    except Exception:
        pass
    name = filepath.stem
    name = re.sub(r'[_\-]?\d{4,}$', '', name)
    parts = re.split(r"[_\-\s]+", name)
    return "".join(p.capitalize() for p in parts if p) + "Scene"


def create_placeholder_svg(name):
    n = name.lower().strip()
    if any(k in n for k in ["coin", "money", "dollar", "rupee", "currency"]):
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            '<circle cx="50" cy="50" r="46" fill="#FFD700" stroke="#B8860B" stroke-width="3"/>'
            '<circle cx="50" cy="50" r="38" fill="none" stroke="#B8860B" stroke-width="2"/>'
            '<text x="50" y="62" text-anchor="middle" font-size="32" '
            'fill="#B8860B" font-family="Arial" font-weight="bold">$</text>'
            '</svg>'
        )
    if any(k in n for k in ["star", "award", "prize"]):
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            '<polygon points="50,5 61,35 95,35 68,57 79,91 50,70 21,91 32,57 5,35 39,35" '
            'fill="#FFD700" stroke="#B8860B" stroke-width="2"/>'
            '</svg>'
        )
    if any(k in n for k in ["arrow", "pointer", "direction"]):
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            '<path d="M 5 42 L 60 42 L 60 22 L 95 50 L 60 78 L 60 58 L 5 58 Z" '
            'fill="#7464CE" stroke="#5a4db5" stroke-width="2"/>'
            '</svg>'
        )
    if any(k in n for k in ["book", "notebook", "textbook"]):
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            '<rect x="12" y="8" width="76" height="84" rx="6" fill="#7464CE" stroke="#5a4db5" stroke-width="2"/>'
            '<rect x="18" y="14" width="32" height="72" fill="#9495D7"/>'
            '<line x1="50" y1="14" x2="50" y2="86" stroke="#5a4db5" stroke-width="2"/>'
            '</svg>'
        )
    if any(k in n for k in ["person", "student", "teacher", "human", "people"]):
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            '<circle cx="50" cy="25" r="18" fill="#7464CE" stroke="#5a4db5" stroke-width="2"/>'
            '<path d="M 20 95 Q 20 55 50 55 Q 80 55 80 95 Z" '
            'fill="#7464CE" stroke="#5a4db5" stroke-width="2"/>'
            '</svg>'
        )
    if any(k in n for k in ["tree", "plant", "flower"]):
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            '<rect x="44" y="60" width="12" height="35" fill="#8B4513"/>'
            '<circle cx="50" cy="40" r="32" fill="#22c55e" stroke="#15803d" stroke-width="2"/>'
            '</svg>'
        )
    if any(k in n for k in ["house", "home", "building", "school"]):
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            '<polygon points="50,5 95,45 5,45" fill="#FF9302" stroke="#e07800" stroke-width="2"/>'
            '<rect x="15" y="45" width="70" height="50" fill="#7464CE" stroke="#5a4db5" stroke-width="2"/>'
            '<rect x="40" y="65" width="20" height="30" fill="#fff" opacity="0.4"/>'
            '</svg>'
        )
    if any(k in n for k in ["heart", "love"]):
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            '<path d="M 50 80 C 10 55 5 20 25 15 C 35 12 45 18 50 28 '
            'C 55 18 65 12 75 15 C 95 20 90 55 50 80 Z" '
            'fill="#ef4444" stroke="#b91c1c" stroke-width="2"/>'
            '</svg>'
        )
    if any(k in n for k in ["check", "tick", "correct", "right", "yes"]):
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            '<circle cx="50" cy="50" r="45" fill="#22c55e" stroke="#15803d" stroke-width="3"/>'
            '<polyline points="25,52 43,70 75,30" fill="none" stroke="#fff" '
            'stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>'
            '</svg>'
        )
    if any(k in n for k in ["cross", "wrong", "error", "no", "close"]):
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            '<circle cx="50" cy="50" r="45" fill="#ef4444" stroke="#b91c1c" stroke-width="3"/>'
            '<line x1="30" y1="30" x2="70" y2="70" stroke="#fff" stroke-width="8" stroke-linecap="round"/>'
            '<line x1="70" y1="30" x2="30" y2="70" stroke="#fff" stroke-width="8" stroke-linecap="round"/>'
            '</svg>'
        )
    if any(k in n for k in ["calc", "calculator"]):
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            '<rect x="15" y="5" width="70" height="90" rx="8" fill="#7464CE" stroke="#5a4db5" stroke-width="2"/>'
            '<rect x="22" y="12" width="56" height="24" rx="4" fill="#9495D7"/>'
            '<circle cx="30" cy="52" r="6" fill="#fff" opacity="0.7"/>'
            '<circle cx="50" cy="52" r="6" fill="#fff" opacity="0.7"/>'
            '<circle cx="70" cy="52" r="6" fill="#fff" opacity="0.7"/>'
            '<circle cx="30" cy="70" r="6" fill="#fff" opacity="0.7"/>'
            '<circle cx="50" cy="70" r="6" fill="#fff" opacity="0.7"/>'
            '<circle cx="70" cy="70" r="6" fill="#FF9302" opacity="0.9"/>'
            '<circle cx="30" cy="88" r="6" fill="#fff" opacity="0.7"/>'
            '<circle cx="50" cy="88" r="6" fill="#fff" opacity="0.7"/>'
            '<circle cx="70" cy="88" r="6" fill="#fff" opacity="0.7"/>'
            '</svg>'
        )
    if any(k in n for k in ["circle", "dot", "ball", "sphere"]):
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            '<circle cx="50" cy="50" r="45" fill="#7464CE" stroke="#5a4db5" stroke-width="3"/>'
            '</svg>'
        )
    if any(k in n for k in ["square", "box", "rect", "block"]):
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            '<rect x="10" y="10" width="80" height="80" rx="8" '
            'fill="#7464CE" stroke="#5a4db5" stroke-width="3"/>'
            '</svg>'
        )
    if any(k in n for k in ["triangle", "tri", "pyramid"]):
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            '<polygon points="50,8 95,90 5,90" '
            'fill="#7464CE" stroke="#5a4db5" stroke-width="3"/>'
            '</svg>'
        )
    short = name[:10] if len(name) <= 10 else name[:9] + "."
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
        '<rect x="8" y="8" width="84" height="84" rx="12" '
        'fill="#7464CE" stroke="#5a4db5" stroke-width="3"/>'
        f'<text x="50" y="58" text-anchor="middle" font-size="13" '
        f'fill="white" font-family="Arial">{short}</text>'
        '</svg>'
    )


def fix_missing_assets(script_path):
    created = []
    try:
        text    = script_path.read_text(encoding="utf-8", errors="ignore")
        pattern = r'SVGMobject\s*\(\s*["\']([^"\']+)["\']'
        matches = re.findall(pattern, text)
        if not matches:
            return []
        for raw_name in set(matches):
            base     = Path(raw_name).stem
            svg_path = script_path.parent / f"{base}.svg"
            if svg_path.exists():
                continue
            svg_path.write_text(
                create_placeholder_svg(base), encoding="utf-8")
            created.append((base, svg_path))
    except Exception as e:
        warn(f"Asset scan error: {e}")
    return created


def fix_all_assets(scripts):
    total_fixed = 0
    for script_path in scripts:
        fixed = fix_missing_assets(script_path)
        if fixed:
            blank()
            print(f"  {C.PURPLE}[FX] Auto-fixing assets: "
                  f"{script_path.name}{C.RESET}")
            for name, path in fixed:
                fix(f"Created: {name}.svg")
                total_fixed += 1
    return total_fixed


def find_video(media_dir, classname, render_start_time=None):
    cutoff = (render_start_time - 10) if render_start_time else 0
    candidates = [
        f for f in media_dir.rglob("*.mp4")
        if classname.lower() in f.stem.lower()
        and f.stat().st_mtime >= cutoff
    ]
    if candidates:
        return max(candidates, key=lambda f: f.stat().st_mtime)
    candidates = [
        f for f in media_dir.rglob("*.mp4")
        if classname.lower() in f.stem.lower()
    ]
    if candidates:
        return max(candidates, key=lambda f: f.stat().st_mtime)
    candidates = [
        f for f in media_dir.rglob("*.mp4")
        if f.stat().st_mtime >= cutoff
    ]
    if candidates:
        return max(candidates, key=lambda f: f.stat().st_mtime)
    return None


def load_results():
    if RESULTS_FILE.exists():
        try:
            return json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_results(results):
    RESULTS_FILE.write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8")


def natural_sort_key(p):
    parts = re.split(r'(\d+)', p.name.lower())
    return [int(x) if x.isdigit() else x for x in parts]


def render_one(script_path, classname, quality, media_dir, idx, total):
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    div()
    print(f"{C.BOLD}{C.CYAN}  [{idx}/{total}]  {script_path.name}{C.RESET}")
    print(f"  {C.GREY}Class   : {classname}{C.RESET}")
    print(f"  {C.GREY}Quality : {quality_label(quality)}{C.RESET}")
    print(f"  {C.GREY}Output  : {media_dir}{C.RESET}")
    blank()

    info("Step 1/3 -- Auto-repair (bookmarks + weight=)...")
    run_repair_on_script(script_path)

    info("Step 2/3 -- Checking SVG assets...")
    fixed_svgs = fix_missing_assets(script_path)
    if fixed_svgs:
        for name, path in fixed_svgs:
            fix(f"Created SVG placeholder: {name}.svg")
    else:
        info("SVG assets OK")

    env = build_env()
    if "OPENAI_API_KEY" in env:
        info("Step 3/3 -- OPENAI_API_KEY loaded")
    else:
        warn("Step 3/3 -- OPENAI_API_KEY not found in .env!")
        warn("           Add OPENAI_API_KEY=sk-... to .env and retry.")

    div()
    print(f"  {C.ORANGE}[..] Rendering -- please wait...{C.RESET}")
    blank()

    cmd = [
        sys.executable, "-m", "manim",
        f"-q{quality}",
        "--media_dir", str(media_dir),
        str(script_path),
        classname,
    ]

    log_filename = (
        f"{script_path.stem}_{datetime.now().strftime('%H%M%S')}.log"
    )
    log_file = LOG_DIR / log_filename
    t_start  = time.time()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(script_path.parent),
            timeout=600,
            env=env,
        )
        elapsed    = round(time.time() - t_start, 1)
        output     = result.stdout + result.stderr
        video_path = find_video(media_dir, classname, t_start)

        try:
            log_file.write_text(output, encoding="utf-8")
        except Exception:
            pass

        if result.returncode == 0:
            ok(f"Rendered in {elapsed}s")
            if video_path:
                ok(f"Video saved --> {video_path}")
            else:
                warn("Video file not located -- check logs.")
            blank()
            return {
                "file": script_path.name, "class": classname,
                "status": "success", "elapsed": elapsed,
                "video": str(video_path) if video_path else "",
                "log": str(log_file), "error": "",
            }

        else:
            last = "\n".join(output.strip().split("\n")[-30:])
            err(f"Manim failed (exit code {result.returncode})")
            print(f"\n{C.GREY}{last}{C.RESET}\n")

            svg_error = ".svg" in output.lower() and any(
                k in output.lower() for k in [
                    "no such file", "could not find",
                    "could not open", "filenotfounderror",
                ]
            )

            if svg_error:
                blank()
                warn("MISSING SVG ASSET DETECTED:")
                m = (
                    re.search(r"['\"]([^'\"]+\.svg)['\"]", output)
                    or re.search(r"(\w[\w/\-]*\.svg)", output, re.IGNORECASE)
                    or re.search(
                        r"FileNotFoundError.*?['\"]([^'\"]+)['\"]", output)
                )
                if m:
                    missing_stem = Path(m.group(1)).stem
                    warn(f"Missing: {missing_stem}.svg -- creating and retrying...")
                    svg_path = script_path.parent / f"{missing_stem}.svg"
                    svg_path.write_text(
                        create_placeholder_svg(missing_stem), encoding="utf-8")
                    fix(f"Created: {svg_path}")
                    blank()
                    info("Retrying render...")
                    blank()

                    result2 = subprocess.run(
                        cmd, capture_output=True, text=True,
                        cwd=str(script_path.parent),
                        timeout=600, env=env,
                    )
                    elapsed2   = round(time.time() - t_start, 1)
                    out2       = result2.stdout + result2.stderr
                    video_path2 = find_video(media_dir, classname, t_start)
                    try:
                        log_file.write_text(out2, encoding="utf-8")
                    except Exception:
                        pass

                    if result2.returncode == 0:
                        ok(f"RETRY SUCCEEDED in {elapsed2}s")
                        if video_path2:
                            ok(f"Video saved --> {video_path2}")
                        blank()
                        return {
                            "file": script_path.name, "class": classname,
                            "status": "success", "elapsed": elapsed2,
                            "video": str(video_path2) if video_path2 else "",
                            "log": str(log_file), "error": "",
                        }
                    else:
                        last2 = "\n".join(out2.strip().split("\n")[-20:])
                        err("Retry also failed.")
                        return {
                            "file": script_path.name, "class": classname,
                            "status": "error", "elapsed": elapsed2,
                            "video": "", "log": str(log_file), "error": last2,
                        }
                else:
                    warn("Could not identify missing SVG -- check log.")

            elif any(k in output.lower() for k in
                     ["importerror", "modulenotfounderror"]):
                blank()
                warn("MISSING PYTHON PACKAGE:")
                m = re.search(r"No module named '([^']+)'", output)
                if m:
                    warn(f"Run:  pip install {m.group(1)}")

            return {
                "file": script_path.name, "class": classname,
                "status": "error", "elapsed": elapsed,
                "video": "", "log": str(log_file), "error": last,
            }

    except subprocess.TimeoutExpired:
        elapsed = round(time.time() - t_start, 1)
        err(f"Timeout after {elapsed}s -- script killed.")
        return {
            "file": script_path.name, "class": classname,
            "status": "timeout", "elapsed": elapsed,
            "video": "", "log": str(log_file),
            "error": f"Timeout after {elapsed}s",
        }

    except FileNotFoundError:
        err("Manim not found!  Run:  pip install manim")
        return {
            "file": script_path.name, "class": classname,
            "status": "error", "elapsed": 0,
            "video": "", "log": "", "error": "manim not found",
        }


def print_summary(results):
    blank()
    div()
    print(f"{C.BOLD}{C.WHITE}   FINAL SUMMARY{C.RESET}")
    div()
    blank()
    success = [r for r in results if r["status"] == "success"]
    errors  = [r for r in results if r["status"] in ("error", "timeout")]
    print(f"  {C.GREEN}[OK] Succeeded : {len(success)}{C.RESET}")
    print(f"  {C.RED}[XX] Failed    : {len(errors)}{C.RESET}")
    print(f"  {C.BLUE}[..] Total     : {len(results)}{C.RESET}")
    blank()
    MAX_NAME = 48
    if success:
        print(f"{C.BOLD}  VIDEOS RENDERED:{C.RESET}")
        div()
        for r in success:
            vid   = Path(r["video"]).name if r["video"] else "--"
            fname = r["file"]
            if len(fname) > MAX_NAME:
                fname = fname[:MAX_NAME - 1] + "."
            print(f"  {C.GREEN}{fname:<{MAX_NAME}}{C.RESET}  {r['elapsed']}s")
            print(f"    --> {C.CYAN}{vid}{C.RESET}")
        blank()
    if errors:
        print(f"{C.BOLD}  ERRORS:{C.RESET}")
        div()
        for r in errors:
            fname = r["file"]
            if len(fname) > MAX_NAME:
                fname = fname[:MAX_NAME - 1] + "."
            print(f"  {C.RED}{fname:<{MAX_NAME}}{C.RESET}  [{r['status']}]")
        blank()
    info(f"Videos : {DEFAULT_MEDIA}")
    info(f"Logs   : {LOG_DIR}")
    info(f"JSON   : {RESULTS_FILE}")
    blank()


def ask_folder():
    print(f"{C.BOLD}  STEP 1 -- SELECT SCRIPTS FOLDER{C.RESET}")
    div()
    blank()
    info(f"Default folder:  {DEFAULT_SCRIPTS}")
    blank()
    print(
        f"  {C.CYAN}Press ENTER{C.RESET} to use the default folder\n"
        f"  {C.CYAN}Or type a full path{C.RESET} and press ENTER"
    )
    blank()
    raw = input("  Folder path: ").strip()
    if not raw:
        folder = DEFAULT_SCRIPTS
        info(f"Using default: {folder}")
    else:
        folder = Path(raw).expanduser().resolve()
        info(f"Using: {folder}")
    blank()
    if not folder.exists():
        warn(f"Folder does not exist -- creating: {folder}")
        folder.mkdir(parents=True, exist_ok=True)
    return folder


def ask_files(folder):
    scripts = sorted(folder.glob("*.py"), key=natural_sort_key)
    blank()
    print(f"{C.BOLD}  STEP 2 -- SELECT FILES TO RENDER{C.RESET}")
    div()
    blank()
    if not scripts:
        err(f"No .py files found in:  {folder}")
        info("Drop your Manim .py files into that folder and run again.")
        sys.exit(1)
    print(f"  {C.CYAN}Found {len(scripts)} .py file(s):{C.RESET}")
    blank()
    for i, s in enumerate(scripts, 1):
        cn = detect_class(s)
        sz = round(s.stat().st_size / 1024, 1)
        print(
            f"  {C.BOLD}{C.ORANGE}  {i:>2}.{C.RESET}  "
            f"{C.WHITE}{s.name:<45}{C.RESET}  "
            f"{C.GREY}class: {cn}  ({sz} KB){C.RESET}"
        )
    blank()
    print(
        f"  {C.CYAN}Press ENTER{C.RESET}             --> run ALL files\n"
        f"  {C.CYAN}Type a number{C.RESET} e.g.  2   --> run that file only\n"
        f"  {C.CYAN}Type numbers{C.RESET}  e.g.  1,3 --> run those files\n"
        f"  {C.CYAN}Type a range{C.RESET}  e.g.  2-5 --> run files 2 to 5"
    )
    blank()
    raw = input("  Your choice: ").strip()
    blank()
    if not raw:
        info(f"Running ALL {len(scripts)} file(s).")
        return scripts
    chosen = []
    for part in re.split(r"[,\s]+", raw):
        part = part.strip()
        if not part:
            continue
        range_match = re.match(r'^(\d+)-(\d+)$', part)
        if range_match:
            start_n = int(range_match.group(1))
            end_n   = int(range_match.group(2))
            for n in range(start_n, end_n + 1):
                if 1 <= n <= len(scripts):
                    if scripts[n - 1] not in chosen:
                        chosen.append(scripts[n - 1])
                else:
                    warn(f"Number {n} out of range -- skipping.")
        elif part.isdigit():
            n = int(part)
            if 1 <= n <= len(scripts):
                if scripts[n - 1] not in chosen:
                    chosen.append(scripts[n - 1])
            else:
                warn(f"Number {n} out of range -- skipping.")
        else:
            warn(f"Invalid input '{part}' -- skipping.")
    if not chosen:
        warn("No valid selection -- running ALL files.")
        return scripts
    info(f"Selected {len(chosen)} file(s):")
    for s in chosen:
        print(f"    {C.GREEN}--> {s.name}{C.RESET}")
    return chosen


def ask_quality():
    blank()
    print(f"{C.BOLD}  STEP 3 -- SELECT RENDER QUALITY{C.RESET}")
    div()
    blank()
    for num, (flag, label) in QUALITY_MAP.items():
        tag = "  <-- recommended" if flag == "m" else ""
        print(
            f"  {C.BOLD}{C.CYAN}  {num}.{C.RESET}  "
            f"-q {flag}   {C.WHITE}{label}{C.RESET}"
            f"{C.ORANGE}{tag}{C.RESET}"
        )
    blank()
    print(
        f"  {C.CYAN}Press ENTER{C.RESET} for default (720p Medium)\n"
        f"  {C.CYAN}Or type 1 / 2 / 3 / 4{C.RESET}"
    )
    blank()
    raw = input("  Quality choice: ").strip()
    blank()
    if not raw:
        info("Using default: 720p Medium")
        return "m"
    if raw in QUALITY_MAP:
        flag, label = QUALITY_MAP[raw]
        info(f"Selected: {label}")
        return flag
    if raw.lower() in ("l", "m", "h", "k"):
        info(f"Selected: {quality_label(raw.lower())}")
        return raw.lower()
    warn(f"Unrecognised '{raw}' -- using default 720p Medium.")
    return "m"


def ask_confirm(scripts, quality):
    blank()
    print(f"{C.BOLD}  STEP 4 -- CONFIRM AND RUN{C.RESET}")
    div()
    blank()
    print(f"  {C.BOLD}Ready to render:{C.RESET}")
    blank()
    print(f"  {C.CYAN}Files       :{C.RESET}  {len(scripts)} script(s)")
    print(f"  {C.CYAN}Quality     :{C.RESET}  {quality_label(quality)}")
    print(f"  {C.CYAN}Videos   -> :{C.RESET}  {DEFAULT_MEDIA}")
    print(f"  {C.CYAN}Auto-fix    :{C.RESET}  Bookmarks | weight= | SVG assets")
    env_ok = (BASE_DIR / ".env").exists()
    print(f"  {C.CYAN}.env        :{C.RESET}  "
          f"{'Found' if env_ok else 'NOT FOUND -- voiceover will fail!'}")
    blank()
    for s in scripts:
        cn = detect_class(s)
        print(f"    {C.GREEN}>> {s.name}{C.RESET}  class: {cn}")
    blank()
    print(
        f"  {C.CYAN}Press ENTER{C.RESET} or type y to start\n"
        f"  Type n to cancel"
    )
    blank()
    raw = input("  Start rendering? [Y/n]: ").strip().lower()
    blank()
    if raw in ("", "y", "yes"):
        return True
    info("Cancelled.")
    return False


def parse_args():
    parser = argparse.ArgumentParser(
        description="Render Manim Python scripts with auto-repair."
    )
    parser.add_argument(
        "--folder",
        help="Folder containing Python scripts. Defaults to the launcher scripts folder.",
    )
    parser.add_argument(
        "--files",
        help="Comma-separated filenames or paths to render. Use all, or omit with --yes, to render every .py file.",
    )
    parser.add_argument(
        "--quality",
        default="",
        help="Render quality: 1/2/3/4 or l/m/h/k. Defaults to m in non-interactive mode.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Run without confirmation prompts.",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Do not ask to open the videos folder after rendering.",
    )
    return parser.parse_args()


def resolve_quality(raw):
    raw = str(raw or "").strip().lower()
    if not raw:
        return "m"
    if raw in QUALITY_MAP:
        return QUALITY_MAP[raw][0]
    if raw in ("l", "m", "h", "k"):
        return raw
    warn(f"Unrecognised quality '{raw}' -- using default 720p Medium.")
    return "m"


def cli_folder(raw):
    folder = Path(raw).expanduser().resolve() if raw else DEFAULT_SCRIPTS
    if not folder.exists():
        warn(f"Folder does not exist -- creating: {folder}")
        folder.mkdir(parents=True, exist_ok=True)
    return folder


def cli_files(folder, raw):
    scripts = sorted(folder.glob("*.py"), key=natural_sort_key)
    raw = str(raw or "").strip()
    if not raw or raw.lower() == "all":
        if not scripts:
            err(f"No .py files found in:  {folder}")
            sys.exit(1)
        info(f"Running ALL {len(scripts)} file(s).")
        return scripts

    chosen = []
    for part in re.split(r"[,;]+", raw):
        part = part.strip().strip('"').strip("'")
        if not part:
            continue
        candidate = Path(part).expanduser()
        if not candidate.is_absolute():
            candidate = folder / candidate
        candidate = candidate.resolve()
        if candidate.exists() and candidate.suffix.lower() == ".py":
            if candidate not in chosen:
                chosen.append(candidate)
        else:
            warn(f"Script not found -- skipping: {candidate}")

    if not chosen:
        err("No valid .py files selected for rendering.")
        sys.exit(1)
    info(f"Selected {len(chosen)} file(s):")
    for script_path in chosen:
        print(f"    {C.GREEN}--> {script_path.name}{C.RESET}")
    return chosen


def main():
    args = parse_args()
    DEFAULT_SCRIPTS.mkdir(parents=True, exist_ok=True)
    DEFAULT_MEDIA.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    print_banner()

    if not (BASE_DIR / ".env").exists():
        warn(".env file not found in launcher folder!")
        warn("Create it with:  OPENAI_API_KEY=sk-your-key-here")
        blank()

    if args.yes or args.folder or args.files:
        folder = cli_folder(args.folder)
        scripts = cli_files(folder, args.files)
        quality = resolve_quality(args.quality)
        info(f"Using non-interactive quality: {quality_label(quality)}")
    else:
        folder  = ask_folder()
        scripts = ask_files(folder)
        quality = ask_quality()

    blank()
    print(f"{C.BOLD}  PRE-SCAN -- AUTO-REPAIR ALL SELECTED SCRIPTS{C.RESET}")
    div()
    info("Running bookmark repair, weight= fix, and SVG check...")
    blank()

    total_wt  = 0
    total_bm  = 0
    total_svg = 0

    for sp in scripts:
        wt, bm  = run_repair_on_script(sp)
        total_wt  += len(wt)
        total_bm  += len(bm)

    total_svg = fix_all_assets(scripts)

    blank()
    if total_wt == 0 and total_bm == 0 and total_svg == 0:
        ok("All scripts clean -- no repairs needed.")
    else:
        ok(f"Pre-scan complete: {total_wt} weight fix(es), "
           f"{total_bm} bookmark removal(s), "
           f"{total_svg} SVG placeholder(s) created.")
    blank()

    if args.yes:
        info("Confirmation skipped by --yes.")
    elif not ask_confirm(scripts, quality):
        return

    blank()
    div()
    print(f"{C.BOLD}{C.WHITE}   RENDERING STARTED{C.RESET}")
    div()
    blank()

    all_results = load_results()
    run_results = []
    total       = len(scripts)
    t_batch     = time.time()

    for idx, script_path in enumerate(scripts, 1):
        classname = detect_class(script_path)
        result = render_one(
            script_path=script_path,
            classname=classname,
            quality=quality,
            media_dir=DEFAULT_MEDIA,
            idx=idx,
            total=total,
        )
        run_results.append(result)
        all_results[script_path.name] = result
        save_results(all_results)

        done_pct = int(idx / total * 40)
        bar = "#" * done_pct + "-" * (40 - done_pct)
        print(
            f"  {C.GREY}Progress: [{C.PURPLE}{bar}{C.GREY}]"
            f"  {idx}/{total}{C.RESET}"
        )
        blank()

        if idx < total:
            delay = 2 if quality in ("l", "m") else 5
            info(f"Waiting {delay}s before next file...")
            time.sleep(delay)

    total_time = round(time.time() - t_batch, 1)
    blank()
    info(f"Total batch time: {total_time}s")

    print_summary(run_results)

    blank()
    div()
    raw = "n" if args.no_open else input("  Open videos folder in explorer? [Y/n]: ").strip().lower()
    if raw in ("", "y", "yes"):
        try:
            if sys.platform == "win32":
                os.startfile(str(DEFAULT_MEDIA))
            elif sys.platform == "darwin":
                subprocess.run(["open", str(DEFAULT_MEDIA)])
            else:
                subprocess.run(["xdg-open", str(DEFAULT_MEDIA)])
            info(f"Opened: {DEFAULT_MEDIA}")
        except Exception as e:
            warn(f"Could not open folder: {e}")
            info(f"Navigate manually to: {DEFAULT_MEDIA}")

    blank()
    ok("Done! All rendering complete.")
    blank()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        blank()
        warn("Interrupted by user.")
        blank()
