#!/usr/bin/env python3
"""sloth-sorter: a lazy file tidier. A local open-weight model (Gemma via Ollama)
reads each file, picks a folder and a clean name. Dry-run unless --apply."""
import argparse, json, shutil, sys, urllib.request
from pathlib import Path

OLLAMA = "http://localhost:11434/api/generate"
CATEGORIES = ["invoices", "contracts", "notes", "code", "images", "media", "docs", "misc"]
TEXT_EXT = {".txt", ".md", ".csv", ".json", ".py", ".js", ".html", ".log"}

PROMPT = """You tidy files. Given a file name and a preview of its content, answer with JSON only:
{{"folder": one of {cats}, "name": short-kebab-case-name-without-extension}}

File name: {name}
Preview:
{preview}
"""

def preview(path: Path, limit=600) -> str:
    if path.suffix.lower() in TEXT_EXT:
        return path.read_text(errors="ignore")[:limit]
    return f"(binary {path.suffix} file, {path.stat().st_size} bytes)"

def ask(model: str, path: Path) -> dict:
    body = json.dumps({
        "model": model, "stream": False, "format": "json",
        "prompt": PROMPT.format(cats=CATEGORIES, name=path.name, preview=preview(path)),
    }).encode()
    req = urllib.request.Request(OLLAMA, body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.loads(json.load(r)["response"])
    folder = data.get("folder") if data.get("folder") in CATEGORIES else "misc"
    name = "".join(c for c in str(data.get("name", path.stem)).lower() if c.isalnum() or c in "-_") or path.stem
    return {"folder": folder, "name": name}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("folder", type=Path)
    ap.add_argument("--model", default="gemma3:4b")
    ap.add_argument("--apply", action="store_true", help="actually move files (default: dry run)")
    args = ap.parse_args()

    files = [p for p in sorted(args.folder.iterdir()) if p.is_file() and not p.name.startswith(".")]
    for p in files:
        try:
            r = ask(args.model, p)
        except Exception as e:
            print(f"skip {p.name}: {e}", file=sys.stderr); continue
        dest = args.folder / r["folder"] / f"{r['name']}{p.suffix.lower()}"
        n = 1
        while dest.exists():
            dest = dest.with_name(f"{r['name']}-{n}{p.suffix.lower()}"); n += 1
        print(f"{p.name}  ->  {dest.relative_to(args.folder)}")
        if args.apply:
            dest.parent.mkdir(exist_ok=True)
            shutil.move(str(p), dest)
    if not args.apply:
        print("\n(dry run — re-run with --apply to move files)")

if __name__ == "__main__":
    main()
