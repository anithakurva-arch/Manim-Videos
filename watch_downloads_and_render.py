import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path


BASE_DIR = Path(__file__).parent.resolve()
DEFAULT_WATCH_DIR = Path(
    os.environ.get("WATCH_SCRIPTS_DIR")
    or (Path.home() / "Downloads" / "scripts")
).expanduser()
STATE_FILE = BASE_DIR / "logs" / "download_watcher_state.json"
WATCH_LOG = BASE_DIR / "logs" / "download_watcher.log"


def log(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line, flush=True)
    WATCH_LOG.parent.mkdir(parents=True, exist_ok=True)
    with WATCH_LOG.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def file_signature(path):
    stat = path.stat()
    return {
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
    }


def load_state():
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def stable_python_files(folder, settle_seconds):
    first = {
        path: file_signature(path)
        for path in folder.glob("*.py")
        if path.is_file()
    }
    time.sleep(settle_seconds)
    stable = {}
    for path, signature in first.items():
        if not path.exists():
            continue
        try:
            current = file_signature(path)
        except OSError:
            continue
        if current == signature:
            stable[path] = current
    return stable


def render_files(files, quality):
    filenames = ",".join(path.name for path in files)
    command = [
        sys.executable,
        str(BASE_DIR / "start.py"),
        "--folder",
        str(files[0].parent),
        "--files",
        filenames,
        "--quality",
        quality,
        "--yes",
        "--no-open",
    ]
    log(f"Starting render for {len(files)} file(s): {filenames}")
    result = subprocess.run(command, cwd=str(BASE_DIR))
    if result.returncode == 0:
        log("Render finished successfully.")
        return True
    log(f"Render failed with exit code {result.returncode}.")
    return False


def watch(folder, quality, interval, settle_seconds, render_existing):
    folder.mkdir(parents=True, exist_ok=True)
    WATCH_LOG.parent.mkdir(parents=True, exist_ok=True)
    state = load_state()

    if render_existing:
        state = {}
    else:
        for path, signature in stable_python_files(folder, settle_seconds).items():
            state[str(path.resolve())] = signature
        save_state(state)

    log(f"Watching for Python scripts in: {folder}")
    log(f"Quality: {quality}. Existing files will {'render' if render_existing else 'be skipped'}.")

    while True:
        try:
            stable = stable_python_files(folder, settle_seconds)
            changed = []
            for path, signature in stable.items():
                key = str(path.resolve())
                if state.get(key) != signature:
                    changed.append(path)

            if changed:
                changed = sorted(changed, key=lambda item: item.name.lower())
                if render_files(changed, quality):
                    for path in changed:
                        key = str(path.resolve())
                        if path.exists():
                            state[key] = file_signature(path)
                    save_state(state)

            time.sleep(interval)
        except KeyboardInterrupt:
            log("Watcher stopped.")
            break
        except Exception as exc:
            log(f"Watcher error: {exc}")
            time.sleep(interval)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Watch a local download folder and render new Manim Python scripts."
    )
    parser.add_argument(
        "--folder",
        default=str(DEFAULT_WATCH_DIR),
        help="Folder to watch for downloaded .py files.",
    )
    parser.add_argument(
        "--quality",
        default="m",
        help="Manim quality passed to start.py: l, m, h, or k.",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=5,
        help="Seconds between folder checks.",
    )
    parser.add_argument(
        "--settle-seconds",
        type=float,
        default=2,
        help="Seconds a .py file must stay unchanged before rendering.",
    )
    parser.add_argument(
        "--render-existing",
        action="store_true",
        help="Render .py files already present when the watcher starts.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    watch(
        folder=Path(args.folder).expanduser().resolve(),
        quality=args.quality,
        interval=max(args.interval, 1),
        settle_seconds=max(args.settle_seconds, 1),
        render_existing=args.render_existing,
    )


if __name__ == "__main__":
    main()
