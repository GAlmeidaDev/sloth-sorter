# sloth-sorter 🦥

A lazy file tidier. A local open-weight model (Gemma 3 via Ollama) reads each file, picks a folder and a clean name. Nothing leaves your machine. Dry run by default.

```bash
ollama pull gemma3:4b
python3 sloth.py ~/Downloads            # preview
python3 sloth.py ~/Downloads --apply    # move files
```

Stdlib-only Python 3. Built for the Hacktoberfest Open-Source AI Challenge: Week 3 (#hf26challenge).
