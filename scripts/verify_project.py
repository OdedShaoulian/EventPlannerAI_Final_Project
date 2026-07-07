from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_PATHS = [
    "app.py",
    "README.md",
    "requirements.txt",
    ".env.example",
    ".gitignore",
    "src/config.py",
    "src/openai_utils.py",
    "src/rag.py",
    "src/tts.py",
    "knowledge_base/packages.md",
    "knowledge_base/pricing_rules.md",
    "knowledge_base/operation_checklist.md",
    "knowledge_base/faq.md",
]

API_KEY_PATTERN = re.compile(r"sk-[A-Za-z0-9_\-]{20,}")


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    sys.exit(1)


def main() -> None:
    print("Checking required files...")
    for rel in REQUIRED_PATHS:
        if not (ROOT / rel).exists():
            fail(f"Missing required file or folder: {rel}")



    print("Scanning for possible API keys...")
    for path in ROOT.rglob("*"):
        if ".venv" in path.parts or "venv" in path.parts:
            continue
        if not path.is_file():
            continue
        if path.name == ".env":  # Skip checking the .env file for hardcoded API keys
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".pptx", ".mp3", ".pdf"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if API_KEY_PATTERN.search(text):
            fail(f"Possible API key found in: {path.relative_to(ROOT)}")

    print("Checking Python syntax without creating cache files...")
    for py_file in ROOT.rglob("*.py"):
        if ".venv" in py_file.parts or "venv" in py_file.parts:
            continue
        source = py_file.read_text(encoding="utf-8", errors="ignore")
        try:
            ast.parse(source, filename=str(py_file))
        except SyntaxError as exc:
            fail(f"Python syntax check failed in {py_file.relative_to(ROOT)}: {exc}")

    print("[OK] Project is ready for GitHub submission.")


if __name__ == "__main__":
    main()
